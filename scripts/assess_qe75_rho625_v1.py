"""Read-only scientific comparison of retained 600/625-Ry diagnostic outputs.

Writes assessment evidence, never launches software or accepts partial energies.
"""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def parse(path):
    text=path.read_text(errors='replace')
    observations=[]; stage=0
    for number,line in enumerate(text.splitlines(),1):
        m=re.search(r'iteration #\s*(\d+)',line)
        if m: stage=int(m.group(1))
        m=re.search(r'negative rho \(up, down\):\s*([\d.EeDd+-]+)\s*([\d.EeDd+-]+)',line)
        if m:
            observations.append({'iteration':stage,'negative_electrons':float(m.group(1).replace('D','E')),
                                 'second_component':float(m.group(2).replace('D','E')),'negative_line':number,
                                 'estimated_scf_error_Ry':None})
        timing=re.search(r'total cpu time spent up to now is\s*([\d.]+) secs',line)
        if timing:
            row=next((r for r in reversed(observations) if r['iteration']==stage),None)
            if row is not None:row['cumulative_QE_CPU_seconds']=float(timing.group(1))
        m=re.search(r'estimated scf accuracy\s*<\s*([\d.EeDd+-]+) Ry',line)
        if m:
            row=next((r for r in reversed(observations) if r['iteration']==stage),None)
            if row is None:
                row={'iteration':stage,'negative_electrons':None};observations.append(row)
            row.update(estimated_scf_error_Ry=float(m.group(1).replace('D','E')),error_line=number)
    grids={}
    for kind,count,x,y,z in re.findall(r'(Dense|Smooth)\s+grid:\s*(\d+) G-vectors\s+FFT dimensions:\s*\(\s*(\d+),\s*(\d+),\s*(\d+)\)',text):
        grids[kind]={'G_vectors':int(count),'FFT_dimensions':[int(x),int(y),int(z)]}
    starts=[line.strip() for line in text.splitlines() if 'starting charge' in line or 'Starting wfcs' in line]
    complete=[r for r in observations if r.get('estimated_scf_error_Ry') is not None]
    return {'path':str(path.relative_to(ROOT)),'observations':observations,'completed_iterations':len(complete),
            'iterations_started':max([0]+[int(x) for x in re.findall(r'iteration #\s*(\d+)',text)]),
            'grids':grids,'initialization_messages':starts,
            'SCF_convergence_reported':'convergence has been achieved' in text,
            'JOB_DONE':'JOB DONE.' in text,'forces_present':'Forces acting on atoms' in text,
            'warnings':[line.strip() for line in text.splitlines() if re.search(r'Warning|eigenvalues not converged|Error in routine',line,re.I)],
            'timings':[line.strip() for line in text.splitlines() if re.search(r'PWSCF\s*:|total cpu time|convergence NOT achieved|Maximum CPU time|stopping',line,re.I)]}


def main():
    ev=ROOT/'evidence/qe75-rho625-run02'; work=ROOT/'local/qe75-rho625-v1/run02'
    result=json.loads((ev/'result.json').read_text())
    ref=parse(ROOT/'local/qe75-fedora-completion-v3/run01/stdout.log')
    probe=parse(work/'stdout.log')
    rows=[]
    for baseline in ref['observations']:
        n=baseline['iteration']
        if n>4:continue
        found=next((r for r in probe['observations'] if r['iteration']==n),None)
        comparison={'iteration':n,'baseline':baseline,'probe':found}
        if found and found.get('negative_electrons') is not None:
            delta=found['negative_electrons']-baseline['negative_electrons']
            comparison.update(negative_delta_electrons=delta,negative_relative_change_percent=100*delta/baseline['negative_electrons'])
        rows.append(comparison)
    samples=[json.loads(line) for line in (work/'resources.jsonl').read_text().splitlines() if line]
    peak=max([0]+[s['memory_peak'] for s in samples])
    for key in ['service','service_before_cleanup']:
        value=result.get(key,{}).get('MemoryPeak','')
        if value.isdigit() and int(value)<2**60:peak=max(peak,int(value))
    final=result.get('final_cgroup',{})
    if final.get('memory.peak','').strip().isdigit():peak=max(peak,int(final['memory.peak']))
    marker=json.loads((work/'execution-started.json').read_text())
    baseline_input=(ROOT/'local/qe75-fedora-completion-v3/run01/input.in').read_text()
    assert (work/'input.in').read_text()==baseline_input.replace('ecutrho=600','ecutrho=625').replace('max_seconds=12948','max_seconds=1350')
    assessment={'scope':'ONE80/625Ry diagnostic; no accepted scientific energy',
       'baseline':ref,'probe':probe,'comparison':rows,'initialization_messages_equal':ref['initialization_messages']==probe['initialization_messages'],
       'input_identity_verified':True,'only_scientific_change':'ecutrho600->625',
       'execution_input_change':'max_seconds12948->1350','scratch_reused':False,
       'peak_bytes':peak,'peak_GiB':peak/2**30,'maximum_sampled_swap_bytes':max([0]+[s['swap_current'] for s in samples]),
       'maximum_memory_events':{k:max([0]+[s['memory_events'].get(k,0) for s in samples]) for k in ['high','max','oom','oom_kill','oom_group_kill']},
       'minimum_host_available_GiB':min(s['system_available'] for s in samples)/2**30,
       'scratch_bytes':sum(p.stat().st_size for p in (work/'scratch').rglob('*') if p.is_file()),
       'run_to_cleanup_seconds':result['time']-marker['time'],'allocation_to_worker_cleanup_seconds':result['allocation_elapsed'],
       'terminal_result':result,'scientific_energy_accepted':False,
       'remaining_uncertainty':['Short unconverged densities do not establish accurate energies or forces.',
          '625Ry retains225^3FFT; unchanged printed negative charge cannot exclude larger-cutoff or FFT-grid sensitivity.',
          'Identical starting controls/messages do not establish bitwise-identical distributed initial wavefunctions.',
          'Full SCF convergence, later-stage memory, cutoff/k-point convergence and UMA accuracy remain unresolved.']}
    (ev/'assessment.json').write_text(json.dumps(assessment,indent=2)+'\n')
    print(json.dumps({k:assessment[k] for k in ['peak_GiB','maximum_sampled_swap_bytes','maximum_memory_events','scratch_bytes','run_to_cleanup_seconds','allocation_to_worker_cleanup_seconds','initialization_messages_equal']},indent=2))
    print(json.dumps(rows,indent=2))


if __name__=='__main__':main()
