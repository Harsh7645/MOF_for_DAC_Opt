"""Staged LBFGS with persistent history, bounded steps and durable checkpoints."""
import json
import time
from pathlib import Path
import numpy as np
from ase.constraints import FixAtoms
from ase.io import write
from ase.optimize import LBFGS
from ase.neighborlist import neighbor_list
from mof_dac.sampling import periodic_change


class ScientificHold(RuntimeError):
    pass


def save(path, obj):
    temp=Path(str(path)+'.tmp');temp.write_text(json.dumps(obj,indent=2,allow_nan=False),encoding='utf-8');temp.replace(path)


def staged_path(atoms, calculator, output, thresholds=(.02,.01,.005), max_steps=1200,
                max_seconds=1200, rigid_host_atoms=0, direct=False, optimizer_class=LBFGS):
    """One optimizer instance per path; repeated run calls retain its curvature history."""
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    if not thresholds or any(t<=0 for t in thresholds) or any(a<=b for a,b in zip(thresholds,thresholds[1:])):
        raise ValueError('Strictly decreasing positive thresholds required')
    initial=atoms.copy();state=atoms.copy();state.calc=calculator
    if rigid_host_atoms:state.set_constraint(FixAtoms(indices=range(rigid_host_atoms)))
    started=time.monotonic();record={'status':'running','checkpoints':[],'direct':direct,'rigid_host_atoms':rigid_host_atoms}
    optimizer=optimizer_class(state,trajectory=str(output/'path.traj'),logfile=str(output/'optimizer.log'),
                              restart=str(output/'optimizer_restart.json'),maxstep=.1)
    def observe():
        energy=float(state.get_potential_energy());forces=state.get_forces();allforces=state.get_forces(apply_constraint=False)
        if not np.isfinite(energy) or not np.isfinite(forces).all() or not np.isfinite(allforces).all() or not np.isfinite(state.positions).all():
            raise ScientificHold('Nonfinite state')
        if not np.array_equal(initial.cell.array,state.cell.array):raise ScientificHold('Cell changed')
        if rigid_host_atoms and not np.array_equal(initial.positions[:rigid_host_atoms],state.positions[:rigid_host_atoms]):
            raise ScientificHold('Rigid host moved')
        change=periodic_change(initial,state)
        if any(change.values()):
            save(output/'unusual_connectivity.json',{'step':optimizer.nsteps,**change});raise ScientificHold('Image-aware bond cutoff graph changed; review required')
        if len(neighbor_list('d',state,.7)):raise ScientificHold('Severe contact below0.7A')
        fmax=float(np.linalg.norm(forces,axis=1).max())
        step={'step':optimizer.nsteps,'energy_ev':energy,'mobile_fmax_ev_A':fmax,
              'all_atom_fmax_ev_A':float(np.linalg.norm(allforces,axis=1).max()),'elapsed_seconds':time.monotonic()-started}
        with (output/'steps.jsonl').open('a',encoding='utf-8') as handle:handle.write(json.dumps(step)+'\n')
        for tol in thresholds:
            if fmax<tol and not any(c['tolerance']==tol for c in record['checkpoints']):
                name=f'checkpoint_{tol:.3f}.traj';write(output/name,state)
                record['checkpoints'].append({**step,'tolerance':tol,'structure':name,'optimizer_iteration':getattr(optimizer,'iteration',None)})
        save(output/'result.json',record)
        if time.monotonic()-started>max_seconds:raise TimeoutError('Per-path wall limit')
    optimizer.attach(observe,interval=1)
    try:
        for tol in ([thresholds[-1]] if direct else thresholds):
            optimizer.run(fmax=tol,steps=max(0,max_steps-optimizer.nsteps))
            if float(np.linalg.norm(state.get_forces(),axis=1).max())>=tol:
                record['status']='step_limit';break
        else:record['status']='complete'
    except ScientificHold as exc:record.update(status='scientific_hold',error=str(exc))
    except Exception as exc:record.update(status='failed',error=f'{type(exc).__name__}: {exc}')
    finally:
        record.update(steps=optimizer.nsteps,elapsed_seconds=time.monotonic()-started)
        write(output/'last_state.traj',state);save(output/'result.json',record)
        optimizer.close()
    return record
