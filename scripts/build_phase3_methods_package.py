"""Render saved evidence only: no solver, fit, inference or geometry calculation."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DEV='plans/uio66-offline-development-v1/results/'
SOURCES={
    'synthetic':'docs/phase3_results.json',
    'case':'docs/uio66_design_results.json',
    'development':DEV+'analysis.json',
    'historical':DEV+'historical_reproduction.json',
    'split':DEV+'exact_split.json',
    'pilot':'artifacts/phase3/uio66_saved_pilot_results_20261004/local_assessment.json',
    'matched':'artifacts/phase3/uio66_matched_v2_results_20261005/local_assessment.json',
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def synthetic_table(data):
    rows=[]
    for bits,summary in data['heldout']['summary_by_bits'].items():
        cases=[r for r in data['heldout']['instances'] if r['bits']==int(bits)]
        rows.append(dict(bits=int(bits),method='Gurobi reference',budget='30 s limit; 1 thread',runs=len(cases),
                         continuous_feasible=None,binary_feasible=summary['certified_references'],
                         optimum_hits=summary['certified_references'],mean_gap_synthetic_units=0.0))
        for steps,gap in summary['sa_gap_by_steps'].items():
            runs=[r for c in cases for r in c['sa_runs'] if r['steps']==int(steps)]
            rows.append(dict(bits=int(bits),method='SA',budget=steps+' steps; 3 seeds/instance',runs=len(runs),
                             continuous_feasible=None,binary_feasible=sum(r['feasible'] for r in runs),
                             optimum_hits=gap['optimum_hits'],mean_gap_synthetic_units=gap['mean']))
        snn=[c['snn_run'] for c in cases]
        rows.append(dict(bits=int(bits),method='SNN raw',budget='2000 iterations; 1 deterministic start/instance',runs=len(snn),
                         continuous_feasible=sum(r['raw_feasible'] for r in snn),
                         binary_feasible=sum(r['raw_feasible'] and r['raw_violations']['integrality']<=1e-7 for r in snn),
                         optimum_hits=None,mean_gap_synthetic_units=None))
        gap=summary['snn_decoded_gap']
        rows.append(dict(bits=int(bits),method='SNN decoded',budget='same raw runs; exact-count decoder',runs=len(snn),
                         continuous_feasible=None,binary_feasible=sum(r['decoded_feasible'] for r in snn),
                         optimum_hits=gap['optimum_hits'],mean_gap_synthetic_units=gap['mean']))
    return rows


def save_table(output,name,rows):
    with (output/(name+'.csv')).open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    def display(v):
        return 'not scored' if v is None else f'{v:.6g}' if isinstance(v,float) else str(v)
    lines=['| '+' | '.join(rows[0])+' |','|'+'---|'*len(rows[0])]
    lines.extend('| '+' | '.join(display(v) for v in row.values())+' |' for row in rows)
    (output/(name+'.md')).write_text('\n'.join(lines)+'\n',encoding='utf-8')


def build(output, source_package=None):
    if source_package is not None:
        receipt = json.loads((source_package/'receipt.json').read_text())
        for name, expected in receipt['outputs'].items():
            if sha(source_package/name) != expected:
                raise ValueError('Snapshot package hash mismatch: '+name)
    output.mkdir(parents=True,exist_ok=False)
    paths={k:(ROOT/v if source_package is None else source_package/'inputs'/(k+'.json')).resolve()
           for k,v in SOURCES.items()}
    inputs={p:sha(p) for p in paths.values()}
    data={k:json.loads(p.read_text()) for k,p in paths.items()}
    syn=synthetic_table(data['synthetic']);save_table(output,'T1_synthetic',syn)
    case=[]
    budgets={'Gurobi':'60 s limit;1 thread','SA':'2000 steps/seed',
             'SNN_raw':'2000 iteration cap/seed','SNN_threshold':'same raw runs; threshold=0.5'}
    for name,row in data['case']['solver_comparison']['summary'].items():
        case.append({'method':name,'budget':budgets[name],**row})
    save_table(output,'T2_six_bit_objective',case)
    hist=data['historical'];dev=data['development'];rows=[]
    for model in ('additive','pairwise'):
        for split in ('train','test'):
            r=hist[model+'_'+split]
            rows.append({'model':model,'scope':'historical development fit' if split=='train' else 'historical exposed evaluation',
                         'MAE_meV':1000*r['mae_ev'],'RMSE_meV':1000*r['rmse_ev']})
        r=dev['cv'][0]['metrics'][model]
        rows.append({'model':model,'scope':'development leave-group-out', 'MAE_meV':1000*r['mae_ev'],'RMSE_meV':1000*r['rmse_ev']})
        rows.append({'model':model,'scope':'development repeated group CV median',
                     'MAE_meV':float(np.median([r['metrics'][model]['mae_ev'] for r in dev['cv'][1:]]))*1000,
                     'RMSE_meV':float(np.median([r['metrics'][model]['rmse_ev'] for r in dev['cv'][1:]]))*1000})
    save_table(output,'T3_surrogate',rows)
    save_table(output,'T4_stability',[{'model':model,'bootstrap_attempts':s['attempted'],
        'identifiable':s['identifiable'],'top10_overlap_median':s['top10_overlap_percentiles_5_50_95'][1],
        'rank_spearman_to_full_fit_median':s['spearman_to_full_fit_percentiles_5_50_95'][1],
        'distinct_preferred_patterns':len(s['preferred_design_counts'])} for model,s in dev['stability'].items()])
    pilot=data['pilot']['stability'];rows=[]
    for r in pilot['configurations']:
        rows.append({'pattern':r['id'][-6:],'CO2_batch_gap_meV':r['absolute_batch_adsorption_difference_ev']['CO2']*1000,
            'H2O_batch_gap_meV':r['absolute_batch_adsorption_difference_ev']['H2O']*1000,
            'paired_batch_gap_meV':r['absolute_batch_delta_difference_ev']*1000,
            'full_energy_gate_pass':r['energy_target_met']})
    save_table(output,'T5_sampling',rows)
    save_table(output,'T6_relaxation',[{'path':r['id'],'status':r['status'],
        'last_change_meV':r['last_change_ev']*1000,'initial_5meV_target_pass':r['initial_target_met']}
        for r in data['matched']['components']])
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.hashsalt':'phase3-methods-v1'})
    def save(fig,name):
        fig.savefig(output/(name+'.png'),dpi=300,bbox_inches='tight')
        fig.savefig(output/(name+'.svg'),bbox_inches='tight',metadata={'Date':None})
        plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.2),layout='constrained')
    for steps,color in [('250','#92bad1'),('1000','#408cb5'),('4000','#174b73')]:
        subset=[r for r in syn if r['method']=='SA' and r['budget'].startswith(steps+' ')]
        axes[0].plot([r['bits'] for r in subset],[100*r['optimum_hits']/r['runs'] for r in subset],'-o',color=color,label=f'SA: {steps} steps, 3 seeds')
    subset=[r for r in syn if r['method']=='SNN decoded']
    axes[0].plot([r['bits'] for r in subset],[100*r['optimum_hits']/r['runs'] for r in subset],'-s',color='#c26124',label='Decoded SNN: 2000 iterations, 1 start')
    axes[0].set(xlabel='Binary variables',ylabel='Optimum hits (%)',xticks=[12,20,50],ylim=(-3,105),title='Fixed synthetic objectives; unequal budgets')
    axes[0].legend(fontsize=8)
    for name,marker,color in [('SNN raw','o','#c26124'),('SNN decoded','s','#26784c')]:
        subset=[r for r in syn if r['method']==name]
        axes[1].plot([r['bits'] for r in subset],[100*r['binary_feasible']/r['runs'] for r in subset],'-'+marker,color=color,label=name)
    axes[1].set(xlabel='Binary variables',ylabel='Binary feasible outputs (%)',xticks=[12,20,50],ylim=(-3,105),title='Raw and decoded outputs are distinct')
    axes[1].legend();save(fig,'F1_solver_outputs')
    fig,ax=plt.subplots(figsize=(9,4.2),layout='constrained');positions=np.arange(8)
    for offset,key,color,label in [(-.24,'CO2_batch_gap_meV','#2678b2','CO2'),(0,'H2O_batch_gap_meV','#d26728','H2O'),(.24,'paired_batch_gap_meV','#4c956c','paired score')]:
        ax.bar(positions+offset,[r[key] for r in rows],width=.23,label=label,color=color)
    ax.axhline(10,color='black',ls='--',lw=1,label='Initial 10 meV target (part of full gate)')
    ax.set(xticks=positions,xticklabels=[r['pattern'] for r in rows],ylabel='Absolute independent-batch difference (meV)',title='Eight-design UMA sampling pilot: instability, not uncertainty calibration')
    ax.legend(fontsize=8,ncol=2);save(fig,'F4_sampling_batches')
    # Reuse the verified exploratory figures byte-for-byte; do not rerun fits.
    for stem,destination in [('fit_and_grouped_cv','F2_surrogate_adequacy'),('coefficient_stability','F3_coefficients'),
                             ('residual_patterns','S1_pattern_residuals'),('development_rank_stability','S2_conditional_ranks'),
                             ('sampling_vs_fitting','S3_nested_sampling')]:
        for extension in ('png','svg'):
            p=(ROOT/DEV/(stem+'.'+extension) if source_package is None else source_package/(destination+'.'+extension)).resolve()
            inputs[p]=sha(p);shutil.copy2(p,output/(destination+'.'+extension))
    snapshots=output/'inputs';snapshots.mkdir()
    for name,path in paths.items():shutil.copy2(path,snapshots/(name+'.json'))
    inputs[Path(__file__)]=sha(Path(__file__))
    if any(sha(p)!=v for p,v in inputs.items()):raise ValueError('Input changed during packaging')
    receipt={'mode':'saved-results aggregation only; no new fits/calculations',
        'inputs':{(p.relative_to(ROOT) if p.is_relative_to(ROOT) else p).as_posix():v for p,v in inputs.items()},
        'outputs':{p.relative_to(output).as_posix():sha(p) for p in sorted(output.rglob('*')) if p.is_file()}}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tables':6,'figures':7,'inputs':len(inputs),'payloads':len(receipt['outputs'])}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source-package',type=Path,help='Verified saved evidence package; avoids original raw-archive paths')
    args=parser.parse_args();build(args.output,args.source_package)
