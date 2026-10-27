"""Inspect only the 276 frozen selected mirror records, bounded to 32 MiB.

Default offline replay. --fetch-selected permits exact HTTP range reads; no
archive download, target edits, parent choice or fitting. Retains every failure.
"""
import argparse
from collections import Counter
from fractions import Fraction
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import math
from pathlib import Path
import struct

from mof_dac.surrogate_baseline import frozen_pairs, load_json
from scripts.inspect_odac25_mirror_sample import Inert, PassiveUnpickler, Ranges, lookup

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT/'artifacts/kaggle/odac25_paired_targets_2026-09-14/paired_targets.json'
CACHE = ROOT/'artifacts/kaggle/odac25_reference_audit_2026-10-02/reference_lookup/phase3_material_base_audited.bare_cache.json'


def integer_vector(value):
    """Decode only observed fixed-size integer buffers; no numpy constructor."""
    if not isinstance(value, Inert) or value.global_name not in ('numpy._core.multiarray._reconstruct', 'numpy.core.multiarray._reconstruct'):
        raise ValueError('Unsupported array representation')
    version, shape, dtype, fortran, raw = value.state
    if version != 1 or len(shape) != 1 or not 0 < shape[0] <= 10000 or dtype.global_name != 'numpy.dtype' or dtype.args[0] != 'i8' or dtype.state[1] != '<' or len(raw) != 8*shape[0]:
        raise ValueError('Unsupported integer vector layout')
    values = struct.unpack('<'+'q'*shape[0], raw)
    if any(z < 1 or z > 118 for z in values):
        raise ValueError('Invalid atomic numbers')
    return values


def inspect(data, selected):
    obj = PassiveUnpickler(io.BytesIO(data)).load()
    if obj.global_name != 'src.data.types.MOFStructure':
        raise ValueError('Unexpected mirror record class')
    state, info = obj.state, obj.state['info']
    if not all(math.isfinite(info[k]) for k in ('energy', 'energy_old', 'energy_mof', 'energy_mof_old', 'energy_ads', 'energy_ads_corrected')):
        raise ValueError('Nonfinite metadata energy')
    if (info['mof_name'], info['name'], info['fid']) != (
            selected['mof_id'], selected['selected_trajectory'], selected['selected_fid']):
        raise ValueError('Frozen identity/trajectory/frame mismatch')
    if abs(info['energy_ads_corrected']-selected['adsorption_energy_ev']) > 1e-10:
        raise ValueError('Frozen corrected energy mismatch')
    gas = selected['adsorbate']
    expected_counts = (1, 0, 0, 0) if gas == 'co2' else (0, 1, 0, 0)
    if tuple(info[k] for k in ('nco2', 'nh2o', 'nn2', 'no2')) != expected_counts or info['nads'] != 1:
        raise ValueError('Frozen single-gas count mismatch')
    total = Counter(integer_vector(state['atomic_numbers']))
    host, guest = Counter(), Counter()
    for block in state['blocks']:
        role = block.state['block_type']
        if role not in ('ADSORBATE', 'LINKER', 'NODE', 'SOLVENT'):
            raise ValueError('Unrecognized mirror block type: '+str(role))
        (guest if role == 'ADSORBATE' else host).update(integer_vector(block.state['atomic_numbers']))
    if host+guest != total or not host:
        raise ValueError('Block partition does not conserve atoms')
    if guest != Counter([6, 8, 8] if gas == 'co2' else [1, 1, 8]):
        raise ValueError('Guest-block composition differs from gas metadata')
    offset = info['energy_old']-info['energy_mof']-info['energy_ads_corrected']
    expected_offset = -22.990396 if gas == 'co2' else -14.236396
    if abs(offset-expected_offset) > 1e-8:
        raise ValueError('Reference-field identity differs')
    return {'mof_id': info['mof_name'], 'gas': gas, 'source_index_key': selected['source_index'],
            'selected_metadata_match': True, 'record_sha256': hashlib.sha256(data).hexdigest(),
            'info': info, 'host_counts': dict(sorted(host.items())), 'guest_counts': dict(sorted(guest.items())),
            'gas_offset_ev': offset,
            'parent_evidence': 'Mirror block partition traced to original tag==0 preprocessing; raw official tags not downloaded'}


