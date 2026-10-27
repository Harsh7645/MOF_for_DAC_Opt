"""Synthetic admission/leakage tests; these are not material benchmark scores."""
import json
from pathlib import Path

import numpy as np
import pytest

from mof_dac import material_baselines as models
from mof_dac import surrogate_baseline as local


def test_cache_ambiguity_never_silently_selects_energy_minimum():
    def group(numbers):
        elements, counts = np.unique(numbers, return_counts=True)
        return {'mof_id': 'a', 'signature': elements.tolist()+[-1]+counts.tolist(),
                'minima': {'energy': {'bare_atomic_numbers': numbers, 'bare_index': 0,
                                     'bare_trajectory': 't', 'bare_fid': 1}}}
    same = local.cache_candidates({'groups': [group([6, 8]), group([6, 6, 8, 8])]}, {'a', 'missing'})
    assert same[0]['status'] == 'cache_consistent_candidate'
    assert same[1]['status'] == 'missing'
    different = local.cache_candidates({'groups': [group([6, 8]), group([6, 8, 8])]}, {'a'})[0]
    assert different['status'] == 'ambiguous_composition' and different['features'] is None
    broken = group([6, 8]); broken['signature'][-1] = 3
    with pytest.raises(ValueError, match='signature'):
        local.cache_candidates({'groups': [broken]}, {'a'})


def test_fractional_atoms_and_degenerate_cv_rejected():
    with pytest.raises(ValueError, match='integers'):
        models.composition_vector([1, 6.9])
    with pytest.raises(ValueError, match='two independent'):
        models.select_ridge_alpha([[1, 0]], [[0, 1]], ['a'])
    with pytest.raises(ValueError, match='positive alpha'):
        models.fit_ridge([[1, 0], [0, 1]], [[0, 1], [1, 0]], np.nan)


def test_grouped_cv_never_splits_related_records(monkeypatch):
    actual_fit = models.fit_ridge
    observed = []
    def record_fit(x, y, alpha):
        observed.append(set(np.asarray(x)[:, 0].astype(int)))
        return actual_fit(x, y, alpha)
    monkeypatch.setattr(models, 'fit_ridge', record_fit)
    x = np.arange(8).reshape(-1, 1)
    y = np.column_stack([x[:, 0], -x[:, 0]])
    models.select_ridge_alpha(x, y, [str(i) for i in range(8)], groups=['a', 'a', 'b', 'b', 'c', 'c', 'd', 'd'])
    assert observed
    for used in observed:
        for a, b in ((0, 1), (2, 3), (4, 5), (6, 7)):
            assert (a in used) == (b in used)


def test_evaluation_targets_cannot_affect_fitted_model():
    def row(i, split, value):
        return {'mof_id': str(i), 'split': split, 'bare_atomic_numbers': [1, 6, i+2],
                'co2_adsorption_energy_ev': value, 'h2o_adsorption_energy_ev': -value}
    train = [row(i, 'train', i/10) for i in range(8)]
    a = models.evaluate_composition_baselines(train, [row(10, 'val', .1), row(11, 'val', .3)])
    b = models.evaluate_composition_baselines(train, [row(10, 'val', 999), row(11, 'val', -999)])
    for key in ('ridge_model', 'selected_alpha', 'train_cv_mae_by_alpha', 'constant_train_mean_ev'):
        assert a[key] == b[key]


def test_related_parent_alias_and_geometry_leakage():
    def parent(ident):
        return {'mof_id': ident, 'aliases': [], 'parent_group_id': ident,
                'geometry_fingerprint': ident, 'bare_atomic_numbers': [6, 8]}
    train, val = {'a': parent('a')}, {'b': parent('b')}
    assert local.separation(train, val)['cross_pool_composition_collisions'] == 1
    for key, value in [('aliases', ['a']), ('parent_group_id', 'a'), ('geometry_fingerprint', 'a')]:
        copy = {'b': {**val['b'], key: value}}
        with pytest.raises(ValueError, match='overlap'):
            local.separation(train, copy)


def test_incompatible_training_stops_before_evaluation(tmp_path):
    source = tmp_path/'labels.json'
    source.write_text(json.dumps({'contract': {**local.CONTRACT, 'target_field': 'adsorption_energy'}}))
    with pytest.raises(ValueError, match='Compatible reviewed'):
        local.run_baselines(source, 'absent', 'absent', 'absent')


