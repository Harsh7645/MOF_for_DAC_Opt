#!/usr/bin/env python3
"""Offline integrity check only. Cannot launch QE, MPI, services or a probe."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'plans/qe75-rho750-pair-v1'

def main():
    pins = json.loads((PLAN / 'source-and-input-hashes.json').read_text())
    for relative, expected in pins.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f'Hash mismatch: {relative}')
    batch = json.loads((PLAN / 'batch.json').read_text())
    assert batch['execution_enabled'] is False and batch['execution_authorized'] is False
    paths = []
    for job in batch['jobs']:
        original = (ROOT / job['baseline_input']).read_bytes()
        candidate = (ROOT / job['input']).read_bytes()
        assert original.count(b'ecutrho=600') == candidate.count(b'ecutrho=750') == 1
        assert candidate.replace(b'ecutrho=750', b'ecutrho=600') == original
        assert hashlib.sha256(candidate).hexdigest() == job['input_sha256']
        paths.append(job['work_root'])
    assert len(paths) == len(set(paths)) == 2
    inv = json.loads((PLAN / 'inventory.json').read_text())
    records = inv['records']
    assert len(records) == 14
    assert sum(r['status'] == 'converged_80_600' for r in records) == 2
    assert sum(r['status'] == 'remaining' and r['kind'] == 'complex' for r in records) == 5
    assert sum(r['status'] == 'remaining' and r['kind'] == 'host' for r in records) == 7
    print(f'PASS: {len(pins)} source/input hashes; two cutoff-only inputs; 14-job inventory.')
    print('PREPARATION ONLY. Local 750-Ry execution NO-GO: unchanged 10/11-GiB guards.')
    print('No QE, MPI, initialization, controller or system mutation performed.')

if __name__ == '__main__':
    main()
