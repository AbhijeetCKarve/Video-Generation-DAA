"""The streaming detector.

One loop serves DAMAD, every baseline and every ablation; what differs
is the configuration.  The loop sees one window at a time and never
looks ahead, so detection latency and adaptation delay are real.

States
------
steady   score, compare with tau, feed the drift detectors
collect  a regime change has been confirmed; wait for K post-change
         windows to form the support set, then adapt
calib    scoring with the adapted model; after calib_len windows the
         threshold is recalibrated (if enabled), the memory buffer is
         updated and a replay meta-update refreshes theta* (if enabled)
"""
from __future__ import annotations

import time
from collections import OrderedDict, deque
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

import numpy as np
import torch

from ..models import vae
from ..models.meta import MetaLearner
from .adwin import ADWIN
from .memory import RegimeMemory
from .mmd import MMDDetector
from .threshold import GatedThreshold


@dataclass
class OnlineConfig:
    name: str = "damad"
    init: str = "meta"                 # meta | static
    adapt_on_start: bool = True        # few-shot adaptation on the first K windows
    drift_policy: str = "meta_adapt"   # none | incremental | finetune | meta_adapt | reset
    detector: str = "adwin+mmd"        # none | adwin | mmd | adwin+mmd
    confirm: int = 2                   # ADWIN alarms needed inside confirm_horizon
    confirm_horizon: int = 160
    replay: bool = True
    recalibrate: bool = True
    k_shot: int = 5
    adapt_steps: int = 3
    finetune_steps: int = 30
    finetune_lr: float = 1e-3
    calib_len: int = 300
    adwin_delta: float = 1e-3
    adwin_block: int = 10
    adwin_min_shift: float = 0.5
    mmd_margin: float = 1.5
    accept_test: bool = True           # champion/challenger check after every adaptation
    accept_margin: float = 0.1         # revert only if the old model is better by this much (log units)
    adwin_confirm: int = 1             # ADWIN hits needed inside confirm_horizon
    shadow_len: int = 600              # how long the previous model keeps scoring in the shadow
    shadow_check: int = 50
    meta_update_iters: int = 10
    refractory: int = 400
    inc_lr: float = 1e-4
    inc_every: int = 1
    inc_batch: int = 32
    memory_capacity: int = 8
    memory_segment: int = 300
    replay_k: int = 3
    pot_q: float = 1e-2
    pot_level: float = 0.98


class ResidualADWIN:
    """ADWIN over block means of the log reconstruction residual.

    Blocks of `block` steps damp short anomaly bursts; only changes where
    the retained (newer) window has the *higher* mean count, because a
    model that fits better than before needs no adaptation.  This is the
    primary gate of Module 1.  The paper's original sketch watched the
    raw input; on real streams the input never stops moving while the
    residual only moves when the fit breaks, so the residual is the
    right thing to watch (Section 6.3 of the manuscript)."""

    def __init__(self, delta: float, block: int = 10, min_shift: float = 0.5):
        self.det = ADWIN(delta=delta, clock=1, min_window=5)
        self.block = block
        self.min_shift = min_shift     # log-residual units; 0.5 is a 65 % rise in residual
        self.buf: List[float] = []
        self.ref_mean: Optional[float] = None

    def reset(self) -> None:
        self.det.reset()
        self.buf.clear()
        self.ref_mean = None

    def update(self, score: float) -> bool:
        self.buf.append(np.log(score + 1e-6))
        if len(self.buf) < self.block:
            return False
        v = float(np.mean(self.buf))
        self.buf.clear()
        before = self.det.mean
        changed = self.det.update(v)
        if self.ref_mean is None and self.det.width >= 10:
            self.ref_mean = before
        if not changed or self.det.last_direction <= 0:
            return False
        # statistically a change, but is it big enough to matter?
        base = self.ref_mean if self.ref_mean is not None else before
        return (self.det.mean - base) >= self.min_shift


@torch.no_grad()
def _score_embed(p, x: torch.Tensor):
    mu, _ = vae.encode(p, x)
    xr = vae.decode(p, mu)
    return float(((xr - x) ** 2).mean()), mu[0].numpy()


