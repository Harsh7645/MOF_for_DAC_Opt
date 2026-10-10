"""Authorized 12-job sequential baseline; exclusive invocation, immutable deadlines, no retries."""
import argparse,hashlib,json,math,os,shutil,subprocess,time,traceback
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from qe75_fedora_v1 import ROOT,sha
import qe75_baseline12_worker_v1 as ctrl
import launch_qe75_rho625_v1 as launch
from assess_qe75_baseline12_v1 import assess
from qe75_feasibility_v2 import resources,check_budget
from run_qe_water_pilot import RY_EV,BOHR_A
E=ROOT/'evidence/qe75-baseline12-v1';D=ROOT/'plans/qe75-baseline12-v1';J=D/'jobs.json'
dump=ctrl.dump

def batch_elapsed():
 b=json.loads((E/'batch-allocation.json').read_text())
 return max(time.time()-b['allocation_start_unix'],time.clock_gettime(time.CLOCK_BOOTTIME)-b['start_boottime'],time.monotonic()-b['start_monotonic'])

def newconfig(job,ev,start,total,dummy=False):
 ev.mkdir(exist_ok=False)
 a={'allocation_start_unix':start,'deadline_unix':start+total,'total_seconds':total,'grace_seconds':20 if dummy else total-1200,'stop_seconds':25 if dummy else total-315,'kill_seconds':27 if dummy else total-300}
 dump(ev/'allocation.json',a);dump(ev/'host-clock-anchor.json',launch.anchor(a))
 c=json.loads((ROOT/'configs/qe75-second-v7.json').read_text())
 for k in ['result','independent_audit','preparation_terminal']:c.pop(k,None)
 c.update(dummy=dummy,attempt_approved=not dummy,authorization_consumed=False,
   work_root=job['work_root'],evidence_root=str(ev),unit='qe75-baseline12-'+('dummy' if dummy else f"job{job['order']:02d}")+'.service',
   inhibitor_who='MOF-QE-baseline12-'+('dummy' if dummy else f"job{job['order']:02d}"),
   allocation_file=str(ev/'allocation.json'),allocation_sha256=sha(ev/'allocation.json'),host_clock_file=str(ev/'host-clock-anchor.json'),
   manifest_id=job['manifest_id'],proposal_input=job['input'],input_sha256=job['input_sha256'],
   expected_atoms=job['nat'],expected_electrons=job['expected_electrons'],job_order=job['order'],
   batch_allocation=str(E/'batch-allocation.json'),batch_allocation_sha256=sha(E/'batch-allocation.json'),jobs_file=str(J),jobs_sha256=sha(J),
   note='Authorized one attempt for this manifest baseline job only; no retry or settings change',
   controller_reviewed_and_dummy_passed=False)
 if not dummy:
  shutil.copyfile(E/'controller-review.json',ev/'controller-review.json');c['controller_review_sha256']=sha(ev/'controller-review.json');c['controller_reviewed_and_dummy_passed']=True
 dump(ev/'config.json',c);return c

def cleanup_check(c):
 units=[c['unit'],c['unit'].replace('.service','-guardian.service'),c['unit'].replace('.service','-grace.timer'),c['unit'].replace('.service','-deadline.timer')]
 workers=ctrl.command(['pgrep','-a','-x','pw.x|mpirun|prterun|orted'],False)
 rows=json.loads(ctrl.command(['systemd-inhibit','--list','--json=short','--no-pager'])['stdout'])
 own=[r for r in rows if r['who']==c['inhibitor_who']]
 states={u:ctrl.properties(u,['ActiveState','SubState','ControlGroup']) for u in units}
 override=Path(os.environ['XDG_RUNTIME_DIR'])/'systemd/user'/(c['unit']+'.d')
 p={'time':time.time(),'workers':workers,'inhibitors_remaining':own,'units':states,'runtime_override_exists':override.exists()}
 dump(Path(c['evidence_root'])/'postflight.json',p)
 assert workers['returncode']==1 and not own and not override.exists(),'Cleanup incomplete'
 assert all(x.get('ActiveState') in ('inactive','failed') and not x.get('ControlGroup') for x in states.values()),'Task unit active'
 return p

