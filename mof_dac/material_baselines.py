"""Leakage-safe composition baselines for paired CO2/H2O targets."""

from dataclasses import dataclass

import numpy as np

from .odac25 import paired_metrics


MAX_ATOMIC_NUMBER = 118


def composition_vector(atomic_numbers):
    """Return element fractions [118] for one bare MOF composition."""
    numbers = np.asarray(atomic_numbers, dtype=int)
    if numbers.ndim != 1 or not len(numbers):
        raise ValueError("atomic_numbers must be a nonempty vector")
    if np.any(numbers < 1) or np.any(numbers > MAX_ATOMIC_NUMBER):
        raise ValueError("atomic_numbers must be in [1, 118]")
    counts = np.bincount(numbers, minlength=MAX_ATOMIC_NUMBER + 1)[1:]
    return counts.astype(float) / len(numbers)


def paired_arrays(rows, *, expected_split):
    """Return IDs, composition matrix [N,118], and paired targets [N,2]."""
    ids, features, targets = [], [], []
    for row in rows:
        if str(row["split"]) != expected_split:
            raise ValueError(f"Expected split {expected_split!r}")
        mof_id = str(row["mof_id"])
        if not mof_id or mof_id in ids:
            raise ValueError(f"Missing or duplicate MOF ID: {mof_id!r}")
        target = np.asarray([row["co2_adsorption_energy_ev"],
                             row["h2o_adsorption_energy_ev"]], dtype=float)
        if not np.isfinite(target).all():
            raise ValueError("Targets must be finite")
        ids.append(mof_id)
        features.append(composition_vector(row["bare_atomic_numbers"]))
        targets.append(target)
    if not rows:
        raise ValueError("At least one paired row is required")
    return ids, np.asarray(features), np.asarray(targets)


@dataclass(frozen=True)
class RidgeModel:
    """Train-fitted standardization plus a two-target ridge regressor."""

    mean: np.ndarray
    scale: np.ndarray
    intercept: np.ndarray
    coefficients: np.ndarray
    alpha: float

    def predict(self, features):
        features = np.asarray(features, dtype=float)
        if features.ndim != 2 or features.shape[1] != len(self.mean):
            raise ValueError("features have incompatible shape")
        return self.intercept + ((features - self.mean) / self.scale) @ self.coefficients


def fit_ridge(features, targets, alpha):
    """Fit paired ridge models; all statistics are learned from these rows only."""
    features, targets = np.asarray(features, float), np.asarray(targets, float)
    if features.ndim != 2 or targets.shape != (len(features), 2) or not len(features):
        raise ValueError("Expected features [N,D] and targets [N,2]")
    if not np.isfinite(features).all() or not np.isfinite(targets).all() or alpha < 0:
        raise ValueError("Finite arrays and nonnegative alpha required")
    mean = features.mean(axis=0)
    scale = features.std(axis=0)
    scale[scale == 0] = 1.0
    x = (features - mean) / scale
    intercept = targets.mean(axis=0)
    coefficients = np.linalg.solve(x.T @ x + float(alpha) * np.eye(x.shape[1]),
                                   x.T @ (targets - intercept))
    return RidgeModel(mean, scale, intercept, coefficients, float(alpha))


def select_ridge_alpha(features, targets, ids, *, alphas=(0.01, 0.1, 1.0, 10.0), folds=5):
    """Choose alpha by deterministic train-only MOF folds and paired MAE."""
    features, targets = np.asarray(features, float), np.asarray(targets, float)
    if len(ids) != len(features) or len(set(ids)) != len(ids) or folds < 2:
        raise ValueError("Unique IDs and at least two folds are required")
    folds = min(folds, len(ids))
    assignment = np.empty(len(ids), dtype=int)
    for fold, index in enumerate(np.argsort(np.asarray(ids, dtype=str), kind="stable")):
        assignment[index] = fold % folds
    scores = {}
    for alpha in alphas:
        errors = []
        for fold in range(folds):
            held = assignment == fold
            if not held.any() or (~held).sum() == 0:
                continue
            prediction = fit_ridge(features[~held], targets[~held], alpha).predict(features[held])
            errors.extend(np.abs(prediction - targets[held]).ravel())
        scores[float(alpha)] = float(np.mean(errors))
    if not scores:
        raise ValueError("Cross-validation produced no folds")
    selected = min(scores, key=lambda alpha: (scores[alpha], alpha))
    return selected, scores


def evaluate_composition_baselines(train_rows, validation_rows, *, top_k=10):
    """Fit on train and evaluate constant/composition baselines on frozen validation."""
    train_ids, train_x, train_y = paired_arrays(train_rows, expected_split="train")
    val_ids, val_x, val_y = paired_arrays(validation_rows, expected_split="val")
    overlap = set(train_ids) & set(val_ids)
    if overlap:
        raise ValueError(f"Train/validation MOF leakage: {sorted(overlap)[:3]}")
    constant = np.broadcast_to(train_y.mean(axis=0), val_y.shape).copy()
    alpha, cv = select_ridge_alpha(train_x, train_y, train_ids)
    ridge = fit_ridge(train_x, train_y, alpha)
    composition = ridge.predict(val_x)
    return {
        "train_samples": len(train_ids), "validation_samples": len(val_ids),
        "feature_definition": "118 bare-MOF elemental fractions",
        "selected_alpha": alpha, "train_cv_mae_by_alpha": cv,
        "constant_train_mean_ev": train_y.mean(axis=0).tolist(),
        "ridge_model": {"feature_mean": ridge.mean.tolist(),
                        "feature_scale": ridge.scale.tolist(),
                        "intercept_ev": ridge.intercept.tolist(),
                        "coefficients": ridge.coefficients.tolist()},
        "constant": {"metrics": paired_metrics(val_y, constant, top_k=top_k),
                     "predictions_ev": constant.tolist()},
        "composition_ridge": {"metrics": paired_metrics(val_y, composition, top_k=top_k),
                              "predictions_ev": composition.tolist()},
        "validation_mof_ids": val_ids,
    }
