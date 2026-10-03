"""CPU solver comparison on a provisional trained UMA quadratic approximation."""

import argparse
import hashlib
import json
import platform
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np

from mof_dac.data import load_instance
from mof_dac.gurobi import solve_gurobi
from mof_dac.optimizers import exact, simulated_annealing
from mof_dac.snn import solve_convex_control, solve_nonconvex_experiment


def benchmark(fit_path, instance_path):
    fit = json.loads(Path(fit_path).read_text())
    problem, metadata = load_instance(instance_path)
    if metadata.get('fit_provenance', {}).get('split_sha256') != fit['split_sha256'] \
            or metadata['fit_provenance'].get('report_sha256') != fit['report_sha256'] \
            or metadata.get('offset_ev') != fit['offset_ev'] \
            or not np.array_equal(problem.h, fit['h_ev']) or not np.array_equal(problem.W, fit['W_ev']):
        raise ValueError('Instance does not match the recorded training fit')
    if problem.n != 6 or metadata['parameter_regime'] != 'heuristic':
        raise ValueError('Expected provisional six-slot model objective')
    offset = fit['offset_ev']
    oracle = exact(problem)
    optimum = float(problem.energy(oracle.x))
    records = []

    def state_summary(state):
        if state is None:
            return None
        finite = np.shape(state) == (6,) and np.isfinite(state).all()
        feasible = bool(finite and problem.feasible(state, binary=True))
        continuous_feasible = bool(finite and problem.feasible(state))
        return {'x': np.asarray(state).tolist(), 'continuous_feasible': continuous_feasible,
            'binary_feasible': feasible,
            'model_delta_ev': float(problem.energy(state))+offset if continuous_feasible else None,
            'binary_optimality_gap_ev': float(problem.energy(state))-optimum if feasible else None,
            'optimum_hit': bool(feasible and abs(float(problem.energy(state))-optimum) <= 1e-8)}

    def run(method, seed, operation):
        started = time.perf_counter()
        try:
            result = operation()
            records.append({'method': method, 'seed': seed, 'status': result.status,
                'seconds': result.seconds, 'diagnostics': result.diagnostics, 'state': state_summary(result.x)})
            return result.x
        except Exception as error:
            records.append({'method': method, 'seed': seed, 'status': 'failed',
                'seconds': time.perf_counter()-started, 'state': None,
                'error': f'{type(error).__name__}: {error}'})
            return None

    run('Gurobi', 0, lambda: solve_gurobi(problem, time_limit=60, seed=0, threads=1))
    route = solve_convex_control if problem.spectrum()['full_space_psd'] else solve_nonconvex_experiment
    for seed in range(10):
        run('SA', seed, lambda: simulated_annealing(problem, seed=seed, steps=2000,
            temperature=2.0, final_temperature=0.01, max_flips=4))
        raw = run('SNN_raw', seed, lambda: route(problem, np.random.default_rng(seed).random(6),
            max_iterations=2000, equality_band=0.0))
        started = time.perf_counter()
        decoded = (np.asarray(raw) >= 0.5).astype(float) if raw is not None and np.isfinite(raw).all() else None
        records.append({'method': 'SNN_threshold', 'seed': seed,
            'status': 'decoded' if decoded is not None else 'failed', 'state': state_summary(decoded),
            'seconds': records[-1]['seconds']+time.perf_counter()-started,
            'decode_rule': 'x>=0.5; no energy optimization or exact repair in decoding'})
    states = np.array([[int(bit) for bit in f'{i:06b}'] for i in range(64)])
    predicted = problem.energy(states)+offset
    observations = {r['id']: r['target_ev'] for r in fit['sampling_diagnostics']}
    ids = ['uio66_'+''.join(map(str, row)) for row in states]
    truth = np.array([observations[k] for k in ids])
    model_top = np.argsort(predicted, kind='stable')[:5]
    sampled_top = np.argsort(truth, kind='stable')[:5]
    packages = {}
    for name in ('numpy', 'scipy', 'snn-opt', 'gurobipy'):
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = 'unavailable; method failure retained'
    return {'scope': 'provisional UMA-trained quadratic; numerical solver quality, not chemical validation',
        'input_sha256': {str(path): hashlib.sha256(Path(path).read_bytes()).hexdigest()
            for path in (fit_path, instance_path)},
        'hardware': {'platform': platform.platform(), 'processor': platform.processor(), 'backend': 'CPU'},
        'packages': packages,
        'curvature': problem.spectrum(), 'offset_ev': offset,
        'oracle': {'state': state_summary(oracle.x), 'seconds': oracle.seconds, 'diagnostics': oracle.diagnostics},
        'runs': records,
        'summary': {method: {'runs': len(group),
            'binary_feasible': sum(bool((r['state'] or {}).get('binary_feasible')) for r in group),
            'optimum_hits': sum(bool((r['state'] or {}).get('optimum_hit')) for r in group)}
            for method in ('Gurobi', 'SA', 'SNN_raw', 'SNN_threshold')
            for group in [[r for r in records if r['method'] == method]]},
        'family_sampling_comparison': {'scope': 'all 64 same-family model samples, includes training; not held-out score',
            'top_k': 5, 'top_k_overlap': len(set(model_top)&set(sampled_top))/5,
            'sampled_best_id': ids[int(np.argmin(truth))], 'sampled_best_delta_ev': float(truth.min()),
            'model_top': [{'id': ids[i], 'predicted_ev': float(predicted[i]), 'sampled_ev': float(truth[i])}
                          for i in model_top]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fit', required=True)
    parser.add_argument('--instance', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise ValueError('Choose a new comparison path; preserve evidence')
    result = benchmark(args.fit, args.instance)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    main()
