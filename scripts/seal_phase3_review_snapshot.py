"""Seal an allowlisted review snapshot. No scientific execution; never overwrite a seal."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

import ase
import matplotlib
import numpy

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=Path('plans/phase3-review-response-v2')
METHODS=Path('plans/phase3-methods-scope-v1')
NEW_DOCS=['PHASE3_REVIEW_RESPONSE_V2.md','PHASE3_SCIENTIFIC_CLARIFICATIONS_V2.md',
          'CHEMISTRY_INSPECTION_REVIEW_V2.md','MANUSCRIPT_METHODS_RESULTS_V2.md','PHASE3_CLOSURE_CHECKLIST_V2.md']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(archive):
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        manifest=json.loads(z.read('SNAPSHOT_MANIFEST.json'))
        assert set(z.namelist())==set(manifest['files'])|{'SNAPSHOT_MANIFEST.json'}
        for name,expected in manifest['files'].items():
            assert digest(z.read(name))==expected,name
    return len(manifest['files'])


def seal():
    destination=ROOT/PACKAGE/'snapshot.zip'
    if destination.exists():raise FileExistsError('Immutable snapshot already exists; use a new version for changes')
    selected=set()
    def add(path):
        p=ROOT/path
        if p.is_dir():selected.update(f.relative_to(ROOT).as_posix() for f in p.rglob('*') if f.is_file())
        else:
            assert p.is_file(),path
            selected.add(p.relative_to(ROOT).as_posix())
    add(PACKAGE/'inspection')
    for name in ('README.md','EVIDENCE_INDEX.md','reviewer_provenance.json','review_status.json','validation.json'):
        add(PACKAGE/name)
    for name in NEW_DOCS:add(Path('docs')/name)
    add(METHODS/'evidence')
    add(METHODS/'scope_receipt.json')
    old=json.loads((ROOT/METHODS/'scope_receipt.json').read_text())
    for path in old['outputs']:add(Path(path))
    preparation=json.loads((ROOT/PACKAGE/'inspection/receipt.json').read_text())
    for path in preparation['inputs']:add(Path(path))
    for path in ['docs/UIO66_QE75_BASELINE14_RESULTS_V1.md','docs/ODAC25_REQUEST_STATUS.json',
                 '.planning/ROADMAP_pre_scope_20261027.md','mof_dac/__init__.py','mof_dac/instances.py',
                 'mof_dac/formulation.py','mof_dac/phase3.py','mof_dac/sampling.py','mof_dac/optimizers.py',
                 'mof_dac/snn.py','mof_dac/gurobi.py','scripts/benchmark_uio66_fit.py',
                 'scripts/analyze_uio66_development.py','scripts/plot_uio66_development.py',
                 'scripts/prepare_uio66_sampling_pilot.py','scripts/seal_phase3_review_snapshot.py',
                 'tests/test_phase3_review_response.py','plans/uio66-offline-development-v1/protocol.json',
                 'plans/uio66-offline-development-v1/results/bootstrap_fits.json',
                 'plans/uio66-offline-development-v1/results/residuals_by_pattern.csv']:
        add(Path(path))
    payload={}
    secret=re.compile(rb'hf_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----')
    for name in sorted(selected):
        assert not ({'configs','local','later_responses','.git','.ssh'} & set(Path(name).parts)),name
        assert Path(name).suffix not in ('.pt','.pem','.key','.ipynb') and Path(name).name!='.env',name
        data=(ROOT/name).read_bytes()
        if Path(name).suffix in ('.md','.json','.py','.csv','.txt'):
            assert not secret.search(data),'Credential-shaped content in '+name
        payload[name]=data
    links=[]
    checked_docs=[Path('docs')/n for n in NEW_DOCS]+[PACKAGE/'README.md',PACKAGE/'EVIDENCE_INDEX.md']
    for p in checked_docs:
        text=re.sub(r'`[^`]*`','',payload[p.as_posix()].decode('utf-8'))
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if '://' in target or target.startswith('#'):continue
            q=((ROOT/p.parent)/target.split('#')[0]).resolve().relative_to(ROOT).as_posix()
            assert q in payload or any(n.startswith(q.rstrip('/')+'/') for n in payload),(p.as_posix(),target)
            links.append({'from':p.as_posix(),'to':q})
    manifest={'version':'phase3-review-response-v2','date':'2026-10-27',
        'source_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'worktree_state':'pre-existing staged changes present; no commit made; actual source bytes identified by files below',
        'environment':{'python':sys.version.split()[0],'numpy':numpy.__version__,'matplotlib':matplotlib.__version__,'ase':ase.__version__},
        'files':{name:digest(data) for name,data in payload.items()},'review_entrypoint_links':links,
        'boundary':'Exact review evidence and offline formatting; not full scientific-run archives, weights or launch state',
        'approval':'No qualified chemistry approval or independent final review documented; Phase 3 incomplete',
        'later_responses':'Outside archive; record reviewed ZIP SHA256; never modify this archive'}
    with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in payload.items():z.writestr(name,data)
        z.writestr('SNAPSHOT_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    count=verify(destination);checksum=digest(destination.read_bytes())
    receipt={'archive':destination.relative_to(ROOT).as_posix(),'sha256':checksum,'bytes':destination.stat().st_size,
             'payloads':count,'verified_payload_hashes':count,'review_links':len(links),'source_HEAD':manifest['source_HEAD'],
             'credentials_scan':'allowlist plus high-specificity token/private-key scan passed; no launch configs included',
             'phase3_status':'incomplete; Q1/Q2 and independent final review pending'}
    (destination.parent/'snapshot_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (destination.parent/'snapshot.zip.sha256').write_text(checksum+'  snapshot.zip\n',encoding='ascii')
    print(json.dumps(receipt))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',type=Path)
    args=parser.parse_args()
    if args.verify:print(json.dumps({'verified_payload_hashes':verify(args.verify)}))
    else:seal()
