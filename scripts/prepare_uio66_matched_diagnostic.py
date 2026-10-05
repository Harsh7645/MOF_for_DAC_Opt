"""Freeze matched endpoint inputs; never overwrite a preregistration."""
import argparse
import json
from pathlib import Path
from ase.io import read, write
from scripts.analyze_uio66_diagnostic import sha, save_json


def select_paths(run):
    jobs=[]
    for row in run['results']:
        if row['id'] not in ('uio66_000000','uio66_110111'):continue
        for gas in ('CO2','H2O'):
            selected=[]
            for batch in (0,1):
                for category in ('targeted','random'):
                    pool=[s for s in row['starts'] if s['status']=='accepted' and s['gas']==gas and s['placement']['batch']==batch
                          and (s['placement']['site_class']=='random_void')==(category=='random')]
                    if not pool:raise ValueError('Missing accepted selection stratum')
                    s=min(pool,key=lambda s:(s['system']['final_energy_ev'],s['start']))
                    item={'id':f"{row['id']}_{gas}_b{batch}_{category}",'design':row['id'],'gas':gas,'batch':batch,
                          'category':category,'start':s['start'],'source_trajectory':s['system']['trajectory_file'],
                          'source_energy_ev':s['system']['final_energy_ev'],'frame':-1,'kind':'matched'}
                    selected.append(item);jobs.append(item)
            winner=min(selected,key=lambda s:(s['source_energy_ev'],s['start']))
            jobs.append({**winner,'id':f"{row['id']}_{gas}_replay",'kind':'replay','frame':0,'paired_with':winner['id']})
            if row['id']=='uio66_110111':
                for batch in (0,1):
                    winner=min((s for s in selected if s['batch']==batch),key=lambda s:(s['source_energy_ev'],s['start']))
                    jobs.append({**winner,'id':f"{row['id']}_{gas}_b{batch}_rigid",'kind':'rigid','paired_with':winner['id']})
    return jobs


def prepare(raw, output, plan_path):
    output.mkdir(parents=True,exist_ok=False);(output/'poses').mkdir()
    plan=json.loads(plan_path.read_text());jobs=[];sources={}
    for worker in (0,1):
        report=raw/f'worker{worker}/adsorption.json';run=json.loads(report.read_text())
        if run['plan_sha256']!=sha(plan_path):raise ValueError('Wrong source plan')
        sources[str(report)]=sha(report)
        items=select_paths(run)
        for item in items:
            source=report.parent/'structures'/item.pop('source_trajectory');atoms=read(source,index=item['frame'])
            dest=output/'poses'/f"{item['id']}.traj";write(dest,atoms)
            item.update({'pose':dest.relative_to(output).as_posix(),'pose_sha256':sha(dest),
                         'source_trajectory':str(source),'source_sha256':sha(source),'host_atoms':len(atoms)-3})
            sources[str(source)]=sha(source);jobs.append(item)
        for row in run['results']:
            if row['id'] not in ('uio66_000000','uio66_110111'):continue
            source=report.parent/'structures'/row['bare']['trajectory_file']
            dest=output/'poses'/f"{row['id']}_bare.traj";write(dest,read(source,index=-1))
            jobs.append({'id':f"{row['id']}_bare",'design':row['id'],'kind':'bare','pose':dest.relative_to(output).as_posix(),
                         'pose_sha256':sha(dest),'source_trajectory':str(source),'source_sha256':sha(source),'frame':-1})
        if worker==0:
            for gas in ('CO2','H2O'):
                source=report.parent/'structures'/run['gas_references'][gas]['trajectory_file'];dest=output/'poses'/f'isolated_{gas}.traj'
                write(dest,read(source,index=-1));jobs.append({'id':f'isolated_{gas}','kind':'gas','gas':gas,
                     'pose':dest.relative_to(output).as_posix(),'pose_sha256':sha(dest),'source_trajectory':str(source),'source_sha256':sha(source),'frame':-1})
    manifest={'protocol':'uio66_matched_geometry_diagnostic_v1','status':'preregistered preparation; execution NOT authorized',
      'original_plan_sha256':sha(plan_path),'mapping':plan['mapping'],'checkpoint_sha256':plan['checkpoint_sha256'],
      'checkpoint_revision':plan['checkpoint_revision'],'model':plan['model'],'task':'odac',
      'selection_rule':'Lowest accepted total energy within design/gas/batch/targeted-or-random; ties by start index. Replay pooled winner original frame0. Rigid best matched per110111 gas/batch.',
      'rigid_rationale':'Saved110111CO2start31 host N22 moves0.568565A, coupled linker/guest motion; four rigid controls retain exact selected host coordinates.',
      'thresholds_ev_A':[.02,.01,.005],'max_steps_per_path':1200,'max_seconds_per_path':1200,
      'allocation':{'gpus':2,'gpu_model_contains':'T4','max_wall_seconds':7200,'threads_per_worker':1,'approved':False},
      'optimizer':{'name':'ASE LBFGS','maxstep_A':.1,'fresh_history_at_path_start':True,'same_history_across_thresholds':True},
      'assessment':{'initial_last_checkpoint_target_ev':.005,'applies_to':['each combo','each reference','each gas Eads','paired difference'],
        'all_required_paths_and_checkpoints':True,'physical_accuracy_claim':False},
      'reference_policy':'Two bare + two isolated gas staged paths. Each of20 flexible completed guests yields one staged empty-host path. Per design/tolerance use lowest complete accepted common bare pool. Rigid interaction uses exact same frozen host single point; do not pool rigid energies with flexible Eads.',
      'failure_policy':'No retries/resampling. Retain every frame/log/checkpoint/error; missing paths remain denominator. Bond-image change/nonfinite/severe contact triggers global scientific hold. Step/time limit makes path incomplete; retain and continue independent paths within allocation.',
      'jobs':jobs,'source_hashes':sources}
    save_json(output/'manifest.json',manifest)
    print(json.dumps({'manifest':str(output/'manifest.json'),'sha256':sha(output/'manifest.json'),
                      'fixed_inputs':len(jobs),'guest_paths':24,'derived_empty_paths':20,'total_relaxation_paths':48}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--plan',type=Path,default=Path('data/design/uio66_sampling_pilot_v2.json'));a=p.parse_args();prepare(a.raw,a.output,a.plan)
