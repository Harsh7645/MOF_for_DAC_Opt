"""Lightweight staging only; new home directory, checksums and safe extraction."""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path


def stage(root, mode):
    root=root.absolute()
    if root.parent!=Path.home().resolve() or not root.name.startswith('mof_dac_qe75_v2_'):
        raise ValueError('Only a new direct child of the authenticated home is allowed')
    if root.is_symlink():raise ValueError('Symlink project root rejected')
    ledger=root/'remote_directory_ledger.json'
    if mode=='create':
        root.mkdir()  # Existing directory rejected; no overwrite or parent creation.
        result={'project_root':str(root),'scratch_root':None,'created':[]}
    else:
        result=json.loads(ledger.read_text())
    try:
        if mode=='verify':
            overlay=root/'cse_v1'
            metadata=json.loads((overlay/'overlay_manifest.json').read_text())
            for name,digest in metadata['files'].items():
                path=overlay/name
                if not path.resolve().is_relative_to(overlay.resolve()):raise ValueError('Unsafe overlay path')
                if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Overlay hash mismatch: '+name)
            spec=importlib.util.spec_from_file_location('verified_extractor',overlay/'verify_extract.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            verification=module.extract(root/'UIO66_Frozen_DFT_QE75_v2.zip',root/'uio66_frozen_dft_v2_qe75_receipt.json',root/'package')
            (root/'package_verification.json').write_text(json.dumps(verification,indent=2)+'\n')
            result['verification']=verification
            result['verified_overlay_files']=len(metadata['files'])
    finally:
        previous={item['path']:item for item in result['created']}
        stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        for path in [root]+sorted(p for p in root.rglob('*') if p.is_dir()):
            previous.setdefault(str(path),{'path':str(path),'recorded_utc':stamp,
                'purpose':'frozen pilot input/evidence staging; no compute scratch',
                'storage_class':'NFS home; backup, quota and retention policy unverified'})
        result['created']=list(previous.values())
        result['jobs_submitted']=[]
        result['cleanup']='No deletion authorized; preserve partial and failed transfers.'
        ledger.write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['create','verify'])
    parser.add_argument('root',type=Path)
    args=parser.parse_args()
    print(json.dumps(stage(args.root,args.mode),indent=2))
