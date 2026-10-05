import json
import numpy as np
import pytest
from ase import Atoms
from mof_dac.frozen_dft import geometry_record,from_record,qe_template,decomposition,force_metrics


def test_exact_geometry_roundtrip_and_tamper():
    a=Atoms('OH2',positions=[[.12345678912345678,0,0],[1.234567891234567,0,0],[0,1.234567891234567,0]],cell=[[14.123456789123456,0,0],[2,13.3,0],[1,3,12.2]],pbc=True)
    r=json.loads(json.dumps(geometry_record(a)))
    assert np.array_equal(from_record(r).positions,a.positions)
    assert np.array_equal(from_record(r).cell.array,a.cell.array)
    r['positions_A'][0][0]+=.00000001
    with pytest.raises(ValueError):from_record(r)


def test_template_is_static_and_blocked():
    a=Atoms('OH2',positions=[[0,0,0],[1,0,0],[0,1,0]],cell=[12,12,12],pbc=True)
    text=qe_template(a,'synthetic')
    assert "calculation='scf'" in text and '__ECUTWFC_RY__' in text and '__O_PBE_UPF__' in text
    assert "dftd3_version=4" in text and 'CELL_PARAMETERS angstrom' in text
    assert "calculation='relax'" not in text and '&IONS' not in text


def test_decomposition_does_not_impute_missing_host():
    d=decomposition(4,3,None,1)
    assert d['delta_complex_eV']==-1 and d['delta_guest_associated_eV'] is None
    assert decomposition(10,8,7,6)=={'delta_complex_eV':-2,'delta_host_eV':-1,'delta_guest_associated_eV':-1}


def test_force_projection_and_zero_motion():
    r=np.zeros((2,3));c=np.array([[1.,0,0],[0,2,0]]);u=np.array([[2.,0,0],[0,0,0]])
    result=force_metrics(r,c,u,{'guest':[0],'node':[1],'amino':[]})
    assert result['guest']['candidate_projection_eV_A']==1
    assert result['node']['candidate_projection_eV_A'] is None
    assert result['amino']['atoms']==0
    with pytest.raises(ValueError):force_metrics(r,c[:1],u,{})


def test_empty_dft_preserves_all_missing():
    from pathlib import Path
    from scripts.assess_uio66_frozen_dft import assess
    package=Path('artifacts/phase3/uio66_frozen_dft_v1_review')
    if not package.exists():pytest.skip('Local research artifacts unavailable')
    answer=assess(package,{})
    assert len(answer['missing_mandatory_DFT'])==14
    assert all(t['DFT']['delta_complex_eV'] is None for t in answer['transitions'])
