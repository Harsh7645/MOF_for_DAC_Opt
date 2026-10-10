"""Collect terminal evidence and portable review package; never starts a worker."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import zipfile
from qe75_fedora_v1 import ROOT,sha
from assess_qe75_completion_v5 import assess


def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')


def call(args):
    r=subprocess.run(args,capture_output=True,text=True,timeout=25)
    return {'command':args,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}


def main():
    config=ROOT/'configs/qe75-fedora-completion-v5.json';c=json.loads(config.read_text())
    ev=Path(c['evidence_root']);root_ev=ROOT/'evidence/qe75-fedora-completion-v5';work=ROOT/c['work_root']
    a=json.loads(Path(c['allocation_file']).read_text())
    with (ev/'finalizer-entered.json').open('x') as f:json.dump({'time':time.time(),'script_sha256':sha(Path(__file__))},f)
    # The existing guardian/timers enforce stopping; this collector only waits.
    while not (ev/'inhibitor-release.json').exists():
        if time.time()>a['deadline_unix']:
            dump(ev/'finalizer-blocked.json',{'reason':'Original allocation expired without release receipt; do not restart','time':time.time()})
            return
        time.sleep(2)
    units=[c['unit'],c['unit'].replace('.service','-guardian.service'),
           c['unit'].replace('.service','-grace.timer'),c['unit'].replace('.service','-deadline.timer')]
    rows=json.loads(call(['systemd-inhibit','--list','--json=short','--no-pager'])['stdout'])
    since=datetime.fromtimestamp(a['allocation_start_unix'],timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    post={'time':time.time(),'allocation_elapsed':time.time()-a['allocation_start_unix'],
          'workers':call(['pgrep','-a','-x','pw.x|mpirun|prterun|orted']),
          'task_inhibitors_remaining':[r for r in rows if r['who']==c['inhibitor_who']],
          'units':{u:call(['systemctl','--user','show',u,'-p','ActiveState','-p','SubState','-p','ControlGroup']) for u in units},
          'runtime_override_exists':(Path('/run/user/1000/systemd/user')/(c['unit']+'.d')).exists(),
          'AC':{str(p):p.read_text().strip() for p in Path('/sys/class/power_supply').glob('*/online')},
          'meminfo':Path('/proc/meminfo').read_text(),'persistent_free_bytes':shutil.disk_usage(ROOT).free,
          'suspend_journal':call(['journalctl','--since',since,'-u','systemd-suspend.service','-u','systemd-hibernate.service','-u','systemd-suspend-then-hibernate.service','--no-pager'])}
    dump(ev/'postflight.json',post)
    result=assess()
    result['postflight_cleanup_verified']=post['workers']['returncode']==1 and not post['task_inhibitors_remaining'] and not post['runtime_override_exists']
    result['allocation_wall_budget_met']=post['allocation_elapsed']<=14400
    if not result['postflight_cleanup_verified'] or not result['allocation_wall_budget_met']:
        result['ready_for_independent_assessment']=False
        result['accepted_converged_SCF_energy']=False
    dump(ev/'assessment.json',result)
    c=json.loads(config.read_text());c.update(preparation_terminal=True,result=str((ev/'assessment.json').relative_to(ROOT)),
      note='TERMINAL; authorization consumed. See assessment for convergence and force verification. No automatic continuation/retry/secondgeometry.')
    dump(config,c)
    dump(ev/'raw-file-hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in sorted(work.rglob('*')) if p.is_file()})
    package=ROOT/'artifacts/phase3/uio66_qe600_completion_v5_review';package.mkdir(exist_ok=False)
    shutil.copytree(work,package/'run')
    shutil.copytree(root_ev,package/'evidence')
    shutil.copyfile(ROOT/'artifacts/phase3/uio66_qe_review_600_625_v1.zip',package/'paired-diagnostic-review.zip')
    shutil.copyfile(config,package/'execution-config.json')
    code=package/'controller';code.mkdir()
    for name in ['qe75_completion_v5.py','launch_qe75_completion_v5.py','resume_qe75_completion_v5.py','assess_qe75_completion_v5.py','finalize_qe75_completion_v5.py']:
        shutil.copyfile(ROOT/'scripts'/name,code/name)
    report=f'''# First frozen water-complex600Ry attempt — review package

Ready for independent assessment: {result['ready_for_independent_assessment']}
Actual text SCF convergence: {result['output_summary']['SCF_convergence_reported']}
Completed SCF error reports: {result['output_summary']['completed_iterations']}
Validation failure: {result['validation_failure']}
Peak memory: {result['peak_GiB']:.6f} GiB; peak sampled swap: {result['maximum_swap_bytes']} bytes.
Memory events: {result['memory_events']}
Launch through cleanup: {result['run_to_cleanup_seconds']:.3f}s.
Allocation through cleanup: {result['allocation_to_worker_cleanup_seconds']:.3f}s.
Final negative pseudocharge: {result['final_negative_pseudocharge_electrons']} electrons.
Force findings: {json.dumps(result['checks'].get('forces',{}))}
Text/XML energy checks: {json.dumps(result['checks'].get('energy',{}))}
Cleanup verified: {result['postflight_cleanup_verified']}; wall budget met: {result['allocation_wall_budget_met']}.

Protocol: ONE80/600Ry first-geometry cleanSCF,127frozenatoms/522electrons,
PBE-D3BJ2body,neutralnspin1,fixedoccupations,conv_thr1e-8Ry,mixing_beta0.3,
CG/mixinghistory4/diskhigh,4physicalcores,11GiBhard/10GiBhigh/zero swap/96tasks.
All earlier evidence preserved;625checkpoint not reused. No secondgeometry run.
SCF convergence does not establish cutoff/kpoint convergence,physicalaccuracy,
UMAaccuracy or Phase3completion. Large forces on frozen structures are findings,
not automatic failure. No unconverged energy is accepted scientifically.

Rawinput,completeoutputs,XML/checkpoints/pseudopotentials/accounting:run/.
Structured independent checks:evidence/launch02/assessment.json.
Verified prior evidence versus reviewer provisional interpretation:paired-diagnostic-review.zip.
Checksums:SHA256SUMS.json. No external message or publication was sent.
'''
    (package/'REVIEW_REPORT.md').write_text(report)
    dump(package/'SHA256SUMS.json',{str(p.relative_to(package)):sha(p) for p in sorted(package.rglob('*')) if p.is_file()})
    zpath=package.with_suffix('.zip')
    with zipfile.ZipFile(zpath,'x',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for p in sorted(package.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(package))
    dump(ev/'portable-review-receipt.json',{'archive':str(zpath.relative_to(ROOT)),'sha256':sha(zpath),
         'size_bytes':zpath.stat().st_size,'time':time.time(),'allocation_elapsed':time.time()-a['allocation_start_unix']})
    dump(ev/'finalization-complete.json',{'time':time.time(),'elapsed':time.time()-a['allocation_start_unix'],
         'ready_for_independent_assessment':result['ready_for_independent_assessment'],'no_additional_calculation_started':True})


if __name__=='__main__':main()
