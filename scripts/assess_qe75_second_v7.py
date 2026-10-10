"""Offline v2 reassessment: delimit total forces from verbosity-high components.
Original v1 assessment, scripts and review archive remain preserved. Never invokes QE.
"""
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from qe75_fedora_v1 import ROOT,sha
from run_qe_water_pilot import parse_result,BOHR_A,RY_EV
from assess_qe75_rho625_v1 import parse


def assess():
    c=json.loads((ROOT/'configs/qe75-second-v7.json').read_text())
    work,ev=ROOT/c['work_root'],Path(c['evidence_root'])
    result=json.loads((ev/'result.json').read_text())
    text=(work/'stdout.log').read_text();err=(work/'stderr.log').read_text()
    samples=[json.loads(l) for l in (work/'resources.jsonl').read_text().splitlines() if l]
    info=parse(work/'stdout.log')
    start=json.loads((work/'execution-started.json').read_text())
    pkg=ROOT/c['package'];manifest=json.loads((pkg/'manifest.json').read_text())
    prefix='uio66_110111_H2O_s28_f0.005_complex';comp=manifest['components'][prefix]
    geometry=json.loads((pkg/comp['geometry_file']).read_text())
    geometry['symbols']=next(p for p in manifest['poses'] if p['id']==comp['pose'])['atom_symbols']
    peak=max([0]+[s['memory_peak'] for s in samples])
    value=result.get('service_before_cleanup',{}).get('MemoryPeak','')
    if value.isdigit() and int(value)<2**60:peak=max(peak,int(value))
    output={'ready_for_independent_assessment':False,'scientific_accuracy_validated':False,
        'accepted_converged_SCF_energy':False,'output_summary':info,'peak_GiB':peak/2**30,'peak_bytes':peak,
        'maximum_swap_bytes':max(s['swap_current'] for s in samples),
        'memory_events':{k:max(s['memory_events'].get(k,0) for s in samples) for k in ['high','max','oom','oom_kill','oom_group_kill']},
        'maximum_tasks':max(s['tasks'] for s in samples),'minimum_host_available_GiB':min(s['system_available'] for s in samples)/2**30,
        'scratch_bytes':sum(p.stat().st_size for p in (work/'scratch').rglob('*') if p.is_file()),
        'run_to_cleanup_seconds':result['time']-start['time'],'allocation_to_worker_cleanup_seconds':result['allocation_elapsed'],
        'checks':{},'validation_failure':None,'restart_decision':'clean second-geometry start; no first-geometry or 625 checkpoint reused',
        'termination_reason':result['termination_reason'],'service':result.get('service_before_cleanup',{}),
        'final_negative_pseudocharge_electrons':info['observations'][-1]['negative_electrons'] if info['observations'] else None}
    before=result.get('service_before_cleanup',{})
    terminal=before if before.get('SubState')=='exited' and before.get('ExecMainCode')=='1' else result.get('service',{})
    output['service']=terminal
    checks=output['checks']
    try:
        assert c['authorization_consumed'] and not c['attempt_approved']
        baseline=ROOT/'evidence/qe75-second-v6/second-input.in'
        assert (work/'input.in').read_bytes()==baseline.read_bytes()
        assert sha(work/'input.in')==start['input_sha256']
        checks['input_byte_identical_to_reviewed_second600']=True
        hashes=json.loads((pkg/'file_hashes.json').read_text())
        for p in (work/'pseudo').iterdir():
            if p.is_file():assert sha(p)==hashes['pseudo/'+p.name]
        checks['potential_hashes']=True
        assert terminal.get('ExecMainStatus')=='0','Worker exit failure'
        assert terminal.get('Result')=='success','Service failure'
        assert output['maximum_swap_bytes']==0 and not any(output['memory_events'].values()),'Resource event'
        assert not any(any(s['pids_events'].values()) for s in samples),'Task-limit event'
        assert result['allocation_elapsed']<=14100,'Worker cleanup deadline exceeded'
        assert not result['workers_remaining']
        assert not re.search(r'Error in routine|MPI_ABORT|segmentation fault|SIGSEGV|forrtl: severe',text+err,re.I)
        checks['process_and_resource_success']=True
        xml=work/'scratch'/(prefix+'.save')/'data-file-schema.xml'
        parsed=parse_result(text,xml,geometry,522,4)
        tree=ET.parse(xml).getroot()
        for node in tree.iter():node.tag=node.tag.split('}')[-1]
        get=lambda p:tree.findtext(p).strip()
        required={'input/control_variables/restart_mode':'from_scratch','input/control_variables/disk_io':'high',
          'input/control_variables/forces':'true','input/electron_control/diagonalization':'cg',
          'input/electron_control/mixing_ndim':'4','input/bands/occupations':'fixed',
          'output/basis_set/gamma_only':'true','output/dft/functional':'PBE',
          'output/dft/vdW/vdw_corr':'grimme-d3','output/dft/vdW/dftd3_version':'4',
          'output/dft/vdW/dftd3_threebody':'false','output/magnetization/lsda':'false'}
        for p,v in required.items():assert get(p)==v,p
        for p,v in [('input/electron_control/conv_thr',5e-9),('input/electron_control/mixing_beta',.3),
                    ('input/bands/tot_charge',0),('output/basis_set/ecutwfc',40),('output/basis_set/ecutrho',300)]:
            assert math.isclose(float(get(p)),v,rel_tol=1e-12,abs_tol=1e-15),p
        scf_error=2*float(get('output/convergence_info/scf_conv/scf_error'))
        assert math.isfinite(scf_error) and 0<=scf_error<=1e-8
        checks['final_SCF_error_Ry']=scf_error
        checks['settings_electrons_and_convergence']=True
        geometry_errors={}
        for sec in ['input','output']:
            st=tree.find(sec+'/atomic_structure');atoms=st.findall('atomic_positions/atom')
            assert len(atoms)==127 and [p.attrib['name'] for p in atoms]==geometry['symbols']
            pos=[[float(v)*BOHR_A for v in p.text.split()] for p in atoms]
            cell=[[float(v)*BOHR_A for v in st.findtext('cell/'+k).split()] for k in ['a1','a2','a3']]
            for label,actual,expected in [('coordinates',pos,geometry['positions_A']),('cell',cell,geometry['cell_A'])]:
                delta=max(abs(x-y) for a,b in zip(actual,expected) for x,y in zip(a,b))
                assert math.isfinite(delta) and delta<=2e-8
                geometry_errors[sec+'_'+label+'_max_error_A']=delta
        checks['geometry']=geometry_errors
        # QE 7.5 PW/src/forces.f90 prints total forces, then component tables.
        blocks=re.findall(r'Forces acting on atoms \(cartesian axes, Ry/au\):\s*\n((?:\s*atom[^\n]*\n)+)',text)
        assert len(blocks)==1, 'Expected one final total-force block'
        rows=re.findall(r'atom\s+(\d+)\s+type\s+(\d+)\s+force\s*=\s*([-+\d.EeDd]+)\s+([-+\d.EeDd]+)\s+([-+\d.EeDd]+)',blocks[0])
        assert len(rows)==127, 'Expected 127 total forces'
        xf=[[float(v)*2 for v in line.split()] for line in get('output/forces').splitlines() if line.strip()]
        assert len(xf)==127 and all(len(r)==3 and all(math.isfinite(v) for v in r) for r in xf)
        types=[p.attrib['name'] for p in tree.findall('input/atomic_species/species')]
        differences=[];norms=[]
        for i,(row,xrow) in enumerate(zip(rows,xf)):
            assert int(row[0])==i+1 and types[int(row[1])-1]==geometry['symbols'][i]
            values=[float(v.replace('D','E')) for v in row[2:]]
            assert all(math.isfinite(v) for v in values)
            differences.extend(abs(x-y) for x,y in zip(values,xrow))
            norms.append(math.sqrt(sum(v*v for v in values))*RY_EV/BOHR_A)
        assert max(differences)<=2e-7,'Text/XML force mismatch'
        checks['forces']={'count':127,'finite':True,'max_text_XML_difference_Ry_bohr':max(differences),
                          'max_norm_eV_A':max(norms),'rms_norm_eV_A':math.sqrt(sum(v*v for v in norms)/127),
                          'max_atom_index_1based':norms.index(max(norms))+1,'large_force_is_not_automatic_failure':True}
        final_iter=re.split(r'iteration #\s*\d+',text)[-1]
        assert not re.search(r'eigenvalues not converged|c_bands.*not converged',final_iter,re.I),'Unresolved final diagonalization warning'
        checks['final_diagonalization_clear']=True
        energy=float(re.findall(r'!\s+total energy\s*=\s*([-+\d.EeDd]+)\s+Ry',text)[-1].replace('D','E'))
        checks['energy']={'text_Ry':energy,'XML_Ha':float(get('output/total_energy/etot')),
                         'difference_Ry':abs(energy-2*float(get('output/total_energy/etot'))),
                         'convention':'total SCF including D3(BJ); no separate dispersion addition'}
        output.update(ready_for_independent_assessment=True,accepted_converged_SCF_energy=True)
        (ev/'completed-SCF-pending-independent-assessment.json').write_text(json.dumps(parsed,indent=2)+'\n')
    except (AssertionError,ValueError,KeyError,AttributeError,FileNotFoundError,ET.ParseError) as e:
        output['validation_failure']=type(e).__name__+': '+str(e)
    output['assessment_note']='Corrected total-force parser, verified independently on first geometry; second input/geometry independently checked here.'
    (ev/'assessment.json').write_text(json.dumps(output,indent=2)+'\n')
    return output


if __name__=='__main__':
    a=assess();print(json.dumps({k:a[k] for k in ['ready_for_independent_assessment','validation_failure','peak_GiB','run_to_cleanup_seconds','final_negative_pseudocharge_electrons']},indent=2))
