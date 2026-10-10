"""Single first-complex attempt under an immutable four-hour total allocation.

Default prepares files only. --launch installs independent absolute stop timers
and a bounded systemd service. --execute is accepted only inside that service.
No restart fallback, retry, second geometry, or scientific acceptance is automatic.
"""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time

from qe75_fedora_v1 import ROOT, sha, runtime_environment
from qe75_feasibility_v2 import INPUT, GIB, pinned, resources, check_budget, variant

CONFIG = ROOT / 'configs/qe75-fedora-completion-v3.json'
UNIT = 'qe75-completion-v3.service'
PREFIX = 'uio66_110111_H2O_s28_f0.010_complex'
TIMERS = ['qe75-completion-v3-grace', 'qe75-completion-v3-deadline']


def dump(path, data):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


def allocation(c):
    a = json.loads((ROOT / c['allocation_file']).read_text())
    if a['deadline_unix'] - a['allocation_start_unix'] != 14400:
        raise ValueError('Invalid total allocation')
    if sha(ROOT / c['allocation_file']) != c['allocation_sha256']:
        raise ValueError('Allocation receipt changed')
    for key, offset in [('graceful_stop_unix', 1200), ('external_stop_unix', 315),
                        ('all_workers_dead_by_unix', 300)]:
        if c[key] != a['deadline_unix'] - offset:
            raise ValueError('Deadline offset changed')
    if time.time() >= c['graceful_stop_unix'] - 600:
        raise ValueError('Insufficient time left for an attempt')
    return a


def allowed(c):
    if not c['attempt_approved'] or c['authorization_consumed']:
        raise ValueError('One-attempt authorization unavailable')
    if c['start_mode'] != 'from_scratch':
        raise ValueError('Prior checkpoint is incomplete; only reviewed clean start allowed')
    expected = ['--host', 'localhost:4', '-np', '4', '--map-by', 'core',
                '--bind-to', 'core', '--nooversubscribe', '--report-bindings']
    if c['mpi_arguments'] != expected or c['ranks'] != 4 or c['threads'] != 1:
        raise ValueError('Unreviewed MPI layout')
    allocation(c)


def prepared_input(c, seconds):
    raw = (ROOT / c['package'] / INPUT).read_text(encoding='ascii')
    return variant(raw).replace('max_seconds=540', 'max_seconds=' + str(seconds), 1)


def prepare(c):
    allowed(c)
    verified = pinned(c)
    r = resources()
    check_budget(r)
    work = ROOT / c['work_root']
    work.mkdir(parents=True, exist_ok=False)
    seconds = math.floor(c['graceful_stop_unix'] - time.time() - 60)
    c['qe_max_seconds'] = seconds
    (work / 'input.in').write_text(prepared_input(c, seconds), encoding='ascii')
    shutil.copyfile(ROOT / c['package'] / INPUT, work / 'sealed-input.in')
    shutil.copytree(ROOT / c['package'] / 'pseudo', work / 'pseudo')
    (work / 'scratch').mkdir()
    dump(work / 'preparation.json', {'package_verification': verified, 'resources': r,
         'unix_time': time.time(), 'input_sha256': sha(work / 'input.in'),
         'sealed_sha256': sha(work / 'sealed-input.in'), 'previous_scratch_reused': []})
    dump(CONFIG, c)


