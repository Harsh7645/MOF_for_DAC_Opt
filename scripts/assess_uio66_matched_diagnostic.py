"""Report every component and gas separately; never refit or infer material ranking."""
import argparse
import json
from pathlib import Path
from mof_dac.matched_diagnostic import save
from mof_dac.geometry_diagnostic import mic, contacts, guest_geometry, angle
from ase.io import read
from mof_dac.shared_rigid_host import check_shared_reference
import numpy as np


def assess(manifest, output):
    plan=json.loads(manifest.read_text());tol=plan['thresholds_ev_A'];target=plan['assessment']['initial_last_checkpoint_target_ev']
    shared=plan['protocol'].endswith('_v2')
    shared_reference=check_shared_reference(output,plan) if shared else None
    jobs=plan['jobs'];ids=[j['id'] for j in jobs]+[j['id']+'_empty' for j in jobs if j['kind'] in ('matched','replay')]
    results={key:json.loads((output/key/'result.json').read_text()) for key in ids if (output/key/'result.json').exists()}
    def energy(key,t):
        result=results.get(key,{})
        if result.get('status')!='complete':return None
        return next((c['energy_ev'] for c in result['checkpoints'] if c['tolerance']==t),None)
    components=[]
    for key in ids:
        values=[energy(key,t) for t in tol];delta=None if any(v is None for v in values) else values[-1]-values[-2]
        components.append({'id':key,'status':results.get(key,{}).get('status','missing'),'energies_ev':values,
                           'checkpoint_changes_ev':[b-a if a is not None and b is not None else None for a,b in zip(values,values[1:])],
                           'last_change_ev':delta,'initial_target_met':delta is not None and abs(delta)<=target})
    references={};adsorption=[];paired=[]
    for design in ('uio66_000000','uio66_110111'):
        pool=[design+'_bare']+[j['id']+'_empty' for j in jobs if j.get('design')==design and j['kind'] in ('matched','replay')]
        references[design]=[]
        for t in tol:
            values=[energy(key,t) for key in pool]
            references[design].append(min(values) if all(v is not None for v in values) else None)
    for job in jobs:
        if job['kind'] not in ('matched','replay','rigid'):continue
        values=[]
        for i,t in enumerate(tol):
            combo=energy(job['id'],t);gas=energy('isolated_'+job['gas'],t)
            if job['kind']=='rigid':
                if shared:
                    bare=shared_reference['energy_ev'] if shared_reference['valid'] and job['id'] in shared_reference['valid_rigid_paths'] else None
                else:
                    f=output/job['id']/'fixed_host.json';bare=json.loads(f.read_text())['energy_ev'] if f.exists() else None
            else:bare=references[job['design']][i]
            values.append(combo-bare-gas if all(v is not None for v in (combo,bare,gas)) else None)
        change=None if any(v is None for v in values) else values[-1]-values[-2]
        adsorption.append({'id':job['id'],'design':job['design'],'gas':job['gas'],'kind':job['kind'],
          'batch':job.get('batch'),'category':job.get('category'),'Eads_or_rigid_interaction_ev':values,
          'checkpoint_changes_ev':[b-a if a is not None and b is not None else None for a,b in zip(values,values[1:])],
          'last_change_ev':change,'initial_target_met':change is not None and abs(change)<=target})
    for design in references:
        for batch in (0,1):
            for category in ('targeted','random'):
                pair=[next(r for r in adsorption if r['design']==design and r['kind']=='matched' and r['gas']==g
                           and r['batch']==batch and r['category']==category) for g in ('CO2','H2O')]
                delta=[a-b if a is not None and b is not None else None for a,b in zip(*(p['Eads_or_rigid_interaction_ev'] for p in pair))]
                change=None if any(v is None for v in delta) else delta[-1]-delta[-2]
                paired.append({'design':design,'batch':batch,'category':category,'CO2_minus_H2O_ev':delta,'last_change_ev':change,
                               'both_gases_individually_stable':all(r['initial_target_met'] for r in pair),
                               'paired_target_met':change is not None and abs(change)<=target})
    matched_controls=[]
    for job in jobs:
        if 'paired_with' not in job:continue
        a=output/job['id']/'checkpoint_0.005.traj';b=output/job['paired_with']/'checkpoint_0.005.traj'
        if a.exists() and b.exists():
            aa,bb=read(a),read(b);d=mic(aa,aa.positions-bb.positions)
            drift=d[:6].mean(axis=0);aligned=d-drift
            direct_guest=float(np.sqrt(np.mean(np.sum(aligned[-3:]**2,axis=1))))
            permutation=mic(aa,aa.positions[-3:]-bb.positions[[-3,-1,-2]])-drift
            guest_rmsd=min(direct_guest,float(np.sqrt(np.mean(np.sum(permutation**2,axis=1)))))
            matched_controls.append({'id':job['id'],'paired_with':job['paired_with'],
              'total_energy_difference_ev':float(aa.get_potential_energy()-bb.get_potential_energy()),
              'host_rmsd_A':float(np.sqrt(np.mean(np.sum(d[:-3]**2,axis=1)))),
              'host_rmsd_Zr_translation_removed_A':float(np.sqrt(np.mean(np.sum(aligned[:-3]**2,axis=1)))),
              'guest_permutation_rmsd_Zr_translation_removed_A':guest_rmsd,
              'guest_axis_difference_deg':angle(guest_geometry(aa)[1],guest_geometry(bb)[1],unsigned=job['gas']=='CO2'),
              'contacts':contacts(aa,plan['mapping']),'paired_contacts':contacts(bb,plan['mapping']),
              'guest_indexed_rmsd_A':float(np.sqrt(np.mean(np.sum(d[-3:]**2,axis=1)))),
              'interpretation':('Shared-host rigid vs original-host flexible comparison: host relaxation, initial host conformation, mapping and reached basin are confounded. '
                  if shared and job['kind']=='rigid' else '')+'Guest identical-atom swap tested; Zr translation removed. No framework symmetry or lattice-image site equivalence assumed.'})
    historical={ 'status':'not_assessable' }
    old=manifest.parent/'reference/uio66_110111_tight_CO2_31.traj'
    new=output/'uio66_110111_CO2_b1_random/checkpoint_0.020.traj'
    if old.exists() and new.exists():
        aa,bb=read(new),read(old);d=mic(aa,aa.positions-bb.positions)
        historical={'status':'available','new_minus_historical_complex_ev':float(aa.get_potential_energy()-bb.get_potential_energy()),
                    'maximum_indexed_displacement_A':float(np.linalg.norm(d,axis=1).max()),
                    'meaning':'Same0.05 start, fresh LBFGS to0.02; first-crossing coordinates vs archived0.02 endpoint.'}
    rigid_references=shared_reference['valid_rigid_paths'] if shared and shared_reference['valid'] else ([] if shared else [
        j['id'] for j in jobs if j['kind']=='rigid' and (output/j['id']/'fixed_host.json').exists()])
    rigid_pairs=[]
    if shared:
        for batch in (0,1):
            pair=[next(r for r in adsorption if r['kind']=='rigid' and r['gas']==g and r['batch']==batch) for g in ('CO2','H2O')]
            values=[a-b if a is not None and b is not None else None for a,b in zip(*(r['Eads_or_rigid_interaction_ev'] for r in pair))]
            change=None if any(v is None for v in values) else values[-1]-values[-2]
            rigid_pairs.append({'batch':batch,'CO2_minus_H2O_ev':values,'last_change_ev':change,
              'both_gases_individually_stable':all(r['initial_target_met'] for r in pair),
              'paired_target_met':change is not None and abs(change)<=target})
    result={'protocol':plan['protocol'],'thresholds_ev_A':tol,'components':components,'common_bare_ev':references,
      'adsorption_components':adsorption,'paired_differences':paired,'matched_controls':matched_controls,
      'historical_start31_reproduction':historical,'rigid_host_single_points_present':int(shared_reference['valid']) if shared else len(rigid_references),
      'shared_host_reference_audit':shared_reference,'shared_host_paired_differences':rigid_pairs,
      'all_required_paths_complete':len(results)==48 and len(rigid_references)==4 and all(r['status']=='complete' for r in results.values()),
      'all_component_energy_targets_met':all(r['initial_target_met'] for r in components),
      'claim':'Numerical diagnostic only; no refit, material ranking, or UMA physical accuracy conclusion.'}
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();save(a.output/'diagnostic_assessment.json',assess(a.manifest,a.output))
