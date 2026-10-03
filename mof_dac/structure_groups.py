"""Conservative duplicate groups under declared parent-crystal operations."""

from collections import Counter
from itertools import combinations

import numpy as np


def _operation_error(left, right, rotation, translation, tolerance):
    """Maximum mapped distance [Angstrom], or None when typed matching fails."""
    from ase.geometry import find_mic
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import maximum_bipartite_matching

    transformed = left.get_scaled_positions() @ rotation.T + translation
    target = right.get_scaled_positions()
    maximum = 0.0
    # Rare elements first reject incompatible amino orientations cheaply.
    species = sorted(set(left.numbers), key=lambda z: np.count_nonzero(left.numbers == z))
    for z in species:
        a, b = transformed[left.numbers == z], target[right.numbers == z]
        delta = (a[:, None, :] - b[None, :, :]) @ left.cell.array
        _, lengths = find_mic(delta.reshape(-1, 3), left.cell, pbc=True)
        distances = lengths.reshape(len(a), len(b))
        matching = maximum_bipartite_matching(csr_matrix(distances <= tolerance), perm_type='column')
        if np.any(matching < 0):
            return None
        maximum = max(maximum, float(np.max(distances[np.arange(len(a)), matching])))
    return maximum


def parent_operation_groups(parent, structures, tolerance=0.01):
    """Group [id -> ASE Atoms] by verified parent-operation matches.

    Connected components keep every detected near-duplicate together for split
    safety. Approximate matching is not transitive: group diameter can exceed
    tolerance. This is not a complete crystallographic equivalence certificate.
    """
    import spglib

    if not np.isfinite(tolerance) or tolerance <= 0:
        raise ValueError('Positive finite distance tolerance required')
    if not structures or not np.all(parent.pbc):
        raise ValueError('Nonempty periodic structure collection required')
    normalized = {}
    metric = parent.cell.array @ parent.cell.array.T
    for key, atoms in structures.items():
        if not np.all(atoms.pbc) or not np.allclose(
                atoms.cell.array @ atoms.cell.array.T, metric, rtol=0, atol=1e-8):
            raise ValueError('Identical fixed periodic cells required')
        if not np.all(np.isfinite(atoms.positions)):
            raise ValueError('Nonfinite coordinates')
        # CIF roundtrips may rotate the Cartesian cell; compare in the parent's frame.
        normalized[key] = atoms.copy()
        normalized[key].set_cell(parent.cell, scale_atoms=True)
    structures = normalized
    symmetry = spglib.get_symmetry((parent.cell.array, parent.get_scaled_positions(), parent.numbers),
                                  symprec=tolerance)
    if symmetry is None:
        raise ValueError('Parent symmetry search failed')
    operations = [(r, t) for r, t in zip(symmetry['rotations'], symmetry['translations'])
                  if _operation_error(parent, parent, r, t, tolerance) is not None]
    if not operations:
        raise ValueError('No verified parent operations')
    links, representatives = [], {key: key for key in structures}

    def root(key):
        while representatives[key] != key:
            representatives[key] = representatives[representatives[key]]
            key = representatives[key]
        return key

    for left, right in combinations(sorted(structures), 2):
        a, b = structures[left], structures[right]
        if Counter(a.numbers) != Counter(b.numbers):
            continue
        for index, (rotation, translation) in enumerate(operations):
            error = _operation_error(a, b, rotation, translation, tolerance)
            if error is not None:
                links.append({'source': left, 'target': right, 'operation_index': index,
                              'max_mapped_distance_angstrom': error})
                x, y = root(left), root(right)
                representatives[max(x, y)] = min(x, y)
                break
    groups = {}
    for key in sorted(structures):
        groups.setdefault(root(key), []).append(key)
    return {'status': 'parent-operation duplicate groups; provisional crystallographic diagnostic',
        'tolerance_angstrom': tolerance, 'spglib_version': spglib.__version__,
        'parent_operations_found': len(symmetry['rotations']), 'verified_parent_operations': len(operations),
        'nominal_structures': len(structures), 'groups': list(groups.values()), 'group_count': len(groups),
        'verified_match_graph': links,
        'limitations': ['Approximate connected groups need not be pairwise within tolerance',
                       'No transformations outside detected parent operations tested',
                       'Relaxation can change symmetry; regroup before fitting or evaluation']}
