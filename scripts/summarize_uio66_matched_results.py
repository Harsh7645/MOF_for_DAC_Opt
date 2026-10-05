"""Post-run coordinate/energy summaries only; never loads a model or alters raw data."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from ase.io import read

from mof_dac.geometry_diagnostic import mic, contacts, guest_geometry, host_descriptors, angle
from mof_dac.shared_rigid_host import map_guest, geometry_hash


def summarize(manifest, raw, output):
    output.mkdir(parents=True, exist_ok=False)
    plan = json.loads(manifest.read_text())
    jobs = {j['id']: j for j in plan['jobs']}
    for job in list(jobs.values()):
        if job['kind'] in ('matched', 'replay'):
            jobs[job['id'] + '_empty'] = {**job, 'kind': 'empty'}
    rows, details = [], {}
    for identifier, job in jobs.items():
        result = json.loads((raw / identifier / 'result.json').read_text())
        assert result['status'] == 'complete', identifier
        atoms = [read(raw / identifier / f'checkpoint_{t:.3f}.traj') for t in plan['thresholds_ev_A']]
        for checkpoint, state in zip(result['checkpoints'], atoms):
            assert abs(state.get_potential_energy() - checkpoint['energy_ev']) < 1e-10
            assert np.linalg.norm(state.get_forces(), axis=1).max() < checkpoint['tolerance']
        guest = job['kind'] in ('matched', 'replay', 'rigid')
        row = {'id': identifier, 'kind': job['kind'], 'steps': result['steps']}
        for t, state in zip(plan['thresholds_ev_A'], atoms):
            row[f'E_{t:.3f}_eV'] = float(state.get_potential_energy())
        for i, (before, after) in enumerate(zip(atoms, atoms[1:])):
            suffix = ('02_to_01', '01_to_005')[i]
            d = mic(after, after.positions - before.positions)
            row[f'dE_{suffix}_eV'] = float(after.get_potential_energy() - before.get_potential_energy())
            row[f'max_displacement_{suffix}_A'] = float(np.linalg.norm(d, axis=1).max())
            if guest:
                row[f'host_max_{suffix}_A'] = float(np.linalg.norm(d[:-3], axis=1).max())
                row[f'guest_max_{suffix}_A'] = float(np.linalg.norm(d[-3:], axis=1).max())
        rows.append(row)
        if guest:
            details[identifier] = [{'tolerance': t, 'contacts': contacts(state, plan['mapping']),
                                   'guest_com_A': guest_geometry(state)[0].tolist(),
                                   'host': host_descriptors(state, plan['mapping'])}
                                  for t, state in zip(plan['thresholds_ev_A'], atoms)]
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (output / 'checkpoint_changes.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    # Reconstruct every mapping independently from the frozen source and exact H*.
    host = read(raw / 'shared_rigid_host/host.traj')
    mappings = []
    for job in plan['jobs']:
        if job['kind'] != 'rigid':
            continue
        mapped, evidence = map_guest(read(manifest.parent / job['pose']), host)
        saved = read(raw / f"shared_rigid_host/{job['id']}.traj")
        assert evidence['valid'] and geometry_hash(mapped) == geometry_hash(saved)
        mappings.append({'id': job['id'], **evidence})
    # Original question: 110111/CO2/start31 continuation, all saved frames.
    key = 'uio66_110111_CO2_b1_random'
    frames = read(raw / key / 'path.traj', ':')
    energy = np.array([a.get_potential_energy() for a in frames])
    forces = np.array([np.linalg.norm(a.get_forces(), axis=1).max() for a in frames])
    distance = np.array([a.get_distance(15, 126, mic=True) for a in frames])
    base = host_descriptors(frames[0], plan['mapping'])['rings']['L1']
    rocking = [angle(base, host_descriptors(a, plan['mapping'])['rings']['L1'], unsigned=True) for a in frames]
    fig, ax = plt.subplots(2, 2, figsize=(10, 6), constrained_layout=True)
    ax[0, 0].plot(energy - energy[0]); ax[0, 0].set_ylabel('Complex energy change (eV)')
    ax[0, 1].semilogy(forces); ax[0, 1].set_ylabel('Maximum force (eV/A)')
    for t in plan['thresholds_ev_A']:
        ax[0, 1].axhline(t, color='gray', linewidth=.6, linestyle='--')
    ax[1, 0].plot(distance); ax[1, 0].set_ylabel('H15 ... CO2 O126 (A)')
    ax[1, 1].plot(rocking); ax[1, 1].set_ylabel('L1 ring rocking from input (degrees)')
    for a in ax.flat:
        a.set_xlabel('Saved frame index (boundary frames may repeat)')
    fig.suptitle('110111 CO2 start31: frozen matched continuation')
    fig.savefig(output / 'start31_continuation.png', dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 4), constrained_layout=True)
    vals = [abs(r['dE_01_to_005_eV']) * 1000 for r in rows]
    ax.bar(range(len(rows)), vals, color=['#b84232' if v > 5 else '#317b9b' for v in vals])
    ax.axhline(5, color='black', linestyle='--', label='Initial diagnostic target: 5 meV')
    ax.set(xlabel='Path index in checkpoint_changes.csv', ylabel='Absolute last-checkpoint change (meV)',
           title='All48 completed paths: force convergence does not imply energy stability')
    ax.legend(); fig.savefig(output / 'energy_stability.png', dpi=160); plt.close(fig)
    delta = mic(frames[-1], frames[-1].positions - frames[0].positions)
    summary = {'checkpoint_rows': rows, 'runtime_mapping_reconstruction': mappings,
               'guest_checkpoint_details': details,
               'start31': {'frames': len(frames), 'total_energy_change_ev': float(energy[-1]-energy[0]),
                           'largest_single_frame_drop_ev': float(np.diff(energy).min()),
                           'H15_O126_initial_final_A': [float(distance[0]), float(distance[-1])],
                           'L1_rocking_final_deg': rocking[-1],
                           'largest_movers': [{'atom': int(i), 'element': frames[-1][i].symbol,
                                              'displacement_A': float(np.linalg.norm(delta[i]))}
                                             for i in np.argsort(np.linalg.norm(delta, axis=1))[-8:][::-1]]},
               'interpretation_scope': 'Post-hoc coordinate summaries, no new inference or changed criteria.'}
    (output / 'geometry_analysis.json').write_text(json.dumps(summary, indent=2) + '\n')
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()}
    (output / 'analysis_hashes.json').write_text(json.dumps(hashes, indent=2) + '\n')
    print(json.dumps({'paths_checked': len(rows), 'mappings_reconstructed': len(mappings), 'start31': summary['start31']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    summarize(args.manifest, args.raw, args.output)
