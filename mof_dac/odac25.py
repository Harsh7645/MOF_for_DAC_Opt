"""Paired CO2/H2O target construction and evaluation utilities."""

import numpy as np
from scipy.stats import rankdata


ADSORBATES = ("co2", "h2o")


def adsorption_energy(total_energy, bare_energy, co2_reference, h2o_reference,
                      n_co2, n_h2o):
    """Return E(system)-E(bare)-n_CO2*E(CO2)-n_H2O*E(H2O), in shared units."""
    values = np.asarray([total_energy, bare_energy, co2_reference, h2o_reference,
                         n_co2, n_h2o], dtype=float)
    if not np.isfinite(values).all() or n_co2 < 0 or n_h2o < 0:
        raise ValueError("Finite energies and nonnegative adsorbate counts required")
    if int(n_co2) != n_co2 or int(n_h2o) != n_h2o:
        raise ValueError("Adsorbate counts must be integers")
    return float(total_energy - bare_energy - n_co2 * co2_reference - n_h2o * h2o_reference)


def pair_adsorbate_rows(rows):
    """Pair one CO2 and one H2O adsorption target per MOF and split.

    Input rows require: mof_id, split, adsorbate and adsorption_energy_ev.
    Duplicate adsorbate records are rejected rather than selected implicitly.
    """
    grouped = {}
    split_by_mof = {}
    for row in rows:
        mof_id, split = str(row["mof_id"]), str(row["split"])
        adsorbate = str(row["adsorbate"]).lower()
        if adsorbate not in ADSORBATES:
            raise ValueError(f"Unsupported adsorbate: {adsorbate}")
        if mof_id in split_by_mof and split_by_mof[mof_id] != split:
            raise ValueError(f"Split leakage for MOF {mof_id}")
        split_by_mof[mof_id] = split
        key = (mof_id, split)
        grouped.setdefault(key, {})
        if adsorbate in grouped[key]:
            raise ValueError(f"Duplicate {adsorbate} target for MOF {mof_id}")
        value = float(row["adsorption_energy_ev"])
        if not np.isfinite(value):
            raise ValueError("Targets must be finite")
        grouped[key][adsorbate] = value
    return [{"mof_id": key[0], "split": key[1],
             "co2_adsorption_energy_ev": values["co2"],
             "h2o_adsorption_energy_ev": values["h2o"]}
            for key, values in sorted(grouped.items()) if set(values) == set(ADSORBATES)]


def paired_metrics(targets, predictions, *, top_k=10):
    """Evaluate [samples,2] CO2/H2O energies and their competition difference."""
    targets = np.asarray(targets, dtype=float)
    predictions = np.asarray(predictions, dtype=float)
    if targets.shape != predictions.shape or targets.ndim != 2 or targets.shape[1] != 2:
        raise ValueError("targets and predictions must share shape [samples,2]")
    if not len(targets) or not np.isfinite(targets).all() or not np.isfinite(predictions).all():
        raise ValueError("Paired arrays must be nonempty and finite")
    if not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be positive")
    error = predictions - targets
    target_delta = targets[:, 0] - targets[:, 1]
    predicted_delta = predictions[:, 0] - predictions[:, 1]
    k = min(top_k, len(targets))
    true_top = set(np.argsort(target_delta, kind="stable")[:k].tolist())
    predicted_top = set(np.argsort(predicted_delta, kind="stable")[:k].tolist())
    true_rank = rankdata(target_delta, method="average")
    predicted_rank = rankdata(predicted_delta, method="average")
    rank_correlation = (None if np.ptp(true_rank) == 0 or np.ptp(predicted_rank) == 0 else
                        float(np.corrcoef(true_rank, predicted_rank)[0, 1]))
    return {"samples": len(targets), "target_order": list(ADSORBATES),
            "mae_ev": np.mean(np.abs(error), axis=0).tolist(),
            "rmse_ev": np.sqrt(np.mean(error ** 2, axis=0)).tolist(),
            "competition_delta_mae_ev": float(np.mean(np.abs(predicted_delta - target_delta))),
            "top_k": k, "competition_top_k_overlap": len(true_top & predicted_top) / k,
            "competition_spearman": rank_correlation,
            "top_k_tie_policy": "stable input order; sorted MOF IDs in row evaluation",
            "predicted_unique_deltas": int(len(np.unique(predicted_delta)))}


def evaluate_prediction_rows(target_rows, prediction_rows, *, split, top_k=10):
    """Join paired predictions to frozen targets by MOF ID and evaluate ranking."""
    targets = pair_adsorbate_rows(target_rows)
    predictions = pair_adsorbate_rows(prediction_rows)
    target_map = {row["mof_id"]: row for row in targets if row["split"] == split}
    prediction_map = {row["mof_id"]: row for row in predictions if row["split"] == split}
    if set(target_map) != set(prediction_map):
        missing = sorted(set(target_map) - set(prediction_map))[:3]
        extra = sorted(set(prediction_map) - set(target_map))[:3]
        raise ValueError(f"Prediction pool mismatch; missing={missing}, extra={extra}")
    ids = sorted(target_map)
    y = [[target_map[key]["co2_adsorption_energy_ev"],
          target_map[key]["h2o_adsorption_energy_ev"]] for key in ids]
    yhat = [[prediction_map[key]["co2_adsorption_energy_ev"],
             prediction_map[key]["h2o_adsorption_energy_ev"]] for key in ids]
    return {"split": split, "mof_ids": ids,
            "metrics": paired_metrics(y, yhat, top_k=top_k)}


