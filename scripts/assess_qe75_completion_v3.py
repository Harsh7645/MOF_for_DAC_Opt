"""Offline assessment of the one completion attempt; never launches QE."""
import json
from datetime import datetime, timezone
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from qe75_completion_v3 import CONFIG, PREFIX, prepared_input, dump, output_status
from qe75_fedora_v1 import ROOT, sha
from qe75_feasibility_v2 import pinned
from run_qe_water_pilot import parse_result, BOHR_A, RY_EV


def assess():
    c = json.loads(CONFIG.read_text())
    work, ev = ROOT / c['work_root'], ROOT / c['evidence_root']
    result = json.loads((work / 'result.json').read_text())
    out = (work / 'stdout.log').read_text()
    stderr = (work / 'stderr.log').read_text()
    samples = [json.loads(x) for x in (work / 'resources.jsonl').read_text().splitlines()]
    started = json.loads((work / 'execution-started.json').read_text())
    package = ROOT / c['package']
    manifest = json.loads((package / 'manifest.json').read_text())
    component = manifest['components'][PREFIX]
    geometry = json.loads((package / component['geometry_file']).read_text())
    geometry['symbols'] = next(p for p in manifest['poses'] if p['id'] == component['pose'])['atom_symbols']
    status = output_status(out)
    assessment = {'ready_for_independent_assessment': False, 'scientific_accuracy_validated': False,
        'run_result': result, 'status': status, 'restart_decision': 'clean start; prior checkpoint incomplete',
        'scf_error_history_Ry': [float(x.replace('D', 'E')) for x in re.findall(
            r'estimated scf accuracy\s*<\s*([\d.EeDd+-]+) Ry', out)],
        'warnings': [x.strip() for x in out.splitlines() if re.search(
            r'warning|negative rho|not converged|renormaliz', x, re.I)],
        'maximum_sampled_swap_bytes': max(s['swap_current'] for s in samples),
        'minimum_host_available_bytes': min(s['system_available'] for s in samples),
        'maximum_sampled_tasks': max(s['tasks'] for s in samples),
        'maximum_sampled_scratch_bytes': max(s['scratch_bytes'] for s in samples),
        'preparation_seconds_before_MPI': started['unix_time'] - started['allocation']['allocation_start_unix'],
        'input_sha256': sha(work / 'input.in'), 'stdout_sha256': sha(work / 'stdout.log'),
        'stderr_sha256': sha(work / 'stderr.log'), 'checks': {}, 'validation_failure': None}
    a = started['allocation']
    gaps = []
    for before, after in zip(samples, samples[1:]):
        realtime = after['unix_time'] - before['unix_time']
        monotonic = after['process_elapsed_seconds'] - before['process_elapsed_seconds']
        if abs(realtime - monotonic) > 5:
            gaps.append({'before_utc': datetime.fromtimestamp(before['unix_time'], timezone.utc).isoformat(),
                         'after_utc': datetime.fromtimestamp(after['unix_time'], timezone.utc).isoformat(),
                         'realtime_gap_seconds': realtime, 'monotonic_gap_seconds': monotonic,
                         'difference_seconds': realtime - monotonic})
    assessment.update(elapsed_allocation_realtime_seconds=result['unix_time']-a['allocation_start_unix'],
                      deadline_overrun_realtime_seconds=max(0, result['unix_time']-a['deadline_unix']),
                      clock_sample_gaps=gaps,
                      allocation_wall_budget_met=result['unix_time'] <= a['deadline_unix'])
    postpath = ev / 'postflight.json'
    if postpath.exists():
        post = json.loads(postpath.read_text())
        gone = post['workers']['returncode'] == 1 and not post['workers']['stdout'] and not any(post['known_worker_PIDs_exist'].values())
        assessment.update(workers_remaining=not gone, cgroup_removed=not post['cgroup_exists'],
                          allocation_wall_budget_met=assessment['allocation_wall_budget_met'] and post['unix_time'] <= a['deadline_unix'],
                          system_suspend_confirmed="PM: suspend entry" in post['sleep_clock_journal']['stdout'] and "System returned from sleep" in post['sleep_clock_journal']['stdout'])
    assessment['checkpoint_files'] = [str(p.relative_to(work)) for p in (work/'scratch').rglob('*') if p.is_file()]
    assessment['saved_XML_present'] = (work/'scratch'/(PREFIX+'.save')/'data-file-schema.xml').exists()
    checks = assessment['checks']
    try:
        assert c['authorization_consumed'] and not c['attempt_approved']
        checks['package_and_executables'] = pinned(c)
        assert (work / 'input.in').read_text() == prepared_input(c, c['qe_max_seconds'])
        assert sha(work / 'input.in') == started['input_sha256']
        checks['input_and_potential_hashes'] = True
        for p in (package / 'pseudo').iterdir():
            if p.is_file():
                assert sha(p) == sha(work / 'pseudo' / p.name)
        assert result['returncode'] == 0, 'MPI did not exit successfully'
        assert result['termination_reason'] == 'process_exit_0_assessment_required', 'Controller stopped the job'
        assert not re.search('Error in routine|MPI_ABORT|segmentation fault', out + stderr, re.I)
        events = dict(line.split() for line in result['memory_events'].splitlines())
        assert all(events.get(k, '0') == '0' for k in ['high', 'max', 'oom', 'oom_kill', 'oom_group_kill'])
        assert assessment['maximum_sampled_swap_bytes'] == 0
        assert result['unix_time'] <= c['all_workers_dead_by_unix']
        checks['exit_and_resource_limits'] = True
        xml = work / 'scratch' / (PREFIX + '.save') / 'data-file-schema.xml'
        parsed = parse_result(out, xml, geometry, 522, 4)
        root = ET.parse(xml).getroot()
        assert root.attrib['Units'] == 'Hartree atomic units'
        for node in root.iter():
            node.tag = node.tag.split('}')[-1]
        def get(path):
            item = root.findtext(path)
            if item is None:
                raise ValueError('Missing XML field: ' + path)
            return item.strip()
        required = {
            'input/control_variables/restart_mode': 'from_scratch',
            'input/control_variables/disk_io': 'high',
            'input/control_variables/forces': 'true',
            'input/electron_control/diagonalization': 'cg',
            'input/electron_control/mixing_ndim': '4',
            'input/bands/occupations': 'fixed',
            'output/basis_set/gamma_only': 'true',
            'output/dft/functional': 'PBE',
            'output/dft/vdW/vdw_corr': 'grimme-d3',
            'output/dft/vdW/dftd3_version': '4',
            'output/dft/vdW/dftd3_threebody': 'false',
            'output/magnetization/lsda': 'false'}
        for path, expected in required.items():
            assert get(path) == expected, path
        for path, expected in [('input/electron_control/conv_thr', 5e-9),
                               ('input/electron_control/mixing_beta', .3),
                               ('input/bands/tot_charge', 0),
                               ('output/basis_set/ecutwfc', 40),
                               ('output/basis_set/ecutrho', 300)]:
            assert math.isclose(float(get(path)), expected, rel_tol=1e-12, abs_tol=1e-15), path
        scf_error = 2 * float(get('output/convergence_info/scf_conv/scf_error'))
        assert math.isfinite(scf_error) and 0 <= scf_error <= 1e-8
        checks['XML_scientific_and_solver_settings'] = True
        checks['final_XML_scf_error_Ry'] = scf_error
        errors = {}
        for section in ['input', 'output']:
            structure = root.find(section + '/atomic_structure')
            atoms = structure.findall('atomic_positions/atom')
            assert len(atoms) == 127 and [p.attrib['name'] for p in atoms] == geometry['symbols']
            positions = [[float(v) * BOHR_A for v in atom.text.split()] for atom in atoms]
            cell = [[float(v) * BOHR_A for v in structure.findtext('cell/' + k).split()] for k in ['a1', 'a2', 'a3']]
            for label, actual, expected in [('positions', positions, geometry['positions_A']), ('cell', cell, geometry['cell_A'])]:
                error = max(abs(x-y) for row, other in zip(actual, expected) for x, y in zip(row, other))
                assert math.isfinite(error) and error <= 2e-8
                errors[section + '_' + label + '_A'] = error
        checks['geometry_max_errors'] = errors
        species = root.findall('input/atomic_species/species')
        order = [p.attrib['name'] for p in species]
        for element in species:
            name = element.findtext('pseudo_file').strip()
            assert sha(work / 'pseudo' / name) == sha(package / 'pseudo' / name)
        forces = re.findall(r'atom\s+(\d+)\s+type\s+(\d+)\s+force\s*=\s*([-+\d.EeDd]+)\s+([-+\d.EeDd]+)\s+([-+\d.EeDd]+)', out)
        assert 'Ry/au' in out and len(forces) == 127
        xml_forces = [[float(v)*2 for v in line.split()] for line in get('output/forces').splitlines() if line.strip()]
        diffs = []
        for i, (row, xml_row) in enumerate(zip(forces, xml_forces)):
            assert int(row[0]) == i+1 and order[int(row[1])-1] == geometry['symbols'][i]
            values = [float(v.replace('D', 'E')) for v in row[2:]]
            assert all(math.isfinite(x) for x in values)
            diffs += [abs(x-y) for x, y in zip(values, xml_row)]
        assert max(diffs) <= 2e-7, 'Text/XML forces disagree'
        checks['maximum_force_text_XML_difference_Ry_bohr'] = max(diffs)
        checks['energy_units'] = 'stdout Ry; XML Hartree (factor 2), checked by existing parser'
        checks['force_units'] = 'stdout Ry/bohr (Ry/au); XML Hartree/bohr (factor 2)'
        checks['xml_sha256'] = sha(xml)
        assessment['SCF_iterations'] = parsed['SCF_iterations']
        assessment['ready_for_independent_assessment'] = True
        # Retain full energy/forces for independent review only, never imply validated accuracy.
        dump(ev / 'completed-SCF-pending-independent-assessment.json', parsed)
    except (AssertionError, ValueError, KeyError, AttributeError, FileNotFoundError, ET.ParseError) as exc:
        assessment['validation_failure'] = type(exc).__name__ + ': ' + str(exc)
    dump(ev / 'assessment.json', assessment)
    print(json.dumps({k: v for k, v in assessment.items() if k not in ['checks', 'warnings', 'run_result']}, indent=2))


if __name__ == '__main__':
    assess()
