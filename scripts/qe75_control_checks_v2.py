"""Non-QE tests of temporary inhibition, fixed deadlines and process cleanup.

This script can launch only its own inert Python dummy workloads, never QE.
No scientific allocation or authorization is created or changed.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence/qe75-control-checks-v2'
WHO = 'MOF-QE-non-QE-control-checks-v2'
SCRIPT = str(Path(__file__).resolve())


def dump(p, data):
    p.write_text(json.dumps(data, indent=2) + '\n')


def call(command):
    p = subprocess.run(command, capture_output=True, text=True, timeout=20)
    return {'command': command, 'code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}


def inhibitors():
    return json.loads(subprocess.check_output(
        ['systemd-inhibit', '--list', '--json=short', '--no-pager'], text=True))


def own_inhibitor():
    rows = [r for r in inhibitors() if r['who'] == WHO]
    assert len(rows) == 1 and rows[0]['mode'] == 'block'
    assert {'sleep', 'idle'} <= set(rows[0]['what'].split(':'))
    assert Path('/proc', str(rows[0]['pid'])).exists()
    return rows[0]


def hold():
    # Independent bounded owner survives loss of the checking CLI. Tests last <60s.
    deadline = time.monotonic() + 120
    while not (EVIDENCE/'release-inhibitor').exists() and time.monotonic() < deadline:
        time.sleep(.1)


def dummy(directory, role):
    p = Path(directory)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    dump(p / (role + '-pid.json'), {'pid': os.getpid(), 'start_ticks': Path('/proc/self/stat').read_text().split()[21],
                                  'role': role, 'unix_time': time.time()})
    if role == 'parent':
        cg = Path('/sys/fs/cgroup') / Path('/proc/self/cgroup').read_text().strip().split('::')[1].lstrip('/')
        dump(p/'actual-limits.json', {k:(cg/k).read_text().strip() for k in
             ['memory.max','memory.high','memory.swap.max','memory.oom.group','pids.max']})
        subprocess.Popen(['/usr/bin/python3', SCRIPT, '--dummy', directory, '--role', 'child'], start_new_session=True)
    elif role == 'child':
        subprocess.Popen(['/usr/bin/python3', SCRIPT, '--dummy', directory, '--role', 'grandchild'], start_new_session=True)
    with (p/(role+'-partial.log')).open('x') as f:
        while True:
            f.write(str(time.time())+'\n'); f.flush()
            time.sleep(.1)


def remaining(directory):
    result = []
    for p in directory.glob('*-pid.json'):
        old = json.loads(p.read_text())
        stat = Path('/proc',str(old['pid']),'stat')
        if stat.exists():
            now = stat.read_text().split()
            if now[21] == old['start_ticks']:
                result.append({'pid':old['pid'], 'state':now[2]})
    return result


def case(name, interrupt=False, simulate_late_resume=False):
    d = EVIDENCE/name; d.mkdir()
    unit = 'qe75-controlcheck-v2-' + name
    start = time.time(); deadline = start + 12
    receipt = {'start':start,'deadline':deadline,'stop_at':deadline-3,'scope':'NON-QE dummy only'}
    dump(d/'allocation.json',receipt)
    original = (d/'allocation.json').read_bytes()
    stamp = datetime.fromtimestamp(int(deadline-3), timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    timer = ['systemd-run','--user','--unit='+unit+'-deadline','--on-calendar='+stamp,
             '--timer-property=AccuracySec=100ms','/usr/bin/systemctl','--user','stop',unit+'.service']
    dump(d/'timer-launch.json',call(timer))
    launch = ['systemd-run','--user','--unit='+unit,'-p','MemoryMax=11G','-p','MemoryHigh=10G',
              '-p','MemorySwapMax=0','-p','OOMPolicy=kill','-p','TasksMax=96','-p','CPUAffinity=0-7',
              '-p','RuntimeMaxSec=9s','-p','TimeoutStopSec=2s','-p','KillMode=control-group',
              '-p','SendSIGKILL=yes','-p','FinalKillSignal=SIGKILL','-p','TimeoutStopFailureMode=kill','/usr/bin/python3',SCRIPT,'--dummy',str(d),'--role','parent']
    dump(d/'service-launch.json',call(launch))
    checks=[]; changed=False
    try:
        while time.time() < deadline+3:
            checks.append({'time':time.time(),'inhibitor':own_inhibitor()})
            pidfiles=list(d.glob('*-pid.json'))
            if len(pidfiles)==3 and not changed and (interrupt or simulate_late_resume):
                parent=json.loads((d/'parent-pid.json').read_text())['pid']
                if interrupt:
                    # Stop the controller's execution without stopping the host.
                    os.kill(parent,signal.SIGSTOP)
                    dump(d/'interruption.json',{'signal':'SIGSTOP','pid':parent,'time':time.time(),
                                               'deadline_unchanged':deadline})
                else:
                    # Inject only a guard-clock value, never change the system clock.
                    observed_after_resume=deadline+1
                    assert observed_after_resume >= receipt['deadline']
                    dump(d/'late-resume-guard.json',{'observed_clock':observed_after_resume,
                         'fixed_deadline':receipt['deadline'],'action':'stop existing entire cgroup; no continuation'})
                    dump(d/'late-resume-stop.json',call(['systemctl','--user','stop',unit+'.service']))
                changed=True
            state=call(['systemctl','--user','show',unit+'.service','-p','ActiveState','--value'])
            if state['stdout'].strip() in ['inactive','failed']:
                break
            time.sleep(.15)
        dump(d/'terminal-service.json',call(['systemctl','--user','show',unit+'.service',
            '-p','ActiveState','-p','SubState','-p','Result','-p','ControlGroup','-p','ExecMainStatus']))
    finally:
        dump(d/'cleanup-stop.json',call(['systemctl','--user','stop',unit+'.service',unit+'-deadline.timer']))
    # Inhibitor owner is still alive through cleanup and worker verification.
    checks.append({'time':time.time(),'inhibitor':own_inhibitor(),'stage':'after cleanup'})
    time.sleep(.3)
    survivors=remaining(d)
    assert not survivors, survivors
    assert len(list(d.glob('*-pid.json')))==3
    assert all(p.stat().st_size>0 for p in d.glob('*-partial.log'))
    assert (d/'allocation.json').read_bytes()==original
    actual=json.loads((d/'actual-limits.json').read_text())
    assert actual=={'memory.max':str(11*2**30),'memory.high':str(10*2**30),
                    'memory.swap.max':'0','memory.oom.group':'1','pids.max':'96'}
    elapsed=time.time()-start
    assert elapsed <= 12, 'Dummy exceeded original total deadline'
    # A resumed controller reads the SAME receipt; it may not create a new one.
    resume_time=max(time.time(),deadline+1)
    assert resume_time >= json.loads((d/'allocation.json').read_text())['deadline']
    dump(d/'result.json',{'passed':True,'elapsed':elapsed,'survivors':survivors,
          'original_receipt_sha256':hashlib.sha256(original).hexdigest(),
          'resume_after_deadline':'REFUSED; no workers spawned; original receipt retained',
          'partial_outputs':3,'inhibitor_covered_cleanup':True,'inhibitor_samples':checks})


def suite():
    EVIDENCE.mkdir(exist_ok=False)
    dump(EVIDENCE/'before.json',{'inhibitors':inhibitors(), 'unix_time':time.time(),
         'AC':{str(p):p.read_text().strip() for p in Path('/sys/class/power_supply').glob('*/online')}})
    holder=None; result={'passed':False,'scientific_jobs_launched':0,'system_suspend_requested':False}
    try:
        holder=subprocess.Popen(['systemd-inhibit','--no-ask-password','--what=sleep:idle','--mode=block',
            '--who='+WHO,'--why=Bounded non-QE control tests and cleanup','/usr/bin/python3',SCRIPT,'--hold'],
            stdout=(EVIDENCE/'inhibitor.stdout').open('x'),stderr=(EVIDENCE/'inhibitor.stderr').open('x'),start_new_session=True)
        for _ in range(30):
            if holder.poll() is not None:raise RuntimeError('Inhibitor acquisition failed')
            if any(r['who']==WHO for r in inhibitors()):break
            time.sleep(.1)
        dump(EVIDENCE/'inhibitor-active.json',own_inhibitor())
        case('deadline')
        case('interrupted',interrupt=True)
        case('late-resume',simulate_late_resume=True)
        # Explicit failure path: finally must clean resources then release owner.
        try:
            raise RuntimeError('injected post-workload failure')
        except RuntimeError as exc:
            result['injected_failure_handled']=str(exc)
        result['passed']=True
    except BaseException as exc:
        result['error']=repr(exc)
    finally:
        # Own units only; no blanket process kill or alteration of power settings.
        for name in ['deadline','interrupted','late-resume']:
            unit='qe75-controlcheck-v2-'+name
            call(['systemctl','--user','stop',unit+'.service',unit+'-deadline.timer'])
        alive=[p for d in EVIDENCE.iterdir() if d.is_dir() for p in remaining(d)]
        result['remaining_dummy_workers']=alive
        if alive:result['passed']=False
        (EVIDENCE/'release-inhibitor').touch()
        if holder is not None: holder.wait(timeout=5)
        after=inhibitors();result['inhibitor_released']=not any(r['who']==WHO for r in after)
        result['passed']=result['passed'] and result['inhibitor_released'] and not alive
        dump(EVIDENCE/'after.json',{'inhibitors':after,'unix_time':time.time()})
        dump(EVIDENCE/'result.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--hold',action='store_true');p.add_argument('--dummy');p.add_argument('--role')
    a=p.parse_args()
    if a.hold:hold()
    elif a.dummy:dummy(a.dummy,a.role)
    else:suite()
