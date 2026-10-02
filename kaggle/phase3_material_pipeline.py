"""Kaggle-side ODAC25 paired material benchmark; requires fairchem and pyarrow."""

import argparse
import hashlib
import json
import re
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

from mof_dac.material_baselines import evaluate_composition_baselines
from mof_dac.odac25 import evaluate_prediction_rows


NAME = re.compile(r"__(mof_plus_adsorbate|mof)__(.+)$")
SINGLE = re.compile(r"^(.+)_w_(CO2|H2O)_\d+$")
GAS_ATOMS = {"co2": (6, 8, 8), "h2o": (1, 1, 8)}


def input_digests(paths):
    """Bind cached component indices to the exact dataset bytes."""
    result = {}
    for name, path in paths.items():
        digest = hashlib.sha256()
        with Path(path).open("rb") as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                digest.update(block)
        result[name] = digest.hexdigest()
    return result


def validate_gas_references(statistics):
    """Reject variable field offsets instead of treating their median as a constant."""
    if set(statistics) != {"co2", "h2o"} or any(
            not np.isfinite(value["max_absolute_deviation_from_median"]) or
            value["max_absolute_deviation_from_median"] > 1e-5 for value in statistics.values()):
        raise ValueError("Inconsistent gas reference fields; run audit_odac25_references.py before MLIP scoring")


def _signature(numbers, gas=None):
    counts = np.bincount(np.asarray(numbers, dtype=int), minlength=119)
    if gas:
        for number in GAS_ATOMS[gas]:
            counts[number] -= 1
    if np.any(counts < 0):
        raise ValueError(f"Invalid {gas} composition")
    return tuple(np.flatnonzero(counts).tolist() + [-1] + counts[counts > 0].tolist())


def _signature_atom_count(signature):
    return sum(signature[signature.index(-1) + 1:])


def _identity(name):
    match = NAME.search(name)
    if not match:
        return None
    trajectory = match.group(2)
    single = SINGLE.match(trajectory)
    mof_id = trajectory.split("_w_", 1)[0]
    return match.group(1), trajectory, mof_id, (single.group(2).lower() if single else None)


