"""Freeze duplicate-group design split without reading adsorption labels."""

import argparse
import hashlib
import json
from pathlib import Path

from mof_dac.design_fit import freeze_split


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', default='artifacts/phase3/uio66_structures/manifest.json')
    parser.add_argument('--groups', nargs='+', default=['artifacts/phase3/uio66_groups.json',
        'artifacts/phase3/uio66_relaxed_groups.json'])
    parser.add_argument('--output', default='data/design/uio66_fit_split.json')
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise ValueError('Split already frozen; use a separate protocol path')
    manifest = json.loads(Path(args.manifest).read_text())
    states = {r['id']: r['state'] for r in manifest['configurations']}
    groups = []
    for path in map(Path, args.groups):
        candidates = [a for a in json.loads(path.read_text())['audits'] if a['tolerance_angstrom'] == 0.05]
        if len(candidates) != 1:
            raise ValueError('Expected one 0.05-Angstrom duplicate audit')
        groups.append(candidates[0]['groups'])
    split = freeze_split(states, groups)
    split['source_sha256'] = {str(p): hashlib.sha256(Path(p).read_bytes()).hexdigest()
        for p in [args.manifest, *args.groups]}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(split, indent=2) + '\n')
    print(f"Frozen split: {len(split['groups'])} groups, {len(split['train_ids'])} train, "
          f"{len(split['test_ids'])} test, rank {split['training_design_rank']}")


if __name__ == '__main__':
    main()
