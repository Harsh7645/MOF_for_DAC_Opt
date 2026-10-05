"""CPU geometry check by default; explicit --execute runs only the eight-design pilot."""

import argparse
import hashlib
import json
import sys
import time
from importlib.metadata import version
from pathlib import Path

import numpy as np

from mof_dac.adsorption import evaluate_candidate, gas_geometry, intact
from mof_dac.relaxation import relax_fixed_cell
from mof_dac.sampling import frozen_input_path, periodic_change, refinement_jobs


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def proposals(host, row, gas):
    from ase.geometry import find_mic
    result = []
    for pose in row['poses'][gas]:
        guest = gas_geometry(gas)
        guest.positions = np.array(pose['guest_positions_angstrom'])
        guest.set_cell(host.cell)
        guest.pbc = True
        _, distance = find_mic((host.positions[:, None]-guest.positions[None]).reshape(-1, 3), host.cell, True)
        if distance.min() < 2.0-1e-8:
            raise ValueError('Frozen placement clashes with current bare host; no resampling')
        result.append((host+guest, pose))
    return result


def validate_plan(plan, root):
    from ase.io import read
    from scripts.prepare_uio66_sampling_pilot import SELECTION
    if plan['protocol'] != 'uio66_eight_stratified_32_v2' or plan['starts_per_gas'] != 32 \
            or [r['pattern'] for r in plan['configurations']] != list(SELECTION) \
            or plan['force_tolerance_ev_per_angstrom'] != .05 or plan['step_budget'] != 400:
        raise ValueError('Not the preregistered eight-design/32-start pilot')
    if sha(root/'data/design/uio66_fit_split.json') != plan['historical_split_sha256']:
        raise ValueError('Historical 51/13 split changed')
    hosts = {}
    for row in plan['configurations']:
        path = frozen_input_path(root, row['bare_input'])
        if not path.is_relative_to(root.resolve()) or sha(path) != row['bare_input_sha256']:
            raise ValueError('Bare input path/hash invalid')
        host = read(path)
        for gas in ('CO2', 'H2O'):
            poses = row['poses'][gas]
            if [p['start'] for p in poses] != list(range(32)) or len({tuple(p['seed_entropy']) for p in poses}) != 32:
                raise ValueError('Wrong/duplicate start identities or seeds')
            for batch in (0, 1):
                from collections import Counter
                quotas = dict(Counter(p['site_class'] for p in poses if p['batch'] == batch))
                if quotas != plan['batch_quotas'] or any(p['batch'] != p['start']//16 for p in poses):
                    raise ValueError('Batch/site allocation changed')
            for p in poses:
                expected_seed = [plan['master_seed'],row['configuration_index'],('CO2','H2O').index(gas),p['batch'],p['batch_slot']]
                if p['seed_entropy'] != expected_seed or p['batch_slot']!=p['start']%16:
                    raise ValueError('Independent seed identity changed')
                xyz = np.array(p['guest_positions_angstrom'])
                reference = gas_geometry(gas).get_all_distances()
                measured = np.linalg.norm(xyz[:,None]-xyz[None],axis=-1)
                if xyz.shape!=(3,3) or not np.isfinite(xyz).all() or not np.allclose(measured,reference,atol=1e-9,rtol=0):
                    raise ValueError('Frozen gas geometry is nonfinite/distorted')
            proposals(host, row, gas)
        hosts[row['id']] = host
    return hosts


def execute_refinement(plan, reports, calculator, output, save):
    from ase.io import read
    jobs = refinement_jobs(plan, reports)
    gas_references = {g: relax_fixed_cell(gas_geometry(g),calculator,output.parent/'structures',
                                        'tight_isolated_'+g,.02,600) for g in ('CO2','H2O')}
    rows = []
    for path, run, source, winners in jobs:
        directory = path.parent/'structures'
        candidates = [source['bare']] + [s['empty_after'] for s in source['starts'] if s['status']=='accepted']
        common = min(candidates,key=lambda e:e['final_energy_ev'])
        base = read(directory/common['trajectory_file'],index=-1)
        tight_bare = relax_fixed_cell(base,calculator,output.parent/'structures',source['id']+'_tight_bare',.02,600)
        bare_change = periodic_change(base, read(output.parent/'structures'/tight_bare['trajectory_file'],index=-1))
        result = {'id':source['id'],'bare':tight_bare,'periodic_bare_connectivity':bare_change,
                  'starts':[],'paired_target_ev':None}
        for s in winners:
            initial = read(directory/s['system']['trajectory_file'],index=-1)
            name = f"{source['id']}_tight_{s['gas']}_{s['start']}"
            record = {'gas':s['gas'],'start':s['start'],'site_class':s['placement']['site_class'],
                      'status':'failed','loose_system_energy_ev':s['system']['final_energy_ev']}
            try:
                system = relax_fixed_cell(initial,calculator,output.parent/'structures',name,.02,600)
                final = read(output.parent/'structures'/system['trajectory_file'],index=-1)
                host = final[:-3]
                empty = relax_fixed_cell(host,calculator,output.parent/'structures',name+'_empty',.02,600)
                empty_final = read(output.parent/'structures'/empty['trajectory_file'],index=-1)
                changes = [periodic_change(initial[:-3],host),periodic_change(host,empty_final),
                           periodic_change(initial[-3:],final[-3:])]
                ok = system['status']=='converged' and system['severe_contacts_below_0_7_angstrom']==0 \
                     and intact(empty) and not any(v for c in changes for v in c.values())
                record.update(system=system,empty_after=empty,periodic_changes=changes,
                              status='accepted' if ok else 'rejected_diagnostic')
            except Exception as error:
                record['error'] = f'{type(error).__name__}: {error}'
            result['starts'].append(record)
        complete = intact(tight_bare) and not any(bare_change.values()) and all(intact(e) for e in gas_references.values()) \
                   and all(s['status']=='accepted' for s in result['starts']) and len(result['starts'])==4
        result['status'] = 'complete_representative_force_check' if complete else 'incomplete_force_check'
        if complete:
            reference = min([tight_bare]+[s['empty_after'] for s in result['starts']],key=lambda e:e['final_energy_ev'])
            result['tight_common_bare_ev'] = reference['final_energy_ev']
            changes = []
            for s in result['starts']:
                loose = s['loose_system_energy_ev']-source['bare_reference_energy_ev']-run['gas_references'][s['gas']]['final_energy_ev']
                tight = s['system']['final_energy_ev']-reference['final_energy_ev']-gas_references[s['gas']]['final_energy_ev']
                s.update(loose_adsorption_ev=loose,tight_adsorption_ev=tight,change_ev=tight-loose)
                changes.append(abs(tight-loose))
            result['max_abs_adsorption_change_ev'] = max(changes)
            tight_min = {g:min(s['tight_adsorption_ev'] for s in result['starts'] if s['gas']==g) for g in ('CO2','H2O')}
            result['representative_tight_delta_ev'] = tight_min['CO2']-tight_min['H2O']
            result['delta_change_ev'] = result['representative_tight_delta_ev']-source['paired_target_ev']
            result['initial_0_01_ev_target_met'] = max(*changes,abs(result['delta_change_ev']))<=.01
        rows.append(result)
        save({'gas_references':gas_references,'results':rows})
    return {'gas_references':gas_references,'results':rows,'status':'representative refinement finished; not a full tight-force ranking'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',default='data/design/uio66_sampling_pilot_v2.json')
    parser.add_argument('--ids',nargs='+')
    parser.add_argument('--output',required=True)
    parser.add_argument('--execute',action='store_true',help='Explicit GPU allocation; otherwise geometry-only')
    parser.add_argument('--checkpoint')
    parser.add_argument('--refine-reports',nargs='+')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = Path(args.output)
    if output.exists() or output.parent.exists():
        raise ValueError('Choose an entirely new output directory; never overwrite evidence')
    plan = json.loads(Path(args.plan).read_text())
    started = time.perf_counter()
    hosts = validate_plan(plan,root)
    plan['_sha256'] = sha(args.plan)
    identifiers = args.ids or list(hosts)
    if not identifiers or len(set(identifiers))!=len(identifiers) or not set(identifiers)<=set(hosts):
        raise ValueError('Only unique IDs from the frozen eight-design pilot allowed')
    if args.refine_reports and args.ids:
        raise ValueError('Force study uses all four preregistered IDs; no --ids override')
    if args.refine_reports:
        from scripts.assess_uio66_sampling_pilot import assess
        assess(args.plan,args.refine_reports)  # saved energies/source/periodic geometry before compute
    result = {'protocol':plan['protocol'],'plan_sha256':plan['_sha256'],'scope':'provisional UMA-only development pilot',
        'status':'geometry dry-run; no new energies','expected_ids':identifiers,'starts_per_gas':32,'fmax':.05,
        'step_budget':400,'source_sha256':{name:sha(root/name) for name in
            ['mof_dac/sampling.py','mof_dac/adsorption.py','mof_dac/relaxation.py','scripts/run_uio66_sampling_pilot.py']},
        'input_sha256':{r['id']:r['bare_input_sha256'] for r in plan['configurations'] if r['id'] in identifiers},
        'gas_references':{},'results':[],'active_candidate':None}
    if args.refine_reports:
        result.update(protocol=plan['protocol']+'_force02',fmax=.02,step_budget=600,starts_per_gas=2,
            expected_ids=plan['force_check']['ids'],scope='representative continuation at tighter forces; not full 32-start ranking',
            loose_report_sha256={str(p):sha(p) for p in map(Path,args.refine_reports)})
    def save(update=None):
        if update:
            result.update(update)
        output.parent.mkdir(parents=True,exist_ok=True)
        temp = output.with_suffix('.tmp')
        temp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        temp.replace(output)
    if not args.execute:
        if args.refine_reports:
            jobs = refinement_jobs(plan,list(map(Path,args.refine_reports)))
            result['representative_guest_refinements'] = sum(len(j[3]) for j in jobs)
        result['initial_guests_checked'] = len(identifiers)*64
        result['cpu_geometry_check_seconds'] = time.perf_counter()-started
        save()
        print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','results','gas_references')}))
        return
    if not args.checkpoint or sha(args.checkpoint)!=plan['checkpoint_sha256']:
        raise ValueError('Exact pinned checkpoint SHA256 required')
    import torch
    from ase.io import read
    from fairchem.core import FAIRChemCalculator
    if version('fairchem-core')!='2.23.0' or not torch.cuda.is_available():
        raise ValueError('Pilot requires fairchem-core 2.23.0 and supported CUDA GPU')
    torch.set_num_threads(1)
    torch.manual_seed(plan['master_seed'])
    result.update(status='running',model=plan['model'],task='odac',checkpoint_sha256=plan['checkpoint_sha256'],
        checkpoint_revision=plan['checkpoint_revision'],gpu=torch.cuda.get_device_name(0),
        python=sys.version,packages={k:version(k) for k in ('fairchem-core','torch','ase','numpy','scipy')})
    save()
    for name,digest in result['source_sha256'].items():
        target = output.parent/'executed_source'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        data = (root/name).read_bytes()
        if hashlib.sha256(data).hexdigest()!=digest:
            raise ValueError('Source changed before execution')
        target.write_bytes(data)
    calculator = FAIRChemCalculator.from_model_checkpoint(args.checkpoint,task_name='odac',device='cuda',inference_settings='batch')
    if args.refine_reports:
        save(execute_refinement(plan,list(map(Path,args.refine_reports)),calculator,output,save))
    else:
        gases = {}
        for gas in ('CO2','H2O'):
            e = relax_fixed_cell(gas_geometry(gas),calculator,output.parent/'structures','isolated_'+gas,.05,400)
            result['gas_references'][gas] = e
            save()
            if not intact(e):
                raise ValueError('Gas reference rejected')
            gases[gas] = read(output.parent/'structures'/e['trajectory_file'],index=-1)
        for key in identifiers:
            row = next(r for r in plan['configurations'] if r['id']==key)
            def progress(bare, records):
                save({'active_candidate':{'id':key,'bare':bare,'starts':records}})
                print(key,len(records),records[-1]['status'],flush=True)
            try:
                answer = evaluate_candidate(hosts[key],calculator,gases,result['gas_references'],output.parent/'structures',
                    key,32,plan['master_seed'],.05,400,progress,
                    proposal_factory=lambda host,gas:proposals(host,row,gas),periodic_guard=True)
                if answer['status']=='failed_periodic_bare':
                    answer.update(status='failed',failure_reason='failed_periodic_bare')
            except Exception as error:
                answer = {'id':key,'status':'failed','paired_target_ev':None,
                    'error':f'{type(error).__name__}: {error}','partial':result['active_candidate']}
            result['results'].append(answer)
            save({'active_candidate':None})
        save({'status':'pilot finished; assess all eight including failures'})
    for name,digest in result['source_sha256'].items():
        target = output.parent/'executed_source'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        data = (root/name).read_bytes()
        if hashlib.sha256(data).hexdigest()!=digest:
            raise ValueError('Source changed during execution')
        target.write_bytes(data)
    save({'elapsed_seconds':time.perf_counter()-started,'peak_gpu_allocated_bytes':torch.cuda.max_memory_allocated()})


if __name__ == '__main__':
    main()
