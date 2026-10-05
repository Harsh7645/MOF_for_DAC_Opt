"""Coordinate-only UiO-66 descriptors. Geometric labels are not chemistry certificates."""
from itertools import combinations, product
import numpy as np
from ase.geometry import find_mic


def mic(atoms, vectors):
    shape = np.asarray(vectors).shape
    return find_mic(np.asarray(vectors).reshape(-1, 3), atoms.cell, atoms.pbc)[0].reshape(shape)


def angle(u, v, unsigned=False):
    cosine = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
    return float(np.degrees(np.arccos(np.clip(abs(cosine) if unsigned else cosine, -1, 1))))


def atom_roles(atoms, mapping, host_count):
    roles = {i: 'node' for i in mapping['node_atom_indices']}
    for slot in mapping['slots']:
        roles.update({i: slot['id'] for i in slot['atom_indices']})
    for i in range(114, host_count):
        nitrogen = [j for j in range(host_count) if atoms[j].symbol == 'N']
        j = min(nitrogen, key=lambda j: atoms.get_distance(i, j, mic=True))
        roles[i] = roles[j] + ':aminoH'
    roles.update({i: 'guest' for i in range(host_count, len(atoms))})
    return roles


def guest_geometry(atoms):
    ids = list(range(len(atoms)-3, len(atoms)))
    xyz = atoms.positions[ids[0]] + mic(atoms, atoms.positions[ids] - atoms.positions[ids[0]])
    com = np.average(xyz, axis=0, weights=atoms.get_masses()[ids])
    axis = xyz[2]-xyz[1] if atoms[ids[0]].symbol == 'C' else (xyz[1]+xyz[2])/2-xyz[0]
    axis /= np.linalg.norm(axis)
    # CO2 axis is undirected; choose a reproducible sign for the table.
    if atoms[ids[0]].symbol == 'C' and axis[np.argmax(abs(axis))] < 0:
        axis = -axis
    normal = np.cross(xyz[1]-xyz[0], xyz[2]-xyz[0])
    normal = normal / np.linalg.norm(normal) if atoms[ids[0]].symbol == 'O' else np.zeros(3)
    return com, axis, normal


def contacts(atoms, mapping):
    n = len(atoms)-3
    roles = atom_roles(atoms, mapping, n)
    d = np.linalg.norm(mic(atoms, atoms.positions[:n, None]-atoms.positions[None, n:]), axis=-1)
    nearest = sorted((float(d[i, j]), i, n+j) for i in range(n) for j in range(3))[:8]
    hbonds = []
    distances = atoms.get_all_distances(mic=True)
    # Operational D-H...A: D=N/O, A=N/O, H...A<=2.5 A, D-H...A>=120 degrees.
    for h in [i for i, a in enumerate(atoms) if a.symbol == 'H']:
        donors = [i for i, a in enumerate(atoms) if a.symbol in ('N','O') and distances[h,i]<1.3]
        for donor in donors:
            for acceptor, a in enumerate(atoms):
                if a.symbol not in ('N','O') or (h<n)==(acceptor<n):
                    continue
                distance = distances[h,acceptor]
                if distance <= 2.5:
                    theta = angle(mic(atoms, atoms.positions[donor]-atoms.positions[h]),
                                  mic(atoms, atoms.positions[acceptor]-atoms.positions[h]))
                    if theta >= 120:
                        hbonds.append({'donor':donor,'H':h,'acceptor':acceptor,'HA_A':float(distance),'DHA_deg':theta})
    motif = sorted(set(roles[i].split(':')[0]+':'+atoms[i].symbol for dist,i,j in nearest if dist<=3.2))
    return {'nearest':nearest, 'hbonds':hbonds, 'motif':'|'.join(motif) or 'no_contact_under_3.2A'}


def host_descriptors(atoms, mapping):
    """Ring normals and amino torsions; node O-H vectors. No model calls."""
    result = {'rings':{},'amino_torsions':{},'OH':{}}
    distances = atoms.get_all_distances(mic=True)
    for slot in mapping['slots']:
        carbons = [i for i in slot['atom_indices'] if atoms[i].symbol=='C']
        oxygens = [i for i in slot['atom_indices'] if atoms[i].symbol=='O']
        ring = [i for i in carbons if all(distances[i,j]>1.65 for j in oxygens)]
        if len(ring)!=6:
            raise ValueError('Aromatic ring mapping changed')
        xyz = mic(atoms, atoms.positions[ring]-atoms.positions[ring[0]])
        normal = np.linalg.svd(xyz-xyz.mean(axis=0))[2][-1]
        if normal[np.argmax(abs(normal))]<0: normal=-normal
        result['rings'][slot['id']] = normal.tolist()
        n,c = slot['substitution_hydrogen'],slot['substitution_carbon']
        if atoms[n].symbol=='N':
            hs=[i for i,a in enumerate(atoms[:len(atoms)-3]) if a.symbol=='H' and distances[i,n]<1.3]
            result['amino_torsions'][slot['id']] = {str(h):float(atoms.get_dihedral(slot['ring_neighbors'][0],c,n,h,mic=True)) for h in hs}
    node=mapping['node_atom_indices']
    for h in [i for i in node if atoms[i].symbol=='H']:
        o=min((i for i in node if atoms[i].symbol=='O'),key=lambda i:atoms.get_distance(h,i,mic=True))
        result['OH'][f'O{o}-H{h}']=mic(atoms,atoms.positions[h]-atoms.positions[o]).tolist()
    return result


def cage_location(atoms):
    """Ideal fcc-node template labels, not a crystallographic cavity assignment."""
    zr=[i for i,a in enumerate(atoms) if a.symbol=='Zr']
    center=atoms.positions[zr[0]]+mic(atoms,atoms.positions[zr]-atoms.positions[zr[0]]).mean(axis=0)
    com,_,_=guest_geometry(atoms)
    offsets={'T+': [.25]*3,'T-':[.75]*3,'O':[.5]*3}
    distances={name:float(np.linalg.norm(mic(atoms,com-center-np.array(v)@atoms.cell))) for name,v in offsets.items()}
    shifts=np.array(list(product(range(-1,2),repeat=3)))
    nodes=shifts@atoms.cell.array
    radius=min(np.linalg.norm(v) for v in nodes if np.linalg.norm(v)>1)
    neighbors=[v for v in nodes if abs(np.linalg.norm(v)-radius)<.05]
    windows=[]
    for u,v in combinations(neighbors,2):
        if abs(np.linalg.norm(u-v)-radius)<.05:
            frac=((u+v)/3)@np.linalg.inv(atoms.cell.array)%1
            if not any(np.linalg.norm(mic(atoms,(frac-f)@atoms.cell.array))<.01 for f in windows): windows.append(frac)
    windows=sorted(windows,key=lambda x:tuple(np.round(x,6)))
    wd=[float(np.linalg.norm(mic(atoms,com-center-w@atoms.cell))) for w in windows]
    return {'nearest_template_cage':min(distances,key=distances.get),'cage_distances_A':distances,
            'nearest_template_window':int(np.argmin(wd)),'window_center_distance_A':min(wd),
            'guest_fractional_com':(com@np.linalg.inv(atoms.cell.array)%1).tolist(),
            'label_status':'nearest ideal-fcc template center, expert assignment pending'}
