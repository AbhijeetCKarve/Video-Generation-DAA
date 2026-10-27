"""ADWIN (Bifet & Gavaldà, 2007), exponential-histogram version.

The detector keeps a variable-length window of recent values.  When the
means of two sub-windows differ by more than a bound derived from the
Hoeffding/Bernstein inequality, the older part is dropped and a change
is reported.  Memory is O(M log n) because values are grouped into
buckets of size 2^i, at most M+1 per row.
"""
from __future__ import annotations

import math
from typing import List


class _Bucket:
    __slots__ = ("n", "s", "ss")

    def __init__(self, n: float, s: float, ss: float):
        self.n, self.s, self.ss = n, s, ss


class ADWIN:
    def __init__(self, delta: float = 0.002, max_buckets: int = 5, clock: int = 32, min_window: int = 10):
        self.delta = delta
        self.M = max_buckets
        self.clock = clock
        self.min_window = min_window
        self.reset()

    def reset(self) -> None:
        self.rows: List[List[_Bucket]] = [[]]      # rows[i] holds buckets of 2^i elements, oldest first
        self.n = 0
        self.total = 0.0
        self.total_sq = 0.0
        self.t = 0
        self.last_change = -1
        self.last_direction = 0      # +1 if the retained (newer) window has the higher mean

    # ------------------------------------------------------------ internals
    def _insert(self, x: float) -> None:
        self.rows[0].append(_Bucket(1.0, x, x * x))
        self.n += 1
        self.total += x
        self.total_sq += x * x
        self._compress()

    def _compress(self) -> None:
        i = 0
        while i < len(self.rows):
            row = self.rows[i]
            if len(row) <= self.M:
                break
            a, b = row[0], row[1]
            merged = _Bucket(a.n + b.n, a.s + b.s, a.ss + b.ss)
            del row[:2]
            if i + 1 == len(self.rows):
                self.rows.append([])
            self.rows[i + 1].append(merged)
            i += 1

    def _drop_oldest(self) -> None:
        for i in range(len(self.rows) - 1, -1, -1):
            if self.rows[i]:
                b = self.rows[i].pop(0)
                self.n -= b.n
                self.total -= b.s
                self.total_sq -= b.ss
                break
        while len(self.rows) > 1 and not self.rows[-1]:
            self.rows.pop()

    @property
    def mean(self) -> float:
        return self.total / self.n if self.n else 0.0

    @property
    def variance(self) -> float:
        if self.n < 2:
            return 0.0
        m = self.mean
        return max(self.total_sq / self.n - m * m, 0.0)

    def _detect(self) -> bool:
        """Scan every bucket boundary from oldest to newest."""
        changed = False
        var = self.variance
        while True:
            cut = False
            n0 = s0 = 0.0
            n1, s1 = self.n, self.total
            # iterate buckets oldest -> newest: largest row first, oldest bucket first
            buckets = [b for i in range(len(self.rows) - 1, -1, -1) for b in self.rows[i]]
            for b in buckets[:-1]:
                n0 += b.n
                s0 += b.s
                n1 -= b.n
                s1 -= b.s
                if n0 < self.min_window or n1 < self.min_window:
                    continue
                m = 1.0 / (1.0 / n0 + 1.0 / n1)
                dd = math.log(2.0 * math.log(max(self.n, 2)) / self.delta)
                eps = math.sqrt(2.0 * var * dd / m) + 2.0 * dd / (3.0 * m)
                if abs(s0 / n0 - s1 / n1) > eps:
                    cut = True
                    break
            if cut and self.n > self.min_window:
                mean_before = self.mean
                self._drop_oldest()
                self.last_direction = 1 if self.mean > mean_before else -1
                changed = True
                continue
            break
        return changed

    # --------------------------------------------------------------- public
    def update(self, x: float) -> bool:
        """Feed one value.  Returns True when a change was detected."""
        self.t += 1
        self._insert(float(x))
        if self.t % self.clock != 0 or self.n < 2 * self.min_window:
            return False
        if self._detect():
            self.last_change = self.t
            return True
        return False

    @property
    def width(self) -> int:
        return int(self.n)
