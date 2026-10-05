"""Read-only v1 source, topology, references, placement and cost audit."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

from mof_dac.adsorption import gas_geometry, place_guests
from mof_dac.sampling import network_winding_rank, periodic_change, periodic_edges
from mof_dac.uio66_structures import map_linkers, substitute_amino


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(root, main, initial_dir, bare_dir):
    from ase import Atoms
    from ase.io import read
    from ase.geometry import find_mic
    from ase.neighborlist import neighbor_list
    from scripts.audit_uio66_adsorption import audit as energy_audit

    root, main, initial_dir, bare_dir = [Path(p).resolve() for p in (root, main, initial_dir, bare_dir)]
    manifest_path = initial_dir/'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    mapping_path = initial_dir/'atom_mapping.json'
    stored_mapping = json.loads(mapping_path.read_text())
    provenance = manifest['parent_provenance']
    parent = Atoms(numbers=provenance['numbers'], positions=provenance['positions_angstrom'],
                   cell=provenance['cell_angstrom'], pbc=provenance['pbc'])
    mapping = map_linkers(parent)
    if mapping['slots'] != stored_mapping['slots'] or mapping['node_atom_indices'] != stored_mapping['node_atom_indices']:
        raise ValueError('Historical mapping cannot be reproduced')
    initial = {r['id']: r for r in manifest['configurations']}
    bare_reports = sorted(bare_dir.glob('gpu*/relaxation.json'))
    bare_inputs = {}
    for p in bare_reports:
        for row in json.loads(p.read_text())['results']:
            if row['id'] in bare_inputs:
                raise ValueError('Duplicate bare ID')
            bare_inputs[row['id']] = p.parent/'structures'/row['final_structure_file']
    reports = sorted(main.glob('worker*/adsorption.json'))
    if len(reports) != 4 or set(initial) != set(bare_inputs) or len(initial) != 64:
        raise ValueError('Expected full 64-design archived pool')
    findings, guests, empties, overhead, audits = [], [], [], [], []
    archived_sources = main/'executed_source'
    all_ids, checkpoints, gas_energies = [], set(), []
    for path in reports:
        run = json.loads(path.read_text())
        for name, digest in run['source_sha256'].items():
            if sha(archived_sources/name) != digest:
                raise ValueError('Executed source hash mismatch')
        for name, digest in run['bare_report_sha256'].items():
            local = bare_dir/Path(name).parent.name/Path(name).name
            if sha(local) != digest:
                raise ValueError('Archived bare report hash mismatch')
        checkpoints.add((run['checkpoint_sha256'], run['checkpoint_revision'], run['task']))
        gas_energies.append([run['gas_references'][g]['final_energy_ev'] for g in ('CO2', 'H2O')])
        audits.append(energy_audit(path))  # re-read final trajectories, forces, CIFs and accounting
        overhead.extend(run['gas_references'].values())
        for row in run['results']:
            key = row['id']
            all_ids.append(key)
            if sha(bare_inputs[key]) != run['input_sha256'][key]:
                raise ValueError('Input CIF hash mismatch')
            info = initial[key]
            cif = initial_dir/info['structure_file']
            if sha(cif) != info['structure_sha256']:
                raise ValueError('Initial proposal changed')
            generated = substitute_amino(parent, mapping, info['state'])
            stored = read(cif)
            stored.set_cell(parent.cell, scale_atoms=True)
            v, distance = find_mic(stored.positions-generated.positions, parent.cell, True)
            if not np.array_equal(stored.numbers, generated.numbers) or distance.max() > 1e-6:
                raise ValueError('Initial amino proposal is not reproducible')
            directory = path.parent/'structures'
            base = read(directory/row['bare']['trajectory_file'], index=-1)
            generated.set_cell(base.cell, scale_atoms=True)
            change = periodic_change(generated, base)
            graph = network_winding_rank(base)
            # This parent is a 3D connected net with eight O neighbors per Zr.
            ii, jj, shifts, distances = neighbor_list('ijSd', base, {('Zr', 'O'): 2.8, ('O', 'H'): 1.3,
                                                                ('C', 'N'): 1.75, ('N', 'H'): 1.3})
            zr_degrees = [int(np.sum((ii == k) & (base.numbers[jj] == 8))) for k in np.flatnonzero(base.numbers == 40)]
            node_h = [k for k in mapping['node_atom_indices'] if base.numbers[k] == 1]
            oh = [(k, jj[(ii == k) & (base.numbers[jj] == 8)].tolist()) for k in node_h]
            amino = []
            for index, slot in enumerate(mapping['slots']):
                if not info['state'][index]:
                    continue
                n, c = slot['substitution_hydrogen'], slot['substitution_carbon']
                hn = jj[(ii == n) & (base.numbers[jj] == 1)]
                cn = jj[(ii == n) & (base.numbers[jj] == 6)]
                if cn.tolist() != [c] or len(hn) != 2:
                    raise ValueError('Amino C/N/H mapping changed')
                a, _ = find_mic(base.positions[c]-base.positions[n], base.cell, True)
                b, _ = find_mic(base.positions[hn]-base.positions[n], base.cell, True)
                amino.append({'slot': slot['id'], 'nitrogen_index': n, 'CN_angstrom': float(np.linalg.norm(a)),
                              'NH_angstrom': np.linalg.norm(b, axis=1).tolist(),
                              'pyramidal_volume_angstrom3': float(abs(np.linalg.det(np.vstack((a, b)))))})
            if graph['components'] != 1 or graph['winding_rank'] != 3 or zr_degrees != [8]*6 \
                    or len(oh) != 4 or any(len(neighbors) != 1 for _, neighbors in oh):
                raise ValueError('Node/periodic-net diagnostic failed')
            supplemental_changes, placement_errors = [], []
            for gas in ('CO2', 'H2O'):
                gas_atoms = read(directory/run['gas_references'][gas]['trajectory_file'], index=-1)
                proposed = place_guests(base, gas_atoms, 4, 41)
                for start in [s for s in row['starts'] if s['gas'] == gas]:
                    system = start['system']
                    first = read(directory/system['trajectory_file'], index=0)
                    final = read(directory/system['trajectory_file'], index=-1)
                    expected, meta = proposed[start['start']]
                    recorded = start['placement']
                    if meta['proposal'] != recorded['proposal'] or any(not np.allclose(meta[k], recorded[k], atol=1e-9, rtol=0)
                            for k in ('rotation','fractional_center','minimum_host_guest_distance_angstrom')) \
                            or not np.allclose(first.positions, expected.positions, atol=1e-9, rtol=0):
                        placement_errors.append((gas, start['start']))
                    pc = periodic_change(base, final[:len(base)])
                    empty_first = read(directory/start['empty_after']['trajectory_file'], index=0)
                    empty_final = read(directory/start['empty_after']['trajectory_file'], index=-1)
                    ec = periodic_change(empty_first, empty_final)
                    if any(pc.values()) or any(ec.values()):
                        supplemental_changes.append({'gas': gas, 'start': start['start'], 'host': pc, 'empty': ec})
                    guests.append(system)
                    empties.append(start['empty_after'])
            overhead.append(row['bare'])
            if placement_errors:
                raise ValueError('Archived placement cannot be reproduced')
            findings.append({'id': key, 'state': info['state'], 'network': graph, 'Zr_O_degrees': zr_degrees,
                'node_H_to_O': oh, 'amino_geometry': amino, 'initial_to_bare_periodic_change': change,
                'adsorption_periodic_changes': supplemental_changes, 'placement_reproduced': 8,
                'historical_delta_ev': row['paired_target_ev']})
    if len(all_ids) != 64 or len(set(all_ids)) != 64 or len(checkpoints) != 1 or np.ptp(gas_energies, axis=0).max() > 1e-10:
        raise ValueError('Pool/model/reference inconsistency')
    def stats(rows):
        t = np.array([r['elapsed_seconds'] for r in rows])
        return {'count': len(rows), 'sum_process_seconds': float(t.sum()), 'mean_seconds': float(t.mean()),
            'median_seconds': float(np.median(t)), 'p90_seconds': float(np.quantile(t, .9)),
            'max_seconds': float(t.max()), 'sum_steps': sum(r['steps'] for r in rows)}
    return {'scope': 'supplemental computational audit; no chemical certificate; historical outputs unchanged',
        'manifest_sha256': sha(manifest_path), 'mapping_sha256': sha(mapping_path),
        'report_sha256': {str(p.relative_to(root)): sha(p) for p in reports},
        'checkpoint': list(checkpoints)[0], 'same_model_gas_energies_ev': gas_energies[0],
        'archived_energy_audits': [{k:v for k,v in a.items() if k not in ('results','structure_trajectory_sha256')} for a in audits],
        'mapping_slots': mapping['slots'], 'configurations': findings,
        'cost': {'guest': stats(guests), 'empty': stats(empties), 'bare_and_gas': stats(overhead),
                 'uncompressed_main_bytes': sum(p.stat().st_size for p in main.rglob('*') if p.is_file())},
        'limitations': ['Distance cutoffs are hypotheses; protonation/synthesis/atom identity require expert review',
            'Atom-index-selected planar amino rotamer and positional isomer space not exhaustively sampled',
            'Same seed 41 used for both gases/configurations in v1; not independent site batches',
            'Runtime reproducibility verified geometrically/accounting-wise, not by new UMA predictions']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main', default='artifacts/kaggle/uio66_adsorption_2026-10-03/main')
    parser.add_argument('--initial', default='artifacts/phase3/uio66_structures')
    parser.add_argument('--bare', default='artifacts/kaggle/uio66_bare_2026-10-03/uio66_full')
    parser.add_argument('--output', default='artifacts/phase3/uio66_sampling_audit_v2.json')
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise ValueError('Preserve audit evidence; choose new output')
    result = audit(Path.cwd(), args.main, args.initial, args.bare)
    root = Path.cwd()
    result['audit_source_sha256'] = {name:sha(root/name) for name in
        ['scripts/audit_uio66_sampling.py','scripts/audit_uio66_adsorption.py',
         'mof_dac/sampling.py','mof_dac/adsorption.py','mof_dac/relaxation.py','mof_dac/uio66_structures.py']}
    for name,digest in result['audit_source_sha256'].items():
        target = output.parent/(output.stem+'_source')/name
        target.parent.mkdir(parents=True,exist_ok=True)
        data = (root/name).read_bytes()
        if hashlib.sha256(data).hexdigest()!=digest:
            raise ValueError('Audit source changed')
        target.write_bytes(data)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'configurations': len(result['configurations']), 'cost': result['cost'],
                      'periodic_host_changes': sum(bool(r['adsorption_periodic_changes']) for r in result['configurations'])}))


if __name__ == '__main__':
    main()