def validation_records(target_source, bare_source, frozen_targets=None, bare_cache_path=None,
                       bare_digest=None):
    """Create frozen validation rows and component indices from ASE-LMDB."""
    from fairchem.core.datasets import AseDBDataset

    target_db, bare_db = AseDBDataset({"src": str(target_source)}), AseDBDataset({"src": str(bare_source)})
    final, gas_values = {}, defaultdict(list)
    frozen = None
    if frozen_targets:
        payload = json.loads(Path(frozen_targets).read_text(encoding="utf-8"))
        if payload["dataset_length"] != len(target_db):
            raise ValueError("Frozen target dataset length changed")
        frozen = {row["source_index"]: row for row in payload["single_gas_targets"]}
        if len(frozen) != len(payload["single_gas_targets"]):
            raise ValueError("Duplicate frozen source index")
    for index in sorted(frozen) if frozen is not None else range(len(target_db)):
        atoms = target_db.get_atoms(index)
        info = atoms.info
        counts = tuple(int(info[key]) for key in ("nco2", "nh2o", "nn2", "no2"))
        gas = "co2" if counts == (1, 0, 0, 0) else ("h2o" if counts == (0, 1, 0, 0) else None)
        if gas is None or int(info["nads"]) != 1:
            if frozen is not None:
                raise ValueError(f"Frozen adsorbate counts changed at source index {index}")
            continue
        reference = float(info["energy_old"] - info["energy_mof"] - info["energy_ads_corrected"])
        gas_values[gas].append(reference)
        candidate = {"mof_id": str(info["mof_name"]), "split": "val", "adsorbate": gas,
                     "adsorption_energy_ev": float(info["energy_ads_corrected"]),
                     "system_kpoint_correction_ev": float(info["energy"] - info["energy_old"]),
                     "reference_bare_energy_ev": float(info["energy_mof"]),
                     "trajectory": str(info["name"]), "fid": int(info["fid"]),
                     "target_index": index, "bare_signature": _signature(atoms.numbers, gas)}
        if frozen is not None:
            expected = frozen[index]
            if (candidate["mof_id"], gas, candidate["trajectory"], candidate["fid"]) != (
                    expected["mof_id"], expected["adsorbate"], expected["selected_trajectory"],
                    expected["selected_fid"]) or not np.isclose(
                        candidate["adsorption_energy_ev"], expected["adsorption_energy_ev"],
                        rtol=0, atol=1e-10):
                raise ValueError(f"Frozen target changed at source index {index}")
        prior = final.get(candidate["trajectory"])
        if prior is None or candidate["fid"] > prior["fid"]:
            final[candidate["trajectory"]] = candidate
    best = {}
    for row in final.values():
        key = row["mof_id"], row["adsorbate"]
        if key not in best or (row["adsorption_energy_ev"], row["trajectory"]) < (
                best[key]["adsorption_energy_ev"], best[key]["trajectory"]):
            best[key] = row

    minima = {}
    selection_rule = "max fid per bare trajectory; minimum final-frame energy per composition"
    cache = None
    if bare_cache_path and Path(bare_cache_path).is_file():
        cache = json.loads(Path(bare_cache_path).read_text(encoding="utf-8"))
        if cache["sha256"] != bare_digest or cache["rows"] != len(bare_db):
            raise ValueError("Bare cache dataset changed")
    if cache and cache.get("selection_rule") == selection_rule:
        minima = {(row["mof_id"], tuple(row["signature"])): row["minima"] for row in cache["groups"]}
    else:
        final_bare = {}
        for index in range(len(bare_db)):
            atoms = bare_db.get_atoms(index)
            info = atoms.info
            key = str(info["mof_name"]), _signature(atoms.numbers)
            trajectory = key, str(info["name"])
            candidate = {"bare_index": index, "fid": int(info["fid"]),
                         "bare_atomic_numbers": atoms.numbers.tolist(),
                         "energy": float(info["energy"]), "energy_old": float(info["energy_old"])}
            if trajectory not in final_bare or candidate["fid"] > final_bare[trajectory]["fid"]:
                final_bare[trajectory] = candidate
        for (key, trajectory), candidate in final_bare.items():
            group = minima.setdefault(key, {})
            for field in ("energy", "energy_old"):
                energy = candidate[field]
                if field not in group or energy < group[field]["energy_ev"]:
                    group[field] = {"bare_index": candidate["bare_index"], "energy_ev": energy,
                        "bare_trajectory": trajectory, "bare_fid": candidate["fid"],
                        "bare_reference_field": field,
                        "bare_kpoint_correction_ev": float(candidate["energy"] - energy),
                        "bare_atomic_numbers": candidate["bare_atomic_numbers"]}
        if bare_cache_path:
            Path(bare_cache_path).write_text(json.dumps({"sha256": bare_digest, "rows": len(bare_db),
                "selection_rule": selection_rule,
                "groups": [{"mof_id": mof, "signature": signature, "minima": value}
                           for (mof, signature), value in minima.items()]}, allow_nan=False), encoding="utf-8")
    bare, mismatches = {}, []
    for (mof, gas), row in best.items():
        key = mof, row["bare_signature"]
        if key not in minima:
            continue
        matches = [candidate for candidate in minima[key].values() if np.isclose(
            candidate["energy_ev"], row["reference_bare_energy_ev"], rtol=0, atol=1e-5)]
        if not matches:
            mismatches.append({"mof_id": mof, "gas": gas, "expected_ev": row["reference_bare_energy_ev"],
                "minima_ev": {field: value["energy_ev"] for field, value in minima[key].items()}})
        else:
            bare[key] = matches[0]
    if mismatches:
        diagnostic = {"status": "bare reference mismatch; no scores", "mismatches": mismatches}
        if bare_cache_path:
            Path(bare_cache_path).with_suffix(".mismatches.json").write_text(
                json.dumps(diagnostic, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps(diagnostic, indent=2), flush=True)
        raise ValueError("No original/corrected bare minimum matches frozen references; diagnostic saved")
    gas_ids = ({mof for mof, gas in best if gas == "co2"} &
               {mof for mof, gas in best if gas == "h2o"})
    paired_ids = sorted(mof for mof in gas_ids if all(
        (mof, best[(mof, gas)]["bare_signature"]) in bare for gas in ("co2", "h2o")))
    single_rows = [{**best[(mof, gas)],
                    **bare[(mof, best[(mof, gas)]["bare_signature"])]}
                   for mof in paired_ids for gas in ("co2", "h2o")]
    for row in single_rows:
        if not np.isclose(row["energy_ev"], row["reference_bare_energy_ev"], rtol=0, atol=1e-5):
            raise ValueError(f"Bare reference mismatch: {row['mof_id']} {row['adsorbate']}")
    if frozen is not None:
        expected_pairs = {row["mof_id"] for row in payload["paired_targets"]}
        if set(paired_ids) != expected_pairs:
            raise ValueError("Frozen paired material pool changed")
    paired_rows = [{"mof_id": mof, "split": "val",
                    "bare_atomic_numbers": bare[(mof, best[(mof, "co2")]["bare_signature"])]["bare_atomic_numbers"],
                    "co2_adsorption_energy_ev": best[(mof, "co2")]["adsorption_energy_ev"],
                    "h2o_adsorption_energy_ev": best[(mof, "h2o")]["adsorption_energy_ev"]}
                   for mof in paired_ids]
    gas_refs = {gas: float(np.median(values)) for gas, values in gas_values.items()}
    gas_stats = {}
    for gas, values in gas_values.items():
        array = np.asarray(values)
        gas_stats[gas] = {
            "count": int(array.size), "min": float(array.min()),
            "q01": float(np.quantile(array, 0.01)), "median": gas_refs[gas],
            "q99": float(np.quantile(array, 0.99)), "max": float(array.max()),
            "std": float(array.std()),
            "max_absolute_deviation_from_median": float(np.max(np.abs(array - gas_refs[gas]))),
        }
    return target_db, bare_db, single_rows, paired_rows, gas_refs, gas_stats


def training_records(parquet_path, validation_ids):
    """Build a bounded training table from one ColabFit shard.

    ColabFit omits ``fid``. Its preserved row order is therefore used to keep the
    last stored row per trajectory; this limitation is recorded in the output.
    """
    import pyarrow.parquet as pq

    rows = pq.read_table(
        parquet_path, columns=["names", "energy", "adsorption_energy", "atomic_numbers"]
    ).to_pylist()
    bare, final = {}, {}
    for index, row in enumerate(rows):
        aliases = [_identity(name) for name in row["names"]]
        leaked = [identity[2] for identity in aliases if identity and identity[2] in validation_ids]
        if leaked:
            raise ValueError(f"Official split identity leakage in row aliases: {leaked[0]}")
        identity = _identity(row["names"][0])
        if identity is None:
            continue
        category, trajectory, mof_id, gas = identity
        if mof_id in validation_ids:
            raise ValueError(f"Official split identity leakage: {mof_id}")
        energy = float(row["energy"])
        if category == "mof":
            key = mof_id, _signature(row["atomic_numbers"])
            if key not in bare or energy < bare[key]["energy_ev"]:
                bare[key] = {"energy_ev": energy,
                             "bare_atomic_numbers": row["atomic_numbers"], "source_index": index}
        elif gas and row["adsorption_energy"] is not None:
            final[trajectory] = {"mof_id": mof_id, "gas": gas, "energy_ev": energy,
                                 "trajectory": trajectory, "source_index": index,
                                 "adsorption_energy_ev": float(row["adsorption_energy"]),
                                 "bare_signature": _signature(row["atomic_numbers"], gas)}
    best = {}
    for row in final.values():
        parent = row["mof_id"], row["bare_signature"]
        if parent not in bare:
            continue
        target = row["adsorption_energy_ev"]
        key = row["mof_id"], row["bare_signature"], row["gas"]
        candidate = {**row, "adsorption_energy_ev": target}
        if key not in best or (target, row["trajectory"]) < (
                best[key]["adsorption_energy_ev"], best[key]["trajectory"]):
            best[key] = candidate
    parent_keys = sorted({(mof, signature) for mof, signature, gas in best if gas == "co2"} &
                         {(mof, signature) for mof, signature, gas in best if gas == "h2o"},
                         key=lambda item: (item[0], _signature_atom_count(item[1])))
    selected_parents = {}
    for parent in parent_keys:
        selected_parents.setdefault(parent[0], parent)
    paired = [{"mof_id": mof, "split": "train",
               "bare_atomic_numbers": bare[parent]["bare_atomic_numbers"],
               "bare_source_index": bare[parent]["source_index"],
               "co2_provenance": best[(mof, parent[1], "co2")],
               "h2o_provenance": best[(mof, parent[1], "h2o")],
               "co2_adsorption_energy_ev": best[(mof, parent[1], "co2")]["adsorption_energy_ev"],
               "h2o_adsorption_energy_ev": best[(mof, parent[1], "h2o")]["adsorption_energy_ev"]}
              for mof, parent in sorted(selected_parents.items())]
    return paired, {"rows": len(rows), "bare_compositions": len(bare),
                    "single_gas_final_trajectories": len(final), "paired_mofs": len(paired),
                    "target_field": "ColabFit adsorption_energy (ODAC25 energy_ads)",
                    "selection_limit": "last stored ColabFit row; fid unavailable"}


def mlip_predictions(model_name, calculator, target_db, bare_db, single_rows, gas_refs,
                     progress_path=None):
    """Predict frozen pre-k-point adsorption labels with recorded DFT correction offsets.

    This is reference-assisted evaluation on DFT-selected geometries, not prospective screening.
    """
    bare_cache, predictions, failures = {}, [], []
    started = time.perf_counter()
    for row in single_rows:
        try:
            bare_key = row["mof_id"], row["bare_index"]
            if bare_key not in bare_cache:
                atoms = bare_db.get_atoms(row["bare_index"]).copy()
                atoms.calc = calculator
                bare_cache[bare_key] = float(atoms.get_potential_energy())
            atoms = target_db.get_atoms(row["target_index"]).copy()
            atoms.calc = calculator
            system = float(atoms.get_potential_energy())
            correction = row["system_kpoint_correction_ev"] - row["bare_kpoint_correction_ev"]
            prediction = system - bare_cache[bare_key] - gas_refs[row["adsorbate"]] - correction
            predictions.append({"mof_id": row["mof_id"], "split": "val",
                                "adsorbate": row["adsorbate"],
                                "adsorption_energy_ev": prediction,
                                "predicted_system_energy_ev": system,
                                "predicted_bare_energy_ev": bare_cache[bare_key],
                                "system_kpoint_correction_ev": row["system_kpoint_correction_ev"],
                                "bare_kpoint_correction_ev": row["bare_kpoint_correction_ev"],
                                "dft_gas_reference_ev": gas_refs[row["adsorbate"]]})
        except Exception as error:  # keep failures in the audit denominator
            failures.append({"mof_id": row["mof_id"], "adsorbate": row["adsorbate"],
                             "error": f"{type(error).__name__}: {error}"})
        completed = len(predictions) + len(failures)
        if progress_path and (completed % 10 == 0 or completed == len(single_rows)):
            Path(progress_path).write_text(json.dumps({"model": model_name,
                "status": "partial" if completed < len(single_rows) else "finished",
                "expected_records": len(single_rows), "predictions": predictions,
                "failures": failures}, indent=2, allow_nan=False) + "\n", encoding="utf-8")
            print(f"{model_name}: {completed}/{len(single_rows)}, failures={len(failures)}", flush=True)
    return {"model": model_name, "elapsed_seconds": time.perf_counter() - started,
            "predictions": predictions, "failures": failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-parquet", required=True)
    parser.add_argument("--val-target", required=True)
    parser.add_argument("--val-bare", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--base-input", help="Reuse an earlier no-model result and skip dataset scans")
    parser.add_argument("--frozen-targets", help="Reuse audited source indices; verify identities and energies")
    parser.add_argument("--uma", action="store_true")
    parser.add_argument("--esen-checkpoint")
    args = parser.parse_args()
    from fairchem.core.datasets import AseDBDataset
    target_db = AseDBDataset({"src": str(args.val_target)})
    bare_db = AseDBDataset({"src": str(args.val_bare)})
    fingerprints = input_digests({"train": args.train_parquet, "val_target": args.val_target,
                                 "val_bare": args.val_bare})
    if args.base_input:
        result = json.loads(Path(args.base_input).read_text(encoding="utf-8"))
        if result.get("models"):
            raise ValueError("--base-input must be a no-model result")
        if result.get("input_sha256") != fingerprints:
            raise ValueError("Cached base input is not bound to these dataset bytes; rebuild it")
        single = result["validation_components"]
        validation = result["validation_rows"]
        gas_refs = result["gas_references_ev"]
        train = result["train_rows"]
    else:
        target_db, bare_db, single, validation, gas_refs, gas_stats = validation_records(
            args.val_target, args.val_bare, args.frozen_targets,
            Path(args.output).with_suffix(".bare_cache.json"), fingerprints["val_bare"])
        train, train_profile = training_records(args.train_parquet,
                                                {row["mof_id"] for row in validation})
        result = {"target_contract": "frozen energy_ads_corrected; strongest final sampled single-gas configuration",
                  "evaluation_protocol": "DFT-selected geometries; predicted corrected total energies minus recorded system/bare k-point shifts and fixed DFT gas energy",
                  "gas_reference_identity": "energy_old - energy_mof - energy_ads_corrected; constant-field audit, not a fitted reference",
                  "gas_references_ev": gas_refs, "gas_reference_statistics_ev": gas_stats,
                  "training_profile": train_profile, "train_rows": train,
                  "validation_rows": validation,
                  "validation_components": single,
                  "simple_baselines": evaluate_composition_baselines(train, validation, top_k=10),
                  "models": {}}
        result["input_sha256"] = fingerprints
    from fairchem.core import FAIRChemCalculator, pretrained_mlip
    if args.uma or args.esen_checkpoint:
        validate_gas_references(result["gas_reference_statistics_ev"])
    progress_path = Path(args.output).with_suffix(".progress.json")
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    if args.uma:
        calc = FAIRChemCalculator(pretrained_mlip.get_predict_unit(
            "uma-s-1p2p1", device="cuda", inference_settings="batch"), task_name="odac")
        output = mlip_predictions("uma-s-1p2p1", calc, target_db, bare_db, single, gas_refs, progress_path)
        if not output["failures"]:
            targets = [{"mof_id": row["mof_id"], "split": "val",
                        "adsorbate": row["adsorbate"],
                        "adsorption_energy_ev": row["adsorption_energy_ev"]} for row in single]
            output["evaluation"] = evaluate_prediction_rows(targets, output["predictions"],
                                                            split="val", top_k=10)
        result["models"]["uma"] = output
    if args.esen_checkpoint:
        calc = FAIRChemCalculator.from_model_checkpoint(
            args.esen_checkpoint, device="cuda", inference_settings="batch")
        output = mlip_predictions("esen_sm_odac25_filtered", calc, target_db, bare_db,
                                  single, gas_refs, progress_path)
        if not output["failures"]:
            targets = [{"mof_id": row["mof_id"], "split": "val",
                        "adsorbate": row["adsorbate"],
                        "adsorption_energy_ev": row["adsorption_energy_ev"]} for row in single]
            output["evaluation"] = evaluate_prediction_rows(targets, output["predictions"],
                                                            split="val", top_k=10)
        result["models"]["esen"] = output
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "train_pairs": len(train),
                      "validation_pairs": len(validation),
                      "models": list(result["models"])}, indent=2))


if __name__ == "__main__":
    main()