def test_parent_export_hash_identity_and_pool_coverage(tmp_path):
    geometry = tmp_path/'parent.json'
    geometry.write_text(json.dumps({'numbers': [6, 8], 'positions_angstrom': [[0, 0, 0], [1, 0, 0]],
                                    'cell_angstrom': (np.eye(3)*10).tolist(), 'metadata': {'mof_name': 'a'}}))
    manifest = tmp_path/'parents.jsonl'
    row = {'mof_id': 'a', 'split': 'train', 'parent_group_id': 'family-a', 'aliases': [],
           'source_sha256': 'a'*64, 'source_index': 5, 'identity_review': 'synthetic fixture',
           'geometry_path': geometry.name, 'geometry_sha256': local.digest(geometry)}
    manifest.write_text(json.dumps(row)+'\n')
    assert local.read_parents(manifest, ['a'], 'train')['a']['bare_atomic_numbers'] == [6, 8]
    with pytest.raises(ValueError, match='coverage'):
        local.read_parents(manifest, ['a', 'b'], 'train')
    geometry.write_text('{}')
    with pytest.raises(ValueError, match='hash mismatch'):
        local.read_parents(manifest, ['a'], 'train')


def test_frozen_target_mutation_rejected(tmp_path):
    f = tmp_path/'fake.json'; f.write_text('{}')
    with pytest.raises(ValueError, match='Frozen evaluation table changed'):
        local.frozen_pairs(f)


def test_guarded_fit_end_to_end_on_synthetic_exports(tmp_path, monkeypatch):
    def export(prefix, split, count):
        singles, pairs, parents = [], [], []
        for i in range(count):
            ident = prefix+str(i)
            gas_rows = [{'mof_id': ident, 'split': split, 'adsorbate': gas,
                         'adsorption_energy_ev': -.1*(i+1)*(j+1), 'selected_trajectory': ident+gas,
                         'selected_fid': 2, 'source_index': i*2+j}
                        for j, gas in enumerate(('co2', 'h2o'))]
            singles.extend(gas_rows)
            pairs.append({'mof_id': ident, 'split': split,
                          'co2_adsorption_energy_ev': gas_rows[0]['adsorption_energy_ev'],
                          'h2o_adsorption_energy_ev': gas_rows[1]['adsorption_energy_ev'],
                          'co2_provenance': gas_rows[0], 'h2o_provenance': gas_rows[1]})
            geom = tmp_path/(ident+'.json')
            geom.write_text(json.dumps({'numbers': [6, i+1], 'positions_angstrom': [[0, 0, 0], [1, 0, 0]],
                                       'cell_angstrom': (np.eye(3)*(10 if split == 'train' else 11)).tolist(),
                                       'metadata': {'mof_name': ident}}))
            parents.append({'mof_id': ident, 'split': split, 'parent_group_id': ident, 'aliases': [],
                            'source_sha256': 'a'*64, 'source_index': i, 'identity_review': 'synthetic only',
                            'geometry_path': geom.name, 'geometry_sha256': local.digest(geom)})
        labels = tmp_path/(prefix+'labels.json')
        labels.write_text(json.dumps({'contract': local.CONTRACT, 'complete_trajectories': True,
                                     'provenance_review': 'synthetic only', 'single_gas_targets': singles, 'paired_targets': pairs}))
        manifest = tmp_path/(prefix+'parents.jsonl')
        manifest.write_text('\n'.join(json.dumps(p) for p in parents)+'\n')
        return labels, manifest, pairs
    train_labels, train_manifest, _ = export('train', 'train', 6)
    val_labels, val_manifest, val_rows = export('eval', 'val', 2)
    # Only this synthetic fixture bypasses the immutable real-pool hash/count gate.
    monkeypatch.setattr(local, 'frozen_pairs', lambda _: val_rows)
    result = local.run_baselines(train_labels, train_manifest, val_labels, val_manifest)
    assert result['train_samples'] == 6 and result['validation_samples'] == 2
    assert len(result['composition_ridge']['predictions_ev']) == 2
    assert result['separation']['parent_alias_group_exact_geometry_overlap'] == 0
    assert len(result['constant']['metrics']['mae_ev']) == 2