def aggregate(ledger):
 results={}
 first=json.loads((ROOT/'evidence/qe75-first-independent-review-v6/review.json').read_text());second=json.loads((ROOT/'evidence/qe75-second-v7/independent-audit-v2.json').read_text())
 ids=ledger['completed_previous_water_complexes']
 results[ids[0]]={'energy_Ha':first['energy_XML_Ha'],'source':'evidence/qe75-first-independent-review-v6/review.json'}
 results[ids[1]]={'energy_Ha':second['energy_Ha'],'source':'evidence/qe75-second-v7/independent-audit-v2.json'}
 for j in ledger['jobs']:
  if j['status']=='completed':
   a=json.loads((ROOT/j['evidence_root']/'assessment.json').read_text());results[j['manifest_id']]={'energy_Ha':a['checks']['energy']['XML_Ha'],'source':j['evidence_root']+'/assessment.json','forces':a['checks']['forces']}
 m=json.loads((ROOT/'artifacts/phase3/uio66_frozen_dft_v2_qe75_fedora_verified01/manifest.json').read_text())
 pairs=[('uio66_110111_H2O_s28_f0.010','uio66_110111_H2O_s28_f0.005'),('uio66_110111_CO2_s7_f0.020','uio66_110111_CO2_s7_f0.010'),('uio66_110111_CO2_s7_f0.010','uio66_110111_CO2_s7_f0.005'),('uio66_000000_CO2_s16_f0.010','uio66_000000_CO2_s16_f0.005')]
 differences=[]
 for a,b in pairs:
  row={'first':a,'second':b,'provisional':True}
  for kind in ('complex','host'):
   x,y=a+'_'+kind,b+'_'+kind
   if x in results and y in results:
    d=(results[y]['energy_Ha']-results[x]['energy_Ha'])*2*RY_EV;row['DFT_delta_'+kind+'_eV']=d
    ux,uy=m['components'][x]['uma'],m['components'][y]['uma']
    if ux and uy and ux.get('energy_eV') is not None and uy.get('energy_eV') is not None:
     ud=uy['energy_eV']-ux['energy_eV'];row['UMA_delta_'+kind+'_eV']=ud;row['DFT_minus_UMA_delta_'+kind+'_eV']=d-ud
  if 'DFT_delta_host_eV' in row and 'DFT_delta_complex_eV' in row:row['DFT_delta_guest_associated_eV']=row['DFT_delta_complex_eV']-row['DFT_delta_host_eV']
  differences.append(row)
 force_data={}
 for id in results:
  if id==ids[0]:work=ROOT/'local/qe75-fedora-completion-v5/run01'
  elif id==ids[1]:work=ROOT/'local/qe75-second-v7/run01'
  else:work=ROOT/next(j['work_root'] for j in ledger['jobs'] if j['manifest_id']==id)
  tree=ET.parse(work/'scratch'/(id+'.save')/'data-file-schema.xml').getroot()
  for node in tree.iter():node.tag=node.tag.split('}')[-1]
  fs=[[float(v)*2*RY_EV/BOHR_A for v in line.split()] for line in tree.findtext('output/forces').splitlines() if line.strip()]
  force_data[id]=fs
 def stats(vectors):
  norms=[math.sqrt(sum(x*x for x in f)) for f in vectors]
  return {'max_vector_norm_eV_A':max(norms),'RMS_vector_norm_eV_A':math.sqrt(sum(v*v for v in norms)/len(norms)),'max_absolute_component_eV_A':max(abs(x) for f in vectors for x in f)}
 fc={'units':'eV/Angstrom','mapping':'Per-component manifest source_atom_indices; no spatial remapping','provisional':True,'large_frozen_forces_not_automatic_failure':True,'per_geometry':{},'between_checkpoints':[]}
 for id,fs in force_data.items():
  comp=m['components'][id];pose=next(p for p in m['poses'] if p['id']==comp['pose']);mapping=comp['source_atom_indices'];u=comp['uma']
  row={'DFT_force_statistics':stats(fs),'source_atom_indices':mapping,'groups':{}}
  for name,indices in pose['groups'].items():
   group=[f for i,f in zip(mapping,fs) if i in indices]
   if group:row['groups'][name]=stats(group)
  if u and u.get('forces_eV_A') is not None:
   uf=u['forces_eV_A'];assert len(uf)==len(fs)
   diff=[[a-b for a,b in zip(f,g)] for f,g in zip(fs,uf)]
   row['DFT_minus_archived_UMA_components']=diff;row['DFT_minus_UMA_statistics']=stats(diff)
  fc['per_geometry'][id]=row
 for a,b in pairs:
  for kind in ('complex','host'):
   x,y=a+'_'+kind,b+'_'+kind
   if x in force_data and y in force_data:
    assert m['components'][x]['source_atom_indices']==m['components'][y]['source_atom_indices']
    diff=[[a-b for a,b in zip(f,g)] for f,g in zip(force_data[y],force_data[x])]
    fc['between_checkpoints'].append({'first':x,'second':y,'second_minus_first_components':diff,'statistics':stats(diff),'interpretation':'Different frozen geometries at same settings; not a numerical cutoff-convergence measure'})
 dump(E/'force-comparisons.json',fc)
 dump(E/'comparisons.json',{'accepted_converged_results':results,'differences':differences,'limitations':'80/600 Gamma frozen single points; cutoff/grid/wavefunction/physical accuracy unresolved. Guest-associated differences include deformation/interactions and are not adsorption energies. Missing UMA hosts remain missing. Phase3 incomplete.'})