def calendar(epoch):
    return datetime.fromtimestamp(math.floor(epoch), timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')


def properties(unit, names):
    command = ['systemctl', '--user', 'show', unit]
    for n in names:
        command += ['-p', n]
    return dict(x.split('=', 1) for x in subprocess.check_output(command, text=True).splitlines())


def timer_epoch(unit):
    p = properties(unit, ['ActiveState', 'NextElapseUSecRealtime', 'TimersCalendar'])
    if p['ActiveState'] != 'active':
        raise ValueError('Required timer inactive: ' + unit)
    epoch = float(subprocess.check_output(['date', '-d', p['NextElapseUSecRealtime'], '+%s'], text=True))
    return epoch, p


def launch(c):
    allowed(c)
    work, ev = ROOT / c['work_root'], ROOT / c['evidence_root']
    if (work / 'execution-started.json').exists():
        raise ValueError('Exclusive attempt marker exists')
    check_budget(resources())
    # A separate absolute timer remains effective if the Python monitor fails.
    commands = [
        ['systemd-run', '--user', '--unit=' + TIMERS[0], '--timer-property=AccuracySec=1s',
         '--on-calendar=' + calendar(c['graceful_stop_unix']), '/usr/bin/touch',
         str(work / 'scratch' / (PREFIX + '.EXIT'))],
        ['systemd-run', '--user', '--unit=' + TIMERS[1], '--timer-property=AccuracySec=1s',
         '--on-calendar=' + calendar(c['external_stop_unix']), '/usr/bin/systemctl', '--user', 'stop', UNIT]]
    # Leave five additional seconds for timer/service creation before runtime begins.
    runtime = math.floor(c['external_stop_unix'] - time.time() - 5)
    if runtime <= 0:
        raise ValueError('Deadline passed')
    command = ['systemd-run', '--user', '--wait', '--pipe', '--unit=' + UNIT,
        '--working-directory=' + str(ROOT), '-p', 'MemoryMax=11G', '-p', 'MemoryHigh=10G',
        '-p', 'MemorySwapMax=0', '-p', 'TasksMax=96', '-p', 'OOMPolicy=kill',
        '-p', 'RuntimeMaxSec=' + str(runtime), '-p', 'TimeoutStopSec=15s',
        '-p', 'KillMode=control-group', '-p', 'SendSIGKILL=yes', '-p', 'CPUAffinity=0-7',
        '-p', 'MemoryAccounting=yes', '-p', 'IOAccounting=yes',
        '/usr/bin/python3', str(Path(__file__).resolve()), '--execute']
    with (ev / 'launch-plan.json').open('x') as stream:
        json.dump({'timer_commands': commands, 'service_command': command,
                   'runtime_seconds': runtime, 'unix_time': time.time()}, stream, indent=2)
    with (ev / 'service-console.log').open('x') as log:
        try:
            for cmd in commands:
                subprocess.run(cmd, stdout=log, stderr=log, check=True)
            status = subprocess.run(command, stdout=log, stderr=log).returncode
            dump(ev / 'launcher-result.json', {'returncode': status, 'unix_time': time.time()})
        finally:
            # Only our own stop/exit-file timers. Never restart anything.
            subprocess.run(['systemctl', '--user', 'stop',
                            *[x + '.timer' for x in TIMERS]], stdout=log, stderr=log)


def span_seconds(value):
    scales = {'h': 3600, 'min': 60, 's': 1, 'ms': .001, 'us': .000001}
    parts = re.findall(r'([\d.]+)(min|ms|us|h|s)', value)
    if not parts:
        raise ValueError('Unrecognized time span: ' + value)
    return sum(float(v) * scales[u] for v, u in parts)


def read_counter(path):
    return dict((k, int(v)) for k, v in (line.split() for line in path.read_text().splitlines()))


def output_status(out):
    iterations = re.findall(r'iteration #\s+(\d+)', out)
    errors = re.findall(r'estimated scf accuracy\s*<\s*([\d.EeDd+-]+) Ry', out)
    return {'iteration_started': int(iterations[-1]) if iterations else 0,
            'iterations_with_error_report': len(errors),
            'latest_error_Ry': float(errors[-1].replace('D', 'E')) if errors else None,
            'convergence_reported': 'convergence has been achieved' in out,
            'forces_started': 'Forces acting on atoms' in out,
            'job_done': 'JOB DONE.' in out,
            'diagonalization_warnings': len(re.findall('eigenvalues not converged', out))}


def execute(c):
    allowed(c)
    a = allocation(c)
    verified = pinned(c)
    r = resources()
    check_budget(r)
    existing = subprocess.run(['pgrep', '-a', '-x', 'pw.x|mpirun|prterun'], capture_output=True, text=True)
    if existing.returncode != 1:
        raise ValueError('Other QE/MPI jobs present or inspection failed: ' + existing.stdout)
    cg = Path('/sys/fs/cgroup') / Path('/proc/self/cgroup').read_text().strip().split('::')[1].lstrip('/')
    actual = {x: (cg / x).read_text().strip() for x in
              ['memory.max', 'memory.high', 'memory.swap.max', 'memory.oom.group', 'pids.max']}
    if actual != {'memory.max': str(11*GIB), 'memory.high': str(10*GIB),
                  'memory.swap.max': '0', 'memory.oom.group': '1', 'pids.max': '96'}:
        raise ValueError('Cgroup limits differ')
    props = properties(UNIT, ['RuntimeMaxUSec', 'TimeoutStopUSec', 'KillMode', 'SendSIGKILL', 'ControlGroup'])
    plan = json.loads((ROOT / c['evidence_root'] / 'launch-plan.json').read_text())
    if span_seconds(props['RuntimeMaxUSec']) != plan['runtime_seconds'] or props['TimeoutStopUSec'] != '15s' or props['KillMode'] != 'control-group' or props['SendSIGKILL'] != 'yes' or Path('/sys/fs/cgroup' + props['ControlGroup']) != cg:
        raise ValueError('External service deadline/kill properties differ')
    timer_checks = {}
    for timer, key in zip(TIMERS, ['graceful_stop_unix', 'external_stop_unix']):
        t, p = timer_epoch(timer + '.timer')
        if abs(t - math.floor(c[key])) > 1:
            raise ValueError('Absolute timer deadline differs')
        timer_checks[timer] = p
    affinity = os.sched_getaffinity(0)
    topo = subprocess.check_output(['lscpu', '-p=CPU,CORE,SOCKET'], text=True)
    cores = {tuple(s.split(',')[1:]) for s in topo.splitlines()
             if not s.startswith('#') and int(s.split(',')[0]) in affinity}
    if affinity != set(range(8)) or len(cores) != 4:
        raise ValueError('Four-core binding differs')
    work, ev = ROOT / c['work_root'], ROOT / c['evidence_root']
    dump(ev / 'host-preflight.json', {'resources': r, 'unix_time': time.time(),
         'processes': subprocess.check_output(['ps', '-eo', 'user:20,pid,ppid,comm,rss', '--sort=-rss'], text=True),
         'swap': subprocess.check_output(['swapon', '--show', '--bytes'], text=True),
         'cpu_topology': topo, 'existing_qe_mpi': existing.stdout})
    if (work / 'input.in').read_text() != prepared_input(c, c['qe_max_seconds']):
        raise ValueError('Execution input changed')
    if any((work / 'scratch').iterdir()):
        raise ValueError('Clean start scratch is not empty')
    for p in (ROOT / c['package'] / 'pseudo').iterdir():
        if p.is_file() and sha(p) != sha(work / 'pseudo' / p.name):
            raise ValueError('Execution potential changed')
    command = [c['mpi_executable'], *c['mpi_arguments'], str(ROOT / c['pw_executable']), '-in', 'input.in']
    with (work / 'execution-started.json').open('x') as f:
        json.dump({'command': command, 'config': c, 'allocation': a, 'package': verified,
                   'actual_limits': actual, 'service': props, 'timers': timer_checks,
                   'affinity': sorted(affinity), 'resources': r, 'unix_time': time.time(),
                   'controller_sha256': sha(Path(__file__)), 'input_sha256': sha(work / 'input.in')}, f, indent=2)
    c['attempt_approved'], c['authorization_consumed'] = False, True
    dump(CONFIG, c)
    proc = None
    started = time.monotonic()
    started_epoch = time.time()
    grace_sent = False
    result = {'scientific_completion': False, 'termination_reason': 'not_started'}

    def interrupted(signum, frame):
        raise RuntimeError('external_signal_' + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    try:
        with (work / 'stdout.log').open('x') as out, (work / 'stderr.log').open('x') as err, (work / 'resources.jsonl').open('x') as samples:
            proc = subprocess.Popen(command, cwd=work, env=runtime_environment(c),
                                    stdout=out, stderr=err, start_new_session=True)
            dump(work / 'worker.json', {'mpi_pid': proc.pid, 'unix_time': started_epoch})
            while proc.poll() is None:
                now = time.time()
                elapsed = time.monotonic() - started
                # Wall deadline also bounded using monotonic elapsed if wall clock moves back.
                effective_now = max(now, started_epoch + elapsed)
                if effective_now >= c['graceful_stop_unix'] and not grace_sent:
                    (work / 'scratch' / (PREFIX + '.EXIT')).touch()
                    dump(work / 'graceful-stop-request.json', {'unix_time': now, 'reason': 'fixed_allocation_graceful_deadline'})
                    grace_sent = True
                mem = int((cg / 'memory.current').read_text())
                events = read_counter(cg / 'memory.events')
                pids = read_counter(cg / 'pids.events')
                rr = resources()
                disk = sum(p.stat().st_size for p in (work / 'scratch').rglob('*') if p.is_file())
                output = (work / 'stdout.log').read_text(errors='replace')
                error = (work / 'stderr.log').read_text(errors='replace')
                s = {'unix_time': now, 'process_elapsed_seconds': elapsed,
                     'allocation_elapsed_seconds': effective_now - a['allocation_start_unix'],
                     'remaining_allocation_seconds': a['deadline_unix'] - effective_now,
                     'memory_current': mem, 'memory_peak': int((cg / 'memory.peak').read_text()),
                     'swap_current': int((cg / 'memory.swap.current').read_text()),
                     'memory_events': events, 'pids_events': pids,
                     'tasks': int((cg / 'pids.current').read_text()), 'scratch_bytes': disk,
                     'system_available': rr['available'], 'free_disk': rr['free_disk'],
                     'memory_stat': read_counter(cg / 'memory.stat'),
                     'graceful_stop_requested': grace_sent, **output_status(output)}
                samples.write(json.dumps(s) + '\n'); samples.flush()
                dump(work / 'status.json', s)
                if effective_now >= c['external_stop_unix'] - 5:
                    raise RuntimeError('fixed_allocation_external_stop')
                if s['swap_current'] or any(events.get(k, 0) for k in ['high', 'max', 'oom', 'oom_kill', 'oom_group_kill']) or any(pids.values()):
                    raise RuntimeError('resource_limit_event')
                if mem >= 10.75 * GIB or rr['available'] < .75 * GIB:
                    raise RuntimeError('memory_headroom_stop')
                if disk >= 20 * GIB or rr['free_disk'] < 20 * GIB:
                    raise RuntimeError('scratch_or_free_disk_stop')
                if re.search(r'Error in routine|MPI_ABORT|segmentation fault|SIGSEGV|forrtl: severe', output + error, re.I):
                    raise RuntimeError('QE_or_MPI_fatal_error')
                time.sleep(2)
        result['termination_reason'] = 'process_exit_' + str(proc.returncode) + '_assessment_required'
    except BaseException as exc:
        result['termination_reason'] = str(exc)
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        if proc is not None and proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=3)
            except ProcessLookupError:
                proc.wait(timeout=3)
        result.update(returncode=proc.returncode if proc else None,
                      elapsed_seconds=time.monotonic() - started, unix_time=time.time(),
                      allocation_elapsed_seconds=time.time() - a['allocation_start_unix'],
                      memory_peak=int((cg / 'memory.peak').read_text()),
                      memory_events=(cg / 'memory.events').read_text(),
                      swap_current=int((cg / 'memory.swap.current').read_text()),
                      pids_events=(cg / 'pids.events').read_text(),
                      cpu_stat=(cg / 'cpu.stat').read_text(), io_stat=(cg / 'io.stat').read_text(),
                      scratch_bytes=sum(p.stat().st_size for p in (work / 'scratch').rglob('*') if p.is_file()))
        dump(work / 'result.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--launch', action='store_true')
    mode.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text())
    if args.launch:
        launch(config)
    elif args.execute:
        execute(config)
    else:
        prepare(config)
