"""Copy exact archived structures and format review tables/views; no calculator or fitting."""
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
from ase.data import chemical_symbols
from ase.geometry import find_mic
from ase.io import read

ROOT = Path(__file__).resolve().parents[1]
FROZEN = Path('artifacts/phase3/uio66_frozen_dft_v2_qe75')
DEV = Path('plans/uio66-offline-development-v1/results')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def image_point(positions, cell, i, anchor):
    """Display only: closest image of atom i to anchor; return exact integer image label."""
    vector, _ = find_mic(positions[i]-anchor, cell, pbc=True)
    shift = np.rint((anchor+vector-positions[i]) @ np.linalg.inv(cell)).astype(int)
    return shift, positions[i]+shift @ cell


def plot_panels(path, title, panels, numbers, rows):
    fig, axes = plt.subplots(len(panels), 2, figsize=(12, 3.8*len(panels)), squeeze=False,
                             layout='constrained')
    colors = {'Zr':'#4a8b87', 'O':'#c33c3c', 'H':'#297fb8', 'N':'#6a50a1', 'C':'#4c4c4c'}
    for row, (name, points) in enumerate(panels):
        for col, dims in enumerate(((0, 1), (0, 2))):
            ax = axes[row, col]
            for i, shift, xyz in points:
                symbol = chemical_symbols[numbers[i]]
                label = f'{symbol}{i}@({shift[0]},{shift[1]},{shift[2]})'
                ax.scatter(xyz[dims[0]], xyz[dims[1]], s=50, color=colors.get(symbol, 'gray'))
                ax.annotate(label, (xyz[dims[0]], xyz[dims[1]]), xytext=(3, 5),
                            textcoords='offset points', fontsize=6.5,
                            arrowprops={'arrowstyle':'-', 'lw':.35, 'color':'gray'})
            ax.set(xlabel='x (Angstrom)', ylabel=('y' if col == 0 else 'z')+' (Angstrom)', title=name)
            ax.set_aspect('equal', adjustable='box'); ax.margins(.25)
        for i, shift, xyz in points:
            rows.append({'view':path.name, 'panel':name, 'atom_index':i,
                         'element':chemical_symbols[numbers[i]],
                         'image_a':int(shift[0]), 'image_b':int(shift[1]), 'image_c':int(shift[2]),
                         'x_A':float(xyz[0]), 'y_A':float(xyz[1]), 'z_A':float(xyz[2])})
    fig.suptitle(title+'\nDisplay images only; exact source coordinates are unchanged', fontsize=11)
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    for ax in axes.flat:
        occupied=[]
        for annotation in ax.texts:
            for dx,dy in [(3,5),(3,17),(3,29),(3,-17),(3,-29),(-90,5),(-90,17),(-90,-17),(3,41),(-90,41)]:
                annotation.set_position((dx,dy))
                box=matplotlib.text.Text.get_window_extent(annotation,renderer).expanded(1.04,1.08)
                if not any(box.overlaps(other) for other in occupied):break
            occupied.append(box)
    # Decimal tolerance in the basename is not a file suffix.
    fig.savefig(Path(str(path)+'.png'), dpi=180, bbox_inches='tight')
    fig.savefig(Path(str(path)+'.svg'), bbox_inches='tight', metadata={'Date':None})
    plt.close(fig)


