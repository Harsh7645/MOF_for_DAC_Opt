"""Create v2 from v1 without overwriting either preparation or historical results."""
import argparse
import json
import shutil
from pathlib import Path
from ase.io import read,write
from mof_dac.shared_rigid_host import map_guest,geometry_hash,scheduled_jobs
from mof_dac.matched_diagnostic import save
from scripts.run_uio66_matched_diagnostic import sha


def revise(source,output):
    output.mkdir(parents=True,exist_ok=False);shutil.copytree(source/'poses',output/'poses')
    plan=json.loads((source/'manifest.json').read_text())
    plan.update(protocol='uio66_matched_geometry_diagnostic_v2',previous_manifest_sha256=sha(source/'manifest.json'),
                status='revised shared-host preregistration; execution NOT authorized')
    seed=next(j for j in plan['jobs'] if j['id']=='uio66_110111_bare')
    plan['rigid_host']={'seed_job_id':seed['id'],'seed_pose_sha256':seed['pose_sha256'],
       'selection':'Existing guest-free initial bare110111 endpoint, chosen independently of guest energies; no best-of-host search or fallback.',
       'definition':'Final complete0.005 eV/A checkpoint of seed path through0.02,0.01,0.005; same fixed cell, no guests.',
       'mapping':'Exact host replacement; indexed Zr0..5 mean MIC translation only; preserve guest internal geometry and cell-frame orientation. Unwrap guest around its first atom. No rotations, scaling, local-site fitting, optimization, repairs or resampling during mapping.',
       'validation':'Same species/order/cell/PBC; finite; max Zr residual<=0.25A; host-guest minimum>=1A; no cross-fragment covalent-cutoff edges; guest distances within1e-9A and connectivity unchanged.',
       'failure':'Missing/nonconverged seed blocks all4rigid paths; retain evidence and run independent flexible jobs. Invalid mapped pose or changed host connectivity causes global scientific hold.',
       'reference':'One same-model single point on exact complete tightly relaxed host; geometry/file hashes reused by all4rigid controls.',
       'preview_status':'Saved-seed geometry checks only; final tight host and its mapping must pass runtime checks before controls.'}
    plan['rigid_rationale']='A single preregistered empty-host conformation removes host variation between rigid controls; flexible comparisons retain host-conformation and starting-geometry confounds.'
    plan['reference_policy']=plan['reference_policy'].replace('Rigid interaction uses exact same frozen host single point; do not pool rigid energies with flexible Eads.',
      'All4rigid interactions use ONE exact tightly relaxed common empty110111 host single point; do not pool rigid energies with flexible Eads.')
    plan['allocation'].update(compute_stop_seconds=6900,retention_reserve_seconds=300)
    plan['schedule']={str(i):[j['id'] for j in scheduled_jobs(plan,i)] for i in (0,1)}
    host=read(source/seed['pose']);previews=[];(output/'mapping_preview').mkdir()
    for job in plan['jobs']:
        if job['kind']!='rigid':continue
        job['pose_role']='source guest endpoint; host is replaced at runtime with common tight host'
        job['host_dependency']=seed['id'];mapped,evidence=map_guest(read(source/job['pose']),host)
        write(output/'mapping_preview'/f"{job['id']}.traj",mapped)
        previews.append({'id':job['id'],**evidence})
    save(output/'mapping_preview.json',{'status':'offline seed preview, NOT final tight-host validation',
         'seed_geometry_sha256':geometry_hash(host),'results':previews})
    if not all(x['valid'] for x in previews):raise ValueError('Seed mapping preview failed; retained for review')
    cost=json.loads(Path('artifacts/phase3/uio66_matched_diagnostic_analysis_v2/measured_cost.json').read_text())
    step_seconds=cost['seconds_per_step_including_component_overhead']
    cost.update(protocol=plan['protocol'],relaxation_paths=48,shared_host_single_points=1,
        mandatory_common_host_prerequisite_steps_max=1200,
        scheduling='GPU0: common bare+4rigid+10flexible+10derived empties=25 paths; GPU1:2gas+bare000000+10flexible+10derived empties=23.',
        revised_bottleneck_minutes_at_step_cap=25*1200*step_seconds/60,
        revised_scenarios_minutes={str(s):25*s*step_seconds/60 for s in (100,300,600,1200)},
        uncertainty='0.005 convergence unmeasured. Mapping/SP/model startup/CPU diagnostics extra; imbalance included only as25vs23paths. 1.5x step-cost at cap exceeds budget; retain incomplete results.')
    save(output/'cost_estimate.json',cost);save(output/'manifest.json',plan)
    print(json.dumps({'manifest_sha256':sha(output/'manifest.json'),'preview':previews,'bottleneck_cap_minutes':cost['revised_bottleneck_minutes_at_step_cap']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();revise(a.source,a.output)
