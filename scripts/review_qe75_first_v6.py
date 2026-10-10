"""Independent offline raw-evidence review; imports no previous result parser."""
import csv,hashlib,json,math,re,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'evidence/qe75-first-independent-review-v6'
EV.mkdir(exist_ok=True)
B=0.529177210903
RY=(4.3597447222071e-18/1.602176634e-19)/2

def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def review():
 work=ROOT/'local/qe75-fedora-completion-v5/run01'
 oldev=ROOT/'evidence/qe75-fedora-completion-v5/launch02'
 pkg=ROOT/'artifacts/phase3/uio66_frozen_dft_v2_qe75_fedora_verified01'
 manifest=json.loads((pkg/'manifest.json').read_text());hashes=json.loads((pkg/'file_hashes.json').read_text())
 receipt=json.loads((oldev/'portable-review-v2-receipt.json').read_text());archive=ROOT/receipt['archive']
 assert sha(archive)==receipt['sha256']
 with zipfile.ZipFile(archive) as z:
  zh=json.loads(z.read('SHA256SUMS.json'))
  assert set(z.namelist())==set(zh)|{'SHA256SUMS.json'}
  for name,value in zh.items():
   with z.open(name) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==value,name
  for p in work.rglob('*'):
   if p.is_file():assert sha(p)==zh['run/'+str(p.relative_to(work))],str(p)
 for p,v in json.loads((oldev/'raw-file-hashes.json').read_text()).items():assert sha(ROOT/p)==v,p
 prefix='uio66_110111_H2O_s28_f0.010_complex';comp=manifest['components'][prefix]
 assert sha(pkg/comp['geometry_file'])==hashes[comp['geometry_file']]
 geom=json.loads((pkg/comp['geometry_file']).read_text());symbols=next(p['atom_symbols'] for p in manifest['poses'] if p['id']==comp['pose'])
 text=(work/'stdout.log').read_text();err=(work/'stderr.log').read_text();inp=(work/'input.in').read_text()
 assert sha(work/'input.in')=='b60f5a1bf910b7883bcbbb1e8e185791ef57103e82af60801f46f25361915838'
 for p in (work/'pseudo').iterdir():assert sha(p)==hashes['pseudo/'+p.name]
 xml=ET.parse(work/'scratch'/(prefix+'.save')/'data-file-schema.xml').getroot()
 assert xml.attrib['Units']=='Hartree atomic units'
 for node in xml.iter():node.tag=node.tag.rsplit('}',1)[-1]
 def get(p):return xml.findtext(p).strip()
 assert get('exit_status')=='0' and get('output/convergence_info/scf_conv/convergence_achieved')=='true'
 assert get('output/band_structure/nelec') and float(get('output/band_structure/nelec'))==522
 assert get('parallel_info/nprocs')=='4' and get('parallel_info/nthreads')=='1'
 iterations=int(get('output/convergence_info/scf_conv/n_scf_steps'));error=2*float(get('output/convergence_info/scf_conv/scf_error'))
 assert iterations==16 and error<=1e-8 and error>=0
 assert 'convergence has been achieved in  16 iterations' in text and 'JOB DONE.' in text
 assert not re.search('convergence NOT achieved|Error in routine|MPI_ABORT|SIGSEGV|segmentation fault|eigenvalues not converged|c_bands.*not converged',text+err,re.I)
 energy=re.findall(r'!\s+total energy\s*=\s*(\S+)\s+Ry',text);assert len(energy)==1
 energy=float(energy[0]);xml_energy=float(get('output/total_energy/etot'));assert abs(energy-2*xml_energy)<5e-9
 errors={}
 for sec in ('input','output'):
  st=xml.find(sec+'/atomic_structure');atoms=st.findall('atomic_positions/atom');assert [a.get('name') for a in atoms]==symbols and len(atoms)==127
  coords=[[float(v)*B for v in a.text.split()] for a in atoms]
  cell=[[float(v)*B for v in st.findtext('cell/'+k).split()] for k in ('a1','a2','a3')]
  for name,a,b in [('positions',coords,geom['positions_A']),('cell',cell,geom['cell_A'])]:
   delta=max(abs(x-y) for r,s in zip(a,b) for x,y in zip(r,s));assert delta<2e-8;errors[sec+'_'+name+'_A']=delta
 # Parse input coordinates independently as well, not just XML.
 lines=inp.splitlines();i=lines.index('ATOMIC_POSITIONS angstrom');pos=[l.split() for l in lines[i+1:i+128]]
 assert [p[0] for p in pos]==symbols
 assert all(float(x)==y for p,g in zip(pos,geom['positions_A']) for x,y in zip(p[1:],g))
 i=lines.index('CELL_PARAMETERS angstrom');assert [[float(v) for v in l.split()] for l in lines[i+1:i+4]]==geom['cell_A']
 # Read the 127 consecutive total-force rows after the unique labelled header.
 heads=[i for i,l in enumerate(text.splitlines()) if 'Forces acting on atoms (cartesian axes, Ry/au):' in l];assert len(heads)==1
 fl=[]
 for l in text.splitlines()[heads[0]+1:]:
  if not l.strip():continue
  if not l.strip().startswith('atom'):break
  t=l.split();assert t[0]=='atom' and t[2]=='type' and t[4:6]==['force','='];fl.append((int(t[1]),int(t[3]),[float(v) for v in t[6:9]]))
 assert len(fl)==127
 vals=[float(v) for v in get('output/forces').split()];assert len(vals)==381
 xf=[vals[i:i+3] for i in range(0,len(vals),3)]
 species=[s.get('name') for s in xml.findall('input/atomic_species/species')]
 table=[];norms=[]
 for i,((idx,typ,f),x) in enumerate(zip(fl,xf)):
  assert idx==i+1 and species[typ-1]==symbols[i]
  assert all(math.isfinite(v) for v in f+x)
  d=max(abs(a-2*b) for a,b in zip(f,x));assert d<=5.01e-9
  norm=math.sqrt(sum(v*v for v in f))*RY/B;norms.append(norm)
  table.append([idx,symbols[i],typ,*f,*x,d,norm])
 with (EV/'force-crosscheck.csv').open('w') as f:
  writer=csv.writer(f);writer.writerow(['atom_1based','symbol','QE_type','text_Fx_Ry_bohr','text_Fy_Ry_bohr','text_Fz_Ry_bohr','XML_Fx_Ha_bohr','XML_Fy_Ha_bohr','XML_Fz_Ha_bohr','max_delta_Ry_bohr','norm_eV_A']);writer.writerows(table)
 # Scan complete output in order for iteration/negative charge/error observations.
 trajectory=[];it=0
 for n,l in enumerate(text.splitlines(),1):
  m=re.search(r'iteration #\s*(\d+)',l)
  if m:it=int(m[1])
  if 'negative rho (up, down):' in l:trajectory.append({'iteration':it,'negative_e':float(l.split(':')[-1].split()[0]),'line':n})
  if 'estimated scf accuracy' in l:
   e=float(l.split('<')[1].split()[0]);trajectory[-1]['error_Ry']=e
 old=json.loads((oldev/'assessment-v2.json').read_text())
 assert [(x['iteration'],x['negative_e']) for x in trajectory]==[(x['iteration'],x['negative_electrons']) for x in old['output_summary']['observations']]
 for x,y in zip(trajectory,old['output_summary']['observations']):assert x.get('error_Ry')==y['estimated_scf_error_Ry']
 resources=[json.loads(l) for l in (work/'resources.jsonl').read_text().splitlines()];res=json.loads((oldev/'result.json').read_text());svc=res['service_before_cleanup']
 assert svc['Result']=='success' and svc['ExecMainStatus']=='0' and res['workers_remaining']==[]
 peak=max(int(svc['MemoryPeak']),max(s['memory_peak'] for s in resources));assert peak==9935745024
 assert int(svc['MemorySwapPeak'])==0
 assert all(s['swap_current']==0 and not any(s['memory_events'].values()) and not any(s['pids_events'].values()) for s in resources)
 assert all(s['AC_online'] and s['inhibitor']['what']=='sleep:idle' and s['inhibitor']['mode']=='block' for s in resources)
 post=json.loads((oldev/'postflight.json').read_text());assert post['workers']['returncode']==1 and post['task_inhibitors_remaining']==[] and not post['runtime_override_exists']
 finish=json.loads((oldev/'finalization-complete.json').read_text());assert finish['elapsed']<14400
 uma={k:manifest['components'][k]['uma']['energy_eV'] for k in (prefix,prefix.replace('0.010','0.005'))}
 out={'passed':True,'substantive_blocker':None,'report_discrepancies':[], 'method':'Independent line/column/XML reconstruction, no import of earlier parser',
 'archive_sha256':receipt['sha256'],'archive_payloads_verified':len(zh),'raw_files_verified':27,'SCF_iterations':iterations,'final_error_Ry':error,
 'energy_Ry':energy,'energy_XML_Ha':xml_energy,'energy_difference_Ry':abs(energy-2*xml_energy),'electrons':522,'geometry_max_errors':errors,
 'forces':{'count':127,'max_text_XML_delta_Ry_bohr':max(r[-2] for r in table),'max_norm_eV_A':max(norms),'rms_norm_eV_A':math.sqrt(sum(v*v for v in norms)/127),'max_atom_1based':norms.index(max(norms))+1},
 'trajectory':trajectory,'peak_bytes':peak,'max_swap_bytes':0,'minimum_host_available_GiB':min(s['system_available'] for s in resources)/2**30,'maximum_tasks':max(s['tasks'] for s in resources),
 'scratch_bytes':sum(p.stat().st_size for p in (work/'scratch').rglob('*') if p.is_file()),'run_through_cleanup_s':res['time']-json.loads((work/'execution-started.json').read_text())['time'],
 'allocation_through_automatic_package_s':finish['elapsed'],'UMA_eV':uma,'UMA_second_minus_first_eV':list(uma.values())[1]-list(uma.values())[0],
 'limits':'Electronic convergence only; cutoff/grid and physical accuracy unresolved. Persistent negative pseudocharge neither automatic acceptance nor rejection.'}
 (EV/'review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['trajectory','UMA_eV']},indent=2))
if __name__=='__main__':review()
