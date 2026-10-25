"""Stdlib-only offline preparation checks and registered sensitivity arithmetic.

Never starts QE/MPI, submits jobs, installs software or accepts physical accuracy.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def force_sensitivity(reference, refined):
    """All atoms, each structure separately; input/output units eV/Angstrom."""
    require(len(reference) == len(refined) > 0, 'Identical nonempty atom mapping required')
    components = []
    for a, b in zip(reference, refined):
        require(len(a) == len(b) == 3, 'Three Cartesian components required')
        require(all(math.isfinite(v) for v in (*a, *b)), 'Nonfinite force')
        delta = [y-x for x, y in zip(a, b)]
        require(all(math.isfinite(v) for v in delta), 'Nonfinite force difference')
        components.append(delta)
    norms = [math.hypot(*row) for row in components]
    maximum = max(norms)
    return {'signed_components_eV_A': components, 'atom_norms_eV_A': norms,
            'maximum_norm_eV_A': maximum, 'sensitivity_target_met': maximum <= 0.005,
            'absolute_accuracy_established': False}


def energy_sensitivities(reference, refined):
    """Reconstructed formulas only; complex/host arrays contain [E(A), E(B)] in eV.

    Missing host data remain unevaluated, never a passing host/decomposition test.
    Formula confirmation and valid SCF/output prerequisites are separate gates.
    """
    def difference(energies, key):
        pair = energies.get(key)
        if pair is None:
            return None
        require(len(pair) == 2 and all(math.isfinite(v) for v in pair), 'Two finite energies required')
        value = pair[1]-pair[0]
        require(math.isfinite(value), 'Nonfinite energy difference')
        return value
    deltas = []
    for energies in (reference, refined):
        c, h = difference(energies, 'complex_eV'), difference(energies, 'host_eV')
        require(c is not None, 'Complex comparison required')
        deltas.append({'complex': c, 'host': h, 'guest_associated': None if h is None else c-h})
    result = {}
    for key in ('complex', 'host', 'guest_associated'):
        a, b = (d[key] for d in deltas)
        if a is None or b is None:
            result[key] = {'status': 'unevaluated', 'sensitivity_target_met': None}
        else:
            change = b-a
            require(math.isfinite(change), 'Nonfinite sensitivity')
            result[key] = {'signed_change_meV': change*1000, 'absolute_change_meV': abs(change)*1000,
                           'sensitivity_target_met': abs(change) <= 0.002}
    return {'comparisons': result, 'absolute_accuracy_established': False,
            'formula_provenance': 'reconstruction; reviewer confirmation tracked in assessment-spec.json'}


def verify(package):
    package = package.resolve()
    hashes = json.loads((package/'file-hashes.json').read_text(encoding='utf-8'))
    for name, expected in hashes.items():
        path = package/name
        require(not path.is_symlink() and path.resolve().is_relative_to(package), 'Unsafe payload path')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, 'Payload hash mismatch: '+name)
    def read(name):
        return json.loads((package/name).read_text(encoding='utf-8'))
    spec, inventory, environment = read('assessment-spec.json'), read('job-inventory.json'), read('environment-requirements.json')
    require(spec['energy']['threshold_meV'] == 2.0 and spec['energy']['inequality'] == '<= threshold', 'Energy registration differs')
    require(spec['force']['threshold_eV_A'] == 0.005 and spec['force']['excluded_atoms'] == [], 'Force registration differs')
    require(spec['energy']['final_common_refined_direct_baseline_comparison_required'], 'Direct baseline comparison required')
    policy = spec['comparison_policy']
    require(policy['successive_registered_refinements_required']
            and policy['eventual_common_refined_vs_original_baseline_required']
            and policy['applies_to'] == ['energy', 'force'], 'Both comparison routes required for energy and force')
    require(not spec['energy']['passing_is_absolute_error_bound'], 'Sensitivity is not absolute accuracy')
    require(all(not x['execution_authorized'] for x in (spec, inventory, environment)), 'Preparation cannot authorize execution')
    require(not inventory['execution_enabled'] and len(inventory['jobs']) == 4, 'Two conditional reproduction and two density jobs required')
    require(inventory['budgets']['density_pair'] == {'jobs': 2, 'wall_hours': 8, 'core_hours': 32}, 'Density budget changed')
    require(inventory['budgets']['combined_if_required'] == {'jobs': 4, 'wall_hours': 16, 'core_hours': 64}, 'Separate reproduction budget required')
    require(environment['available_RAM_GiB_at_launch_min'] == 24 and environment['hard_job_memory_GiB'] == 20
            and environment['graceful_stop_memory_GiB'] == 18 and environment['job_swap_bytes'] == 0, 'Resource proposal differs')
    with (package/'force-atom-map.csv').open(newline='', encoding='utf-8') as stream:
        mapping = list(csv.DictReader(stream))
    baseline = read('baseline-reference.json')
    for ident in baseline['geometry_order']:
        original = (package/'inputs'/f'{ident}__80_600.in').read_bytes()
        candidate = (package/'inputs'/f'{ident}__80_750.in').read_bytes()
        require(original.count(b'ecutrho=600') == candidate.count(b'ecutrho=750') == 1, 'Unique density change required')
        require(candidate.replace(b'ecutrho=750', b'ecutrho=600') == original, 'Additional input change')
        geometry = read('geometries/'+ident+'.json')
        rows = [r for r in mapping if r['manifest_id'] == ident]
        require(len(rows) == len(geometry['numbers']) == 127, 'All 127 atoms required')
        require([int(r['QE_atom_1based']) for r in rows] == list(range(1, 128)), 'QE order changed')
        require([int(r['atomic_number']) for r in rows] == geometry['numbers'], 'Atom identity changed')
        require([int(r['source_index_0based']) for r in rows] == baseline['structures'][ident]['source_atom_indices'], 'Source mapping changed')
        forces = baseline['structures'][ident]['forces_eV_A']
        require(len(forces) == 127, 'Baseline forces missing')
        force_sensitivity(forces, forces)  # Shape/finite validation only, not a refined-result assessment.
    return {'payloads_verified': len(hashes), 'immediate_density_jobs': 2,
            'conditional_extra_baseline_jobs': 2, 'mapped_atoms': len(mapping),
            'execution_authorized': False, 'formula_confirmed': spec['energy']['formula_confirmed'],
            'comparison_routes': ['successive_registered_refinements', 'common_refined_vs_original_baseline'],
            'machine_identified': environment['machine_identified'], 'scientific_results_assessed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path('plans/qe75-water-convergence-v2'))
    args = parser.parse_args()
    print(json.dumps(verify(args.package), indent=2))
