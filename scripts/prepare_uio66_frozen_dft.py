"""Freeze seven archived checkpoints and chemistry inspection; never execute inference."""
import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from ase import Atoms
from ase.io import read, write
from ase.io.trajectory import Trajectory

from mof_dac.frozen_dft import (geometry_record, from_record, inspect_geometry, atom_groups,
                              aligned_view, qe_template, decomposition)
from mof_dac.geometry_diagnostic import mic
from mof_dac.shared_rigid_host import geometry_hash


SELECTION = [
    ('uio66_110111_H2O_b1_random',28,[.01,.005]),
    ('uio66_110111_CO2_b0_targeted',7,[.02,.01,.005]),
    ('uio66_000000_CO2_b1_targeted',16,[.01,.005]),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,value):
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def prepare(root, output):
    source_root = root/'artifacts/phase3/uio66_matched_v2_results_20261005'
    raw = source_root/'raw/matched_diagnostic_results_v2'
    frozen = source_root/'raw/matched_diagnostic_frozen_v2'
    receipt = json.loads((source_root/'local_verification.json').read_text())
    for rel,digest in receipt['all_raw_file_sha256'].items():
        if sha(source_root/'raw'/rel)!=digest:
            raise ValueError(f'Historical file changed: {rel}')
    plan = json.loads((frozen/'manifest.json').read_text())
    jobs = {j['id']:j for j in plan['jobs']}
    output.mkdir(parents=True,exist_ok=False)
    (output/'geometries').mkdir(); (output/'inspection').mkdir(); (output/'templates').mkdir()
    shutil.copy2(frozen/'manifest.json',output/'source_manifest.json')
    components, poses, transitions, frames_by_job = {}, [], [], {}
    for job_id,start,thresholds in SELECTION:
        job = jobs[job_id]; assert job['start']==start
        result = json.loads((raw/job_id/'result.json').read_text())
        trajectory = read(raw/job_id/'path.traj',':'); frames_by_job[job_id]=trajectory
        previous = None
        for tol in thresholds:
            checkpoint = next(c for c in result['checkpoints'] if c['tolerance']==tol)
            path = raw/job_id/checkpoint['structure']; atoms=read(path)
            identifier = f"{job['design']}_{job['gas']}_s{start}_f{tol:.3f}"
            source_hash = geometry_hash(atoms)
            indices = [i for i,a in enumerate(trajectory) if geometry_hash(a)==source_hash]
            assert indices, 'Checkpoint absent from archived trajectory'
            k=indices[0]; lo=max(0,k-1); hi=min(len(trajectory)-1,k+1)
            motion=mic(atoms,trajectory[hi].positions-trajectory[lo].positions)
            motion-=motion[:6].mean(axis=0)
            shutil.copy2(path,output/'geometries'/f'{identifier}_complex.traj')
            assert sha(path)==sha(output/'geometries'/f'{identifier}_complex.traj')
            pose={'id':identifier,'source_job':job_id,'design':job['design'],'gas':job['gas'],'start':start,
                  'tolerance_eV_A':tol,'host_atoms':job['host_atoms'],'source_path':path.relative_to(root).as_posix(),
                  'source_sha256':sha(path),'source_trajectory':(raw/job_id/'path.traj').relative_to(root).as_posix(),
                  'source_trajectory_sha256':sha(raw/job_id/'path.traj'),'trajectory_frame_indices':indices,
                  'optimizer_checkpoint':checkpoint,'atom_id_policy':'0-based source order; no sorting or standardization',
                  'atom_symbols':atoms.get_chemical_symbols(),'groups':atom_groups(atoms,plan['mapping']),
                  'local_motion_A':motion.tolist(),'motion_frames':[lo,hi],
                  'local_motion_policy':'MIC adjacent saved-frame secant; indexed Zr mean translation removed; not physical dynamics'}
            for kind,fragment in [('complex',atoms),('host',atoms[:job['host_atoms']]),('guest_optional',atoms[job['host_atoms']:])]:
                key=f'{identifier}_{kind}'; fragment=fragment.copy()
                record=geometry_record(fragment); save(output/'geometries'/f'{key}.json',record)
                restored=from_record(json.loads((output/'geometries'/f'{key}.json').read_text()))
                assert np.array_equal(restored.positions,fragment.positions) and np.array_equal(restored.cell.array,fragment.cell.array)
                if kind!='complex':
                    fragment.calc=None; write(output/'geometries'/f'{key}.traj',fragment)
                    assert geometry_hash(read(output/'geometries'/f'{key}.traj'))==record['geometry_sha256']
                (output/'templates'/f'{key}.qe.in.template').write_text(qe_template(fragment,key),encoding='utf-8')
                components[key]={'geometry_file':f'geometries/{key}.json','geometry_sha256':record['geometry_sha256'],
                                 'kind':kind,'pose':identifier,'source_atom_indices':list(range(len(atoms))) if kind=='complex' else
                                 (list(range(job['host_atoms'])) if kind=='host' else list(range(job['host_atoms'],len(atoms)))),
                                 'uma':None,'dft':None,'charge':0,'spin':'closed-shell nspin=1 proposal; expert confirmation pending'}
                if kind=='complex':
                    components[key]['uma']={'energy_eV':float(atoms.get_potential_energy()),'forces_eV_A':atoms.get_forces().tolist(),
                                           'source':pose['source_path'],'sha256':sha(path),'frame':0,
                                           'convention':'frozen UMA/ODAC checkpoint and calculation settings; no new inference'}
            save(output/'inspection'/f'{identifier}.json',inspect_geometry(atoms,plan['mapping']))
            poses.append(pose)
            if previous:
                transitions.append({'id':previous['id']+'__to__'+identifier,'before':previous['id'],'after':identifier})
            previous=pose
    # Exact geometry lookup: saved references, all their frames; never reuse a relaxed nearby host.
    targets={v['geometry_sha256']:k for k,v in components.items() if v['kind']!='complex'}
    reference_paths=sorted(raw.glob('*_empty/path.traj'))+sorted(raw.glob('*_bare/path.traj'))+sorted(raw.glob('isolated_*/path.traj'))+[raw/'shared_rigid_host/host.traj']
    for path in reference_paths:
        with Trajectory(path) as trajectory:
            for index,atoms in enumerate(trajectory):
                key=targets.get(geometry_hash(atoms))
                if key and components[key]['uma'] is None:
                    components[key]['uma']={'energy_eV':float(atoms.get_potential_energy()),'forces_eV_A':atoms.get_forces().tolist(),
                                           'source':path.relative_to(root).as_posix(),'sha256':sha(path),'frame':index,
                                           'convention':'same frozen UMA/ODAC execution; exact numbers/positions/cell/PBC hash match'}
    # Display only: unwrap the first configuration once, then carry each atom's image gauge.
    for job_id,start,thresholds in SELECTION:
        group=[p for p in poses if p['source_job']==job_id]
        baseline=read(output/'geometries'/f"{group[0]['id']}_complex.traj")
        first=aligned_view(baseline,plan['mapping'])
        fig,axes=plt.subplots(3,len(group),figsize=(6*len(group),12),squeeze=False,constrained_layout=True)
        display=[]
        colors={'guest':'#cf442f','amino':'#335bbc','node':'#7d657e','rings_carboxylates':'#8b8b8b'}
        for col,pose in enumerate(group):
            atoms=read(output/'geometries'/f"{pose['id']}_complex.traj")
            delta=mic(atoms,atoms.positions-baseline.positions); drift=delta[:6].mean(axis=0); delta-=drift
            xyz=first+delta; disp=atoms.copy();disp.calc=None;disp.positions=xyz
            save(output/'inspection'/f"{pose['id']}_display_only.json",{'display_only':True,'coordinates_A':xyz.tolist(),
                 'source_geometry_sha256':geometry_hash(atoms),'Zr_translation_removed_A':drift.tolist()})
            display.append(disp)
            for name,ids in pose['groups'].items():
                axes[0,col].scatter(xyz[ids,0],xyz[ids,1],s=18,c=colors[name],label=name)
                axes[1,col].scatter(xyz[ids,0],xyz[ids,2],s=18,c=colors[name])
                axes[2,col].scatter(ids,np.linalg.norm(delta[ids],axis=1),s=18,c=colors[name])
            axes[0,col].quiver(first[:,0],first[:,1],delta[:,0],delta[:,1],angles='xy',scale_units='xy',scale=1,width=.002)
            for i in np.argsort(np.linalg.norm(delta,axis=1))[-5:]:
                axes[0,col].annotate(f'{atoms[i].symbol}{i}',xyz[i,:2],fontsize=8)
            axes[0,col].set(title=f"{pose['gas']} start{start}, f={pose['tolerance_eV_A']}",xlabel='x(A)',ylabel='y(A)',aspect='equal')
            axes[1,col].quiver(first[:,0],first[:,2],delta[:,0],delta[:,2],angles='xy',scale_units='xy',scale=1,width=.002)
            axes[1,col].set(xlabel='x(A)',ylabel='z(A)',aspect='equal')
            axes[2,col].set(xlabel='Source atom index',ylabel='Zr-translation-aligned displacement(A)')
        axes[0,0].legend(fontsize=8)
        fig.suptitle(f'{job_id}: display-only periodic fragment views; arrows from first checkpoint')
        fig.savefig(output/'inspection'/f'{job_id}.png',dpi=140);plt.close(fig)
        write(output/'inspection'/f'{job_id}_display_only.traj',display)
    tables={}
    for pose in poses:
        inspection=json.loads((output/'inspection'/f"{pose['id']}.json").read_text())
        for name in ['Zr_O_contacts','node_protons','carboxylates','amino','crowding_excluding_shared_bonded_neighbor']:
            tables.setdefault(name,[]).extend({'pose':pose['id'],**row} for row in inspection[name])
        tables.setdefault('guest_contacts',[]).extend({'pose':pose['id'],**row} for row in inspection['guest']['periodic_contacts'])
    for name,rows in tables.items():
        fields=list(dict.fromkeys(k for row in rows for k in row))
        with (output/'inspection'/f'{name}.csv').open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
            writer.writerows({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in row.items()} for row in rows)
    parent_path=root/'artifacts/kaggle/odac25_reference_audit_2026-10-02/final_frames/phase3_uio66_candidate_parent.json'
    library_path=root/'artifacts/kaggle/uio66_bare_2026-10-03/executed_source/uio66_structures/manifest.json'
    parent=json.loads(parent_path.read_text());used=json.loads(library_path.read_text())['parent_provenance']
    exact={k:parent[k]==used[k] for k in ['numbers','positions_angstrom','cell_angstrom','pbc','source_sha256','source_index']}
    save(output/'parent_audit.json',{'export_path':parent_path.relative_to(root).as_posix(),'export_sha256':sha(parent_path),
         'library_manifest':library_path.relative_to(root).as_posix(),'library_sha256':sha(library_path),
         'exact_export_matches_library_parent':exact,'source_index':parent['source_index'],'metadata':parent['metadata'],
         'publication_source_status':'DOI10.1021/jz4002345 inaccessible via web tool; original publication CIF not obtained/verified',
         'meaning':'Exact match establishes exported ODAC parent provenance, not experimental structure/proton validity.'})
    shutil.copy2(parent_path,output/'parent_source.json')
    for tr in transitions:
        values=[components[f"{tr[k]}_{kind}"]['uma'] for kind in ('complex','host') for k in ('before','after')]
        tr['uma_decomposition']=decomposition(*(v['energy_eV'] if v else None for v in values))
        before=read(output/'geometries'/f"{tr['before']}_complex.traj")
        after=read(output/'geometries'/f"{tr['after']}_complex.traj")
        delta=mic(before,after.positions-before.positions);delta-=delta[:6].mean(axis=0)
        inspection=json.loads((output/'inspection'/f"{tr['before']}.json").read_text())
        moving=[]
        for amino in inspection['amino']:
            ids=[amino['N']]+amino['H']
            if np.linalg.norm(delta[ids],axis=1).max()>=.1:moving.extend(ids)
        tr['moving_amino_indices']=sorted(set(moving))
        tr['moving_amino_rule']='N/H group with any atom moving >=0.1A between selected checkpoints after Zr translation removal; descriptor only'
    for pose in poses:
        pose['groups']['moving_amino']=sorted({i for tr in transitions if pose['id'] in (tr['before'],tr['after']) for i in tr['moving_amino_indices']})
    manifest={'protocol':'uio66_frozen_geometry_dft_diagnostic_v1','status':'PREPARATION ONLY; no DFT or UMA launch authorized',
              'source_manifest_sha256':sha(frozen/'manifest.json'),'source_checkpoint_sha256':plan['checkpoint_sha256'],
              'source_calculation_convention':{'task':'odac','UMA':'uma-s-1p2p1','FAIRChem':'2.23.0','charge':0,'spin':0},
              'mapping':plan['mapping'],'poses':poses,'components':components,'transitions':transitions,
              'reuse_search_scope':[p.relative_to(root).as_posix() for p in reference_paths],
              'pilot':[p['id']+'_complex' for p in poses if p['source_job']==SELECTION[0][0]],
              'mandatory_calculations':14,'optional_extracted_guests':7,
              'DFT_environment':'not established; QE templates only; no pseudopotentials supplied',
              'missing_uma_single_points':[k for k,v in components.items() if v['uma'] is None]}
    save(output/'manifest.json',manifest)
    save(output/'validation.json',{'historical_raw_hashes_checked':len(receipt['all_raw_file_sha256']),
         'exact_checkpoint_copies':7,'geometry_roundtrips':21,'stripped_host_slices':7,
         'optional_guest_slices':7,'parent_matches':exact,
         'uma_complexes_available':7,'uma_hosts_available':sum(v['kind']=='host' and v['uma'] is not None for v in components.values()),
         'DFT_inference':False,'UMA_inference':False})
    for folder in ['scripts','mof_dac']:(output/folder).mkdir()
    for rel in ['scripts/prepare_uio66_frozen_dft.py','mof_dac/frozen_dft.py','mof_dac/geometry_diagnostic.py','mof_dac/sampling.py','mof_dac/shared_rigid_host.py']:
        shutil.copy2(root/rel,output/rel)
    save(output/'file_hashes.json',{p.relative_to(output).as_posix():sha(p) for p in output.rglob('*') if p.is_file()})
    print(json.dumps(json.loads((output/'validation.json').read_text())))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path('.'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();prepare(args.root.resolve(),args.output.resolve())
