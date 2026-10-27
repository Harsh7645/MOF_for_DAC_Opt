"""Check new publication aggregation, without rerunning scientific analyses."""
import copy
import csv
import hashlib
import json
from pathlib import Path

from scripts.build_phase3_methods_package import synthetic_table


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'plans/phase3-methods-scope-v1/evidence'


def saved(name):
    return json.loads((PACKAGE / 'inputs' / (name + '.json')).read_text())


def test_raw_outputs_are_not_scored_as_binary_optima():
    rows = synthetic_table(saved('synthetic'))
    raw = [r for r in rows if r['method'] == 'SNN raw']
    assert [r['binary_feasible'] for r in raw] == [3, 0, 0]
    assert all(r['runs'] == 20 for r in raw)
    assert all(r['optimum_hits'] is None and r['mean_gap_synthetic_units'] is None for r in raw)
    sa = [r for r in rows if r['method'] == 'SA']
    assert len(sa) == 9
    assert all(r['runs'] == 60 and r['binary_feasible'] == 60 for r in sa)
    decoded = [r for r in rows if r['method'] == 'SNN decoded']
    assert [r['optimum_hits'] for r in decoded] == [15, 10, 7]
    assert all(r['binary_feasible'] == 20 for r in decoded)


def test_continuous_feasibility_does_not_imply_integrality():
    data = copy.deepcopy(saved('synthetic'))
    case = next(c for c in data['heldout']['instances'] if c['bits'] == 12 and c['snn_run']['raw_feasible'])
    case['snn_run']['raw_violations']['integrality'] = 0.25
    row = next(r for r in synthetic_table(data) if r['bits'] == 12 and r['method'] == 'SNN raw')
    assert row['continuous_feasible'] == 3
    assert row['binary_feasible'] == 2
    assert row['mean_gap_synthetic_units'] is None


def test_export_preserves_denominators_failure_paths_and_rmse_exception():
    def table(name):
        with (PACKAGE / (name + '.csv')).open(newline='') as handle:
            return list(csv.DictReader(handle))

    assert [len(table(n)) for n in ('T1_synthetic', 'T2_six_bit_objective', 'T3_surrogate',
                                  'T4_stability', 'T5_sampling', 'T6_relaxation')] == [18, 4, 8, 2, 8, 48]
    assert all(r['optimum_hits'] == '' and r['mean_gap_synthetic_units'] == ''
               for r in table('T1_synthetic') if r['method'] == 'SNN raw')
    cv = {r['model']: r for r in table('T3_surrogate') if r['scope'] == 'development leave-group-out'}
    assert float(cv['pairwise']['MAE_meV']) > float(cv['additive']['MAE_meV'])
    assert float(cv['pairwise']['RMSE_meV']) < float(cv['additive']['RMSE_meV'])
    assert sum(r['full_energy_gate_pass'] == 'True' for r in table('T5_sampling')) == 1
    assert sum(r['initial_5meV_target_pass'] == 'False' for r in table('T6_relaxation')) == 4
    assert all(r['status'] == 'complete' for r in table('T6_relaxation'))


def test_new_package_hashes_and_original_sources_are_unchanged():
    receipt = json.loads((PACKAGE / 'receipt.json').read_text())
    assert len(receipt['inputs']) == 18
    assert len(receipt['outputs']) == 33
    for base, entries in ((ROOT, receipt['inputs']), (PACKAGE, receipt['outputs'])):
        for path, expected in entries.items():
            assert hashlib.sha256((base / path).read_bytes()).hexdigest() == expected, path