def fractions(counts):
    total = sum(counts.values())
    return tuple((int(z), str(Fraction(n, total))) for z, n in sorted(counts.items(), key=lambda p: int(p[0])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fetch-selected', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    pairs = frozen_pairs(FROZEN)
    ranges = Ranges('test', args.cache, offline=not args.fetch_selected, cap=32*1024**2)
    records, failures = [], []
    # Precache the observed two-level byte-key B-tree before parallel value reads.
    # Each selected key has a distinct overflow range; no concurrent cache writers
    # touch the same file. The shared range-byte budget is reserved under a lock.
    meta = ranges.get(0, 8192)
    offset = max((0, 4096), key=lambda o: struct.unpack_from('<Q', meta, o+144)[0])
    depth = struct.unpack_from('<H', meta, offset+94)[0]
    if depth != 2:
        raise ValueError('Only observed two-level test DB supported')
    root = ranges.get(struct.unpack_from('<Q', meta, offset+128)[0]*4096, 4096)
    lower = struct.unpack_from('<H', root, 12)[0]
    for pointer in struct.unpack_from('<'+'H'*((lower-16)//2), root, 16):
        lo, hi, upper = struct.unpack_from('<HHH', root, pointer)
        ranges.get((lo | hi << 16 | upper << 32)*4096, 4096)

    def task(selected):
        try:
            data, entries = lookup(ranges, str(selected['source_index']).encode())
            return inspect(data, selected), None
        except Exception as error:
            return None, {'mof_id': selected['mof_id'], 'gas': selected['adsorbate'],
                          'source_index': selected['source_index'], 'error': type(error).__name__+': '+str(error)}

    selected_rows = [pair[gas+'_provenance'] for pair in pairs for gas in ('co2', 'h2o')]
    if len({r['source_index'] for r in selected_rows}) != len(selected_rows):
        raise ValueError('Selected source keys must be unique')
    with ThreadPoolExecutor(max_workers=4) as pool:
        for row, failure in pool.map(task, selected_rows):
            if row is not None:
                records.append(row)
                with (args.output/'selected_records.jsonl').open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(row, allow_nan=False)+'\n')
            else:
                failures.append(failure)
                with (args.output/'failures.jsonl').open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(failure)+'\n')
            if (len(records)+len(failures)) % 20 == 0:
                print(f'processed={len(records)+len(failures)}/276 passed={len(records)} failed={len(failures)}', flush=True)
    cached = {}
    for group in load_json(CACHE)['groups']:
        signature = group['signature']; split = signature.index(-1)
        counts = dict(zip(signature[:split], signature[split+1:]))
        cached.setdefault(group['mof_id'], set()).add(fractions(counts))
    found = {(r['mof_id'], r['gas']): r for r in records}
    comparison = []
    for pair in pairs:
        ident = pair['mof_id']; rows = [found.get((ident, gas)) for gas in ('co2', 'h2o')]
        row = {'mof_id': ident, 'prior_distinct_cache_compositions': len(cached[ident])}
        if any(r is None for r in rows):
            row['status'] = 'selected_records_incomplete'
        else:
            vectors = [fractions(r['host_counts']) for r in rows]
            row.update({'status': 'same_selected_host_composition' if vectors[0] == vectors[1] else 'different_selected_host_compositions',
                        'both_match_cached_candidates': all(v in cached[ident] for v in vectors),
                        'co2_host_counts': rows[0]['host_counts'], 'h2o_host_counts': rows[1]['host_counts']})
        comparison.append(row)
    report = {'frozen_target_sha256': hashlib.sha256(FROZEN.read_bytes()).hexdigest(),
              'records_verified': len(records), 'failures': failures, 'pair_audit': comparison,
              'counts': dict(Counter(r['status'] for r in comparison)),
              'range_budget_bytes': ranges.cap, 'range_bytes_including_cache_reuse': ranges.bytes_read,
              'ranges': ranges.receipts, 'full_database_hash_verified': False,
              'source_url': ranges.url, 'no_target_edits_or_model_fitting': True}
    (args.output/'assessment.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('records_verified', 'counts', 'range_bytes_including_cache_reuse')}))


if __name__ == '__main__':
    main()
