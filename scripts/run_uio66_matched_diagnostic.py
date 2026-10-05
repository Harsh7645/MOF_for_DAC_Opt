"""Dry-run validation by default. GPU execution requires explicit reviewed allocation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import zipfile
from ase.io import read, write
import numpy as np
from mof_dac.matched_diagnostic import staged_path, save
from mof_dac.sampling import frozen_input_path
from mof_dac.shared_rigid_host import map_guest, geometry_hash, scheduled_jobs


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def validate(manifest_path):
    plan=json.loads(manifest_path.read_text());root=manifest_path.parent
    if plan['protocol'] not in ('uio66_matched_geometry_diagnostic_v1','uio66_matched_geometry_diagnostic_v2'):raise ValueError('Wrong protocol')
    if plan['thresholds_ev_A']!=[.02,.01,.005] or plan['max_steps_per_path']!=1200:raise ValueError('Changed frozen limits')
    counts={kind:sum(j['kind']==kind for j in plan['jobs']) for kind in ('matched','replay','rigid','bare','gas')}
    if counts!={'matched':16,'replay':4,'rigid':4,'bare':2,'gas':2}:raise ValueError('Wrong diagnostic scope')
    if len({j['id'] for j in plan['jobs']})!=28:raise ValueError('Duplicate path')
    for job in plan['jobs']:
        path=frozen_input_path(root,job['pose'])
        if sha(path)!=job['pose_sha256']:raise ValueError('Pose hash mismatch')
        atoms=read(path)
        if job['kind'] in ('matched','replay','rigid') and len(atoms)!=job['host_atoms']+3:raise ValueError('Wrong atom count')
    if plan['protocol'].endswith('_v2'):
        seed=next(j for j in plan['jobs'] if j['id']=='uio66_110111_bare')
        if seed['pose_sha256']!=plan['rigid_host']['seed_pose_sha256']:raise ValueError('Wrong shared host seed')
        if plan['rigid_host']['seed_job_id']!=seed['id']:raise ValueError('Wrong host dependency')
        for job in plan['jobs']:
            if job['kind']=='rigid':
                _,evidence=map_guest(read(root/job['pose']),read(root/seed['pose']))
                if not evidence['valid'] or job['host_dependency']!=seed['id']:raise ValueError('Invalid seed mapping/dependency')
        if plan['schedule']!={str(i):[j['id'] for j in scheduled_jobs(plan,i)] for i in (0,1)}:
            raise ValueError('Frozen schedule mismatch')
    return plan


def prepare_shared_host(plan, manifest_path, output, calculator):
    """Publish a single reference and all four validated mappings only after tight completion."""
    seed_result=json.loads((output/plan['rigid_host']['seed_job_id']/'result.json').read_text())
    if seed_result['status']!='complete':raise ValueError('Shared host prerequisite incomplete')
    folder=output/'shared_rigid_host';folder.mkdir(exist_ok=False)
    host=read(output/plan['rigid_host']['seed_job_id']/'checkpoint_0.005.traj');host.set_constraint();host.calc=calculator
    energy=float(host.get_potential_energy());force=float(np.linalg.norm(host.get_forces(),axis=1).max())
    write(folder/'host.traj',host)
    valid=np.isfinite([energy,force]).all() and force<.005
    record={'status':'ready' if valid else 'invalid','energy_ev':energy,'fmax_ev_A':force,
            'host_geometry_sha256':geometry_hash(host),'host_file_sha256':sha(folder/'host.traj'),
            'source_job':plan['rigid_host']['seed_job_id'],'source_checkpoint_sha256':sha(output/plan['rigid_host']['seed_job_id']/'checkpoint_0.005.traj'),
            'single_point_count':1,'mapping':[]}
    for job in plan['jobs']:
        if job['kind']!='rigid':continue
        mapped,evidence=map_guest(read(manifest_path.parent/job['pose']),host)
        path=folder/f"{job['id']}.traj";write(path,mapped)
        record['mapping'].append({'id':job['id'],'file':path.name,'file_sha256':sha(path),**evidence})
        valid=bool(valid and evidence['valid'])
    record['status']='ready' if valid else 'scientific_hold'
    save(folder/'reference.json',record)
    if not valid:save(output/'SCIENTIFIC_HOLD.json',{'job':'shared_rigid_host','reason':'Common host force or mapped-pose validation failed','evidence':record})
    return record


def worker(manifest_path, output, checkpoint, index):
    # CUDA_VISIBLE_DEVICES is set by controller before this import.
    import torch
    from fairchem.core import FAIRChemCalculator
    torch.set_num_threads(1)
    plan=validate(manifest_path)
    calculator=FAIRChemCalculator.from_model_checkpoint(str(checkpoint),task_name='odac',device='cuda',inference_settings='batch')
    jobs=scheduled_jobs(plan,index);worker_dir=output/f'worker{index}';worker_dir.mkdir()
    shared=plan['protocol'].endswith('_v2')
    def run(job, atoms):
        if (output/'SCIENTIFIC_HOLD.json').exists():return None
        save(worker_dir/'active.json',{'id':job['id'],'started_epoch':time.time()})
        result=staged_path(atoms,calculator,output/job['id'],thresholds=plan['thresholds_ev_A'],
                          max_steps=plan['max_steps_per_path'],max_seconds=plan['max_seconds_per_path'],
                          rigid_host_atoms=job.get('host_atoms',0) if job['kind']=='rigid' else 0,direct=job['kind']=='replay')
        if result['status']=='scientific_hold':save(output/'SCIENTIFIC_HOLD.json',{'job':job['id'],**result})
        save(worker_dir/'active.json',{'id':None})
        return result
    for job in jobs:
        atoms=read(frozen_input_path(manifest_path.parent,job['pose']))
        if shared and job['kind']=='rigid':
            reference=output/'shared_rigid_host/reference.json'
            data=json.loads(reference.read_text()) if reference.exists() else {}
            if data.get('status')!='ready':
                folder=output/job['id'];folder.mkdir();save(folder/'result.json',{'status':'blocked_host_dependency','checkpoints':[],
                    'reason':'No complete validated0.005 common empty host; no fallback or alternate host'})
                continue
            entry=next(e for e in data['mapping'] if e['id']==job['id']);path=reference.parent/entry['file']
            if sha(path)!=entry['file_sha256'] or sha(reference.parent/'host.traj')!=data['host_file_sha256']:
                raise ValueError('Shared host/mapping file changed')
            atoms=read(path)
            if geometry_hash(atoms[:job['host_atoms']])!=data['host_geometry_sha256']:raise ValueError('Rigid host differs from shared reference')
        result=run(job,atoms)
        if result is None or result['status']=='scientific_hold':break
        if shared and job['id']==plan['rigid_host']['seed_job_id'] and result['status']=='complete':
            save(worker_dir/'active.json',{'id':'shared_rigid_host_SP_and_mapping','started_epoch':time.time()})
            reference=prepare_shared_host(plan,manifest_path,output,calculator)
            save(worker_dir/'active.json',{'id':None})
            if reference['status']!='ready':break
        if job['kind'] in ('matched','replay') and result['status']=='complete':
            final=read(output/job['id']/'checkpoint_0.005.traj');empty=final[:job['host_atoms']]
            empty_job={**job,'id':job['id']+'_empty','kind':'empty'}
            write(output/job['id']/'derived_empty_input.traj',empty)
            empty_result=run(empty_job,empty)
            if empty_result is None or empty_result['status']=='scientific_hold':break
        if job['kind']=='rigid' and shared:
            save(output/job['id']/'shared_host_reference.json',{'reference':'shared_rigid_host/reference.json',
                 'reference_sha256':sha(output/'shared_rigid_host/reference.json'),'host_geometry_sha256':geometry_hash(atoms[:job['host_atoms']]),
                 'paired_flexible':job['paired_with'],'comparison':'Same guest source, different initial host geometry; not a pure host-freezing ablation'})
        if job['kind']=='rigid' and not shared:
            host=atoms[:job['host_atoms']];host.calc=calculator
            # Exact fixed host single point, no host relaxation or geometry substitution.
            save(worker_dir/'active.json',{'id':job['id']+'_host_SP','started_epoch':time.time()})
            energy=float(host.get_potential_energy());write(output/job['id']/'fixed_host.traj',host)
            save(output/job['id']/'fixed_host.json',{'energy_ev':energy,'geometry_policy':'exact input frozen host'})
            save(worker_dir/'active.json',{'id':None})


def inventory(plan, output):
    expected=[j['id'] for j in plan['jobs']]+[j['id']+'_empty' for j in plan['jobs'] if j['kind'] in ('matched','replay')]
    rows=[]
    for identifier in expected:
        result=output/identifier/'result.json'
        rows.append({'id':identifier,**(json.loads(result.read_text()) if result.exists() else {'status':'not_completed_or_not_started'})})
    save(output/'inventory.json',rows)
    return rows


def execute(args, plan):
    if args.approved_wall_hours!=2:raise ValueError('Execution requires reviewed --approved-wall-hours 2; preparation is not authorization')
    if args.allocation_start_epoch is None or not 0<=time.time()-args.allocation_start_epoch<7200:
        raise ValueError('Original allocation start timestamp required; never refresh or extend')
    if args.checkpoint is None or sha(args.checkpoint)!=plan['checkpoint_sha256']:raise ValueError('Pinned checkpoint hash mismatch')
    seal=args.manifest.parent/'release.json'
    release=json.loads(seal.read_text())
    for rel,expected in release['sha256'].items():
        if sha(frozen_input_path(args.manifest.parent,rel))!=expected:raise ValueError(f'Release hash mismatch: {rel}')
    # Require execution from the frozen code root, not a different importable checkout.
    if Path(__file__).resolve()!=args.manifest.parent.resolve()/'scripts/run_uio66_matched_diagnostic.py':
        raise ValueError('Execute the frozen bundle code from its root')
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,name,uuid,memory.total','--format=csv,noheader'],text=True)
    lines=gpu.strip().splitlines()
    if len(lines)!=2 or any('T4' not in s for s in lines):raise ValueError('Requires actual two T4 GPUs')
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=False)
    started=args.allocation_start_epoch;allocation={'started_epoch':started,'deadline_epoch':started+6900,
       'allocation_end_epoch':started+7200,'retention_reserve_seconds':300,'gpu_inventory':gpu,
       'manifest_sha256':sha(args.manifest),'release_sha256':sha(seal),'checkpoint_sha256':sha(args.checkpoint),
       'allocation_scope':'first notebook cell through controller; includes setup, recorded clock never refreshed','max_gpu_hours':4}
    save(output/'allocation.json',allocation)
    with (output/'environment.txt').open('w') as handle:
        subprocess.run([sys.executable,'-m','pip','freeze'],stdout=handle,check=True,timeout=max(1,allocation['deadline_epoch']-time.time()))
    processes=[];logs=[];reason='finished'
    try:
        if time.time()>=allocation['deadline_epoch']:raise TimeoutError('Compute budget exhausted before worker launch')
        for index in (0,1):
            env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(index),OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
            log=(output/f'worker{index}.log').open('w');logs.append(log)
            command=[sys.executable,'-m','scripts.run_uio66_matched_diagnostic','--manifest',str(args.manifest.resolve()),
                     '--output',str(output),'--checkpoint',str(args.checkpoint.resolve()),'--worker',str(index)]
            processes.append(subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT))
        while any(p.poll() is None for p in processes):
            if time.time()>=allocation['deadline_epoch']:reason='allocation_time_limit';break
            if (output/'SCIENTIFIC_HOLD.json').exists():reason='scientific_hold';break
            if any(p.poll() not in (None,0) for p in processes):reason='worker_failure';break
            timeout=False
            for index in (0,1):
                active=output/f'worker{index}/active.json'
                if active.exists():
                    state=json.loads(active.read_text())
                    if state.get('id') and time.time()-state['started_epoch']>plan['max_seconds_per_path']:
                        reason='path_time_limit';timeout=True;break
            if timeout:break
            time.sleep(1)
        if reason=='finished' and any(p.poll() not in (None,0) for p in processes):reason='worker_failure'
    finally:
        for p in processes:
            if p.poll() is None:p.terminate()
        for p in processes:
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        for log in logs:log.close()
        inventory(plan,output)
        save(output/'completion.json',{'reason':reason,'elapsed_seconds':time.time()-started,'returncodes':[p.returncode for p in processes]})
        files={p.relative_to(output).as_posix():sha(p) for p in output.rglob('*') if p.is_file()}
        save(output/'output_hashes.json',files)
        with zipfile.ZipFile(output.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
            for p in output.rglob('*'):
                if p.is_file():z.write(p,p.relative_to(output))
    return reason


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output',type=Path)
    p.add_argument('--checkpoint',type=Path);p.add_argument('--execute',action='store_true');p.add_argument('--approved-wall-hours',type=float)
    p.add_argument('--allocation-start-epoch',type=float)
    p.add_argument('--worker',type=int,choices=(0,1),help=argparse.SUPPRESS);args=p.parse_args();plan=validate(args.manifest)
    if args.worker is not None:worker(args.manifest,args.output,args.checkpoint,args.worker)
    elif args.execute:
        if args.output is None:p.error('--output required')
        print(execute(args,plan))
    else:print(json.dumps({'validation':'passed','new_inference':False,'fixed_inputs':len(plan['jobs']),'relaxation_paths':48,
        'rigid_host_single_points':1 if plan['protocol'].endswith('_v2') else 4,
        'final_tight_host_mapping':'pending GPU prerequisite' if plan['protocol'].endswith('_v2') else 'not applicable'}))
