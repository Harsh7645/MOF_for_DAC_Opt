"""Enumerate the provisional library without fabricating structures or scores."""

import argparse
import json
from pathlib import Path

from mof_dac.uio66 import enumerate_design


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', default='data/design/uio66_provisional.json')
    parser.add_argument('--output', default='artifacts/phase3/uio66_provisional_design.json')
    args = parser.parse_args()
    result = enumerate_design(json.loads(Path(args.library).read_text(encoding='utf-8')))
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(f'{len(result["configurations"])} nominal configurations; no structures or scores: {path}')


if __name__ == '__main__':
    main()
