"""Execution-contract checks for the Kaggle material benchmark."""

import json
from pathlib import Path

import pytest

from kaggle.audit_odac25_references import reference_audit
from kaggle.phase3_material_pipeline import input_digests, validate_gas_references, mlip_predictions
from mof_dac.odac25 import paired_metrics


def test_reference_audit_exposes_inconsistent_corrected_fields():
    class Atoms:
        def __init__(self, shift):
            self.info = {'nco2': 1, 'nh2o': 0, 'nn2': 0, 'no2': 0, 'nads': 1,
                         'energy': -32.0 + shift, 'energy_old': -32.0,
                         'energy_mof': -10.0, 'energy_mof_old': -10.0,
                         'energy_ads': -1.0, 'energy_ads_corrected': -1.0}

        def __len__(self):
            return 4

        def get_potential_energy(self):
            return self.info['energy']

    class Dataset:
        def __len__(self):
            return 2

        def get_atoms(self, index):
            return Atoms(index * 0.2)

    result = reference_audit(Dataset())
    assert result['statistics']['co2:energy-energy_mof-energy_ads_corrected']['spread_ev'] == pytest.approx(0.2)
    assert result['statistics']['co2:energy_old-energy_mof_old-energy_ads']['spread_ev'] == 0
    assert result['status'].startswith('diagnostic_only')


def test_kaggle_notebook_code_cells_compile():
    root = Path(__file__).resolve().parents[1]
    for path in (root / 'kaggle').glob('*.ipynb'):
        for index, cell in enumerate(json.loads(path.read_text(encoding='utf-8'))['cells']):
            if cell['cell_type'] == 'code':
                source = '\n'.join(line for line in ''.join(cell['source']).splitlines()
                                   if not line.startswith('%'))
                compile(source, f'{path}:{index}', 'exec')


def test_cached_input_binding_and_reference_guard(tmp_path):
    path = tmp_path / 'dataset'
    path.write_bytes(b'first')
    original = input_digests({'val': path})
    path.write_bytes(b'second')
    assert original != input_digests({'val': path})
    good = {gas: {'max_absolute_deviation_from_median': 1e-9} for gas in ('co2', 'h2o')}
    validate_gas_references(good)
    good['co2']['max_absolute_deviation_from_median'] = 0.7
    with pytest.raises(ValueError, match='Inconsistent gas reference'):
        validate_gas_references(good)


def test_spearman_uses_average_ties_and_rejects_constant_rank():
    actual = [[0, 0], [1, 0], [2, 0], [3, 0]]
    assert paired_metrics(actual, [[0, 0]] * 4)['competition_spearman'] is None
    tied = paired_metrics(actual, [[0, 0], [0, 0], [2, 0], [3, 0]])
    assert tied['competition_spearman'] == pytest.approx(0.9486832980505138)
    assert tied['predicted_unique_deltas'] == 3


def test_mlip_subtraction_preserves_frozen_kpoint_convention(tmp_path):
    class Atoms:
        def __init__(self, energy):
            self.energy = energy

        def copy(self):
            return Atoms(self.energy)

        def get_potential_energy(self):
            return self.energy

    class Dataset:
        def __init__(self, energy):
            self.energy = energy

        def get_atoms(self, index):
            return Atoms(self.energy)

    rows = [{'mof_id': 'm', 'bare_index': 0, 'target_index': 0, 'adsorbate': 'co2',
             'system_kpoint_correction_ev': 0.2, 'bare_kpoint_correction_ev': 0.1}]
    path = tmp_path / 'progress.json'
    result = mlip_predictions('test', object(), Dataset(-32), Dataset(-10), rows,
                              {'co2': -21}, path)
    assert result['predictions'][0]['adsorption_energy_ev'] == pytest.approx(-1.1)
    assert json.loads(path.read_text())['status'] == 'finished'


def test_bare_selection_uses_final_frames_and_invalidates_old_cache(monkeypatch, tmp_path):
    import sys
    import types
    import numpy as np
    from kaggle.phase3_material_pipeline import validation_records

    class Atoms:
        def __init__(self, numbers, **info):
            self.numbers = np.array(numbers)
            self.info = {'mof_name': 'm', **info}

    bare = [Atoms([40], name='a', fid=0, energy=-12, energy_old=-12.1),
            Atoms([40], name='a', fid=1, energy=-10, energy_old=-10.1),
            Atoms([40], name='b', fid=2, energy=-9, energy_old=-9.1)]
    target = [Atoms([40, *gas], name=name, fid=3, energy=-32, energy_old=-32.2,
                    energy_mof=-10.1, energy_ads_corrected=-1, nads=1,
                    nco2=int(name == 'co2'), nh2o=int(name == 'h2o'), nn2=0, no2=0)
              for name, gas in [('co2', [6, 8, 8]), ('h2o', [1, 1, 8])]]

    class Dataset:
        def __init__(self, config):
            self.rows = bare if config['src'] == 'bare' else target

        def __len__(self):
            return len(self.rows)

        def get_atoms(self, index):
            return self.rows[index]

    monkeypatch.setitem(sys.modules, 'fairchem.core.datasets',
                        types.SimpleNamespace(AseDBDataset=Dataset))
    cache = tmp_path / 'bare.json'
    cache.write_text(json.dumps({'sha256': 'digest', 'rows': 3, 'groups': []}))
    result = validation_records('target', 'bare', bare_cache_path=cache, bare_digest='digest')
    assert len(result[3]) == 1
    assert all(row['bare_index'] == 1 and row['bare_fid'] == 1 for row in result[2])
    assert all(row['bare_reference_field'] == 'energy_old' for row in result[2])
    assert all(row['bare_kpoint_correction_ev'] == pytest.approx(0.1) for row in result[2])
    assert 'max fid' in json.loads(cache.read_text())['selection_rule']
    validation_records('target', 'bare', bare_cache_path=cache, bare_digest='digest')
    with pytest.raises(ValueError, match='Bare cache dataset changed'):
        validation_records('target', 'bare', bare_cache_path=cache, bare_digest='other')
