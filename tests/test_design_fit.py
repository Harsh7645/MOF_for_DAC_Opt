"""Recover known quadratic targets while enforcing grouped holdout boundaries."""

import copy
import itertools

import numpy as np
import pytest

from mof_dac.design_fit import freeze_split, evaluate_fit


def test_quadratic_recovery_and_group_leakage_guards():
    states = {'uio66_'+''.join(map(str, state)): list(state) for state in itertools.product((0, 1), repeat=6)}
    ids = sorted(states)
    singletons = [[k] for k in ids]
    combined = [[ids[2], ids[3]]] + [[k] for k in ids if k not in (ids[2], ids[3])]
    split = freeze_split(states, [singletons, combined])
    assert ids[0] in split['train_ids'] and ids[-1] in split['train_ids']
    assert (ids[2] in split['test_ids']) == (ids[3] in split['test_ids'])
    h = np.arange(6)*0.2
    W = np.ones((6, 6))*0.05
    np.fill_diagonal(W, 0)
    targets = {k: float(0.4 + np.dot(v, h) + 0.5*np.array(v)@W@np.array(v)) for k, v in states.items()}
    result = evaluate_fit(states, targets, split, bootstrap=8)
    assert result['rank'] == 22 and result['parameters'] == 22
    assert np.allclose(result['h_ev'], h) and np.allclose(result['W_ev'], W)
    assert result['offset_ev'] == pytest.approx(0.4)
    assert result['pairwise_test']['max_absolute_error_ev'] < 1e-12
    assert result['additive_test']['mae_ev'] > 0.01
    assert result['uncertainty']['attempted'] == 8
    bad_targets = dict(targets)
    bad_targets[ids[0]] = None
    with pytest.raises(ValueError, match='Incomplete'):
        evaluate_fit(states, bad_targets, split)
    bad_split = copy.deepcopy(split)
    bad_split['test_ids'].append(bad_split['train_ids'][0])
    with pytest.raises(ValueError, match='disjoint'):
        evaluate_fit(states, targets, bad_split)
    with pytest.raises(ValueError, match='every state'):
        freeze_split(states, [singletons[:-1]])


def test_report_fit_is_train_only_and_bound_to_frozen_sources(tmp_path, monkeypatch):
    import hashlib
    import json
    from scripts import fit_uio66_adsorption as pipeline
    from mof_dac.data import load_instance

    states = {'uio66_'+''.join(map(str, v)): list(v) for v in itertools.product((0, 1), repeat=6)}
    manifest, groups = tmp_path/'manifest.json', tmp_path/'groups.json'
    manifest.write_text(json.dumps({'configurations': [{'id': k, 'state': v} for k, v in states.items()]}))
    groups.write_text(json.dumps({'audits': [{'tolerance_angstrom': 0.05, 'groups': [[k] for k in states]}]}))
    split = freeze_split(states, [[[k] for k in states]])
    split['source_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (manifest, groups)}
    split_path = tmp_path/'split.json'
    split_path.write_text(json.dumps(split))
    report = tmp_path/'adsorption.json'
    # Explicitly synthetic metadata. The independent trajectory auditor is tested separately.
    report.write_text(json.dumps({'protocol': 'uio66_uma_paired_flexible_v1', 'model': 'uma-s-1p2p1',
        'task': 'odac', 'checkpoint_revision': 'f611b917d9c68566bbbeccbb0aa0f7cad1696cb2', 'checkpoint_sha256':
        'b2673b85037b075674c25f55c34ffe1ff1e15db924be977b10a184765df0d5ce',
        'source_sha256': {}, 'seed': 41, 'starts_per_gas': 4, 'step_budget': 200, 'fmax': 0.05,
        'placement': 'synthetic test', 'reference': 'synthetic test'}))
    rows = [{'id': k, 'status': 'complete_model_sample', 'paired_target_ev':
        float(0.4 + 0.2*sum(v) + 0.1*v[0]*v[1]), 'gas_results':
        {gas: {'sampled_range_ev': 0.1, 'sampled_adsorption_energies_ev':
            [float(0.4+0.2*sum(v)+0.1*v[0]*v[1]) if gas=='CO2' else 0.0]*4}
            for gas in ('CO2', 'H2O')}} for k, v in states.items()]
    monkeypatch.setattr(pipeline, 'audit', lambda _: {'source_report_sha256': 'synthetic', 'results': rows})
    fit, graph = pipeline.fit_reports([report], manifest, split_path, bootstrap=2)
    instance = tmp_path/'instance.json'
    instance.write_text(json.dumps(graph))
    problem, metadata = load_instance(instance)
    for row in rows:
        assert metadata['offset_ev'] + problem.energy(states[row['id']]) == pytest.approx(row['paired_target_ev'])
    assert metadata['parameter_regime'] == 'heuristic' and len(graph['edges']) == 15
    assert fit['sampling_budget_sensitivity']['delta_max_absolute_change_ev'] == 0
    from scripts import benchmark_uio66_fit as comparison
    from mof_dac.optimizers import Result
    fit_path = tmp_path/'fit.json'
    fit_path.write_text(json.dumps(fit))
    monkeypatch.setattr(comparison, 'solve_gurobi', lambda *a, **k:
        Result('synthetic_test', np.zeros(6), 0.001, 'optimal'))
    monkeypatch.setattr(comparison, 'simulated_annealing', lambda *a, **k:
        Result('synthetic_test', np.ones(6), 0.002, 'feasible_candidate'))
    monkeypatch.setattr(comparison, 'solve_nonconvex_experiment', lambda *a, **k:
        Result('synthetic_test', np.full(6, 0.51), 0.003, 'feasible_unconverged'))
    checked = comparison.benchmark(fit_path, instance)
    assert checked['oracle']['state']['model_delta_ev'] == pytest.approx(0.4)
    assert checked['summary']['SNN_raw']['binary_feasible'] == 0
    assert checked['summary']['SNN_threshold']['binary_feasible'] == 10
    assert checked['summary']['SNN_threshold']['optimum_hits'] == 0
    assert checked['summary']['Gurobi']['optimum_hits'] == 1
    assert checked['summary']['SA']['optimum_hits'] == 0
    assert all(r['state']['binary_optimality_gap_ev'] is None for r in checked['runs'] if r['method']=='SNN_raw')
    json.dumps(checked, allow_nan=False)
    for row in rows:
        if row['id'] in split['test_ids']:
            row['paired_target_ev'] += 10
    second, _ = pipeline.fit_reports([report], manifest, split_path, bootstrap=2)
    assert second['h_ev'] == fit['h_ev'] and second['W_ev'] == fit['W_ev']
    assert second['pairwise_test']['mae_ev'] == pytest.approx(10)
    rows[0]['paired_target_ev'] = None
    with pytest.raises(ValueError, match='Incomplete target'):
        pipeline.fit_reports([report], manifest, split_path)
    groups.write_text(groups.read_text()+' ')
    with pytest.raises(ValueError, match='source changed'):
        pipeline.fit_reports([report], manifest, split_path)
