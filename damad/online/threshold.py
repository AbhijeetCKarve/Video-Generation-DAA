"""Threshold selection on reconstruction residuals.

`pot_threshold` is the Peaks-Over-Threshold procedure of Siffer et al.
(KDD 2017): a generalised Pareto distribution is fitted to the excesses
over a high empirical quantile and the detection threshold is the
quantile of that tail at risk level q.  It needs no labels.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import genpareto


def pot_threshold(scores: np.ndarray, q: float = 1e-3, level: float = 0.98, min_excess: int = 10) -> float:
    s = np.asarray(scores, dtype=np.float64)
    s = s[np.isfinite(s)]
    n = len(s)
    if n < 20:
        return float(np.max(s)) * 1.5 if n else np.inf
    t = float(np.quantile(s, level))
    y = s[s > t] - t
    if len(y) < min_excess or np.all(y < 1e-12):
        return float(np.quantile(s, 1.0 - q)) if q > 1.0 / n else float(np.max(s)) * 1.2
    try:
        gamma, _, sigma = genpareto.fit(y, floc=0.0)
    except Exception:  # noqa: BLE001
        return float(np.max(s)) * 1.2
    gamma = float(np.clip(gamma, -0.5, 1.0))
    sigma = max(float(sigma), 1e-9)
    r = q * n / len(y)
    if abs(gamma) < 1e-6:
        z = t - sigma * np.log(r)
    else:
        z = t + (sigma / gamma) * (r ** (-gamma) - 1.0)
    if not np.isfinite(z) or z < t:
        z = float(np.max(s)) * 1.2
    # guard against absurd extrapolation on short calibration windows
    return float(min(z, 10.0 * float(np.max(s))))


class GatedThreshold:
    """Holds the current threshold and only recomputes it when told that a
    regime change has been confirmed, so that short residual bursts do
    not move it."""

    def __init__(self, q: float = 1e-3, level: float = 0.98):
        self.q = q
        self.level = level
        self.tau = np.inf
        self.n_recal = 0

    def calibrate(self, scores: np.ndarray) -> float:
        self.tau = pot_threshold(scores, self.q, self.level)
        self.n_recal += 1
        return self.tau
