"""Independent terminal verification of second frozen SCF; never executes QE."""
import csv,hashlib,json,math,re
from pathlib import Path
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];E=R/'evidence/qe75-second-v6';W=R/'local/qe75-second-v6/run01'
B=0.529177210903;RY=4.3597447222071e-18/1.602176634e-19/2

def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
 out={'passed':False,'failure':None,'accepted_energy':False}
 try:
  cfg=json.loads((R/'configs/qe75-second-v6.json').read_text());pkg=R/cfg['package'];m=json.loads((pkg/'manifest.json').read_text());h=json.loads((pkg/'file_hashes.json').read_text())
  pfx='uio66_110111_H2O_s28_f0.005_complex';comp=m['components'][pfx];g=json.loads((pkg/comp['geometry_file']).read_text());sym=next(p['atom_symbols'] for p in m['poses'] if p['id']==comp['pose'])
  assert sha(pkg/comp['geometry_file'])==h[comp['geometry_file']]
  for p,v in json.loads((E/'raw-file-hashes.json').read_text()).items():assert sha(R/p)==v,p
  assert sha(W/'input.in')==cfg['input_sha256']=='6e5208b721ce790b932a67ba103f135c28cfe2889b02fc2a2958614532be62b3'
  for p in (W/'pseudo').iterdir():assert sha(p)==h['pseudo/'+p.name]
  text=(W/'stdout.log').read_text();stderr=(W/'stderr.log').read_text();inp=(W/'input.in').read_text()
  x=ET.parse(W/'scratch'/(pfx+'.save')/'data-file-schema.xml').getroot();assert x.attrib['Units']=='Hartree atomic units'
  for n in x.iter():n.tag=n.tag.rsplit('}',1)[-1]
  get=lambda k:x.findtext(k).strip()
  assert get('exit_status')=='0' and get('output/convergence_info/scf_conv/convergence_achieved')=='true'
  steps=int(get('output/convergence_info/scf_conv/n_scf_steps'));err=2*float(get('output/convergence_info/scf_conv/scf_error'));assert math.isfinite(err) and 0<=err<=1e-8
  assert float(get('output/band_structure/nelec'))==522
  assert get('parallel_info/nprocs')=='4' and get('parallel_info/nthreads')=='1'
  assert 'JOB DONE.' in text and re.search(r'convergence has been achieved in\s+'+str(steps)+r' iterations',text)
  assert not re.search(r'convergence NOT achieved|Error in routine|MPI_ABORT|segmentation fault|eigenvalues not converged|c_bands.*not converged',text+stderr,re.I)
  ens=re.findall(r'!\s+total energy\s*=\s*(\S+)\s+Ry',text);assert len(ens)==1
  et=float(ens[0]);ex=float(get('output/total_energy/etot'));assert math.isfinite(ex) and abs(et-2*ex)<5.1e-9
  geomerr={}
  for sec in ('input','output'):
   st=x.find(sec+'/atomic_structure');ats=st.findall('atomic_positions/atom');assert [a.get('name') for a in ats]==sym and len(ats)==127
   coords=[[float(v)*B for v in a.text.split()] for a in ats];cell=[[float(v)*B for v in st.findtext('cell/'+v).split()] for v in ('a1','a2','a3')]
   for label,actual,expected in [('positions',coords,g['positions_A']),('cell',cell,g['cell_A'])]:
    d=max(abs(a-b) for v,w in zip(actual,expected) for a,b in zip(v,w));assert math.isfinite(d) and d<2e-8;geomerr[sec+'_'+label+'_A']=d
  coords=inp.split('ATOMIC_POSITIONS angstrom\n')[1].splitlines()[:127];assert [l.split()[0] for l in coords]==sym
  assert [[float(v) for v in l.split()[1:]] for l in coords]==g['positions_A']
  lines=text.splitlines();heads=[i for i,l in enumerate(lines) if 'Forces acting on atoms (cartesian axes, Ry/au):' in l];assert len(heads)==1
  rows=[]
  for line in lines[heads[0]+1:]:
   if not line.strip():continue
   if not line.strip().startswith('atom'):break
   t=line.split();assert t[0]=='atom' and t[2]=='type' and t[4:6]==['force','='];rows.append((int(t[1]),int(t[3]),[float(v) for v in t[6:9]]))
  values=[float(v) for v in get('output/forces').split()];assert len(values)==381 and len(rows)==127
  species=[a.get('name') for a in x.findall('input/atomic_species/species')];table=[];norms=[]
  for i,(idx,typ,f) in enumerate(rows):
   xf=values[3*i:3*i+3];assert idx==i+1 and species[typ-1]==sym[i] and all(math.isfinite(v) for v in f+xf)
   diff=max(abs(a-2*b) for a,b in zip(f,xf));assert diff<5.1e-9
   norm=math.sqrt(sum(v*v for v in f))*RY/B;norms.append(norm);table.append([idx,sym[i],typ,*f,*xf,diff,norm])
  with (E/'independent-force-crosscheck.csv').open('w') as f:
   writer=csv.writer(f);writer.writerow(['atom','symbol','type','Fx_Ry_bohr','Fy_Ry_bohr','Fz_Ry_bohr','XML_Fx_Ha_bohr','XML_Fy_Ha_bohr','XML_Fz_Ha_bohr','max_difference_Ry_bohr','norm_eV_A']);writer.writerows(table)
  res=json.loads((E/'result.json').read_text());svc=res['service_before_cleanup'];assert svc['ExecMainStatus']=='0' and svc['Result']=='success' and not res['workers_remaining']
  samples=[json.loads(l) for l in (W/'resources.jsonl').read_text().splitlines()];assert all(s['swap_current']==0 and not any(s['memory_events'].values()) and not any(s['pids_events'].values()) for s in samples)
  final=res['final_cgroup'];counters=dict(l.split() for l in final['memory.events'].splitlines());assert not any(int(v) for v in counters.values())
  assert int(final['memory.swap.current'])==0
  post=json.loads((E/'postflight.json').read_text());assert post['workers']['returncode']==1 and not post['inhibitors_remaining'] and not post['runtime_override_exists']
  assert res['allocation_elapsed']<=14100 and json.loads((E/'finalization-complete.json').read_text())['elapsed']<14400
  first=json.loads((R/'evidence/qe75-first-independent-review-v6/review.json').read_text());delta=(ex-first['energy_XML_Ha'])*2*RY
  compa=json.loads((E/'comparison.json').read_text());assert compa['valid_pair'] and abs(delta-compa['DFT_second_minus_first_eV'])<1e-10
  neg=[float(v) for v in re.findall(r'negative rho \(up, down\):\s*(\S+)',text)]
  out.update(passed=True,accepted_energy=True,SCF_iterations=steps,error_Ry=err,energy_Ry=et,energy_Ha=ex,text_XML_difference_Ry=abs(et-2*ex),electrons=522,geometry_errors=geomerr,forces={'count':127,'max_norm_eV_A':max(norms),'rms_norm_eV_A':math.sqrt(sum(v*v for v in norms)/127),'max_atom_1based':norms.index(max(norms))+1,'max_text_XML_difference_Ry_bohr':max(r[-2] for r in table)},negative_pseudocharge_e=neg,DFT_second_minus_first_eV=delta,UMA_second_minus_first_eV=compa['UMA_second_minus_first_eV'],all_final_memory_events_zero=True,no_final_diagonalization_warning=True,cutoff_grid_physical_accuracy_unresolved=True)
 except Exception as ex:out['failure']=repr(ex)
 (E/'independent-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
