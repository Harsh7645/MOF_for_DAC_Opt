"""Build review-only initial geometries from a provenance-bearing ODAC25 parent."""

import argparse
import hashlib
import json
from pathlib import Path

from mof_dac.uio66 import enumerate_design
from mof_dac.uio66_structures import map_linkers, substitute_amino


def main():
    from ase import Atoms
    from ase.io import write

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent', required=True, help='Exported provenance and ordered coordinates JSON')
    parser.add_argument('--library', default='data/design/uio66_provisional.json')
    parser.add_argument('--output', default='artifacts/phase3/uio66_structures')
    args = parser.parse_args()
    payload = json.loads(Path(args.parent).read_text(encoding='utf-8'))
    if not payload.get('source_sha256') or payload.get('source_index') is None:
        raise ValueError('Parent dataset provenance required')
    parent = Atoms(numbers=payload['numbers'], positions=payload['positions_angstrom'],
                   cell=payload['cell_angstrom'], pbc=payload['pbc'])
    mapping = map_linkers(parent)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    mapping['parent_json_sha256'] = hashlib.sha256(Path(args.parent).read_bytes()).hexdigest()
    (output / 'atom_mapping.json').write_text(json.dumps(mapping, indent=2) + '\n', encoding='utf-8')
    design = enumerate_design(json.loads(Path(args.library).read_text(encoding='utf-8')))
    for row in design['configurations']:
        atoms = substitute_amino(parent, mapping, row['state'])
        path = output / (row['id'] + '.cif')
        write(path, atoms)
        row.update(structure_file=path.name, structure_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                   structure_status='unrelaxed initial guess; chemical validity unverified')
    design.update(parent_provenance=payload, atom_mapping_file='atom_mapping.json',
        geometry_policy='fixed parent; planar amino initialization; no relaxation, symmetry deduplication or labels')
    (output / 'manifest.json').write_text(json.dumps(design, indent=2) + '\n', encoding='utf-8')
    print(f"Saved {len(design['configurations'])} unrelaxed proposals to {output}; no physical scores")


if __name__ == '__main__':
    main()