def progress(ledger):
 ledger['updated_UTC']=datetime.now(timezone.utc).isoformat();ledger['batch_elapsed_seconds']=batch_elapsed();dump(E/'progress.json',ledger)
 lines=['# Authorized remaining baseline batch v1','',f"Status: **{ledger['status']}**. Elapsed {ledger['batch_elapsed_seconds']/3600:.3f} h of immutable 48 h.",'','|Order|Manifest ID|State|Runtime through cleanup (s)|Peak GiB|Evidence|','|---|---|---|---:|---:|---|']
 for j in ledger['jobs']:lines.append(f"|{j['order']}|`{j['manifest_id']}`|{j['status']}|{j.get('runtime_s','')}|{j.get('peak_GiB','')}|`{j['evidence_root']}`|")
 lines+=['',f"Blocker: {ledger.get('blocker','none')}",'','Four physical cores, 11-GiB hard / 10-GiB high, zero job swap, 96 tasks. One attempt per manifest ID. Fixed per-job and batch deadlines; no retries. Two completed water complexes excluded. Each pending launch requires fresh AC, >=12-GiB available RAM, disk, workers and inhibitor checks. Cutoff/physical accuracy and Phase 3 unresolved.','', 'Raw outputs/checkpoints: `local/qe75-baseline12-v1/jobNN/run01/`. Comparisons: `evidence/qe75-baseline12-v1/comparisons.json`.']
 (ROOT/'docs/UIO66_QE75_BASELINE12_V1_PROGRESS.md').write_text('\n'.join(lines)+'\n')
 marker='<!-- END BASELINE12 LIVE STATUS -->'
 done=sum(j['status']=='completed' for j in ledger['jobs'])
 active=[j['manifest_id'] for j in ledger['jobs'] if j['status']=='active']
 head=('LATEST 2026-10-09: AUTHORIZED 12-job80/600 baseline batch v1 '+ledger['status'].upper()+'.\n'
       f'Completed {done}/12; active {active}. Two previous water complexes excluded.\n'
       'Read docs/UIO66_QE75_BASELINE12_V1_PROGRESS.md and evidence/qe75-baseline12-v1/progress.json.\n'
       'ONE attempt/job,4h/jobinclprepcleanup,48himmutablebatch;sequential4cores/11hard10high/zeroswap/96tasks.\n'
       'Controller run_qe75_baseline12_v1.py is exclusively entered; do not relaunch or reset allocations.\n'
       'If active,monitor existing qe75-baseline12-batch.service only. If stopped,report blocker,no automatic retry.\n'
       f'Blocker: {ledger.get("blocker","none")}. Pending IDs retain status; no extra calculations.\n'
       'Raw local/qe75-baseline12-v1/;evidence evidence/qe75-baseline12-v1/;same80/600science.\n'
       '750Ry checks NOT authorized;no limitsincrease/relaxation/UMA/refit. Phase3/cutoff/physicalaccuracy unresolved.\n'+marker+'\n\n')
 for name in ['docs/UIO66_QE75_FEDORA_HANDOFF.md','AGENTS.md','MODEL_HANDOFF.md','.planning/STATE.md']:
  path=ROOT/name;old=path.read_text()
  if marker in old:old=old.split(marker,1)[1].lstrip('\n')
  path.write_text(head+old)


def dummy():
 job=dict(json.loads(J.read_text())[0]);job['work_root']='local/qe75-baseline12-v1/dummy01'
 ev=E/'dummy01';c=newconfig(job,ev,time.time(),40,True);launch.SCRIPT=ctrl.SCRIPT
 r=launch.run_guard(c,ev/'config.json');cleanup_check(c);w=ROOT/c['work_root']
 assert not r['workers_remaining'] and r['runtime_override_removed'] and r['allocation_elapsed']<40
 assert r['service']['ExecMainStatus']=='9' and not r['authorization_consumed']
 assert (w/'scratch'/(job['manifest_id']+'.EXIT')).exists() and (w/'interruption.json').exists()
 for role in ('parent','child','grandchild'):
  p=json.loads((w/(role+'-pid.json')).read_text());f=Path('/proc',str(p['pid']),'stat')
  assert not f.exists() or f.read_text().split()[21]!=p['start_ticks']
  assert (w/(role+'-partial.log')).stat().st_size>0
 dump(E/'controller-review.json',{'passed':True,'controller_sha256':sha(ctrl.SCRIPT),'jobs_sha256':sha(J),'dummy_result':str((ev/'result.json').relative_to(ROOT)),'dynamic_prefix_EXIT_verified':True,'process_groups_gone':True,'partials_retained':True,'original_deadline_unchanged':True,'inhibitor_cleanup_verified':True,'unchanged_controls_reused':'v7 verified controller plus rho625 dummy02/control checks v3; 11/10/0/96 and physical cores unchanged','changes':'Pinned manifest target/input and immutable batch receipt gate only; sequential coordinator and generic atom/electron assessor','dummy_elapsed_s':r['allocation_elapsed']})
 print('Changed target/deadline adapter dummy PASS; no QE invoked',flush=True)

