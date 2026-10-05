"""Geometry-only DFT diagnostic utilities. No calculator or execution backend."""
import json
from pathlib import Path

import numpy as np
from ase import Atoms
from ase.neighborlist import neighbor_list

from mof_dac.geometry_diagnostic import mic, atom_roles, contacts, host_descriptors
from mof_dac.sampling import periodic_edges
from mof_dac.shared_rigid_host import geometry_hash


def geometry_record(atoms):
    """Python float JSON preserves the source float64 values on round trip."""
    return {'numbers': atoms.numbers.tolist(), 'positions_A': atoms.positions.tolist(),
            'cell_A': atoms.cell.array.tolist(), 'pbc': atoms.pbc.tolist(),
            'geometry_sha256': geometry_hash(atoms)}


def from_record(record):
    atoms = Atoms(numbers=record['numbers'], positions=record['positions_A'],
                  cell=record['cell_A'], pbc=record['pbc'])
    if geometry_hash(atoms) != record['geometry_sha256']:
        raise ValueError('Geometry changed during serialization')
    return atoms


def inspect_geometry(atoms, mapping):
    """Image-explicit distance descriptors; cutoffs are flags, not bond-order claims."""
    n = len(atoms)-3
    d = atoms.get_all_distances(mic=True)
    symbols = atoms.get_chemical_symbols()
    ii, jj, ss, dd = neighbor_list('ijSd', atoms, 3.5)
    pairs = [{'i': int(i), 'j': int(j), 'image_j': s.tolist(), 'distance_A': float(v)}
             for i, j, s, v in zip(ii, jj, ss, dd)]
    zro = [p for p in pairs if symbols[p['i']] == 'Zr' and symbols[p['j']] == 'O']
    protons = []
    for h in mapping['node_atom_indices']:
        if symbols[h] != 'H':
            continue
        donor = min((i for i in mapping['node_atom_indices'] if symbols[i]=='O'), key=lambda i: d[h,i])
        protons.append({'H': h, 'position_A': atoms.positions[h].tolist(), 'nearest_node_O': donor,
                        'OH_A': float(d[h, donor]), 'nearby_acceptors': [p for p in pairs
                        if p['i']==h and symbols[p['j']] in ('O','N') and p['j']!=donor]})
    carboxylates, amino = [], []
    for slot in mapping['slots']:
        cs = [i for i in slot['atom_indices'] if symbols[i]=='C']
        os = [i for i in slot['atom_indices'] if symbols[i]=='O']
        for c in cs:
            oxy = [o for o in os if d[c,o]<1.85]
            if len(oxy)!=2:
                continue
            attached = min((v for v in cs if v!=c), key=lambda v: d[c,v])
            adjacent = min((v for v in cs if v not in (c,attached)), key=lambda v: d[attached,v])
            carboxylates.append({'slot': slot['id'], 'C': c, 'O': oxy,
                'CO_A': [float(d[c,o]) for o in oxy], 'ring_attachment_C': attached,
                'torsion_indices': [[adjacent,attached,c,o] for o in oxy],
                'ring_carboxylate_dihedral_deg': [float(atoms.get_dihedral(adjacent,attached,c,o,mic=True)) for o in oxy],
                'O_Zr_contacts': [p for p in zro if p['j'] in oxy],
                'coordination_cutoff_A': 2.8})
        nitrogen, carbon = slot['substitution_hydrogen'], slot['substitution_carbon']
        if symbols[nitrogen]=='N':
            hs = [h for h in range(n) if symbols[h]=='H' and d[nitrogen,h]<1.3]
            amino.append({'slot': slot['id'], 'N': nitrogen, 'C': carbon, 'H': hs,
                          'CN_A': float(d[carbon,nitrogen]), 'NH_A': [float(d[nitrogen,h]) for h in hs],
                          'HNH_deg': float(atoms.get_angle(hs[0],nitrogen,hs[1],mic=True)) if len(hs)==2 else None,
                          'sum_three_angles_deg': float(sum(atoms.get_angle(a,nitrogen,b,mic=True)
                             for a,b in [(carbon,hs[0]),(carbon,hs[1]),(hs[0],hs[1])])) if len(hs)==2 else None})
    bonds = periodic_edges(atoms)
    adjacency={i:set() for i in range(len(atoms))}
    for i,j,*_ in bonds:
        adjacency[i].add(j);adjacency[j].add(i)
    crowding = []
    for p in pairs:
        i,j,s = p['i'],p['j'],p['image_j']
        edge = min((i,j,*s),(j,i,*[-v for v in s]))
        if i<j and edge not in bonds:
            crowding.append({**p,'shares_bonded_neighbor':bool(adjacency[i]&adjacency[j])})
    guest = list(range(n,n+3))
    return {'Zr_O_contacts': zro, 'Zr_coordination_under_2_8A': {str(i): sum(p['i']==i and p['distance_A']<2.8 for p in zro) for i in range(6)},
            'node_protons': protons, 'carboxylates': carboxylates, 'amino': amino,
            'crowding_nearest_nonbonded_cutoff_pairs': sorted(crowding,key=lambda p:p['distance_A'])[:30],
            'crowding_excluding_shared_bonded_neighbor': sorted([p for p in crowding if not p['shares_bonded_neighbor']],key=lambda p:p['distance_A'])[:30],
            'guest': {'indices': guest, 'symbols': symbols[n:], 'distances_A': d[n:,n:].tolist(),
                      'angle_deg': float(atoms.get_angle(n+1,n,n+2,mic=True)),
                      'periodic_contacts': [p for p in pairs if p['i']>=n and p['j']<n],
                      'contact_descriptor': contacts(atoms,mapping)},
            'host_descriptors': host_descriptors(atoms,mapping),
            'caution': 'Distance-inferred membership and coordination, not chemical validation; all geometries retained.'}


