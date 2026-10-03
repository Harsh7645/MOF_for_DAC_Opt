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
    parser.add_argument('--uio66-structures', help='Optional hashed provisional structure directory')
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
        if args.uio66_structures:
            directory = Path(args.uio66_structures).resolve()
            manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
            extras = [directory / 'manifest.json', directory / 'atom_mapping.json']
            for row in manifest['configurations']:
                path = (directory / row['structure_file']).resolve()
                if not path.is_relative_to(directory) or path.suffix != '.cif':
                    raise ValueError('Invalid structure manifest path')
                if hashlib.sha256(path.read_bytes()).hexdigest() != row['structure_sha256']:
                    raise ValueError(f'Structure hash changed: {row["id"]}')
                extras.append(path)
            for path in extras:
                name = 'uio66_structures/' + path.relative_to(directory).as_posix()
                archive.write(path, name)
                hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        archive.writestr('bundle_manifest.json', json.dumps({'sha256': hashes}, indent=2) + '\n')
    print(f'Bundle: {output} ({output.stat().st_size} bytes, {len(hashes)} files)')


if __name__ == '__main__':
    main()
