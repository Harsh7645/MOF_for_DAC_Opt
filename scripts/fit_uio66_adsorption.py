"""Fit audited, complete UMA design targets using the label-independent split."""

import argparse
import hashlib
import json
import sys
from importlib.metadata import version
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

from mof_dac.design_fit import evaluate_fit, freeze_split
from scripts.audit_uio66_adsorption import audit


def fit_reports(reports, manifest_path, split_path, bootstrap=200):
    """Require the full frozen pool/protocol; never silently drop failed targets."""
    root = Path(__file__).resolve().parents[1]
    split_path, manifest_path = Path(split_path), Path(manifest_path)
    split = json.loads(split_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    states = {row['id']: row['state'] for row in manifest['configurations']}
    manifest_digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if len(states) != 64 or len({tuple(v) for v in states.values()}) != 64 \
            or any(len(v) != 6 or not set(v) <= {0, 1} for v in states.values()):
        raise ValueError('Expected all 64 unique six-bit substitution configurations')
    groups = []
    for name, digest in split['source_sha256'].items():
        path = root / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Frozen split source changed: {name}')
        if digest == manifest_digest:
            continue
        candidates = [a for a in json.loads(path.read_text())['audits'] if a['tolerance_angstrom'] == 0.05]
        if len(candidates) != 1:
            raise ValueError('Missing frozen duplicate audit')
        groups.append(candidates[0]['groups'])
    if manifest_digest not in split['source_sha256'].values():
        raise ValueError('Manifest not bound to frozen split')
    rebuilt = freeze_split(states, groups, seed=split['seed'])
    if any(split[key] != value for key, value in rebuilt.items()):
        raise ValueError('Frozen split identities or policy changed')
    targets, rows, prefix_targets, fingerprints, protocol = {}, {}, {}, {}, None
    shared = ('protocol', 'model', 'task', 'checkpoint_revision', 'checkpoint_sha256',
              'source_sha256', 'seed', 'starts_per_gas', 'step_budget', 'fmax', 'placement', 'reference')
    for path in map(Path, reports):
        run = json.loads(path.read_text())
        metadata = {key: run[key] for key in shared}
        if protocol is not None and protocol != metadata:
            raise ValueError('Reports use different model, source or sampling protocols')
        protocol = metadata
        if run['protocol'] != 'uio66_uma_paired_flexible_v1' or run['starts_per_gas'] != 4 \
                or run['step_budget'] != 200 or run['fmax'] != 0.05 or run['seed'] != 41 \
                or run['model'] != 'uma-s-1p2p1' or run['task'] != 'odac' \
                or run['checkpoint_revision'] != 'f611b917d9c68566bbbeccbb0aa0f7cad1696cb2' \
                or run['checkpoint_sha256'] != 'b2673b85037b075674c25f55c34ffe1ff1e15db924be977b10a184765df0d5ce':
            raise ValueError('Expected frozen four-start UMA design protocol')
        checked = audit(path)
        fingerprints[str(path)] = checked['source_report_sha256']
        for row in checked['results']:
            if row['id'] in targets or row['id'] not in states:
                raise ValueError('Duplicate or unknown configuration target')
            if row['status'] != 'complete_model_sample' or row['paired_target_ev'] is None:
                raise ValueError(f'Incomplete target: {row["id"]}; preserve failures, do not subset-fit')
            targets[row['id']], rows[row['id']] = row['paired_target_ev'], row
            # Runner records starts in ascending index; prefix sites share the full common bare reference.
            prefix_targets[row['id']] = min(row['gas_results']['CO2']['sampled_adsorption_energies_ev'][:2]) \
                - min(row['gas_results']['H2O']['sampled_adsorption_energies_ev'][:2])
    if set(targets) != set(states):
        raise ValueError('Full frozen 64-state design pool required')
    result = evaluate_fit(states, targets, split, bootstrap=bootstrap)
    prefix_fit = evaluate_fit(states, prefix_targets, split, bootstrap=0)
    identifiers = sorted(states)
    full = np.array([targets[k] for k in identifiers])
    prefix = np.array([prefix_targets[k] for k in identifiers])
    full_rank, prefix_rank = rankdata(full), rankdata(prefix)
    rank_correlation = None if np.ptp(full_rank) == 0 or np.ptp(prefix_rank) == 0 else \
        float(np.corrcoef(full_rank, prefix_rank)[0, 1])
    full_top, prefix_top = set(np.argsort(full, kind='stable')[:10]), set(np.argsort(prefix, kind='stable')[:10])
    result['sampling_budget_sensitivity'] = {
        'scope': 'nested two-start prefix versus four starts, same model/cell; not global-search uncertainty',
        'delta_mean_absolute_change_ev': float(np.mean(np.abs(full-prefix))),
        'delta_max_absolute_change_ev': float(np.max(np.abs(full-prefix))),
        'all_family_spearman': rank_correlation, 'all_family_top10_overlap': len(full_top & prefix_top)/10,
        'training_h_max_absolute_change_ev': float(np.max(np.abs(np.array(result['h_ev'])-prefix_fit['h_ev']))),
        'training_J_max_absolute_change_ev': float(np.max(np.abs(np.array(result['W_ev'])-prefix_fit['W_ev'])))}
    result.update(protocol=protocol, report_sha256=fingerprints,
        fit_source_sha256={name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in
            ('scripts/fit_uio66_adsorption.py', 'mof_dac/design_fit.py', 'mof_dac/parameters.py',
             'scripts/audit_uio66_adsorption.py')},
        fit_environment={'python': sys.version, 'packages': {name: version(name) for name in ('numpy', 'scipy', 'ase')}},
        split_sha256=hashlib.sha256(split_path.read_bytes()).hexdigest(),
        manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        target_definition='min sampled Eads(CO2) - min sampled Eads(H2O); lower preferred',
        sampling_diagnostics=[{'id': k, 'target_ev': targets[k],
            'co2_range_ev': rows[k]['gas_results']['CO2']['sampled_range_ev'],
            'h2o_range_ev': rows[k]['gas_results']['H2O']['sampled_range_ev']}
            for k in sorted(targets)],
        validation_scope='same provisional fixed-template family; not independent DFT/ODAC25 validation')
    ids = [f'amino_slot_{i}' for i in range(6)]
    provenance = {'source': 'audited UMA-s-1p2p1 four-start paired design experiment',
        'method': 'training-only OLS; six binary BDC-to-NH2-BDC substitution choices', 'units': 'eV'}
    def coefficient_uncertainty(index):
        evidence = result['uncertainty']
        std = evidence.get('coefficient_std_ev')
        limits = evidence.get('coefficient_percentiles_2_5_97_5_ev')
        return {'bootstrap_std_ev': std[index] if std is not None else None,
            'bootstrap_interval_ev': [row[index] for row in limits] if limits is not None else None,
            'uncertainty_scope': 'conditional training-group bootstrap; physical and site-sampling error uncalibrated'}
    graph = {'schema_version': 1, 'id': 'uio66_uma_train_fit_v1', 'parameter_regime': 'heuristic',
        'energy_units': 'eV', 'missing_interactions': 'modeled_zero',
        'description': 'Provisional UMA-derived quadratic approximation; chemistry unvalidated. All 15 pairs fit.',
        'offset_ev': result['offset_ev'], 'fit_provenance': {k: result[k] for k in
            ('protocol', 'report_sha256', 'split_sha256', 'manifest_sha256', 'fit_source_sha256',
             'fit_environment', 'validation_scope')},
        'nodes': [{'id': k, 'kind': 'linker', 'h': result['h_ev'][i], **provenance,
            **coefficient_uncertainty(i+1)} for i, k in enumerate(ids)],
        'edges': [{'i': ids[i], 'j': ids[j], 'J': result['W_ev'][i][j], **provenance,
            **coefficient_uncertainty(index+7)} for index, (i, j) in enumerate(zip(*np.triu_indices(6, 1)))],
        'constraints': [],
        'structural_rules': 'Fixed neutral Zr6 node and all six occupied linkers compiled into template; '
            'each bit selects BDC(0)/NH2-BDC(1). No approved amino budget beyond 0..6.'}
    return result, graph


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reports', nargs='+', required=True)
    parser.add_argument('--manifest', default='artifacts/phase3/uio66_structures/manifest.json')
    parser.add_argument('--split', default='data/design/uio66_fit_split.json')
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    output = Path(args.output_dir)
    if output.exists():
        raise ValueError('Choose a new fit output directory; preserve evidence')
    result, graph = fit_reports(args.reports, args.manifest, args.split)
    output.mkdir(parents=True)
    for name, payload in [('fit.json', result), ('instance.json', graph)]:
        (output / name).write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'train_count', 'test_count', 'rank',
        'pairwise_test', 'additive_test')}, indent=2))


if __name__ == '__main__':
    main()
