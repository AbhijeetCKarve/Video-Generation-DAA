"""Maximum mean discrepancy between a reference set of encoder embeddings
and the most recent embeddings.

The bandwidth is the median pairwise distance inside the reference set
and the alarm threshold is a multiple of the largest MMD^2 between a
contiguous block of the reference and the rest of it (a block
bootstrap), so no label and no hand-set threshold is needed.  Two consecutive exceedances are required before an alarm is
raised; one exceedance is cheap to get from a short anomaly burst.
"""
from __future__ import annotations

from collections import deque

import numpy as np


def _sqdist(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    aa = (A * A).sum(1)[:, None]
    bb = (B * B).sum(1)[None, :]
    return np.maximum(aa + bb - 2.0 * A @ B.T, 0.0)


def mmd2(X: np.ndarray, Y: np.ndarray, gamma: float) -> float:
    """Unbiased MMD^2 with a Gaussian kernel."""
    m, n = len(X), len(Y)
    Kxx = np.exp(-gamma * _sqdist(X, X))
    Kyy = np.exp(-gamma * _sqdist(Y, Y))
    Kxy = np.exp(-gamma * _sqdist(X, Y))
    np.fill_diagonal(Kxx, 0.0)
    np.fill_diagonal(Kyy, 0.0)
    return float(Kxx.sum() / (m * (m - 1)) + Kyy.sum() / (n * (n - 1)) - 2.0 * Kxy.mean())


class MMDDetector:
    def __init__(self, n_recent: int = 64, check_every: int = 32, n_boot: int = 50,
                 confirm: int = 2, seed: int = 0, margin: float = 1.5):
        self.n_recent = n_recent
        self.margin = margin
        self.check_every = check_every
        self.n_boot = n_boot
        self.confirm = confirm
        self.rng = np.random.default_rng(seed)
        self.ref = None
        self.gamma = 1.0
        self.thr = np.inf
        self.recent: deque = deque(maxlen=n_recent)
        self.t = 0
        self.streak = 0
        self.last_value = 0.0

    def calibrate(self, ref: np.ndarray) -> None:
        ref = np.asarray(ref, dtype=np.float64)
        self.ref = ref
        d = _sqdist(ref, ref)
        med = np.median(d[np.triu_indices(len(ref), 1)])
        self.gamma = 1.0 / max(med, 1e-6)
        # block null: a *contiguous* stretch of the reference against the
        # rest of it.  A random-split null ignores the slow within-regime
        # variation that real sensor streams have and sets the bar far
        # too low; the block version asks whether the recent stretch looks
        # less like the reference than the reference's own stretches do.
        null = []
        n = len(ref)
        h = max(2, min(self.n_recent, n // 2))
        for _ in range(self.n_boot):
            a = int(self.rng.integers(0, n - h + 1))
            blk = ref[a:a + h]
            rest = np.concatenate([ref[:a], ref[a + h:]], 0)
            if len(rest) > 2 * h:
                rest = rest[self.rng.choice(len(rest), 2 * h, replace=False)]
            null.append(mmd2(rest, blk, self.gamma))
        self.thr = float(np.max(null)) * self.margin + 1e-6
        self.recent.clear()
        self.streak = 0

    def update(self, z: np.ndarray) -> bool:
        self.t += 1
        self.recent.append(np.asarray(z, dtype=np.float64))
        if self.ref is None or self.t % self.check_every != 0 or len(self.recent) < self.n_recent:
            return False
        Y = np.stack(self.recent)
        sub = self.ref if len(self.ref) <= 2 * self.n_recent else self.ref[self.rng.choice(len(self.ref), 2 * self.n_recent, replace=False)]
        self.last_value = mmd2(sub, Y, self.gamma)
        if self.last_value > self.thr:
            self.streak += 1
        else:
            self.streak = 0
        return self.streak >= self.confirm
