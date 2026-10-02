import json
from pathlib import Path

import numpy as np

from mof_dac.parameters import pairwise_design
from mof_dac.uio66 import enumerate_design


def test_provisional_design_stoichiometry_and_identifiability():
    path = Path(__file__).resolve().parents[1] / 'data/design/uio66_provisional.json'
    library = json.loads(path.read_text(encoding='utf-8'))
    result = enumerate_design(library)
    rows = result['configurations']
    assert len(rows) == 64 and len({row['id'] for row in rows}) == 64
    for row in rows:
        k = row['amino_linker_count']
        expected = {'C': 48, 'H': 28 + k, 'O': 32, 'Zr': 6}
        if k:
            expected['N'] = k
        assert row['composition'] == expected
        assert row['formal_charge'] == 0 and row['structure_status'] == 'not assembled'
    assert np.linalg.matrix_rank(pairwise_design([row['state'] for row in rows])) == 22
    assert all(edge['pair_coefficient_ev'] is None for edge in result['variable_graph']['edges'])
    library['aminated_linker_budget'] = {'minimum': 2, 'maximum': 2}
    assert len(enumerate_design(library)['configurations']) == 15


def test_real_parent_mapping_and_substitutions_when_evidence_available():
    import pytest
    ase = pytest.importorskip('ase')
    from mof_dac.uio66_structures import map_linkers, substitute_amino
    root = Path(__file__).resolve().parents[1]
    path = root / 'artifacts/kaggle/odac25_reference_audit_2026-10-02/final_frames/phase3_uio66_candidate_parent.json'
    if not path.exists():
        pytest.skip('Authenticated parent artifact is local and not committed')
    payload = json.loads(path.read_text(encoding='utf-8'))
    parent = ase.Atoms(numbers=payload['numbers'], positions=payload['positions_angstrom'],
                       cell=payload['cell_angstrom'], pbc=payload['pbc'])
    mapping = map_linkers(parent)
    assert len(mapping['slots']) == 6 and len(mapping['node_atom_indices']) == 18
    assert sum(len(row['atom_indices']) for row in mapping['slots']) == 96
    for k in range(7):
        atoms = substitute_amino(parent, mapping, [1] * k + [0] * (6-k))
        assert len(atoms) == len(parent) + 2*k
        assert np.count_nonzero(atoms.numbers == 7) == k
        assert np.allclose(atoms.cell.array, parent.cell.array)
    with pytest.raises(ValueError, match='primitive composition'):
        map_linkers(parent[:-1])
    with pytest.raises(ValueError, match='binary substitution'):
        substitute_amino(parent, mapping, [2] * 6)
