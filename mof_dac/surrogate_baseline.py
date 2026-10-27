"""Bounded, provenance-aware preparation for the frozen ODAC25 regression pool.

No download, inference or DFT. Cache compositions are candidates, not verified
structures. Training admission requires independently reviewed export provenance.
"""
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import numpy as np

from .material_baselines import composition_vector, evaluate_composition_baselines
from .odac25 import pair_adsorbate_rows

FROZEN_SHA256 = '58c5dd5bec75366e3cd95dbd7ba9d714d1ff0163a560158cf154640aed5095bf'
CONTRACT = {
    'target_field': 'energy_ads_corrected', 'units': 'eV',
    'reduction': 'exact_single_gas;max_fid_per_trajectory;min_final_corrected_per_mof_gas',
    'reference_convention': 'ODAC25_20250918_filtered_pre_kpoint_corrected_adsorption',
}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load_json(path, max_bytes=64 * 1024**2):
    path = Path(path)
    if path.stat().st_size > max_bytes:
        raise ValueError('JSON exceeds bounded input size')
    return json.loads(path.read_text(encoding='utf-8'))


def validate_pairs(payload, split):
    singles, pairs = payload['single_gas_targets'], payload['paired_targets']
    rebuilt = pair_adsorbate_rows(singles)
    if any(r['split'] != split for r in singles):
        raise ValueError('Official split differs')
    expected = {r['mof_id']: r for r in rebuilt}
    if len(pairs) != len(expected) or len({r['mof_id'] for r in pairs}) != len(pairs):
        raise ValueError('Pair IDs missing or duplicated')
    single_map = {(r['mof_id'], r['adsorbate']): r for r in singles}
    for row in pairs:
        if row['mof_id'] not in expected or any(row[k] != v for k, v in expected[row['mof_id']].items()):
            raise ValueError('Pair differs from selected single-gas labels')
        for gas in ('co2', 'h2o'):
            source = single_map[row['mof_id'], gas]
            if row[gas+'_provenance'] != source:
                raise ValueError('Pair provenance differs from selected record')
            if not source['selected_trajectory'] or any(
                    not isinstance(source[k], int) or source[k] < 0 for k in ('selected_fid', 'source_index')):
                raise ValueError('Explicit trajectory/frame/source index required')
    return sorted(pairs, key=lambda r: r['mof_id'])


def frozen_pairs(path):
    if digest(path) != FROZEN_SHA256:
        raise ValueError('Frozen evaluation table changed')
    rows = validate_pairs(load_json(path), 'val')
    if len(rows) != 138:
        raise ValueError('Frozen evaluation pool must contain all 138 MOFs')
    return rows


def cache_candidates(cache, ids):
    """Retain every cached composition; never choose by energy or first match."""
    by_id = defaultdict(list)
    for group in cache['groups']:
        if group['mof_id'] not in ids:
            continue
        for field, item in group['minima'].items():
            numbers = item['bare_atomic_numbers']
            composition_vector(numbers)  # Reject invalid atoms before integer conversion.
            counts = Counter(numbers)
            signature = sorted(counts) + [-1] + [counts[z] for z in sorted(counts)]
            if signature != group['signature']:
                raise ValueError('Cache signature does not match atomic numbers')
            fractions = tuple((z, str(Fraction(n, len(numbers)))) for z, n in sorted(counts.items()))
            by_id[group['mof_id']].append({
                'fractions': fractions, 'atomic_numbers': numbers,
                'bare_index': item['bare_index'], 'trajectory': item['bare_trajectory'],
                'fid': item['bare_fid'], 'field': field})
    output = []
    for ident in sorted(ids):
        entries = by_id[ident]
        unique = sorted(set(e['fractions'] for e in entries))
        status = 'missing' if not entries else ('ambiguous_composition' if len(unique) > 1 else 'cache_consistent_candidate')
        output.append({'mof_id': ident, 'status': status, 'verified_parent_structure': False,
                       'distinct_fraction_vectors': len(unique), 'cache_entries': len(entries),
                       'candidate_fractions': [list(x) for x in unique],
                       'features': composition_vector(entries[0]['atomic_numbers']).tolist() if len(unique) == 1 else None,
                       'source_records': [{k: v for k, v in e.items() if k not in ('fractions', 'atomic_numbers')} for e in entries]})
    return output


