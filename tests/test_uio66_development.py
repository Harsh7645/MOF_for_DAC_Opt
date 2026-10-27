"""Development-only resampling boundaries and fixed-label diagnostics."""
import json
from pathlib import Path

import numpy as np
import pytest

from scripts.analyze_uio66_development import development_analysis, metrics, sampling_analysis, solve

ROOT=Path(__file__).resolve().parents[1]


def fixture():
    split=json.loads((ROOT/'data/design/uio66_fit_split.json').read_text())
    states={k:list(map(int,k[-6:])) for k in split['train_ids']}
    targets={k:float(np.dot(v,np.arange(1,7))*.01+.017*v[0]*v[1]+.003*np.sin(int(k[-6:],2))) for k,v in states.items()}
    groups=[g for g in split['groups'] if set(g)<=set(states)]
    protocol={'seed':20261026,'cv':{'repeats':2,'repeated_group_folds':5},'bootstrap_replicates':12}
    return split,states,targets,groups,protocol


def test_groups_and_historical_evaluation_never_cross_new_fit_boundaries():
    split,states,targets,groups,protocol=fixture()
    analysis,folds,draws=development_analysis(states,targets,groups,protocol)
    historical=set(split['test_ids'])
    assert set(analysis['ids']).isdisjoint(historical)
    for fold in folds:
        train,validation=set(fold['train_ids']),set(fold['validation_ids'])
        assert train.isdisjoint(validation|historical)
        assert validation.isdisjoint(historical)
        assert train|validation==set(states)
        assert all(not(set(g)&train and set(g)&validation) for g in groups)
    assert len(draws)==12
    assert all(set(g).isdisjoint(historical) for d in draws for i in d['draw_group_indices'] for g in [groups[i]])


def test_fold_coefficients_do_not_see_held_group_labels():
    _,states,targets,groups,protocol=fixture()
    _,first,_=development_analysis(states,targets,groups,protocol)
    changed=dict(targets)
    for key in groups[0]:changed[key]+=10
    _,second,_=development_analysis(states,changed,groups,protocol)
    assert first[0]['validation_ids']==groups[0]
    assert first[0]['models']==second[0]['models']
    assert [(f['train_ids'],f['validation_ids']) for f in first]==[(f['train_ids'],f['validation_ids']) for f in second]


def test_group_coverage_and_rank_deficiency_fail_closed():
    _,states,targets,groups,protocol=fixture()
    with pytest.raises(ValueError,match='partition'):
        development_analysis(states,targets,groups[:-1],protocol)
    weights,rank=solve(np.ones((5,3)),np.arange(5))
    assert weights is None and rank==1


def test_sampling_components_can_change_while_paired_difference_cancels():
    _,states,_,_,_=fixture()
    ids=sorted(states)
    rows={k:{'gas_results':{
        'CO2':{'sampled_adsorption_energies_ev':[-.2,-.3,-.4,-.5]},
        'H2O':{'sampled_adsorption_energies_ev':[-.1,-.2,-.3,-.4]}}} for k in ids}
    result=sampling_analysis(ids,states,rows)
    assert result['CO2_change']['mae_ev']==pytest.approx(.2)
    assert result['H2O_change']['mae_ev']==pytest.approx(.2)
    assert result['delta_change']['mae_ev']==pytest.approx(0,abs=1e-14)


def test_metrics_preserve_signed_bias_and_group_weighting():
    result=metrics([1.,1.,-1.],groups=[np.array([0,1]),np.array([2])])
    assert result['bias_ev']==pytest.approx(1/3)
    assert result['group_balanced_mae_ev']==1
