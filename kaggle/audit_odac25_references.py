"""Audit ODAC25 energy-field identities; never fit gas energies to validation labels."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


def reference_audit(dataset, samples=2048):
    """Compare declared field combinations on uniformly spaced stored records."""
    values, examples = defaultdict(list), []
    for index in np.unique(np.linspace(0, len(dataset) - 1, min(samples, len(dataset)), dtype=int)):
        atoms = dataset.get_atoms(int(index))
        info = atoms.info
        counts = tuple(int(info[key]) for key in ('nco2', 'nh2o', 'nn2', 'no2'))
        gas = 'co2' if counts == (1, 0, 0, 0) else 'h2o' if counts == (0, 1, 0, 0) else None
        if gas is None or int(info['nads']) != 1:
            continue
        for system, bare, adsorption in (
            ('energy', 'energy_mof', 'energy_ads_corrected'),
            ('energy_old', 'energy_mof', 'energy_ads_corrected'),
            ('energy', 'energy_mof_old', 'energy_ads'),
            ('energy_old', 'energy_mof_old', 'energy_ads'),
        ):
            fields = [info.get(key) for key in (system, bare, adsorption)]
            if any(value is None for value in fields):
                continue
            reference = float(fields[0]) - float(fields[1]) - float(fields[2])
            values[f'{gas}:{system}-{bare}-{adsorption}'].append(reference)
        if len(examples) < 12:
            examples.append({'index': int(index), 'atoms': len(atoms),
                             'metadata': {key: info.get(key) for key in (
                                 'mof_name', 'name', 'fid', 'supercell', 'energy', 'energy_old',
                                 'energy_mof', 'energy_mof_old', 'energy_ads_corrected', 'energy_ads')},
                             'calculator_energy_ev': float(atoms.get_potential_energy())})
    statistics = {}
    for key, entries in values.items():
        array = np.asarray(entries)
        if not np.isfinite(array).all():
            raise ValueError(f'Nonfinite reference: {key}')
        statistics[key] = {'count': len(entries), 'minimum_ev': float(array.min()),
                           'maximum_ev': float(array.max()), 'spread_ev': float(np.ptp(array)),
                           'median_ev': float(np.median(array))}
    return {'dataset_rows': len(dataset), 'requested_samples': samples,
            'statistics': statistics, 'examples': examples,
            'status': 'diagnostic_only; no gas reference approved'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--output', required=True)
    parser.add_argument('--samples', type=int, default=2048)
    args = parser.parse_args()
    if args.samples < 1:
        parser.error('--samples must be positive')
    from fairchem.core.datasets import AseDBDataset
    result = reference_audit(AseDBDataset({'src': args.source}), args.samples)
    Path(args.output).write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
