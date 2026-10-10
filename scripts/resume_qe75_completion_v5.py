"""Resume only the prelaunch AC gate, retaining the original allocation."""
import json,time
from pathlib import Path
from qe75_fedora_v1 import ROOT,sha
from qe75_completion_v5 import dump
import launch_qe75_rho625_v1 as tested

if __name__=='__main__':
    config=ROOT/'configs/qe75-fedora-completion-v5.json'
    c=json.loads(config.read_text());ev=Path(c['evidence_root'])
    with (ev/'launcher-entered.json').open('x') as f:json.dump({'time':time.time(),'script_sha256':sha(Path(__file__))},f)
    a=json.loads(Path(c['allocation_file']).read_text())
    tested.SCRIPT=ROOT/'scripts/qe75_completion_v5.py'
    r=tested.run_guard(c,config)
    dump(ev/'launcher-final.json',{'result':r,'time':time.time(),'total_elapsed':time.time()-a['allocation_start_unix']})
    print(json.dumps({'reason':r['termination_reason'],'consumed':r['authorization_consumed'],'elapsed':r['allocation_elapsed']}))
