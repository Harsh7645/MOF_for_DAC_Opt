"""Create a no-overwrite, hash-sealed review bundle and disabled Kaggle notebook."""
import argparse
import json
from pathlib import Path
import shutil
import zipfile
from scripts.run_uio66_matched_diagnostic import sha, validate
from mof_dac.matched_diagnostic import save


NOTEBOOK_CODE = '''# Preparation template only. Enable solely after explicit diagnostic approval.
APPROVED = False
assert APPROVED, 'Not authorized: review the diagnostic and two-T4, two-hour cap first'
import os, sys, time, json, subprocess, zipfile, hashlib, traceback
from pathlib import Path
from kaggle_secrets import UserSecretsClient
W = Path('/kaggle/working')
receipt = W/'matched_allocation_start.json'
assert not receipt.exists(), 'Never refresh an allocation or silently rerun'
START = time.time()
receipt.write_text(json.dumps({'started_epoch': START, 'deadline_epoch': START+7200}))
ROOT = W/'matched_diagnostic_frozen'
OUT = W/'matched_diagnostic_results'
def remaining():
    value = START+7200-time.time()
    if value <= 0: raise TimeoutError('Original allocation exhausted')
    return value
try:
    gpu = subprocess.check_output(['nvidia-smi','--query-gpu=index,name,uuid,memory.total','--format=csv,noheader'],text=True,timeout=remaining())
    (W/'matched_gpu_observation.txt').write_text(gpu)
    assert len(gpu.strip().splitlines()) == 2 and all('T4' in x for x in gpu.splitlines())
    bundles = list(Path('/kaggle/input').rglob('UIO66_Matched_Diagnostic_v1.zip'))
    assert len(bundles) == 1 and not ROOT.exists()
    with zipfile.ZipFile(bundles[0]) as z:
        for name in z.namelist(): assert (ROOT/name).resolve().is_relative_to(ROOT.resolve())
        z.extractall(ROOT)
    release = json.loads((ROOT/'release.json').read_text())
    for name,digest in release['sha256'].items():
        p = ROOT/name
        assert hashlib.sha256(p.read_bytes()).hexdigest() == digest, name
    os.chdir(ROOT)
    env = dict(os.environ, PYTHONPATH=str(ROOT), OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    with (W/'matched_install.log').open('w') as log:
        subprocess.run([sys.executable,'-m','pip','install','fairchem-core==2.23.0','ase==3.26.0'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=remaining())
    subprocess.run([sys.executable,'-m','scripts.run_uio66_matched_diagnostic','--manifest',str(ROOT/'manifest.json')],env=env,check=True,timeout=remaining())
    env['HF_TOKEN'] = UserSecretsClient().get_secret('HF_TOKEN')
    download = "from huggingface_hub import hf_hub_download; from pathlib import Path; import json; p=json.loads(Path('manifest.json').read_text()); q=hf_hub_download('facebook/UMA','checkpoints/uma-s-1p2p1.pt',revision=p['checkpoint_revision']); Path('/kaggle/working/matched_checkpoint_path.txt').write_text(q)"
    subprocess.run([sys.executable,'-c',download],env=env,check=True,timeout=remaining())
    checkpoint = (W/'matched_checkpoint_path.txt').read_text()
    env.pop('HF_TOKEN',None)
    command = [sys.executable,'-m','scripts.run_uio66_matched_diagnostic','--manifest',str(ROOT/'manifest.json'),
               '--output',str(OUT),'--checkpoint',checkpoint,'--execute','--approved-wall-hours','2',
               '--allocation-start-epoch',str(START)]
    # Controller owns the hard deadline and terminates both model workers.
    subprocess.run(command,env=env,check=True)
    subprocess.run([sys.executable,'-m','scripts.assess_uio66_matched_diagnostic','--manifest',str(ROOT/'manifest.json'),'--output',str(OUT)],env=env,check=True)
except BaseException:
    (W/'matched_workflow_error.txt').write_text(traceback.format_exc())
    raise
finally:
    # Saved private batch output: retain setup failures and partial raw trajectories too.
    with zipfile.ZipFile(W/'matched_diagnostic_evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in W.rglob('*'):
            if p.is_file() and p.suffix != '.zip' and (p.is_relative_to(OUT) or p.parent == W or p.is_relative_to(ROOT)):
                z.write(p,p.relative_to(W))
'''


