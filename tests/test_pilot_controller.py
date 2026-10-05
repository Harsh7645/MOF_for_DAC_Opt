"""Deadline/stop checks never need CUDA or a scientific calculation."""
import subprocess
import sys
import time

import pytest

from scripts.control_uio66_sampling_pilot import monitor, stop_reason


def test_budget_and_chemistry_stop_terminate_only_owned_process(tmp_path):
    stop = tmp_path/'STOP'
    assert stop_reason(time.time()+60,stop) is None
    stop.write_text('Expert found a material protonation issue')
    assert 'protonation' in stop_reason(time.time()+60,stop)
    stop.unlink()
    child = subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)'],start_new_session=True)
    with pytest.raises(RuntimeError,match='deadline'):
        monitor([child],time.time()-1,stop)
    assert child.poll() is not None
    sibling = subprocess.Popen([sys.executable,'-c','pass'],start_new_session=True)
    monitor([sibling],time.time()+10,stop)
    assert sibling.returncode==0