def run():
 with (E/'batch-entered.json').open('x') as f:json.dump({'time':time.time(),'script_sha256':sha(Path(__file__))},f)
 ledger=json.loads((E/'progress.json').read_text());ba=json.loads((E/'batch-allocation.json').read_text());current=None
 try:
  assert json.loads((E/'controller-review.json').read_text())['controller_sha256']==sha(ctrl.SCRIPT)
  launch.SCRIPT=ctrl.SCRIPT
  for job in ledger['jobs']:
   current=job;assert job['status']=='pending' and job['attempts']==0
   assert batch_elapsed()<ba['total_seconds']-1800,'Batch deadline/reserve reached'
   if not job['feasibility_pass']:raise ValueError('Per-job memory feasibility failed')
   start=ba['allocation_start_unix'] if job['order']==1 else time.time()
   total=min(14400,ba['deadline_unix']-start)
   ev=ROOT/job['evidence_root'];c=newconfig(job,ev,start,total)
   ctrl.PREFIX=job['manifest_id'];ctrl.fresh(c);ctrl.reuse_verification(c)
   job['status']='active';ledger['status']='active';progress(ledger)
   result=launch.run_guard(c,ev/'config.json')
   cfg=json.loads((ev/'config.json').read_text());job['attempts']=int(cfg['authorization_consumed']);job['authorization_consumed']=cfg['authorization_consumed']
   cleanup_check(c)
   if not cfg['authorization_consumed']:raise RuntimeError('Prelaunch hold: '+result['termination_reason'])
   a=assess(ev/'config.json');job.update(runtime_s=a['run_to_cleanup_seconds'],peak_GiB=a['peak_GiB'],SCF_iterations=a.get('checks',{}).get('SCF_iterations'),negative_pseudocharge=a['final_negative_pseudocharge_electrons'])
   dump(ev/'raw-file-hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/job['work_root']).rglob('*')) if p.is_file()})
   assert a['ready_for_independent_assessment'],a['validation_failure']
   assert not result['workers_remaining'] and (ev/'postflight.json').exists()
   elapsed=time.time()-start;assert elapsed<total,'Job finalization exceeded allocation'
   dump(ev/'finalization-complete.json',{'time':time.time(),'elapsed':elapsed,'accepted_converged_SCF':True,'raw_files_hashed':True})
   job['status']='completed';job['allocation_elapsed_s']=elapsed;aggregate(ledger);progress(ledger)
  ledger['status']='completed';aggregate(ledger)
 except BaseException as ex:
  ledger['status']='stopped';ledger['blocker']=repr(ex);ledger['traceback']=traceback.format_exc()
  if current:
   ev=ROOT/current['evidence_root']
   if (ev/'config.json').exists():
    c=json.loads((ev/'config.json').read_text());current['attempts']=int(c['authorization_consumed']);current['status']='failed' if c['authorization_consumed'] else 'prelaunch_hold'
    # Emergency cleanup only of this task's worker, then inhibitor owner; never unrelated processes.
    for u in [c['unit'],c['unit'].replace('.service','-guardian.service')]:ctrl.command(['systemctl','--user','stop',u],False)
    for kind in ('-grace.timer','-deadline.timer'):ctrl.command(['systemctl','--user','stop',c['unit'].replace('.service',kind)],False)
    try:cleanup_check(c)
    except Exception as cleanup:ledger['cleanup_blocker']=repr(cleanup)
    w=ROOT/current['work_root']
    if w.exists():dump(ev/'raw-file-hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in sorted(w.rglob('*')) if p.is_file()})
  aggregate(ledger)
 finally:
  progress(ledger);dump(E/'batch-terminal.json',{'time':time.time(),'status':ledger['status'],'elapsed_s':batch_elapsed(),'blocker':ledger.get('blocker'),'cleanup_blocker':ledger.get('cleanup_blocker')})
  print(json.dumps({'status':ledger['status'],'blocker':ledger.get('blocker')}),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--dummy',action='store_true');g.add_argument('--run',action='store_true');a=p.parse_args()
 dummy() if a.dummy else run()
