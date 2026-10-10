"""Offline terminal assessment, cleanup audit and Windows package; never starts QE."""
from datetime import datetime,timezone
import json,shutil,time,zipfile
from pathlib import Path
from qe75_fedora_v1 import ROOT,sha
from finalize_qe75_completion_v5 import call,dump
from assess_qe75_second_v7 import assess
from run_qe_water_pilot import RY_EV
import xml.etree.ElementTree as ET

def main():
 E=ROOT/'evidence/qe75-second-v7';C=ROOT/'configs/qe75-second-v7.json';c=json.loads(C.read_text());w=ROOT/c['work_root'];a=json.loads((E/'allocation.json').read_text())
 with (E/'finalizer-entered.json').open('x') as f:json.dump({'time':time.time(),'sha256':sha(Path(__file__))},f)
 while not (E/'inhibitor-release.json').exists():
  if time.time()>a['deadline_unix']:
   dump(E/'finalizer-blocked.json',{'reason':'Original deadline expired without release receipt; never restart','time':time.time()});return
  time.sleep(2)
 units=[c['unit'],c['unit'].replace('.service','-guardian.service'),c['unit'].replace('.service','-grace.timer'),c['unit'].replace('.service','-deadline.timer')]
 inhibitors=json.loads(call(['systemd-inhibit','--list','--json=short','--no-pager'])['stdout'])
 post={'time':time.time(),'elapsed':time.time()-a['allocation_start_unix'],'workers':call(['pgrep','-a','-x','pw.x|mpirun|prterun|orted']),
  'inhibitors_remaining':[r for r in inhibitors if r['who']==c['inhibitor_who']],
  'units':{u:call(['systemctl','--user','show',u,'-p','ActiveState','-p','SubState','-p','ControlGroup']) for u in units},
  'runtime_override_exists':(Path('/run/user/1000/systemd/user')/(c['unit']+'.d')).exists(),
  'suspend_journal':call(['journalctl','--since',datetime.fromtimestamp(a['allocation_start_unix'],timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),'-u','systemd-suspend.service','-u','systemd-hibernate.service','-u','systemd-suspend-then-hibernate.service','--no-pager'])}
 dump(E/'postflight.json',post)
 try:r=assess()
 except Exception as ex:
  r={'ready_for_independent_assessment':False,'accepted_converged_SCF_energy':False,'validation_failure':repr(ex)}
 r['cleanup_verified']=post['workers']['returncode']==1 and not post['inhibitors_remaining'] and not post['runtime_override_exists'] and all(any('ActiveState='+state in v['stdout'] for state in ['inactive','failed']) and ('ControlGroup=' not in v['stdout'] or 'ControlGroup=\n' in v['stdout']) for v in post['units'].values())
 r['allocation_budget_met']=post['elapsed']<14400
 if not r['cleanup_verified'] or not r['allocation_budget_met']:r['ready_for_independent_assessment']=False;r['accepted_converged_SCF_energy']=False
 dump(E/'assessment.json',r)
 comparison={'valid_pair':False,'provisional':True,'reason':'Second assessment not yet passed','cutoff_grid_accuracy_unresolved':True}
 if r['ready_for_independent_assessment']:
  prior=ROOT/'local/qe75-fedora-completion-v5/run01';hashes=json.loads((ROOT/'evidence/qe75-fedora-completion-v5/launch02/raw-file-hashes.json').read_text())
  fx=next((prior/'scratch').glob('*.save/data-file-schema.xml'))
  for p in [fx,prior/'input.in',prior/'stdout.log']:assert sha(p)==hashes[str(p.relative_to(ROOT))]
  t=ET.parse(fx).getroot()
  for n in t.iter():n.tag=n.tag.split('}')[-1]
  first=float(t.findtext('output/total_energy/etot'));second=r['checks']['energy']['XML_Ha']
  m=json.loads((ROOT/c['package']/'manifest.json').read_text());ids=['uio66_110111_H2O_s28_f0.010_complex','uio66_110111_H2O_s28_f0.005_complex'];uma=[m['components'][k]['uma']['energy_eV'] for k in ids]
  delta=(second-first)*2*RY_EV;ud=uma[1]-uma[0]
  comparison={'valid_pair':True,'provisional':True,'DFT_first_Ha':first,'DFT_second_Ha':second,'DFT_second_minus_first_eV':delta,'UMA_first_eV':uma[0],'UMA_second_eV':uma[1],'UMA_second_minus_first_eV':ud,'DFT_minus_UMA_delta_eV':delta-ud,'Ry_to_eV':RY_EV,'cutoff_grid_accuracy_unresolved':True,'interpretation':'Two converged frozen SCFs only; not an adsorption energy, relaxation result or material/UMA accuracy validation.'}
 dump(E/'comparison.json',comparison)
 c=json.loads(C.read_text());c.update(preparation_terminal=True,result='evidence/qe75-second-v7/assessment.json',note='TERMINAL; consumed; no retry/additional geometry/convergence study. See actual assessment and provisional comparison.');dump(C,c)
 dump(E/'raw-file-hashes.json',{str(p.relative_to(ROOT)):sha(p) for p in sorted(w.rglob('*')) if p.is_file()})
 report=f'''# Second frozen water-complex 80/600-Ry attempt — terminal review

Ready for assessment: {r['ready_for_independent_assessment']}. Validation failure: {r.get('validation_failure')}.

Assessment and resource evidence:

```json
{json.dumps({k:v for k,v in r.items() if k!='output_summary'},indent=2)}
```

Provisional second-minus-first comparison:

```json
{json.dumps(comparison,indent=2)}
```

Both geometries retain the approved 80/600-Ry PBE-D3(BJ) two-body protocol, Gamma, neutral nspin=1, fixed occupations, conv_thr=1e-8 Ry, beta=0.3, CG/mixing4/diskhigh; 127 frozen atoms and 522 electrons. No prior scratch reused. Four physical cores, 11-GiB hard/10-GiB high/zero job swap/96 tasks and immutable four-hour allocation. Persistent negative pseudocharge and finite frozen-geometry forces are findings requiring interpretation, not automatic acceptance/rejection. No unconverged energy is accepted.

Smallest proposed density-grid check: paired 80/750-Ry calculations, retaining all other settings, on adequate verified hardware. Verify actual grid changes; compare delta-energy changes to 2–3 meV and force changes to 0.005–0.01 eV/Å. This two-job proposal is NOT authorized and does not replace later wavefunction-cutoff/k-point checks. Prior memory estimates exceed this laptop's cap. Phase 3, physical accuracy and UMA accuracy remain unresolved.

Raw data/checkpoints/UPFs: run/. Evidence/accounting/trajectory: evidence/. First full review and independent audit: first-review.zip and first-independent-review.zip. SHA256SUMS.json covers every payload. Original failures/evidence retained. No extra calculation was launched.
'''
 (E/'TERMINAL_REVIEW.md').write_text(report)
 package=ROOT/'artifacts/phase3/uio66_qe_water_pair_v7_windows';package.mkdir(exist_ok=False)
 shutil.copytree(w,package/'run');shutil.copytree(E,package/'evidence')
 shutil.copyfile(ROOT/'artifacts/phase3/uio66_qe600_completion_v5_review_v2.zip',package/'first-review.zip')
 shutil.copyfile(ROOT/'artifacts/phase3/uio66_qe_first_independent_review_v6.zip',package/'first-independent-review.zip')
 shutil.copyfile(E/'TERMINAL_REVIEW.md',package/'REVIEW_REPORT.md');shutil.copyfile(C,package/'execution-config.json')
 code=package/'controller';code.mkdir()
 for name in ['qe75_second_v7.py','launch_qe75_second_v7.py','assess_qe75_second_v7.py','finalize_qe75_second_v7.py']:
  shutil.copyfile(ROOT/'scripts'/name,code/name)
 sums={str(p.relative_to(package)):sha(p) for p in sorted(package.rglob('*')) if p.is_file()};dump(package/'SHA256SUMS.json',sums)
 dest=package.with_suffix('.zip')
 with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for p in sorted(package.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(package))
 import hashlib
 with zipfile.ZipFile(dest) as z:
  for n,h in sums.items():
   with z.open(n) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==h,n
 receipt={'archive':str(dest.relative_to(ROOT)),'sha256':sha(dest),'size_bytes':dest.stat().st_size,'verified_payloads':len(sums),'time':time.time(),'allocation_elapsed':time.time()-a['allocation_start_unix']}
 dump(E/'portable-review-receipt.json',receipt);dest.with_suffix('.zip.sha256').write_text(receipt['sha256']+'  '+dest.name+'\n')
 dump(E/'finalization-complete.json',{'time':time.time(),'elapsed':time.time()-a['allocation_start_unix'],'ready_for_independent_assessment':r['ready_for_independent_assessment'],'additional_calculation_started':False})
 print(json.dumps(receipt))
if __name__=='__main__':main()
