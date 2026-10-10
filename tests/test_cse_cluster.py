"""Synthetic CSE allocation checks; do not imply real cluster entitlement."""
import pytest
import hashlib
import json
from pathlib import Path
from scripts.run_qe_water_pilot import preflight, validate_slurm
from tests.test_param_shakti import allocation


def cpu_allocation():
    config,env,job=allocation()
    config.update(runtime_mode='cse_slurm_v1',ranks=12,slurm_partition='cpupart')
    env['SLURM_NTASKS']='12'
    return config,env,job.replace('40','12').replace('medium','cpupart')


def test_cse_cpu_layout_is_not_param_40_rank_rule():
    config,env,job=cpu_allocation()
    assert validate_slurm(config,env,job)['NumTasks']=='12'


def test_cse_rejects_allocated_gpu():
    config,env,job=cpu_allocation()
    with pytest.raises(ValueError,match='CPU-only'):
        validate_slurm(config,env,job+' AllocTRES=cpu=12,gres/gpu=1')


def test_cse_preflight_refuses_login_node(monkeypatch,tmp_path):
    import scripts.run_qe_water_pilot as runner
    monkeypatch.setattr(runner,'sha',lambda path:'synthetic')
    monkeypatch.setattr(runner,'verify_package',lambda path:140)
    monkeypatch.setattr(runner.platform,'system',lambda:'Linux')
    monkeypatch.delenv('SLURM_JOB_ID',raising=False)
    config,_,_=cpu_allocation()
    config.update(package_hash_manifest_sha256='synthetic',allocation_confirmed=True,
                  approval_reference='synthetic test only')
    with pytest.raises(ValueError,match='refuse login-node'):
        preflight(tmp_path,config)


def test_hash_works_without_python311_file_digest(monkeypatch,tmp_path):
    from scripts.run_qe_water_pilot import sha
    monkeypatch.delattr(hashlib,'file_digest',raising=False)
    path=tmp_path/'bytes';path.write_bytes(b'preserve frozen input')
    assert sha(path)==hashlib.sha256(path.read_bytes()).hexdigest()


def test_staging_refuses_existing_root_and_retains_failure_ledger(monkeypatch,tmp_path):
    from hpc.cse_v1.stage_remote import stage
    monkeypatch.setattr(Path,'home',classmethod(lambda cls:tmp_path))
    root=tmp_path/'mof_dac_qe75_v2_synthetic'
    result=stage(root,'create')
    assert result['created'][0]['path']==str(root)
    with pytest.raises(FileExistsError):stage(root,'create')
    with pytest.raises(FileNotFoundError):stage(root,'verify')
    assert json.loads((root/'remote_directory_ledger.json').read_text())['jobs_submitted']==[]
    with pytest.raises(ValueError):stage(tmp_path.parent/'outside_home','create')
