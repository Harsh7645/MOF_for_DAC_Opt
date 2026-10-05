import json
from pathlib import Path
import numpy as np
import pytest
from ase import Atoms
from ase.io import read,write
from mof_dac.shared_rigid_host import map_guest,geometry_hash,scheduled_jobs,check_shared_reference
from scripts.run_uio66_matched_diagnostic import validate,prepare_shared_host,inventory
from ase.calculators.calculator import Calculator, all_changes


class Harmonic(Calculator):
    implemented_properties=['energy','forces']
    def __init__(self, target):super().__init__();self.target=target.copy()
    def calculate(self,atoms=None,properties=('energy','forces'),system_changes=all_changes):
        super().calculate(atoms,properties,system_changes)
        d=atoms.positions-self.target;self.results={'energy':float(.5*np.sum(d*d)),'forces':-d}


def example():
    host=Atoms('Zr6',positions=[[2,2,2],[4,2,2],[2,4,2],[2,2,4],[4,4,2],[4,2,4]],cell=[20]*3,pbc=True)
    guest=Atoms('CO2',positions=[[10,10,10],[10,10,11.2],[10,10,8.8]],cell=host.cell,pbc=True)
    return host,host+guest


def test_common_host_mapping_preserves_guest_and_exact_host():
    host,source=example();host.positions+=[.3,.2,-.1]
    source.positions[-1]+=[0,0,20]  # Equivalent guest image.
    mapped,r=map_guest(source,host)
    assert r['valid'];assert np.array_equal(mapped.positions[:6],host.positions)
    assert np.allclose(r['translation_A'],[.3,.2,-.1])
    assert np.allclose(mapped[-3:].get_all_distances(mic=True),source[-3:].get_all_distances(mic=True))
    assert geometry_hash(mapped[:6])==geometry_hash(host)


def test_mapping_rejects_clashes_cell_and_nonrigid_alignment():
    host,source=example();source.positions[-3:]=source.positions[0]+[[0,0,0],[0,0,1.2],[0,0,-1.2]]
    _,r=map_guest(source,host);assert not r['valid'] and not r['checks']['clearance_ge_1A']
    changed=host.copy();changed.cell[0,0]+=1
    with pytest.raises(ValueError,match='fixed cell'):map_guest(source,changed)
    host.positions[0]+=[1,0,0];_,r=map_guest(source,host)
    assert not r['checks']['ZR_residual_le_0_25A']


def test_schedule_dependency_and_no_duplicate_paths():
    p=Path('data/design/uio66_matched_diagnostic_v2.json');plan=json.loads(p.read_text())
    a,b=scheduled_jobs(plan,0),scheduled_jobs(plan,1)
    assert a[0]['id']=='uio66_110111_bare'
    assert all(j['kind']=='rigid' for j in a[1:5])
    assert not any(j['kind']=='rigid' for j in b)
    assert len({j['id'] for j in a+b})==len(a+b)==28
    assert sum(2 if j['kind'] in ('matched','replay') else 1 for j in a)==25
    assert sum(2 if j['kind'] in ('matched','replay') else 1 for j in b)==23


def test_one_reference_shared_and_tampered_host_detected(tmp_path):
    host,source=example();host.calc=Harmonic(host.positions)
    seed=tmp_path/'seed';seed.mkdir();write(seed/'checkpoint_0.005.traj',host)
    (seed/'result.json').write_text(json.dumps({'status':'complete'}))
    write(tmp_path/'pose.traj',source)
    jobs=[{'id':f'rigid{i}','kind':'rigid','pose':'pose.traj','host_atoms':6} for i in range(4)]
    plan={'rigid_host':{'seed_job_id':'seed'},'jobs':jobs,'thresholds_ev_A':[.02,.01,.005]}
    ref=prepare_shared_host(plan,tmp_path/'manifest.json',tmp_path,Harmonic(host.positions))
    assert ref['status']=='ready' and ref['single_point_count']==1
    assert len({r['host_geometry_sha256'] for r in ref['mapping']})==1
    audit=check_shared_reference(tmp_path,plan);assert audit['valid'] and audit['energy_ev']==0
    changed=read(tmp_path/'shared_rigid_host/host.traj');changed.positions[0,0]+=.01
    write(tmp_path/'shared_rigid_host/host.traj',changed)
    assert not check_shared_reference(tmp_path,plan)['valid']


def test_incomplete_dependency_is_retained(tmp_path):
    plan=json.loads(Path('data/design/uio66_matched_diagnostic_v2.json').read_text())
    seed=tmp_path/'uio66_110111_bare';seed.mkdir()
    (seed/'result.json').write_text(json.dumps({'status':'step_limit','checkpoints':[]}))
    result=inventory(plan,tmp_path)
    assert len(result)==48
    assert next(r for r in result if r['id']=='uio66_110111_bare')['status']=='step_limit'
    assert not check_shared_reference(tmp_path,plan)['valid']


def test_actual_seed_preview_and_flexible_inputs_unchanged():
    path=Path('artifacts/phase3/uio66_matched_diagnostic_v2/manifest.json')
    if not path.exists():pytest.skip('Local archived poses absent')
    plan=validate(path);old=json.loads(Path('data/design/uio66_matched_diagnostic_v1.json').read_text())
    for a,b in zip(plan['jobs'],old['jobs']):assert a['pose_sha256']==b['pose_sha256']
    preview=json.loads((path.parent/'mapping_preview.json').read_text())
    assert len(preview['results'])==4 and all(r['valid'] for r in preview['results'])


def test_deadline_terminates_workers_and_archives_incomplete(tmp_path,monkeypatch):
    from types import SimpleNamespace
    import scripts.run_uio66_matched_diagnostic as runner
    root=tmp_path/'frozen';root.mkdir();(root/'scripts').mkdir()
    manifest=root/'manifest.json';manifest.write_text('{}');(root/'release.json').write_text('{"sha256":{}}')
    checkpoint=tmp_path/'model';checkpoint.write_bytes(b'analytic-test-only')
    plan=json.loads(Path('data/design/uio66_matched_diagnostic_v2.json').read_text())
    plan['checkpoint_sha256']=runner.sha(checkpoint)
    processes=[]
    class Process:
        def __init__(self,*args,**kwargs):self.returncode=None;processes.append(self)
        def poll(self):return self.returncode
        def terminate(self):self.returncode=-15
        def kill(self):self.returncode=-9
        def wait(self,timeout=None):return self.returncode
    clock=SimpleNamespace(time=lambda:7101 if len(processes)==2 else 101,sleep=lambda _:None)
    monkeypatch.setattr(runner,'time',clock)
    monkeypatch.setattr(runner,'__file__',str(root/'scripts/run_uio66_matched_diagnostic.py'))
    monkeypatch.setattr(runner.subprocess,'check_output',lambda *a,**k:'0, Tesla T4, UUID0, 15360\n1, Tesla T4, UUID1, 15360\n')
    monkeypatch.setattr(runner.subprocess,'run',lambda *a,**k:None)
    monkeypatch.setattr(runner.subprocess,'Popen',Process)
    args=SimpleNamespace(approved_wall_hours=2,allocation_start_epoch=100,checkpoint=checkpoint,manifest=manifest,output=tmp_path/'result')
    assert runner.execute(args,plan)=='allocation_time_limit'
    assert len(processes)==2 and all(p.returncode==-15 for p in processes)
    assert len(json.loads((args.output/'inventory.json').read_text()))==48
    assert args.output.with_suffix('.zip').exists()
    allocation=json.loads((args.output/'allocation.json').read_text())
    assert allocation['deadline_epoch']==7000 and allocation['allocation_end_epoch']==7300
