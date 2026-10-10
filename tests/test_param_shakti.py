import importlib.util
import json
from pathlib import Path
import pytest
from scripts.run_qe_water_pilot import validate_slurm


def allocation():
    # Synthetic Slurm metadata, not an actual account/allocation.
    config={'site_layout_verified':True,'allocation_charge_reviewed':True,'ranks':40,
            'threads':1,'slurm_account':'synthetic','slurm_partition':'medium'}
    env={'SLURM_JOB_ID':'42','SLURM_NTASKS':'40','SLURM_JOB_NUM_NODES':'1'}
    job='JobId=42 JobState=RUNNING NumNodes=1 NumCPUs=40 NumTasks=40 CPUs/Task=1 TimeLimit=04:00:00 Account=synthetic Partition=medium MinMemoryNode=64G'
    return config,env,job


def test_registered_slurm_layout():
    c,e,j=allocation();assert validate_slurm(c,e,j)['NumCPUs']=='40'


@pytest.mark.parametrize('before,after',[('NumTasks=40','NumTasks=32'),('Account=synthetic','Account=other'),
    ('JobState=RUNNING','JobState=PENDING'),('TimeLimit=04:00:00','TimeLimit=08:00:00'),
    ('MinMemoryNode=64G','MinMemoryNode=32G'),('NumNodes=1','NumNodes=2')])
def test_slurm_mismatch_rejected(before,after):
    c,e,j=allocation()
    with pytest.raises(ValueError):validate_slurm(c,e,j.replace(before,after))


def test_login_is_not_compute_entitlement():
    c,e,j=allocation();e.pop('SLURM_JOB_ID')
    with pytest.raises(ValueError):validate_slurm(c,e,j)
    c['allocation_charge_reviewed']=False
    with pytest.raises(ValueError):validate_slurm(c,e,j)


def test_pinned_transfer_roundtrip(tmp_path):
    archive=Path('artifacts/phase3/UIO66_Frozen_DFT_QE75_v2.zip')
    if not archive.exists():pytest.skip('Local sealed artifacts absent')
    spec=importlib.util.spec_from_file_location('verify_extract','hpc/param_shakti_v1/verify_extract.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    receipt=archive.with_name('uio66_frozen_dft_v2_qe75_receipt.json')
    answer=module.extract(archive,receipt,tmp_path/'package')
    assert answer['verified_files']==140
    with pytest.raises(FileExistsError):module.extract(archive,receipt,tmp_path/'package')
    bad=json.loads(receipt.read_text());bad['zip_sha256']='0'*64
    fake=tmp_path/'wrong_receipt.json';fake.write_text(json.dumps(bad))
    with pytest.raises(ValueError):module.extract(archive,fake,tmp_path/'other')
