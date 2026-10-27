"""Bounded read-only LMDB range inspection; no model/data fitting.

Only supports the observed little-endian, 64-bit LMDB layout, 4096-byte pages,
ordinary byte keys and overflow values. Fails on other layouts. Pickle globals
become inert placeholders: no imported dataset classes or pickle-callable code.
Each HTTP range must be honored exactly. Cache enables offline replay.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import pickle
import struct
import threading
from urllib.request import Request, urlopen

REVISION = '81a85299823a7e75e0ed7fe39640c99297906080'
SIZES = {'test': 141197312, 'train': 6547623936}


class Inert:
    def __new__(cls, *args, **kwargs):
        value = object.__new__(cls)
        value.args = args
        return value

    def __init__(self, *args, **kwargs):
        self.args = args

    def __setstate__(self, state):
        self.state = state


class PassiveUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        # Even numpy constructors are not executed. Keep their bytes/state only.
        return type('InertGlobal', (Inert,), {'global_name': module+'.'+name})

    def persistent_load(self, pid):
        raise ValueError('Persistent pickle references unsupported')


def plain(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, bytes):
        return {'bytes': len(value), 'sha256': hashlib.sha256(value).hexdigest()}
    if isinstance(value, type) and issubclass(value, Inert):
        return {'inert_type': value.global_name}
    if isinstance(value, Inert):
        return {'inert_global': value.global_name, 'args': plain(value.args),
                'state': plain(getattr(value, 'state', None))}
    raise ValueError('Unsupported passive value')


class Ranges:
    def __init__(self, split, output, offline=False, cap=2*1024**2):
        self.split, self.output, self.offline, self.cap = split, output, offline, cap
        self.bytes_read, self.receipts = 0, []
        self.lock = threading.Lock()
        self.output.mkdir(parents=True, exist_ok=True)
        self.url = f'https://huggingface.co/datasets/nayoung10/AtomMOF-data/resolve/{REVISION}/odac25/odac25_{split}.lmdb'

    def get(self, start, size):
        with self.lock:
            if start < 0 or size <= 0 or start+size > SIZES[self.split] or self.bytes_read+size > self.cap:
                raise ValueError('Range budget/bounds exceeded')
            self.bytes_read += size
        path = self.output/f'{self.split}_{start}_{size}.bin'
        if path.exists():
            data = path.read_bytes()
        else:
            if self.offline:
                raise ValueError('Missing cached range')
            end = start+size-1
            # Query distinguishes ranges for HTTP caches that ignore Vary: Range.
            request = Request(self.url+f'?range_start={start}', headers={
                'Range': f'bytes={start}-{end}', 'Accept-Encoding': 'identity'})
            with urlopen(request, timeout=25) as response:
                if response.status != 206 or response.headers.get('Content-Range') != f'bytes {start}-{end}/{SIZES[self.split]}':
                    raise ValueError('Range not honored; body not read')
                data = response.read(size+1)
            if len(data) != size:
                raise ValueError('Range length mismatch')
            path.write_bytes(data)
        if len(data) != size:
            raise ValueError('Cached range length mismatch')
        with self.lock:
            self.receipts.append({'file': path.name, 'start': start, 'bytes': size,
                                  'sha256': hashlib.sha256(data).hexdigest()})
        return data


def lookup(ranges, key):
    meta = ranges.get(0, 8192)
    candidates = []
    for offset in (0, 4096):
        if struct.unpack_from('<II', meta, offset+16) != (0xBEEFC0DE, 1):
            raise ValueError('Unsupported LMDB metadata')
        db = struct.unpack_from('<IHHQQQQQ', meta, offset+88)
        candidates.append((struct.unpack_from('<Q', meta, offset+144)[0], db))
    _, db = max(candidates)
    page_number = db[-1]
    for _ in range(8):
        page = ranges.get(page_number*4096, 4096)
        pgno, _, flags, lower, upper = struct.unpack_from('<QHHHH', page)
        if pgno != page_number or lower < 16 or lower > upper or upper > 4096:
            raise ValueError('Invalid LMDB page')
        pointers = struct.unpack_from('<'+'H'*((lower-16)//2), page, 16)
        nodes = []
        for pointer in pointers:
            lo, hi, node_flags, key_size = struct.unpack_from('<HHHH', page, pointer)
            node_key = page[pointer+8:pointer+8+key_size]
            nodes.append((node_key, pointer, lo, hi, node_flags, key_size))
        if flags == 1:  # Branch: last lower bound <= requested byte key.
            node = [n for n in nodes if n[0] <= key][-1]
            page_number = node[2] | (node[3] << 16) | (node[4] << 32)
            continue
        if flags != 2:
            raise ValueError('Unsupported LMDB page type')
        matches = [n for n in nodes if n[0] == key]
        if len(matches) != 1:
            raise ValueError('Requested exact LMDB key missing')
        _, pointer, lo, hi, node_flags, key_size = matches[0]
        size, offset = lo | hi << 16, pointer+8+key_size
        if size > 512*1024:
            raise ValueError('Record exceeds sample cap')
        if node_flags == 1:
            overflow = struct.unpack_from('<Q', page, offset)[0]
            data = ranges.get(overflow*4096, size+16)
            if struct.unpack_from('<Q', data)[0] != overflow or struct.unpack_from('<H', data, 10)[0] != 4:
                raise ValueError('Invalid overflow page')
            return data[16:], db[-2]
        if node_flags == 0 and offset+size <= 4096:
            return page[offset:offset+size], db[-2]
        raise ValueError('Unsupported LMDB leaf value')
    raise ValueError('Exceeded tree depth bound')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--split', choices=SIZES, required=True)
    parser.add_argument('--keys', nargs='+', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    if len(args.keys) > 8:
        raise ValueError('At most eight sample keys')
    ranges = Ranges(args.split, args.output, args.offline)
    result = []
    for key in args.keys:
        data, count = lookup(ranges, key.encode('ascii'))
        (args.output/f'{args.split}_key_{int(key)}.pickle').write_bytes(data)
        state = plain(PassiveUnpickler(io.BytesIO(data)).load())
        result.append({'key': key, 'database_entries': count, 'record_sha256': hashlib.sha256(data).hexdigest(), 'passive_state': state})
    payload = {'url': ranges.url, 'revision': REVISION, 'sample_only': True,
               'full_LFS_hash_verified': False, 'requested_bytes_including_cached_reuse': ranges.bytes_read,
               'ranges': ranges.receipts, 'records': result}
    (args.output/f'{args.split}_sample.json').write_text(json.dumps(payload, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'split': args.split, 'keys': args.keys, 'database_entries': count,
                      'bounded_bytes': ranges.bytes_read, 'sample_only': True}))


if __name__ == '__main__':
    main()
