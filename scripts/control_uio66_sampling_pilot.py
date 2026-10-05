"""Approved eight-design run; shared deadline and retained raw/failed outputs."""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b''):
            digest.update(block)
    return digest.hexdigest()


def stop_reason(deadline, stop_file):
    if stop_file.exists():
        return 'chemistry/user stop: ' + stop_file.read_text()[:1000]
    if time.time() >= deadline:
        return 'reviewed 4.2-hour allocation deadline reached'
    return None


def terminate(process):
    if process.poll() is None:
        if os.name == 'posix':
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            if os.name == 'posix':
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait()


def monitor(processes, deadline, stop_file):
    """Only terminate owned process groups; always preserve files already written."""
    try:
        while any(p.poll() is None for p in processes):
            reason = stop_reason(deadline, stop_file)
            if reason:
                raise RuntimeError(reason)
            if any(p.poll() not in (None, 0) for p in processes):
                raise RuntimeError('Worker failed; stop allocation and retain partial outputs')
            time.sleep(.5)
        if any(p.returncode for p in processes):
            raise RuntimeError('Worker failed; retain outputs')
    finally:
        for process in processes:
            terminate(process)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--bundle-sha256', required=True)
    parser.add_argument('--allocation-start-utc', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = Path(args.output).resolve()
    if out.exists():
        raise ValueError('Choose a new output root; no overwrite/resume')
    start = datetime.fromisoformat(args.allocation_start_utc.replace('Z', '+00:00'))
    if start.tzinfo is None or start.timestamp()>time.time():
        raise ValueError('Allocation start requires a past timezone-aware timestamp')
    deadline = start.timestamp() + 4.2*3600
    stop_file = out/'STOP'
    if stop_reason(deadline,stop_file):
        raise ValueError('No budget remaining')
    manifest_path = root/'bundle_manifest.json'
    manifest = json.loads(manifest_path.read_text())['sha256']
    if sha(args.bundle)!=args.bundle_sha256:
        raise ValueError('Frozen bundle hash mismatch')
    for name,digest in manifest.items():
        target = (root/name).resolve()
        if not target.is_relative_to(root) or sha(target)!=digest:
            raise ValueError('Frozen source/input hash mismatch: '+name)
    plan_path = root/'data/design/uio66_sampling_pilot_v2.json'
    plan = json.loads(plan_path.read_text())
    if sha(plan_path)!='f5b4cd746c471838b141c91d88442026ab4f1bcc0bf7548d5665a8924724f68e' \
            or sha(args.checkpoint)!=plan['checkpoint_sha256']:
        raise ValueError('Preregistered plan or pinned checkpoint changed')
    import torch
    if not torch.cuda.is_available() or torch.cuda.device_count()!=2 or any(
            'T4' not in torch.cuda.get_device_name(i) for i in range(2)):
        raise ValueError('Reviewed allocation requires exactly two T4 GPUs')
    if version('fairchem-core')!='2.23.0':
        raise ValueError('Expected fairchem-core 2.23.0')
    out.mkdir()
    receipt = {'scope':'512 guest starts plus 16 registered force continuations; no refit/DFT/expansion',
        'allocation_start_utc':start.isoformat(), 'deadline_utc':datetime.fromtimestamp(deadline,timezone.utc).isoformat(),
        'gpu_names':[torch.cuda.get_device_name(i) for i in range(2)], 'cpu_threads_per_worker':1,
        'main_workers':4,'workers_per_gpu':2,'force_workers':1,'force_gpu':0,
        'budget_seconds':15120,'bundle_sha256':args.bundle_sha256,'manifest_sha256':sha(manifest_path),
        'plan_sha256':sha(plan_path),'checkpoint_sha256':plan['checkpoint_sha256'],
        'checkpoint_revision':plan['checkpoint_revision'],'file_sha256':manifest,
        'packages':{n:version(n) for n in ('torch','fairchem-core','ase','numpy','scipy')},
        'python':sys.version,'nvidia_smi':subprocess.check_output(['nvidia-smi'],text=True),
        'chemistry_review':'pending expert validation; no material issue reported before launch',
        'status':'preflight passed; main starting','commands':[]}
    def save():
        temporary = out/'allocation.tmp'
        temporary.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
        temporary.replace(out/'allocation.json')
    save()
    frozen = out/'frozen'
    frozen.mkdir()
    shutil.copy2(args.bundle,frozen/'execution_bundle.zip')
    shutil.copy2(manifest_path,frozen/'bundle_manifest.json')
    (frozen/'checkpoint_identity.json').write_text(json.dumps({k:receipt[k] for k in
        ('checkpoint_sha256','checkpoint_revision','plan_sha256','bundle_sha256')},indent=2)+'\n')
    for file in frozen.iterdir():
        file.chmod(0o444)
    environment = dict(os.environ,PYTHONPATH=str(root),OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
    def command(module,extra):
        return [sys.executable,'-m',module,'--plan',str(plan_path),*extra]
    def launch(cmd,log_name,gpu=None):
        reason = stop_reason(deadline,stop_file)
        if reason:
            raise RuntimeError(reason)
        env = environment if gpu is None else dict(environment,CUDA_VISIBLE_DEVICES=str(gpu))
        receipt['commands'].append({'argv':cmd,'gpu':gpu,'started_utc':datetime.now(timezone.utc).isoformat()})
        save()
        with (out/log_name).open('w') as log:
            return subprocess.Popen(cmd,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    reports = [out/f'worker{i}'/'adsorption.json' for i in range(4)]
    owned = []
    try:
        for i,report in enumerate(reports):
            ids = [r['id'] for r in plan['configurations'][2*i:2*i+2]]
            owned.append(launch(command('scripts.run_uio66_sampling_pilot',[
                '--execute','--checkpoint',args.checkpoint,'--ids',*ids,'--output',str(report)]),f'worker{i}.log',i%2))
        monitor(owned,deadline,stop_file)
        receipt['status']='main completed; auditing all eight'
        save()
        audit_args = ['--reports',*map(str,reports),'--output',str(out/'loose_assessment.json')]
        monitor([launch(command('scripts.assess_uio66_sampling_pilot',audit_args),'loose_assessment.log')],deadline,stop_file)
        assessment = json.loads((out/'loose_assessment.json').read_text())
        if any(r['status']!='complete' for r in assessment['stability']['configurations']):
            raise RuntimeError('Incomplete main pilot; no force winner selection or ranking')
        receipt['status']='loose audited; representative force checks starting (stability not presumed)'
        save()
        force = out/'force02'/'force_comparison.json'
        monitor([launch(command('scripts.run_uio66_sampling_pilot',[
            '--execute','--checkpoint',args.checkpoint,'--refine-reports',*map(str,reports),
            '--output',str(force)]),'force02.log',0)],deadline,stop_file)
        monitor([launch(command('scripts.assess_uio66_sampling_pilot',[
            '--reports',*map(str,reports),'--force-report',str(force),'--output',str(out/'combined_assessment.json')]),
            'combined_assessment.log')],deadline,stop_file)
        receipt['status']='finished; frozen criteria assessed; human review before any next work'
    except BaseException as error:
        receipt['status']='stopped; raw/partial results retained'
        receipt['stop_reason']=f'{type(error).__name__}: {error}'
        print(receipt['stop_reason'],flush=True)
    finally:
        for process in owned:
            terminate(process)
        receipt['finished_utc']=datetime.now(timezone.utc).isoformat()
        receipt['allocation_elapsed_seconds']=time.time()-start.timestamp()
        receipt['allocated_gpu_hours_until_controller_finish']=2*receipt['allocation_elapsed_seconds']/3600
        receipt['note']='GPU reservation must be switched off in Kaggle after archiving; this receipt is not a quota bill'
        save()
        archive = shutil.make_archive(str(out)+'_raw','zip',out)
        print(json.dumps({'status':receipt['status'],'archive':archive,'archive_sha256':sha(archive)}),flush=True)


if __name__=='__main__':
    main()
