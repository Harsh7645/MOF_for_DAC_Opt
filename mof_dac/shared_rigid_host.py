"""Preregistered common-host mapping; no resampling, affine strain or inference."""
import hashlib
import json
import numpy as np
from mof_dac.geometry_diagnostic import mic
from mof_dac.sampling import periodic_edges, periodic_change


def geometry_hash(atoms):
    h=hashlib.sha256()
    for value,dtype in ((atoms.numbers,'<i8'),(atoms.positions,'<f8'),(atoms.cell.array,'<f8'),(atoms.pbc,'u1')):
        h.update(np.ascontiguousarray(value,dtype=dtype).tobytes())
    return h.hexdigest()


def map_guest(source, host):
    """Replace host; translate intact guest by mean MIC displacement of matched Zr0..5."""
    n=len(host)
    if len(source)!=n+3 or not np.array_equal(source.numbers[:n],host.numbers):
        raise ValueError('Host atom order/composition mismatch')
    if not np.array_equal(source.cell.array,host.cell.array) or not np.array_equal(source.pbc,host.pbc):
        raise ValueError('Mapping requires identical fixed cell and PBC')
    if not np.isfinite(host.positions).all() or not np.isfinite(source.positions).all():raise ValueError('Nonfinite geometry')
    if host.get_chemical_symbols()[:6]!=['Zr']*6:raise ValueError('Expected indexed Zr6 node')
    shifts=mic(host,host.positions[:6]-source.positions[:6]);translation=shifts.mean(axis=0)
    residual=float(np.linalg.norm(shifts-translation,axis=1).max())
    guest=source[-3:].copy();guest.set_constraint()
    guest.positions=source.positions[n]+mic(source,source.positions[n:]-source.positions[n])+translation
    mapped=host.copy();mapped.set_constraint();mapped.calc=None;mapped+=guest
    distances=np.linalg.norm(mic(mapped,mapped.positions[:n,None]-mapped.positions[None,n:]),axis=-1)
    minimum=float(distances.min())
    cross=sorted(e for e in periodic_edges(mapped) if (e[0]<n)!=(e[1]<n))
    guest_error=float(np.max(abs(guest.get_all_distances(mic=True)-source[-3:].get_all_distances(mic=True))))
    checks={'ZR_residual_le_0_25A':residual<=.25,'clearance_ge_1A':minimum>=1.,
            'no_host_guest_covalent_cutoff_edges':not cross,'guest_geometry_preserved':guest_error<1e-9,
            'guest_connectivity_preserved':not any(periodic_change(source[-3:],guest).values()),
            'exact_host_coordinates':np.array_equal(mapped.positions[:n],host.positions)}
    evidence={'valid':all(checks.values()),'checks':checks,'translation_A':translation.tolist(),
              'max_Zr_translation_residual_A':residual,'minimum_host_guest_distance_A':minimum,
              'guest_distance_error_A':guest_error,'cross_fragment_edges':cross,
              'host_geometry_sha256':geometry_hash(host),'mapped_geometry_sha256':geometry_hash(mapped)}
    return mapped,evidence


def scheduled_jobs(plan,index):
    """GPU0 owns the common host and all rigid controls; GPU1 can progress independently."""
    jobs=plan['jobs']
    if plan['protocol'].endswith('_v1'):return jobs[index::2]
    flexible=[j for j in jobs if j['kind'] in ('matched','replay')]
    priority=([j for j in jobs if j['id']=='uio66_110111_bare']+[j for j in jobs if j['kind']=='rigid']) if index==0 else [
        j for j in jobs if j['kind']=='gas']+[j for j in jobs if j['id']=='uio66_000000_bare']
    return priority+flexible[index::2]


def check_shared_reference(output, plan):
    """Audit exact common-host provenance; retain errors instead of substituting references."""
    from ase.io import read
    folder=output/'shared_rigid_host';path=folder/'reference.json'
    answer={'valid':False,'errors':[],'valid_rigid_paths':[],'energy_ev':None}
    if not path.exists():answer['errors'].append('shared reference missing');return answer
    try:
        ref=json.loads(path.read_text());host=read(folder/'host.traj')
        digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        expected=ref['host_geometry_sha256']
        if ref['status']!='ready' or ref['fmax_ev_A']>=.005:raise ValueError('Shared host not tightly converged/ready')
        if digest(folder/'host.traj')!=ref['host_file_sha256'] or geometry_hash(host)!=expected:raise ValueError('Common host hash mismatch')
        seed=output/plan['rigid_host']['seed_job_id']/'checkpoint_0.005.traj'
        if json.loads((seed.parent/'result.json').read_text())['status']!='complete':raise ValueError('Shared host prerequisite incomplete')
        if digest(seed)!=ref['source_checkpoint_sha256'] or geometry_hash(read(seed))!=expected:raise ValueError('Common host differs from seed checkpoint')
        if not np.isfinite(ref['energy_ev']) or abs(host.get_potential_energy()-ref['energy_ev'])>1e-10:raise ValueError('Reference energy mismatch')
        answer.update(valid=True,energy_ev=ref['energy_ev'],host_geometry_sha256=expected)
        for job in plan['jobs']:
            if job['kind']!='rigid':continue
            entry=next(r for r in ref['mapping'] if r['id']==job['id'])
            mapped=folder/entry['file']
            if not entry['valid'] or digest(mapped)!=entry['file_sha256'] or geometry_hash(read(mapped)[:job['host_atoms']])!=expected:
                raise ValueError('Mapped common-host pose mismatch')
            pointer=output/job['id']/'shared_host_reference.json'
            if not pointer.exists():continue
            p=json.loads(pointer.read_text())
            if p['reference_sha256']!=digest(path) or p['host_geometry_sha256']!=expected:raise ValueError('Rigid reference pointer mismatch')
            for tol in plan['thresholds_ev_A']:
                checkpoint=output/job['id']/f'checkpoint_{tol:.3f}.traj'
                if checkpoint.exists() and geometry_hash(read(checkpoint)[:job['host_atoms']])!=expected:
                    raise ValueError('A rigid checkpoint used another host')
            answer['valid_rigid_paths'].append(job['id'])
    except (KeyError,ValueError,OSError,StopIteration) as exc:
        answer.update(valid=False,energy_ev=None);answer['errors'].append(str(exc))
    return answer
