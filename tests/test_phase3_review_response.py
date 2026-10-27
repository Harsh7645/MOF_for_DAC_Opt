"""Review-package checks only: no scientific fits, optimization or inference."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from ase.io import read
from mof_dac.instances import decode_slot_state

ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'plans/phase3-review-response-v2/inspection'


def load(path):
    return json.loads(path.read_text())


def test_decoder_ties_count_and_objective_independence():
    # Three equal B-A contrasts: stable lower-slot tie breaking; k fixed externally.
    assert np.array_equal(decode_slot_state([.2,.8,.1,.7,.3,.9],0),[1,0,1,0,1,0])
    assert np.array_equal(decode_slot_state([0,1,1,2,2,3],2),[0,1,0,1,1,0])
    # No h/W argument or quadratic energy evaluation in the decoder.
    assert np.array_equal(decode_slot_state([0,1,0,3,0,2],1),[1,0,0,1,1,0])


def test_exact_geometries_csv_and_integer_images():
    geometries={}
    for p in (PACKET/'exact').glob('uio66*.json'):
        g=load(p); a=read(p.with_suffix('.traj'))
        assert np.array_equal(g['positions_A'],a.positions)
        assert np.array_equal(g['cell_A'],a.cell.array)
        assert np.array_equal(g['numbers'],a.numbers)
        geometries[p.stem]=(np.array(g['positions_A']),np.array(g['cell_A']))
    assert len(geometries)==5
    p=load(PACKET/'exact/parent_source.json')
    geometries['parent']=(np.array(p['positions_angstrom']),np.array(p['cell_angstrom']))
    with (PACKET/'coordinates.csv').open() as handle:rows=list(csv.DictReader(handle))
    assert len(rows)==749
    for r in rows:
        assert np.array_equal([float(r[k]) for k in ('x_A','y_A','z_A')],geometries[r['pose']][0][int(r['atom_index'])])
    with (PACKET/'view_images.csv').open() as handle:
        for r in csv.DictReader(handle):
            name='parent' if r['view']=='parent_node' else r['view'].rsplit('_',1)[0]
            xyz,cell=geometries[name];image=np.array([int(r[k]) for k in ('image_a','image_b','image_c')])
            assert np.array_equal([float(r[k]) for k in ('x_A','y_A','z_A')],xyz[int(r['atom_index'])]+image@cell)
    assert len(list((PACKET/'views').glob('*.svg')))==11
    assert len(list((PACKET/'views').glob('*f0.010_OH.svg')))==2


def test_retained_draw_denominators_and_seed_identity():
    with (PACKET/'bootstrap_draw_status.csv').open() as handle:rows=list(csv.DictReader(handle))
    assert len(rows)==2000
    assert sum(r['excluded_from_conditional_summaries']=='True' for r in rows if r['model']=='pairwise')==23
    assert sum(r['excluded_from_conditional_summaries']=='True' for r in rows if r['model']=='additive')==0
    with (PACKET/'pilot_seed_streams.csv').open() as handle:rows=list(csv.DictReader(handle))
    assert len(rows)==512 and len({r['seed_entropy'] for r in rows})==512
    for r in rows:
        seed=json.loads(r['seed_entropy'])
        assert seed[0]==20261003 and seed[2]=={'CO2':0,'H2O':1}[r['gas']]
        assert seed[3:]==[int(r['batch']),int(r['batch_slot'])]
        assert int(r['start'])==16*int(r['batch'])+int(r['batch_slot'])


def test_new_packet_receipt_and_old_scope_unchanged():
    for base,path in ((PACKET,PACKET/'receipt.json'),(ROOT,ROOT/'plans/phase3-methods-scope-v1/scope_receipt.json')):
        receipt=load(path)
        for relative,expected in receipt['outputs'].items():
            assert hashlib.sha256((base/relative).read_bytes()).hexdigest()==expected,relative
