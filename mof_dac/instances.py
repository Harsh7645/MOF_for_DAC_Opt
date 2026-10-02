"""Controlled synthetic slot instances; no chemical identity or validity implied."""

import numpy as np

from .formulation import Problem


def slot_problem(slots, *, seed=0, functionalized=None, frustrated=False,
                 degenerate=False, interaction_density=None, interaction_scale=0.5):
    """Build a two-option fixed-template assignment problem with 2*slots bits.

    Option B is the abstract functionalized choice. The fixed metal/node is
    eliminated because it is not a decision variable. A redundant total-occupancy
    row acts as the synthetic charge-audit analogue.
    """
    if slots < 2:
        raise ValueError("At least two slots required")
    if interaction_density is not None and not 0 <= interaction_density <= 1:
        raise ValueError("interaction_density must be in [0, 1]")
    if not np.isfinite(interaction_scale) or interaction_scale < 0:
        raise ValueError("interaction_scale must be finite and nonnegative")
    functionalized = slots // 2 if functionalized is None else functionalized
    ids = tuple(f"s{s}_{option}" for s in range(slots) for option in "AB")
    rng = np.random.default_rng(seed)
    h = np.zeros(2 * slots) if degenerate else rng.normal(0, 1, 2 * slots)
    W = np.zeros((2 * slots, 2 * slots))
    if not degenerate:
        if interaction_density is None:
            contacts = {tuple(sorted((s, (s + 1) % slots))) for s in range(slots)}
        else:
            contacts = {(s, t) for s in range(slots) for t in range(s + 1, slots)
                        if rng.random() < interaction_density}
        for s, t in sorted(contacts):
            for a in range(2):
                for b in range(2):
                    i, j = 2 * s + a, 2 * t + b
                    W[i, j] = W[j, i] = rng.normal(0, interaction_scale)
    E = np.zeros((slots + 2, 2 * slots))
    e = np.ones(slots + 2)
    for s in range(slots):
        E[s, 2 * s:2 * s + 2] = 1
    E[slots, 1::2] = 1
    e[slots] = functionalized
    E[slots + 1] = 1
    e[slots + 1] = slots
    U = np.zeros((int(frustrated), 2 * slots))
    u = np.ones(int(frustrated))
    if frustrated:
        U[0, [1, 3]] = 1
    return Problem(ids, h, W, E, e, U, u)


def phase1_instances():
    """Named deterministic family used by the Phase 1 verification sweep."""
    return {
        "slots2": slot_problem(2, seed=0),
        "slots4_frustrated": slot_problem(4, seed=1, frustrated=True),
        "slots6": slot_problem(6, seed=2),
        "slots8_frustrated": slot_problem(8, seed=3, frustrated=True),
        "slots4_degenerate": slot_problem(4, degenerate=True),
        "slots4_infeasible": slot_problem(4, functionalized=5),
    }


def decode_slot_state(state, functionalized):
    """Nearest binary two-option/slot state with an exact number of B choices."""
    state = np.asarray(state, dtype=float)
    if state.ndim != 1 or len(state) % 2 or not np.isfinite(state).all():
        raise ValueError("state must be a finite flat array with two values per slot")
    slots = len(state) // 2
    if not isinstance(functionalized, int) or not 0 <= functionalized <= slots:
        raise ValueError("functionalized must be an integer in [0, slots]")
    selected_b = np.argsort(-(state[1::2] - state[0::2]), kind="stable")[:functionalized]
    decoded = np.zeros_like(state)
    decoded[0::2] = 1
    decoded[2 * selected_b] = 0
    decoded[2 * selected_b + 1] = 1
    return decoded