def freeze(source, output):
    plan=validate(source/'manifest.json');output.mkdir(parents=True,exist_ok=False)
    version='v2' if plan['protocol'].endswith('_v2') else 'v1'
    shutil.copy2(source/'manifest.json',output/'manifest.json');shutil.copytree(source/'poses',output/'poses')
    if version=='v2':
        shutil.copytree(source/'mapping_preview',output/'mapping_preview')
        for name in ('mapping_preview.json','cost_estimate.json'):shutil.copy2(source/name,output/name)
    (output/'reference').mkdir()
    shutil.copy2('artifacts/phase3/uio66_saved_pilot_results_20261004/raw/uio66_sampling_authorized/force02/structures/uio66_110111_tight_CO2_31.traj',
                 output/'reference/uio66_110111_tight_CO2_31.traj')
    files=list(Path('mof_dac').glob('*.py'))+[Path('scripts')/name for name in (
        'run_uio66_matched_diagnostic.py','assess_uio66_matched_diagnostic.py','prepare_uio66_matched_diagnostic.py',
        'analyze_uio66_diagnostic.py','summarize_uio66_diagnostic_evidence.py','freeze_uio66_matched_diagnostic.py','revise_uio66_shared_host.py')]
    files += [Path('tests/test_matched_diagnostic.py'),Path('docs/UIO66_MATCHED_DIAGNOSTIC.md')]
    if version=='v2':files += [Path('tests/test_shared_rigid_host.py'),Path('docs/UIO66_MATCHED_DIAGNOSTIC_V2.md')]
    for src in files:
        dest=output/src;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
    code=NOTEBOOK_CODE.replace('UIO66_Matched_Diagnostic_v1.zip',f'UIO66_Matched_Diagnostic_{version}.zip')
    if version=='v2':
        code=code.replace('value = START+7200-time.time()', 'value = START+6900-time.time()')
        code=code.replace("str(OUT)],env=env,check=True)", "str(OUT)],env=env,check=True,timeout=max(1,START+7050-time.time()))")
        code=code.replace("'w',zipfile.ZIP_DEFLATED)", "'w',zipfile.ZIP_STORED)")
        for name in ('matched_allocation_start','matched_diagnostic_frozen','matched_diagnostic_results',
                     'matched_gpu_observation','matched_install','matched_checkpoint_path','matched_workflow_error','matched_diagnostic_evidence'):
            code=code.replace(name,name+'_v2')
    notebook={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'python3','display_name':'Python 3'}},
      'cells':[{'cell_type':'markdown','metadata':{},'source':['# Matched geometry diagnostic — review only\nPrivate saved batch; two T4s, original two-hour deadline. No expansion/refit/DFT.']},
               {'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':code.splitlines(True)}]}
    save(output/'matched_diagnostic.ipynb',notebook)
    save(Path('kaggle/uio66_matched_diagnostic_v2.ipynb' if version=='v2' else 'kaggle/uio66_matched_diagnostic.ipynb'),notebook)
    save(output/'release.json',{'status':'review bundle; no compute authorization','sha256':{p.relative_to(output).as_posix():sha(p) for p in output.rglob('*') if p.is_file()}})
    bundle=output.parent/f'UIO66_Matched_Diagnostic_{version}.zip'
    with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED) as z:
        for p in output.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(output));p.chmod(0o444)
    bundle.chmod(0o444)
    print(json.dumps({'bundle':str(bundle),'sha256':sha(bundle),'bytes':bundle.stat().st_size,'manifest_sha256':sha(output/'manifest.json')}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();freeze(a.source,a.output)
