import json
from pathlib import Path
import numpy as np
import pytest
from ase import Atoms
from ase.calculators.calculator import Calculator, all_changes
from ase.io import read
from mof_dac.matched_diagnostic import staged_path
from mof_dac.geometry_diagnostic import guest_geometry, mic
from scripts.prepare_uio66_matched_diagnostic import select_paths
from scripts.run_uio66_matched_diagnostic import validate
from scripts.assess_uio66_matched_diagnostic import assess


class Harmonic(Calculator):
    implemented_properties=['energy','forces']
    def __init__(self, target):
        super().__init__();self.target=np.asarray(target)
    def calculate(self,atoms=None,properties=('energy','forces'),system_changes=all_changes):
        super().calculate(atoms,properties,system_changes)
        d=atoms.positions-self.target;self.results={'energy':float(.5*np.sum(d*d)),'forces':-d}


def test_staged_history_matches_uninterrupted(tmp_path):
    a=Atoms('He2',positions=[[0,0,0],[4,0,0]],cell=[20]*3,pbc=True)
    target=a.positions+[[.8,.2,0],[-.2,.4,0]]
    staged=staged_path(a,Harmonic(target),tmp_path/'staged')
    direct=staged_path(a,Harmonic(target),tmp_path/'direct',direct=True)
    assert staged['status']==direct['status']=='complete'
    assert staged['steps']==direct['steps']
    s,d=read(tmp_path/'staged/path.traj',':'),read(tmp_path/'direct/path.traj',':')
    assert len(s)==len(d)
    assert all(np.allclose(x.positions,y.positions,atol=1e-12) for x,y in zip(s,d))
    assert [c['tolerance'] for c in staged['checkpoints']]==[.02,.01,.005]
    assert all(c['optimizer_iteration']==c['step'] for c in staged['checkpoints'])


def test_rigid_host_and_raw_host_force_retained(tmp_path):
    a=Atoms('He2',positions=[[0,0,0],[4,0,0]],cell=[20]*3,pbc=True)
    r=staged_path(a,Harmonic(a.positions+1),tmp_path/'rigid',rigid_host_atoms=1)
    assert r['status']=='complete'
    final=read(tmp_path/'rigid/last_state.traj')
    assert np.array_equal(final.positions[0],a.positions[0])
    assert r['checkpoints'][-1]['all_atom_fmax_ev_A']>1
    assert r['checkpoints'][-1]['mobile_fmax_ev_A']<.005


def test_limits_and_no_overwrite(tmp_path):
    a=Atoms('He',positions=[[0,0,0]],cell=[20]*3,pbc=True)
    r=staged_path(a,Harmonic([[3,0,0]]),tmp_path/'limit',max_steps=1)
    assert r['status']=='step_limit' and r['steps']==1
    assert (tmp_path/'limit/path.traj').exists()
    with pytest.raises(FileExistsError):staged_path(a,Harmonic([[3,0,0]]),tmp_path/'limit')
    r=staged_path(a,Harmonic([[3,0,0]]),tmp_path/'time',max_seconds=-1)
    assert r['status']=='failed' and 'TimeoutError' in r['error']


def test_scientific_hold_retains_unusual_state(tmp_path):
    a=Atoms('He2',positions=[[0,0,0],[.5,0,0]],cell=[20]*3,pbc=True)
    r=staged_path(a,Harmonic(a.positions),tmp_path/'clash')
    assert r['status']=='scientific_hold'
    assert (tmp_path/'clash/last_state.traj').exists()


def test_periodic_guest_geometry():
    a=Atoms('CO2',positions=[[9.8,0,0],[8.6,0,0],[1.,0,0]],cell=[10]*3,pbc=True)
    com,axis,_=guest_geometry(a)
    assert np.allclose(com,[9.8,0,0]);assert np.allclose(axis,[1,0,0])
    assert np.allclose(mic(a,[[10.2,0,0]]),[[.2,0,0]])


def test_selection_is_stratified_and_replay_original():
    starts=[]
    for gas in ('CO2','H2O'):
        for i in range(32):starts.append({'status':'accepted','gas':gas,'start':i,
          'placement':{'batch':i//16,'site_class':'random_void' if i%16>=8 else 'node_OH'},
          'system':{'final_energy_ev':-i,'trajectory_file':f'{gas}_{i}.traj'}})
    jobs=select_paths({'results':[{'id':'uio66_110111','starts':starts}]})
    assert [j['start'] for j in jobs if j['kind']=='matched']==[7,15,23,31]*2
    assert all(j['frame']==0 and j['start']==31 for j in jobs if j['kind']=='replay')
    assert [j['start'] for j in jobs if j['kind']=='rigid']==[15,31]*2


def test_missing_results_stay_in_denominator(tmp_path):
    manifest=Path('artifacts/phase3/uio66_matched_diagnostic_v1/manifest.json')
    if not manifest.exists():pytest.skip('Local preregistration artifact absent')
    validate(manifest)
    report=assess(manifest,tmp_path)
    assert len(report['components'])==48
    assert not report['all_required_paths_complete']
    assert not report['all_component_energy_targets_met']
    assert all(r['last_change_ev'] is None for r in report['components'])


def test_paired_cancellation_cannot_pass_unstable_gases(tmp_path):
    manifest=Path('artifacts/phase3/uio66_matched_diagnostic_v1/manifest.json')
    if not manifest.exists():pytest.skip('Local preregistration artifact absent')
    plan=json.loads(manifest.read_text());jobs=plan['jobs']
    ids=[j['id'] for j in jobs]+[j['id']+'_empty' for j in jobs if j['kind'] in ('matched','replay')]
    for key in ids:
        p=tmp_path/key;p.mkdir()
        values=[-1,-1,-1.02] if any(j['id']==key and j['kind']=='matched' for j in jobs) else [-1]*3
        (p/'result.json').write_text(json.dumps({'status':'complete','checkpoints':[{'tolerance':t,'energy_ev':v} for t,v in zip([.02,.01,.005],values)]}))
    result=assess(manifest,tmp_path)
    assert all(p['paired_target_met'] for p in result['paired_differences'])
    assert all(not p['both_gases_individually_stable'] for p in result['paired_differences'])
    assert not result['all_component_energy_targets_met']
