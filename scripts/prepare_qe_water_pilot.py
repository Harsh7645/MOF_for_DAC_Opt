"""Build revision 2 from sealed coordinates and checksum-pinned official SSSP files.

Preparation only: no pw.x, UMA, scheduler or system installer is invoked.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import tarfile
import xml.etree.ElementTree as ET

import numpy as np
from ase.io import read
from mof_dac.frozen_dft import from_record, qe_template

CANDIDATES = {'Zr': 'Zr_pbe_v1.uspp.F.UPF', 'O': 'O.pbe-n-kjpaw_psl.0.1.UPF',
              'C': 'C.pbe-n-kjpaw_psl.1.0.0.UPF', 'N': 'N.oncvpsp.upf',
              'H': 'H_ONCV_PBE-1.0.oncvpsp.upf'}
PINNED = {'SSSP_1.3.0_PBE_precision.json': '1692c5c9ce89e1c7c783f8f0eee0cbfa',
          'SSSP_1.3.0_PBE_precision.tar.gz': 'fde94756886f32ada7bf597547557eb5'}
OLD_ZIP_SHA = '572b56a936408bc06036a29becc69b02ca2064690ed024eeefacb9ddcbd14bca'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf8')


def upf_header(text):
    """Read both old GBRV UPF and XML UPF headers; retain literal source evidence."""
    if '<PP_HEADER>' in text:
        raw = re.search(r'<PP_HEADER>.*?</PP_HEADER>', text, re.S).group()
        return {'raw_header': raw, 'element': re.search(r'\n\s*(\w+)\s+Element', raw)[1],
                'z_valence': float(re.search(r'([\d.]+)\s+Z valence', raw)[1]),
                'pseudo_type': 'US', 'relativistic': 'scalar' if 'Scalar-Relativistic' in text else 'unverified',
                'functional': 'PBE' if 'PBE  Exchange-Correlation' in raw else 'unverified',
                'semicore': '4s2 4p6 in valence; 4d2 5s2; empty 5p projector',
                'header_cutoffs_Ry': [0, 0], 'cutoff_note': 'zero header values are not recommendations'}
    raw = re.search(r'<PP_HEADER\s.*?/>', text, re.S).group()
    attrs = ET.fromstring(raw).attrib
    return {'raw_header': raw, **attrs, 'element': attrs['element'].strip(),
            'z_valence': float(attrs['z_valence']),
            'semicore': 'not applicable for these first-row/H potentials'}


def verify_library(source):
    metadata = json.loads((source/'SSSP_1.3.0_PBE_precision.json').read_text())
    downloads = {}
    for name, md5 in PINNED.items():
        content = (source/name).read_bytes()
        if hashlib.md5(content).hexdigest() != md5:
            raise ValueError('Published archive/metadata checksum mismatch: '+name)
        downloads[name] = {'published_md5': md5, 'sha256': sha(source/name), 'bytes': len(content)}
    selected = {}
    with tarfile.open(source/'SSSP_1.3.0_PBE_precision.tar.gz') as archive:
        for element, filename in CANDIDATES.items():
            entry = metadata[element]
            if entry['filename'] != filename:
                raise ValueError('Candidate differs from pinned collection: '+element)
            members = [m for m in archive.getmembers() if Path(m.name).name == filename and m.isfile()]
            if len(members) != 1:
                raise ValueError('Missing/ambiguous archive member: '+filename)
            content = archive.extractfile(members[0]).read()
            if hashlib.md5(content).hexdigest() != entry['md5']:
                raise ValueError('Published potential checksum mismatch: '+filename)
            if content != (source/filename).read_bytes():
                raise ValueError('Local potential differs from verified archive')
            header = upf_header(content.decode())
            if header['element'] != element:
                raise ValueError('UPF element mismatch')
            selected[element] = {**entry, 'sha256': sha(source/filename), 'upf': header}
    return {'collection': 'SSSP 1.3.0 PBE Precision',
            'doi': 'https://doi.org/10.24435/materialscloud:f3-ym',
            'record': 'https://archive.materialscloud.org/records/rcyfm-68h65',
            'published_checksum_algorithm': 'MD5; local SHA256 additionally recorded',
            'downloads': downloads, 'potentials': selected}


def pilot_input(atoms, identifier, potentials, cutoffs=(80, 600), conv='1.0d-8', mesh='gamma'):
    text = qe_template(atoms, identifier)
    text = text.replace('! TEMPLATE ONLY: environment, pseudopotentials and chemistry approval unresolved',
                        '! QE 7.5 preparation v2; runtime executable/allocation verification required')
    text = text.replace('dftd3_threebody=.true.', 'dftd3_threebody=.false.')
    text = text.replace('__PSEUDO_DIR__', './pseudo').replace('__ECUTWFC_RY__', str(cutoffs[0]))
    text = text.replace('__ECUTRHO_RY__', str(cutoffs[1])).replace('conv_thr=1.0d-8', 'conv_thr='+conv)
    text = text.replace('1 1 1 0 0 0', '2 2 2 0 0 0') if mesh == '2x2x2' else text.replace('K_POINTS automatic\n1 1 1 0 0 0', 'K_POINTS gamma')
    for element, entry in potentials.items():
        text = text.replace('__'+element+'_PBE_UPF__', entry['filename'])
    if '__' in text:
        raise ValueError('Unresolved input placeholder')
    return text


def build(previous, library, output):
    if output.exists():
        raise FileExistsError('Use a new revision directory; preserve prior preparation')
    hashes = json.loads((previous/'file_hashes.json').read_text())
    for name, expected in hashes.items():
        if sha(previous/name) != expected:
            raise ValueError('Sealed v1 changed: '+name)
    old_zip = previous.parent/'UIO66_Frozen_DFT_Review_v1.zip'
    if sha(old_zip) != OLD_ZIP_SHA:
        raise ValueError('Sealed v1 ZIP changed')
    provenance = verify_library(library)
    output.mkdir(parents=True)
    # Copy exact scientific evidence; obsolete input/source templates stay in v1.
    for directory in ('geometries', 'inspection'):
        shutil.copytree(previous/directory, output/directory, copy_function=shutil.copyfile)
    for name in ('manifest.json', 'parent_source.json', 'parent_audit.json', 'assessment_no_dft.json', 'dft_records_empty.json'):
        shutil.copyfile(previous/name, output/name)
    (output/'pseudo').mkdir(); (output/'provenance').mkdir(); (output/'inputs').mkdir()
    for entry in provenance['potentials'].values():
        shutil.copyfile(library/entry['filename'], output/'pseudo'/entry['filename'])
    for name in ('record.json', 'SSSP_1.3.0_PBE_precision.json'):
        shutil.copyfile(library/name, output/'provenance'/name)
    write_json(output/'pseudopotentials.json', provenance)
    manifest = json.loads((output/'manifest.json').read_text())
    inputs = {}; electrons = {}; checks = []
    for key, component in manifest['components'].items():
        atoms = from_record(json.loads((output/component['geometry_file']).read_text()))
        counts = Counter(atoms.get_chemical_symbols())
        nelec = sum(counts[e]*provenance['potentials'][e]['upf']['z_valence'] for e in counts)
        if nelec % 2 != 0:
            raise ValueError('Odd neutral electron count incompatible with fixed nspin=1 branch')
        electrons[key] = {'composition': dict(counts), 'electrons': nelec, 'occupied_bands': int(nelec/2),
                          'caution': 'Even count permits but does not establish insulating closed-shell ground state'}
        variants = {'baseline': ((80,600),'1.0d-8','gamma')}
        if 'H2O_s28' in key and component['kind'] in ('complex','host'):
            variants.update({'cutoff': ((100,750),'1.0d-8','gamma'), 'kmesh': ((80,600),'1.0d-8','2x2x2')})
            if component['kind']=='complex':
                variants['electronic'] = ((80,600),'1.0d-10','gamma')
        for variant, (cutoffs,conv,mesh) in variants.items():
            relative = 'inputs/'+key+'__'+variant+'.in'
            text = pilot_input(atoms,key,provenance['potentials'],cutoffs,conv,mesh)
            (output/relative).write_bytes(text.encode('ascii'))
            reread = read(output/relative,format='espresso-in')
            if not (np.array_equal(reread.numbers, atoms.numbers) and np.array_equal(reread.positions, atoms.positions)
                    and np.array_equal(reread.cell.array, atoms.cell.array)):
                raise ValueError('Input roundtrip changes coordinates/cell')
            checks.append(relative)
            inputs[key+'__'+variant] = {'input': relative, 'component':key, 'variant':variant,
                'sha256':sha(output/relative),'cutoffs_Ry':cutoffs,'conv_thr_Ry':float(conv.replace('d','e')),
                'mesh':mesh, 'electrons':nelec, 'geometry':component['geometry_file']}
    pilot = [k for k in inputs if 'H2O_s28' in k and k.endswith('_complex__baseline')]
    write_json(output/'pilot_plan.json', {'revision':'qe75_sssp130_v2','status':'PREPARATION_ONLY',
        'pilot':pilot,'inputs':inputs,'electron_counts':electrons,'mandatory_baseline_jobs':14,
        'convergence_jobs':10,'optional_guest_jobs':7,'per_job_wall_seconds':14400,
        'orderly_QE_max_seconds':13800,'whole_pilot_wall_seconds':28800,
        'resource_request':{'nodes':1,'physical_cores':32,'memory_GiB':64,'scratch_GiB':100},
        'no_execution_authorized':True})
    write_json(output/'preparation_validation.json',{'v1_files_unchanged':len(hashes),'v1_zip_sha256':OLD_ZIP_SHA,
        'input_exact_roundtrips':checks,'geometry_files_byte_identical':all(sha(p)==sha(previous/'geometries'/p.name)
              for p in (output/'geometries').iterdir()), 'runtime_QE_validation':'NOT RUN; no executable',
        'library_published_checksums':'metadata, full archive, and all five selected potentials verified'})
    return len(checks)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--previous',type=Path,default=Path('artifacts/phase3/uio66_frozen_dft_v1_review'))
    parser.add_argument('--library',type=Path,default=Path('data/external/sssp_1.3.0_pbe_precision'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print('Validated input roundtrips:',build(args.previous,args.library,args.output))
