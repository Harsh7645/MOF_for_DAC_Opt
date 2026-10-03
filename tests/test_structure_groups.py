"""Meaningful geometry matching and convergence evidence checks."""

import numpy as np
import pytest


def test_parent_operation_groups_preserve_atom_order_translation_and_cell_frame():
    ase = pytest.importorskip('ase')
    pytest.importorskip('spglib')
    from mof_dac.structure_groups import parent_operation_groups

    parent = ase.Atoms('CO', positions=[[0.2, 0.3, 0.4], [1.4, 0.3, 0.4]], cell=[8, 8, 8], pbc=True)
    reordered = parent[[1, 0]]
    reordered.positions += [8, 0, 0]
    rotation = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    rotated = parent.copy()
    rotated.positions = rotated.positions @ rotation
    rotated.set_cell(rotated.cell.array @ rotation)
    changed = parent.copy()
    changed.positions[1, 0] += 0.5
    result = parent_operation_groups(parent, {'a': parent, 'b': reordered, 'c': rotated, 'd': changed}, 1e-4)
    assert sorted(map(sorted, result['groups'])) == [['a', 'b', 'c'], ['d']]
    assert all(edge['max_mapped_distance_angstrom'] <= 1e-4 for edge in result['verified_match_graph'])
    with pytest.raises(ValueError, match='tolerance'):
        parent_operation_groups(parent, {'a': parent}, 0)
    changed.set_cell([9, 8, 8])
    with pytest.raises(ValueError, match='fixed periodic cells'):
        parent_operation_groups(parent, {'a': changed})


def test_relaxation_saves_convergence_and_step_limit_separately(tmp_path):
    ase = pytest.importorskip('ase')
    from ase.calculators.calculator import Calculator, all_changes
    from mof_dac.relaxation import relax_fixed_cell

    class SyntheticHarmonic(Calculator):
        implemented_properties = ['energy', 'forces']

        def calculate(self, atoms=None, properties=None, system_changes=all_changes):
            super().calculate(atoms, properties, system_changes)
            delta = atoms.positions - np.array([[2.0, 2.0, 2.0]])
            self.results = {'energy': float(0.5*np.sum(delta**2)), 'forces': -delta}

    atoms = ase.Atoms('H', positions=[[2.8, 2.0, 2.0]], cell=[8, 8, 8], pbc=True)
    stopped = relax_fixed_cell(atoms, SyntheticHarmonic(), tmp_path, 'stopped', steps=0)
    assert stopped['status'] == 'step_limit' and stopped['steps'] == 0
    result = relax_fixed_cell(atoms, SyntheticHarmonic(), tmp_path, 'converged', steps=30)
    assert result['status'] == 'converged' and result['max_force_ev_per_angstrom'] < 0.05
    assert result['final_energy_ev'] < result['initial_energy_ev']
    assert (tmp_path / result['trajectory_file']).exists()
    assert (tmp_path / result['final_structure_file']).exists()
    assert result['chemical_validity'].startswith('unverified')

    # Audit uses saved trajectory forces/energy, not only self-reported status.
    import hashlib
    import json
    from ase.io import write
    from scripts.audit_uio66_relaxation import audit
    inputs = tmp_path / 'inputs'
    inputs.mkdir()
    initial_file = inputs / 'converged.cif'
    write(initial_file, atoms)
    digest = hashlib.sha256(initial_file.read_bytes()).hexdigest()
    manifest = inputs / 'manifest.json'
    manifest.write_text(json.dumps({'configurations': [{'id': 'converged',
        'structure_file': initial_file.name, 'structure_sha256': digest}]}))
    evidence = tmp_path / 'run' / 'relaxation.json'
    evidence.parent.mkdir()
    # Re-run to the same directory layout used by the production runner.
    result = relax_fixed_cell(atoms, SyntheticHarmonic(), evidence.parent / 'structures', 'converged')
    run = {'manifest_sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(),
        'input_sha256': {'converged': digest}, 'expected_ids': ['converged'],
        'checkpoint_sha256': 'synthetic-test-calculator', 'source_sha256': {},
        'fmax': 0.05, 'results': [result]}
    evidence.write_text(json.dumps(run))
    checked = audit(inputs, [evidence])
    assert checked['status_counts'] == {'converged': 1}
    assert checked['unchanged_inferred_edges'] == 1
    with pytest.raises(ValueError, match='Duplicate'):
        audit(inputs, [evidence, evidence])
    run['results'][0]['final_energy_ev'] += 1.0
    evidence.write_text(json.dumps(run))
    with pytest.raises(ValueError, match='energy disagrees'):
        audit(inputs, [evidence])


def test_connectivity_diagnostic_detects_broken_periodic_bond():
    ase = pytest.importorskip('ase')
    from mof_dac.relaxation import connectivity_change

    initial = ase.Atoms('CO', positions=[[7.8, 2, 2], [1.0, 2, 2]], cell=[8, 8, 8], pbc=True)
    translated = initial.copy()
    translated.positions[1] += [8, 0, 0]
    same = connectivity_change(initial, translated)
    assert not same['lost_edges'] and same['max_atom_displacement_angstrom'] < 1e-12
    broken = initial.copy()
    broken.positions[1, 0] += 1.0
    assert connectivity_change(initial, broken)['lost_edges'] == [[0, 1]]
    broken.numbers[1] = 7
    with pytest.raises(ValueError, match='atom order'):
        connectivity_change(initial, broken)