def profile_adsorbate_rows(rows):
    """Report target availability without choosing among repeated trajectories."""
    fields = ("mof_name", "name", "fid", "nco2", "nh2o", "nn2", "no2",
              "nads", "energy_ads_corrected")
    missing = {field: 0 for field in fields}
    category = {"co2_single": 0, "h2o_single": 0, "other": 0}
    finite_targets = {"co2": 0, "h2o": 0}
    grouped, trajectories = {}, set()
    records = inconsistent_counts = 0
    for row in rows:
        records += 1
        for field in fields:
            missing[field] += int(row.get(field) is None)
        try:
            raw_counts = tuple(float(row[key]) for key in ("nco2", "nh2o", "nn2", "no2"))
            raw_nads = float(row["nads"])
            if any(not np.isfinite(value) or not value.is_integer()
                   for value in raw_counts + (raw_nads,)):
                raise ValueError
            counts = tuple(int(value) for value in raw_counts)
            nads = int(raw_nads)
            if any(value < 0 for value in counts) or nads != sum(counts):
                inconsistent_counts += 1
                category["other"] += 1
                continue
        except (KeyError, TypeError, ValueError, OverflowError):
            inconsistent_counts += 1
            category["other"] += 1
            continue
        adsorbate = "co2" if counts == (1, 0, 0, 0) else (
            "h2o" if counts == (0, 1, 0, 0) else None)
        if adsorbate is None:
            category["other"] += 1
            continue
        category[adsorbate + "_single"] += 1
        try:
            target = float(row["energy_ads_corrected"])
        except (KeyError, TypeError, ValueError):
            continue
        if not np.isfinite(target) or row.get("mof_name") is None:
            continue
        finite_targets[adsorbate] += 1
        key = (str(row["mof_name"]), adsorbate)
        grouped[key] = grouped.get(key, 0) + 1
        if row.get("name") is not None:
            trajectories.add(str(row["name"]))
    co2_mofs = {mof for (mof, adsorbate) in grouped if adsorbate == "co2"}
    h2o_mofs = {mof for (mof, adsorbate) in grouped if adsorbate == "h2o"}
    return {"records": records, "missing_or_null_by_field": missing,
            "inconsistent_adsorbate_count_rows": inconsistent_counts,
            "record_categories": category, "finite_corrected_targets": finite_targets,
            "unique_target_trajectories": len(trajectories),
            "unique_target_mofs": len(co2_mofs | h2o_mofs),
            "mofs_with_both_single_adsorbates": len(co2_mofs & h2o_mofs),
            "mof_adsorbate_groups_with_multiple_records":
                sum(count > 1 for count in grouped.values())}


def select_relaxed_adsorbate_targets(rows, *, split):
    """Reduce relaxation rows to one sampled single-gas target per MOF.

    For each trajectory, retain its largest ``fid`` (the final stored frame).
    Across final frames from different sampled trajectories for the same
    MOF/gas, retain the lowest corrected adsorption energy. Mixed and
    multi-molecule configurations are outside this paired-target contract.
    """
    if not str(split):
        raise ValueError("split is required")
    final_by_trajectory = {}
    for source_index, row in enumerate(rows):
        try:
            raw = tuple(float(row[key]) for key in ("nco2", "nh2o", "nn2", "no2"))
            raw_nads = float(row["nads"])
        except (KeyError, TypeError, ValueError, OverflowError) as error:
            raise ValueError(f"Invalid adsorbate counts at row {source_index}") from error
        if any(not np.isfinite(value) or not value.is_integer()
               for value in raw + (raw_nads,)):
            raise ValueError(f"Invalid adsorbate counts at row {source_index}")
        counts, nads = tuple(int(value) for value in raw), int(raw_nads)
        if any(value < 0 for value in counts) or nads != sum(counts):
            raise ValueError(f"Inconsistent adsorbate counts at row {source_index}")
        adsorbate = "co2" if counts == (1, 0, 0, 0) else (
            "h2o" if counts == (0, 1, 0, 0) else None)
        if adsorbate is None:
            continue
        try:
            if row["mof_name"] is None or row["name"] is None:
                raise ValueError
            mof_id = str(row["mof_name"])
            trajectory = str(row["name"])
            fid = int(row["fid"])
            energy = float(row["energy_ads_corrected"])
        except (KeyError, TypeError, ValueError, OverflowError) as error:
            raise ValueError(f"Invalid target metadata at row {source_index}") from error
        if not mof_id or not trajectory or fid < 0 or not np.isfinite(energy):
            raise ValueError(f"Invalid target metadata at row {source_index}")
        key = trajectory
        candidate = {"mof_id": mof_id, "split": str(split), "adsorbate": adsorbate,
                     "adsorption_energy_ev": energy, "selected_trajectory": trajectory,
                     "selected_fid": fid, "source_index": source_index}
        prior = final_by_trajectory.get(key)
        if prior is not None:
            if (prior["mof_id"], prior["adsorbate"]) != (mof_id, adsorbate):
                raise ValueError(f"Trajectory {trajectory} changes MOF or adsorbate")
            if prior["selected_fid"] == fid:
                raise ValueError(f"Duplicate final-frame key {trajectory}/{fid}")
        if prior is None or fid > prior["selected_fid"]:
            final_by_trajectory[key] = candidate

    grouped = {}
    for candidate in final_by_trajectory.values():
        key = candidate["mof_id"], candidate["adsorbate"]
        grouped.setdefault(key, []).append(candidate)
    selected = []
    for candidates in grouped.values():
        winner = min(candidates, key=lambda row: (
            row["adsorption_energy_ev"], row["selected_trajectory"], row["selected_fid"]))
        selected.append({**winner, "trajectory_candidates": len(candidates)})
    return sorted(selected, key=lambda row: (row["mof_id"], row["adsorbate"]))
