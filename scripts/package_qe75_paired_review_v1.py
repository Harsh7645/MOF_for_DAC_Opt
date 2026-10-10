"""Verify retained diagnostics and package complete evidence; never invokes QE."""
from pathlib import Path
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
import zipfile
from assess_qe75_rho625_v1 import parse
from run_qe_water_pilot import BOHR_A

ROOT=Path(__file__).resolve().parents[1]


def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    ev=ROOT/'evidence/qe75-fedora-completion-v5'
    pkg=ROOT/'artifacts/phase3/uio66_frozen_dft_v2_qe75_fedora_verified01'
    runs={'600':ROOT/'local/qe75-fedora-completion-v3/run01', '625':ROOT/'local/qe75-rho625-v1/run02'}
    for name in ['evidence/qe75-fedora-completion-v3/raw-file-hashes.json','evidence/qe75-rho625-run02/raw-file-hashes.json']:
        for file,pin in json.loads((ROOT/name).read_text()).items():
            assert sha(ROOT/file)==pin,file
    baseline=(runs['600']/'input.in').read_text()
    assert (runs['625']/'input.in').read_text()==baseline.replace('ecutrho=600','ecutrho=625').replace('max_seconds=12948','max_seconds=1350')
    parsed={k:parse(p/'stdout.log') for k,p in runs.items()}
    for k,p in runs.items():
        (p/'stderr.log').read_text()  # Inspect complete stderr, preserved below.
        assert [v['negative_electrons'] for v in parsed[k]['observations']]==[.3659,.3741,.3836,.3887,.394]
        assert parsed[k]['completed_iterations']==4 and not parsed[k]['SCF_convergence_reported']
    manifest=json.loads((pkg/'manifest.json').read_text())
    comp=manifest['components']['uio66_110111_H2O_s28_f0.010_complex']
    geo=json.loads((pkg/comp['geometry_file']).read_text())
    symbols=next(p for p in manifest['poses'] if p['id']==comp['pose'])['atom_symbols']
    xml=next((runs['625']/'scratch').glob('*.save/data-file-schema.xml'))
    rt=ET.parse(xml).getroot()
    for n in rt.iter():n.tag=n.tag.split('}')[-1]
    assert rt.attrib['Units']=='Hartree atomic units'
    get=lambda path:rt.findtext(path).strip()
    assert get('output/convergence_info/scf_conv/convergence_achieved')=='false'
    assert get('output/convergence_info/scf_conv/n_scf_steps')=='4'
    assert float(get('output/band_structure/nelec'))==522
    assert float(get('output/basis_set/ecutrho'))==312.5
    assert abs(float(get('output/convergence_info/scf_conv/scf_error'))*2-.262183)<1e-8
    checks={}
    for sec in ['input','output']:
        st=rt.find(sec+'/atomic_structure');atoms=st.findall('atomic_positions/atom')
        assert [n.attrib['name'] for n in atoms]==symbols
        pos=[[float(x)*BOHR_A for x in n.text.split()] for n in atoms]
        cell=[[float(x)*BOHR_A for x in st.findtext('cell/'+k).split()] for k in ['a1','a2','a3']]
        for label,actual,expected in [('coordinates',pos,geo['positions_A']),('cell',cell,geo['cell_A'])]:
            error=max(abs(x-y) for r,s in zip(actual,expected) for x,y in zip(r,s))
            assert error<2e-8
            checks[sec+'_'+label+'_max_error_A']=error
    inventory={}
    for name in ['local/qe75-fedora-v1/smoke01','local/qe75-fedora-feasibility-v2/run01','local/qe75-fedora-completion-v3/run01']:
        p=ROOT/name
        inventory[name]={'xml':[str(f.relative_to(ROOT)) for f in (p/'scratch').rglob('data-file-schema.xml')],
                         'density':[str(f.relative_to(ROOT)) for f in (p/'scratch').rglob('charge-density.dat')],
                         'files':[str(f.relative_to(p)) for f in (p/'scratch').rglob('*') if f.is_file()]}
    audit={'material_discrepancy':False,'raw_hashes_verified':{'600':25,'625':29},
           'full_stdout_stderr_read':True,'parsed_outputs':parsed,'XML625_checks':checks,
           'checkpoint_inventory':inventory,'restart_decision':'Clean start;600SCF v2/v3 lack completeXML/density; initialization-only checkpoint is not anSCFrestart.625checkpoint excluded.',
           'reviewer_status':'User-supplied provisional recommendation to continue first frozen geometry at80/600Ry. No separate reviewer document found; not verification of physical/numerical accuracy.'}
    (ev/'preflight-evidence-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    review=ROOT/'artifacts/phase3/uio66_qe_review_600_625_v1';review.mkdir(exist_ok=False)
    for tag,p in runs.items():
        d=review/('rho'+tag);d.mkdir()
        for name in ['input.in','stdout.log','stderr.log']:shutil.copyfile(p/name,d/name)
        xs=list((p/'scratch').rglob('data-file-schema.xml'))
        if xs:shutil.copyfile(xs[0],d/'data-file-schema.xml')
        else:(d/'XML_NOT_AVAILABLE.txt').write_text('No XML exists for this interrupted600Ry SCF. No XML substituted from another run.\n')
    shutil.copyfile(ROOT/'docs/UIO66_QE75_RHO625_RESULTS_V1.md',review/'PAIRED_RESULTS.md')
    shutil.copyfile(ev/'preflight-evidence-audit.json',review/'LOCAL_VERIFICATION.json')
    (review/'REVIEW_STATUS.md').write_text('''# Reviewer evidence package

Verified local evidence: exact executed600/625Ry inputs, complete stdout/stderr,
available625Ry XML, paired report and local checks. Missing600Ry SCF XML is explicit.
Both outputs are unconverged; no scientific energy is accepted.

Provisional recommendation supplied by the user: continue FIRST frozen water
complex at80/600Ry towardSCFconvergence. No separate reviewer document was supplied
or found. This interpretation does not establish accuracy or remove later review.

Authorized: ONE first-geometry attempt, exact model/UPFs/PBE-D3BJ/charge/spin/fixed
occupations/conv_thr1e-8/mixing_beta0.3;4physicalcores;11GiBhard/10GiBhigh/zero job
swap/96tasks;4h including preparation/cleanup. Nonzero negativepseudocharge alone
is not a stop condition. No625restart,secondgeometry,expansion or retry.
''')
    hashes={str(p.relative_to(review)):sha(p) for p in sorted(review.rglob('*')) if p.is_file()}
    (review/'SHA256SUMS.json').write_text(json.dumps(hashes,indent=2)+'\n')
    zpath=review.with_suffix('.zip')
    with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(review.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(review))
    receipt={'archive':str(zpath.relative_to(ROOT)),'sha256':sha(zpath),'files':len(hashes)+1,'no_QE_launched':True}
    (ev/'review-package-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'audit_passed':True,'XML_checks':checks,'review_package':receipt,'restart':audit['restart_decision']},indent=2))


if __name__=='__main__':main()
