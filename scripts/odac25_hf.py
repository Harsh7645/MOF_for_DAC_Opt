"""Guarded ODAC25 Hugging Face inventory, download, inspection and UMA smoke test."""

import argparse
import fnmatch
import json
import os
from pathlib import Path


REPO_ID = "facebook/ODAC25"


def _token():
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("Set HF_TOKEN as a secret environment variable; never put it in code")
    return token


def inventory(output):
    from huggingface_hub import HfApi, hf_hub_download

    info = HfApi().model_info(REPO_ID, files_metadata=True, token=_token())
    files = []
    for item in info.siblings:
        lfs = getattr(item, "lfs", None)
        checksum = lfs.get("sha256") if isinstance(lfs, dict) else getattr(lfs, "sha256", None)
        files.append({"path": item.rfilename, "size_bytes": item.size, "sha256": checksum})
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"repo_id": REPO_ID, "revision": info.sha,
                                  "files": files}, indent=2) + "\n", encoding="utf-8")
    hf_hub_download(REPO_ID, "DATASET.md", token=_token(), local_dir=output.parent)
    return files


def download(inventory_path, patterns, output, max_gb):
    from huggingface_hub import snapshot_download

    data = json.loads(Path(inventory_path).read_text(encoding="utf-8"))
    selected = [row for row in data["files"]
                if any(fnmatch.fnmatch(row["path"], pattern) for pattern in patterns)]
    if not selected:
        raise ValueError("No repository files match the requested patterns")
    if any(row["size_bytes"] is None for row in selected):
        raise ValueError("Cannot enforce download cap because file sizes are missing")
    total = sum(row["size_bytes"] for row in selected)
    if total > max_gb * 1024 ** 3:
        raise ValueError(f"Selected {total / 1024**3:.2f} GiB exceeds --max-gb {max_gb}")
    snapshot_download(REPO_ID, revision=data["revision"], token=_token(),
                      allow_patterns=patterns, local_dir=output)
    return selected


def inspect_dataset(source, output, samples):
    from fairchem.core.datasets import AseDBDataset

    dataset = AseDBDataset({"src": str(source)})
    records = []
    for index in range(min(samples, len(dataset))):
        atoms = dataset.get_atoms(index)
        records.append({"index": index, "atoms": len(atoms),
                        "formula": atoms.get_chemical_formula(),
                        "pbc": atoms.pbc.tolist(),
                        "info_schema": {key: type(value).__name__
                                        for key, value in sorted(atoms.info.items())},
                        "calculator_result_keys": sorted(atoms.calc.results) if atoms.calc else []})
    payload = {"source": str(source), "dataset_length": len(dataset), "samples": records}
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def uma_smoke(source, output, samples, device):
    from fairchem.core import FAIRChemCalculator, pretrained_mlip
    from fairchem.core.datasets import AseDBDataset

    dataset = AseDBDataset({"src": str(source)})
    predictor = pretrained_mlip.get_predict_unit("uma-s-1p2p1", device=device)
    calculator = FAIRChemCalculator(predictor, task_name="odac")
    rows = []
    for index in range(min(samples, len(dataset))):
        atoms = dataset.get_atoms(index)
        reference = float(atoms.get_potential_energy())
        candidate = atoms.copy()
        candidate.calc = calculator
        prediction = float(candidate.get_potential_energy())
        rows.append({"index": index, "reference_total_energy_ev": reference,
                     "uma_total_energy_ev": prediction,
                     "absolute_error_ev": abs(prediction - reference)})
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps({"model": "uma-s-1p2p1", "task": "odac",
                                       "device": device, "rows": rows}, indent=2) + "\n",
                            encoding="utf-8")
    return rows


def profile_targets(source, output, split, limit):
    from fairchem.core.datasets import AseDBDataset
    from mof_dac.odac25 import profile_adsorbate_rows

    dataset = AseDBDataset({"src": str(source)})
    count = len(dataset) if not limit else min(limit, len(dataset))
    profile = profile_adsorbate_rows(dataset.get_atoms(index).info
                                    for index in range(count))
    payload = {"source": str(source), "split": split,
               "dataset_length": len(dataset), "profile": profile}
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return profile


def materialize_targets(source, output, split, limit):
    from fairchem.core.datasets import AseDBDataset
    from mof_dac.odac25 import pair_adsorbate_rows, select_relaxed_adsorbate_targets

    dataset = AseDBDataset({"src": str(source)})
    count = len(dataset) if not limit else min(limit, len(dataset))
    targets = select_relaxed_adsorbate_targets(
        (dataset.get_atoms(index).info for index in range(count)), split=split)
    pairs = pair_adsorbate_rows(targets)
    payload = {
        "source": str(source), "split": split, "dataset_length": len(dataset),
        "rows_scanned": count,
        "selection_rule": "max fid per trajectory, then minimum final-frame energy_ads_corrected per MOF/gas; exact one-molecule CO2/H2O records only",
        "single_gas_targets": targets, "paired_targets": pairs,
    }
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inv = commands.add_parser("inventory")
    inv.add_argument("--output", default="artifacts/odac25/inventory.json")
    get = commands.add_parser("download")
    get.add_argument("--inventory", default="artifacts/odac25/inventory.json")
    get.add_argument("--allow", action="append", required=True)
    get.add_argument("--output", default="data/raw/odac25")
    get.add_argument("--max-gb", type=float, default=20)
    show = commands.add_parser("inspect")
    show.add_argument("source")
    show.add_argument("--output", default="artifacts/odac25/schema.json")
    show.add_argument("--samples", type=int, default=8)
    smoke = commands.add_parser("uma-smoke")
    smoke.add_argument("source")
    smoke.add_argument("--output", default="artifacts/odac25/uma_smoke.json")
    smoke.add_argument("--samples", type=int, default=16)
    smoke.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    profile = commands.add_parser("profile-targets")
    profile.add_argument("source")
    profile.add_argument("--output", default="artifacts/odac25/target_profile.json")
    profile.add_argument("--split", required=True)
    profile.add_argument("--limit", type=int, default=0)
    materialize = commands.add_parser("materialize-targets")
    materialize.add_argument("source")
    materialize.add_argument("--output", default="artifacts/odac25/paired_targets.json")
    materialize.add_argument("--split", required=True)
    materialize.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    if args.command == "inventory":
        rows = inventory(args.output)
    elif args.command == "download":
        rows = download(args.inventory, args.allow, args.output, args.max_gb)
    elif args.command == "inspect":
        rows = inspect_dataset(args.source, args.output, args.samples)["samples"]
    elif args.command == "uma-smoke":
        rows = uma_smoke(args.source, args.output, args.samples, args.device)
    elif args.command == "profile-targets":
        rows = profile_targets(args.source, args.output, args.split, args.limit)
    else:
        rows = materialize_targets(args.source, args.output, args.split, args.limit)
    count = (rows["records"] if args.command == "profile-targets" else
             len(rows["paired_targets"]) if args.command == "materialize-targets" else len(rows))
    print(f"{args.command}: {count} records")


if __name__ == "__main__":
    main()
