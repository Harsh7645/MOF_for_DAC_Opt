"""Offline saved-force/coordinate analysis. No inference imports or new energies."""
import argparse
import csv
import hashlib
import json
from itertools import combinations
from pathlib import Path
import numpy as np
from ase.io import read
from mof_dac.geometry_diagnostic import mic, angle, atom_roles, guest_geometry, contacts, host_descriptors, cage_location
from mof_dac.sampling import periodic_change


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf-8')


def csv_rows(path, rows):
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def analyze(raw, plan, output):
    output.mkdir(parents=True,exist_ok=False)
    mapping=plan['mapping']
    tight=raw/'force02/structures/uio66_110111_tight_CO2_31.traj'
    loose=raw/'worker1/structures/uio66_110111_CO2_31.traj'
    frames=read(tight,index=':'); initial,final=frames[0],frames[-1];n=len(initial)-3
    roles=atom_roles(initial,mapping,n)
    displacement=mic(initial,final.positions-initial.positions)
    motions=[{'index_0based':i,'element':a.symbol,'role':roles[i],'displacement_A':float(np.linalg.norm(displacement[i])),
              'dx_A':float(displacement[i,0]),'dy_A':float(displacement[i,1]),'dz_A':float(displacement[i,2])} for i,a in enumerate(initial)]
    csv_rows(output/'atom_displacements.csv',sorted(motions,key=lambda r:-r['displacement_A']))
    descriptors=[host_descriptors(a,mapping) for a in frames]
    contact_records=[contacts(a,mapping) for a in frames]
    # Track every close contact present at either endpoint, plus all node H/guest O.
    pairs=sorted({(i,j) for rec in (contact_records[0],contact_records[-1]) for d,i,j in rec['nearest']} |
                 {(h,j) for h in mapping['node_atom_indices'] if initial[h].symbol=='H' for j in range(n,len(initial)) if initial[j].symbol=='O'})
    metrics=[]; edge_events=[]
    com0,axis0,_=guest_geometry(initial)
    for step,a in enumerate(frames):
        com,axis,_=guest_geometry(a)
        drift=mic(a,a.positions[:6]-initial.positions[:6]).mean(axis=0)
        disp=mic(a,a.positions-initial.positions)-drift
        row={'step':step,'energy_ev':float(a.get_potential_energy()),'relative_energy_ev':float(a.get_potential_energy()-initial.get_potential_energy()),
             'max_force_ev_A':float(np.linalg.norm(a.get_forces(),axis=1).max()),
             'guest_COM_displacement_A':float(np.linalg.norm(mic(a,com-com0)-drift)),
             'guest_axis_change_deg':angle(axis0,axis,unsigned=True),'host_max_drift_corrected_A':float(np.linalg.norm(disp[:n],axis=1).max())}
        row.update({f'guest_COM_{c}_A':float((com0+mic(a,com-com0))[k]) for k,c in enumerate('xyz')})
        row['node_O109_H15_A']=float(a.get_distance(109,15,mic=True))
        row['O109_H15_O126_angle_deg']=angle(mic(a,a.positions[109]-a.positions[15]),mic(a,a.positions[126]-a.positions[15]))
        row.update({f'd_{i}_{j}_A':float(a.get_distance(i,j,mic=True)) for i,j in pairs})
        row.update({f'ring_{key}_rotation_deg':angle(descriptors[0]['rings'][key],value,unsigned=True) for key,value in descriptors[step]['rings'].items()})
        row.update({f'node_{key}_rotation_deg':angle(descriptors[0]['OH'][key],value) for key,value in descriptors[step]['OH'].items()})
        row.update({f'amino_{key}_H{h}_torsion_deg':torsion for key,values in descriptors[step]['amino_torsions'].items() for h,torsion in values.items()})
        change=periodic_change(initial,a)
        if any(change.values()): edge_events.append({'step':step,**change})
        metrics.append(row)
    csv_rows(output/'tight_trajectory_steps.csv',metrics)
    save_json(output/'contact_history.json',contact_records)
    save_json(output/'host_conformation_history.json',descriptors)
    save_json(output/'trajectory_edge_events.json',edge_events)
    summary={'trajectory_sha256':sha(tight),'loose_trajectory_sha256':sha(loose),'frames':len(frames),
             'energy_drop_ev':metrics[-1]['relative_energy_ev'],'largest_single_step_drop_ev':float(np.diff([r['energy_ev'] for r in metrics]).min()),
             'endpoint_motion':sorted(motions,key=lambda r:-r['displacement_A'])[:16],
             'initial_contacts':contact_records[0],'final_contacts':contact_records[-1],
             'final_step':metrics[-1],'image_edge_event_frames':len(edge_events)}
    save_json(output/'trajectory_summary.json',summary)
    endpoints=[]; provenance={str(tight):sha(tight),str(loose):sha(loose)}
    for worker in (0,1):
        reportpath=raw/f'worker{worker}/adsorption.json';run=json.loads(reportpath.read_text());provenance[str(reportpath)]=sha(reportpath)
        for candidate in run['results']:
            if candidate['id'] not in ('uio66_000000','uio66_110111'):continue
            for start in candidate['starts']:
                path=reportpath.parent/'structures'/start['system']['trajectory_file']; a=read(path,index=-1)
                provenance[str(path)]=sha(path)
                con=contacts(a,mapping);com,axis,normal=guest_geometry(a)
                desc=host_descriptors(a,mapping)
                location=cage_location(a)
                endpoints.append({'design':candidate['id'],'gas':start['gas'],'start':start['start'],
                    'batch':start['placement']['batch'],'initial_site':start['placement']['site_class'],'status':start['status'],
                    'total_energy_ev':start['system']['final_energy_ev'],
                    'adsorption_energy_ev':start['system']['final_energy_ev']-candidate['bare_reference_energy_ev']-run['gas_references'][start['gas']]['final_energy_ev'],
                    'force_ev_A':start['system']['max_force_ev_per_angstrom'],
                    'contact_motif':con['motif'],'contacts':con,'location':location,'axis_cartesian':axis.tolist(),'water_normal':normal.tolist(),
                    'host_conformation':desc,'trajectory':str(path),'sha256':sha(path)})
    save_json(output/'pilot_endpoints.json',endpoints)
    table=[{'design':e['design'],'gas':e['gas'],'start':e['start'],'batch':e['batch'],'initial_site':e['initial_site'],
            'status':e['status'],'total_energy_ev':e['total_energy_ev'],'adsorption_energy_ev':e['adsorption_energy_ev'],'force_ev_A':e['force_ev_A'],
            'contact_motif':e['contact_motif'],'cage':e['location']['nearest_template_cage'],
            'window':e['location']['nearest_template_window'],'window_distance_A':e['location']['window_center_distance_A'],
            'COM_fractional':json.dumps(e['location']['guest_fractional_com']),'orientation_axis':json.dumps(e['axis_cartesian']),
            'H_bonds':json.dumps(e['contacts']['hbonds']),'host_conformation':json.dumps(e['host_conformation'])} for e in endpoints]
    csv_rows(output/'pilot_endpoints.csv',table)
    # Broad motif recurrence is only a screening descriptor. Include site identities and energies.
    recurrence=[]
    for design in ('uio66_000000','uio66_110111'):
        for gas in ('CO2','H2O'):
            pool=[e for e in endpoints if e['design']==design and e['gas']==gas]
            for motif in sorted({e['contact_motif'] for e in pool}):
                group=[e for e in pool if e['contact_motif']==motif]
                recurrence.append({'design':design,'gas':gas,'motif':motif,'starts':[e['start'] for e in group],
                  'both_batches':len({e['batch'] for e in group})==2,'energy_span_ev':max(e['total_energy_ev'] for e in group)-min(e['total_energy_ev'] for e in group),
                  'best_energy_ev':min(e['total_energy_ev'] for e in group)})
    save_json(output/'broad_motif_recurrence.json',recurrence)
    save_json(output/'source_hashes.json',provenance)
    plot(frames,metrics,pairs,output)
    return summary


