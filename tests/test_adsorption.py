"""Geometry, flexible-reference accounting and failure preservation checks."""

import numpy as np
import pytest

pytest.importorskip('ase')
from ase import Atoms
from mof_dac.adsorption import gas_geometry, place_guests, summarize_adsorption, evaluate_candidate


def evidence(identifier, energy):
    return {'id': identifier, 'status': 'converged', 'final_energy_ev': energy,
        'severe_contacts_below_0_7_angstrom': 0,
        'connectivity': {'lost_edges': [], 'gained_edges': []}}


def test_placement_is_reproducible_and_respects_periodic_clearance():
    from ase.geometry import find_mic
    host = Atoms('C', positions=[[0, 0, 0]], cell=[12, 12, 12], pbc=True)
    gas = gas_geometry('CO2')
    assert len(gas) == 3 and not gas.pbc.any()
    first, second = place_guests(host, gas, 3), place_guests(host, gas, 3)
    for (left, meta), (right, other) in zip(first, second):
        assert np.array_equal(left.positions, right.positions) and meta == other
        _, distance = find_mic(left.positions[1:] - left.positions[0], left.cell, pbc=True)
        assert distance.min() >= 2.0
        assert np.allclose(left[1:].get_all_distances(), gas.get_all_distances())
    with pytest.raises(ValueError):
        gas_geometry('CO')
    with pytest.raises(ValueError):
        place_guests(host, gas, 0)


def test_common_bare_reference_and_incomplete_pairs():
    bare = evidence('initial_bare', -10)
    gases = {'CO2': evidence('isolated_co2', -3), 'H2O': evidence('isolated_h2o', -2)}
    starts = [
        {'gas': 'CO2', 'start': 0, 'status': 'accepted', 'system': evidence('co2', -14),
         'empty_after': evidence('co2_empty', -11)},
        {'gas': 'H2O', 'start': 0, 'status': 'accepted', 'system': evidence('h2o', -13.5),
         'empty_after': evidence('h2o_empty', -11.2)}]
    result = summarize_adsorption(bare, gases, starts, 1)
    assert result['bare_reference_id'] == 'h2o_empty'
    assert result['gas_results']['CO2']['minimum_sampled_adsorption_ev'] == pytest.approx(0.2)
    assert result['paired_target_ev'] == pytest.approx(0.5)
    broken = {**starts[1], 'status': 'rejected_diagnostic', 'empty_after': evidence('broken_empty', -100)}
    result = summarize_adsorption(bare, gases, [starts[0], broken], 1)
    assert result['bare_reference_id'] == 'co2_empty' and result['paired_target_ev'] is None
    assert result['gas_results']['H2O']['accepted_starts'] == 0


def test_adsorption_pipeline_saves_systems_and_desorbed_references(tmp_path):
    from ase.calculators.calculator import Calculator, all_changes
    from ase.io import read
    from mof_dac.relaxation import relax_fixed_cell

    class SyntheticBookkeeping(Calculator):
        implemented_properties = ['energy', 'forces']
        def calculate(self, atoms=None, properties=None, system_changes=all_changes):
            super().calculate(atoms, properties, system_changes)
            interaction = (0.2 if 1 in atoms.numbers else 0.5) if len(atoms) == 4 else 0
            self.results = {'energy': float(-len(atoms)-interaction), 'forces': np.zeros((len(atoms), 3))}

    calculator = SyntheticBookkeeping()
    structures = tmp_path / 'structures'
    gases, references = {}, {}
    for name in ('CO2', 'H2O'):
        references[name] = relax_fixed_cell(gas_geometry(name), calculator, structures, name)
        gases[name] = read(structures / references[name]['trajectory_file'], index=-1)
    host = Atoms('C', positions=[[0, 0, 0]], cell=[12, 12, 12], pbc=True)
    saved = []
    result = evaluate_candidate(host, calculator, gases, references, structures, 'synthetic', starts=1,
                                save_start=lambda bare, rows: saved.append(len(rows)))
    assert result['status'] == 'complete_model_sample' and saved == [1, 2]
    assert result['paired_target_ev'] == pytest.approx(-0.3)
    assert len(list(structures.glob('synthetic*_empty.traj'))) == 2
    assert all(r['status'] == 'accepted' for r in result['starts'])
    import json
    from scripts.audit_uio66_adsorption import audit
    report = tmp_path / 'adsorption.json'
    payload = {'expected_ids': ['synthetic'], 'results': [result], 'gas_references': references,
        'fmax': 0.05, 'starts_per_gas': 1, 'protocol': 'synthetic_test', 'scope': 'synthetic bookkeeping test'}
    report.write_text(json.dumps(payload))
    checked = audit(report)
    assert checked['status_counts'] == {'complete_model_sample': 1}
    result['starts'][0]['system']['final_energy_ev'] += 0.01
    report.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match='energy mismatch'):
        audit(report)
