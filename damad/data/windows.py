"""Sliding windows over multivariate streams."""
from __future__ import annotations

import numpy as np


def make_windows(X: np.ndarray, W: int, stride: int = 1) -> np.ndarray:
    """Return (N, W*d) flattened windows; window i ends at step i*stride+W-1."""
    T, d = X.shape
    if T < W:
        return np.empty((0, W * d), dtype=np.float32)
    n = (T - W) // stride + 1
    idx = np.arange(W)[None, :] + stride * np.arange(n)[:, None]
    return X[idx].reshape(n, W * d).astype(np.float32)


def window_labels(y: np.ndarray, W: int, stride: int = 1) -> np.ndarray:
    """Label of the window = label of its last step (point-wise scoring)."""
    T = len(y)
    n = (T - W) // stride + 1
    return y[W - 1 + stride * np.arange(n)]


def sample_windows(X: np.ndarray, W: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """n random windows (with replacement) from a stream segment."""
    T = len(X)
    if T < W:
        raise ValueError(f"segment of length {T} shorter than window {W}")
    starts = rng.integers(0, T - W + 1, size=n)
    idx = np.arange(W)[None, :] + starts[:, None]
    return X[idx].reshape(n, -1).astype(np.float32)
