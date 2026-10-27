"""Bounded parent diagnostics; no identity certification, relabeling or fitting.

Replay selected records offline. Optional network access is restricted to the
two EPONEE single-CO2 entries in the already pinned mirror system index.
"""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import struct

import networkx as nx
import numpy as np

from mof_dac.surrogate_baseline import frozen_pairs
from scripts.audit_odac25_acquisition import FROZEN, ROOT, inspect, integer_vector
from scripts.inspect_odac25_mirror_sample import Inert, PassiveUnpickler, Ranges, REVISION, lookup

BASE = ROOT / 'local/odac25-acquisition-20261026'
FROZEN_SHA = '58c5dd5bec75366e3cd95dbd7ba9d714d1ff0163a560158cf154640aed5095bf'
SHARD_SHA = '2927f1ebb3af5fd4ea6e5d1072f9bdef549afa9e53ce3f0605955885da4b6c8c'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def array(value):
    """Decode a bounded numeric buffer, never execute a pickle constructor."""
    if not isinstance(value, Inert) or value.global_name not in (
            'numpy._core.multiarray._reconstruct', 'numpy.core.multiarray._reconstruct'):
        raise ValueError('Unsupported array class')
    version, shape, dtype, fortran, raw = value.state
    if (version != 1 or not 1 <= len(shape) <= 2 or
            any(type(n) is not int or n < 0 or n > 30000 for n in shape) or
            dtype.global_name != 'numpy.dtype' or dtype.args[0] not in ('i8', 'f8') or
            dtype.state[1] != '<' or type(fortran) is not bool):
        raise ValueError('Unsupported numeric layout')
    if len(raw) > 2*1024**2 or len(raw) != 8*int(np.prod(shape)):
        raise ValueError('Invalid buffer size')
    result = np.frombuffer(raw, dtype='<'+dtype.args[0]).reshape(shape, order='F' if fortran else 'C')
    if not np.isfinite(result).all():
        raise ValueError('Nonfinite numeric buffer')
    return result


def fragment_signature(block):
    """Index-invariant fragment diagnostic, NOT a periodic-parent identifier."""
    numbers = integer_vector(block['atomic_numbers'])
    charges, edges, orders = (array(block[k]) for k in ('formal_charges', 'bond_indices', 'bond_types'))
    if charges.shape != (len(numbers),) or edges.shape != (2, len(orders)):
        raise ValueError('Invalid fragment graph dimensions')
    graph = nx.Graph()
    for i, (z, charge) in enumerate(zip(numbers, charges)):
        graph.add_node(i, label=f'{z}:{int(charge)}')
    for (i, j), order in zip(edges.T, orders):
        i, j = int(i), int(j)
        if i == j or min(i, j) < 0 or max(i, j) >= len(numbers):
            raise ValueError('Invalid fragment bond')
        label = str(int(order))
        if graph.has_edge(i, j) and graph.edges[i, j]['label'] != label:
            raise ValueError('Conflicting fragment bond types')
        graph.add_edge(i, j, label=label)
    graph_hash = nx.weisfeiler_lehman_graph_hash(graph, node_attr='label', edge_attr='label', iterations=3)
    h_neighbors = Counter()
    for i, z in enumerate(numbers):
        if z == 1:
            h_neighbors[','.join(map(str, sorted(numbers[j] for j in graph.neighbors(i))))] += 1
    return {
        'role': block['block_type'], 'atoms': len(numbers), 'bonds': graph.number_of_edges(),
        'wl_hash': graph_hash, 'formal_charge': int(charges.sum()),
        'hydrogen_neighbor_atomic_numbers': dict(sorted(h_neighbors.items())),
    }


def structural_diagnostics(data):
    state = PassiveUnpickler(io.BytesIO(data)).load().state
    total_numbers = integer_vector(state['atomic_numbers'])
    fragments, roles, guest_indices, block_numbers = [], Counter(), [], []
    cursor = 0
    for item in state['blocks']:
        b = item.state
        numbers = integer_vector(b['atomic_numbers'])
        block_numbers.extend(numbers)
        roles[b['block_type']] += len(numbers)
        if b['block_type'] == 'ADSORBATE':
            guest_indices.extend(range(cursor, cursor+len(numbers)))
        else:
            fragments.append(fragment_signature(b))
        cursor += len(numbers)
    # The mirror reconstructs blocks and concatenates fragment atoms separately:
    # do not assume their atom ordering is interchangeable without checking.
    order_matches = tuple(block_numbers) == total_numbers
    cell = array(state['cell'])
    if cell.shape != (3, 3) or abs(np.linalg.det(cell)) < 1e-6:
        raise ValueError('Invalid cell')
    coords = array(state['original_cart_coords'])
    if coords.shape != (len(total_numbers), 3):
        raise ValueError('Invalid coordinate dimensions')
    tokens = sorted(json.dumps(f, sort_keys=True) for f in fragments)
    return {
        'info': state['info'], 'roles_atom_counts': dict(sorted(roles.items())),
        'block_order_matches_structure_atomic_numbers': order_matches,
        'host_fragment_signature_sha256': digest(json.dumps(tokens).encode()),
        'host_fragment_diagnostics': fragments,
        'cell_angstrom': cell.tolist(), 'cell_volume_angstrom3': abs(float(np.linalg.det(cell))),
        'supercell': state['info']['supercell'],
        'original_coordinate_buffer_sha256': digest(state['original_cart_coords'].state[-1]),
        'raw_official_tags_available': False,
        'authoritative_parent_state_id': None,
        'limitations': 'Fragment hashes omit interfragment periodic connectivity; inferred bonds/charges are mirror outputs. Coordinates are reordered and may be Niggli-reduced. No parent identity certification.',
    }


