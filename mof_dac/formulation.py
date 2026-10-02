"""Matrix contract: h[n], W[n,n], E[me,n], e[me], U[mu,n], u[mu]."""

from dataclasses import dataclass

import numpy as np


@dataclass
class Problem:
    ids: tuple[str, ...]
    h: np.ndarray
    W: np.ndarray
    E: np.ndarray
    e: np.ndarray
    U: np.ndarray
    u: np.ndarray

    def __post_init__(self):
        n = len(self.ids)
        if not n or len(set(self.ids)) != n:
            raise ValueError("Variable IDs must be nonempty and unique")
        for name in ("h", "W", "E", "e", "U", "u"):
            value = np.array(getattr(self, name), dtype=np.float64, copy=True)
            if not np.isfinite(value).all():
                raise ValueError(f"{name} contains nonfinite coefficients")
            setattr(self, name, value)
        if self.h.shape != (n,) or self.W.shape != (n, n):
            raise ValueError("Expected h[n] and W[n,n]")
        for matrix, rhs in ((self.E, self.e), (self.U, self.u)):
            if matrix.ndim != 2 or matrix.shape[1] != n or rhs.shape != (matrix.shape[0],):
                raise ValueError("Constraint matrix/RHS dimensions disagree")
        if not np.allclose(self.W, self.W.T, atol=1e-12, rtol=0):
            raise ValueError("W must be symmetric")
        if np.any(np.diag(self.W) != 0):
            raise ValueError("W diagonal must be zero; linear costs belong in h")

    @property
    def n(self):
        return len(self.ids)

    def state(self, x):
        """Validate a state [n] or batch [...,n]; never clip silently."""
        x = np.asarray(x, dtype=np.float64)
        if x.ndim == 0 or x.shape[-1] != self.n or not np.isfinite(x).all():
            raise ValueError("State must be finite with final dimension n")
        return x

    def energy(self, x):
        x = self.state(x)
        return x @ self.h + 0.5 * np.einsum("...i,ij,...j->...", x, self.W, x)

    def gradient(self, x):
        return self.state(x) @ self.W + self.h

    def violations(self, x):
        """Maximum raw linear, box and integrality residual per state."""
        x = self.state(x)
        return {
            "equality": np.max(np.abs(x @ self.E.T - self.e), axis=-1, initial=0),
            "inequality": np.max(x @ self.U.T - self.u, axis=-1, initial=0),
            "bounds": np.maximum(np.max(-x, axis=-1, initial=0),
                                 np.max(x - 1, axis=-1, initial=0)),
            "integrality": np.max(np.abs(x - np.rint(x)), axis=-1, initial=0),
        }

    def feasible(self, x, *, binary=False, tol=1e-7):
        if not np.isfinite(tol) or tol < 0:
            raise ValueError("Tolerance must be finite and nonnegative")
        residuals = self.violations(x)
        names = ("equality", "inequality", "bounds", "integrality") if binary else (
            "equality", "inequality", "bounds")
        return np.maximum.reduce([residuals[name] for name in names]) <= tol

    def binary_qubo(self):
        """Symmetric Q[n,n]. Equivalent to energy only for binary states."""
        return np.diag(self.h) + self.W / 2

    def equality_penalty_qubo(self, rho):
        """Return Q, offset for H + rho*||Ex-e||^2 on bits.

        Inequalities remain explicit. This is not a full unconstrained export.
        """
        if not np.isfinite(rho) or rho <= 0:
            raise ValueError("rho must be finite and positive")
        Q = self.binary_qubo() + rho * (self.E.T @ self.E)
        Q -= np.diag(2 * rho * (self.E.T @ self.e))
        return Q, float(rho * (self.e @ self.e))

    def spectrum(self):
        eigenvalues = np.linalg.eigvalsh(self.W)
        return {"min_eigenvalue": float(eigenvalues[0]),
                "max_eigenvalue": float(eigenvalues[-1]),
                "full_space_psd": bool(eigenvalues[0] >= -1e-10)}

    def snn_arrays(self, *, equality_band=0.0):
        """A[n,n], b[n], C[m,n], d[m] for Cx+d<=0, including bounds.

        Export does not assert convexity or execute a solver. Epsilon bands
        change the equality feasible set and must be logged by the caller.
        """
        if not np.isfinite(equality_band) or equality_band < 0:
            raise ValueError("Equality band must be finite and nonnegative")
        C = np.vstack((self.U, self.E, -self.E, np.eye(self.n), -np.eye(self.n)))
        d = np.concatenate((-self.u, -self.e - equality_band,
                            self.e - equality_band, -np.ones(self.n), np.zeros(self.n)))
        return self.W.copy(), self.h.copy(), C, d
