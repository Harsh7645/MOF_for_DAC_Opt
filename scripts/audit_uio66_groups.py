"""Audit generated fixed-cell proposals across frozen geometry tolerances."""

import argparse
import hashlib
import json
from pathlib import Path

from mof_dac.structure_groups import parent_operation_groups


def main():
    from ase import Atoms
    from ase.io import read

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--structures', default='artifacts/phase3/uio66_structures')
    parser.add_argument('--output', default='artifacts/phase3/uio66_groups.json')
    parser.add_argument('--tolerances', nargs='+', type=float, default=[1e-5, 0.01, 0.05])
    parser.add_argument('--relaxation-reports', nargs='+', help='Use hashed final CIFs from completed runs')
    args = parser.parse_args()
    directory = Path(args.structures)
    manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    payload = manifest['parent_provenance']
    parent = Atoms(numbers=payload['numbers'], positions=payload['positions_angstrom'],
                   cell=payload['cell_angstrom'], pbc=payload['pbc'])
    structures, fingerprints, reports = {}, {}, {}
    relaxed = {}
    for report_path in map(Path, args.relaxation_reports or []):
        run = json.loads(report_path.read_text())
        if run['manifest_sha256'] != hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest():
            raise ValueError('Relaxation manifest changed')
        reports[str(report_path)] = hashlib.sha256(report_path.read_bytes()).hexdigest()
        for row in run['results']:
            if row['id'] in relaxed or row['status'] != 'converged':
                raise ValueError('Duplicate or unconverged relaxation identity')
            relaxed[row['id']] = (report_path.parent / 'structures' / row['final_structure_file'],
                                  row['final_structure_sha256'])
    if reports and set(relaxed) != {row['id'] for row in manifest['configurations']}:
        raise ValueError('Relaxation pool does not match all manifest identities')
    for row in manifest['configurations']:
        path = directory / row['structure_file']
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row['structure_sha256']:
            raise ValueError(f'Structure changed: {path}')
        if reports:
            path, expected_digest = relaxed[row['id']]
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != expected_digest:
                raise ValueError(f'Relaxed structure changed: {path}')
        structures[row['id']] = read(path)
        fingerprints[row['id']] = digest
    audits = []
    for tolerance in args.tolerances:
        audit = parent_operation_groups(parent, structures, tolerance)
        audits.append(audit)
        print(f"tolerance={tolerance}: {audit['group_count']} groups, "
              f"{audit['verified_parent_operations']} parent operations", flush=True)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({'protocol': 'declared parent-operation near-duplicate audit',
        'geometry_stage': 'relaxed' if reports else 'initial',
        'relaxation_report_sha256': reports,
        'structure_sha256': fingerprints, 'audits': audits}, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
