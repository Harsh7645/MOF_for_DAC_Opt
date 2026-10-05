"""Read-only publication/ODAC parent comparison; no corrections or model inference."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import warnings
import numpy as np
from ase import Atoms
from ase.io import read
import spglib


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def describe(atoms):
    symbols=atoms.get_chemical_symbols();d=atoms.get_all_distances(mic=True)
    oxygen=[i for i,s in enumerate(symbols) if s=='O']
    oh=[]
    for i,s in enumerate(symbols):
        if s=='H':
            j=min(oxygen,key=lambda j:d[i,j])
            if d[i,j]<1.3:oh.append({'H_index':i,'O_index':j,'OH_A':float(d[i,j]),
                                    'H_position_A':atoms.positions[i].tolist()})
    return {'atoms':len(atoms),'composition':dict(Counter(symbols)),
            'cell_A':atoms.cell.array.tolist(),'cell_parameters':atoms.cell.cellpar().tolist(),
            'volume_A3':atoms.get_volume(),'H_with_O_within_1_3_A':oh}


def compare(cif,parent):
    if hashlib.md5(cif.read_bytes()).hexdigest()!='dc66090fa4ba6d2d1ccb52aaa8e2314c':
        raise ValueError('Original CIF published checksum mismatch')
    with warnings.catch_warnings(record=True) as log:
        warnings.simplefilter('always');original=read(cif)
    record=json.loads(parent.read_text());archived=Atoms(numbers=record['numbers'],
        positions=record['positions_angstrom'],cell=record['cell_angstrom'],pbc=record['pbc'])
    # Analysis copy only. Never write standardized coordinates as calculation inputs.
    primitive=spglib.standardize_cell((original.cell.array,original.get_scaled_positions(),original.numbers),
                                      to_primitive=True,no_idealize=True,symprec=1e-3)
    if primitive is None:raise ValueError('Cannot derive comparison primitive cell')
    cell,scaled,numbers=primitive;analysis=Atoms(numbers=numbers,scaled_positions=scaled,cell=cell,pbc=True)
    return {'original_source':'https://acs.figshare.com/articles/dataset/2022858',
        'download':'https://ndownloader.figshare.com/files/3594150','publication_doi':'10.1021/jz4002345',
        'CIF_sha256':sha(cif),'published_md5':'dc66090fa4ba6d2d1ccb52aaa8e2314c',
        'archived_parent_sha256':sha(parent),'original':describe(original),'archived_parent':describe(archived),
        'analysis_only_primitive':describe(analysis),'spglib_version':spglib.__version__,
        'primitive_method':'to_primitive=True,no_idealize=True,symprec=0.001A; read-only comparison, not replacement geometry',
        'same_primitive_composition':Counter(analysis.numbers)==Counter(archived.numbers),
        'primitive_volume_difference_percent':100*(archived.get_volume()/analysis.get_volume()-1),
        'parser_warnings':[str(w.message) for w in log],
        'CIF_source_notes':'data_calc0; creation method GDIS; audit date 2012-12-19; P1; do not label these coordinates experimental refinement without reviewing paper/SI',
        'unresolved':['No unique periodic atom correspondence established across source and ODAC frame7.',
                      'Proton sites/orientations and original-to-ODAC preprocessing/relaxation require expert review.',
                      'Parent comparison does not validate manually constructed amino rotamers or ordered derivatives.'],
        'preservation':'Canonical CIF, archived parent and all 21 frozen calculation geometries unchanged.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cif',type=Path,default=Path('data/external/uio66_publication_jz4002345/jz4002345_si_002.cif'))
    p.add_argument('--parent',type=Path,default=Path('artifacts/phase3/uio66_frozen_dft_v1_review/parent_source.json'))
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Keep previous provenance comparison')
    a.output.write_text(json.dumps(compare(a.cif,a.parent),indent=2)+'\n',encoding='utf8')
