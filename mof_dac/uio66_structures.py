"""Provisional periodic atom mapping and amino substitutions; requires ASE."""

from collections import Counter, defaultdict

import numpy as np


def map_linkers(atoms):
    """Infer six finite BDC graphs in one C48H28O32Zr6 cell; retain image shifts.

    Distance cutoffs are a topology hypothesis, not a chemical bond certificate.
    Atom indices belong to this exact ordered parent structure.
    """
    from ase.neighborlist import neighbor_list

    if Counter(atoms.get_chemical_symbols()) != Counter(C=48, H=28, O=32, Zr=6):
        raise ValueError('Expected one ideal hydroxylated UiO-66 primitive composition')
    if not np.all(atoms.pbc) or abs(np.linalg.det(atoms.cell.array)) < 1:
        raise ValueError('Nondegenerate fully periodic cell required')
    if not np.all(np.isfinite(atoms.positions)):
        raise ValueError('Nonfinite coordinates')
    # Only C-C, C-H and C-O bonds connect the organic molecules.
    left, right, shifts = neighbor_list('ijS', atoms,
        {('C', 'C'): 1.75, ('C', 'H'): 1.3, ('C', 'O'): 1.65})
    adjacency = defaultdict(list)
    for i, j, shift in zip(left, right, shifts):
        adjacency[int(i)].append((int(j), shift))
    unseen = set(np.flatnonzero(atoms.numbers == 6).tolist())
    slots, organic = [], set()
    while unseen:
        seed = min(unseen)
        images, pending = {seed: np.zeros(3, dtype=int)}, [seed]
        while pending:
            i = pending.pop()
            for j, shift in adjacency[i]:
                image = images[i] + shift
                if j in images:
                    if not np.array_equal(images[j], image):
                        raise ValueError('Organic component winds through the periodic cell')
                else:
                    images[j] = image
                    pending.append(j)
        ids = sorted(images)
        if Counter(atoms[ids].get_chemical_symbols()) != Counter(C=8, H=4, O=4):
            raise ValueError('Inferred component is not a complete BDC linker')
        if organic.intersection(ids):
            raise ValueError('Overlapping linker components')
        organic.update(ids)
        unseen.difference_update(ids)
        hydrogen = min(i for i in ids if atoms.numbers[i] == 1)
        if len(adjacency[hydrogen]) != 1:
            raise ValueError('Substitution H must have one inferred carbon neighbor')
        carbon = adjacency[hydrogen][0][0]
        ring_neighbors = sorted(j for j, _ in adjacency[carbon] if atoms.numbers[j] == 6)
        if len(ring_neighbors) != 2:
            raise ValueError('Substitution carbon must have two ring-carbon neighbors')
        slots.append({'id': f'L{len(slots)}', 'atom_indices': ids,
            'image_shifts': {str(i): images[i].tolist() for i in ids},
            'substitution_hydrogen': hydrogen, 'substitution_carbon': carbon,
            'ring_neighbors': ring_neighbors})
    node = sorted(set(range(len(atoms))) - organic)
    if len(slots) != 6 or Counter(atoms[node].get_chemical_symbols()) != Counter(Zr=6, O=8, H=4):
        raise ValueError('Expected six BDC linkers plus the hydroxylated Zr6 node')
    return {'status': 'distance-inferred mapping; chemistry review pending',
        'bond_cutoffs_angstrom': {'C-C': 1.75, 'C-H': 1.3, 'C-O': 1.65},
        'orientation_policy': 'lowest parent H atom index per linker; planar NH2 initial guess',
        'slots': slots, 'node_atom_indices': node}


def substitute_amino(parent, mapping, state):
    """Return an unrelaxed [N_parent + 2*sum(state),3] coordinate proposal.

    Replace each selected ring H by N, add two H. Fixed C-N/N-H lengths
    (1.39/1.01 Angstrom) and planar angles are initialization assumptions.
    """
    from ase import Atom
    from ase.neighborlist import neighbor_list

    if len(state) != 6 or any(bit not in (0, 1) for bit in state):
        raise ValueError('Six binary substitution bits required')
    atoms = parent.copy()
    atoms.calc = None
    for bit, slot in zip(state, mapping['slots']):
        if not bit:
            continue
        shifts = slot['image_shifts']
        position = lambda i: parent.positions[i] + np.array(shifts[str(i)]) @ parent.cell.array
        h, c = slot['substitution_hydrogen'], slot['substitution_carbon']
        outward = position(h) - position(c)
        outward /= np.linalg.norm(outward)
        tangent = position(slot['ring_neighbors'][0]) - position(c)
        tangent -= np.dot(tangent, outward) * outward
        tangent /= np.linalg.norm(tangent)
        nitrogen = position(c) + 1.39 * outward
        atoms.numbers[h], atoms.positions[h] = 7, nitrogen
        for sign in (-1, 1):
            atoms.append(Atom('H', nitrogen + 1.01 * (0.5 * outward + sign * np.sqrt(0.75) * tangent)))
    atoms.wrap()
    k = sum(state)
    expected = Counter(C=48, H=28 + k, O=32, Zr=6)
    if k:
        expected['N'] = k
    if Counter(atoms.get_chemical_symbols()) != expected or not np.all(np.isfinite(atoms.positions)):
        raise ValueError('Substitution composition/coordinate check failed')
    distances = neighbor_list('d', atoms, 0.7)
    if len(distances):
        raise ValueError('Severe periodic contact below 0.7 Angstrom; proposal rejected')
    return atoms
