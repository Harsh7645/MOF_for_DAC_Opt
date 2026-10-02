"""Strict manifest validation for external material-ranking data."""

import csv
import json
from pathlib import Path

import numpy as np


REQUIRED_COLUMNS = ("structure_id", "cif_path", "target", "target_units", "split",
                    "source", "license", "conditions_json")
VALID_SPLITS = {"train", "validation", "test"}


def load_material_manifest(path, *, require_files=True):
    """Load a provenance-bearing label manifest without inferring chemistry."""
    path = Path(path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or any(name not in reader.fieldnames for name in REQUIRED_COLUMNS):
            raise ValueError(f"Manifest requires columns: {', '.join(REQUIRED_COLUMNS)}")
        rows = list(reader)
    if not rows:
        raise ValueError("Material manifest is empty")
    seen = set()
    for number, row in enumerate(rows, start=2):
        identifier = row["structure_id"].strip()
        if not identifier or identifier in seen:
            raise ValueError(f"Missing or duplicate structure_id at row {number}")
        seen.add(identifier)
        if row["split"] not in VALID_SPLITS:
            raise ValueError(f"Invalid split at row {number}")
        target = float(row["target"])
        if not np.isfinite(target):
            raise ValueError(f"Nonfinite target at row {number}")
        if not all(row[name].strip() for name in ("target_units", "source", "license")):
            raise ValueError(f"Missing provenance at row {number}")
        conditions = json.loads(row["conditions_json"])
        if not isinstance(conditions, dict) or not conditions:
            raise ValueError(f"Missing target conditions at row {number}")
        cif = (path.parent / row["cif_path"]).resolve()
        if require_files and not cif.is_file():
            raise ValueError(f"Missing CIF at row {number}: {cif}")
        row["target"] = target
        row["conditions"] = conditions
        row["resolved_cif_path"] = str(cif)
    if not {row["split"] for row in rows}.issubset(VALID_SPLITS):
        raise ValueError("Unexpected split")
    return rows
