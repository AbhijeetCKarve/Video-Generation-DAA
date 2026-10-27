"""Regime-indexed memory buffer (Module 3).

One entry per regime the detector has lived through: a short raw segment
that stands in for the regime, its first- and second-moment summary and
the threshold that was in force.  The meta-update draws replay episodes
from these entries so that the meta-initialisation does not drift away
from regimes it has already seen.  Storage is one segment per regime,
not one record per observation, which keeps the buffer small.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np

from ..data.tasks import Regime


@dataclass
class RegimeEntry:
    regime_id: int
    segment: np.ndarray        # (L, d) raw standardised steps
    mean: np.ndarray           # (d,)
    var: np.ndarray            # (d,)
    tau: float
    t_start: int
    t_end: int

    def as_regime(self) -> Regime:
        return Regime(f"mem{self.regime_id}", self.segment, self.t_start)

    @property
    def nbytes(self) -> int:
        return int(self.segment.nbytes + self.mean.nbytes + self.var.nbytes)


class RegimeMemory:
    def __init__(self, capacity: int = 8, segment_len: int = 300, replay_k: int = 3, seed: int = 0):
        self.capacity = capacity
        self.segment_len = segment_len
        self.replay_k = replay_k
        self.entries: List[RegimeEntry] = []
        self.rng = np.random.default_rng(seed)
        self._next_id = 0

    def add(self, X_segment: np.ndarray, tau: float, t_start: int, t_end: int) -> RegimeEntry:
        seg = np.asarray(X_segment, dtype=np.float32)
        if len(seg) > self.segment_len:
            seg = seg[-self.segment_len:]
        e = RegimeEntry(self._next_id, seg, seg.mean(0), seg.var(0), float(tau), t_start, t_end)
        self._next_id += 1
        self.entries.append(e)
        if len(self.entries) > self.capacity:
            self.entries.pop(0)            # oldest regime leaves first
        return e

    def sample(self, current: np.ndarray) -> List[Regime]:
        """Regimes for a meta-update: the current one plus up to replay_k
        past regimes, weighted towards those whose summary is closest to
        the current segment (operational similarity) with a recency
        bonus."""
        out = [Regime("current", np.asarray(current, dtype=np.float32), 0)]
        if not self.entries:
            return out
        cur_mean = current.mean(0)
        dists = np.array([np.linalg.norm(e.mean - cur_mean) for e in self.entries])
        rec = np.arange(len(self.entries), 0, -1)          # 1 = newest
        w = np.exp(-dists / (dists.mean() + 1e-6)) + 0.5 / rec
        w = w / w.sum()
        k = min(self.replay_k, len(self.entries))
        idx = self.rng.choice(len(self.entries), size=k, replace=False, p=w)
        out.extend(self.entries[i].as_regime() for i in idx)
        return out

    def __len__(self) -> int:
        return len(self.entries)

    @property
    def nbytes(self) -> int:
        return sum(e.nbytes for e in self.entries)