def read_parents(path, expected_ids, split, max_records=10000):
    """Read reviewed JSONL parent exports, with exact geometry and source binding.

    Each line binds a geometry JSON (numbers, positions_angstrom, cell_angstrom,
    metadata.mof_name) to its SHA256; canonical group and aliases come from a
    reviewed identity map, not a guessed refcode prefix or formula.
    """
    path = Path(path)
    rows = {}
    with path.open(encoding='utf-8') as stream:
        for index in range(max_records + 1):
            line = stream.readline(2 * 1024**2 + 1)
            if not line:
                break
            if len(line) > 2 * 1024**2 or index == max_records:
                raise ValueError('Parent export exceeds line/record cap')
            item = json.loads(line)
            ident = item['mof_id']
            if not ident or ident in rows or item['split'] != split:
                raise ValueError('Duplicate parent or incorrect official split')
            if not item['parent_group_id'] or not item['identity_review'] or not item['source_sha256']:
                raise ValueError('Reviewed identity/source provenance required')
            if len(item['source_sha256']) != 64 or not isinstance(item['source_index'], int) or item['source_index'] < 0:
                raise ValueError('Invalid source digest/index')
            aliases = item['aliases']
            if not isinstance(aliases, list) or any(not isinstance(a, str) or not a for a in aliases):
                raise ValueError('Explicit string aliases required')
            geometry_path = (path.parent / item['geometry_path']).resolve()
            if digest(geometry_path) != item['geometry_sha256']:
                raise ValueError('Parent geometry hash mismatch')
            geometry = load_json(geometry_path, max_bytes=2 * 1024**2)
            numbers = geometry['numbers']
            composition_vector(numbers)
            positions, cell = np.asarray(geometry['positions_angstrom'], float), np.asarray(geometry['cell_angstrom'], float)
            if positions.shape != (len(numbers), 3) or cell.shape != (3, 3) or not np.isfinite(positions).all() or not np.isfinite(cell).all() or abs(np.linalg.det(cell)) < 1e-8:
                raise ValueError('Invalid parent coordinates/cell')
            if geometry['metadata']['mof_name'] != ident:
                raise ValueError('Parent identity mismatch')
            # Exact stored geometry duplicate guard. Not a symmetry/translation equivalence proof.
            key = json.dumps([numbers, positions.tolist(), cell.tolist()], separators=(',', ':'))
            rows[ident] = {**item, 'bare_atomic_numbers': numbers,
                           'geometry_fingerprint': hashlib.sha256(key.encode()).hexdigest()}
    if set(rows) != set(expected_ids):
        raise ValueError('Parent coverage differs from complete label pool')
    return rows


def separation(train, evaluation):
    """Reject parent/alias/family/exact-geometry leakage; report feature collisions."""
    def keys(records, kind):
        if kind == 'aliases':
            return {name for r in records.values() for name in [r['mof_id'], *r['aliases']]}
        return {r[kind] for r in records.values()}
    for kind in ('aliases', 'parent_group_id', 'geometry_fingerprint'):
        overlap = keys(train, kind) & keys(evaluation, kind)
        if overlap:
            raise ValueError(f'Train/evaluation {kind} overlap: {sorted(overlap)[:3]}')
    # Duplicated geometries within train must share a fold, even under different IDs.
    groups_by_geometry = defaultdict(set)
    groups_by_alias = defaultdict(set)
    for row in train.values():
        groups_by_geometry[row['geometry_fingerprint']].add(row['parent_group_id'])
        for alias in [row['mof_id'], *row['aliases']]:
            groups_by_alias[alias].add(row['parent_group_id'])
    if any(len(groups) > 1 for groups in groups_by_geometry.values()):
        raise ValueError('Identical training geometry has inconsistent parent groups')
    if any(len(groups) > 1 for groups in groups_by_alias.values()):
        raise ValueError('Related training aliases have inconsistent parent groups')
    fractions = lambda r: tuple(composition_vector(r['bare_atomic_numbers']))
    collisions = len({fractions(r) for r in train.values()} & {fractions(r) for r in evaluation.values()})
    return {'parent_alias_group_exact_geometry_overlap': 0,
            'cross_pool_composition_collisions': collisions,
            'composition_collision_is_not_structure_identity': True,
            'symmetry_equivalent_duplicates': 'Require reviewed identity map; exact hash is insufficient'}


def run_baselines(training_path, training_parents, evaluation_path, evaluation_parents):
    """Admission gates precede training. All CV statistics use training groups only."""
    payload = load_json(training_path)
    if payload.get('contract') != CONTRACT or payload.get('complete_trajectories') is not True or not payload.get('provenance_review'):
        raise ValueError('Compatible reviewed corrected/final-frame training export required')
    train_rows = validate_pairs(payload, 'train')
    evaluation_rows = frozen_pairs(evaluation_path)
    train = read_parents(training_parents, [r['mof_id'] for r in train_rows], 'train')
    evaluation = read_parents(evaluation_parents, [r['mof_id'] for r in evaluation_rows], 'val')
    audit = separation(train, evaluation)
    for rows, parents in ((train_rows, train), (evaluation_rows, evaluation)):
        for row in rows:
            row['bare_atomic_numbers'] = parents[row['mof_id']]['bare_atomic_numbers']
    groups = [train[r['mof_id']]['parent_group_id'] for r in train_rows]
    result = evaluate_composition_baselines(train_rows, evaluation_rows, train_groups=groups)
    result['separation'] = audit
    result['cv_groups'] = dict(zip([r['mof_id'] for r in train_rows], groups))
    result['scope'] = 'Supervised frozen-field regression only; ODAC25 reference geometry/physical validation unresolved'
    result['input_hashes'] = {str(p): digest(p) for p in (training_path, training_parents, evaluation_path, evaluation_parents)}
    return result
