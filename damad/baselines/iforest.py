"""Isolation Forest on flattened windows: the classical unsupervised
reference point.  Trained once on pooled normal windows; the threshold
comes from the same POT procedure as every other method."""
from __future__ import annotations

import time
from typing import Dict

import numpy as np
from sklearn.ensemble import IsolationForest

from ..online.threshold import pot_threshold


def run_iforest(train_windows: np.ndarray, Xw: np.ndarray, k_shot: int, calib_len: int,
                seed: int, pot_q: float = 1e-2, pot_level: float = 0.98, max_train: int = 20000) -> Dict:
    rng = np.random.default_rng(seed)
    if len(train_windows) > max_train:
        train_windows = train_windows[rng.choice(len(train_windows), max_train, replace=False)]
    t0 = time.perf_counter()
    forest = IsolationForest(n_estimators=100, random_state=seed, n_jobs=1).fit(train_windows)
    fit_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    scores = -forest.score_samples(Xw)
    score_s = time.perf_counter() - t0
    c0, c1 = k_shot, min(len(Xw), k_shot + calib_len)
    tau = pot_threshold(scores[c0:c1], pot_q, pot_level)
    return {
        "config": {"name": "IF"},
        "scores": scores,
        "alarms": scores > tau,
        "tau": np.full(len(Xw), tau),
        "eval_start": c1,
        "drift_events": [], "adapt_events": [], "recal_events": [],
        "memory_regimes": 0, "memory_bytes": 0,
        "timings": {"score_s": score_s, "adapt_s": fit_s, "meta_update_s": 0.0, "n_adapt": 1, "n_meta_update": 0},
        "n_params": 0,
    }