def plot(frames,metrics,pairs,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    x=np.arange(len(metrics));fig,axes=plt.subplots(4,2,figsize=(13,16),constrained_layout=True)
    def lines(ax,keys,title,ylabel):
        for key in keys:ax.plot(x,[r[key] for r in metrics],label=key)
        ax.set(xlabel='LBFGS step',ylabel=ylabel,title=title);ax.legend(fontsize=6)
    lines(axes[0,0],['relative_energy_ev'],'110111 CO2 start31: stored energies','eV')
    lines(axes[0,1],['max_force_ev_A'],'Stored maximum force','eV/angstrom')
    lines(axes[1,0],['guest_COM_displacement_A','host_max_drift_corrected_A'],'Motion after Zr translation removal','angstrom')
    close=[f'd_{i}_{j}_A' for i,j in pairs if min(metrics[0][f'd_{i}_{j}_A'],metrics[-1][f'd_{i}_{j}_A'])<3.1]
    lines(axes[1,1],close,'Close host/guest contacts (zero-based indices)','angstrom')
    lines(axes[2,0],['guest_axis_change_deg']+[f'ring_L{i}_rotation_deg' for i in range(6)],'Guest and linker rotation','degrees')
    lines(axes[2,1],[k for k in metrics[0] if k.startswith('node_') and k.endswith('rotation_deg')],'Node OH rotation','degrees')
    for key in [k for k in metrics[0] if k.startswith('amino_L1') or k.startswith('amino_L3')]:
        values=np.unwrap(np.radians([r[key] for r in metrics]));axes[3,0].plot(x,np.degrees(values-values[0]),label=key)
    axes[3,0].set(xlabel='LBFGS step',ylabel='degrees',title='Amino torsion change relative to ring');axes[3,0].legend(fontsize=6)
    lines(axes[3,1],[f'guest_COM_{c}_A' for c in 'xyz'],'Guest COM coordinates (same periodic image)','angstrom')
    fig.savefig(output/'trajectory_diagnostics.png',dpi=170);plt.close(fig)
    # Actual periodic images nearest the guest, same image gauge for both endpoints.
    first,last=frames[0],frames[-1];com,_,_=guest_geometry(first)
    p0=com+mic(first,first.positions-com);p1=p0+mic(first,last.positions-first.positions)
    chosen=[i for i in range(len(first)) if min(np.linalg.norm(p0[i]-com),np.linalg.norm(p1[i]-com))<4.5 or i in (109,15)]
    fig=plt.figure(figsize=(13,6));colors={'H':'silver','C':'black','N':'royalblue','O':'red','Zr':'teal'}
    for panel,(p,title) in enumerate(((p0,'Initial: 0.05 endpoint'),(p1,'Final: 0.02 endpoint'))):
        ax=fig.add_subplot(1,2,panel+1,projection='3d')
        for i in chosen:
            ax.scatter(*p[i],color=colors[first[i].symbol],s=45 if i>=len(first)-3 else 20)
            ax.text(*p[i],str(i),fontsize=7)
        for i,j in combinations(chosen,2):
            if np.linalg.norm(p[i]-p[j]) < (1.8 if first[i].symbol!='H' and first[j].symbol!='H' else 1.3):
                ax.plot(*np.array([p[i],p[j]]).T,color='grey',linewidth=.7)
        ax.set(title=title,xlabel='x (A)',ylabel='y (A)',zlabel='z (A)');ax.set_box_aspect((1,1,1))
        for k,setter in enumerate((ax.set_xlim,ax.set_ylim,ax.set_zlim)):
            values=np.concatenate((p0[chosen,k],p1[chosen,k]));setter(values.min()-.5,values.max()+.5)
    fig.tight_layout();fig.savefig(output/'local_structures.png',dpi=180);plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--plan',type=Path,default=Path('data/design/uio66_sampling_pilot_v2.json'));args=p.parse_args()
    result=analyze(args.raw,json.loads(args.plan.read_text()),args.output)
    print(json.dumps({k:result[k] for k in ('frames','energy_drop_ev','largest_single_step_drop_ev','image_edge_event_frames')}))
