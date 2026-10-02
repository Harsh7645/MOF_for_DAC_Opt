"""Fit training-only paired composition baselines and evaluate frozen validation."""

import argparse
import hashlib
import json
from pathlib import Path

from mof_dac.material_baselines import evaluate_composition_baselines


def _load(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload.get("paired_targets", payload)
    if not isinstance(rows, list):
        raise ValueError(f"{path} must contain a list or paired_targets list")
    return rows


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True)
    parser.add_argument("--validation", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()
    result = evaluate_composition_baselines(_load(args.train), _load(args.validation),
                                            top_k=args.top_k)
    result["inputs"] = {"train": str(args.train), "train_sha256": _sha256(args.train),
                        "validation": str(args.validation),
                        "validation_sha256": _sha256(args.validation)}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"wrote {output}: {result['validation_samples']} validation MOFs")


if __name__ == "__main__":
    main()
