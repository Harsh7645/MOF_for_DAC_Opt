"""One Fedora SCF resource test; default is preparation, never scientific acceptance."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

from qe75_fedora_v1 import ROOT, sha, verify_package, runtime_environment

CONFIG = ROOT / 'configs/qe75-fedora-feasibility-v2.json'
INPUT = 'inputs/uio66_110111_H2O_s28_f0.010_complex__baseline.in'
UNIT = 'qe75-feasibility-v2.service'
GIB = 2**30


def dump(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def variant(original):
    changes = [("&CONTROL\n", "&CONTROL\n disk_io='high', verbosity='high',\n"),
               ('max_seconds=13800', 'max_seconds=540'),
               ('&ELECTRONS\n', "&ELECTRONS\n diagonalization='cg', mixing_ndim=4,\n")]
    changed = original
    for old, new in changes:
        if changed.count(old) != 1:
            raise ValueError('Unexpected sealed input format')
        changed = changed.replace(old, new, 1)
    check = changed
    for old, new in reversed(changes):
        check = check.replace(new, old, 1)
    if check != original:
        raise ValueError('Unexpected scientific input change')
    return changed


def resources():
    info = Path('/proc/meminfo').read_text()
    mem = {k: int(v) * 1024 for k, v in re.findall(r'^(\w+):\s+(\d+) kB', info, re.M)}
    return {'meminfo': info, 'total': mem['MemTotal'], 'available': mem['MemAvailable'],
            'free_disk': shutil.disk_usage(ROOT).free}


def check_budget(r):
    if r['total'] - 11 * GIB < 3.5 * GIB or r['available'] < 12 * GIB:
        raise ValueError('Need 3.5 GiB total reserve and 12 GiB currently available')
    if r['free_disk'] < 40 * GIB:
        raise ValueError('Need 40 GiB persistent free disk')


def pinned(config):
    receipt = verify_package(config)
    for file_key, hash_key in [('pw_executable', 'pw_sha256'), ('mpi_executable', 'mpi_sha256'),
                                ('ompi_prterun', 'prterun_sha256')]:
        if sha(ROOT / config[file_key]) != config[hash_key]:
            raise ValueError('Executable changed: ' + file_key)
    return receipt


def prepare(config):
    receipt = pinned(config)
    r = resources()
    check_budget(r)
    work = ROOT / config['work_root']
    work.mkdir(parents=True, exist_ok=False)
    raw = (ROOT / config['package'] / INPUT).read_bytes()
    (work / 'sealed-input.in').write_bytes(raw)
    (work / 'input.in').write_bytes(variant(raw.decode('ascii')).encode('ascii'))
    shutil.copytree(ROOT / config['package'] / 'pseudo', work / 'pseudo')
    (work / 'scratch').mkdir()
    dump(work / 'preparation.json', {'package': receipt, 'resources': r,
                                    'source_sha256': sha(work / 'sealed-input.in'),
                                    'input_sha256': sha(work / 'input.in'), 'launched': False})


def execute(config):
    if not config['feasibility_test_approved'] or config['authorization_consumed']:
        raise ValueError('One-test authorization unavailable')
    if config['ranks'] != 4 or config['threads'] != 1 or config['memory_max_GiB'] != 11:
        raise ValueError('Unreviewed allocation')
    pinned(config)
    r = resources()
    check_budget(r)
    existing = subprocess.run(['pgrep', '-a', '-x', 'pw.x|mpirun|prterun'],
                              capture_output=True, text=True)
    if existing.returncode != 1:
        raise ValueError('Existing QE/MPI job or failed process inspection: ' + existing.stdout)
    cg = Path('/sys/fs/cgroup') / Path('/proc/self/cgroup').read_text().strip().split('::')[1].lstrip('/')
    limits = {k: (cg / k).read_text().strip() for k in
              ['memory.max', 'memory.high', 'memory.swap.max', 'memory.oom.group', 'pids.max']}
    if limits != {'memory.max': str(11*GIB), 'memory.high': str(10*GIB),
                  'memory.swap.max': '0', 'memory.oom.group': '1', 'pids.max': '96'}:
        raise ValueError('Actual cgroup limits differ: ' + str(limits))
    props = dict(line.split('=', 1) for line in subprocess.check_output(
        ['systemctl', '--user', 'show', UNIT, '-p', 'RuntimeMaxUSec', '-p', 'TimeoutStopUSec',
         '-p', 'KillMode', '-p', 'SendSIGKILL', '-p', 'ControlGroup'], text=True).splitlines())
    if props['RuntimeMaxUSec'] != '9min 45s' or props['TimeoutStopUSec'] != '15s' or props['KillMode'] != 'control-group' or props['SendSIGKILL'] != 'yes' or Path('/sys/fs/cgroup'+props['ControlGroup']) != cg:
        raise ValueError('Actual service time/termination limits differ')
    affinity = os.sched_getaffinity(0)
    if affinity != set(range(8)):
        raise ValueError('Expected logical CPUs 0-7, four physical cores')
    topo = subprocess.check_output(['lscpu', '-p=CPU,CORE,SOCKET'], text=True)
    cores = {tuple(line.split(',')[1:]) for line in topo.splitlines()
             if not line.startswith('#') and int(line.split(',')[0]) in affinity}
    if len(cores) != 4:
        raise ValueError('Physical-core mapping changed')
    work = ROOT / config['work_root']
    original = (ROOT / config['package'] / INPUT).read_bytes()
    if (work/'input.in').read_bytes() != variant(original.decode('ascii')).encode('ascii'):
        raise ValueError('Staged input changed')
    for p in (ROOT/config['package']/'pseudo').iterdir():
        if p.is_file() and sha(p) != sha(work/'pseudo'/p.name):
            raise ValueError('Staged potential changed')
    command = [config['mpi_executable'], *config['mpi_arguments'],
               str(ROOT / config['pw_executable']), '-in', 'input.in']
    expected_mpi = ['--host', 'localhost:4', '-np', '4', '--map-by', 'core',
                    '--bind-to', 'core', '--nooversubscribe', '--report-bindings']
    if config['mpi_arguments'] != expected_mpi:
        raise ValueError('Unreviewed MPI layout')
    with (work/'execution-started.json').open('x') as stream:
        json.dump({'command': command, 'configuration': config, 'resources': r, 'limits': limits,
                   'service': props, 'affinity': sorted(affinity), 'unix_time': time.time()}, stream, indent=2)
    config['authorization_consumed'] = True
    config['feasibility_test_approved'] = False
    dump(CONFIG, config)
    proc = None
    start = time.monotonic()
    result = {'scientific_result': False, 'termination_reason': 'not_started'}
    def interrupted(signum, frame):
        raise RuntimeError('external_signal_' + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    try:
        with (work/'stdout.log').open('x') as out, (work/'stderr.log').open('x') as err, (work/'resources.jsonl').open('x') as samples:
            proc = subprocess.Popen(command, cwd=work, env=runtime_environment(config),
                                    stdout=out, stderr=err, start_new_session=True)
            while proc.poll() is None:
                elapsed = time.monotonic() - start
                mem = int((cg/'memory.current').read_text())
                disk = sum(p.stat().st_size for p in (work/'scratch').rglob('*') if p.is_file())
                rr = resources()
                sample = {'elapsed_seconds': elapsed, 'memory_current': mem,
                          'memory_peak': int((cg/'memory.peak').read_text()),
                          'swap_current': int((cg/'memory.swap.current').read_text()),
                          'scratch_bytes': disk, 'system_available': rr['available'],
                          'free_disk': rr['free_disk']}
                samples.write(json.dumps(sample)+'\n'); samples.flush()
                if elapsed >= 570:
                    raise RuntimeError('time_limit_570s_orderly_stop')
                if mem >= 10.75*GIB:
                    raise RuntimeError('memory_stop_10.75GiB')
                if rr['available'] < .75*GIB:
                    raise RuntimeError('system_available_below_0.75GiB')
                if disk >= 20*GIB or rr['free_disk'] < 20*GIB:
                    raise RuntimeError('scratch_or_free_disk_stop')
                if 'Error in routine' in (work/'stdout.log').read_text() or 'MPI_ABORT' in (work/'stderr.log').read_text():
                    raise RuntimeError('QE_or_MPI_error')
                time.sleep(1)
        result['termination_reason'] = 'process_exit_' + str(proc.returncode) + '_review_required'
    except BaseException as exc:
        result['termination_reason'] = str(exc)
    finally:
        if proc is not None and proc.poll() is None:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)
        result.update(elapsed_seconds=time.monotonic()-start,
                      returncode=proc.returncode if proc else None,
                      memory_peak=int((cg/'memory.peak').read_text()),
                      memory_events=(cg/'memory.events').read_text(),
                      pids_events=(cg/'pids.events').read_text(),
                      cpu_stat=(cg/'cpu.stat').read_text(), io_stat=(cg/'io.stat').read_text(),
                      scratch_bytes=sum(p.stat().st_size for p in (work/'scratch').rglob('*') if p.is_file()))
        dump(work/'result.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    cfg = json.loads(CONFIG.read_text())
    execute(cfg) if args.execute else prepare(cfg)
