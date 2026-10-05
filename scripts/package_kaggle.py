"""Package explicit code paths; exclude credentials, weights and raw databases."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from mof_dac.sampling import frozen_input_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='artifacts/kaggle/MOF_DAC_Kaggle_bundle.zip')
    parser.add_argument('--frozen-targets', help='Optional audited paired_targets.json input')
    parser.add_argument('--uio66-structures', help='Optional hashed provisional structure directory')
    parser.add_argument('--uio66-bare-results', help='Audited directory with gpu*/relaxation.json and hashed CIFs')
    parser.add_argument('--sampling-pilot', action='store_true', help='Include frozen v2 plan and only its eight hashed bare CIFs')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    paths = [root / 'pyproject.toml', root / 'docs/ODAC25_TARGET_CONTRACT.md',
             root / 'docs/PHASE3_REFERENCE_AUDIT.md',
             root / 'docs/UIO66_PROVISIONAL_LIBRARY.md',
             root / 'docs/UIO66_ADSORPTION_PROTOCOL.md',
             root / 'data/design/uio66_provisional.json']
    if args.sampling_pilot:
        plan_path = root/'data/design/uio66_sampling_pilot_v2.json'
        plan = json.loads(plan_path.read_text())
        split = root/'data/design/uio66_fit_split.json'
        if len(plan['configurations'])!=8 or hashlib.sha256(split.read_bytes()).hexdigest()!=plan['historical_split_sha256']:
            raise ValueError('Wrong pilot pool or changed historical split')
        paths.extend([plan_path,split,root/'docs/UIO66_SAMPLING_PILOT_V2.md',root/'docs/UIO66_CHEMISTRY_REVIEW.md'])
        recovery = root/'docs/UIO66_PILOT_RECOVERY.md'
        if recovery.exists():
            paths.append(recovery)
        for row in plan['configurations']:
            path = frozen_input_path(root, row['bare_input'])
            if not path.is_relative_to(root) or path.suffix!='.cif' or hashlib.sha256(path.read_bytes()).hexdigest()!=row['bare_input_sha256']:
                raise ValueError('Pilot input changed')
            paths.append(path)
    for name in ('docs/uio66_design_results.json', 'data/design/uio66_uma_train_fit_v1.json'):
        if (root / name).exists():
            paths.append(root / name)
    if args.uio66_bare_results:
        split_path = root / 'data/design/uio66_fit_split.json'
        paths.append(split_path)
        for name, digest in json.loads(split_path.read_text())['source_sha256'].items():
            path = (root / name).resolve()
            if not path.is_relative_to(root) or path.suffix != '.json' \
                    or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError('Frozen fit split source changed')
            paths.append(path)
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
        if args.uio66_bare_results:
            from mof_dac.adsorption import intact
            directory = Path(args.uio66_bare_results).resolve()
            reports = sorted(directory.glob('gpu*/relaxation.json'))
            identifiers = set()
            extras = list(reports)
            for report in reports:
                for row in json.loads(report.read_text())['results']:
                    path = (report.parent / 'structures' / row['final_structure_file']).resolve()
                    if not path.is_relative_to(directory) or path.suffix != '.cif' or not intact(row) \
                            or row['id'] in identifiers \
                            or hashlib.sha256(path.read_bytes()).hexdigest() != row['final_structure_sha256']:
                        raise ValueError('Invalid, duplicated or changed bare input')
                    identifiers.add(row['id'])
                    extras.append(path)
            if len(identifiers) != 64:
                raise ValueError('Expected all 64 accepted bare structures')
            for path in extras:
                name = 'uio66_bare/' + path.relative_to(directory).as_posix()
                archive.write(path, name)
                hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        archive.writestr('bundle_manifest.json', json.dumps({'sha256': hashes}, indent=2) + '\n')
    print(f'Bundle: {output} ({output.stat().st_size} bytes, {len(hashes)} files)')


if __name__ == '__main__':
    main()
