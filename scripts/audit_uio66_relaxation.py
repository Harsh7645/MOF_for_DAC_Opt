"""Audit complete bare-structure runs without treating them as adsorption labels."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np


def audit(structures, reports):
    """Verify all 64 identities, file hashes, force status and saved diagnostics."""
    from ase.io import read
    from ase.neighborlist import neighbor_list
    from mof_dac.relaxation import connectivity_change

    structures = Path(structures)
    manifest_path = structures / 'manifest.json'
    expected = {r['id']: r for r in json.loads(manifest_path.read_text())['configurations']}
    rows, runs = {}, []
    for report_path in map(Path, reports):
        run = json.loads(report_path.read_text())
        if run['manifest_sha256'] != hashlib.sha256(manifest_path.read_bytes()).hexdigest():
            raise ValueError('Source manifest changed')
        if len(run['results']) != len(run['expected_ids']):
            raise ValueError('Incomplete run')
        if set(r['id'] for r in run['results']) != set(run['expected_ids']):
            raise ValueError('Run identities do not match its request')
        runs.append({'path': str(report_path), 'sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
                     'checkpoint_sha256': run['checkpoint_sha256'], 'source_sha256': run['source_sha256']})
        for row in run['results']:
            identifier = row['id']
            if identifier in rows or identifier not in expected:
                raise ValueError('Duplicate or unknown identity')
            initial_path = structures / expected[identifier]['structure_file']
            digest = hashlib.sha256(initial_path.read_bytes()).hexdigest()
            if digest != expected[identifier]['structure_sha256'] or digest != run['input_sha256'][identifier]:
                raise ValueError('Input structure hash changed')
            record = dict(row)
            if row['status'] != 'failed':
                final_path = report_path.parent / 'structures' / row['final_structure_file']
                if hashlib.sha256(final_path.read_bytes()).hexdigest() != row['final_structure_sha256']:
                    raise ValueError('Output structure hash changed')
                initial, final = read(initial_path), read(final_path)
                if not np.allclose(initial.cell.array, final.cell.array, atol=1e-8, rtol=0):
                    raise ValueError('Fixed cell changed in output CIF')
                record['cif_connectivity'] = connectivity_change(initial, final)
                last = read(report_path.parent / 'structures' / row['trajectory_file'], index=-1)
                force = float(np.linalg.norm(last.get_forces(), axis=1).max())
                if not np.isclose(force, row['max_force_ev_per_angstrom'], atol=1e-7, rtol=0):
                    raise ValueError('Reported force disagrees with saved trajectory')
                if not np.isclose(last.get_potential_energy(), row['final_energy_ev'], atol=1e-7, rtol=0):
                    raise ValueError('Reported energy disagrees with saved trajectory')
                contacts = len(neighbor_list('d', final, 0.7)) // 2
                if contacts != row['severe_contacts_below_0_7_angstrom']:
                    raise ValueError('Reported contact count disagrees with saved CIF')
                if row['status'] == 'converged' and row['max_force_ev_per_angstrom'] >= run['fmax']:
                    raise ValueError('Invalid convergence assertion')
            rows[identifier] = record
    if set(rows) != set(expected):
        raise ValueError('Not every manifest identity has one result')
    if len({run['checkpoint_sha256'] for run in runs}) != 1:
        raise ValueError('Mixed model checkpoints')
    if len({json.dumps(run['source_sha256'], sort_keys=True) for run in runs}) != 1:
        raise ValueError('Mixed source versions')
    return {'scope': 'bare fixed-cell structures only; not adsorption labels or h/J',
        'configurations': len(rows), 'status_counts': dict(Counter(r['status'] for r in rows.values())),
        'contact_free': sum(r.get('severe_contacts_below_0_7_angstrom') == 0 for r in rows.values()),
        'unchanged_inferred_edges': sum(not r.get('cif_connectivity', {}).get('lost_edges', [None])
            and not r.get('cif_connectivity', {}).get('gained_edges', [None]) for r in rows.values()),
        'chemistry_status': 'provisional; bond cutoffs and model convergence are insufficient validation',
        'runs': runs, 'results': [rows[key] for key in sorted(rows)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--structures', required=True)
    parser.add_argument('--reports', nargs='+', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = audit(args.structures, args.reports)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['runs', 'results']}))


if __name__ == '__main__':
    main()