def prepare(output):
    output.mkdir(parents=True, exist_ok=False)
    inputs = {}

    def load(relative):
        p = ROOT/relative; inputs[Path(relative).as_posix()] = sha(p)
        return json.loads(p.read_text())

    def copy(relative, destination):
        p = ROOT/relative; inputs[Path(relative).as_posix()] = sha(p)
        destination.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(p, destination)

    manifest = load(FROZEN/'manifest.json')
    parent = load(FROZEN/'parent_source.json')
    poses = [p for p in manifest['poses'] if p['design']=='uio66_110111']
    exact = output/'exact'; exact.mkdir()
    views = output/'views'; views.mkdir()
    copy(FROZEN/'parent_source.json', exact/'parent_source.json')
    copy(FROZEN/'provenance/jz4002345_si_002.cif', exact/'source_publication.cif')
    copy(FROZEN/'provenance/publication_comparison.json', output/'source_publication_comparison.json')
    mapping = manifest['mapping']; write_json(output/'atom_mapping.json', mapping)
    source_records, coordinates, cells, view_rows, hydroxyls = [], [], [], [], []
    plt.rcParams.update({'svg.hashsalt':'phase3-review-v2', 'font.size':9})
    for pose in poses:
        identifier = pose['id']; component = manifest['components'][identifier+'_complex']
        geo = load(FROZEN/component['geometry_file'])
        xyz, cell = np.array(geo['positions_A']), np.array(geo['cell_A'])
        numbers = geo['numbers']
        source_path = Path(pose['source_path'])
        assert sha(ROOT/source_path)==pose['source_sha256'], source_path
        checkpoint = read(ROOT/source_path)
        assert np.array_equal(checkpoint.positions, xyz) and np.array_equal(checkpoint.cell.array, cell)
        assert np.array_equal(checkpoint.numbers, numbers)
        copy(source_path, exact/(identifier+'.traj'))
        copy(FROZEN/component['geometry_file'], exact/(identifier+'.json'))
        descriptors = load(FROZEN/'inspection'/(identifier+'.json'))
        copy(FROZEN/'inspection'/(identifier+'.json'), output/(identifier+'_inspection.json'))
        source_records.append({k:pose[k] for k in ('id','source_path','source_sha256','source_trajectory',
                              'source_trajectory_sha256','trajectory_frame_indices','optimizer_checkpoint','atom_id_policy')})
        for i, (number, position) in enumerate(zip(numbers, xyz)):
            coordinates.append(dict(pose=identifier,atom_index=i,element=chemical_symbols[number],
                                    x_A=position[0],y_A=position[1],z_A=position[2]))
        for axis, vector in enumerate(cell):
            cells.append(dict(pose=identifier,axis=axis,x_A=vector[0],y_A=vector[1],z_A=vector[2]))
        panels=[]
        for proton in descriptors['node_protons']:
            h, o = proton['H'], proton['nearest_node_O']
            anchor = xyz[h]; oshift, opos = image_point(xyz, cell, o, anchor)
            points = [(h,np.zeros(3,dtype=int),anchor),(o,oshift,opos)]
            for contact in descriptors['Zr_O_contacts']:
                if contact['j']==o and contact['distance_A']<2.8:
                    z=contact['i']; shift=oshift-np.array(contact['image_j'])
                    points.append((z,shift,xyz[z]+shift@cell))
            # All acceptors remain in exact inspection JSON; show the three nearest for legibility.
            for contact in sorted(proton['nearby_acceptors'],key=lambda c:c['distance_A'])[:3]:
                j=contact['j']; shift=np.array(contact['image_j']); points.append((j,shift,xyz[j]+shift@cell))
            panels.append((f'OH: O{o}-H{h}; nearest three candidate acceptors',points))
            vector=anchor-opos
            hydroxyls.append(dict(pose=identifier,H=h,O=o,O_image_a=int(oshift[0]),O_image_b=int(oshift[1]),
                O_image_c=int(oshift[2]),OH_x_A=vector[0],OH_y_A=vector[1],OH_z_A=vector[2],
                saved_OH_A=proton['OH_A']))
        plot_panels(views/(identifier+'_OH'),identifier,panels,numbers,view_rows)
        guest_points={}
        for i in descriptors['guest']['indices']:
            shift,pos=image_point(xyz,cell,i,xyz[124]);guest_points[(i,*shift)]=(i,shift,pos)
        for contact in descriptors['guest']['periodic_contacts']:
            i,j=contact['i'],contact['j']; shift_i,_=image_point(xyz,cell,i,xyz[124])
            shift=shift_i+np.array(contact['image_j']);guest_points[(j,*shift)]=(j,shift,xyz[j]+shift@cell)
        plot_panels(views/(identifier+'_guest'),identifier+'; guest and all saved contacts <3.5 A',
                    [('Periodic guest environment',list(guest_points.values()))],numbers,view_rows)
    # Parent node view explicitly uses the archived ideal-model atom order, not CIF atom correspondence.
    xyz=np.array(parent['positions_angstrom']);cell=np.array(parent['cell_angstrom']);numbers=parent['numbers']
    points=[(i,*image_point(xyz,cell,i,xyz[0])) for i in mapping['node_atom_indices']]
    plot_panels(views/'parent_node','Ideal-model parent node; four labeled hydroxyl protons',
                [('Node nearest images relative to Zr0',points)],numbers,view_rows)
    for i,(number,position) in enumerate(zip(numbers,xyz)):
        coordinates.append(dict(pose='parent',atom_index=i,element=chemical_symbols[number],x_A=position[0],y_A=position[1],z_A=position[2]))
    for axis,vector in enumerate(cell):cells.append(dict(pose='parent',axis=axis,x_A=vector[0],y_A=vector[1],z_A=vector[2]))
    write_csv(output/'coordinates.csv',coordinates);write_csv(output/'cells.csv',cells)
    write_csv(output/'view_images.csv',view_rows);write_csv(output/'OH_vectors.csv',hydroxyls)
    write_json(output/'source_geometries.json',source_records)
    selected={p['id'] for p in poses}
    for name in ('amino','carboxylates','crowding_excluding_shared_bonded_neighbor','guest_contacts','node_protons','Zr_O_contacts'):
        p=ROOT/FROZEN/'inspection'/(name+'.csv');inputs[p.relative_to(ROOT).as_posix()]=sha(p)
        with p.open() as handle:rows=[r for r in csv.DictReader(handle) if r['pose'] in selected]
        write_csv(output/(name+'.csv'),rows)
    # Keep existing Zr-aligned before/after figures and display-coordinate files unchanged.
    for job in ('uio66_110111_H2O_b1_random','uio66_110111_CO2_b0_targeted'):
        copy(FROZEN/'inspection'/(job+'.png'),views/(job+'_archived.png'))
    for pose in poses:
        copy(FROZEN/'inspection'/(pose['id']+'_display_only.json'),views/(pose['id']+'_display_only.json'))
    analysis=load(DEV/'analysis.json');bootstrap=load(DEV/'bootstrap_fits.json')
    write_csv(output/'bootstrap_draw_status.csv',[dict(draw=r['replicate'],model=model,rank=s['rank'],
        status=s['status'],excluded_from_conditional_summaries=s['status']!='identifiable')
        for r in bootstrap for model,s in r['models'].items()])
    write_json(output/'conditional_summary_definitions.json',{
        'coefficient_endpoints_percent':[2.5,50,97.5], 'ranking_endpoints_percent':[5,50,95],
        'pairwise':{'attempted':1000,'included':977,'excluded':23},'additive':{'attempted':1000,'included':1000,'excluded':0},
        'conditional_keys':['coefficient_percentiles_2_5_50_97_5_ev','coefficient_positive_fraction',
             'rank_percentiles_5_50_95','top10_overlap_percentiles_5_50_95','spearman_to_full_fit_percentiles_5_50_95','preferred_design_counts'],
        'not_bootstrap_conditional':['full_fit_preferred_design','condition_number','full_coefficients_ev','historical metrics','CV metrics'],
        'rank_deficient_pairwise_draws':[r['replicate'] for r in bootstrap if r['models']['pairwise']['status']=='rank_deficient']})
    write_json(output/'saved_stability_summaries.json',analysis['stability'])
    terms=['offset']+[f'h{i}' for i in range(6)]+[f'J{i}{j}' for i in range(6) for j in range(i+1,6)]
    write_csv(output/'coefficient_endpoints.csv',[dict(model=model,term=terms[i],p2_5_eV=q[0],median_eV=q[1],p97_5_eV=q[2],
        positive_fraction=s['coefficient_positive_fraction'][i],included=s['identifiable'],excluded=s['attempted']-s['identifiable'])
        for model,s in analysis['stability'].items() for i,q in enumerate(zip(*s['coefficient_percentiles_2_5_50_97_5_ev']))])
    sampling=load(Path('data/design/uio66_sampling_pilot_v2.json'))
    write_csv(output/'pilot_selection.csv',[{k:c[k] for k in ('pattern','configuration_index','reason','historical_fitted_rank','historical_sampled_rank','historical_split_role')} for c in sampling['configurations']])
    write_csv(output/'pilot_seed_streams.csv',[dict(pattern=c['pattern'],gas=gas,start=p['start'],batch=p['batch'],
        batch_slot=p['batch_slot'],site_class=p['site_class'],anchor=p['site_anchor'],seed_entropy=json.dumps(p['seed_entropy']))
        for c in sampling['configurations'] for gas,poses_ in c['poses'].items() for p in poses_])
    inputs[Path(__file__).relative_to(ROOT).as_posix()]=sha(__file__)
    assert len(list(views.glob('*.svg')))==11
    assert len(list(views.glob('*.png')))==13  # eleven new views plus two archived comparisons
    assert all(sha(ROOT/p)==value for p,value in inputs.items())
    write_json(output/'receipt.json',{'mode':'exact copies, saved summaries and display geometry only; no new scientific calculations/fits',
        'inputs':inputs,'outputs':{p.relative_to(output).as_posix():sha(p) for p in sorted(output.rglob('*')) if p.is_file()}})
    print(json.dumps({'exact_checkpoints':len(source_records),'node_OH_environments':len(hydroxyls),'coordinate_rows':len(coordinates),
                      'bootstrap_records':len(bootstrap),'new_display_figure_pairs':11,'inputs':len(inputs)}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    prepare(parser.parse_args().output)
