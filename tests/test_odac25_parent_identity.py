"""Identity diagnostics must not turn matching surrogates into proof."""
import numpy as np
import pytest

from scripts.audit_odac25_parent_identity import array, fragment_signature, pair_status
from scripts.inspect_odac25_mirror_sample import Inert


def inert_array(values, dtype='i8', fortran=False):
    values = np.array(values, dtype='<'+dtype, order='F' if fortran else 'C')
    dt = Inert(dtype, False, True)
    dt.global_name = 'numpy.dtype'
    dt.state = (3, '<', None, None, None, -1, -1, 0)
    result = Inert()
    result.global_name = 'numpy._core.multiarray._reconstruct'
    result.state = (1, values.shape, dt, fortran, values.tobytes(order='F' if fortran else 'C'))
    return result


def block(numbers, edges, charges=None):
    return {'block_type': 'LINKER', 'atomic_numbers': inert_array(numbers),
            'bond_indices': inert_array(edges), 'bond_types': inert_array([1]*len(edges[0])),
            'formal_charges': inert_array(charges or [0]*len(numbers))}


def test_safe_array_fortran_and_rejects_nonfinite_or_bad_layout():
    assert array(inert_array([[1, 2], [3, 4]], fortran=True)).tolist() == [[1, 2], [3, 4]]
    with pytest.raises(ValueError, match='Nonfinite'):
        array(inert_array([float('nan')], dtype='f8'))
    bad = inert_array([1, 2])
    bad.state = bad.state[:-1]+(b'bad',)
    with pytest.raises(ValueError, match='buffer size'):
        array(bad)


def test_fragment_signature_ignores_atom_permutation():
    a = block([6, 8, 1], [[0, 1], [1, 2]])
    b = block([1, 6, 8], [[1, 2], [2, 0]])
    assert fragment_signature(a) == fragment_signature(b)


def test_fragment_signature_detects_hydrogen_placement_and_charge():
    a = fragment_signature(block([6, 8, 1], [[0, 1], [1, 2]]))
    b = fragment_signature(block([6, 8, 1], [[0, 0], [1, 2]]))
    c = fragment_signature(block([6, 8, 1], [[0, 1], [1, 2]], [0, -1, 0]))
    assert a['wl_hash'] != b['wl_hash']
    assert a['hydrogen_neighbor_atomic_numbers'] != b['hydrogen_neighbor_atomic_numbers']
    assert a['wl_hash'] != c['wl_hash']


def test_invalid_fragment_indices_fail():
    with pytest.raises(ValueError, match='Invalid fragment bond'):
        fragment_signature(block([6, 8], [[0], [2]]))


def test_equal_composition_never_certifies_identity_and_no_supercell_normalization():
    a = {'host_counts': {1: 2, 8: 1}}
    b = {'host_counts': {1: 4, 8: 2}}
    assert pair_status(a, a) == 'composition_matched_identity_unverified'
    assert pair_status(a, b) == 'framework_composition_conflict'
    assert pair_status(a, None) == 'incomplete'
