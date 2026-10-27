"""Windows-safe audit/feature recovery and guarded constant/ridge execution.

Run as python -m scripts.local_surrogate_baseline audit --output <new-directory>.
Only the fit subcommand trains, after all admission gates pass. No network access.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import platform
import shutil
import time
import tracemalloc
import zipfile

import numpy as np

from mof_dac.surrogate_baseline import (CONTRACT, cache_candidates, digest, frozen_pairs,
                                       load_json, run_baselines)

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIR = ROOT/'artifacts/kaggle/odac25_paired_targets_2026-09-14'
AUDIT_DIR = ROOT/'artifacts/kaggle/odac25_reference_audit_2026-10-02'
FROZEN = TARGET_DIR/'paired_targets.json'


def save(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def verify_archives():
    files = {f['name']: f for f in load_json(TARGET_DIR/'evidence_manifest.json')['files']}
    if any(digest(TARGET_DIR/name) != item['sha256'] for name, item in files.items()):
        raise ValueError('Frozen target evidence manifest mismatch')
    archive_name = 'ODAC25_Phase3_reference_lookup.zip'
    receipt = load_json(AUDIT_DIR/'evidence_manifest.json')[archive_name]
    if digest(AUDIT_DIR/archive_name) != receipt['sha256']:
        raise ValueError('Archived reference evidence changed')
    verified = []
    with zipfile.ZipFile(AUDIT_DIR/archive_name) as archive:
        for member in archive.infolist():
            if member.file_size > 4 * 1024**2:
                raise ValueError('Unexpected large evidence member')
            local = AUDIT_DIR/'reference_lookup'/member.filename
            if local.read_bytes() != archive.read(member):
                raise ValueError('Extracted evidence differs from archive: '+member.filename)
            verified.append({'path': local.relative_to(ROOT).as_posix(), 'sha256': digest(local)})
    return verified


def measured(function):
    tracemalloc.start()
    start = time.perf_counter()
    result = function()
    elapsed = time.perf_counter()-start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, {'seconds': elapsed, 'python_traced_peak_bytes': peak,
                    'memory_scope': 'Python allocations only, not total process RSS'}


def inventory():
    roots = [ROOT/'data', ROOT/'artifacts', ROOT/'local', Path.home()/'Downloads']
    found = []
    for root in roots:
        if not root.exists():
            continue
        for directory, folders, files in os.walk(root):
            folders[:] = [f for f in folders if not any(x in f.lower() for x in ('test', 'pytest', '__pycache__', '.venv'))]
            for name in files:
                p = Path(directory)/name
                if p.suffix.lower() in ('.parquet', '.lmdb', '.aselmdb', '.pkl'):
                    found.append({'path': str(p), 'bytes': p.stat().st_size})
    return {'roots': [str(p) for p in roots], 'excluded': 'test fixtures, environments, pycache', 'candidates': found}


def plot_coverage(rows, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    labels = ['Consistent cached\ncomposition candidate', 'Ambiguous\ncomposition', 'Missing cache']
    counts = [sum(r['status'] == s for r in rows) for s in ('cache_consistent_candidate', 'ambiguous_composition', 'missing')]
    fig, ax = plt.subplots(figsize=(7, 4), layout='constrained')
    bars = ax.bar(labels, counts, color=['#4477AA', '#EE7733', '#888888'])
    ax.bar_label(bars)
    ax.set_ylim(0, 138)
    ax.set_ylabel('Frozen evaluation MOFs')
    ax.set_title('Composition recovery audit — not benchmark results')
    fig.savefig(output/'feature_coverage.png', dpi=160)
    plt.close(fig)


def audit(output):
    output.mkdir(parents=True, exist_ok=False)
    evidence = verify_archives()
    rows = frozen_pairs(FROZEN)
    cache_path = AUDIT_DIR/'reference_lookup/phase3_material_base_audited.bare_cache.json'
    cache = load_json(cache_path)
    ids = [r['mof_id'] for r in rows]
    sample, sample_cost = measured(lambda: cache_candidates(cache, set(ids[:8])))
    save(output/'sample8.json', {'rows': sample, 'measurement': sample_cost})
    # Scaling processes only a 474-kB cache and 138 output vectors, not raw LMDBs.
    candidates, full_cost = measured(lambda: cache_candidates(cache, set(ids)))
    save(output/'feature_candidates.json', candidates)
    with (output/'feature_status.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=['mof_id', 'status', 'distinct_fraction_vectors', 'cache_entries', 'verified_parent_structure'])
        writer.writeheader()
        writer.writerows({k: row[k] for k in writer.fieldnames} for row in candidates)
    with (output/'composition_candidates.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['mof_id', 'evidence_status']+[f'fraction_Z{z:03d}' for z in range(1, 119)])
        for row in candidates:
            writer.writerow([row['mof_id'], row['status']]+(row['features'] or ['']*118))
    lookup = load_json(AUDIT_DIR/'reference_lookup/phase3_reference_frame_lookup.json')
    parent = load_json(AUDIT_DIR/'reference_lookup/phase3_uio66_candidate_parent.json')
    parent_id = parent['metadata']['mof_name']
    parent_matches = [g for g in cache['groups'] if g['mof_id'] == parent_id and any(
        v['bare_index'] == parent['source_index'] and v['bare_atomic_numbers'] == parent['numbers'] for v in g['minima'].values())]
    if not parent_matches or cache['sha256'] != parent['source_sha256']:
        raise ValueError('Full parent export does not match archived bare cache provenance')
    report = {
        'status': 'blocked_no_compatible_training_no_benchmark_results', 'contract': CONTRACT,
        'frozen_pairs': len(rows), 'frozen_single_gas_labels': 285,
        'frozen_sha256': digest(FROZEN), 'cache_sha256': digest(cache_path),
        'feature_schema': '118 bare-parent elemental fractions, Z=1..118, dimensionless; no geometry-derived descriptors',
        'candidate_counts': {s: sum(r['status'] == s for r in candidates) for s in sorted({r['status'] for r in candidates})},
        'ambiguous_ids': [r['mof_id'] for r in candidates if r['status'] == 'ambiguous_composition'],
        'full_parent_exports_matched': [parent_id],
        'parent_export_scope': 'Numbers/index/source hash match; chemistry and reference-energy identity not thereby verified',
        'reference_lookup': {'distinct_unresolved_energies': len(lookup['references']),
                             'without_stored_energy_match': sum(not r['hits'] for r in lookup['references'])},
        'training_inventory': inventory(), 'sample8': sample_cost, 'all138': full_cost,
        'disk_free_GiB': shutil.disk_usage(ROOT).free/2**30,
        'environment': {'python': platform.python_version(), 'platform': platform.platform(), 'numpy': np.__version__},
        'verified_evidence': evidence,
        'unresolved': ['compatible corrected/final-frame training export', 'complete verified parent structure exports',
                       '31 multi-composition parent identities', 'reviewed parent-family/alias map and split separation',
                       'ODAC25 reference geometry mapping; independent of frozen-field regression',
                       'higher-cutoff DFT deferred for RAM; Phase 3 incomplete'],
        'models_fit': 0, 'evaluation_metrics': None,
    }
    save(output/'audit.json', report)
    plot_coverage(candidates, output)
    print(json.dumps({k: report[k] for k in ('status', 'candidate_counts', 'sample8', 'all138', 'models_fit')}, indent=2))


def fit(args):
    # Do not create success artifacts until admission and fitting succeed.
    if args.output.exists():
        raise ValueError('Use a new output directory; preserve previous evidence')
    result = run_baselines(args.train_labels, args.train_parents, FROZEN, args.evaluation_parents)
    args.output.mkdir(parents=True)
    save(args.output/'results.json', result)
    targets = {r['mof_id']: r for r in frozen_pairs(FROZEN)}
    with (args.output/'predictions.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['mof_id', 'model', 'co2_true_eV', 'h2o_true_eV', 'co2_pred_eV', 'h2o_pred_eV', 'delta_true_eV', 'delta_pred_eV'])
        for model in ('constant', 'composition_ridge'):
            for ident, pred in zip(result['validation_mof_ids'], result[model]['predictions_ev']):
                target = targets[ident]
                co2, h2o = target['co2_adsorption_energy_ev'], target['h2o_adsorption_energy_ev']
                writer.writerow([ident, model, co2, h2o, *pred, co2-h2o, pred[0]-pred[1]])
    print('Saved full-pool predictions and separate-gas/competition metrics; no physical validation claim.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    a = commands.add_parser('audit')
    a.add_argument('--output', type=Path, required=True)
    f = commands.add_parser('fit')
    for name in ('train-labels', 'train-parents', 'evaluation-parents', 'output'):
        f.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    audit(args.output) if args.command == 'audit' else fit(args)
