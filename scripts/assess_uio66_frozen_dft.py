"""Assess supplied frozen-geometry single points; no DFT/UMA runner or model import."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

from mof_dac.frozen_dft import decomposition, force_metrics, from_record


def assess(package, records):
    manifest=json.loads((package/'manifest.json').read_text())
    components=manifest['components'];accepted={};excluded={}
    for key,result in records.items():
        if key not in components:
            raise ValueError(f'Unknown component: {key}')
        if result is None:
            continue
        component=components[key]
        geometry=json.loads((package/component['geometry_file']).read_text());atoms=from_record(geometry)
        if result.get('geometry_sha256')!=component['geometry_sha256']:
            raise ValueError(f'Geometry mismatch: {key}')
        if not result.get('electronic_converged',False) or result.get('ionic_steps')!=0:
            excluded[key]='Missing SCF convergence or ionic_steps !=0';continue
        if result.get('charge')!=0 or result.get('spin')!='nonmagnetic':
            excluded[key]='Charge/spin differs from provisional neutral closed-shell protocol';continue
        required=['method_id','energy_convention','code_version','pseudopotential_hashes','raw_output','raw_output_sha256']
        if any(not result.get(k) for k in required):
            raise ValueError(f'Missing calculation provenance: {key}')
        source=Path(result['raw_output'])
        if not source.is_absolute():source=package/source
        if hashlib.sha256(source.read_bytes()).hexdigest()!=result['raw_output_sha256']:
            raise ValueError(f'Raw output hash mismatch: {key}')
        forces=np.array(result['forces_eV_A']);energy=float(result['energy_eV'])
        if forces.shape!=(len(atoms),3) or not np.isfinite(forces).all() or not np.isfinite(energy):
            raise ValueError(f'Nonfinite/incorrect shape: {key}')
        bound=result.get('energy_uncertainty_eV')
        if bound is not None and (not np.isfinite(bound) or bound<0):
            raise ValueError('Numerical uncertainty must be finite and nonnegative')
        accepted[key]=result
    transitions=[]
    for tr in manifest['transitions']:
        keys=[f'{tr[which]}_{kind}' for kind in ('complex','host') for which in ('before','after')]
        result=[accepted.get(k) for k in keys]
        conventions={(r['method_id'],r['energy_convention'],r['code_version'],
                      json.dumps(r['pseudopotential_hashes'],sort_keys=True)) for r in result if r}
        if len(conventions)>1:raise ValueError('Mixed method/energy/pseudopotential conventions within decomposition')
        dft=decomposition(*(r['energy_eV'] if r else None for r in result))
        uma=decomposition(*(components[k]['uma']['energy_eV'] if components[k]['uma'] else None for k in keys))
        row={'id':tr['id'],'DFT':dft,'UMA':uma,'complete_DFT_decomposition':all(r is not None for r in result)}
        row['DFT_minus_UMA_eV']={k:dft[k]-uma[k] if dft[k] is not None and uma[k] is not None else None for k in dft}
        guest=[accepted.get(f"{tr[k]}_guest_optional") for k in ('before','after')]
        if all(guest):
            for g in guest:
                signature=(g['method_id'],g['energy_convention'],g['code_version'],json.dumps(g['pseudopotential_hashes'],sort_keys=True))
                if conventions and signature not in conventions:raise ValueError('Optional guest method convention differs')
        dg=guest[1]['energy_eV']-guest[0]['energy_eV'] if all(guest) else None
        row['optional_periodic_guest_delta_eV']=dg
        row['optional_interaction_delta_eV']=dft['delta_guest_associated_eV']-dg if dg is not None and dft['delta_guest_associated_eV'] is not None else None
        # A numerical uncertainty is required before classifying the sign.
        bounds=[r.get('energy_uncertainty_eV') if r else None for r in result]
        def classify(delta,bound):
            if delta is None or bound is None:return 'unassessed_missing_energy_or_numerical_bound'
            return 'negative_resolved' if delta < -bound else ('positive_resolved' if delta>bound else 'within_numerical_uncertainty')
        dc_bound=sum(bounds[:2]) if all(v is not None for v in bounds[:2]) else None
        dh_bound=sum(bounds[2:]) if all(v is not None for v in bounds[2:]) else None
        row['DFT_numerical_sign']={
            'complex':classify(dft['delta_complex_eV'],dc_bound),'host':classify(dft['delta_host_eV'],dh_bound),
            'guest_associated':classify(dft['delta_guest_associated_eV'],dc_bound+dh_bound if dc_bound is not None and dh_bound is not None else None)}
        transitions.append(row)
    force_rows=[]
    for pose in manifest['poses']:
        for kind in ('complex','host'):
            key=f"{pose['id']}_{kind}";dft=accepted.get(key);uma=components[key]['uma']
            if not dft or not uma:continue
            n=pose['host_atoms'] if kind=='host' else len(pose['atom_symbols'])
            groups={k:[i for i in ids if i<n] for k,ids in pose['groups'].items()}
            force_rows.append({'component':key,'groups':force_metrics(uma['forces_eV_A'],dft['forces_eV_A'],
                              pose['local_motion_A'][:n],groups),
                              'local_motion_frames':pose['motion_frames'],
                              'meaning':'Saved optimizer secant, not a diffusion trajectory or activation barrier.'})
    return {'accepted':list(accepted),'excluded':excluded,'transitions':transitions,'forces':force_rows,
            'missing_mandatory_DFT':[k for k,v in components.items() if v['kind']!='guest_optional' and k not in accepted],
            'claim':'Frozen same-composition differences only; no physical-accuracy or material-ranking conclusion.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',type=Path,required=True)
    p.add_argument('--records',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('Preserve previous assessment')
    answer=assess(a.package,json.loads(a.records.read_text()))
    a.output.write_text(json.dumps(answer,indent=2,allow_nan=False)+'\n')
