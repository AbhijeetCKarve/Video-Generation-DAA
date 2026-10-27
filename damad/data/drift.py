"""Synthetic concept drift injected into a test stream at known change
points.

The transformation is affine and is applied to every observation after
the change point, anomalous or not, so the anomaly structure relative to
the surrounding normal behaviour is preserved.  A static detector that
has calibrated on the pre-drift regime sees the shift as a flood of high
residuals, which is exactly the failure mode the paper is about.

Drift patterns follow the four usual categories (Gama et al. 2014):
  sudden      one abrupt change
  gradual     the two regimes are mixed over a transition window
  incremental the shift grows linearly over a long window
  recurring   the stream alternates between two regimes
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class DriftSpec:
    kind: str                      # sudden | gradual | incremental | recurring
    change_points: List[int]       # step indices where a regime change starts
    transition: int = 0            # steps over which gradual/incremental drift unfolds
    magnitude: float = 1.0         # offset in training-std units
    scale: float = 1.0             # multiplicative change in spread
    frac_sensors: float = 0.5      # fraction of sensors affected


def _regime_transform(d: int, spec: DriftSpec, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Random per-sensor offset and scale for one new regime."""
    k = max(1, int(round(spec.frac_sensors * d)))
    sensors = rng.choice(d, size=k, replace=False)
    offset = np.zeros(d, dtype=np.float32)
    scale = np.ones(d, dtype=np.float32)
    sign = rng.choice([-1.0, 1.0], size=k)
    offset[sensors] = sign * spec.magnitude * rng.uniform(0.6, 1.4, size=k)
    scale[sensors] = spec.scale ** rng.uniform(0.5, 1.5, size=k)
    return offset, scale


def inject_drift(X: np.ndarray, spec: DriftSpec, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return (X_drifted, regime_id per step).  regime_id is 0 before the
    first change point and increments at each change point (for recurring
    drift it alternates 0/1)."""
    rng = np.random.default_rng(seed)
    T, d = X.shape
    Xd = X.copy()
    regime = np.zeros(T, dtype=int)
    cps = sorted(spec.change_points)

    if spec.kind == "recurring":
        offA, scA = np.zeros(d, np.float32), np.ones(d, np.float32)
        offB, scB = _regime_transform(d, spec, rng)
        cur = 0
        bounds = cps + [T]
        start = 0
        for i, cp in enumerate(bounds):
            if cur == 1:
                Xd[start:cp] = Xd[start:cp] * scB + offB
            regime[start:cp] = cur
            start = cp
            cur = 1 - cur
        return Xd, regime

    cum_off, cum_sc = np.zeros(d, np.float32), np.ones(d, np.float32)
    for r, cp in enumerate(cps, start=1):
        off, sc = _regime_transform(d, spec, rng)
        nxt = cps[r] if r < len(cps) else T
        seg = slice(cp, nxt)
        if spec.kind == "sudden":
            Xd[seg] = Xd[seg] * sc + off
        elif spec.kind in ("gradual", "incremental"):
            L = max(1, spec.transition)
            t = np.arange(cp, nxt)
            alpha = np.clip((t - cp) / L, 0.0, 1.0)[:, None].astype(np.float32)
            if spec.kind == "gradual":
                # probabilistic mixing: each step is drawn from old or new regime
                pick = (rng.uniform(size=len(t))[:, None] < alpha).astype(np.float32)
                Xd[seg] = Xd[seg] * (1 - pick) + (Xd[seg] * sc + off) * pick
            else:
                Xd[seg] = Xd[seg] * (1 + alpha * (sc - 1)) + alpha * off
        else:
            raise ValueError(spec.kind)
        regime[seg] = r
    return Xd, regime


def default_specs(T: int, W: int) -> List[DriftSpec]:
    """The drift conditions used in the protocol: change points at fixed
    fractions of the stream so that every method sees the same stream."""
    c1, c2, c3 = int(0.35 * T), int(0.6 * T), int(0.8 * T)
    L = max(20 * W, int(0.05 * T))
    return [
        DriftSpec("sudden", [c1, c2], magnitude=1.5, scale=1.3),
        DriftSpec("gradual", [c1, c2], transition=L, magnitude=1.5, scale=1.3),
        DriftSpec("incremental", [c1], transition=int(0.3 * T), magnitude=2.0, scale=1.3),
        DriftSpec("recurring", [c1, c2, c3], magnitude=1.5, scale=1.3),
    ]
