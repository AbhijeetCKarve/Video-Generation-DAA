"""Evaluation metrics, all strictly point-wise.

No point-adjust is applied anywhere.  A window is scored by the label
of its last step.

  precision / recall / f1   at the method's own deployed threshold
  auroc / auprc             threshold-free, over the evaluated region
  best_f1                   the F1 an oracle threshold would reach
                            (reported for context only, never as the
                            headline number)
  detection_latency         steps from the start of each anomaly segment
                            to the first alarm inside it (detected
                            segments only) plus the fraction detected
  fpr_pre / fpr_drift       false-alarm rate on normal steps before the
                            first injected change point and after it
  adaptation_steps          steps after each change point until the
                            rolling false-alarm rate comes back to the
                            pre-drift level (plus a margin)
"""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score


def _segments(y: np.ndarray) -> List[tuple]:
    segs, start = [], None
    for i, v in enumerate(y):
        if v and start is None:
            start = i
        elif not v and start is not None:
            segs.append((start, i))
            start = None
    if start is not None:
        segs.append((start, len(y)))
    return segs


def prf(y: np.ndarray, a: np.ndarray) -> Dict[str, float]:
    tp = float(np.sum(a & (y == 1)))
    fp = float(np.sum(a & (y == 0)))
    fn = float(np.sum(~a & (y == 1)))
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"precision": p, "recall": r, "f1": f}


def best_f1(y: np.ndarray, s: np.ndarray, n_grid: int = 200) -> float:
    if y.sum() == 0 or y.sum() == len(y):
        return 0.0
    qs = np.unique(np.quantile(s, np.linspace(0.5, 0.999, n_grid)))
    return max(prf(y, s > q)["f1"] for q in qs)


def detection_latency(y: np.ndarray, a: np.ndarray) -> Dict[str, float]:
    segs = _segments(y)
    lat, hit = [], 0
    for s0, s1 in segs:
        idx = np.flatnonzero(a[s0:s1])
        if len(idx):
            hit += 1
            lat.append(int(idx[0]))
    return {
        "n_segments": len(segs),
        "segment_detection_rate": hit / len(segs) if segs else float("nan"),
        "latency_mean": float(np.mean(lat)) if lat else float("nan"),
        "latency_median": float(np.median(lat)) if lat else float("nan"),
    }


def rolling_rate(x: np.ndarray, w: int) -> np.ndarray:
    c = np.cumsum(np.insert(x.astype(float), 0, 0.0))
    out = np.full(len(x), np.nan)
    if len(x) >= w:
        out[w - 1:] = (c[w:] - c[:-w]) / w
    return out


def drift_metrics(y: np.ndarray, a: np.ndarray, regime: Optional[np.ndarray],
                  change_points: Optional[List[int]], window: int = 100, margin: float = 0.05) -> Dict[str, float]:
    out = {"fpr_pre": float("nan"), "fpr_drift": float("nan"), "adaptation_steps": float("nan"),
           "adaptation_recovered": float("nan")}
    normal = y == 0
    if regime is None or change_points is None or not change_points:
        if normal.any():
            out["fpr_pre"] = float(a[normal].mean())
        return out
    cps = sorted(c for c in change_points if 0 < c < len(y))
    pre = np.zeros(len(y), bool)
    pre[:cps[0]] = True
    post = ~pre
    if (pre & normal).any():
        out["fpr_pre"] = float(a[pre & normal].mean())
    if (post & normal).any():
        out["fpr_drift"] = float(a[post & normal].mean())
    base = out["fpr_pre"] if np.isfinite(out["fpr_pre"]) else 0.0
    steps, recovered = [], []
    fa = (a & normal).astype(float)
    for i, cp in enumerate(cps):
        end = cps[i + 1] if i + 1 < len(cps) else len(y)
        seg = fa[cp:end]
        if len(seg) < window:
            continue
        r = rolling_rate(seg, window)
        ok = np.flatnonzero(r <= base + margin)
        ok = ok[ok >= window - 1]
        if len(ok):
            steps.append(int(ok[0]))
            recovered.append(1.0)
        else:
            steps.append(len(seg))
            recovered.append(0.0)
    if steps:
        out["adaptation_steps"] = float(np.mean(steps))
        out["adaptation_recovered"] = float(np.mean(recovered))
    return out


def evaluate(result: Dict, y_w: np.ndarray, regime_w: Optional[np.ndarray] = None,
             change_points_w: Optional[List[int]] = None) -> Dict[str, float]:
    e0 = result["eval_start"]
    y = y_w[e0:].astype(int)
    a = result["alarms"][e0:].astype(bool)
    s = np.asarray(result["scores"][e0:], dtype=np.float64)
    finite = s[np.isfinite(s)]
    top = float(finite.max()) * 10.0 + 1.0 if len(finite) else 1.0
    s = np.nan_to_num(s, nan=top, posinf=top, neginf=0.0)
    m: Dict[str, float] = {}
    m.update(prf(y, a))
    if 0 < y.sum() < len(y):
        m["auroc"] = float(roc_auc_score(y, s))
        m["auprc"] = float(average_precision_score(y, s))
    else:
        m["auroc"] = m["auprc"] = float("nan")
    m["best_f1"] = best_f1(y, s)
    m.update(detection_latency(y, a))
    reg = None if regime_w is None else regime_w[e0:]
    cps = None if change_points_w is None else [c - e0 for c in change_points_w]
    m.update(drift_metrics(y, a, reg, cps))
    m["alarm_rate"] = float(a.mean())
    m["anomaly_rate"] = float(y.mean())
    m["n_eval"] = int(len(y))
    tm = result["timings"]
    m["ms_per_window"] = 1000.0 * tm["score_s"] / max(1, len(result["scores"]))
    m["adapt_s_total"] = tm["adapt_s"]
    m["meta_update_s_total"] = tm["meta_update_s"]
    m["n_adapt"] = tm["n_adapt"]
    m["n_meta_update"] = tm["n_meta_update"]
    m["n_drift_events"] = len(result["drift_events"])
    srcs = result.get("drift_sources", [])
    m["n_drift_adwin"] = sum("adwin" in x for x in srcs)
    m["n_drift_mmd"] = sum("mmd" in x for x in srcs)
    m["n_rejected"] = len(result.get("rejected_events", []))
    m["memory_bytes"] = result["memory_bytes"]
    m["n_params"] = result["n_params"]
    return m
