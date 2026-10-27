"""Offline meta-learning study: LSTM-AE + corrected FOMAML, run through
the DAMAD harness (loaders, point-wise metrics, POT threshold, seeds).

Two kinds of job:

  within   one (dataset, seed): regimes or channels as tasks, static
           and meta-trained LSTM-AEs, MLP-AE and Isolation Forest, K-shot
           evaluation on the held-out streams at K in {1, 5, 20, 100},
           adaptation-effect measurements, task-diversity scores.
  transfer one (source plant, target plant, seed): PCA-32 bridge, model
           meta-trained or statically trained on the source, adapted on
           K target windows, scored on the target attack stream; a
           target-trained reference and a from-scratch control.

    python experiments/obj2/run_obj2.py --workers 4
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
import traceback
from multiprocessing import get_context
from pathlib import Path
from typing import Dict, List

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from damad.data.cache import load_cached                                  # noqa: E402
from damad.data.loaders import meta_split                                 # noqa: E402
from damad.data.regimes import build_regimes, regime_windows, split_regimes  # noqa: E402
from damad.eval.metrics import evaluate                                   # noqa: E402
from damad.models.fomaml import FOMAMLConfig, inner_adapt, meta_train, train_static  # noqa: E402
from damad.models.lstm_ae import LSTMAE, MLPAE, n_params, param_vector    # noqa: E402
from damad.online.threshold import pot_threshold                          # noqa: E402

L = 30
PLANTS = ["swat", "wadi", "hai"]
NASA = ["smap", "msl"]
SHOTS = [1, 5, 20, 100]
CALIB = {"swat": 300, "wadi": 300, "hai": 300, "smap": 200, "msl": 200}
# adaptation settings: the draft's (10 SGD steps at 0.01), the one the
# meta-learner was trained for (5 steps at 0.1) and a heavy one
ADAPT = {"draft": (10, 0.01), "matched": (5, 0.1), "heavy": (50, 0.1)}
DRAFT_ONLY = {"Static-AE+FT", "MAML-AE"}      # the draft setting is scored for these two only
OUT = ROOT / "results" / "obj2"


def windows3d(X: np.ndarray, stride: int = 1) -> np.ndarray:
    T = len(X)
    if T < L:
        return np.empty((0, L, X.shape[1]), np.float32)
    n = (T - L) // stride + 1
    idx = np.arange(L)[None, :] + stride * np.arange(n)[:, None]
    return X[idx].astype(np.float32)


def labels_last(y: np.ndarray) -> np.ndarray:
    return y[L - 1:]


def jsonable(d: Dict) -> Dict:
    o = {}
    for k, v in d.items():
        if isinstance(v, (np.floating, np.integer)):
            v = v.item()
        if isinstance(v, float) and not np.isfinite(v):
            v = None
        o[k] = v
    return o


# ----------------------------------------------------------------- scoring
def score_stream(model, Xw: np.ndarray, torch) -> np.ndarray:
    return model.score(torch.as_tensor(Xw)).numpy().astype(np.float64)


def evaluate_scores(scores: np.ndarray, yw: np.ndarray, K: int, calib: int) -> Dict:
    c0, c1 = K, min(len(scores), K + calib)
    tau = pot_threshold(scores[c0:c1], 1e-2, 0.98)
    res = {"scores": scores, "alarms": scores > tau, "tau": np.full(len(scores), tau), "eval_start": c1,
           "drift_events": [], "adapt_events": [], "recal_events": [], "memory_regimes": 0, "memory_bytes": 0,
           "timings": {"score_s": 0.0, "adapt_s": 0.0, "meta_update_s": 0.0, "n_adapt": 1, "n_meta_update": 0},
           "n_params": 0}
    m = evaluate(res, yw)
    y, s = yw[c1:], scores[c1:]
    if (y == 1).any() and (y == 0).any():
        m["separation"] = float(s[y == 1].mean() / max(s[y == 0].mean(), 1e-12))
    else:
        m["separation"] = float("nan")
    m["tau"] = float(tau)
    return m


def adaptation_effect(base, adapted, s0: np.ndarray, s1: np.ndarray, start: int) -> Dict:
    """How much did K-step adaptation change the model and its ranking?
    `s0`/`s1` are the full-stream scores before/after adaptation; only the
    evaluation part (from `start`) is compared."""
    from scipy.stats import spearmanr
    v0, v1 = param_vector(base), param_vector(adapted)
    rel = float((v1 - v0).norm() / max(float(v0.norm()), 1e-12))
    a, b = s0[start:], s1[start:]
    rho = float(spearmanr(a, b).correlation) if len(a) > 10 else float("nan")
    return {"rel_param_change": rel, "score_spearman": rho, "score_mean_ratio": float(b.mean() / max(a.mean(), 1e-12))}


def adapted_runs(bases: Dict[str, object], S, Xw: np.ndarray, base_scores: Dict[str, np.ndarray], start: int,
                 torch, settings=ADAPT) -> List[tuple]:
    """(method, setting, scores, effect) for every adapting method and
    adaptation setting."""
    out = []
    for setting, (steps, lr) in settings.items():
        for name, base in bases.items():
            if setting == "draft" and name not in DRAFT_ONLY:
                continue
            a = inner_adapt(base, S, steps, lr)
            sc = score_stream(a, Xw, torch)
            out.append((name, setting, sc, adaptation_effect(base, a, base_scores[name], sc, start)))
    return out


# ------------------------------------------------------------ task samplers
def make_sampler(groups: List[np.ndarray], cfg: FOMAMLConfig, torch):
    def sample(rng):
        g = groups[rng.integers(len(groups))]
        need = cfg.support + cfg.query
        if len(g) >= need:
            idx = rng.permutation(len(g))[:need]
        else:
            idx = rng.choice(len(g), need, replace=True)
        S, Q = g[idx[:cfg.support]], g[idx[cfg.support:]]
        return torch.as_tensor(S), torch.as_tensor(Q)
    return sample


def make_val(groups: List[np.ndarray], cfg: FOMAMLConfig, torch, seed: int):
    rng = np.random.default_rng(seed + 999)
    sample = make_sampler(groups, cfg, torch)
    fixed = [sample(rng) for _ in range(4)]

    def val():
        S = torch.cat([f[0] for f in fixed])[: cfg.support]
        Q = torch.cat([f[1] for f in fixed])
        return S, Q
    return val


# ------------------------------------------------------------------ within
def run_within(dataset: str, seed: int, quick: bool) -> str:
    import torch
    torch.set_num_threads(1)
    t0 = time.time()
    log = lambda *a: print(f"[{dataset} s{seed} {time.time() - t0:5.0f}s]", *a, flush=True)  # noqa: E731
    ents = load_cached(dataset)
    split = meta_split(ents, seed)
    mt, ho = split["meta_train"], split["held_out"]
    if quick:
        ho = ho[:2]
    d = ents[0].d
    rng = np.random.default_rng(seed)
    outer = 60 if quick else 600
    static_steps = 200 if quick else 2000
    fcfg = FOMAMLConfig(outer_steps=outer)
    meta: Dict = {"dataset": dataset, "seed": seed, "n_meta_train": len(mt), "n_held_out": len(ho), "d": d}

    # ---- training windows and tasks
    if dataset in PLANTS:
        streams = getattr(mt[0], "train_segments", None) or [mt[0].X_train]
        pooled = np.concatenate([windows3d(s, stride=5) for s in streams])
        if len(pooled) > 20000:
            pooled = pooled[rng.choice(len(pooled), 20000, replace=False)]
        regs = build_regimes(pooled, seed)
        groups = regime_windows(pooled, regs)
        train_groups, val_groups = split_regimes(groups, seed)
        meta.update({"regime_k": regs.k, "silhouette": regs.silhouette, "silhouette_curve": regs.curve,
                     "regime_sizes": regs.sizes, "n_train_regimes": len(train_groups), "n_val_regimes": len(val_groups)})
        log(f"pooled {pooled.shape}; {regs.k} regimes, silhouette {regs.silhouette:.3f}")
    else:
        chans = [windows3d(e.X_train, stride=2) for e in mt]
        chans = [c for c in chans if len(c) >= 40]
        pooled = np.concatenate(chans)
        if len(pooled) > 20000:
            pooled = pooled[rng.choice(len(pooled), 20000, replace=False)]
        train_groups, val_groups = split_regimes(chans, seed)
        # per-channel diversity: silhouette of each channel's own windows
        per_chan = {}
        for e in mt + ho:
            w = windows3d(e.X_train, stride=2)
            if len(w) >= 60:
                r = build_regimes(w, seed, k_range=(2, 6), max_fit=2000)
                per_chan[e.name] = {"silhouette": r.silhouette, "k": r.k}
        regs_all = build_regimes(pooled, seed)
        meta.update({"silhouette": regs_all.silhouette, "regime_k": regs_all.k, "per_channel": per_chan,
                     "n_train_regimes": len(train_groups), "n_val_regimes": len(val_groups)})
        log(f"{len(chans)} channel tasks; pooled silhouette {regs_all.silhouette:.3f}")

    # ---- models
    torch.manual_seed(seed)
    static = LSTMAE(d, L)
    h = train_static(static, pooled, static_steps, seed)
    meta["static_best_val"] = h["best_val"]
    log(f"static LSTM-AE trained (val {h['best_val']:.4f}, {n_params(static)} params)")
    torch.manual_seed(seed)
    mlp = MLPAE(d, L)
    h = train_static(mlp, pooled, static_steps, seed)
    log(f"static MLP-AE trained (val {h['best_val']:.4f})")
    torch.manual_seed(seed)
    init = LSTMAE(d, L)
    init_state = copy.deepcopy(init.state_dict())
    sampler = make_sampler(train_groups, fcfg, torch)
    val = make_val(val_groups or train_groups, fcfg, torch, seed)
    maml = LSTMAE(d, L)
    maml.load_state_dict(init_state)
    hist = meta_train(maml, sampler, fcfg, seed, val_task=val, log_every=100)
    meta["maml_hist"] = {"loss": hist["loss"][::10], "val": hist["val"], "step": hist["step"],
                         "param_change_mean": float(np.mean(hist["param_change"])),
                         "param_change_zero_frac": float(np.mean(np.array(hist["param_change"]) == 0.0)),
                         "best_val": hist["best_val"]}
    log(f"FOMAML meta-trained: val {hist['best_val']:.4f}, mean |dtheta| {meta['maml_hist']['param_change_mean']:.2e}")
    broken = LSTMAE(d, L)
    broken.load_state_dict(init_state)
    bcfg = FOMAMLConfig(outer_steps=min(100, outer), broken=True)
    bh = meta_train(broken, sampler, bcfg, seed, val_task=val, log_every=50)
    meta["broken_hist"] = {"val": bh["val"], "step": bh["step"],
                           "param_change_mean": float(np.mean(bh["param_change"])),
                           "param_change_zero_frac": float(np.mean(np.array(bh["param_change"]) == 0.0)),
                           "max_abs_param_diff_from_init": float(max((p - init_state[k]).abs().max().item() for k, p in broken.state_dict().items()))}
    log(f"broken FOMAML control: mean |dtheta| {meta['broken_hist']['param_change_mean']:.2e}, "
        f"zero-change fraction {meta['broken_hist']['param_change_zero_frac']:.2f}")

    from sklearn.ensemble import IsolationForest
    flat = pooled.reshape(len(pooled), -1)
    if len(flat) > 10000:
        flat = flat[rng.choice(len(flat), 10000, replace=False)]
    forest = IsolationForest(n_estimators=100, random_state=seed, n_jobs=1).fit(flat)

    # ---- evaluation
    OUT.mkdir(parents=True, exist_ok=True)
    fout = open(OUT / f"within_{dataset}.jsonl", "a")
    n = 0
    for ent in ho:
        Xw = windows3d(ent.X_test)
        yw = labels_last(ent.y_test)
        calib = CALIB[dataset]
        torch.manual_seed(seed + 7)
        fresh = LSTMAE(d, L)
        bases = {"Static-AE+FT": static, "MAML-AE": maml, "MAML-AE-broken": broken, "Scratch": fresh}
        base_scores = {"Static-AE+FT": score_stream(static, Xw, torch), "MAML-AE": score_stream(maml, Xw, torch),
                       "MAML-AE-broken": score_stream(broken, Xw, torch), "Scratch": score_stream(fresh, Xw, torch)}
        s_mlp = score_stream(mlp, Xw, torch)
        s_if = -forest.score_samples(Xw.reshape(len(Xw), -1)).astype(np.float64)
        for K in SHOTS:
            if K + calib + 50 >= len(Xw):
                continue
            S = torch.as_tensor(Xw[:K])
            start = K + calib
            # non-adapting methods: identical scores at every K, threshold calibrated after the K support windows
            runs = [("Static-AE", "none", base_scores["Static-AE+FT"], None), ("MLP-AE", "none", s_mlp, None),
                    ("IsoForest", "none", s_if, None), ("MAML-AE-noadapt", "none", base_scores["MAML-AE"], None),
                    ("Scratch-noadapt", "none", base_scores["Scratch"], None)]
            ta = time.perf_counter()
            runs += adapted_runs(bases, S, Xw, base_scores, start, torch)
            adapt_s = time.perf_counter() - ta
            for name, setting, sc, eff in runs:
                try:
                    m = evaluate_scores(sc, yw, K, calib)
                    rec = {"dataset": dataset, "seed": seed, "entity": ent.name, "method": name, "adapt": setting,
                           "k_shot": K, "T": int(len(Xw)), "adapt_s_total": adapt_s, **m}
                    if eff:
                        rec.update(eff)
                    fout.write(json.dumps(jsonable(rec)) + "\n")
                    n += 1
                except Exception:  # noqa: BLE001
                    log(f"FAILED {ent.name} {name} K={K}\n{traceback.format_exc()}")
            fout.flush()
        log(f"{ent.name}: done ({n} rows)")
    fout.close()
    with open(OUT / f"meta_{dataset}_s{seed}.json", "w") as f:
        json.dump(meta, f, default=float)
    return f"within {dataset} seed {seed}: {n} rows in {time.time() - t0:.0f}s"


# ---------------------------------------------------------------- transfer
def pca_bridge(X_normal: np.ndarray, n: int = 32):
    from sklearn.decomposition import PCA
    pca = PCA(n_components=min(n, X_normal.shape[1]), random_state=0).fit(X_normal)
    Z = pca.transform(X_normal)
    lo, hi = Z.min(0), Z.max(0)
    span = np.where(hi - lo < 1e-9, 1.0, hi - lo)

    def proj(X):
        return np.clip((pca.transform(X) - lo) / span, -1.0, 2.0).astype(np.float32)
    return proj, float(pca.explained_variance_ratio_.sum())


def plant_stream(dataset: str):
    ents = load_cached(dataset)
    e = ents[0]
    segs = getattr(e, "train_segments", None) or [e.X_train]
    normal = np.concatenate(segs)
    tests = [(x.name, x.X_test, x.y_test) for x in ents]
    return normal, tests


def run_transfer(src: str, tgt: str, seed: int, quick: bool) -> str:
    import torch
    torch.set_num_threads(1)
    t0 = time.time()
    log = lambda *a: print(f"[{src}->{tgt} s{seed} {time.time() - t0:5.0f}s]", *a, flush=True)  # noqa: E731
    rng = np.random.default_rng(seed)
    outer = 60 if quick else 600
    static_steps = 200 if quick else 2000
    s_normal, _ = plant_stream(src)
    t_normal, t_tests = plant_stream(tgt)
    proj_s, var_s = pca_bridge(s_normal)
    proj_t, var_t = pca_bridge(t_normal)
    Zs = windows3d(proj_s(s_normal), stride=5)
    Zt = windows3d(proj_t(t_normal), stride=5)
    if len(Zs) > 20000:
        Zs = Zs[rng.choice(len(Zs), 20000, replace=False)]
    if len(Zt) > 20000:
        Zt = Zt[rng.choice(len(Zt), 20000, replace=False)]
    regs = build_regimes(Zs, seed)
    train_groups, val_groups = split_regimes(regime_windows(Zs, regs), seed)
    fcfg = FOMAMLConfig(outer_steps=outer)
    d = Zs.shape[2]
    torch.manual_seed(seed)
    maml = LSTMAE(d, L)
    hist = meta_train(maml, make_sampler(train_groups, fcfg, torch), fcfg, seed,
                      val_task=make_val(val_groups or train_groups, fcfg, torch, seed), log_every=100)
    torch.manual_seed(seed)
    static_src = LSTMAE(d, L)
    train_static(static_src, Zs, static_steps, seed)
    torch.manual_seed(seed)
    static_tgt = LSTMAE(d, L)
    train_static(static_tgt, Zt, static_steps, seed)
    log(f"trained: source regimes {regs.k} (sil {regs.silhouette:.3f}); PCA var {var_s:.3f}/{var_t:.3f}")
    OUT.mkdir(parents=True, exist_ok=True)
    fout = open(OUT / "transfer.jsonl", "a")
    n = 0
    for name, Xtest, ytest in t_tests:
        Xw = windows3d(proj_t(Xtest))
        yw = labels_last(ytest)
        calib = CALIB[tgt]
        torch.manual_seed(seed + 7)
        fresh = LSTMAE(d, L)
        bases = {"MAML-transfer": maml, "Static-transfer": static_src, "Scratch": fresh}
        base_scores = {"MAML-transfer": score_stream(maml, Xw, torch), "Static-transfer": score_stream(static_src, Xw, torch),
                       "Scratch": score_stream(fresh, Xw, torch)}
        s_tgt = score_stream(static_tgt, Xw, torch)
        settings = {k: v for k, v in ADAPT.items() if k != "draft"}
        for K in ([20] if quick else [20, 100]):
            if K + calib + 50 >= len(Xw):
                continue
            S = torch.as_tensor(Xw[:K])
            start = K + calib
            runs = [("Target-static", "none", s_tgt, None), ("Source-static-noadapt", "none", base_scores["Static-transfer"], None),
                    ("MAML-transfer-noadapt", "none", base_scores["MAML-transfer"], None)]
            runs += adapted_runs(bases, S, Xw, base_scores, start, torch, settings)
            for mname, setting, sc, eff in runs:
                m = evaluate_scores(sc, yw, K, calib)
                rec = {"source": src, "target": tgt, "seed": seed, "entity": name, "method": mname, "adapt": setting,
                       "k_shot": K, "pca_var_source": var_s, "pca_var_target": var_t, "source_silhouette": regs.silhouette,
                       "maml_best_val": hist["best_val"], **m}
                if eff:
                    rec.update(eff)
                fout.write(json.dumps(jsonable(rec)) + "\n")
                n += 1
        fout.flush()
    fout.close()
    return f"transfer {src}->{tgt} seed {seed}: {n} rows in {time.time() - t0:.0f}s"


def _star(job):
    kind, args = job
    try:
        return run_within(*args) if kind == "within" else run_transfer(*args)
    except Exception:  # noqa: BLE001
        return f"JOB FAILED {job}:\n{traceback.format_exc()}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", default=",".join(PLANTS + NASA))
    ap.add_argument("--seeds", default="0,1,2,3,4")
    ap.add_argument("--transfer", default="1")
    ap.add_argument("--within", default="1")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(",")]
    jobs = []
    if a.within == "1":
        jobs += [("within", (d, s, a.quick)) for d in a.datasets.split(",") for s in seeds]
    if a.transfer == "1":
        plants = [p for p in PLANTS if p in a.datasets.split(",")]
        jobs += [("transfer", (s_, t_, s, a.quick)) for s_ in plants for t_ in plants if s_ != t_ for s in seeds]
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    if a.workers == 1:
        for j in jobs:
            print(_star(j), flush=True)
        return
    with get_context("spawn").Pool(a.workers) as pool:
        for msg in pool.imap_unordered(_star, jobs):
            print(msg, flush=True)


if __name__ == "__main__":
    main()
