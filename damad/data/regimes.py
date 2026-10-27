"""Operating regimes as meta-learning tasks, built by clustering.

Each normal window is summarised by its per-feature mean and standard
deviation.  k-means on the summaries, with k picked by the silhouette
score, gives the regimes; the silhouette of the chosen clustering is the
task-diversity score of the stream.  This is the construction used in
the offline study; the online study segments in time instead.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


@dataclass
class RegimeSet:
    labels: np.ndarray           # cluster id per window
    k: int
    silhouette: float
    curve: Dict[int, float]      # silhouette per candidate k
    sizes: Dict[int, int]


def summarise(windows: np.ndarray) -> np.ndarray:
    """(N, L, d) -> (N, 2d): per-feature mean and std of each window."""
    return np.concatenate([windows.mean(1), windows.std(1)], 1).astype(np.float32)


def build_regimes(windows: np.ndarray, seed: int, k_range: Tuple[int, int] = (2, 12),
                  max_fit: int = 5000, min_size: int = 80) -> RegimeSet:
    rng = np.random.default_rng(seed)
    F = summarise(windows)
    fit_idx = rng.choice(len(F), min(max_fit, len(F)), replace=False)
    curve: Dict[int, float] = {}
    best_k, best_s, best_km = None, -1.0, None
    for k in range(k_range[0], k_range[1] + 1):
        if k >= len(fit_idx):
            break
        km = KMeans(n_clusters=k, n_init=4, random_state=seed).fit(F[fit_idx])
        s = float(silhouette_score(F[fit_idx], km.labels_))
        curve[k] = s
        if s > best_s:
            best_k, best_s, best_km = k, s, km
    labels = best_km.predict(F)
    sizes = {int(c): int((labels == c).sum()) for c in range(best_k)}
    return RegimeSet(labels, best_k, best_s, curve, sizes)


def regime_windows(windows: np.ndarray, regimes: RegimeSet, min_size: int = 80) -> List[np.ndarray]:
    """Windows grouped by regime, dropping regimes too small for episodes."""
    out = []
    for c, n in regimes.sizes.items():
        if n >= min_size:
            out.append(windows[regimes.labels == c])
    return out


def split_regimes(groups: List[np.ndarray], seed: int, val_frac: float = 0.2):
    """Hold out at least one regime for meta-validation."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(groups))
    n_val = max(1, int(round(val_frac * len(groups)))) if len(groups) > 1 else 0
    val = [groups[i] for i in idx[:n_val]]
    train = [groups[i] for i in idx[n_val:]] or groups
    return train, val
