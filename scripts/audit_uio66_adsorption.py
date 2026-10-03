"""Recompute provisional adsorption labels from saved energies and trajectories."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np


def audit(report_path):
    from ase.io import read
    from ase.geometry import find_mic
    from ase.neighborlist import neighbor_list
    from mof_dac.adsorption import intact, summarize_adsorption
    from mof_dac.relaxation import connectivity_change

    report_path = Path(report_path)
    run = json.loads(report_path.read_text())
    structures = report_path.parent / 'structures'
    if len(run['results']) != len(run['expected_ids']) or set(r['id'] for r in run['results']) != set(run['expected_ids']):
        raise ValueError('Incomplete or duplicated candidate result pool')
    fingerprints = {}

    def check(evidence):
        if evidence['status'] == 'failed':
            return
        cif = structures / evidence['final_structure_file']
        digest = hashlib.sha256(cif.read_bytes()).hexdigest()
        if digest != evidence['final_structure_sha256']:
            raise ValueError('Structure hash changed')
        trajectory = structures / evidence['trajectory_file']
        first, final = read(trajectory, index=0), read(trajectory, index=-1)
        if not np.array_equal(first.numbers, final.numbers) or not np.array_equal(first.cell.array, final.cell.array):
            raise ValueError('Atom order/composition or fixed cell changed')
        stored = read(cif)
        if not np.array_equal(stored.numbers, final.numbers) or not np.allclose(
                stored.cell.array, final.cell.array, atol=1e-7, rtol=0):
            raise ValueError('CIF composition/cell disagrees with trajectory')
        _, difference = find_mic(stored.positions-final.positions, final.cell, final.pbc)
        if difference.max() > 1e-6:
            raise ValueError('CIF coordinates disagree with trajectory')
        energy, force = float(final.get_potential_energy()), float(np.linalg.norm(final.get_forces(), axis=1).max())
        if not np.isclose(energy, evidence['final_energy_ev'], atol=1e-7, rtol=0):
            raise ValueError('Trajectory/report energy mismatch')
        if not np.isclose(force, evidence['max_force_ev_per_angstrom'], atol=1e-7, rtol=0):
            raise ValueError('Trajectory/report force mismatch')
        if evidence['status'] == 'converged' and force >= run['fmax']:
            raise ValueError('Convergence flag contradicts saved force')
        contacts = int(len(neighbor_list('d', final, 0.7)) // 2)
        if contacts != evidence['severe_contacts_below_0_7_angstrom']:
            raise ValueError('Severe-contact diagnostic contradicts trajectory')
        change = connectivity_change(first, final)
        for key in ('lost_edges', 'gained_edges'):
            if change[key] != evidence['connectivity'][key]:
                raise ValueError('Connectivity diagnostic contradicts trajectory')
        for path in (cif, trajectory):
            fingerprints[path.relative_to(report_path.parent).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()

    for gas in ('CO2', 'H2O'):
        check(run['gas_references'][gas])
        if not intact(run['gas_references'][gas]):
            raise ValueError('Invalid gas reference')
    rows = []
    for row in run['results']:
        if row['status'] == 'failed':
            rows.append({'id': row['id'], 'status': 'failed', 'paired_target_ev': None})
            continue
        check(row['bare'])
        keys = {(r['gas'], r['start']) for r in row['starts']}
        allowed = {(gas, index) for gas in ('CO2', 'H2O') for index in range(run['starts_per_gas'])}
        if len(keys) != len(row['starts']) or not keys <= allowed:
            raise ValueError('Duplicate gas/start identity')
        for start in row['starts']:
            for field in ('system', 'empty_after'):
                if field in start:
                    check(start[field])
            if start['status'] == 'accepted':
                combo = read(structures / start['system']['trajectory_file'], index=-1)
                initial = read(structures / start['system']['trajectory_file'], index=0)
                bare = read(structures / row['bare']['trajectory_file'], index=-1)
                host_change = connectivity_change(bare, combo[:len(bare)])
                guest_change = connectivity_change(initial[len(bare):], combo[len(bare):])
                if start['system']['status'] != 'converged' \
                        or start['system']['severe_contacts_below_0_7_angstrom'] != 0 or not intact(start['empty_after']) \
                        or any(change[k] for change in (host_change, guest_change) for k in ('lost_edges', 'gained_edges')):
                    raise ValueError('Accepted start violates convergence/connectivity diagnostics')
        summary = summarize_adsorption(row['bare'], run['gas_references'],
            sorted(row['starts'], key=lambda r: (r['gas'], r['start'])), run['starts_per_gas'])
        if summary['status'] != row['status'] or summary['paired_target_ev'] != row['paired_target_ev']:
            raise ValueError('Saved paired target/status disagrees with recomputed energy accounting')
        rows.append({'id': row['id'], **summary})
    return {'scope': run['scope'], 'source_report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
        'protocol': run['protocol'], 'starts_per_gas': run['starts_per_gas'], 'configurations': len(rows),
        'status_counts': dict(Counter(r['status'] for r in rows)),
        'structure_trajectory_sha256': fingerprints, 'results': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = audit(args.report)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('structure_trajectory_sha256', 'results')}))


if __name__ == '__main__':
    main()
