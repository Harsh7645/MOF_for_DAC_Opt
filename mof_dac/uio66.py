"""Provisional UiO-66 occupancy design; no coordinates or physical coefficients."""

import itertools
from collections import Counter


def enumerate_design(library):
    """Enumerate occupancy vectors [N,6], stoichiometry and pending interaction graph."""
    slots = library['slots']
    if len(slots) != 6 or len(set(slots)) != 6:
        raise ValueError('Six unique primitive-cell slots required')
    linkers = {row['id']: row for row in library['linkers']}
    if set(linkers) != {'BDC', 'NH2_BDC'}:
        raise ValueError('Expected BDC and NH2_BDC linker choices')
    budget = library['aminated_linker_budget']
    if not 0 <= budget['minimum'] <= budget['maximum'] <= 6:
        raise ValueError('Invalid amino-linker budget')
    configurations = []
    for state in itertools.product((0, 1), repeat=6):
        if not budget['minimum'] <= sum(state) <= budget['maximum']:
            continue
        counts = Counter(library['node']['composition'])
        charge = library['node']['formal_charge']
        for bit in state:
            linker = linkers['NH2_BDC' if bit else 'BDC']
            counts.update(linker['composition'])
            charge += linker['formal_charge']
        if charge != 0:
            raise ValueError('Provisional formal charge balance failed')
        configurations.append({'id': 'uio66_' + ''.join(map(str, state)),
            'state': list(state), 'amino_linker_count': sum(state),
            'composition': dict(sorted(counts.items())), 'formal_charge': charge,
            'structure_status': 'not assembled', 'split': 'unassigned until symmetry deduplication'})
    return {'status': 'provisional design enumeration; no material scores',
        'variable_graph': {'nodes': [{'id': slot, 'linear_coefficient_ev': None} for slot in slots],
            'edges': [{'source': left, 'target': right, 'pair_coefficient_ev': None,
                       'relation': 'candidate regression term; physical contact unknown'}
                      for left, right in itertools.combinations(slots, 2)]},
        'configurations': configurations,
        'nominal_configs': len(configurations), 'symmetry_unique_configs': None,
        'missing_coefficients_policy': 'reject optimization; null never means zero'}
