"""New preparation/metric tests only; no repeated baseline audit or inference."""
from pathlib import Path
import json
import math
import shutil
import pytest
from scripts.check_qe75_water_convergence_v2 import energy_sensitivities, force_sensitivity, verify


def test_force_norm_not_component_or_rms():
    # Every component below threshold; vector norm still exceeds it.
    result=force_sensitivity([[0,0,0]]*127,[[0,0,0]]*126+[[.004,.004,0]])
    assert result['maximum_norm_eV_A'] > .005
    assert result['sensitivity_target_met'] is False


def test_force_exact_boundary_and_all_atoms():
    assert force_sensitivity([[0,0,0]],[[.003,.004,0]])['sensitivity_target_met']
    with pytest.raises(ValueError):force_sensitivity([[0,0,0]]*127,[[0,0,0]]*126)
    with pytest.raises(ValueError):force_sensitivity([[0,0,0]],[[math.nan,0,0]])


def test_energy_targets_do_not_hide_decomposition_or_missing_hosts():
    # Synthetic: each primary shift is 1.5meV, difference-of-shifts is 3meV.
    r=energy_sensitivities({'complex_eV':[0,0],'host_eV':[0,0]},
                           {'complex_eV':[0,.0015],'host_eV':[0,-.0015]})['comparisons']
    assert r['complex']['sensitivity_target_met'] and r['host']['sensitivity_target_met']
    assert r['guest_associated']['sensitivity_target_met'] is False
    missing=energy_sensitivities({'complex_eV':[0,0]},{'complex_eV':[0,.002]})
    assert missing['comparisons']['complex']['sensitivity_target_met']
    assert missing['comparisons']['host']['sensitivity_target_met'] is None
    assert missing['absolute_accuracy_established'] is False


def test_portable_preparation_and_tampering(tmp_path):
    package=Path('plans/qe75-water-convergence-v2')
    result=verify(package)
    assert result['mapped_atoms']==254 and result['execution_authorized'] is False
    assert result['scientific_results_assessed'] is False
    shutil.copytree(package,tmp_path/'package')
    target=next((tmp_path/'package/inputs').glob('*80_750.in'))
    target.write_bytes(target.read_bytes().replace(b'ecutwfc=80',b'ecutwfc=100'))
    with pytest.raises(ValueError,match='hash mismatch'):verify(tmp_path/'package')


def test_successive_passes_do_not_replace_direct_baseline_comparison():
    # Synthetic cumulative drift: both adjacent steps pass; final vs original fails.
    energies = [{'complex_eV': [0, v]} for v in (0, .0015, .003)]
    forces = [[[0, 0, 0]] * 126 + [[v, 0, 0]] for v in (0, .003, .006)]
    for a, b in ((0, 1), (1, 2)):
        assert energy_sensitivities(energies[a], energies[b])['comparisons']['complex']['sensitivity_target_met']
        assert force_sensitivity(forces[a], forces[b])['sensitivity_target_met']
    assert not energy_sensitivities(energies[0], energies[2])['comparisons']['complex']['sensitivity_target_met']
    assert not force_sensitivity(forces[0], forces[2])['sensitivity_target_met']
