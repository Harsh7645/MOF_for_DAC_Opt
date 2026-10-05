"""Numerical diagnostics only; synthetic tests do not validate chemistry."""

import copy
import json
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip('ase')
from ase import Atoms
from mof_dac.adsorption import gas_geometry, summarize_adsorption, evaluate_candidate
from mof_dac.relaxation import connectivity_change, relax_fixed_cell
from mof_dac.sampling import periodic_edges, periodic_change, network_winding_rank, cluster_minima
from scripts.assess_uio66_sampling_pilot import stability


def test_frozen_input_paths_are_portable_and_contained(tmp_path):
    from mof_dac.sampling import frozen_input_path
    expected = tmp_path/'artifacts'/'structures'/'host.cif'
    assert frozen_input_path(tmp_path, r'artifacts\structures\host.cif') == expected
    assert frozen_input_path(tmp_path, 'artifacts/structures/host.cif') == expected
    for invalid in (r'C:\outside.cif', '/outside.cif', r'..\outside.cif', '../outside.cif', r'\\server\share\host.cif'):
        with pytest.raises(ValueError, match='relative|escapes'):
            frozen_input_path(tmp_path, invalid)


def test_report_relocation_keeps_original_hashes_and_is_one_to_one(tmp_path):
    import hashlib
    from scripts.assess_uio66_sampling_pilot import report_hashes
    reports = [tmp_path/f'worker{i}'/'adsorption.json' for i in range(2)]
    for i,path in enumerate(reports):
        path.parent.mkdir()
        path.write_text(json.dumps({'synthetic_worker':i}))
    mapping = {f'/kaggle/working/pilot/worker{i}/adsorption.json':str(p) for i,p in enumerate(reports)}
    expected = {name:hashlib.sha256(Path(p).read_bytes()).hexdigest() for name,p in mapping.items()}
    assert report_hashes(reports,mapping)==expected
    assert report_hashes(reports)=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in reports}
    with pytest.raises(ValueError,match='exactly once'):
        report_hashes(reports,{name:str(reports[0]) for name in mapping})
    with pytest.raises(ValueError,match='exactly once'):
        report_hashes([reports[0],reports[0]],mapping)
    reports[0].write_text('modified synthetic report')
    assert report_hashes(reports,mapping)!=expected


def test_periodic_edges_retain_multiplicity_self_images_and_wrapping():
    initial = Atoms('CC',positions=[[.1,0,0],[1.2,0,0]],cell=[2.5,8,8],pbc=True)
    final = initial.copy()
    final.positions[1,0] = .6
    assert connectivity_change(initial,final)['lost_edges']==[]
    assert periodic_change(initial,final)['lost_image_edges']
    wrapped = initial.copy()
    wrapped.positions[1] += initial.cell[0]
    assert not any(periodic_change(initial,wrapped).values())
    single = Atoms('C',positions=[[0,0,0]],cell=[1.6]*3,pbc=True)
    assert len(periodic_edges(single))==3
    assert network_winding_rank(single)=={'components':1,'winding_rank':3,'image_edges':3}


def test_minima_matching_permutations_translation_and_complete_link():
    host = Atoms('C',positions=[[0,0,0]],cell=[12]*3,pbc=True)
    gas = gas_geometry('H2O')
    gas.positions += [3,0,0]-gas.get_center_of_mass()
    a = host+gas
    a.pbc = True
    b = a.copy()
    b.positions += [1,2,3]
    b.positions[[2,3]] = b.positions[[3,2]]
    c = a.copy()
    c.positions[1:] += [2,0,0]
    groups = cluster_minima([(0,-1,a),(1,-1.005,b),(2,-1.008,c)],1)
    assert {frozenset(g['start_ids']) for g in groups}=={frozenset((0,1)),frozenset((2,))}
    # Nearby energies alone cannot merge geometrically distinct sites.
    assert groups[0]['start_ids']==[2]


def _evidence(key,energy):
    return {'id':key,'status':'converged','final_energy_ev':energy,
            'severe_contacts_below_0_7_angstrom':0,'connectivity':{'lost_edges':[],'gained_edges':[]}}


