"""Audit the retained AC-stopped second attempt offline; no QE invocation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
R=Path(__file__).resolve().parents[1];E=R/'evidence/qe75-second-v6';W=R/'local/qe75-second-v6/run01'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 h=json.loads((E/'raw-file-hashes.json').read_text())
 for p,v in h.items():assert sha(R/p)==v,p
 s=[json.loads(l) for l in (W/'resources.jsonl').read_text().splitlines()];res=json.loads((E/'result.json').read_text());follow=json.loads((E/'postflight-followup.json').read_text());receipt=json.loads((E/'portable-review-receipt.json').read_text())
 assert sha(R/receipt['archive'])==receipt['sha256']
 text=(W/'stdout.log').read_text();err=(W/'stderr.log').read_text();trajectory=[];it=0
 for n,l in enumerate(text.splitlines(),1):
  m=re.search(r'iteration #\s*(\d+)',l)
  if m:it=int(m[1])
  if 'negative rho (up, down):' in l:trajectory.append({'iteration':it,'negative_e':float(l.split(':')[-1].split()[0]),'line':n})
  if 'estimated scf accuracy' in l:trajectory[-1]['error_Ry']=float(l.split('<')[-1].split()[0])
 actual_inhibitors=[r for r in json.loads(follow['inhibitors']['stdout']) if r['who']=='MOF-QE-second-v6']
 cleanup=follow['workers']['returncode']==1 and not actual_inhibitors and not follow['override_exists'] and all('ControlGroup=\n' in v['stdout'] for k,v in follow['units'].items() if k.endswith('.service'))
 assert cleanup
 assert res['termination_reason']=='AC_lost' and s[-1]['AC_online']==False
 assert all(v['AC_online'] for v in s[:-1])
 assert all(v['inhibitor']['mode']=='block' and v['inhibitor']['what']=='sleep:idle' for v in s)
 assert not any(v['swap_current'] or any(v['memory_events'].values()) or any(v['pids_events'].values()) for v in s)
 assert not any(int(line.split()[1]) for line in res['final_cgroup']['memory.events'].splitlines())
 scratch={str(p.relative_to(W/'scratch')):p.stat().st_size for p in (W/'scratch').rglob('*') if p.is_file()}
 xml=list((W/'scratch').rglob('data-file-schema.xml'));density=list((W/'scratch').rglob('charge-density.dat'))
 assert not xml and not density and 'JOB DONE.' not in text and 'convergence has been achieved' not in text
 assert not re.search(r'atom\s+\d+\s+type\s+\d+\s+force\s*=',text)
 out={'terminal':True,'converged':False,'accepted_energy':False,'valid_DFT_difference':False,'termination':'AC_lost',
 'iterations_completed':sum('error_Ry' in x for x in trajectory),'iterations_started':it,'last_error_Ry':trajectory[-1]['error_Ry'],'trajectory':trajectory,
 'raw_hashes_verified':len(h),'archive_sha256_verified':receipt['sha256'],'peak_bytes':max(int(res['service']['MemoryPeak']),max(v['memory_peak'] for v in s)),
 'zero_job_swap':True,'zero_memory_and_task_limit_events':True,'all_samples_inhibited':True,'AC_false_samples':sum(not v['AC_online'] for v in s),'samples':len(s),
 'AC_loss_UTC':datetime.fromtimestamp(s[-1]['time'],timezone.utc).isoformat(),'worker_cleanup_UTC':datetime.fromtimestamp(res['time'],timezone.utc).isoformat(),
 'run_to_cleanup_s':res['time']-json.loads((W/'execution-started.json').read_text())['time'],'allocation_to_cleanup_s':res['allocation_elapsed'],
 'allocation_to_package_s':receipt['allocation_elapsed'],'actual_final_service':res['service'],'scratch_bytes':sum(scratch.values()),'scratch_files':scratch,
 'XML_present':False,'charge_density_present':False,'final_forces_present':False,'restart_complete':False,'cleanup_verified':cleanup,
 'warnings':re.findall(r'^.*(?:not converged|Error in routine|MPI_ABORT|segmentation fault).*$' ,text+err,re.M|re.I),
 'minimum_host_available_GiB':min(v['system_available'] for v in s)/2**30,'current_AC':follow['AC'],
 'assessment_corrections':['Pre-stop ExecMainStatus=0 belonged to a RUNNING service and is not successful completion; final stopped service exit=1.', 'Systemd failed is terminal with empty cgroup. Original cleanup flag required inactive and falsely reported cleanup failure; workers/inhibitor/override are absent.']}
 (E/'partial-independent-audit.json').write_text(json.dumps(out,indent=2)+'\n')
 orig=json.loads((E/'assessment.json').read_text());orig['cleanup_verified']=True;orig['checks']['process_and_resource_success']=False;orig['actual_terminal_service']=res['service'];orig['assessment_corrections']=out['assessment_corrections'];orig['original_assessment_preserved']='assessment.json';(E/'assessment-terminal-v2.json').write_text(json.dumps(orig,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k not in ['trajectory','scratch_files','actual_final_service']},indent=2))
if __name__=='__main__':main()
