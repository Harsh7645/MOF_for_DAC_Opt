"""Read-only, stdlib-only review of the pinned baseline14 ZIP (Python >=3.10).
Never imports launch controllers or invokes QE, MPI, UMA, or systemd.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import xml.etree.ElementTree as ET
import zipfile

ARCHIVE_SHA256 = '8f7fbf7abc4839117595f18e14b42db05d8392547cede539232ae937e99bf0d7'
RY_EV = 13.605693122994017
BOHR_A = 0.529177210903
SYMBOLS = {1: 'H', 6: 'C', 7: 'N', 8: 'O', 40: 'Zr'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_member(name):
    p = PurePosixPath(name)
    require(bool(name) and not p.is_absolute() and '..' not in p.parts
            and '\\' not in name and ':' not in name, 'Unsafe ZIP member: ' + name)
    return p


def total_forces(text):
    headers = list(re.finditer(r'Forces acting on atoms \(cartesian axes, Ry/au\):', text))
    require(len(headers) == 1, 'Expected one total-force block')
    rows = []
    for line in text[headers[0].end():].splitlines():
        if not line.strip():
            continue
        if not line.strip().startswith('atom'):
            break
        match = re.fullmatch(r'\s*atom\s+(\d+)\s+type\s+(\d+)\s+force\s*=\s*(\S+)\s+(\S+)\s+(\S+)\s*', line)
        require(match is not None, 'Malformed force row')
        rows.append((int(match[1]), int(match[2]),
                     [float(match[i].replace('D', 'E')) for i in (3, 4, 5)]))
    return rows


def close_vectors(actual, expected, tolerance, label):
    require(len(actual) == len(expected), label + ': vector count')
    for a, b in zip(actual, expected):
        require(len(a) == len(b) == 3, label + ': component count')
        require(all(math.isfinite(x) and math.isfinite(y) and abs(x-y) < tolerance
                    for x, y in zip(a, b)), label + ': mismatch')


def review(archive, output, extract_to=None):
    require(hashlib.sha256(archive.read_bytes()).hexdigest() == ARCHIVE_SHA256,
            'External archive SHA256 mismatch')
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        require(len(names) == len(set(names)), 'Duplicate ZIP members')
        for info in z.infolist():
            safe_member(info.filename)
            require((info.external_attr >> 16) & 0o170000 != 0o120000, 'ZIP symlink')
        hashes = json.loads(z.read('SHA256SUMS.json'))
        require(set(names) == set(hashes) | {'SHA256SUMS.json'}, 'Payload inventory mismatch')
        require(len(hashes) == 471, 'Expected 471 payloads')
        for name, digest in hashes.items():
            require(hashlib.sha256(z.read(name)).hexdigest() == digest, 'Payload hash: ' + name)
        read = lambda p: z.read(p).decode('utf-8')
        data = lambda p: json.loads(read(p))
        manifest = data('frozen-package/manifest.json')
        frozen_hashes = data('frozen-package/file_hashes.json')
        comparisons = data('evidence/comparisons.json')
        force_report = data('evidence/force-comparisons.json')
        valences = {}
        for name in names:
            if name.startswith('pseudo/'):
                require(hashes[name] == frozen_hashes[name], 'Frozen PP pin: ' + name)
                s = read(name)
                if 'Z valence' in s:
                    el, val = 'Zr', float(re.search(r'([\d.E+-]+)\s+Z valence', s)[1])
                else:
                    el = re.search(r'element\s*=\s*"\s*(\w+)\s*"', s)[1]
                    val = float(re.search(r'z_valence\s*=\s*"\s*([\d.Ee+-]+)', s)[1])
                valences[el] = val
        rows, force_rows, all_forces = [], [], {}
        xmls = sorted(n for n in names if n.startswith('raw/') and n.endswith('/data-file-schema.xml'))
        require(len(xmls) == 14, 'Expected 14 final XML files')
        for xml_path in xmls:
            root = xml_path.split('/scratch/')[0]
            ident = xml_path.split('/')[-2].removesuffix('.save')
            comp = manifest['components'][ident]
            geo_path = 'frozen-package/' + comp['geometry_file']
            require(hashes[geo_path] == frozen_hashes[comp['geometry_file']], 'Frozen geometry pin')
            geo = data(geo_path)
            parent = data('frozen-package/' + manifest['components'][comp['pose']+'_complex']['geometry_file'])
            require(geo['cell_A'] == parent['cell_A'], 'Matching cell')
            require(geo['positions_A'] == [parent['positions_A'][i] for i in comp['source_atom_indices']], 'Host correspondence')
            symbols = [SYMBOLS[n] for n in geo['numbers']]
            ne = sum(valences[s] for s in symbols) - comp['charge']
            inp = root + '/input.in'
            require(hashes[inp] == data(root+'/execution-started.json')['input_sha256'], 'Executed input pin')
            text, stderr = read(root+'/stdout.log'), read(root+'/stderr.log')
            x = ET.fromstring(read(xml_path))
            require(x.attrib['Units'] == 'Hartree atomic units', 'XML units')
            for node in x.iter():
                node.tag = node.tag.split('}')[-1]
            get = lambda p: x.findtext(p).strip()
            require(get('exit_status') == '0' and get('output/convergence_info/scf_conv/convergence_achieved') == 'true', 'SCF not complete')
            steps = int(get('output/convergence_info/scf_conv/n_scf_steps'))
            error = 2 * float(get('output/convergence_info/scf_conv/scf_error'))
            require(math.isfinite(error) and 0 <= error <= 1e-8, 'SCF threshold')
            require('JOB DONE.' in text and re.search(r'convergence has been achieved in\s*'+str(steps)+r' iterations', text), 'Text completion')
            require(not re.search(r'convergence NOT achieved|Error in routine|MPI_ABORT|segmentation fault', text+stderr, re.I), 'Fatal output')
            require(not re.search(r'eigenvalues not converged|c_bands.*not converged', re.split(r'iteration #\s*\d+',text)[-1], re.I), 'Final diagonalization')
            require(float(get('output/band_structure/nelec')) == ne, 'Electron count')
            for path, value in [('output/basis_set/ecutwfc',40), ('output/basis_set/ecutrho',300), ('input/electron_control/conv_thr',5e-9), ('input/electron_control/mixing_beta',.3), ('input/bands/tot_charge',0)]:
                require(math.isclose(float(get(path)), value, rel_tol=1e-12, abs_tol=1e-15), path)
            for path, value in [('parallel_info/nprocs','4'), ('parallel_info/nthreads','1'), ('input/electron_control/diagonalization','cg'), ('input/electron_control/mixing_ndim','4'), ('input/bands/occupations','fixed'), ('output/basis_set/gamma_only','true'), ('output/dft/functional','PBE'), ('output/dft/vdW/vdw_corr','grimme-d3'), ('output/dft/vdW/dftd3_version','4'), ('output/dft/vdW/dftd3_threebody','false'), ('output/magnetization/lsda','false')]:
                require(get(path) == value, path)
            for section in ('input','output'):
                st = x.find(section+'/atomic_structure')
                atoms = st.findall('atomic_positions/atom')
                require([a.get('name') for a in atoms] == symbols, 'Atom identities')
                close_vectors([[float(v)*BOHR_A for v in a.text.split()] for a in atoms], geo['positions_A'], 2e-8, 'Coordinates')
                close_vectors([[float(v)*BOHR_A for v in st.findtext('cell/'+k).split()] for k in ('a1','a2','a3')], geo['cell_A'], 2e-8, 'Cell')
            energies = re.findall(r'!\s+total energy\s*=\s*(\S+)\s+Ry', text)
            ha = float(get('output/total_energy/etot'))
            require(len(energies) == 1 and math.isfinite(ha) and abs(float(energies[0])-2*ha) < 5.1e-9, 'Text/XML energy')
            require(ha == comparisons['accepted_converged_results'][ident]['energy_Ha'], 'Reported energy')
            raw_forces = total_forces(text)
            values = [2*float(v) for v in get('output/forces').split()]
            require(len(raw_forces) == len(symbols) and len(values) == 3*len(symbols), 'Force count')
            xml_forces = [values[i:i+3] for i in range(0,len(values),3)]
            close_vectors([r[2] for r in raw_forces], xml_forces, 5.1e-9, 'Total forces Ry/bohr')
            types = [s.get('name') for s in x.findall('input/atomic_species/species')]
            forces = [[v*RY_EV/BOHR_A for v in row] for row in xml_forces]
            for i, (r, f) in enumerate(zip(raw_forces, forces)):
                require(r[0] == i+1 and 1 <= r[1] <= len(types) and types[r[1]-1] == symbols[i], 'Force atom mapping')
                force_rows.append([ident,i+1,comp['source_atom_indices'][i],symbols[i],*r[2],*xml_forces[i],*f])
            maxforce = max(math.sqrt(sum(v*v for v in f)) for f in forces)
            require(abs(maxforce-force_report['per_geometry'][ident]['DFT_force_statistics']['max_vector_norm_eV_A']) < 1e-12, 'Force report maximum')
            require(comp['source_atom_indices'] == force_report['per_geometry'][ident]['source_atom_indices'], 'Force report mapping')
            all_forces[ident] = forces
            neg = [float(v) for v in re.findall(r'negative rho \(up, down\):\s*(\S+)', text)]
            samples = [json.loads(line) for line in read(root+'/resources.jsonl').splitlines() if line]
            require(bool(samples), 'Missing resources')
            for s in samples:
                require(s['swap_current'] == 0 and not any(s['memory_events'].values()) and not any(s['pids_events'].values()), 'Resource event')
            rows.append(dict(manifest_id=ident,atoms=len(symbols),electrons=ne,iterations=steps,error_Ry=error,energy_Ha=ha,force_max_eV_A=maxforce,negative_pseudocharge_e=neg,sampled_peak_GiB=max(s['memory_peak'] for s in samples)/2**30))
        require({r['manifest_id'] for r in rows} == {k for k,v in manifest['components'].items() if v['kind'] in ('complex','host')}, 'Mandatory inventory')
        energies = {r['manifest_id']:r['energy_Ha'] for r in rows}
        deltas = []
        for d in comparisons['differences']:
            new = {'first':d['first'], 'second':d['second']}
            for kind in ('complex','host'):
                ids = [d[k]+'_'+kind for k in ('first','second')]
                value = (energies[ids[1]]-energies[ids[0]])*2*RY_EV
                key = 'DFT_delta_'+kind+'_eV'
                require(abs(value-d[key]) < 1e-10, 'Energy comparison')
                new[key] = value
                uma = [manifest['components'][i]['uma'] for i in ids]
                if all(u and u.get('energy_eV') is not None for u in uma):
                    key = 'UMA_delta_'+kind+'_eV'
                    new[key] = uma[1]['energy_eV']-uma[0]['energy_eV']
                    require(abs(new[key]-d[key]) < 1e-10, 'UMA comparison')
            new['DFT_delta_guest_associated_eV'] = new['DFT_delta_complex_eV']-new['DFT_delta_host_eV']
            require(abs(new['DFT_delta_guest_associated_eV']-d['DFT_delta_guest_associated_eV']) < 1e-10, 'Guest-associated comparison')
            deltas.append(new)
        # Reconstruct archived UMA force component differences where measured.
        for ident, forces in all_forces.items():
            uma = manifest['components'][ident]['uma']
            if uma and uma.get('forces_eV_A') is not None:
                delta = [[v-u for v,u in zip(f,g)] for f,g in zip(forces,uma['forces_eV_A'])]
                close_vectors(delta, force_report['per_geometry'][ident]['DFT_minus_archived_UMA_components'], 1e-12, 'UMA force differences')
        for pair in force_report['between_checkpoints']:
            first, second = pair['first'], pair['second']
            require(manifest['components'][first]['source_atom_indices'] == manifest['components'][second]['source_atom_indices'], 'Paired force mapping')
            delta = [[b-a for a,b in zip(f,g)] for f,g in zip(all_forces[first],all_forces[second])]
            close_vectors(delta, pair['second_minus_first_components'], 1e-12, 'Paired force components')
        output.mkdir(parents=True, exist_ok=False)
        summary = dict(passed=True,archive_sha256=ARCHIVE_SHA256,payloads_verified=len(hashes),jobs=rows,force_vectors=len(force_rows),differences=deltas,limitations='SCF only. Numerical/physical/UMA accuracy and Phase 3 remain unresolved. Resource values here are sampled; original lifetime service accounting is retained in evidence. Historical report maximum-force wording is corrected in the tracked Windows guide.')
        (output/'review.json').write_text(json.dumps(summary,indent=2)+'\n', encoding='utf-8')
        with (output/'forces.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f)
            w.writerow(['manifest_id','QE_atom_1based','source_atom_0based','symbol','text_Fx_Ry_bohr','text_Fy_Ry_bohr','text_Fz_Ry_bohr','XML_Fx_Ry_bohr','XML_Fy_Ry_bohr','XML_Fz_Ry_bohr','Fx_eV_A','Fy_eV_A','Fz_eV_A'])
            w.writerows(force_rows)
        if extract_to is not None:
            extract_to.mkdir(parents=True, exist_ok=False)
            # Fresh directory; all member paths and types checked above.
            z.extractall(extract_to)
        return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', type=Path, default=Path('artifacts/phase3/uio66_qe_baseline14_review_v1.zip'))
    p.add_argument('--output', type=Path, required=True, help='New directory; never overwrite evidence')
    p.add_argument('--extract-to', type=Path, help='Optional new extraction directory')
    args = p.parse_args()
    result = review(args.archive, args.output, args.extract_to)
    print(f"PASS: {result['payloads_verified']} payloads, {len(result['jobs'])} SCFs, {result['force_vectors']} force vectors; {args.output}")


if __name__ == '__main__':
    main()