def all_test_keys(ranges):
    """Enumerate only the small observed two-level index, not record values."""
    meta = ranges.get(0, 8192)
    offset = max((0, 4096), key=lambda o: struct.unpack_from('<Q', meta, o+144)[0])
    if struct.unpack_from('<H', meta, offset+94)[0] != 2:
        raise ValueError('Unexpected index depth')
    root = ranges.get(struct.unpack_from('<Q', meta, offset+128)[0]*4096, 4096)
    keys = []
    for pointer in struct.unpack_from('<'+'H'*((struct.unpack_from('<H', root, 12)[0]-16)//2), root, 16):
        lo, hi, upper = struct.unpack_from('<HHH', root, pointer)
        page = ranges.get((lo | hi << 16 | upper << 32)*4096, 4096)
        if struct.unpack_from('<H', page, 10)[0] != 2:
            raise ValueError('Expected leaf')
        for pos in struct.unpack_from('<'+'H'*((struct.unpack_from('<H', page, 12)[0]-16)//2), page, 16):
            size = struct.unpack_from('<H', page, pos+6)[0]
            keys.append(page[pos+8:pos+8+size].decode('ascii'))
    if len(keys) != struct.unpack_from('<Q', meta, offset+120)[0] or keys != sorted(set(keys)):
        raise ValueError('Invalid ordered key inventory')
    return keys


def pair_status(co2, h2o):
    if co2 is None or h2o is None:
        return 'incomplete'
    return ('composition_matched_identity_unverified' if co2['host_counts'] == h2o['host_counts']
            else 'framework_composition_conflict')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fetch-eponee', action='store_true')
    args = parser.parse_args()
    if digest(FROZEN.read_bytes()) != FROZEN_SHA:
        raise ValueError('Frozen targets changed')
    args.output.mkdir(parents=True, exist_ok=False)
    ranges = Ranges('test', BASE/'ranges', offline=True, cap=32*1024**2)
    keys = all_test_keys(ranges)
    key_ordinals = {key: ordinal for ordinal, key in enumerate(keys)}
    system_path = BASE/'mirror_system_index.json'
    systems = json.loads(system_path.read_text())
    system_index = {(r['mof_id'], r['adsorbate_signature']): r['mirror_row_indices'] for r in systems}
    rows, records, errors = [], [], []
    for pair in frozen_pairs(FROZEN):
        selected = {}
        row = {'mof_id': pair['mof_id'], 'identity_verified': False,
               'source_release': 'ODAC25 filtered 20250918', 'source_split': 'val',
               'source_shard': 'val/mof_plus_adsorbate/part_00000.aselmdb',
               'source_shard_sha256': SHARD_SHA, 'mirror_revision': REVISION}
        for gas in ('co2', 'h2o'):
            p = pair[gas+'_provenance']
            for field in ('source_index', 'selected_trajectory', 'selected_fid', 'adsorption_energy_ev', 'trajectory_candidates'):
                row[gas+'_'+field] = p[field]
            key = str(p['source_index'])
            if key not in key_ordinals:
                selected[gas] = None
                errors.append({'mof_id': pair['mof_id'], 'gas': gas, 'key': key, 'reason': 'exact_key_absent_from_pinned_mirror'})
                continue
            signature = 'CO2:1_H2O:0_N2:0_O2:0' if gas == 'co2' else 'CO2:0_H2O:1_N2:0_O2:0'
            if key_ordinals[key] not in system_index[(pair['mof_id'], signature)]:
                raise ValueError('Mirror ordinal/source-key mapping mismatch')
            data, _ = lookup(ranges, key.encode())
            record = inspect(data, p)
            record['structural'] = structural_diagnostics(data)
            record['mirror_row_ordinal'] = key_ordinals[key]
            records.append(record)
            selected[gas] = record
            for field in ('host_counts', 'guest_counts', 'record_sha256'):
                row[gas+'_'+field] = record[field]
            for field in ('sid', 'supercell', 'energy_mof', 'energy_mof_old', 'energy_old', 'energy_ads', 'energy'):
                row[gas+'_'+field] = record['info'][field]
        co2, h2o = selected['co2'], selected['h2o']
        row['status'] = pair_status(co2, h2o)
        if co2 and h2o:
            a, b = co2['structural'], h2o['structural']
            row['host_delta_h2o_minus_co2'] = {str(z): h2o['host_counts'].get(z, 0)-co2['host_counts'].get(z, 0)
                for z in sorted(set(co2['host_counts']) | set(h2o['host_counts']))
                if h2o['host_counts'].get(z, 0) != co2['host_counts'].get(z, 0)}
            row['fragment_signatures_equal'] = a['host_fragment_signature_sha256'] == b['host_fragment_signature_sha256']
            row['cell_exact_equal'] = a['cell_angstrom'] == b['cell_angstrom']
            row['cell_volume_relative_difference'] = abs(b['cell_volume_angstrom3']/a['cell_volume_angstrom3']-1)
            row['supercell_equal'] = a['supercell'] == b['supercell']
            row['energy_mof_difference_h2o_minus_co2_ev'] = h2o['info']['energy_mof']-co2['info']['energy_mof']
        rows.append(row)
    extra = Ranges('test', BASE/'ranges', offline=not args.fetch_eponee, cap=2*1024**2)
    eponee = []
    for ordinal in system_index[('EPONEE', 'CO2:1_H2O:0_N2:0_O2:0')]:
        key = keys[ordinal]
        data, _ = lookup(extra, key.encode())
        s = structural_diagnostics(data)
        if s['info']['mof_name'] != 'EPONEE' or (s['info']['nco2'], s['info']['nh2o'], s['info']['nn2'], s['info']['no2']) != (1, 0, 0, 0):
            raise ValueError('EPONEE system index inconsistent')
        eponee.append({'source_index_key': key, 'mirror_row_ordinal': ordinal,
                       'record_sha256': digest(data), 'info': s['info'], 'substituted': False})
    counts = dict(Counter(r['status'] for r in rows))
    summary = {'version': 'parent-identity-v1', 'counts': counts, 'rows': len(rows),
        'selected_records': len(records), 'missing_selected': errors,
        'authoritatively_verified_pairs': 0, 'admitted_corrected_pairs': 0,
        'eponee_other_records': eponee, 'mirror_key_count': len(keys),
        'networkx_version': nx.__version__, 'numpy_version': np.__version__,
        'counted_cached_and_new_range_bytes': ranges.bytes_read+extra.bytes_read,
        'energy_reference_issue': 'separate_unresolved',
        'limitations': 'Same composition/fragment hashes/cell/reference energy do not establish parent state. No complete periodic connectivity or original tag verification.'}
    def write(name, obj):
        (args.output/name).write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    write('pair_status_v1.json', rows)
    fields = sorted(set().union(*(r.keys() for r in rows)))
    with (args.output/'pair_status_v1.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['mof_id', 'status']+[k for k in fields if k not in ('mof_id', 'status')])
        writer.writeheader()
        writer.writerows({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v for k, v in r.items()} for r in rows)
    (args.output/'selected_structure_diagnostics.jsonl').write_text(''.join(json.dumps(r, sort_keys=True)+'\n' for r in records), encoding='utf-8')
    write('summary.json', summary)
    write('range_receipts.json', {'url': ranges.url, 'ranges': ranges.receipts+extra.receipts})
    write('corrected_pool_proposal_v1.json', {
        'status': 'proposal_only_identity_and_compatibility_gates_pending',
        'historical_pool_sha256': FROZEN_SHA, 'historical_count': 138,
        'admitted_pairs': [], 'pending_identity_ids': [r['mof_id'] for r in rows if r['status']=='composition_matched_identity_unverified'],
        'excluded_current_selected_pair_ids': [r['mof_id'] for r in rows if r['status']=='framework_composition_conflict'],
        'incomplete_ids': [r['mof_id'] for r in rows if r['status']=='incomplete'],
        'policy': 'PAIRING_RULE.md', 'training_fitting_authorized': False})
    inputs = [FROZEN, system_path, BASE/'selected-audit-v3-offline/selected_records.jsonl',
              BASE/'atom_extract_blocks.py', BASE/'atom_extract_feats.py', BASE/'atom_lmdb_utils.py',
              Path(__file__), ROOT/'scripts/audit_odac25_acquisition.py', ROOT/'scripts/inspect_odac25_mirror_sample.py']
    write('receipt.json', {'input_sha256': {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in inputs},
                         'output_sha256': {p.name: digest(p.read_bytes()) for p in sorted(args.output.iterdir()) if p.is_file()}})
    print(json.dumps({k: summary[k] for k in ('counts', 'rows', 'selected_records', 'admitted_corrected_pairs')}))


if __name__ == '__main__':
    main()
