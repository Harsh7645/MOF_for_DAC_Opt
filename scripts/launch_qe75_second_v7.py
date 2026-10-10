"""Launch the single authorized second geometry with original immutable allocation."""
import json,time
from pathlib import Path
from qe75_fedora_v1 import ROOT,sha
from qe75_second_v7 import dump
import launch_qe75_rho625_v1 as tested
E=ROOT/'evidence/qe75-second-v7';C=ROOT/'configs/qe75-second-v7.json'
if __name__=='__main__':
 with (E/'launcher-entered.json').open('x') as f:json.dump({'time':time.time(),'script_sha256':sha(Path(__file__))},f)
 c=json.loads(C.read_text());tested.SCRIPT=ROOT/'scripts/qe75_second_v7.py'
 result=tested.run_guard(c,C)
 dump(E/'launcher-final.json',{'result':result,'time':time.time()})
 print(json.dumps(result))
