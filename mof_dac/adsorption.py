"""Provisional single-molecule adsorption sampling; no DAC performance claims."""

import numpy as np

from mof_dac.relaxation import connectivity_change, relax_fixed_cell


def gas_geometry(name):
    """ASE initial gas geometry [3,3]; isolated/nonperiodic 30-Angstrom box."""
    from ase.build import molecule

    if name not in ('CO2', 'H2O'):
        raise ValueError('Only neutral CO2 and H2O are supported')
    atoms = molecule(name)
    atoms.set_cell([30, 30, 30])
    atoms.center()
    atoms.pbc = False
    return atoms


def place_guests(host, gas, count=4, seed=41, clearance=2.0):
    """Seeded uniform fractional positions/orientations; reject host overlaps.

    Same seed and fixed cell couple the proposals across substitution states.
    Rejection can change accepted sites. This bounded sample is not a global search.
    """
    from ase.geometry import find_mic
    from scipy.spatial.transform import Rotation

    if count < 1 or not np.isfinite(clearance) or clearance <= 0 or not np.all(host.pbc):
        raise ValueError('Positive count/clearance and periodic host required')
    rng = np.random.default_rng(seed)
    centered = gas.positions - gas.get_center_of_mass()
    candidates = []
    for proposal in range(10000):
        center = rng.random(3)
        rotation = Rotation.random(random_state=rng).as_matrix()
        guest = gas.copy()
        guest.positions = centered @ rotation.T + center @ host.cell.array
        guest.set_cell(host.cell)
        guest.pbc = True
        _, distances = find_mic((host.positions[:, None] - guest.positions[None]).reshape(-1, 3),
                                host.cell, pbc=True)
        if distances.min() < clearance:
            continue
        system = host.copy() + guest
        candidates.append((system, {'proposal': proposal, 'fractional_center': center.tolist(),
            'rotation': rotation.tolist(), 'minimum_host_guest_distance_angstrom': float(distances.min())}))
        if len(candidates) == count:
            return candidates
    raise ValueError('Placement budget exhausted; no placeholder structures emitted')


def intact(evidence):
    """Require convergence, severe-contact and declared connectivity diagnostics."""
    return (evidence['status'] == 'converged' and evidence['severe_contacts_below_0_7_angstrom'] == 0
        and not evidence['connectivity']['lost_edges'] and not evidence['connectivity']['gained_edges'])


def summarize_adsorption(bare, gas_references, starts, expected_starts):
    """Common lowest sampled empty-MOF reference; incomplete pairs stay null."""
    references = [bare] + [r['empty_after'] for r in starts if r.get('status') == 'accepted']
    references = [r for r in references if intact(r)]
    if not references:
        return {'status': 'failed_bare_reference', 'paired_target_ev': None}
    reference = min(references, key=lambda r: r['final_energy_ev'])
    summaries = {}
    for gas in ('CO2', 'H2O'):
        rows = [r for r in starts if r['gas'] == gas]
        valid = [r for r in rows if r.get('status') == 'accepted']
        complete = len(rows) == expected_starts and len(valid) == expected_starts and intact(gas_references[gas])
        energies = [r['system']['final_energy_ev'] - reference['final_energy_ev']
                    - gas_references[gas]['final_energy_ev'] for r in valid]
        selected = min(valid, key=lambda r: r['system']['final_energy_ev']) if valid else None
        summaries[gas] = {'complete': complete, 'expected_starts': expected_starts,
            'accepted_starts': len(valid), 'sampled_adsorption_energies_ev': energies,
            'minimum_sampled_adsorption_ev': min(energies) if energies else None,
            'sampled_range_ev': float(np.ptp(energies)) if energies else None,
            'selected_start': selected['start'] if selected else None}
    complete = all(r['complete'] for r in summaries.values())
    return {'status': 'complete_model_sample' if complete else 'incomplete_model_sample',
        'bare_reference_id': reference['id'], 'bare_reference_energy_ev': reference['final_energy_ev'],
        'gas_results': summaries, 'paired_target_ev':
            summaries['CO2']['minimum_sampled_adsorption_ev'] - summaries['H2O']['minimum_sampled_adsorption_ev']
            if complete else None,
        'scope': 'UMA minimum among declared starts; not DFT, equilibrium selectivity or global minima'}


def evaluate_candidate(host, calculator, gas_atoms, gas_references, output, identifier,
                       starts=4, seed=41, fmax=0.05, steps=200, save_start=None):
    """Flexible fixed-cell host+guest relaxation and desorbed bare-reference search."""
    from pathlib import Path
    from ase.io import read

    output = Path(output)
    bare = relax_fixed_cell(host, calculator, output, identifier + '_bare', fmax, steps)
    if not intact(bare):
        return {'id': identifier, 'bare': bare, 'starts': [], 'status': 'failed_bare_reference', 'paired_target_ev': None}
    base = read(output / bare['trajectory_file'], index=-1)
    base.calc = None
    records = []
    for gas in ('CO2', 'H2O'):
        proposals = place_guests(base, gas_atoms[gas], starts, seed)
        for index, (system, placement) in enumerate(proposals):
            name = f'{identifier}_{gas}_{index}'
            row = {'gas': gas, 'start': index, 'placement': placement, 'status': 'failed'}
            try:
                combo = relax_fixed_cell(system, calculator, output, name, fmax, steps)
                final = read(output / combo['trajectory_file'], index=-1)
                framework = final[:len(base)]
                molecule = final[len(base):]
                host_change = connectivity_change(base, framework)
                # Compare intramolecular bonds only; contacts to the host may be physical.
                guest_change = connectivity_change(system[len(base):], molecule)
                empty = relax_fixed_cell(framework, calculator, output, name + '_empty', fmax, steps)
                row.update(system=combo, empty_after=empty, host_connectivity=host_change,
                           guest_connectivity=guest_change)
                conserved = not any(check[k] for check in (host_change, guest_change)
                                    for k in ('lost_edges', 'gained_edges'))
                row['status'] = 'accepted' if combo['status'] == 'converged' and conserved and intact(empty) \
                    and combo['severe_contacts_below_0_7_angstrom'] == 0 else 'rejected_diagnostic'
            except Exception as error:
                row['error'] = f'{type(error).__name__}: {error}'
            records.append(row)
            if save_start:
                save_start(bare, records)
    return {'id': identifier, 'bare': bare, 'starts': records,
            **summarize_adsorption(bare, gas_references, records, starts)}
