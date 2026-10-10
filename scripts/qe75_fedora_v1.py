"""Fedora v1 package/software checks and initialization staging; cannot run DFT.

The sealed 32-rank launcher is preserved. This adapter only stages nstep=0
copies after checking release identity. It never calls pw.x with an input.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def resolve(name):
    return (ROOT / name).resolve()


def verify_package(config):
    archive, receipt, package = (resolve(config[k]) for k in ('archive', 'receipt', 'package'))
    for path in (archive, receipt, package / 'file_hashes.json'):
        if not path.exists():
            raise ValueError(f'Required transferred artifact missing: {path.relative_to(ROOT)}')
    if sha(archive) != config['archive_sha256']:
        raise ValueError('Sealed ZIP SHA256 differs from documented release')
    release = json.loads(receipt.read_text())
    def values(obj):
        if isinstance(obj, dict):
            return [v for x in obj.values() for v in values(x)]
        if isinstance(obj, list):
            return [v for x in obj for v in values(x)]
        return [obj]
    pins = values(release)
    manifest_sha = sha(package / 'file_hashes.json')
    if config['archive_sha256'] not in pins or manifest_sha not in pins:
        raise ValueError('Receipt does not pin both archive and manifest hashes; inspect schema')
    hashes = json.loads((package / 'file_hashes.json').read_text())
    if len(hashes) != config['expected_package_files']:
        raise ValueError('Unexpected release file count')
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        candidates = [n for n in names if n == 'file_hashes.json' or n.endswith('/file_hashes.json')]
        matching = [n for n in candidates if hashlib.sha256(z.read(n)).hexdigest() == manifest_sha]
        if len(matching) != 1 or len(names) != len(set(names)):
            raise ValueError('ZIP manifest identity/duplicate entry failure')
        prefix = matching[0][:-len('file_hashes.json')]
        for name, expected in hashes.items():
            path = (package / name).resolve()
            if not path.is_relative_to(package) or sha(path) != expected:
                raise ValueError('Unpacked release mismatch: ' + name)
            if hashlib.sha256(z.read(prefix + name)).hexdigest() != expected:
                raise ValueError('Archived release mismatch: ' + name)
    return {'verified_files': len(hashes), 'archive_sha256': sha(archive),
            'manifest_sha256': manifest_sha, 'receipt_sha256': sha(receipt)}


def software(config):
    result = {}
    env = runtime_environment(config)
    for kind, key, args in [('pw', 'pw_executable', ['-in', '/dev/null']), ('mpi', 'mpi_executable', ['--version'])]:
        path = resolve(config[key])
        if not path.is_file():
            raise ValueError('Executable absent: ' + str(path))
        parent = ROOT / 'evidence/qe75-fedora-v1'
        parent.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix=kind + '-startup-', dir=parent))
        run = subprocess.run([str(path), *args], stdin=subprocess.DEVNULL,
                             capture_output=True, text=True, timeout=30, env=env, cwd=work)
        (work / 'stdout.log').write_text(run.stdout)
        (work / 'stderr.log').write_text(run.stderr)
        output = run.stdout + run.stderr
        if (kind == 'pw' and not expected_empty_input_startup(run.returncode, output)) or (kind == 'mpi' and run.returncode):
            raise ValueError('Executable startup/version check failed: ' + output)
        digest = sha(path)
        if config[kind + '_sha256'] and digest != config[kind + '_sha256']:
            raise ValueError('Executable pin differs: ' + kind)
        result[kind] = {'path': str(path), 'sha256': digest, 'output': output,
                        'command': [str(path), *args], 'returncode': run.returncode,
                        'retained_startup_directory': str(work.relative_to(ROOT)),
                        'check': 'expected empty-input rejection, NOT SCF validation' if kind == 'pw' else 'version'}
    result['ldd'] = subprocess.run(['ldd', str(resolve(config['pw_executable']))],
                                   capture_output=True, text=True, check=True).stdout
    if 'not found' in result['ldd']:
        raise ValueError('Unresolved shared libraries')
    runtime = resolve(config['ompi_prterun'])
    if not config.get('prterun_sha256') or sha(runtime) != config['prterun_sha256']:
        raise ValueError('Underlying PRRTE runtime hash is not pinned or differs')
    result['prterun'] = {'path': str(runtime), 'sha256': sha(runtime)}
    return result


def expected_empty_input_startup(returncode, output):
    """QE 7.5 has no -h handler: use explicit /dev/null and require its exact failure."""
    errors = re.findall(r'Error in routine\s+(\w+)\s*\(\s*(\d+)\s*\)', output)
    return (returncode == 1 and bool(re.search(r'Program PWSCF\s+v\.7\.5\b', output))
            and errors == [('read_namelists', '2')]
            and 'could not find namelist &control' in output
            and not any(s in output for s in ('Operation not permitted', 'socket() failed',
                                              'Self-consistent Calculation', 'iteration #')))


def runtime_environment(config):
    return os.environ | {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1',
                         'MKL_NUM_THREADS': '1', 'OMPI_PRTERUN': config['ompi_prterun'],
                         'PATH': config['mpi_runtime_bin'] + ':' + os.environ.get('PATH', '')}


def stage(config):
    verified = verify_package(config)
    checked = software(config)
    if not config['pw_sha256'] or not config['mpi_sha256']:
        raise ValueError('Pin checked executables in a reviewed configuration first')
    topology = subprocess.check_output(['lscpu', '-p=CPU,CORE,SOCKET'], text=True)
    cores = {tuple(line.split(',')[1:]) for line in topology.splitlines()
             if not line.startswith('#') and int(line.split(',')[0]) in os.sched_getaffinity(0)}
    if config['ranks'] != 4 or config['threads'] != 1 or len(cores) < 4:
        raise ValueError('Fedora v1 requires four physical cores and one thread per rank')
    mem = int(re.search(r'MemAvailable:\s+(\d+)', Path('/proc/meminfo').read_text())[1]) * 1024
    if mem < config['minimum_available_RAM_GiB'] * 2**30:
        raise ValueError('Need 10 GiB available physical RAM; close applications and recheck')
    if shutil.disk_usage(ROOT).free < config['minimum_free_disk_GiB'] * 2**30:
        raise ValueError('Insufficient persistent free disk')
    package = resolve(config['package'])
    source = package / 'inputs/uio66_110111_H2O_s28_f0.010_complex__baseline.in'
    raw = source.read_bytes()
    text = raw.decode('ascii')
    if re.search(r'\bnstep\s*=', text, re.I) or len(re.findall(r'&CONTROL\b', text, re.I)) != 1:
        raise ValueError('Unexpected input: inspect before creating initialization copy')
    modified = re.sub(r'(&CONTROL\b)', r'\1\n  nstep=0,', text, count=1, flags=re.I)
    # Only this insertion is permitted; all existing settings/coordinates survive.
    if modified.replace('\n  nstep=0,', '', 1).encode('ascii') != raw:
        raise ValueError('Input copy changed beyond the documented insertion')
    work = resolve(config['smoke_root'])
    if not work.is_relative_to(ROOT / 'local'):
        raise ValueError('Smoke storage must be inside persistent repository local/')
    work.mkdir(parents=True, exist_ok=False)
    (work / 'scratch').mkdir()
    shutil.copytree(package / 'pseudo', work / 'pseudo')
    (work / 'sealed-input.in').write_bytes(raw)
    (work / 'input.in').write_bytes(modified.encode('ascii'))
    record = {'package': verified, 'software': checked, 'source_sha256': sha(source),
              'input_sha256': sha(work / 'input.in'), 'change': 'Only add nstep=0 to &CONTROL',
              'calculation_launched': False, 'not_a_scientific_result': True}
    (work / 'staging.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['package', 'software', 'stage-smoke'])
    parser.add_argument('--config', default='configs/qe75-fedora-v1.json')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = resolve(args.output)
    if output.exists():
        parser.error('Use a new output path to preserve previous evidence')
    config = json.loads(resolve(args.config).read_text())
    try:
        data = {'status': 'PASS', 'result': {'package': verify_package, 'software': software,
                                          'stage-smoke': stage}[args.action](config)}
    except (OSError, ValueError, subprocess.SubprocessError, KeyError, zipfile.BadZipFile) as exc:
        data = {'status': 'BLOCKED', 'reason': str(exc)}
    data.update(action=args.action, scientific_calculation_launched=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))
    return 0 if data['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
