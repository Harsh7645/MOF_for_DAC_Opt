"""Paired UMA-only design experiment; independent of frozen ODAC25 validation."""

import argparse
import hashlib
import json
import sys
from importlib.metadata import version
from pathlib import Path

from mof_dac.adsorption import evaluate_candidate, gas_geometry, intact
from mof_dac.relaxation import relax_fixed_cell


def main():
    import numpy as np
    import torch
    from ase.io import read
    from fairchem.core import FAIRChemCalculator

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bare-reports', nargs='+', required=True)
    parser.add_argument('--checkpoint', required=True)
    parser.add_argument('--checkpoint-revision', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--ids', nargs='+')
    parser.add_argument('--starts', type=int, default=4)
    parser.add_argument('--steps', type=int, default=200)
    parser.add_argument('--fmax', type=float, default=0.05)
    args = parser.parse_args()
    if args.starts < 1 or args.steps < 0 or not np.isfinite(args.fmax) or args.fmax <= 0:
        raise ValueError('Invalid calculation budget')
    output = Path(args.output)
    if output.exists():
        raise ValueError('Choose a new output path; preserve old evidence')
    inputs, reports = {}, {}
    checkpoint_sha, checkpoint_md5 = hashlib.sha256(), hashlib.md5()
    with Path(args.checkpoint).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8*1024*1024), b''):
            checkpoint_sha.update(chunk)
            checkpoint_md5.update(chunk)
    if checkpoint_md5.hexdigest() != '3497615fd30a24c5b35cd3b41a682e6e':
        raise ValueError('Wrong UMA-s-1p2p1 checkpoint')
    for path in map(Path, args.bare_reports):
        payload = json.loads(path.read_text())
        if payload['checkpoint_sha256'] != checkpoint_sha.hexdigest():
            raise ValueError('Bare run and adsorption checkpoint differ')
        reports[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        for row in payload['results']:
            if row['id'] in inputs or not intact(row):
                raise ValueError('Duplicate or unaccepted bare structure')
            structure = path.parent / 'structures' / row['final_structure_file']
            if hashlib.sha256(structure.read_bytes()).hexdigest() != row['final_structure_sha256']:
                raise ValueError('Bare structure hash changed')
            inputs[row['id']] = (structure, row['final_structure_sha256'])
    identifiers = args.ids or sorted(inputs)
    if len(set(identifiers)) != len(identifiers) or not set(identifiers) <= set(inputs):
        raise ValueError('Unknown or duplicate configuration ID')
    np.random.seed(41)
    torch.set_num_threads(1)
    torch.manual_seed(41)
    result = {'status': 'running', 'protocol': 'uio66_uma_paired_flexible_v1',
        'scope': 'provisional UMA-only sampled adsorption; not DFT or the ODAC25 benchmark',
        'model': 'uma-s-1p2p1', 'task': 'odac', 'checkpoint_revision': args.checkpoint_revision,
        'checkpoint_sha256': checkpoint_sha.hexdigest(), 'checkpoint_md5': checkpoint_md5.hexdigest(),
        'source_sha256': {name: hashlib.sha256(Path(__file__).resolve().parents[1].joinpath(name).read_bytes()).hexdigest()
            for name in ['mof_dac/adsorption.py', 'mof_dac/relaxation.py', 'kaggle/run_uio66_adsorption.py']},
        'bare_report_sha256': reports, 'input_sha256': {k: inputs[k][1] for k in identifiers},
        'seed': 41, 'starts_per_gas': args.starts, 'step_budget': args.steps, 'fmax': args.fmax,
        'placement': 'uniform fractional centers; uniform SO(3); 2-Angstrom host/guest clearance; bounded rejection',
        'reference': 'lowest accepted sampled empty MOF after both gas desorption relaxations; isolated gas task odac',
        'python': sys.version, 'packages': {k: version(k) for k in ['fairchem-core', 'torch', 'ase', 'numpy', 'scipy']},
        'gpu': torch.cuda.get_device_name(0), 'torch_cpu_threads': torch.get_num_threads(),
        'expected_ids': identifiers,
        'gas_references': {}, 'results': [], 'active_candidate': None}
    output.parent.mkdir(parents=True, exist_ok=True)

    def save():
        temporary = output.with_suffix('.tmp')
        temporary.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
        temporary.replace(output)

    save()
    calculator = FAIRChemCalculator.from_model_checkpoint(args.checkpoint, task_name='odac',
        device='cuda', inference_settings='batch')
    gases = {}
    for name in ('CO2', 'H2O'):
        evidence = relax_fixed_cell(gas_geometry(name), calculator, output.parent / 'structures',
                                    'isolated_' + name, args.fmax, args.steps)
        result['gas_references'][name] = evidence
        save()
        if not intact(evidence):
            raise ValueError('Isolated gas failed convergence/connectivity checks')
        gases[name] = read(output.parent / 'structures' / evidence['trajectory_file'], index=-1)
        gases[name].calc = None
        print('isolated', name, evidence['final_energy_ev'], evidence['status'], flush=True)
    for identifier in identifiers:
        def save_start(bare, starts):
            result['active_candidate'] = {'id': identifier, 'bare': bare, 'starts': starts}
            save()
            last = starts[-1]
            print(identifier, last['gas'], last['start'], last['status'], flush=True)
        try:
            row = evaluate_candidate(read(inputs[identifier][0]), calculator, gases,
                result['gas_references'], output.parent / 'structures', identifier,
                args.starts, 41, args.fmax, args.steps, save_start)
        except Exception as error:
            row = {'id': identifier, 'status': 'failed', 'error': f'{type(error).__name__}: {error}',
                   'paired_target_ev': None, 'partial': result['active_candidate']}
        result['results'].append(row)
        result['active_candidate'] = None
        save()
        print(identifier, row['status'], row['paired_target_ev'], flush=True)
    result['status'] = 'finished; provisional sampled model energies only'
    result['peak_gpu_allocated_bytes'] = torch.cuda.max_memory_allocated()
    save()


if __name__ == '__main__':
    main()
