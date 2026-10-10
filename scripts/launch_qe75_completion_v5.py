"""Launch ONE authorized600Ry completion attempt using reviewed controls."""
import json,time
from pathlib import Path
from qe75_fedora_v1 import ROOT,sha
from qe75_completion_v5 import dump
import launch_qe75_rho625_v1 as tested

EV=ROOT/'evidence/qe75-fedora-completion-v5'
CONFIG=ROOT/'configs/qe75-fedora-completion-v5.json'

if __name__=='__main__':
    with (EV/'launcher-entered.json').open('x') as f:json.dump({'time':time.time(),'script_sha256':sha(Path(__file__))},f)
    a=json.loads((EV/'allocation.json').read_text())
    dump(EV/'host-clock-anchor.json',tested.anchor(a))
    c=json.loads(CONFIG.read_text())
    tested.SCRIPT=ROOT/'scripts/qe75_completion_v5.py'
    result=tested.run_guard(c,CONFIG)
    dump(EV/'launcher-final.json',{'result':result,'time':time.time(),'total_elapsed':time.time()-a['allocation_start_unix']})
    print(json.dumps({'reason':result['termination_reason'],'consumed':result['authorization_consumed'],'elapsed':result['allocation_elapsed']}))
