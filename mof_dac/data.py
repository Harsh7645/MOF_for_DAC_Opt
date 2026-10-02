"""Load a provenance-bearing selection graph; no CoRE-to-coefficient inference."""

import json
from pathlib import Path

import numpy as np

from .formulation import Problem


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value):
        raise ValueError("Coefficients must be finite JSON numbers")
    return float(value)


def _provenance(record, units=None):
    for key in ("source", "method"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError(f"Missing provenance: {key}")
    if units is not None and record.get("units") != units:
        raise ValueError("Coefficient units must match dataset energy_units")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_instance(path):
    """Return (Problem, original JSON metadata). Node order fixes x indexing."""
    data = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    if data.get("schema_version") != 1:
        raise ValueError("Expected schema_version=1")
    if data.get("parameter_regime") not in ("synthetic", "heuristic", "dft_grounded"):
        raise ValueError("Declare parameter_regime")
    if data.get("missing_interactions") != "modeled_zero":
        raise ValueError("Declare missing_interactions=modeled_zero; unknown values are not zeros")
    units = data.get("energy_units")
    if not isinstance(units, str) or not units.strip():
        raise ValueError("Declare energy_units")
    nodes = data["nodes"]
    ids = tuple(node["id"] for node in nodes)
    if not ids or any(not isinstance(i, str) or not i.strip() for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("Node IDs must be nonempty unique strings")
    index = {key: i for i, key in enumerate(ids)}
    h = []
    for node in nodes:
        _provenance(node, units)
        if node.get("kind") not in ("metal", "linker"):
            raise ValueError("Node kind must be metal or linker")
        h.append(_number(node["h"]))
    W = np.zeros((len(ids), len(ids)))
    seen = set()
    for edge in data["edges"]:
        _provenance(edge, units)
        a, b = edge["i"], edge["j"]
        if a not in index or b not in index or a == b:
            raise ValueError("Edge needs two distinct known endpoints")
        pair = tuple(sorted((a, b)))
        if pair in seen:
            raise ValueError("Duplicate undirected edge")
        seen.add(pair)
        i, j = index[a], index[b]
        W[i, j] = W[j, i] = _number(edge["J"])
    rows = {"eq": [], "le": []}
    rhs = {"eq": [], "le": []}
    names = set()
    for constraint in data["constraints"]:
        name = constraint["id"]
        if not isinstance(name, str) or not name or name in names:
            raise ValueError("Constraint IDs must be nonempty and unique")
        names.add(name)
        _provenance(constraint)
        sense = constraint["sense"]
        if sense not in rows:
            raise ValueError("Constraint sense must be eq or le")
        row = np.zeros(len(ids))
        for key, value in constraint["coefficients"].items():
            if key not in index:
                raise ValueError(f"Unknown constraint variable: {key}")
            row[index[key]] = _number(value)
        rows[sense].append(row)
        rhs[sense].append(_number(constraint["rhs"]))
    problem = Problem(ids, np.array(h), W,
                      np.array(rows["eq"]).reshape(-1, len(ids)), np.array(rhs["eq"]),
                      np.array(rows["le"]).reshape(-1, len(ids)), np.array(rhs["le"]))
    return problem, data