def _finetune(p0, S: np.ndarray, steps: int, lr: float, beta: float) -> "OrderedDict[str, torch.Tensor]":
    p = vae.clone(p0)
    opt = torch.optim.Adam(list(p.values()), lr=lr)
    S = torch.as_tensor(S)
    for _ in range(steps):
        opt.zero_grad()
        vae.loss(p, S, beta).backward()
        opt.step()
    return OrderedDict((k, v.detach()) for k, v in p.items())


class StreamingDetector:
    def __init__(self, cfg: OnlineConfig, W: int, meta: Optional[MetaLearner] = None,
                 static_params=None, seed: int = 0, beta: float = 0.1):
        self.cfg = cfg
        self.W = W
        self.meta = meta
        self.static = static_params
        self.seed = seed
        self.beta = beta
        if cfg.init == "meta" and meta is None:
            raise ValueError("meta init requested without a meta-learner")
        if cfg.init == "static" and static_params is None:
            raise ValueError("static init requested without static parameters")

    def _meta_update(self, cfg, memory, X_raw, collect_start, t, W, K, timings) -> None:
        """Replay meta-update of theta* from the current regime plus a few
        remembered ones (Module 3)."""
        if cfg.drift_policy != "meta_adapt" or not cfg.replay or self.meta is None:
            return
        tm = time.perf_counter()
        cur = X_raw[collect_start:t + W]
        regimes = memory.sample(cur)
        self.meta.meta_train(regimes, W, iters=cfg.meta_update_iters, k_shot=K)
        timings["meta_update_s"] += time.perf_counter() - tm
        timings["n_meta_update"] += 1

    # --------------------------------------------------------------- run
    def run(self, Xw: np.ndarray, X_raw: np.ndarray) -> Dict:
        cfg, W = self.cfg, self.W
        N = len(Xw)
        K = cfg.k_shot
        Xt = torch.as_tensor(Xw)
        scores = np.zeros(N, dtype=np.float64)
        alarms = np.zeros(N, dtype=bool)
        tau_trace = np.full(N, np.inf)
        drift_events: List[int] = []
        drift_sources: List[str] = []
        adapt_events: List[int] = []
        recal_events: List[int] = []
        rejected_events: List[int] = []
        trace: List[tuple] = []                 # (t, what, detail) for debugging and figures
        timings = {"score_s": 0.0, "adapt_s": 0.0, "meta_update_s": 0.0, "n_adapt": 0, "n_meta_update": 0}

        theta_star = self.meta.theta if self.meta is not None else None

        # ---- initial model
        t0 = time.perf_counter()
        if cfg.init == "meta":
            if cfg.adapt_on_start:
                p = self.meta.adapt(Xw[:K], cfg.adapt_steps)
            else:
                p = OrderedDict((k, v.detach()) for k, v in theta_star.items())
        else:
            p = OrderedDict((k, v.detach()) for k, v in self.static.items())
            if cfg.adapt_on_start and cfg.drift_policy == "finetune":
                p = _finetune(p, Xw[:K], cfg.finetune_steps, cfg.finetune_lr, self.beta)
        timings["adapt_s"] += time.perf_counter() - t0
        timings["n_adapt"] += 1

        # ---- initial calibration on the windows after the support set
        thr = GatedThreshold(cfg.pot_q, cfg.pot_level)
        c0, c1 = K, min(N, K + cfg.calib_len)
        with torch.no_grad():
            mu, _ = vae.encode(p, Xt[c0:c1])
            xr = vae.decode(p, mu)
            calib_scores = ((xr - Xt[c0:c1]) ** 2).mean(1).numpy()
            calib_emb = mu.numpy()
        thr.calibrate(calib_scores)
        eval_start = c1

        # ---- drift detectors
        use_adwin = cfg.detector in ("adwin", "adwin+mmd") and cfg.drift_policy in ("finetune", "meta_adapt", "reset")
        use_mmd = cfg.detector in ("mmd", "adwin+mmd") and cfg.drift_policy in ("finetune", "meta_adapt", "reset")
        adwin = ResidualADWIN(cfg.adwin_delta, cfg.adwin_block, cfg.adwin_min_shift) if use_adwin else None
        mmd = MMDDetector(seed=self.seed, confirm=cfg.confirm, margin=cfg.mmd_margin) if use_mmd else None
        if mmd is not None:
            mmd.calibrate(calib_emb)
        adwin_hits: deque = deque()

        memory = RegimeMemory(cfg.memory_capacity, cfg.memory_segment, cfg.replay_k, seed=self.seed)
        regime_start = 0
        state = "steady"
        collect_start = calib_start = shadow_start = -1
        shadow_p = None
        shadow_tau = np.inf
        shadow_old: deque = deque(maxlen=100)
        shadow_new: deque = deque(maxlen=100)
        mem_entry = None
        prev_p, prev_tau = None, np.inf
        last_adapt = eval_start

        # incremental learner state
        inc_opt = None
        inc_buf: deque = deque(maxlen=cfg.inc_batch)
        if cfg.drift_policy == "incremental":
            p = vae.clone(p)
            inc_opt = torch.optim.Adam(list(p.values()), lr=cfg.inc_lr)

        for t in range(N):
            ts = time.perf_counter()
            s, z = _score_embed(p, Xt[t:t + 1])
            scores[t] = s
            alarm = s > thr.tau
            alarms[t] = alarm
            tau_trace[t] = thr.tau
            timings["score_s"] += time.perf_counter() - ts

            if t < eval_start:
                continue

            # --- incremental baseline: keep learning from non-alarmed windows
            if inc_opt is not None:
                if not alarm:
                    inc_buf.append(t)
                if t % cfg.inc_every == 0 and len(inc_buf) >= 4:
                    ta = time.perf_counter()
                    inc_opt.zero_grad()
                    vae.loss(p, Xt[list(inc_buf)], self.beta).backward()
                    inc_opt.step()
                    timings["adapt_s"] += time.perf_counter() - ta
                continue

            if cfg.drift_policy not in ("finetune", "meta_adapt", "reset"):
                continue

            # --- drift monitoring
            confirmed = False
            source = ""
            if adwin is not None and adwin.update(s):
                adwin_hits.append(t)
            while adwin_hits and adwin_hits[0] < t - cfg.confirm_horizon:
                adwin_hits.popleft()
            if adwin is not None and len(adwin_hits) >= cfg.adwin_confirm:
                confirmed = True
                source += "adwin"
            if mmd is not None and mmd.update(z):
                confirmed = True
                source += "mmd"

            if state == "steady":
                if confirmed and t - last_adapt >= cfg.refractory:
                    state = "collect"
                    collect_start = t
                    drift_events.append(t)
                    drift_sources.append(source)
                    trace.append((t, "trigger", source))
                    adwin_hits.clear()
                continue

            if state == "collect":
                if t - collect_start + 1 >= K:
                    S = Xw[t - K + 1:t + 1]
                    ta = time.perf_counter()
                    prev_p, prev_tau = p, thr.tau          # kept so that a bad adaptation can be undone
                    mem_entry = None
                    if cfg.drift_policy == "meta_adapt":
                        mem_entry = memory.add(X_raw[regime_start:collect_start + W - 1], thr.tau, regime_start, collect_start)
                        p = self.meta.adapt(S, cfg.adapt_steps, theta=theta_star)
                    elif cfg.drift_policy == "finetune":
                        p = _finetune(self.static, S, cfg.finetune_steps, cfg.finetune_lr, self.beta)
                    elif cfg.drift_policy == "reset":
                        p = _finetune(vae.init_params(Xw.shape[1], self.meta.cfg.hidden if self.meta else 128,
                                                      self.meta.cfg.latent if self.meta else 16, self.seed + t),
                                      S, cfg.finetune_steps * 4, cfg.finetune_lr, self.beta)
                    timings["adapt_s"] += time.perf_counter() - ta
                    timings["n_adapt"] += 1
                    adapt_events.append(t)
                    trace.append((t, "adapt", ""))
                    state = "calib"
                    calib_start = t + 1
                continue

            if state == "calib":
                if t - calib_start + 1 >= cfg.calib_len:
                    seg = slice(calib_start, t + 1)
                    # --- first acceptance check (SP3): adapting must have lowered
                    # the residual on the stretch that followed the change.
                    if cfg.accept_test:
                        with torch.no_grad():
                            r_old = vae.score(prev_p, Xt[seg]).numpy()
                        gain = float(np.median(np.log(r_old + 1e-6)) - np.median(np.log(scores[seg] + 1e-6)))
                        if gain < -cfg.accept_margin:
                            p, thr.tau = prev_p, prev_tau
                            if mem_entry is not None and mem_entry in memory.entries:
                                memory.entries.remove(mem_entry)
                            rejected_events.append(t)
                            trace.append((t, "reject_calib", f"gain={gain:.2f}"))
                            adwin.reset() if adwin is not None else None
                            if mmd is not None:
                                with torch.no_grad():
                                    mmd.calibrate(vae.encode(p, Xt[seg])[0].numpy())
                            last_adapt = t
                            state = "steady"
                            continue
                    if cfg.recalibrate:
                        thr.calibrate(scores[seg])
                        recal_events.append(t)
                        trace.append((t, "recal", f"tau={thr.tau:.3g}"))
                    with torch.no_grad():
                        emb = vae.encode(p, Xt[seg])[0].numpy()
                    if mmd is not None:
                        mmd.calibrate(emb)
                    if adwin is not None:
                        adwin.reset()
                    regime_start = collect_start
                    last_adapt = t
                    if cfg.accept_test:
                        # --- second check: the previous model keeps scoring in the
                        # shadow.  If the stream comes back to where the old model
                        # fits better, the trigger was an anomaly, not a regime
                        # change, and the adaptation is undone together with tau.
                        state = "shadow"
                        shadow_start = t
                        shadow_p, shadow_tau = prev_p, prev_tau
                        shadow_old.clear()
                        shadow_new.clear()
                    else:
                        self._meta_update(cfg, memory, X_raw, collect_start, t, W, K, timings)
                        theta_star = self.meta.theta if self.meta is not None else None
                        state = "steady"
                continue

            if state == "shadow":
                with torch.no_grad():
                    shadow_old.append(float(np.log(vae.score(shadow_p, Xt[t:t + 1]).item() + 1e-6)))
                shadow_new.append(float(np.log(s + 1e-6)))
                elapsed = t - shadow_start
                if elapsed % cfg.shadow_check == 0 and len(shadow_new) >= 50:
                    if np.median(shadow_old) + cfg.accept_margin < np.median(shadow_new):
                        trace.append((t, "reject_shadow", f"old={np.median(shadow_old):.2f} new={np.median(shadow_new):.2f}"))
                        p, thr.tau = shadow_p, shadow_tau
                        if mem_entry is not None and mem_entry in memory.entries:
                            memory.entries.remove(mem_entry)
                        rejected_events.append(t)
                        regime_start = memory.entries[-1].t_end if memory.entries else 0
                        if adwin is not None:
                            adwin.reset()
                        if mmd is not None:
                            with torch.no_grad():
                                seg = slice(max(0, t - cfg.calib_len), t + 1)
                                mmd.calibrate(vae.encode(p, Xt[seg])[0].numpy())
                        last_adapt = t
                        state = "steady"
                        continue
                if elapsed >= cfg.shadow_len:
                    trace.append((t, "accept", f"old={np.median(shadow_old):.2f} new={np.median(shadow_new):.2f}"))
                    self._meta_update(cfg, memory, X_raw, collect_start, t, W, K, timings)
                    theta_star = self.meta.theta if self.meta is not None else None
                    last_adapt = t
                    state = "steady"
                continue

        return {
            "config": asdict(cfg),
            "scores": scores,
            "alarms": alarms,
            "tau": tau_trace,
            "eval_start": eval_start,
            "drift_events": drift_events,
            "drift_sources": drift_sources,
            "adapt_events": adapt_events,
            "recal_events": recal_events,
            "rejected_events": rejected_events,
            "trace": trace,
            "memory_regimes": len(memory),
            "memory_bytes": memory.nbytes,
            "timings": timings,
            "n_params": vae.n_params(p),
        }
