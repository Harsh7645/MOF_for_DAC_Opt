"""Preparation/parser tests: synthetic outputs are explicitly not research results."""
import json
from pathlib import Path
import pytest
from scripts.prepare_qe_water_pilot import verify_library, build, pilot_input
from scripts.run_qe_water_pilot import parse_result, BOHR_A, RY_EV, verify_package

LIB=Path('data/external/sssp_1.3.0_pbe_precision')


def test_pinned_real_library_and_input_electrons():
    if not LIB.exists():pytest.skip('Official data downloaded locally only')
    p=verify_library(LIB)['potentials']
    assert [p[e]['upf']['z_valence'] for e in ('Zr','O','C','N','H')]==[12,6,4,5,1]
    assert max(v['cutoff_wfc'] for v in p.values())==80
    assert max(v['cutoff_rho'] for v in p.values())==600
    assert '4s2 4p6' in p['Zr']['upf']['semicore']
    from ase import Atoms
    text=pilot_input(Atoms('OH2',positions=[[0,0,0],[1,0,0],[0,1,0]],cell=[10,10,10]),'test',p)
    assert 'dftd3_threebody=.false.' in text and '__' not in text
    assert 'ecutwfc=80, ecutrho=600' in text and 'K_POINTS gamma' in text
    assert 'conv_thr=1.0d-8' in text and "calculation='scf'" in text


def synthetic_output(tmp_path):
    # One synthetic atom, deliberately unrelated to UiO-66; format/unit test only.
    xml='''<espresso Units="Hartree atomic units"><general_info><creator VERSION="7.5"/></general_info>
    <parallel_info><nprocs>32</nprocs><nthreads>1</nthreads></parallel_info>
    <input><control_variables><calculation>scf</calculation></control_variables></input>
    <output><convergence_info><scf_conv><convergence_achieved>true</convergence_achieved><n_scf_steps>12</n_scf_steps></scf_conv></convergence_info>
    <band_structure><nelec>2</nelec></band_structure><atomic_structure>
    <atomic_positions><atom name="He">0 0 0</atom></atomic_positions>
    <cell><a1>10 0 0</a1><a2>0 10 0</a2><a3>0 0 10</a3></cell></atomic_structure>
    <total_energy><etot>-2</etot></total_energy><forces>0.001 0 0</forces></output><exit_status>0</exit_status></espresso>'''
    f=tmp_path/'synthetic.xml';f.write_text(xml)
    geo={'symbols':['He'],'positions_A':[[0,0,0]],'cell_A':[[10*BOHR_A,0,0],[0,10*BOHR_A,0],[0,0,10*BOHR_A]]}
    return 'Program PWSCF v.7.5\nconvergence has been achieved\n! total energy = -4.00000000 Ry\nJOB DONE.',f,geo


def test_xml_hartree_and_text_ry_units(tmp_path):
    out,xml,geo=synthetic_output(tmp_path);r=parse_result(out,xml,geo,2,32)
    assert r['energy_eV']==pytest.approx(-4*RY_EV)
    assert r['forces_eV_A'][0][0]==pytest.approx(.002*RY_EV/BOHR_A)
    assert r['energy_uncertainty_eV'] is None


@pytest.mark.parametrize('fault',['incomplete','unconverged','geometry','identity','electrons','allocation','energy','relax','xml_unconverged'])
def test_reject_invalid_comparison(tmp_path,fault):
    out,xml,geo=synthetic_output(tmp_path);electrons=2;ranks=32
    if fault=='incomplete':out=out.replace('JOB DONE.','')
    if fault=='unconverged':out+='\nconvergence NOT achieved'
    if fault=='geometry':geo['positions_A'][0][0]=.001
    if fault=='identity':geo['symbols']=['H']
    if fault=='electrons':electrons=3
    if fault=='allocation':ranks=16
    if fault=='energy':out=out.replace('-4.00000000','-4.01000000')
    if fault=='relax':xml.write_text(xml.read_text().replace('>scf<','>relax<'))
    if fault=='xml_unconverged':xml.write_text(xml.read_text().replace('>true<','>false<'))
    with pytest.raises(ValueError):parse_result(out,xml,geo,electrons,ranks)


def test_package_tamper_fails(tmp_path):
    from scripts.run_qe_water_pilot import sha
    (tmp_path/'input.in').write_text('fixed')
    (tmp_path/'file_hashes.json').write_text(json.dumps({'input.in':sha(tmp_path/'input.in')}))
    assert verify_package(tmp_path)==1
    (tmp_path/'input.in').write_text('changed')
    with pytest.raises(ValueError):verify_package(tmp_path)


def test_preserve_prior_package(tmp_path):
    with pytest.raises(FileExistsError):build(Path('absent'),Path('absent'),tmp_path)


def test_retention_includes_failed_scratch(tmp_path):
    from scripts.run_qe_water_pilot import sha,verify_retained
    evidence=tmp_path/'evidence';scratch=tmp_path/'scratch';evidence.mkdir();scratch.mkdir()
    (evidence/'stderr.log').write_text('synthetic failure')
    (scratch/'partial.dat').write_text('synthetic partial restart')
    (evidence/'states.json').write_text(json.dumps([{'status':'failed_or_incomplete'}]))
    (evidence/'evidence_hashes.json').write_text(json.dumps({'stderr.log':sha(evidence/'stderr.log')}))
    (evidence/'scratch_hashes.json').write_text(json.dumps({'partial.dat':sha(scratch/'partial.dat')}))
    assert verify_retained(evidence,scratch)['two_complete'] is False
    (scratch/'partial.dat').write_text('truncated')
    with pytest.raises(ValueError):verify_retained(evidence,scratch)


def test_unapproved_preflight_never_invokes_executable(tmp_path,monkeypatch):
    import scripts.run_qe_water_pilot as runner
    (tmp_path/'file_hashes.json').write_text('{}')
    monkeypatch.setattr(runner.platform,'system',lambda:'Linux')
    def forbidden(*args,**kwargs):raise AssertionError('Executable must not be called')
    monkeypatch.setattr(runner.subprocess,'run',forbidden)
    with pytest.raises(ValueError,match='allocation'):
        runner.preflight(tmp_path,{'package_hash_manifest_sha256':runner.sha(tmp_path/'file_hashes.json')})
