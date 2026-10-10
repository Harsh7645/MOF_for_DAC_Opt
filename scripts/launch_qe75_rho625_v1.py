"""Finish the interrupted non-QE controller check, then launch ONE approved probe.

Fixed run02 allocation predates this preparation. Never renew it or retry QE.
"""
import json
import os
from pathlib import Path
import subprocess
import time

from qe75_fedora_v1 import ROOT, sha
from qe75_rho625_v1 import dump, command, stop_reason, GIB, SCRIPT

EV = ROOT/'evidence/qe75-rho625-run02'
CONFIG = ROOT/'configs/qe75-rho625-v2.json'
DUMMY = ROOT/'evidence/qe75-rho625-controller-dummy02'


def anchor(a):
    delta = time.time()-a['allocation_start_unix']
    return {'start_boottime_host': time.clock_gettime(time.CLOCK_BOOTTIME)-delta,
            'start_monotonic_host': time.monotonic()-delta,
            'original_start_unix': a['allocation_start_unix']}


def run_guard(c, config):
    a=json.loads(Path(c['allocation_file']).read_text())
    remaining=int(a['deadline_unix']-time.time())
    if remaining < (35 if c['dummy'] else 180):
        raise ValueError('Insufficient unchanged allocation remaining')
    unit=c['unit'].replace('.service','-guardian.service')
    runtime=remaining-(3 if c['dummy'] else 45)
    args=['systemd-run','--user','--wait','--pipe','--unit='+unit,
          '--working-directory='+str(ROOT),'-p','RuntimeMaxSec='+str(runtime),
          '-p','TimeoutStopSec='+('2s' if c['dummy'] else '30s'),
          '/usr/bin/systemd-inhibit','--no-ask-password','--what=sleep:idle','--mode=block',
          '--who='+c['inhibitor_who'],'--why=Bounded QE diagnostic controller and worker cleanup',
          '/usr/bin/python3',str(SCRIPT),'--supervise',str(config)]
    ev=Path(c['evidence_root'])
    dump(ev/'guardian-launch.json',{'command':args,'time':time.time()})
    with (ev/'guardian-console.log').open('x') as log:
        rc=subprocess.run(args,stdout=log,stderr=log).returncode
    dump(ev/'guardian-exit.json',{'returncode':rc,'time':time.time()})
    rows=json.loads(command(['systemd-inhibit','--list','--json=short','--no-pager'])['stdout'])
    remaining_owners=[r for r in rows if r['who']==c['inhibitor_who']]
    dump(ev/'inhibitor-release.json',{'remaining':remaining_owners,'time':time.time()})
    if remaining_owners:
        raise ValueError('Task inhibitor unexpectedly retained')
    return json.loads((ev/'result.json').read_text())


def main():
    with (EV/'launcher-entered.json').open('x') as f:
        json.dump({'time':time.time(),'script_sha256':sha(Path(__file__))},f)
    a=json.loads((EV/'allocation.json').read_text())
    dump(EV/'host-clock-anchor.json',anchor(a))
    c=json.loads(CONFIG.read_text())
    DUMMY.mkdir(exist_ok=False)
    da={'allocation_start_unix':time.time(),'total_seconds':40,'grace_seconds':20,'stop_seconds':25,'kill_seconds':27}
    da['deadline_unix']=da['allocation_start_unix']+40
    dump(DUMMY/'allocation.json',da); dump(DUMMY/'host-clock-anchor.json',anchor(da))
    d=dict(c)
    d.update(dummy=True,attempt_approved=False,authorization_consumed=False,
             allocation_file=str(DUMMY/'allocation.json'),host_clock_file=str(DUMMY/'host-clock-anchor.json'),
             allocation_sha256=sha(DUMMY/'allocation.json'),work_root='local/qe75-rho625-v1/dummy02',
             evidence_root=str(DUMMY),unit='qe75-rho625-dummy02.service',inhibitor_who='MOF-QE-rho625-dummy02')
    dump(DUMMY/'config.json',d)
    test=run_guard(d,DUMMY/'config.json')
    dw=ROOT/d['work_root']
    assert test['workers_remaining']==[] and test['runtime_override_removed']
    assert test['allocation_sha256']==d['allocation_sha256']
    assert test['allocation_elapsed']<40 and not test['authorization_consumed']
    assert test['service']['ExecMainStatus']=='9',test
    assert (dw/'interruption.json').exists() and (dw/'scratch'/('uio66_110111_H2O_s28_f0.010_complex.EXIT')).exists()
    for role in ['parent','child','grandchild']:
        p=json.loads((dw/(role+'-pid.json')).read_text());stat=Path('/proc',str(p['pid']),'stat')
        assert not stat.exists() or stat.read_text().split()[21]!=p['start_ticks']
        assert (dw/(role+'-partial.log')).stat().st_size>0
    base={'swap_current':0,'memory_events':{},'pids_events':{},'memory_current':9*GIB,
          'system_available':3*GIB,'scratch_bytes':0,'free_disk':100*GIB}
    assert stop_reason(base) is None
    assert stop_reason(dict(base,memory_events={'high':1}))=='resource_limit_event'
    assert stop_reason(dict(base,swap_current=1))=='resource_limit_event'
    assert stop_reason(dict(base,pids_events={'max':1}))=='resource_limit_event'
    review={'passed':True,'controller_sha256':sha(SCRIPT),'dummy_result':str(DUMMY/'result.json'),
            'dummy_elapsed':test['allocation_elapsed'],'high_memory_guard':'any memory.high event stops whole worker cgroup',
            'fixed_deadline_and_cleanup':True,'three_separate_process_groups_gone':True,
            'partial_outputs_retained':True,'inhibitor_released':True,'time':time.time(),
            'reused_controls':'evidence/qe75-control-checks-v3/; unchanged thresholds and stop-policy override',
            'controller_changes':'reuse full-package evidence, runtime executable/UPF pins; retain successful-worker accounting; guard empty cgroup path'}
    dump(EV/'controller-review.json',review)
    c.update(controller_reviewed_and_dummy_passed=True,controller_review_sha256=sha(EV/'controller-review.json'))
    dump(CONFIG,c)
    # Final resource, AC, jobs and inhibitor checks occur inside the guarded worker,
    # immediately before its exclusive launch marker and exec. No confirmation gap.
    result=run_guard(c,CONFIG)
    dump(EV/'launcher-final.json',{'result':result,'time':time.time(),'total_elapsed':time.time()-a['allocation_start_unix']})
    print(json.dumps({'termination':result['termination_reason'],'consumed':result['authorization_consumed'],
                      'elapsed':result['allocation_elapsed']},indent=2))


if __name__=='__main__':
    main()