def atom_groups(atoms, mapping):
    n = len(atoms)-3
    roles = atom_roles(atoms,mapping,n)
    amino = [i for i in range(n) if atoms[i].symbol=='N' or ':aminoH' in roles[i]]
    node = list(mapping['node_atom_indices'])
    return {'guest': list(range(n,n+3)), 'amino': amino, 'node': node,
            'rings_carboxylates': [i for i in range(n) if i not in amino+node]}


def aligned_view(atoms, mapping):
    """Display-only fragment unwrapping. Periodic extended net cannot be one finite molecule."""
    xyz = atoms.positions.copy()
    node = mapping['node_atom_indices']
    xyz[node] = xyz[0] + mic(atoms,xyz[node]-xyz[0])
    groups = atom_groups(atoms,mapping)
    for slot in mapping['slots']:
        ids = list(slot['atom_indices'])
        for h in groups['amino']:
            if h>=114 and np.argmin([atoms.get_distance(h,s['substitution_hydrogen'],mic=True) for s in mapping['slots']]) == mapping['slots'].index(slot):
                ids.append(h)
        anchor = slot['substitution_carbon']
        xyz[ids] = xyz[anchor] + mic(atoms,atoms.positions[ids]-atoms.positions[anchor])
        center = xyz[ids].mean(axis=0)
        xyz[ids] += xyz[node].mean(axis=0)+mic(atoms,center-xyz[node].mean(axis=0))-center
    n = len(atoms)-3
    xyz[n:] = atoms.positions[n]+mic(atoms,atoms.positions[n:]-atoms.positions[n])
    center = xyz[n:].mean(axis=0)
    xyz[n:] += xyz[node].mean(axis=0)+mic(atoms,center-xyz[node].mean(axis=0))-center
    return xyz


def qe_template(atoms, identifier):
    """Non-executable template: unknown PP/cutoffs deliberately remain placeholders."""
    species = list(dict.fromkeys(atoms.get_chemical_symbols()))
    lines = ["! TEMPLATE ONLY: environment, pseudopotentials and chemistry approval unresolved",
      "&CONTROL", " calculation='scf', restart_mode='from_scratch', tprnfor=.true.,",
      f" prefix='{identifier}', outdir='./scratch', pseudo_dir='__PSEUDO_DIR__', max_seconds=13800,", "/",
      "&SYSTEM", f" ibrav=0, nat={len(atoms)}, ntyp={len(species)},",
      " input_dft='PBE', vdw_corr='grimme-d3', dftd3_version=4, dftd3_threebody=.true.,",
      " ecutwfc=__ECUTWFC_RY__, ecutrho=__ECUTRHO_RY__,",
      " occupations='fixed', tot_charge=0, nspin=1, nosym=.true., noinv=.true.,", "/",
      "&ELECTRONS", " conv_thr=1.0d-8, electron_maxstep=200, scf_must_converge=.true., mixing_beta=0.3,", "/",
      "ATOMIC_SPECIES"]
    for s in species:
        mass = float(atoms.get_masses()[atoms.get_chemical_symbols().index(s)])
        lines.append(f'{s} {mass!r} __{s}_PBE_UPF__')
    lines += ['CELL_PARAMETERS angstrom'] + [' '.join(repr(float(v)) for v in row) for row in atoms.cell.array]
    lines += ['ATOMIC_POSITIONS angstrom'] + [a.symbol+' '+' '.join(repr(float(v)) for v in a.position) for a in atoms]
    lines += ['K_POINTS automatic','1 1 1 0 0 0']
    return '\n'.join(lines)+'\n'


def force_metrics(reference, candidate, direction, groups):
    """Forces/directions (N,3), same Cartesian frame. Projections are local slopes, not barriers."""
    reference, candidate, direction = map(np.asarray,(reference,candidate,direction))
    if reference.shape!=candidate.shape or reference.shape!=direction.shape or reference.ndim!=2 or reference.shape[1]!=3:
        raise ValueError('Expected matching(N,3) force and local-motion arrays')
    if not all(np.isfinite(x).all() for x in (reference,candidate,direction)):
        raise ValueError('Nonfinite force or motion')
    rows = {}
    for name,ids in groups.items():
        if not ids:
            rows[name] = {'atoms':0}; continue
        r,c,u = reference[ids],candidate[ids],direction[ids]
        norm = np.linalg.norm(u)
        rows[name] = {'atoms':len(ids),'vector_rmse_eV_A':float(np.sqrt(np.mean(np.sum((c-r)**2,axis=1)))),
                     'reference_fmax_eV_A':float(np.linalg.norm(r,axis=1).max()),
                     'candidate_fmax_eV_A':float(np.linalg.norm(c,axis=1).max()),
                     'reference_projection_eV_A':float(np.sum(r*u)/norm) if norm>1e-12 else None,
                     'candidate_projection_eV_A':float(np.sum(c*u)/norm) if norm>1e-12 else None}
    return rows


def decomposition(before_complex, after_complex, before_host, after_host):
    dc = None if before_complex is None or after_complex is None else after_complex-before_complex
    dh = None if before_host is None or after_host is None else after_host-before_host
    return {'delta_complex_eV':dc,'delta_host_eV':dh,
            'delta_guest_associated_eV':None if dc is None or dh is None else dc-dh}
