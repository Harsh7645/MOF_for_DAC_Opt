"""Fixed-cell relaxation evidence; convergence is not chemical validation."""

import hashlib
import time
from pathlib import Path

import numpy as np


def connectivity_change(initial, final):
    """Compare distance-inferred typed edges; diagnostic, not bond validation."""
    from ase.geometry import find_mic
    from ase.neighborlist import neighbor_list

    if not np.array_equal(initial.numbers, final.numbers) or not np.allclose(
            initial.cell.array, final.cell.array, atol=1e-10, rtol=0):
        raise ValueError('Connectivity comparison requires identical atom order and cell')
    cutoffs = {('C', 'C'): 1.75, ('C', 'H'): 1.3, ('C', 'O'): 1.65,
               ('C', 'N'): 1.75, ('N', 'H'): 1.3, ('O', 'H'): 1.3, ('Zr', 'O'): 2.8}

    def edges(atoms):
        left, right = neighbor_list('ij', atoms, cutoffs)
        return {(int(i), int(j)) for i, j in zip(left, right) if i < j}

    before, after = edges(initial), edges(final)
    _, displacement = find_mic(final.positions - initial.positions, initial.cell, initial.pbc)
    return {'status': 'distance-cutoff diagnostic; chemistry review required',
        'cutoffs_angstrom': {'-'.join(pair): distance for pair, distance in cutoffs.items()},
        'initial_edges': len(before), 'final_edges': len(after),
        'lost_edges': [list(edge) for edge in sorted(before - after)],
        'gained_edges': [list(edge) for edge in sorted(after - before)],
        'max_atom_displacement_angstrom': float(displacement.max())}


def relax_fixed_cell(atoms, calculator, output, identifier, fmax=0.05, steps=150):
    """Relax positions [n,3], preserve cell [3,3], save trajectory and final CIF."""
    from ase.io import write
    from ase.neighborlist import neighbor_list
    from ase.optimize import LBFGS

    if not np.isfinite(fmax) or fmax <= 0 or steps < 0:
        raise ValueError('Positive force tolerance and nonnegative step budget required')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    state = atoms.copy()
    cell = state.cell.array.copy()
    state.calc = calculator
    initial_energy = float(state.get_potential_energy())
    trajectory = output / f'{identifier}.traj'
    optimizer = LBFGS(state, trajectory=str(trajectory), logfile=str(output / f'{identifier}.log'),
                      maxstep=0.1)
    converged = bool(optimizer.run(fmax=fmax, steps=steps))
    force = float(np.linalg.norm(state.get_forces(), axis=1).max())
    energy = float(state.get_potential_energy())
    if not np.isfinite([initial_energy, energy, force]).all() or not np.all(np.isfinite(state.positions)):
        raise ValueError('Nonfinite relaxation output')
    if not np.array_equal(state.cell.array, cell):
        raise ValueError('Fixed cell changed')
    state.wrap()
    final = output / f'{identifier}.cif'
    write(final, state)
    contacts = neighbor_list('d', state, 0.7)
    return {'id': identifier, 'status': 'converged' if converged and force < fmax else 'step_limit',
        'initial_energy_ev': initial_energy, 'final_energy_ev': energy,
        'max_force_ev_per_angstrom': force, 'force_tolerance_ev_per_angstrom': fmax,
        'steps': optimizer.nsteps, 'step_budget': steps,
        'elapsed_seconds': time.perf_counter() - started,
        'severe_contacts_below_0_7_angstrom': int(len(contacts) // 2),
        'atoms': len(state), 'formula': state.get_chemical_formula(),
        'trajectory_file': trajectory.name, 'final_structure_file': final.name,
        'final_structure_sha256': hashlib.sha256(final.read_bytes()).hexdigest(),
        'connectivity': connectivity_change(atoms, state),
        'chemical_validity': 'unverified; force convergence and contact check are insufficient',
        'target_scope': 'component total energy; adsorption requires consistent host/system/gas subtraction'}
