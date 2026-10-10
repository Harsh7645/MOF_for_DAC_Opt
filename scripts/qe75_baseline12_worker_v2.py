"""One authorized manifest baseline job; batch orchestrator handles sequential order.

Guard runs as a separate user service under systemd-inhibit. The worker has its
own cgroup, immutable absolute timers, runtime backup and whole-cgroup cleanup.
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
from qe75_feasibility_v2 import GIB, resources, check_budget
from qe75_completion_v3 import properties, calendar, read_counter, output_status

SCRIPT = Path(__file__).resolve()
PREFIX = None  # bound to the pinned manifest job at process entry


def dump(p, value):
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    tmp.replace(p)


def command(args, check=True):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=25)
    except subprocess.TimeoutExpired as exc:
        if check:
            raise
        return {'args': args, 'returncode': 124, 'stdout': '', 'stderr': str(exc)}
    if check and r.returncode:
        raise RuntimeError(str(args) + ': ' + r.stderr)
    return {'args': args, 'returncode': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}


def receipt(c):
    p = ROOT / c['allocation_file']
    if sha(p) != c['allocation_sha256']:
        raise ValueError('Immutable allocation changed')
    return json.loads(p.read_text())


def elapsed(c):
    a = receipt(c)
    h = json.loads((ROOT / c['host_clock_file']).read_text())
    return max(time.time() - a['allocation_start_unix'],
               time.clock_gettime(time.CLOCK_BOOTTIME) - h['start_boottime_host'],
               time.monotonic() - h['start_monotonic_host'])


def ac_online():
    files = list(Path('/sys/class/power_supply').glob('*/online'))
    return bool(files) and any(p.read_text().strip() == '1' for p in files)


def inhibitor(c):
    rows = json.loads(command(['systemd-inhibit', '--list', '--json=short', '--no-pager'])['stdout'])
    own = [r for r in rows if r['who'] == c['inhibitor_who']]
    if len(own) != 1 or own[0]['mode'] != 'block' or not {'sleep', 'idle'} <= set(own[0]['what'].split(':')):
        raise ValueError('Task-owned sleep/idle inhibitor absent')
    if not Path('/proc', str(own[0]['pid'])).exists():
        raise ValueError('Inhibitor owner gone')
    return own[0]


def fresh(c):
    if not c['dummy']:
        ba = ROOT / c['batch_allocation']
        if sha(ba) != c['batch_allocation_sha256']:
            raise ValueError('Batch deadline receipt changed')
        batch = json.loads(ba.read_text())
        clock_path = ROOT / c['batch_clock_file']
        if sha(clock_path) != c['batch_clock_sha256']:
            raise ValueError('Recovery clock anchor changed')
        clock = json.loads(clock_path.read_text())
        if Path('/proc/sys/kernel/random/boot_id').read_text().strip() != clock['boot_id']:
            raise ValueError('Unexpected boot; never auto-resume')
        be = max(time.time()-batch['allocation_start_unix'],
                 clock['original_elapsed_at_recovery_s']+time.clock_gettime(time.CLOCK_BOOTTIME)-clock['recovery_boottime'],
                 clock['original_elapsed_at_recovery_s']+time.monotonic()-clock['recovery_monotonic'])
        if be >= batch['total_seconds']-300:
            raise ValueError('Batch finalization reserve reached')
        jobs = ROOT / c['jobs_file']
        if sha(jobs) != c['jobs_sha256']:
            raise ValueError('Reviewed manifest job list changed')
        selected = json.loads(jobs.read_text())[c['job_order']-1]
        if selected['manifest_id'] != PREFIX or not selected['feasibility_pass'] or selected['input_sha256'] != c['input_sha256']:
            raise ValueError('Manifest job identity or feasibility differs')
        if sha(ROOT / selected['geometry_file']) != selected['geometry_file_sha256']:
            raise ValueError('Frozen geometry changed')
    if not ac_online():
        raise ValueError('AC disconnected')
    jobs = command(['pgrep', '-a', '-x', 'pw.x|mpirun|prterun|orted'], check=False)
    if jobs['returncode'] != 1:
        raise ValueError('Existing QE/MPI job or inspection failure')
    r = resources()
    if not c['dummy']:
        if not c.get('controller_reviewed_and_dummy_passed', False):
            raise ValueError('Controller review and integrated dummy test incomplete')
        review_path = ROOT / c['evidence_root'] / 'controller-review.json'
        review = json.loads(review_path.read_text())
        if sha(review_path) != c['controller_review_sha256'] or review['controller_sha256'] != sha(SCRIPT) or not review['passed']:
            raise ValueError('Controller review identity changed')
        check_budget(r)
    if elapsed(c) >= receipt(c)['grace_seconds'] - (1 if c['dummy'] else 30):
        raise ValueError('Insufficient original allocation remaining')
    return r


def reuse_verification(c):
    """Reuse the recorded full package audit; check runtime identities only."""
    p = ROOT / 'evidence/qe75-rho-diagnostic-plan-v1/final-verification.json'
    v = json.loads(p.read_text())
    manifest = ROOT / c['package'] / 'file_hashes.json'
    if v['sealed_package']['verified_files'] != 140 or sha(manifest) != v['sealed_package']['manifest_sha256']:
        raise ValueError('Recorded package verification cannot be reused')
    for key, pin in [('pw_executable','pw_sha256'), ('mpi_executable','mpi_sha256'), ('ompi_prterun','prterun_sha256')]:
        if sha(ROOT / c[key]) != c[pin]:
            raise ValueError('Executable changed: ' + key)
    return {'reused_evidence': str(p.relative_to(ROOT)), 'evidence_sha256': sha(p),
            'verified_files_previously': 140, 'current_manifest_sha256': sha(manifest)}


def override(unit):
    p = Path(os.environ['XDG_RUNTIME_DIR']) / 'systemd/user' / (unit + '.d')
    p.mkdir(parents=True, exist_ok=False)
    f = p / '90-qe-stop.conf'
    f.write_text('[Service]\nTimeoutStopFailureMode=kill\nFinalKillSignal=SIGKILL\n')
    command(['systemctl', '--user', 'daemon-reload'])
    return f


def stop_reason(s):
    if s['swap_current'] or any(s['memory_events'].get(k, 0) for k in
                              ['high', 'max', 'oom', 'oom_kill', 'oom_group_kill']) or any(s['pids_events'].values()):
        return 'resource_limit_event'
    if s['memory_current'] >= 10.75*GIB or s['system_available'] < .75*GIB:
        return 'memory_headroom_stop'
    if s['scratch_bytes'] >= 20*GIB or s['free_disk'] < 20*GIB:
        return 'storage_stop'
    return None


def dummy_process(work, role):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    dump(work / (role + '-pid.json'), {'pid': os.getpid(), 'start_ticks': Path('/proc/self/stat').read_text().split()[21]})
    if role != 'grandchild':
        subprocess.Popen(['/usr/bin/python3', str(SCRIPT), '--dummy-process', str(work),
                          '--role', 'child' if role == 'parent' else 'grandchild'], start_new_session=True)
    with (work / (role + '-partial.log')).open('x') as f:
        while True:
            f.write(str(time.time()) + '\n'); f.flush(); time.sleep(.1)


def worker(c, config_path):
    work = ROOT / c['work_root']
    fresh(c)
    active_inhibitor = inhibitor(c)
    cg = Path('/sys/fs/cgroup') / Path('/proc/self/cgroup').read_text().strip().split('::')[1].lstrip('/')
    actual = {k: (cg / k).read_text().strip() for k in
              ['memory.max', 'memory.high', 'memory.swap.max', 'memory.oom.group', 'pids.max']}
    expected = {'memory.max': str(11*GIB), 'memory.high': str(10*GIB), 'memory.swap.max': '0',
                'memory.oom.group': '1', 'pids.max': '96'}
    if actual != expected:
        raise ValueError('Cgroup limits differ')
    p = properties(c['unit'], ['KillMode', 'SendSIGKILL', 'FinalKillSignal', 'TimeoutStopFailureMode', 'TimeoutStopUSec'])
    if p != {'KillMode': 'control-group', 'SendSIGKILL': 'yes', 'FinalKillSignal': '9',
             'TimeoutStopFailureMode': 'kill', 'TimeoutStopUSec': '2s' if c['dummy'] else '15s'}:
        raise ValueError('Effective stop policy differs: ' + str(p))
    topo = command(['lscpu', '-p=CPU,CORE,SOCKET'])['stdout']
    affinity = os.sched_getaffinity(0)
    cores = {tuple(x.split(',')[1:]) for x in topo.splitlines()
             if not x.startswith('#') and int(x.split(',')[0]) in affinity}
    if affinity != set(range(8)) or len(cores) != 4:
        raise ValueError('Four-physical-core allocation differs')
    if not c['dummy']:
        if not c['attempt_approved'] or c['authorization_consumed']:
            raise ValueError('One-run authorization unavailable')
        reuse_verification(c)
        if sha(work / 'input.in') != c['input_sha256'] or any((work / 'scratch').iterdir()):
            raise ValueError('Input changed or scratch not empty')
        hashes = json.loads((ROOT / c['package'] / 'file_hashes.json').read_text())
        for f in (ROOT / c['package'] / 'pseudo').iterdir():
            if f.is_file() and (sha(f) != hashes['pseudo/'+f.name] or sha(f) != sha(work / 'pseudo' / f.name)):
                raise ValueError('Potential changed')
    dump(work / 'worker-checks.json', {'actual_limits': actual, 'stop_policy': p,
         'affinity': sorted(affinity), 'physical_cores': sorted(cores), 'inhibitor': active_inhibitor,
         'elapsed': elapsed(c), 'cgroup': str(cg), 'resources': resources(),
         'AC_online': ac_online(), 'controller_sha256': sha(SCRIPT)})
    if c['dummy']:
        dummy_process(work, 'parent')
        return
    cmd = [c['mpi_executable'], *c['mpi_arguments'], str(ROOT / c['pw_executable']), '-in', 'input.in']
    with (work / 'execution-started.json').open('x') as f:
        json.dump({'command': cmd, 'time': time.time(), 'allocation': receipt(c),
                   'input_sha256': c['input_sha256'], 'controller_sha256': sha(SCRIPT)}, f, indent=2)
    c['attempt_approved'], c['authorization_consumed'] = False, True
    dump(config_path, c)
    os.chdir(work)
    os.execve(cmd[0], cmd, runtime_environment(c))


def supervise(c, config_path):
    work, ev = ROOT / c['work_root'], ROOT / c['evidence_root']
    a = receipt(c)
    result = {'scientific_energy_accepted': False, 'termination_reason': 'preparation_failed'}
    unit, timer = c['unit'], c['unit'].removesuffix('.service') + '-deadline'
    grace = c['unit'].removesuffix('.service') + '-grace'
    cg = None; policy = None; launched = False; max_memory = 0; max_swap = 0
    def interrupted(signum, frame):
        raise RuntimeError('guardian_signal_' + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    try:
        r = fresh(c); dump(ev / 'inhibitor-active.json', inhibitor(c))
        work.mkdir(parents=True, exist_ok=False)
        (work / 'scratch').mkdir()
        if not c['dummy']:
            verified = reuse_verification(c)
            proposal = ROOT / c['proposal_input']
            if sha(proposal) != c['input_sha256']:
                raise ValueError('Unreviewed scientific/control input change')
            shutil.copyfile(proposal, work / 'input.in')
            shutil.copytree(ROOT / c['package'] / 'pseudo', work / 'pseudo')
            c['input_sha256'] = sha(work / 'input.in'); dump(config_path, c)
            dump(work / 'preparation.json', {'package': verified, 'resources': r, 'time': time.time(),
                 'scientific_change': 'manifest baseline geometry; unchanged 80/600Ry protocol', 'execution_input_change': 'none; max_seconds12948 retained',
                 'scratch_reused': False})
        policy = override(unit)
        (ev / 'runtime-stop-policy.conf').write_text(policy.read_text())
        timeout = 2 if c['dummy'] else 15
        end = a['allocation_start_unix'] + a['stop_seconds']
        for name, when, action in [
            (grace, a['allocation_start_unix'] + a['grace_seconds'], ['/usr/bin/touch', str(work/'scratch'/(PREFIX+'.EXIT'))]),
            (timer, end, ['/usr/bin/systemctl', '--user', 'stop', unit])]:
            dump(ev / (name + '.json'), command(['systemd-run', '--user', '--unit='+name,
                 '--timer-property=AccuracySec=1s', '--on-calendar='+calendar(when), *action]))
            props = properties(name+'.timer', ['ActiveState', 'NextElapseUSecRealtime'])
            epoch = float(command(['date', '-d', props['NextElapseUSecRealtime'], '+%s'])['stdout'])
            if props['ActiveState'] != 'active' or abs(epoch-math.floor(when)) > 1:
                raise ValueError('Absolute timer verification failed')
        runtime = math.floor(a['stop_seconds'] - elapsed(c) + (5 if c['dummy'] else -2))
        if runtime <= 0:
            raise ValueError('Original deadline too close')
        args = ['systemd-run', '--user', '--unit='+unit, '--working-directory='+str(ROOT),
                '-p', 'MemoryMax=11G', '-p', 'MemoryHigh=10G', '-p', 'MemorySwapMax=0',
                '-p', 'TasksMax=96', '-p', 'OOMPolicy=kill', '-p', 'CPUAffinity=0-7',
                '-p', 'MemoryAccounting=yes', '-p', 'IOAccounting=yes',
                '-p', 'RemainAfterExit=yes',
                '-p', 'RuntimeMaxSec='+str(runtime), '-p', 'TimeoutStopSec='+str(timeout)+'s',
                '-p', 'KillMode=control-group', '-p', 'SendSIGKILL=yes', '-p', 'FinalKillSignal=SIGKILL',
                '-p', 'StandardOutput=append:'+str(work/'stdout.log'),
                '-p', 'StandardError=append:'+str(work/'stderr.log'),
                '/usr/bin/python3', str(SCRIPT), '--worker', str(config_path)]
        dump(ev/'worker-launch.json', command(args)); launched = True
        props = properties(unit, ['ControlGroup'])
        cg = Path('/sys/fs/cgroup'+props['ControlGroup']) if props['ControlGroup'] else None
        grace_sent = False
        with (work/'resources.jsonl').open('x') as stream:
            dummy_pause = False
            while properties(unit, ['ActiveState'])['ActiveState'] in ['active', 'activating', 'deactivating']:
                if properties(unit, ['SubState'])['SubState'] == 'exited':
                    break
                if c['dummy'] and (work/'grandchild-pid.json').exists() and not dummy_pause:
                    dump(work/'interruption.json', {'action': 'guardian monitoring paused; independent service/timer continues', 'seconds': 30})
                    time.sleep(30); dummy_pause = True
                    continue
                if cg is None or not cg.exists():
                    break
                rr = resources(); out = (work/'stdout.log').read_text(errors='replace') if (work/'stdout.log').exists() else ''
                err = (work/'stderr.log').read_text(errors='replace') if (work/'stderr.log').exists() else ''
                s = {'time': time.time(), 'allocation_elapsed': elapsed(c),
                     'memory_current': int((cg/'memory.current').read_text()),
                     'memory_peak': int((cg/'memory.peak').read_text()),
                     'swap_current': int((cg/'memory.swap.current').read_text()),
                     'memory_events': read_counter(cg/'memory.events'), 'pids_events': read_counter(cg/'pids.events'),
                     'tasks': int((cg/'pids.current').read_text()),
                     'worker_pids': (cg/'cgroup.procs').read_text().split(),
                     'scratch_bytes': sum(p.stat().st_size for p in (work/'scratch').rglob('*') if p.is_file()),
                     'system_available': rr['available'], 'free_disk': rr['free_disk'],
                     'inhibitor': inhibitor(c), 'AC_online': ac_online(),
                     'negative_pseudocharge_electrons': [float(x.replace('D','E')) for x in re.findall(r'negative rho \(up, down\):\s*([\d.EeDd+-]+)',out)], **output_status(out)}
                max_memory=max(max_memory,s['memory_peak']); max_swap=max(max_swap,s['swap_current'])
                stream.write(json.dumps(s)+'\n'); stream.flush(); dump(work/'status.json',s)
                reason = stop_reason(s)
                if reason: raise RuntimeError(reason)
                if not s['AC_online']: raise RuntimeError('AC_lost')
                if re.search(r'Error in routine|MPI_ABORT|segmentation fault|SIGSEGV|forrtl: severe', out+err, re.I):
                    raise RuntimeError('QE_or_MPI_fatal_error')
                if s['allocation_elapsed'] >= a['stop_seconds']:
                    raise RuntimeError('original_external_deadline')
                if not grace_sent and s['allocation_elapsed'] >= a['grace_seconds']:
                    (work/'scratch'/(PREFIX+'.EXIT')).touch()
                    dump(work/'graceful-stop.json', {'time': time.time(), 'elapsed': elapsed(c),
                         'reason': 'original_graceful_deadline'})
                    grace_sent = True
                time.sleep(.2 if c['dummy'] else 2)
        result['termination_reason'] = 'worker_terminal; see exit status and QE output'
    except BaseException as e:
        result['termination_reason'] = str(e)
    finally:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        dump(ev/'cleanup-entered.json', {'time': time.time(), 'termination_reason': result['termination_reason'], 'cleanup_verified': False})
        try:
            result['inhibitor_before_cleanup'] = inhibitor(c)
        except Exception as exc:
            result['inhibitor_before_cleanup'] = {'error': str(exc)}
        if launched:
            result['service_before_cleanup'] = properties(unit, ['ActiveState','SubState','Result','ExecMainCode','ExecMainStatus',
                 'MemoryPeak','MemorySwapPeak','CPUUsageNSec','IOReadBytes','IOWriteBytes','ExecMainStartTimestamp','ExecMainExitTimestamp'])
            if cg is not None and cg.exists():
                result['final_cgroup'] = {k: (cg/k).read_text() for k in
                    ['memory.peak','memory.swap.current','memory.events','pids.events','cpu.stat','io.stat']}
            result['stop'] = command(['systemctl', '--user', 'stop', unit], check=False)
            result['service'] = properties(unit, ['ActiveState','SubState','Result','ExecMainCode','ExecMainStatus',
                 'MemoryPeak','MemorySwapPeak','CPUUsageNSec','IOReadBytes','IOWriteBytes','ExecMainStartTimestamp','ExecMainExitTimestamp'])
        survivors = [] if cg is None or not cg.exists() else (cg/'cgroup.procs').read_text().split()
        result.update(workers_remaining=survivors, max_sampled_memory_bytes=max_memory, max_sampled_swap_bytes=max_swap,
                      allocation_elapsed=elapsed(c), time=time.time(), allocation_sha256=sha(ROOT/c['allocation_file']))
        if survivors:
            command(['systemctl','--user','kill','--kill-whom=all','--signal=SIGKILL',unit],check=False)
            raise RuntimeError('Cleanup detected remaining workers; evidence retained')
        try:
            result['inhibitor_after_worker_cleanup'] = inhibitor(c)
        except Exception as exc:
            result['inhibitor_after_worker_cleanup'] = {'error': str(exc)}
        for name in [timer, grace]:
            command(['systemctl','--user','stop',name+'.timer'],check=False)
        dump(ev/'journal.json', command(['journalctl','--user','-u',unit,'-u',timer+'.service','-u',grace+'.service','--no-pager'],check=False))
        if policy is not None:
            policy.unlink(); policy.parent.rmdir(); command(['systemctl','--user','daemon-reload'])
        result['runtime_override_removed'] = policy is None or not policy.exists()
        result['authorization_consumed'] = json.loads(config_path.read_text())['authorization_consumed']
        dump(ev/'result.json', result)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--worker'); modes.add_argument('--supervise'); modes.add_argument('--dummy-process')
    parser.add_argument('--role',default='parent'); args=parser.parse_args()
    if args.dummy_process:
        dummy_process(Path(args.dummy_process),args.role)
    else:
        path=Path(args.worker or args.supervise).resolve(); c=json.loads(path.read_text())
        PREFIX = c['manifest_id']
        (worker(c,path) if args.worker else supervise(c,path))
