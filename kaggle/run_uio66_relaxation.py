"""Pinned UMA fixed-cell structural pilot; does not modify the ODAC25 benchmark."""

import argparse
import hashlib
import json
import sys
from importlib.metadata import version
from pathlib import Path

from mof_dac.relaxation import relax_fixed_cell


def main():
    import numpy as np
    import torch
    from ase.io import read
    from fairchem.core import FAIRChemCalculator

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--structures', required=True)
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--checkpoint-revision', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--ids', nargs='+')
    parser.add_argument('--steps', type=int, default=150)
    parser.add_argument('--fmax', type=float, default=0.05)
    parser.add_argument('--device', choices=['cuda', 'cpu'], default='cuda')
    args = parser.parse_args()
    directory, output = Path(args.structures), Path(args.output)
    if output.exists():
        raise ValueError('Output exists; choose a new run path to preserve evidence')
    manifest_path = directory / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    rows = {row['id']: row for row in manifest['configurations']}
    identifiers = args.ids or sorted(rows)
    if len(set(identifiers)) != len(identifiers) or not set(identifiers) <= set(rows):
        raise ValueError('Unknown or duplicate configuration ID')
    inputs = {}
    for identifier in identifiers:
        row = rows[identifier]
        path = directory / row['structure_file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != row['structure_sha256']:
            raise ValueError(f'Structure hash changed: {identifier}')
        inputs[identifier] = path
    np.random.seed(41)
    torch.manual_seed(41)
    checkpoint_hash = hashlib.sha256()
    checkpoint_md5 = hashlib.md5()
    with Path(args.checkpoint).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8*1024*1024), b''):
            checkpoint_hash.update(chunk)
            checkpoint_md5.update(chunk)
    if checkpoint_md5.hexdigest() != '3497615fd30a24c5b35cd3b41a682e6e':
        raise ValueError('Checkpoint does not match the official UMA-s-1.2.1 checksum')
    result = {'status': 'running; bare-structure preparation only',
        'protocol': 'UMA odac; fixed cell; all atom positions relaxed; LBFGS maxstep 0.1 Angstrom',
        'checkpoint_revision': args.checkpoint_revision, 'checkpoint_sha256': checkpoint_hash.hexdigest(),
        'checkpoint_md5': checkpoint_md5.hexdigest(),
        'model': 'uma-s-1p2p1', 'task': 'odac', 'inference_settings': 'batch',
        'seed': 41, 'steps': args.steps, 'fmax': args.fmax, 'device': args.device,
        'gpu': torch.cuda.get_device_name(0) if args.device == 'cuda' else None,
        'python': sys.version, 'packages': {name: version(name) for name in ['fairchem-core','torch','ase','numpy']},
        'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        'input_sha256': {key: rows[key]['structure_sha256'] for key in identifiers},
        'source_sha256': {name: hashlib.sha256(
            Path(__file__).resolve().parents[1].joinpath(name).read_bytes()).hexdigest()
            for name in ['mof_dac/relaxation.py', 'kaggle/run_uio66_relaxation.py']},
        'expected_ids': identifiers, 'results': []}
    output.parent.mkdir(parents=True, exist_ok=True)

    def save():
        output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')

    save()
    calculator = FAIRChemCalculator.from_model_checkpoint(args.checkpoint, task_name='odac',
        device=args.device, inference_settings='batch')
    for identifier in identifiers:
        try:
            evidence = relax_fixed_cell(read(inputs[identifier]), calculator,
                output.parent / 'structures', identifier, args.fmax, args.steps)
        except Exception as error:
            evidence = {'id': identifier, 'status': 'failed', 'error': f'{type(error).__name__}: {error}'}
        result['results'].append(evidence)
        save()
        print(identifier, evidence['status'], evidence.get('max_force_ev_per_angstrom'), flush=True)
    result['status'] = 'finished; bare-structure preparation only; no adsorption labels or h/J'
    save()


if __name__ == '__main__':
    main()
