"""Independent offline terminal audit of the twelve authorized baseline SCFs."""
from pathlib import Path
import csv,hashlib,json,math,re,subprocess,time,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];E=R/'evidence/qe75-baseline12-recovery-v2';V=E/'terminal-review-v1';P=R/'artifacts/phase3/uio66_frozen_dft_v2_qe75_fedora_verified01'
B=.529177210903;RY=13.605693122994017

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def call(a):
 p=subprocess.run(a,capture_output=True,text=True,timeout=30);return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def main():
 V.mkdir(exist_ok=False);jobs=json.loads((R/'plans/qe75-baseline12-recovery-v2/jobs.json').read_text());m=json.loads((P/'manifest.json').read_text());fh=json.loads((P/'file_hashes.json').read_text());symbols={1:'H',6:'C',7:'N',8:'O',40:'Zr'};valences={};rows=[];force_rows=[];count=0
 for p in (P/'pseudo').iterdir():
  if not p.is_file():continue
  assert sha(p)==fh['pseudo/'+p.name];s=p.read_text()
  if 'Z valence' in s:el='Zr';v=float(re.search(r'([\d.E+-]+)\s+Z valence',s).group(1))
  else:el=re.search(r'element\s*=\s*"\s*(\w+)\s*"',s).group(1);v=float(re.search(r'z_valence\s*=\s*"\s*([\d.Ee+-]+)',s).group(1))
  valences[el]=v
 try:
  for j in jobs:
   id=j['manifest_id'];ev=R/j['evidence_root'];w=R/j['work_root'];c=json.loads((ev/'config.json').read_text());a=json.loads((ev/'assessment.json').read_text());res=json.loads((ev/'result.json').read_text());final=json.loads((ev/'finalization-complete.json').read_text());comp=m['components'][id];g=json.loads((P/comp['geometry_file']).read_text());syms=[symbols[z] for z in g['numbers']];nat=len(syms);ne=sum(valences[s] for s in syms)-comp['charge']
   assert sha(P/comp['geometry_file'])==fh[comp['geometry_file']];assert nat==j['nat'] and ne==j['expected_electrons']
   cg=json.loads((P/m['components'][comp['pose']+'_complex']['geometry_file']).read_text());assert g['cell_A']==cg['cell_A'];assert g['positions_A']==[cg['positions_A'][i] for i in comp['source_atom_indices']]
   for p,h in json.loads((ev/'raw-file-hashes.json').read_text()).items():assert sha(R/p)==h,p;count+=1
   assert sha(w/'input.in')==j['input_sha256']==c['input_sha256'];assert (w/'input.in').read_bytes()==(R/j['input']).read_bytes()
   for p in (w/'pseudo').iterdir():assert sha(p)==fh['pseudo/'+p.name]
   text=(w/'stdout.log').read_text();errtext=(w/'stderr.log').read_text();x=ET.parse(w/'scratch'/(id+'.save')/'data-file-schema.xml').getroot();assert x.attrib['Units']=='Hartree atomic units'
   for el in x.iter():el.tag=el.tag.split('}')[-1]
   get=lambda p:x.findtext(p).strip()
   assert get('exit_status')=='0' and get('output/convergence_info/scf_conv/convergence_achieved')=='true'
   steps=int(get('output/convergence_info/scf_conv/n_scf_steps'));error=2*float(get('output/convergence_info/scf_conv/scf_error'));assert math.isfinite(error) and 0<=error<=1e-8
   assert get('parallel_info/nprocs')=='4' and get('parallel_info/nthreads')=='1';assert float(get('output/band_structure/nelec'))==ne
   assert 'JOB DONE.' in text and re.search(r'convergence has been achieved in\s*'+str(steps)+r' iterations',text)
   assert not re.search(r'convergence NOT achieved|Error in routine|MPI_ABORT|segmentation fault',text+errtext,re.I)
   assert not re.search(r'eigenvalues not converged|c_bands.*not converged',re.split(r'iteration #\s*\d+',text)[-1],re.I)
   ens=re.findall(r'!\s+total energy\s*=\s*(\S+)\s+Ry',text);assert len(ens)==1;en=float(ens[0]);ha=float(get('output/total_energy/etot'));assert math.isfinite(ha) and abs(en-2*ha)<5.1e-9
   for path,v in [('output/basis_set/ecutwfc',40),('output/basis_set/ecutrho',300),('input/electron_control/conv_thr',5e-9),('input/electron_control/mixing_beta',.3),('input/bands/tot_charge',0)]:assert math.isclose(float(get(path)),v,abs_tol=1e-15,rel_tol=1e-12)
   for path,v in [('input/electron_control/diagonalization','cg'),('input/electron_control/mixing_ndim','4'),('input/bands/occupations','fixed'),('output/basis_set/gamma_only','true'),('output/dft/functional','PBE'),('output/dft/vdW/vdw_corr','grimme-d3'),('output/dft/vdW/dftd3_version','4'),('output/dft/vdW/dftd3_threebody','false'),('output/magnetization/lsda','false')]:assert get(path)==v,path
   for sec in ('input','output'):
    st=x.find(sec+'/atomic_structure');ats=st.findall('atomic_positions/atom');assert len(ats)==nat and [z.get('name') for z in ats]==syms
    pos=[[float(v)*B for v in z.text.split()] for z in ats];cell=[[float(v)*B for v in st.findtext('cell/'+z).split()] for z in ('a1','a2','a3')]
    for actual,expected in [(pos,g['positions_A']),(cell,g['cell_A'])]:assert max(abs(a-b) for q,r in zip(actual,expected) for a,b in zip(q,r))<2e-8
   lines=text.splitlines();heads=[i for i,l in enumerate(lines) if 'Forces acting on atoms (cartesian axes, Ry/au)' in l];assert len(heads)==1;fr=[]
   for line in lines[heads[0]+1:]:
    if not line.strip():continue
    if not line.strip().startswith('atom'):break
    fr.append(line.split())
   xf=[float(v)*2 for v in get('output/forces').split()];assert len(fr)==nat and len(xf)==3*nat;types=[z.get('name') for z in x.findall('input/atomic_species/species')];norms=[]
   for i,f in enumerate(fr):
    assert int(f[1])==i+1 and types[int(f[3])-1]==syms[i];v=[float(z) for z in f[6:9]];xx=xf[3*i:3*i+3];assert all(math.isfinite(z) for z in v+xx);diff=max(abs(q-r) for q,r in zip(v,xx));assert diff<5.1e-9
    fv=[z*RY/B for z in xx];norms.append(math.sqrt(sum(z*z for z in fv)));force_rows.append([id,i+1,comp['source_atom_indices'][i],syms[i],*v,*xx,*fv,diff])
   svc=res['service_before_cleanup'];assert svc['ExecMainCode']=='1' and svc['ExecMainStatus']=='0' and svc['Result']=='success';peak=int(svc['MemoryPeak']);assert peak<10*2**30 and int(svc['MemorySwapPeak'])==0
   assert not res['workers_remaining'] and res['runtime_override_removed'];assert res['termination_reason']=='worker_terminal; see exit status and QE output';assert res['allocation_elapsed']<=14100 and final['elapsed']<14400
   assert json.loads((ev/'inhibitor-release.json').read_text())['remaining']==[]
   samples=[json.loads(l) for l in (w/'resources.jsonl').read_text().splitlines()];assert samples
   for q in samples:assert q['AC_online'] and q['inhibitor'] and q['swap_current']==0 and not any(q['memory_events'].values()) and not any(q['pids_events'].values())
   if res.get('final_cgroup'):
    for k in ('memory.events','pids.events'):assert not any(int(l.split()[1]) for l in res['final_cgroup'][k].splitlines())
   journal=json.loads((ev/'journal.json').read_text())['stdout'];assert not re.search(r'oom-kill|Out of memory|Memory cgroup out of memory',journal,re.I)
   post=json.loads((ev/'postflight.json').read_text());assert post['workers']['returncode']==1 and not post['inhibitors_remaining'] and not post['runtime_override_exists']
   neg=[float(v) for v in re.findall(r'negative rho \(up, down\):\s*(\S+)',text)]
   checkpoint=[p for p in (w/'scratch').rglob('*') if p.is_file()];assert (w/'scratch'/(id+'.save')/'charge-density.dat').exists() and (w/'scratch'/(id+'.save')/'paw.txt').exists();assert all((w/'scratch'/(id+'.wfc'+str(i))).exists() for i in range(1,5))
   assert a['ready_for_independent_assessment'] and a['accepted_converged_SCF_energy'];assert abs(a['checks']['energy']['XML_Ha']-ha)<1e-12;assert a['checks']['SCF_iterations']==steps;assert abs(a['checks']['forces']['max_norm_eV_A']-max(norms))<3e-7
   row={'job':j['order'],'id':id,'passed':True,'atoms':nat,'electrons':ne,'iterations':steps,'error_Ry':error,'energy_Ha':ha,'energy_text_Ry':en,'text_XML_difference_Ry':abs(en-2*ha),'force_count':nat,'force_max_eV_A':max(norms),'force_RMS_eV_A':math.sqrt(sum(v*v for v in norms)/nat),'final_negative_pseudocharge_e':neg[-1] if neg else None,'negative_trajectory':neg,'peak_GiB':peak/2**30,'swap_bytes':0,'minimum_host_available_GiB':min(q['system_available'] for q in samples)/2**30,'runtime_cleanup_s':a['run_to_cleanup_seconds'],'allocation_finalization_s':final['elapsed'],'scratch_bytes':sum(p.stat().st_size for p in checkpoint),'final_cgroup_counters_available':bool(res.get('final_cgroup')),'warnings':a['output_summary']['warnings'],'grids':a['output_summary']['grids'],'checkpoint_components_present':True}
   rows.append(row);put(V/'audit-in-progress.json',{'jobs_verified':len(rows),'raw_hashes_verified':count});print('verified',j['order'],id,flush=True)
  comparison=json.loads((E/'comparisons.json').read_text());energy={j['id']:j['energy_Ha'] for j in rows};energy.update({k:v['energy_Ha'] for k,v in comparison['accepted_converged_results'].items() if k not in energy})
  for d in comparison['differences']:
   for kind in ('complex','host'):
    delta=(energy[d['second']+'_'+kind]-energy[d['first']+'_'+kind])*2*RY;assert abs(delta-d['DFT_delta_'+kind+'_eV'])<1e-10
    u=[m['components'][d[k]+'_'+kind]['uma'] for k in ('first','second')]
    if all(v and v.get('energy_eV') is not None for v in u):assert abs((u[1]['energy_eV']-u[0]['energy_eV'])-d['UMA_delta_'+kind+'_eV'])<1e-10
   assert abs(d['DFT_delta_guest_associated_eV']-(d['DFT_delta_complex_eV']-d['DFT_delta_host_eV']))<1e-10
  workers=call(['pgrep','-a','-x','pw.x|mpirun|prterun|orted']);assert workers['returncode']==1
  ins=call(['systemd-inhibit','--list','--json=short','--no-pager']);own=[q for q in json.loads(ins['stdout']) if q['who'].startswith('MOF-QE-baseline12')];assert not own
  overrides=list(Path('/run/user/1000/systemd/user').glob('qe75-baseline12*.service.d'));assert not overrides
  units={}
  for j in jobs:
   name=f"qe75-baseline12-v2-job{j['order']:02d}"
   for suffix in ('.service','-guardian.service','-grace.timer','-deadline.timer'):
    r=call(['systemctl','--user','show',name+suffix,'-p','ActiveState','-p','ControlGroup']);d=dict(l.split('=',1) for l in r['stdout'].splitlines());assert d.get('ActiveState') in ('inactive','failed') and not d.get('ControlGroup');units[name+suffix]=d
  terminal=json.loads((E/'batch-terminal.json').read_text());assert terminal['status']=='completed' and terminal['elapsed_s']<172800
  put(V/'independent-audit.json',{'passed':True,'jobs':rows,'raw_hashes_verified':count,'force_vectors_independently_checked':len(force_rows),'new_jobs':12,'total_baseline_with_prior_water':14,'batch_elapsed_s':terminal['elapsed_s'],'comparison_reconstructed':True,'all_workers_gone':True,'task_inhibitors_released':True,'task_overrides_absent':True,'current_units':units,'limitations':'Successful SCF only; cutoff/grid/wavefunction/physical accuracy unresolved. No new computation invoked. Final cgroups removed on exit; use preserved lifetime service peaks and all samples, not invented final counters.','audit_time':time.time()})
  with (V/'all-force-crosschecks.csv').open('w') as f:
   wr=csv.writer(f);wr.writerow(['manifest_id','QE_atom','source_atom_0based','symbol','text_Fx_Ry_bohr','text_Fy_Ry_bohr','text_Fz_Ry_bohr','XML_Fx_Ry_bohr','XML_Fy_Ry_bohr','XML_Fz_Ry_bohr','Fx_eV_A','Fy_eV_A','Fz_eV_A','max_text_XML_difference_Ry_bohr']);wr.writerows(force_rows)
  print('PASS',len(rows),'jobs;',len(force_rows),'force vectors;',count,'raw hashes',flush=True)
 except BaseException as ex:
  put(V/'audit-failure.json',{'error':repr(ex),'verified_jobs':rows,'time':time.time()});raise
if __name__=='__main__':main()
