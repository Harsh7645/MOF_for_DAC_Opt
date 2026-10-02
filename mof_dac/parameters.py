"""Synthetic pairwise coefficient recovery for parameter-pipeline validation."""

import numpy as np


def pairwise_design(states):
    """Return [samples, 1+n+n(n-1)/2] constant/linear/pair features."""
    states = np.asarray(states, dtype=float)
    if states.ndim != 2 or not np.isfinite(states).all():
        raise ValueError("states must be a finite [samples,n] matrix")
    i, j = np.triu_indices(states.shape[1], 1)
    return np.column_stack((np.ones(len(states)), states, states[:, i] * states[:, j]))


def fit_pairwise(states, targets):
    """Fit a complete quadratic pseudo-energy and reject unidentifiable designs."""
    states = np.asarray(states, dtype=float)
    targets = np.asarray(targets, dtype=float)
    design = pairwise_design(states)
    if targets.shape != (len(states),) or not np.isfinite(targets).all():
        raise ValueError("targets must be finite with one value per state")
    rank = int(np.linalg.matrix_rank(design))
    if rank < design.shape[1]:
        raise ValueError(f"Pairwise coefficients unidentifiable: rank {rank}/{design.shape[1]}")
    coefficients, *_ = np.linalg.lstsq(design, targets, rcond=None)
    n = states.shape[1]
    h = coefficients[1:n + 1]
    W = np.zeros((n, n))
    i, j = np.triu_indices(n, 1)
    W[i, j] = W[j, i] = coefficients[n + 1:]
    residual = design @ coefficients - targets
    return {"offset": float(coefficients[0]), "h": h, "W": W,
            "rank": rank, "parameters": design.shape[1],
            "rmse": float(np.sqrt(np.mean(residual ** 2)))}
