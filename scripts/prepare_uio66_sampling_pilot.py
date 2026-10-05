"""Freeze eight v2 patterns, 512 initial poses and an archive-based cost estimate."""

import argparse
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np

from mof_dac.adsorption import gas_geometry
from mof_dac.sampling import pilot_proposals, linker_node_graph


# Selected from historical v1 only; new pilot labels have never been inspected.
SELECTION = {
    '000000': 'Unfunctionalized end member; node/linker adsorption control',
    '111111': 'Fully aminated end member; historical best sampled state',
    '110111': 'Historical fitted optimum, different from sampled optimum',
    '001001': 'Largest absolute historical fitted-vs-sampled rank disagreement (57 vs 20)',
    '000110': 'Two-amino arrangement; opposite-direction rank disagreement (23 vs 56)',
    '001100': 'Third two-amino arrangement, different slots; rank disagreement (25 vs 52)',
    '000111': 'Three-amino contiguous-index pattern; matched composition with 010101',
    '010101': 'Three-amino alternating-index pattern; indices are not chemical adjacency',
}


def prepare(root, bare_dir, main_dir, audit_path):
    from ase.io import read
    started = time.perf_counter()
    root, bare_dir, main_dir, audit_path = [Path(p).resolve() for p in (root, bare_dir, main_dir, audit_path)]
    digest = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
    audit = json.loads(audit_path.read_text())
    split_path = root/'data/design/uio66_fit_split.json'
    split = json.loads(split_path.read_text())
    mapping_path = root/'artifacts/phase3/uio66_structures/atom_mapping.json'
    mapping = json.loads(mapping_path.read_text())
    from ase import Atoms
    manifest = json.loads((root/'artifacts/phase3/uio66_structures/manifest.json').read_text(encoding='utf-8'))
    p = manifest['parent_provenance']
    parent = Atoms(numbers=p['numbers'],positions=p['positions_angstrom'],cell=p['cell_angstrom'],pbc=p['pbc'])
    node_graph = linker_node_graph(parent,mapping)
    paths, main_rows, report_hashes = {}, {}, {}
    for report in sorted(bare_dir.glob('gpu*/relaxation.json')):
        for row in json.loads(report.read_text())['results']:
            paths[row['id']] = report.parent/'structures'/row['final_structure_file']
    for report in sorted(main_dir.glob('worker*/adsorption.json')):
        report_hashes[str(report.relative_to(root))] = digest(report)
        main_rows.update({r['id']: r for r in json.loads(report.read_text())['results']})
    if audit['report_sha256'] != report_hashes or audit['mapping_sha256'] != digest(mapping_path):
        raise ValueError('Audit does not bind current historical reports/mapping')
    fit_path = root/'artifacts/phase3/uio66_uma_fit/fit.json'
    fit = json.loads(fit_path.read_text())
    predicted = {}
    for key in sorted(main_rows):
        x = np.array(list(map(int, key[-6:])))
        predicted[key] = float(fit['offset_ev']+np.array(fit['h_ev'])@x+.5*x@np.array(fit['W_ev'])@x)
    rank = {key: i+1 for i, key in enumerate(sorted(predicted, key=lambda k: (predicted[k], k)))}
    sampled_rank = {key:i+1 for i,key in enumerate(sorted(main_rows,key=lambda k:(main_rows[k]['paired_target_ev'],k)))}
    rows, historical_cost = [], 0.
    for index, (pattern, reason) in enumerate(SELECTION.items()):
        key = 'uio66_'+pattern
        path = paths[key]
        host = read(path)
        poses = {gas: pilot_proposals(host, gas_geometry(gas), mapping, index, gas_index)
                 for gas_index, gas in enumerate(('CO2', 'H2O'))}
        row = main_rows[key]
        historical_cost += sum(s[field]['elapsed_seconds'] for s in row['starts'] for field in ('system','empty_after'))*8
        rows.append({'id': key, 'pattern': pattern, 'configuration_index': index, 'reason': reason,
            'historical_fitted_rank': rank[key], 'historical_sampled_rank': sampled_rank[key],
            'historical_split_role': 'test' if key in split['test_ids'] else 'train',
            'duplicate_group_index': next(i for i,g in enumerate(split['groups']) if key in g),
            'bare_input': str(path.relative_to(root)), 'bare_input_sha256': digest(path), 'poses': poses})
    if len({r['duplicate_group_index'] for r in rows}) != 8:
        raise ValueError('Selected patterns must occupy distinct historical duplicate groups')
    overhead = audit['cost']['bare_and_gas']['sum_process_seconds']
    nominal = historical_cost+overhead
    backup = root/'artifacts/kaggle/uio66_adsorption_2026-10-03/notebook_full_execution_backup.ipynb'
    notebook = json.loads(backup.read_text(encoding='utf-8'))
    cell = next(c for c in notebook['cells'] if 'Full adsorption worker return codes' in str(c.get('outputs','')))
    timing = cell['metadata']['execution']
    observed_wall = (datetime.fromisoformat(timing['iopub.status.idle'])-datetime.fromisoformat(timing['iopub.status.busy'])).total_seconds()
    baseline = sum(audit['cost'][k]['sum_process_seconds'] for k in ('guest','empty','bare_and_gas'))
    overhead_factor = observed_wall/(baseline/4)
    nominal *= overhead_factor
    disk = audit['cost']['uncompressed_main_bytes']
    # Measured process time is not GPU utilization or a CPU-inference measurement.
    return {'protocol': 'uio66_eight_stratified_32_v2', 'status': 'preselected; geometry dry-run only; no new UMA energies',
        'selection_scope': 'development sampling pilot, deliberately informed by historical v1; not blind validation',
        'historical_split_sha256': digest(split_path), 'historical_fit_sha256': digest(fit_path),
        'audit_sha256': digest(audit_path), 'historical_report_sha256': report_hashes,
        'mapping_sha256': digest(mapping_path), 'mapping': mapping,'linker_node_graph':node_graph,
        'checkpoint_sha256': audit['checkpoint'][0], 'checkpoint_revision': audit['checkpoint'][1],
        'model': 'uma-s-1p2p1', 'task': 'odac', 'master_seed': 20261003,
        'starts_per_gas': 32, 'batches': 2, 'starts_per_batch': 16,
        'batch_quotas': {'node_OH':2,'node_oxo':2,'linker_face':2,'substitution_pocket':2,'random_void':8},
        'force_tolerance_ev_per_angstrom': .05, 'step_budget':400,
        'reference_policy': 'same pinned model; lowest accepted empty after both gases; batch-specific and pooled references',
        'failure_policy': 'all 32 starts must pass; incomplete pairs null; no successful-only ranking or random fallback',
        'minima_definition': {'energy_ev':.01,'host_rmsd_angstrom':.15,'guest_rmsd_angstrom':.35,
                              'clustering':'complete-link; same species permutations and periodic translation; no crystal symmetry equivalence'},
        'assessment': {'initial_energy_target_ev':.01,'near_tie_delta_ev':.02,'rank_spearman_minimum':.9,
                       'top2_overlap_required':1.0,'scope':'heuristic initial assessment, not universal error bound'},
        'force_check': {'ids':['uio66_000000','uio66_111111','uio66_110111','uio66_001001'],
                       'rule':'lowest accepted targeted and random-void system per gas, pooled over batches',
                       'additional_guest_relaxations':16,'fmax':.02,'steps':600,
                       'reference':'also refine four common empties, two isolated gases and each stripped empty'},
        'configurations': rows,
        'cost_estimate': {'historical_guest_process_seconds':audit['cost']['guest']['sum_process_seconds'],
            'observed_4worker_2T4_cell_wall_seconds':observed_wall,'timing_backup_sha256':digest(backup),
            'observed_wall_over_sum_process_div4_factor':overhead_factor,
            'historical_empty_process_seconds':audit['cost']['empty']['sum_process_seconds'],
            'selected_scaled_nominal_process_seconds':nominal,
            'nominal_4worker_2T4_wall_hours':nominal/4/3600,
            'planning_4worker_2T4_wall_hours_range':[nominal/4/3600,3*nominal/4/3600],
            'planning_2worker_1T4_wall_hours_range':[nominal/2/3600,3*nominal/2/3600],
            'planning_1worker_1T4_wall_hours_range':[nominal/3600,3*nominal/3600],
            'force_refinement_allowance_fraction':.25, 'observed_main_uncompressed_bytes':disk,
            'planning_uncompressed_bytes_range':[disk,3*disk], 'reserve_output_disk_bytes':2*1024**3,
            'limitations':['1-to-3x contingency for site choice/400-step budget; not a measured v2 runtime',
                'Add 25% time/storage allowance for representative tighter-force study, not measured yet',
                'Four workers shared two T4s in v1; summed wall seconds are not independent GPU-hours',
                'GPU allocator peaks ~1.6GB per worker exclude CUDA context/model/runtime memory',
                'CPU-only UMA throughput was not measured; CPU dry-run time is not its estimate']},
        'dry_run_seconds':time.perf_counter()-started,
        'test_policy':'51/13 split bytes and historical scores preserved; all 13 previously scored, no untouched final test claim'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bare', default='artifacts/kaggle/uio66_bare_2026-10-03/uio66_full')
    parser.add_argument('--main', default='artifacts/kaggle/uio66_adsorption_2026-10-03/main')
    parser.add_argument('--audit', default='artifacts/phase3/uio66_sampling_audit_v2.json')
    parser.add_argument('--output', default='data/design/uio66_sampling_pilot_v2.json')
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise ValueError('Selection/poses are frozen; choose a new plan path')
    result = prepare(Path.cwd(), args.bare, args.main, args.audit)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'patterns':[r['pattern'] for r in result['configurations']],
                      'poses':sum(len(p) for r in result['configurations'] for p in r['poses'].values()),
                      'dry_run_seconds':result['dry_run_seconds'],'cost':result['cost_estimate']}))


if __name__ == '__main__':
    main()
