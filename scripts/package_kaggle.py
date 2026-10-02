"""Package explicit code paths; exclude credentials, weights and raw databases."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='artifacts/kaggle/MOF_DAC_Kaggle_bundle.zip')
    parser.add_argument('--frozen-targets', help='Optional audited paired_targets.json input')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    paths = [root / 'pyproject.toml', root / 'docs/ODAC25_TARGET_CONTRACT.md',
             root / 'docs/PHASE3_REFERENCE_AUDIT.md',
             root / 'docs/UIO66_PROVISIONAL_LIBRARY.md',
             root / 'data/design/uio66_provisional.json']
    for directory, patterns in [('mof_dac', ['*.py']), ('scripts', ['*.py']),
                                 ('kaggle', ['*.py', '*.ipynb'])]:
        for pattern in patterns:
            paths.extend((root / directory).glob(pattern))
    hashes = {}
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(paths)):
            name = path.relative_to(root).as_posix()
            archive.write(path, name)
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        if args.frozen_targets:
            path = Path(args.frozen_targets)
            name = 'kaggle/frozen_targets_v1.json'
            archive.write(path, name)
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        archive.writestr('bundle_manifest.json', json.dumps({'sha256': hashes}, indent=2) + '\n')
    print(f'Bundle: {output} ({output.stat().st_size} bytes, {len(hashes)} files)')


if __name__ == '__main__':
    main()
