"""Prepare a private saved-batch replay; never allocate GPUs or start inference."""
import argparse
import json
from pathlib import Path
import textwrap


def batch_cell(body, working='/kaggle/working'):
    """Block until owned jobs end; archive evidence even when setup fails."""
    return ("import hashlib, json, traceback, zipfile\n"
            "from datetime import datetime, timezone\nfrom pathlib import Path\n"
            f"WORKING=Path({str(working)!r})\n"
            "workflow={'status':'started','started_utc':datetime.now(timezone.utc).isoformat()}\n"
            "try:\n" + textwrap.indent(body, '    ') + "\n"
            "    workflow['status']='controller returned; inspect allocation and frozen assessment'\n"
            "except BaseException as error:\n"
            "    workflow.update(status='failed; partial evidence retained',error_type=type(error).__name__,error=str(error))\n"
            "    traceback.print_exc()\n"
            "finally:\n"
            "    controller=globals().get('CONTROLLER')\n"
            "    if controller is not None and controller.poll() is None:\n"
            "        raise RuntimeError('Owned controller still live; do not archive live trajectories as final')\n"
            "    workflow['finished_utc']=datetime.now(timezone.utc).isoformat()\n"
            "    state_path=WORKING/'saved_batch_state.json'\n"
            "    state_path.write_text(json.dumps(workflow,indent=2)+chr(10))\n"
            "    evidence=WORKING/'UIO66_sampling_saved_batch_evidence.zip'\n"
            "    assert not evidence.exists(), 'Never overwrite evidence'\n"
            "    with zipfile.ZipFile(evidence,'w',zipfile.ZIP_DEFLATED) as archive:\n"
            "        archive.write(state_path,state_path.name)\n"
            "        for folder in (globals().get('OUT'),globals().get('PRE')):\n"
            "            if folder is not None and folder.exists():\n"
            "                for file in sorted(folder.rglob('*')):\n"
            "                    if file.is_file(): archive.write(file,str(file.relative_to(WORKING)))\n"
            "        log=globals().get('controller_log')\n"
            "        if log is not None and log.exists(): archive.write(log,log.name)\n"
            "    print('SAVED BATCH STATE:',json.dumps(workflow),flush=True)\n"
            "    print('EVIDENCE:',evidence.name,evidence.stat().st_size,hashlib.sha256(evidence.read_bytes()).hexdigest(),flush=True)\n")


def prepare(source, approved=False):
    notebook = json.loads(Path(source).read_text())
    cells = notebook['cells']
    preflight = ''.join(cells[1]['source']).replace(
        "AUTH=json.loads(release_paths[0].read_text())",
        "AUTH=json.loads(release_paths[0].read_text())\n"
        "assert AUTH.get('execution_mode')=='saved_batch' and AUTH.get('replacement_pilot_approved') is True, 'Replacement run approval and saved-batch receipt required'"
    )
    body = '\n'.join((preflight, ''.join(cells[2]['source']),
                       ''.join(cells[3]['source']),
                       "CONTROLLER.wait()\nprint('CONTROLLER TERMINAL:',CONTROLLER.returncode,flush=True)",
                       ''.join(cells[4]['source'])))
    code = batch_cell(body)
    compile(code, 'saved pilot cell', 'exec')
    notebook['cells'] = [
        {'cell_type':'markdown','metadata':{},'source':[
            '# UiO-66 replacement pilot — private saved batch\n',
            ('User explicitly approved this replacement: same512+16,2T4,max4.2h; execution receipt must confirm approval.\n'
             if approved else 'PREPARED ONLY; replacement compute is not authorized yet.\n'),
            'After explicit approval, freeze this notebook/code/512-pose manifest/checkpoint hashes\n',
            'with a saved-batch execution receipt and a reviewed two-T4 deadline.\n',
            'Use Save Version → Save & Run All; verify a numbered private version actually starts.\n',
            'This one cell waits for the controller, then archives raw results and failures.\n',
            'Download and hash-verify saved version outputs before declaring evidence secured.\n',
            'No refit, new poses, 64-design expansion or DFT.\n']},
        {'cell_type':'code','metadata':{},'source':code.splitlines(keepends=True),
         'execution_count':None,'outputs':[]}
    ]
    return notebook


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',default='kaggle/uio66_sampling_pilot_authorized.ipynb')
    parser.add_argument('--output',default='kaggle/uio66_sampling_pilot_saved_run.ipynb')
    parser.add_argument('--approved-label',action='store_true',help='Label user-approved replay; does not bypass receipt gate')
    args = parser.parse_args()
    notebook = prepare(args.source,args.approved_label)
    Path(args.output).write_text(json.dumps(notebook,indent=2)+chr(10))
    print('Prepared saved-batch notebook; no GPU allocation/inference')


if __name__=='__main__':
    main()
