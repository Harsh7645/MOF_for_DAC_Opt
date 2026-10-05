"""Inventory all available two-design archives separately; measured cost and provenance."""
import argparse
import json
from pathlib import Path
from ase.io import read
import numpy as np
from mof_dac.geometry_diagnostic import contacts, host_descriptors, cage_location, guest_geometry
from scripts.analyze_uio66_diagnostic import sha, save_json, csv_rows


def summarize(root, analysis, manifest):
    raw=root/'artifacts/phase3/uio66_saved_pilot_results_20261004/raw/uio66_sampling_authorized'
    plan=json.loads(manifest.read_text());mapping=plan['mapping']
    historical=list((root/'artifacts/kaggle/uio66_adsorption_2026-10-03').rglob('adsorption.json'))
    reports=[raw/'force02/force_comparison.json']+historical
    rows=json.loads((analysis/'pilot_endpoints.json').read_text())
    for r in rows:r.update(source_family='replacement32start',tolerance_ev_A=.05)
    for report in reports:
        run=json.loads(report.read_text());family='replacement_force02' if report.name=='force_comparison.json' else 'historical4start_or_smoke'
        for candidate in run['results']:
            if candidate['id'] not in ('uio66_000000','uio66_110111'):continue
            for start in candidate['starts']:
                path=report.parent/'structures'/start['system']['trajectory_file']
                record={'design':candidate['id'],'gas':start['gas'],'start':start['start'],'source_family':family,
                  'batch':None,'batch_note':'force continuation or historical seed; not an independent replacement batch',
                  'status':start['status'],'total_energy_ev':start['system']['final_energy_ev'],
                  'tolerance_ev_A':start['system']['force_tolerance_ev_per_angstrom'],'report':str(report),'report_sha256':sha(report),
                  'trajectory':str(path),'available':path.exists()}
                if path.exists():
                    a=read(path);com,axis,normal=guest_geometry(a)
                    record.update(sha256=sha(path),contacts=contacts(a,mapping),location=cage_location(a),
                                  axis_cartesian=axis.tolist(),water_normal=normal.tolist(),host_conformation=host_descriptors(a,mapping))
                rows.append(record)
    save_json(analysis/'all_available_endpoints.json',rows)
    csv_rows(analysis/'all_available_endpoints.csv',[{key:(json.dumps(r.get(key)) if isinstance(r.get(key),(dict,list)) else r.get(key)) for key in
      ['source_family','design','gas','start','batch','status','tolerance_ev_A','total_energy_ev','contacts','location','axis_cartesian','water_normal','host_conformation','trajectory','sha256']} for r in rows])
    # Verify every source from the completed replacement against its immutable download receipt.
    receipt=json.loads((raw.parent.parent/'download_verification.json').read_text());verified={}
    for source in json.loads((analysis/'source_hashes.json').read_text()):
        path=Path(source);path=path if path.is_absolute() else root/path
        expected=receipt['raw_files_sha256'][path.relative_to(raw.parent).as_posix()]
        if sha(path)!=expected:raise ValueError('Archived source hash mismatch')
        verified[path.relative_to(root).as_posix()]=expected
    force=json.loads((raw/'force02/force_comparison.json').read_text())
    components=list(force['gas_references'].values())
    for r in force['results']:
        components.append(r['bare'])
        for s in r['starts']:components.extend([s['system'],s['empty_after']])
    seconds=sum(r['elapsed_seconds'] for r in components);steps=sum(r['steps'] for r in components)
    trajs=list((raw/'force02/structures').glob('*.traj'));frame_count=sum(len(read(p,':')) for p in trajs)
    trajectory_bytes=sum(p.stat().st_size for p in trajs)
    cost={'measured_force_components':len(components),'measured_force_steps':steps,'component_seconds':seconds,
      'seconds_per_step_including_component_overhead':seconds/steps,'force_worker_total_seconds':force['elapsed_seconds'],
      'trajectory_bytes':trajectory_bytes,'stored_frames':frame_count,'bytes_per_stored_frame':trajectory_bytes/frame_count,
      'diagnostic_paths':48,'hard_step_cap_per_path':1200,'max_frames':48*1201,
      'step_cap_estimate_two_gpu_hours':48*1200*seconds/steps/2/3600,
      'step_cap_trajectory_bytes_estimate':48*1201*trajectory_bytes/frame_count,
      'scenarios_two_gpu_minutes':{str(s):48*s*seconds/steps/2/60 for s in [100,300,600,1200]},
      'uncertainty':'0.005 tolerance unmeasured; reference/guest atom counts, diagnostic neighbor checks, load imbalance and model noise change throughput. Not a completion guarantee.',
      'proposed_allocation':{'two_T4_wall_hours':2,'allocated_GPU_hours_max':4,'output_reserve_GiB':2,'model_and_environment_cache_extra':True}}
    save_json(analysis/'measured_cost.json',cost);save_json(analysis/'verified_archive_sources.json',verified)
    # Broad H-bond chemistry-class recurrence, retaining actual atom/site identities.
    recurrence=[]
    for design in ('uio66_000000','uio66_110111'):
        for gas in ('CO2','H2O'):
            pool=[r for r in rows if r['source_family']=='replacement32start' and r['design']==design and r['gas']==gas]
            for r in pool:
                motifs=[]
                n=114 if design.endswith('000000') else 124
                for hb in r['contacts']['hbonds']:
                    motifs.append('nodeOH->guest' if hb['donor'] in mapping['node_atom_indices'] else
                                  'aminoNH->guest' if hb['donor']<n else 'waterOH->host')
                r['HB_class']='|'.join(sorted(set(motifs))) or 'none_under_declared_cutoff'
            best=min(pool,key=lambda r:r['total_energy_ev'])
            opposite=[r for r in pool if r['batch']!=best['batch'] and r['HB_class']==best['HB_class']]
            recurrence.append({'design':design,'gas':gas,'lowest_sampled_start':best['start'],'HB_class':best['HB_class'],
              'same_broad_class_other_batch':[r['start'] for r in opposite],
              'best_other_batch_class_gap_ev':min(r['total_energy_ev'] for r in opposite)-best['total_energy_ev'] if opposite else None,
              'warning':'Class recurrence does not establish identical site, host conformation or physical minimum.'})
    save_json(analysis/'hydrogen_bond_recurrence.json',recurrence)
    print(json.dumps({'endpoint_rows':len(rows),'verified_sources':len(verified),'cost':cost,'recurrence':recurrence},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--analysis',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True)
    a=p.parse_args();summarize(Path.cwd(),a.analysis,a.manifest)
