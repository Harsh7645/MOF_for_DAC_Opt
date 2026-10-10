"""Offline assessment of the one Fedora initialization; never launches a process."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from qe75_fedora_v1 import ROOT, verify_package
from run_qe_water_pilot import BOHR_A, parse_result


def assess():
    config = json.loads((ROOT / 'configs/qe75-fedora-v1.json').read_text())
    package_verification = verify_package(config)
    assert not config['initialization_execution_approved']
    assert not config['scientific_execution_approved']
    work = ROOT / config['smoke_root']
    package = ROOT / config['package']
    out = (work / 'stdout.log').read_text()
    err = (work / 'stderr.log').read_text()
    result = json.loads((work / 'result.json').read_text())
    service = (ROOT / 'evidence/qe75-fedora-init01/service-console.log').read_text()
    xml = next((work / 'scratch').rglob('data-file-schema.xml'))
    root = ET.parse(xml).getroot()
    assert root.attrib['Units'] == 'Hartree atomic units'
    for node in root.iter():
        node.tag = node.tag.split('}')[-1]
    def value(path):
        return root.findtext(path).strip()
    assert value('input/control_variables/calculation') == 'scf'
    assert value('input/control_variables/nstep') == '0'
    assert value('exit_status') == '255'
    assert value('output/convergence_info/scf_conv/n_scf_steps') == '0'
    assert value('output/convergence_info/scf_conv/convergence_achieved') == 'false'
    assert root.find('output/total_energy') is None
    assert root.find('output/forces') is None
    assert not re.search(r'iteration\s*#|!\s+total energy|convergence has been achieved', out)
    assert 'Error in routine' not in out + err and 'JOB DONE.' in out
    assert result['returncode'] == 0
    assert value('parallel_info/nprocs') == '4' and value('parallel_info/nthreads') == '1'
    assert value('output/basis_set/gamma_only') == 'true'
    assert float(value('output/basis_set/ecutwfc')) * 2 == 80
    assert float(value('output/basis_set/ecutrho')) * 2 == 600
    assert value('output/dft/functional') == 'PBE'
    assert value('output/dft/vdW/vdw_corr') == 'grimme-d3'
    assert value('output/dft/vdW/dftd3_version') == '4'
    assert value('output/dft/vdW/dftd3_threebody') == 'false'
    assert float(re.search(r'number of electrons\s*=\s*([\d.]+)', out)[1]) == 522
    assert int(re.search(r'number of Kohn-Sham states\s*=\s*(\d+)', out)[1]) == 261
    key = 'uio66_110111_H2O_s28_f0.010_complex'
    manifest = json.loads((package / 'manifest.json').read_text())
    component = manifest['components'][key]
    geometry = json.loads((package / component['geometry_file']).read_text())
    geometry['symbols'] = next(p for p in manifest['poses'] if p['id'] == component['pose'])['atom_symbols']
    max_errors = {}
    for section in ('input', 'output'):
        structure = root.find(section + '/atomic_structure')
        atoms = structure.findall('atomic_positions/atom')
        assert len(atoms) == 127 and [a.attrib['name'] for a in atoms] == geometry['symbols']
        positions = [[float(x) * BOHR_A for x in a.text.split()] for a in atoms]
        cell = [[float(x) * BOHR_A for x in structure.findtext('cell/' + a).split()] for a in ('a1', 'a2', 'a3')]
        for field, actual, expected in [('positions', positions, geometry['positions_A']), ('cell', cell, geometry['cell_A'])]:
            error = max(abs(x - y) for row, orig in zip(actual, expected) for x, y in zip(row, orig))
            assert error < 2e-8
            max_errors[section + '_' + field + '_A'] = error
    try:
        parse_result(out, xml, geometry, 522, 4)
    except ValueError as exc:
        parser_rejection = str(exc)
    else:
        raise AssertionError('Scientific parser accepted initialization-only output')
    events = dict(line.split() for line in result['memory_events'].splitlines())
    assert all(events[key] == '0' for key in ('high', 'max', 'oom', 'oom_kill'))
    grids = {}
    for key in ('fft_grid', 'fft_smooth'):
        grids[key] = [int(root.find('output/basis_set/' + key).attrib['nr' + str(n)]) for n in (1, 2, 3)]
    return {
        'status': 'INITIALIZATION_ONLY_VERIFIED', 'scientific_result': False,
        'package_verification': package_verification, 'MPI_ranks': 4, 'threads_per_rank': 1,
        'atoms': 127, 'electrons': 522, 'occupied_bands': 261, 'cutoffs_Ry': [80, 600],
        'grids': grids, 'dense_G_vectors': int(value('output/basis_set/ngm')),
        'smooth_G_vectors': int(value('output/basis_set/ngms')),
        'PW_distribution_tally': int(re.search(r'^\s*Sum\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)', out, re.M)[1]), 'final_npwx': None,
        'npwx_note': 'Initialization XML writes npwx=0; final wavefunction dimension was not initialized.',
        'SCF_iterations': 0, 'DFT_energy_or_force_result': False, 'internal_XML_exit_status': 255,
        'process_exit_code': result['returncode'],
        'exit_note': 'Build uses default STOP without returning internal status; XML 255 confirms initialization.',
        'coordinate_max_errors_A': max_errors, 'scientific_parser_rejection': parser_rejection,
        'estimated_max_dynamical_RAM_per_rank_GiB_lower_bound_printed': float(re.search(r'Estimated max dynamical RAM per process >\s*([\d.]+) GB', out)[1]),
        'estimated_total_dynamical_RAM_GiB_lower_bound_printed': float(re.search(r'Estimated total dynamical RAM >\s*([\d.]+) GB', out)[1]),
        'memory_estimate_note': 'QE labels these GB but divides by 1024^3 in memory_report.f90. Rough estimates before large allocations, not measured full SCF peaks.',
        'measured_service_memory_peak_bytes': int(result['memory_peak']), 'memory_events': events,
        'service_wall_seconds': float(re.search(r'Service runtime:\s*([\d.]+)s', service)[1]),
        'service_CPU_seconds': float(re.search(r'CPU time consumed:\s*([\d.]+)s', service)[1]),
        'runner_MPI_monitor_seconds': result['elapsed_seconds'],
        'QE_reported_wall_seconds': float(re.search(r'PWSCF\s*:\s*[\d.]+s CPU\s*([\d.]+)s WALL', out)[1]),
        'service_swap_peak_bytes': int(re.search(r'swap:\s*(\d+)B', service)[1]),
        'accounting_source': 'evidence/qe75-fedora-init01/service-console.log',
        'scratch_bytes': sum(p.stat().st_size for p in (work / 'scratch').rglob('*') if p.is_file()),
        'warnings': ['QE renormalized C/O pseudo atomic wavefunctions in memory; sealed UPFs unchanged',
                     'IEEE_UNDERFLOW_FLAG and IEEE_DENORMAL notes on four ranks; no QE fatal error',
                     'systemd CPUAccounting property deprecated; CPU accounting still reported'],
        'decision': 'Do not launch full SCF under current 8-GiB cap; estimate exceeds cap. No further execution authorized.',
        'unknowns': ['actual SCF/diagonalization peak RAM', 'full SCF runtime and scratch',
                     'SCF convergence', 'forces and total energies', 'numerical convergence and UMA accuracy',
                     'complete converged-output parser compatibility'],
    }


if __name__ == '__main__':
    assessment = assess()
    destination = ROOT / 'evidence/qe75-fedora-init01/assessment.json'
    with destination.open('x') as stream:
        json.dump(assessment, stream, indent=2)
        stream.write('\n')
    print(json.dumps(assessment, indent=2))
