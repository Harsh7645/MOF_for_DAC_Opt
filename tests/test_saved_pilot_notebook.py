"""Synthetic retention checks; no real UMA energies or GPU allocation."""
import json
from pathlib import Path
import sys
import zipfile

import pytest

from scripts.create_saved_pilot_notebook import batch_cell, prepare


@pytest.mark.parametrize('fail',[False,True])
def test_saved_batch_waits_and_retains_terminal_evidence(tmp_path,fail):
    body = (
        "import subprocess\n"
        "OUT=WORKING/'synthetic_out'\nOUT.mkdir()\n"
        "PRE=WORKING/'synthetic_preflight'\nPRE.mkdir()\n"
        "(PRE/'provenance.txt').write_text('synthetic only')\n"
        "controller_log=WORKING/'synthetic_controller.log'\n"
        "controller_log.write_text('synthetic only')\n"
        f"CONTROLLER=subprocess.Popen([{sys.executable!r},'-c',"
        "\"import time; from pathlib import Path; time.sleep(.1); Path('terminal.txt').write_text('raw synthetic evidence')\"],cwd=OUT)\n"
        "CONTROLLER.wait()\n"
    )
    if fail:
        body += "raise ValueError('synthetic failure after owned job ends')\n"
    namespace = {}
    exec(compile(batch_cell(body,tmp_path),'synthetic saved batch','exec'),namespace)
    assert namespace['CONTROLLER'].poll()==0
    with zipfile.ZipFile(tmp_path/'UIO66_sampling_saved_batch_evidence.zip') as archive:
        assert archive.read('synthetic_out/terminal.txt')==b'raw synthetic evidence'
        assert archive.read('synthetic_preflight/provenance.txt')==b'synthetic only'
        state=json.loads(archive.read('saved_batch_state.json'))
        assert state['status'].startswith('failed' if fail else 'controller returned')
        assert 'finished_utc' in state


def test_saved_notebook_rejects_old_receipt_before_inference(tmp_path):
    root=Path(__file__).resolve().parents[1]
    notebook=prepare(root/'kaggle/uio66_sampling_pilot_authorized.ipynb')
    code=''.join(notebook['cells'][1]['source'])
    assert code==''.join(prepare(root/'kaggle/uio66_sampling_pilot_authorized.ipynb',approved=True)['cells'][1]['source'])
    inputs=tmp_path/'input'
    inputs.mkdir()
    (inputs/'execution_release.json').write_text('{}')
    working=tmp_path/'working'
    working.mkdir()
    code=code.replace("WORKING=Path('/kaggle/working')",f"WORKING=Path({str(working)!r})")
    code=code.replace("Path('/kaggle/input')",f"Path({str(inputs)!r})")
    namespace={}
    exec(compile(code,'unapproved saved batch','exec'),namespace)
    state=json.loads((working/'saved_batch_state.json').read_text())
    assert state['error_type']=='AssertionError'
    assert 'Replacement run approval' in state['error']
    assert 'CONTROLLER' not in namespace and 'CHECKPOINT' not in namespace