def _rows():
    gases = {'CO2':_evidence('CO2',-3),'H2O':_evidence('H2O',-2)}
    rows = []
    for i in range(8):
        bare = _evidence('bare',-10)
        starts = [{'gas':g,'start':s,'placement':{'batch':s//16},'status':'accepted',
            'system':_evidence('combo',(-14+.1*i) if g=='CO2' else -12.8),
            'empty_after':bare} for g in ('CO2','H2O') for s in range(32)]
        rows.append({'id':str(i),'bare':bare,'starts':starts,**summarize_adsorption(bare,gases,starts,32)})
    return rows,gases


def test_independent_batch_assessment_failure_and_unstable_minima():
    rows,gases = _rows()
    result = stability(rows,gases)
    assert result['ranking']['criterion_met'] and result['energy_stability']=='initial target met'
    broken = copy.deepcopy(rows)
    broken[0]['starts'][0]['status']='failed'
    broken[0].update(summarize_adsorption(broken[0]['bare'],gases,broken[0]['starts'],32))
    assert stability(broken,gases)['ranking']=='not assessed'
    shifted = copy.deepcopy(rows)
    shifted[0]['starts'][16]['system']['final_energy_ev']-=.1
    shifted[0].update(summarize_adsorption(shifted[0]['bare'],gases,shifted[0]['starts'],32))
    assert stability(shifted,gases)['energy_stability']=='initial target not met'


def test_frozen_real_plan_geometry_seeds_and_no_full64_route():
    from scripts.run_uio66_sampling_pilot import validate_plan
    from mof_dac.sampling import pilot_proposals
    root = Path(__file__).resolve().parents[1]
    plan = json.loads((root/'data/design/uio66_sampling_pilot_v2.json').read_text())
    if not (root/plan['configurations'][0]['bare_input']).exists():
        pytest.skip('Local archived CIFs excluded from git; portable diagnostics above still run')
    hosts = validate_plan(plan,root)
    assert len(hosts)==8
    row = plan['configurations'][0]
    poses = pilot_proposals(hosts[row['id']],gas_geometry('CO2'),plan['mapping'],0,0)
    assert all(np.allclose(p['guest_positions_angstrom'],q['guest_positions_angstrom'],atol=1e-9,rtol=0)
               for p,q in zip(poses,row['poses']['CO2']))
    changed = copy.deepcopy(plan)
    changed['configurations']*=8
    with pytest.raises(ValueError,match='eight-design'):
        validate_plan(changed,root)
    changed = copy.deepcopy(plan)
    changed['configurations'][0]['poses']['H2O'][0]['seed_entropy'][2]=0
    with pytest.raises(ValueError,match='seed identity'):
        validate_plan(changed,root)


def test_new_factory_pipeline_retains_failures_and_periodic_guard(tmp_path):
    from ase.calculators.calculator import Calculator, all_changes
    from ase.io import read
    class Synthetic(Calculator):
        implemented_properties=['energy','forces']
        def calculate(self,atoms=None,properties=None,system_changes=all_changes):
            super().calculate(atoms,properties,system_changes)
            self.results={'energy':float(-len(atoms)),'forces':np.zeros((len(atoms),3))}
    calculator = Synthetic()
    gases,refs = {},{}
    for g in ('CO2','H2O'):
        refs[g]=relax_fixed_cell(gas_geometry(g),calculator,tmp_path,'iso_'+g)
        gases[g]=read(tmp_path/refs[g]['trajectory_file'],index=-1)
    host = Atoms('C',positions=[[0,0,0]],cell=[12]*3,pbc=True)
    def factory(base,gas):
        guest=gas_geometry(gas)
        guest.positions += [5,5,5]-guest.get_center_of_mass()
        guest.set_cell(base.cell)
        guest.pbc=True
        return [(base+guest,{'batch':0,'site_class':'synthetic'})]
    result = evaluate_candidate(host,calculator,gases,refs,tmp_path,'synthetic_v2',starts=1,
        proposal_factory=factory,periodic_guard=True)
    assert result['status']=='complete_model_sample'
    assert all(not any(s['periodic_host_connectivity'].values()) for s in result['starts'])
    with pytest.raises(ValueError,match='Proposal count'):
        evaluate_candidate(host,calculator,gases,refs,tmp_path,'wrong',starts=2,proposal_factory=factory)


def test_representative_force_pipeline_and_independent_energy_audit(tmp_path):
    """All component energies here come from an explicitly synthetic calculator."""
    import hashlib
    from ase.calculators.calculator import Calculator, all_changes
    from scripts.run_uio66_sampling_pilot import execute_refinement
    from scripts.assess_uio66_sampling_pilot import assess_force
    class Synthetic(Calculator):
        implemented_properties=['energy','forces']
        def calculate(self,atoms=None,properties=None,system_changes=all_changes):
            super().calculate(atoms,properties,system_changes)
            self.results={'energy':float(-len(atoms)),'forces':np.zeros((len(atoms),3))}
    calculator=Synthetic()
    loose_dir=tmp_path/'loose'
    structures=loose_dir/'structures'
    host=Atoms('C',positions=[[0,0,0]],cell=[12]*3,pbc=True)
    bare=relax_fixed_cell(host,calculator,structures,'bare')
    gasrefs,systems={},{}
    for gas in ('CO2','H2O'):
        gasrefs[gas]=relax_fixed_cell(gas_geometry(gas),calculator,structures,'isolated_'+gas)
        guest=gas_geometry(gas)
        guest.positions += [5,5,5]-guest.get_center_of_mass()
        guest.set_cell(host.cell)
        guest.pbc=True
        systems[gas]=relax_fixed_cell(host+guest,calculator,structures,'combo_'+gas)
    ids=[f'synthetic_{i}' for i in range(8)]
    plan={'protocol':'synthetic_force_test','configurations':[{'id':key} for key in ids],
          'force_check':{'ids':ids[:4]},'checkpoint_sha256':'synthetic_no_model'}
    plan_path=tmp_path/'plan.json'
    plan_path.write_text(json.dumps(plan))
    plan['_sha256']=hashlib.sha256(plan_path.read_bytes()).hexdigest()
    rows=[]
    for key in ids:
        starts=[{'gas':gas,'start':s,'placement':{'site_class':'random_void' if s>=8 else 'node_OH'},
                 'status':'accepted','system':systems[gas],'empty_after':bare}
                for gas in ('CO2','H2O') for s in range(32)]
        rows.append({'id':key,'bare':bare,'starts':starts,**summarize_adsorption(bare,gasrefs,starts,32)})
    report=loose_dir/'report.json'
    report.write_text(json.dumps({'protocol':plan['protocol'],'plan_sha256':plan['_sha256'],
                                 'gas_references':gasrefs,'results':rows}))
    force=tmp_path/'tight'/'report.json'
    payload=execute_refinement(plan,[report],calculator,force,lambda update:None)
    assert len(payload['results'])==4 and sum(len(r['starts']) for r in payload['results'])==16
    from scripts.assess_uio66_sampling_pilot import EXECUTED_SOURCES
    root=Path(__file__).resolve().parents[1]
    hashes={}
    for name in EXECUTED_SOURCES:
        data=(root/name).read_bytes()
        destination=force.parent/'executed_source'/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(data)
        hashes[name]=hashlib.sha256(data).hexdigest()
    payload.update(plan_sha256=plan['_sha256'],protocol=plan['protocol']+'_force02',fmax=.02,step_budget=600,
                   checkpoint_sha256=plan['checkpoint_sha256'],source_sha256=hashes,
                   loose_report_sha256={str(report):hashlib.sha256(report.read_bytes()).hexdigest()})
    force.write_text(json.dumps(payload))
    checked=assess_force(plan_path,[report],force)
    assert checked['initial_0_01_ev_target_met']
    payload['results'][0]['periodic_bare_connectivity']['lost_image_edges']=[[0,0,1,0,0]]
    force.write_text(json.dumps(payload))
    with pytest.raises(ValueError,match='periodic topology'):
        assess_force(plan_path,[report],force)
    payload['results'][0]['periodic_bare_connectivity']['lost_image_edges']=[]
    payload['results'][0]['starts'][0]['change_ev']+=.1
    force.write_text(json.dumps(payload))
    with pytest.raises(ValueError,match='accounting mismatch'):
        assess_force(plan_path,[report],force)
