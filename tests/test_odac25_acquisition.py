"""Offline synthetic tests for the bounded metadata investigator; no training."""
import io
import pickle
import struct
from pathlib import Path

import numpy as np
import pytest

from scripts import inspect_odac25_mirror_sample as sample
from scripts.audit_odac25_acquisition import integer_vector
from scripts import audit_odac25_acquisition as audit


def test_pickle_callables_are_inert(tmp_path):
    target = tmp_path/'must-not-exist'
    class Payload:
        def __reduce__(self):
            return eval, (f"open({str(target)!r}, 'w').write('executed')",)
    result = sample.PassiveUnpickler(io.BytesIO(pickle.dumps(Payload()))).load()
    assert isinstance(result, sample.Inert)
    assert not target.exists()


def test_integer_buffer_is_decoded_without_numpy_constructor():
    data = pickle.dumps(np.array([1, 6, 8], dtype='<i8'), protocol=4)
    inert = sample.PassiveUnpickler(io.BytesIO(data)).load()
    assert integer_vector(inert) == (1, 6, 8)
    invalid = sample.PassiveUnpickler(io.BytesIO(pickle.dumps(np.array([0], dtype='<i8'), protocol=4))).load()
    with pytest.raises(ValueError, match='Invalid atomic'):
        integer_vector(invalid)


def test_range_budget_and_ignored_range_never_read_body(tmp_path, monkeypatch):
    reader = sample.Ranges('test', tmp_path, cap=16)
    with pytest.raises(ValueError, match='budget'):
        reader.get(0, 17)
    class Response:
        status = 200
        headers = {}
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, *args): raise AssertionError('Must not read ignored-range body')
    monkeypatch.setattr(sample, 'urlopen', lambda *a, **kw: Response())
    with pytest.raises(ValueError, match='Range not honored'):
        reader.get(0, 8)


def test_exact_key_lookup_and_missing_key():
    meta = bytearray(8192)
    for offset in (0, 4096):
        struct.pack_into('<II', meta, offset+16, 0xBEEFC0DE, 1)
        struct.pack_into('<IHHQQQQQ', meta, offset+88, 0, 0, 1, 0, 1, 0, 1, 2)
    struct.pack_into('<Q', meta, 4096+144, 1)
    leaf = bytearray(4096)
    struct.pack_into('<QHHHH', leaf, 0, 2, 0, 2, 18, 4000)
    struct.pack_into('<H', leaf, 16, 4000)
    struct.pack_into('<HHHH', leaf, 4000, 5, 0, 0, 3)
    leaf[4008:4016] = b'101hello'
    class Fixture:
        def get(self, start, size):
            return bytes(meta) if start == 0 else bytes(leaf)
    assert sample.lookup(Fixture(), b'101') == (b'hello', 1)
    with pytest.raises(ValueError, match='exact LMDB key missing'):
        sample.lookup(Fixture(), b'102')


def test_nonfinite_reference_metadata_rejected(monkeypatch):
    from types import SimpleNamespace
    info = dict.fromkeys(('energy', 'energy_old', 'energy_mof', 'energy_mof_old', 'energy_ads', 'energy_ads_corrected'), 0.)
    info['energy_mof'] = float('nan')
    obj = SimpleNamespace(global_name='src.data.types.MOFStructure', state={'info': info})
    monkeypatch.setattr(audit, 'PassiveUnpickler', lambda _: SimpleNamespace(load=lambda: obj))
    with pytest.raises(ValueError, match='Nonfinite metadata'):
        audit.inspect(b'', {})
