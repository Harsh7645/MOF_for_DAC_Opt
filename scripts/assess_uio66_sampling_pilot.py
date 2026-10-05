"""Audit the complete development pilot; independent-batch stability and basins."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from mof_dac.adsorption import summarize_adsorption
from mof_dac.sampling import cluster_minima, frozen_input_path, periodic_change


EXECUTED_SOURCES = {'mof_dac/sampling.py','mof_dac/adsorption.py','mof_dac/relaxation.py',
                    'scripts/run_uio66_sampling_pilot.py'}


def stability(rows, gas_references, target=.01):
    """All starts count; failed/incomplete configurations invalidate ranking."""
    from scipy.stats import spearmanr
    diagnostics = []
    for row in rows:
        if row['status']!='complete_model_sample' or len(row['starts'])!=64:
            diagnostics.append({'id':row['id'],'status':'incomplete; no ranking','energy_target_met':False})
            continue
        batches = [summarize_adsorption(row['bare'],gas_references,
            [s for s in row['starts'] if s['placement']['batch']==b],16) for b in (0,1)]
        if any(b['status']!='complete_model_sample' for b in batches):
            diagnostics.append({'id':row['id'],'status':'incomplete; no ranking','energy_target_met':False})
            continue
        shifts = {g:abs(batches[0]['gas_results'][g]['minimum_sampled_adsorption_ev']-
                        batches[1]['gas_results'][g]['minimum_sampled_adsorption_ev']) for g in ('CO2','H2O')}
        delta = abs(batches[0]['paired_target_ev']-batches[1]['paired_target_ev'])
        gains = {g: batches[0]['gas_results'][g]['minimum_sampled_adsorption_ev']-
                    row['gas_results'][g]['minimum_sampled_adsorption_ev'] for g in ('CO2','H2O')}
        # Common bare-reference changes affect Eads; retain a reference-independent
        # system-minimum comparison to distinguish site search from empty-MOF drift.
        combo_shifts = {g:abs(min(s['system']['final_energy_ev'] for s in row['starts']
                                  if s['gas']==g and s['placement']['batch']==0)-
                              min(s['system']['final_energy_ev'] for s in row['starts']
                                  if s['gas']==g and s['placement']['batch']==1)) for g in ('CO2','H2O')}
        diagnostics.append({'id':row['id'],'status':'complete','batches':batches,
            'absolute_batch_adsorption_difference_ev':shifts,'absolute_batch_delta_difference_ev':delta,
            'absolute_batch_system_minimum_difference_ev':combo_shifts,'16_to_32_adsorption_change_ev':gains,
            'bare_reference_batch_difference_ev':abs(batches[0]['bare_reference_energy_ev']-batches[1]['bare_reference_energy_ev']),
            'energy_target_met':max(*shifts.values(),delta,*combo_shifts.values(),*map(abs,gains.values()))<=target})
    if any(d['status']!='complete' for d in diagnostics) or len(diagnostics)!=8:
        return {'configurations':diagnostics,'energy_stability':'fail/incomplete','ranking':'not assessed',
                'next_decision':'no-go for scaling; retain failures and repair/review diagnostics'}
    values = np.array([[d['batches'][b]['paired_target_ev'] for d in diagnostics] for b in (0,1)])
    ranks = [sorted(range(8),key=lambda i:(values[b,i],diagnostics[i]['id'])) for b in (0,1)]
    correlation = float(spearmanr(values[0],values[1]).statistic) if all(np.ptp(v)>0 for v in values) else None
    top2_overlap = len(set(ranks[0][:2])&set(ranks[1][:2]))/2
    reversals, uncertain_pairs = [], []
    for i in range(8):
        for j in range(i+1,8):
            gaps = values[:,i]-values[:,j]
            pair = [diagnostics[i]['id'],diagnostics[j]['id']]
            if min(abs(gaps))<=2*target:
                uncertain_pairs.append(pair)
            elif gaps[0]*gaps[1]<0:
                reversals.append(pair)
    top_boundary_near_tie = any(abs(values[b,ranks[b][1]]-values[b,ranks[b][2]])<=2*target for b in (0,1))
    rank_pass = correlation is not None and correlation>=.9 and top2_overlap==1 and not reversals and not top_boundary_near_tie
    energy_pass = all(d['energy_target_met'] for d in diagnostics)
    return {'configurations':diagnostics,'initial_target_ev':target,
        'energy_stability':'initial target met' if energy_pass else 'initial target not met',
        'ranking':{'batch_spearman':correlation,'top2_overlap':top2_overlap,'decisive_reversals':reversals,
            'near_tie_pairs':uncertain_pairs,'top2_boundary_near_tie':top_boundary_near_tie,'criterion_met':rank_pass},
        'next_decision':'computational sampling candidate for force/chemistry review; no automatic full-run authorization'
            if energy_pass and rank_pass else 'no-go for scaling; investigate sampling, ties and force convergence'}


def report_hashes(report_paths, report_path_map=None):
    """Explicit one-to-one relocation; original report bytes/keys stay untouched."""
    sha = lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    if report_path_map is None:
        return {str(p):sha(p) for p in map(Path,report_paths)}
    supplied = [Path(p).resolve() for p in report_paths]
    mapped = [Path(p).resolve() for p in report_path_map.values()]
    if len(set(supplied))!=len(supplied) or len(set(mapped))!=len(mapped) \
            or len(mapped)!=len(supplied) or set(mapped)!=set(supplied):
        raise ValueError('Report relocation must map each supplied report exactly once')
    return {original:sha(local) for original,local in report_path_map.items()}


def assess_force(plan_path, report_paths, force_path, report_path_map=None):
    """Independently verify representative tight trajectories and subtraction."""
    from ase.io import read
    from ase.geometry import find_mic
    from ase.neighborlist import neighbor_list
    from mof_dac.adsorption import intact
    from mof_dac.sampling import refinement_jobs
    sha = lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    plan = json.loads(Path(plan_path).read_text())
    plan['_sha256'] = sha(plan_path)
    path = Path(force_path)
    run = json.loads(path.read_text())
    if run['plan_sha256']!=plan['_sha256'] or run['protocol']!=plan['protocol']+'_force02' \
            or run['fmax']!=.02 or run['step_budget']!=600 or run['checkpoint_sha256']!=plan['checkpoint_sha256']:
        raise ValueError('Wrong force-study protocol')
    if run['loose_report_sha256']!=report_hashes(report_paths,report_path_map):
        raise ValueError('Force study used different loose reports')
    if set(run['source_sha256'])!=EXECUTED_SOURCES:
        raise ValueError('Missing executed force sources')
    for name,digest in run['source_sha256'].items():
        if sha(path.parent/'executed_source'/name)!=digest:
            raise ValueError('Force source snapshot changed')
    baselines = {r['id']:(p,loose,r,w) for p,loose,r,w in refinement_jobs(plan,list(map(Path,report_paths)))}
    if len(run['results'])!=4 or {r['id'] for r in run['results']}!=set(baselines):
        raise ValueError('Force check must retain all four IDs')
    directory = path.parent/'structures'
    def component(e):
        first = read(directory/e['trajectory_file'],index=0)
        final = read(directory/e['trajectory_file'],index=-1)
        cif = directory/e['final_structure_file']
        if sha(cif)!=e['final_structure_sha256']:
            raise ValueError('Force CIF hash mismatch')
        stored = read(cif)
        if not np.array_equal(first.numbers,final.numbers) or not np.allclose(first.cell,final.cell,atol=1e-7,rtol=0) \
                or not np.array_equal(stored.numbers,final.numbers) or not np.allclose(stored.cell,final.cell,atol=1e-7,rtol=0):
            raise ValueError('Force component changed order/cell')
        _,distance = find_mic(stored.positions-final.positions,final.cell,final.pbc)
        if distance.max()>1e-6 or not np.isclose(final.get_potential_energy(),e['final_energy_ev'],atol=1e-7,rtol=0) \
                or not np.isclose(np.linalg.norm(final.get_forces(),axis=1).max(),e['max_force_ev_per_angstrom'],atol=1e-7,rtol=0):
            raise ValueError('Force evidence differs from trajectory/CIF')
        if e['status']=='converged' and e['max_force_ev_per_angstrom']>=.02:
            raise ValueError('Tight force criterion not reached')
        contacts = len(neighbor_list('d',final,.7))//2
        if contacts!=e['severe_contacts_below_0_7_angstrom']:
            raise ValueError('Force contact diagnostic differs from trajectory')
        return first,final
    for gas in ('CO2','H2O'):
        component(run['gas_references'][gas])
    rows = []
    for row in run['results']:
        p,loose,source,winners = baselines[row['id']]
        bare_first,bare_final = component(row['bare'])
        common = min([source['bare']]+[s['empty_after'] for s in source['starts'] if s['status']=='accepted'],
                     key=lambda e:e['final_energy_ev'])
        loose_bare = read(p.parent/'structures'/common['trajectory_file'],index=-1)
        if not np.array_equal(bare_first.numbers,loose_bare.numbers) or not np.allclose(
                bare_first.positions,loose_bare.positions,atol=1e-9,rtol=0):
            raise ValueError('Tight bare did not restart from the selected common reference')
        bare_change = periodic_change(bare_first,bare_final)
        if row.get('periodic_bare_connectivity')!=bare_change or (
                row['status']=='complete_representative_force_check' and any(bare_change.values())):
            raise ValueError('Tight bare changed periodic topology or its diagnostic')
        if {(s['gas'],s['start']) for s in row['starts']}!={(s['gas'],s['start']) for s in winners}:
            raise ValueError('Force poses not chosen by preregistered rule')
        for s in row['starts']:
            if 'system' in s:
                first,final = component(s['system'])
                winner = next(w for w in winners if (w['gas'],w['start'])==(s['gas'],s['start']))
                original = read(p.parent/'structures'/winner['system']['trajectory_file'],index=-1)
                if not np.allclose(first.positions,original.positions,atol=1e-9,rtol=0):
                    raise ValueError('Tight study changed starting basin')
                if 'empty_after' in s:
                    empty_first,empty_final = component(s['empty_after'])
                    if s['status']=='accepted' and (any(periodic_change(first[:-3],final[:-3]).values())
                            or any(periodic_change(first[-3:],final[-3:]).values())
                            or any(periodic_change(empty_first,empty_final).values()) or not intact(s['empty_after'])
                            or s['system']['status']!='converged' or s['system']['severe_contacts_below_0_7_angstrom']!=0):
                        raise ValueError('Tight accepted state changed topology')
        if row['status']!='complete_representative_force_check':
            rows.append({'id':row['id'],'status':'incomplete','initial_target_met':False})
            continue
        if len(row['starts'])!=4 or any(s['status']!='accepted' for s in row['starts']) \
                or not intact(row['bare']) or not all(intact(g) for g in run['gas_references'].values()):
            raise ValueError('Complete force check has failed components')
        bare = min([row['bare']]+[s['empty_after'] for s in row['starts']],key=lambda e:e['final_energy_ev'])['final_energy_ev']
        changes,tight_min = [],{}
        for s in row['starts']:
            winner = next(w for w in winners if (w['gas'],w['start'])==(s['gas'],s['start']))
            before = winner['system']['final_energy_ev']-source['bare_reference_energy_ev']-loose['gas_references'][s['gas']]['final_energy_ev']
            after = s['system']['final_energy_ev']-bare-run['gas_references'][s['gas']]['final_energy_ev']
            if not np.isclose(s['change_ev'],after-before,atol=1e-9,rtol=0):
                raise ValueError('Force adsorption accounting mismatch')
            changes.append(abs(after-before))
            tight_min[s['gas']] = min(tight_min.get(s['gas'],float('inf')),after)
        delta_change = tight_min['CO2']-tight_min['H2O']-source['paired_target_ev']
        rows.append({'id':row['id'],'status':'complete','max_abs_adsorption_shift_ev':max(changes),
            'delta_shift_ev':delta_change,'initial_target_met':max(*changes,abs(delta_change))<=.01})
    return {'scope':'representative continuations only, not full tight-force minima/ranking',
            'report_sha256':sha(path),'configurations':rows,'initial_0_01_ev_target_met':all(r['initial_target_met'] for r in rows)}


def assess(plan_path, report_paths, force_path=None, report_path_map=None):
    from ase.io import read
    from scripts.audit_uio66_adsorption import audit
    sha = lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
    plan = json.loads(Path(plan_path).read_text())
    plan_digest = sha(plan_path)
    expected = {r['id']:r for r in plan['configurations']}
    pools, gas_references, audits, basin_results, source_hashes = {},None,[],[],None
    for path in map(Path,report_paths):
        run = json.loads(path.read_text())
        if run['plan_sha256']!=plan_digest or run['protocol']!=plan['protocol'] or run['starts_per_gas']!=32 \
                or run['fmax']!=.05 or run['step_budget']!=400 or run['checkpoint_sha256']!=plan['checkpoint_sha256']:
            raise ValueError('Report does not match pilot plan/model/budget')
        if set(run['source_sha256'])!=EXECUTED_SOURCES or (source_hashes is not None and source_hashes!=run['source_sha256']):
            raise ValueError('Missing or mixed executed sources')
        source_hashes = run['source_sha256']
        for name,digest in run['source_sha256'].items():
            if sha(path.parent/'executed_source'/name)!=digest:
                raise ValueError('Executed source hash mismatch')
        if gas_references is not None and any(abs(gas_references[g]['final_energy_ev']-
                run['gas_references'][g]['final_energy_ev'])>1e-6 for g in ('CO2','H2O')):
            raise ValueError('Gas references disagree across workers')
        gas_references = run['gas_references']
        audits.append(audit(path))
        for row in run['results']:
            key = row['id']
            if key not in expected or key in pools:
                raise ValueError('Unknown or duplicate configuration')
            pools[key] = row
            if run['input_sha256'].get(key)!=expected[key]['bare_input_sha256']:
                raise ValueError('Bare input provenance changed')
            if row['status']!='complete_model_sample':
                continue
            base = read(path.parent/'structures'/row['bare']['trajectory_file'],index=-1)
            first_bare = read(path.parent/'structures'/row['bare']['trajectory_file'],index=0)
            root = Path(__file__).resolve().parents[1]
            frozen_input = frozen_input_path(root, expected[key]['bare_input'])
            if sha(frozen_input)!=expected[key]['bare_input_sha256']:
                raise ValueError('Frozen input CIF unavailable/changed')
            host_input = read(frozen_input)
            if not np.array_equal(first_bare.numbers,host_input.numbers) or not np.allclose(
                    first_bare.positions,host_input.positions,atol=1e-9,rtol=0) or any(periodic_change(first_bare,base).values()):
                raise ValueError('Bare trajectory does not bind conserved frozen host')
            for gas in ('CO2','H2O'):
                items, labels = [],{}
                for s in [s for s in row['starts'] if s['gas']==gas]:
                    if s['placement']!=expected[key]['poses'][gas][s['start']]:
                        raise ValueError('Start geometry/seed/stratum differs from frozen plan')
                    initial = read(path.parent/'structures'/s['system']['trajectory_file'],index=0)
                    if not np.allclose(initial.positions[len(base):],s['placement']['guest_positions_angstrom'],atol=1e-9,rtol=0):
                        raise ValueError('Initial guest geometry was changed')
                    final = read(path.parent/'structures'/s['system']['trajectory_file'],index=-1)
                    empty_first = read(path.parent/'structures'/s['empty_after']['trajectory_file'],index=0)
                    empty_final = read(path.parent/'structures'/s['empty_after']['trajectory_file'],index=-1)
                    if any(periodic_change(base,final[:len(base)]).values()) or any(periodic_change(empty_first,empty_final).values()):
                        raise ValueError('Accepted start changed periodic host topology')
                    items.append((s['start'],s['system']['final_energy_ev'],final))
                    labels[s['start']] = s['placement']['batch']
                groups = cluster_minima(items,len(base))
                minimum = groups[0]
                basin_results.append({'id':key,'gas':gas,'approximate_minima':groups,
                    'lowest_basin_seen_in_both_batches':{labels[i] for i in minimum['start_ids']}=={0,1},
                    'cross_batch_basins':sum({labels[i] for i in g['start_ids']}=={0,1} for g in groups),
                    'limitations':'No crystal symmetry or exhaustive basin equivalence; complete-link thresholds are diagnostics'})
    if set(pools)!=set(expected):
        raise ValueError('Incomplete eight-design result pool; report missing jobs, do not rank a subset')
    result = stability([pools[r['id']] for r in plan['configurations']],gas_references,
                       plan['assessment']['initial_energy_target_ev'])
    return {'protocol':plan['protocol'],'scope':'development pilot; not independent physical validation',
        'assessment_source_sha256':{name:sha(Path(__file__).resolve().parents[1]/name) for name in
            ['scripts/assess_uio66_sampling_pilot.py','scripts/audit_uio66_adsorption.py','mof_dac/sampling.py']},
        'plan_sha256':plan_digest,'report_sha256':{str(p):sha(p) for p in map(Path,report_paths)},
        'energy_audit_statuses':[a['status_counts'] for a in audits], 'basins':basin_results,
        'provenance_relocation':report_path_map,
        'stability':result,'force_check':assess_force(plan_path,report_paths,force_path,report_path_map) if force_path else
            'pending separate representative 0.02 eV/Angstrom refinement',
        'chemistry_review':'pending; computation alone cannot approve template or DAC claims'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',default='data/design/uio66_sampling_pilot_v2.json')
    parser.add_argument('--reports',nargs='+',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--force-report')
    parser.add_argument('--report-path-map',help='JSON original-path to local-path map; raw hashes must match')
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise ValueError('Preserve assessment; choose new output')
    path_map = json.loads(Path(args.report_path_map).read_text()) if args.report_path_map else None
    result = assess(args.plan,args.reports,args.force_report,path_map)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result['stability']['next_decision']))


if __name__=='__main__':
    main()
