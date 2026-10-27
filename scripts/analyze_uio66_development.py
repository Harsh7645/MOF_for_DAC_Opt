"""Offline, grouped exploratory diagnostics; never replace historical fits."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
from scipy.stats import rankdata

from mof_dac.adsorption import summarize_adsorption
from mof_dac.design_fit import evaluate_fit, freeze_split
from mof_dac.parameters import pairwise_design

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT/'plans/uio66-offline-development-v1/protocol.json'
MODELS = {'additive': 7, 'pairwise': 22}
TERMS = ['offset']+[f'h{i}' for i in range(6)]+[f'J{i}{j}' for i, j in zip(*np.triu_indices(6, 1))]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def metrics(error, groups=None):
    error = np.asarray(error, float)
    valid = np.isfinite(error)
    if not valid.any():
        return {'count': 0}
    values = error[valid]
    result = {'count': int(valid.sum()), 'bias_ev': float(values.mean()),
              'mae_ev': float(np.abs(values).mean()), 'rmse_ev': float(np.sqrt(np.mean(values**2))),
              'max_absolute_error_ev': float(np.abs(values).max())}
    if groups is not None:
        result['group_balanced_mae_ev'] = float(np.mean([
            np.abs(error[g][np.isfinite(error[g])]).mean() for g in groups if np.isfinite(error[g]).any()]))
    return result


def correlation(a, b):
    a, b = rankdata(a), rankdata(b)
    return None if np.ptp(a) == 0 or np.ptp(b) == 0 else float(np.corrcoef(a, b)[0, 1])


def solve(matrix, target):
    rank = int(np.linalg.matrix_rank(matrix))
    if rank < matrix.shape[1]:
        return None, rank
    return np.linalg.lstsq(matrix, target, rcond=None)[0], rank


def load_history(protocol):
    """Use pinned reports/cached audits; no repeated trajectory/chemistry audit."""
    fit_path, split_path = (ROOT/protocol[k] for k in ('historical_fit', 'split'))
    for path, key in ((fit_path, 'historical_fit_sha256'), (split_path, 'split_sha256')):
        if sha(path) != protocol[key]:
            raise ValueError('Frozen source hash changed: '+str(path))
    fit, split = json.loads(fit_path.read_text()), json.loads(split_path.read_text())
    inputs = {fit_path: sha(fit_path), split_path: sha(split_path), PROTOCOL: sha(PROTOCOL)}
    for name, expected in {**fit['fit_source_sha256'], **split['source_sha256']}.items():
        path = ROOT/name
        if sha(path) != expected:
            raise ValueError('Historical source changed: '+name)
        inputs[path] = expected
    manifest = json.loads((ROOT/'artifacts/phase3/uio66_structures/manifest.json').read_text())
    states = {r['id']: r['state'] for r in manifest['configurations']}
    group_lists = []
    for name in split['source_sha256']:
        if name.endswith('manifest.json'):
            continue
        group_lists.append(next(r['groups'] for r in json.loads((ROOT/name).read_text())['audits'] if r['tolerance_angstrom']==0.05))
    rebuilt = freeze_split(states, group_lists, seed=split['seed'])
    if any(split[k] != v for k, v in rebuilt.items()):
        raise ValueError('Frozen split reconstruction differs')
    rows = {}
    for name, expected in fit['report_sha256'].items():
        path = ROOT/name.replace('\\', '/')
        if sha(path) != expected:
            raise ValueError('Report hash changed')
        inputs[path] = expected
        audit_path = path.with_name('audit.json')
        cached = json.loads(audit_path.read_text())
        if cached['source_report_sha256'] != expected:
            raise ValueError('Cached audit belongs to a different report')
        inputs[audit_path] = sha(audit_path)
        audited = {r['id']: r for r in cached['results']}
        run = json.loads(path.read_text())
        for row in run['results']:
            if row['id'] in rows:
                raise ValueError('Repeated design')
            starts = sorted(row['starts'], key=lambda r: (r['gas'], r['start']))
            if {(r['gas'], r['start']) for r in starts} != {(g, i) for g in ('CO2','H2O') for i in range(4)} or len(starts)!=8:
                raise ValueError('Expected four starts per gas')
            summary = summarize_adsorption(row['bare'], run['gas_references'], starts, 4)
            if summary['status'] != 'complete_model_sample' or summary != {k:row[k] for k in summary}:
                raise ValueError('Saved energy accounting differs')
            if abs(summary['paired_target_ev']-audited[row['id']]['paired_target_ev'])>1e-12:
                raise ValueError('Cached audit label differs')
            rows[row['id']] = summary
    targets = {k: r['paired_target_ev'] for k, r in rows.items()}
    reproduced = evaluate_fit(states, targets, split, bootstrap=fit['uncertainty']['attempted'])
    # Compare coefficients, historical metrics/predictions, and original group bootstrap.
    def close(a, b):
        if isinstance(a, dict):
            return all(k in b and close(v, b[k]) for k, v in a.items())
        if isinstance(a, list):
            return len(a)==len(b) and all(close(v,w) for v,w in zip(a,b))
        if isinstance(a, (int,float)):
            return bool(np.isclose(a,b,atol=1e-11,rtol=0))
        return a==b
    if not close(reproduced, fit):
        raise ValueError('Historical numerical reproduction failed')
    return states, rows, split, reproduced, inputs


def development_analysis(states, targets, groups, protocol):
    """Boundary accepts development records ONLY. No evaluation labels or tuning."""
    ids = sorted(states)
    if set(ids) != set(targets):
        raise ValueError('State/target identities differ')
    flattened = [k for g in groups for k in g]
    if len(flattened)!=len(ids) or set(flattened)!=set(ids):
        raise ValueError('Groups must partition development IDs exactly')
    index = {k:i for i,k in enumerate(ids)}
    gi = [np.array([index[k] for k in g], int) for g in groups]
    x, y = pairwise_design([states[k] for k in ids]), np.array([targets[k] for k in ids])
    if not np.isfinite(y).all():
        raise ValueError('Nonfinite development targets')
    full = {name: solve(x[:,:n],y)[0] for name,n in MODELS.items()}
    if any(v is None for v in full.values()):
        raise ValueError('Full development design unidentified')
    rng = np.random.default_rng(protocol['seed'])
    schedules = [('leave_group_out',0,[np.array([i]) for i in range(len(gi))])]
    for repeat in range(protocol['cv']['repeats']):
        schedules.append(('repeated_group_kfold',repeat,np.array_split(rng.permutation(len(gi)), protocol['cv']['repeated_group_folds'])))
    folds, cv, logo = [], [], {}
    for method, repeat, holdouts in schedules:
        predictions = {name:np.full(len(ids),np.nan) for name in MODELS}
        for fold, group_indices in enumerate(holdouts):
            test = np.concatenate([gi[i] for i in group_indices])
            train = np.setdiff1d(np.arange(len(ids)),test)
            record = {'method':method,'repeat':repeat,'fold':fold,
                      'train_ids':[ids[i] for i in train], 'validation_ids':[ids[i] for i in test], 'models':{}}
            for name,n in MODELS.items():
                w,rank = solve(x[train,:n], y[train])
                r = {'rank':rank,'parameters':n,'status':'identifiable' if w is not None else 'rank_deficient'}
                if w is not None:
                    prediction = x[test,:n]@w
                    predictions[name][test] = prediction
                    r.update(coefficients_ev=w.tolist(), predictions_ev=prediction.tolist())
                record['models'][name]=r
            folds.append(record)
        entry = {'method':method,'repeat':repeat,'metrics':{
            name:metrics(pred-y,gi) for name,pred in predictions.items()}}
        common = np.logical_and.reduce([np.isfinite(p) for p in predictions.values()])
        entry['common_coverage'] = int(common.sum())
        entry['common_pairwise_minus_additive_mae_ev'] = float(np.mean(
            np.abs(predictions['pairwise'][common]-y[common])-np.abs(predictions['additive'][common]-y[common]))) if common.any() else None
        cv.append(entry)
        if method=='leave_group_out':
            logo = {name:[float(v) if np.isfinite(v) else None for v in pred] for name,pred in predictions.items()}
    bootstrap, samples = [], {name:[] for name in MODELS}
    # Separate deterministic RNG stream from the CV fold schedule.
    rng = np.random.default_rng(protocol['seed']+1)
    for replicate in range(protocol['bootstrap_replicates']):
        draw = rng.integers(len(gi),size=len(gi))
        selected = np.concatenate([gi[i] for i in draw])
        record = {'replicate':replicate,'draw_group_indices':draw.tolist(),'models':{}}
        for name,n in MODELS.items():
            w, rank = solve(x[selected,:n], y[selected])
            record['models'][name] = {'rank':rank,'status':'identifiable' if w is not None else 'rank_deficient'}
            if w is not None:
                samples[name].append(w)
                record['models'][name]['coefficients_ev']=w.tolist()
        bootstrap.append(record)
    stability = {}
    for name,n in MODELS.items():
        weights = np.array(samples[name])
        if len(weights)<2:
            raise ValueError('Insufficient identifiable bootstrap replicates; retain protocol and inspect')
        predicted = weights@x[:,:n].T
        ranks = np.array([rankdata(v) for v in predicted])
        base = x[:,:n]@full[name]
        top = set(np.argsort(base,kind='stable')[:10])
        overlap = [len(top & set(np.argsort(v,kind='stable')[:10]))/10 for v in predicted]
        best = Counter(ids[i] for i in np.argmin(predicted,axis=1))
        stability[name] = {'attempted':len(bootstrap),'identifiable':len(weights),
            'coefficient_percentiles_2_5_50_97_5_ev':np.percentile(weights,[2.5,50,97.5],axis=0).tolist(),
            'coefficient_positive_fraction':np.mean(weights>0,axis=0).tolist(),
            'rank_percentiles_5_50_95':np.percentile(ranks,[5,50,95],axis=0).tolist(),
            'top10_overlap_percentiles_5_50_95':np.percentile(overlap,[5,50,95]).tolist(),
            'spearman_to_full_fit_percentiles_5_50_95':np.percentile([correlation(v,base) for v in predicted],[5,50,95]).tolist(),
            'preferred_design_counts':dict(best.most_common()), 'full_fit_preferred_design':ids[int(np.argmin(base))],
            'condition_number':float(np.linalg.cond(x[:,:n]))}
    return {'ids':ids,'groups':groups,'full_coefficients_ev':{k:v.tolist() for k,v in full.items()},
            'cv':cv,'logo_predictions_ev':logo,'stability':stability}, folds, bootstrap


def sampling_analysis(ids, states, rows):
    records=[]
    for k in ids:
        r={'id':k}
        for gas in ('CO2','H2O'):
            e=rows[k]['gas_results'][gas]['sampled_adsorption_energies_ev']
            r[gas+'_two_ev'],r[gas+'_four_ev']=min(e[:2]),min(e)
            r[gas+'_four_minus_two_ev']=min(e)-min(e[:2])
            r[gas+'_four_start_range_ev']=float(np.ptp(e))
        r['delta_two_ev']=r['CO2_two_ev']-r['H2O_two_ev']
        r['delta_four_ev']=r['CO2_four_ev']-r['H2O_four_ev']
        r['delta_four_minus_two_ev']=r['delta_four_ev']-r['delta_two_ev']
        records.append(r)
    a,b=(np.array([r['delta_'+s+'_ev'] for r in records]) for s in ('two','four'))
    x=pairwise_design([states[k] for k in ids])
    fits={}
    for name,n in MODELS.items():
        wa,wb=np.linalg.lstsq(x[:,:n],a,rcond=None)[0],np.linalg.lstsq(x[:,:n],b,rcond=None)[0]
        fits[name]={'max_abs_coefficient_change_ev':float(np.max(np.abs(wb-wa))),
                    'coefficient_four_minus_two_ev':(wb-wa).tolist(),
                    'predicted_rank_spearman':correlation(x[:,:n]@wa,x[:,:n]@wb)}
    return {'records':records,'delta_change':metrics(b-a),
            'CO2_change':metrics([r['CO2_four_minus_two_ev'] for r in records]),
            'H2O_change':metrics([r['H2O_four_minus_two_ev'] for r in records]),
            'sampled_target_spearman':correlation(a,b),
            'sampled_top10_overlap':len(set(np.argsort(a,kind='stable')[:10]) & set(np.argsort(b,kind='stable')[:10]))/10,
            'exploratory_fits_development_only':fits}


def save_csv(path, rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    protocol=json.loads(PROTOCOL.read_text())
    states,rows,split,reproduced,inputs=load_history(protocol)
    write_json(args.output/'historical_reproduction.json',reproduced)
    write_json(args.output/'exact_split.json',split)
    development=set(split['train_ids'])
    ds={k:states[k] for k in sorted(development)}
    dt={k:rows[k]['paired_target_ev'] for k in ds}
    groups=[g for g in split['groups'] if set(g)<=development]
    analysis,folds,bootstrap=development_analysis(ds,dt,groups,protocol)
    sampling=sampling_analysis(analysis['ids'],ds,rows)
    residuals=[]
    group_id={k:i for i,g in enumerate(split['groups']) for k in g}
    for k in sorted(states):
        x=pairwise_design([states[k]])[0]
        r={'id':k,'pattern':k.rsplit('_',1)[1],'amino_count':sum(states[k]),'duplicate_group':group_id[k],
           'split':'development' if k in development else 'historical_evaluation','target_ev':rows[k]['paired_target_ev']}
        for name,n in MODELS.items():
            r[name+'_prediction_ev']=float(x[:n]@analysis['full_coefficients_ev'][name])
            r[name+'_residual_ev']=r[name+'_prediction_ev']-r['target_ev']
            pred=analysis['logo_predictions_ev'][name][analysis['ids'].index(k)] if k in development else None
            r[name+'_logo_residual_ev']=pred-r['target_ev'] if pred is not None else None
        residuals.append(r)
    grouped=[]
    for scope in ('development','historical_evaluation'):
        for count in range(7):
            selected=[r for r in residuals if r['split']==scope and r['amino_count']==count]
            if not selected:continue
            for name in MODELS:
                grouped.append({'split':scope,'amino_count':count,'model':name,
                    **metrics([r[name+'_residual_ev'] for r in selected]),
                    'logo':metrics([r[name+'_logo_residual_ev'] if r[name+'_logo_residual_ev'] is not None else np.nan for r in selected])})
    # Largest historical contributions are descriptive, never used to alter fitting.
    hist=[dict(r,pairwise_minus_additive_abs_error_ev=abs(r['pairwise_residual_ev'])-abs(r['additive_residual_ev']))
          for r in residuals if r['split']=='historical_evaluation']
    analysis['historical_error_contributions']=sorted(hist,key=lambda r:r['pairwise_minus_additive_abs_error_ev'],reverse=True)
    analysis['residuals_by_amino_count']=grouped
    analysis['sampling_sensitivity']=sampling
    save_csv(args.output/'residuals_by_pattern.csv',residuals)
    write_json(args.output/'analysis.json',analysis)
    write_json(args.output/'cv_folds.json',folds)
    write_json(args.output/'bootstrap_fits.json',bootstrap)
    from scripts.plot_uio66_development import plot
    plot(args.output,analysis,residuals,reproduced)
    for path in (Path(__file__),ROOT/'scripts/plot_uio66_development.py'):
        inputs[path]=sha(path)
    if any(sha(p)!=v for p,v in inputs.items()):
        raise ValueError('An input changed during analysis')
    write_json(args.output/'receipt.json',{'scope':'exploratory offline development; no historical replacement',
        'python':platform.python_version(),'numpy':np.__version__,
        'inputs':{p.relative_to(ROOT).as_posix():v for p,v in inputs.items()},
        'outputs':{p.name:sha(p) for p in sorted(args.output.iterdir()) if p.is_file()}})
    print(json.dumps({'historical_reproduction':'pass','development_count':len(ds),'groups':len(groups),
                      'logo':analysis['cv'][0],'bootstrap_identifiable':{k:v['identifiable'] for k,v in analysis['stability'].items()}}))


if __name__=='__main__':
    main()
