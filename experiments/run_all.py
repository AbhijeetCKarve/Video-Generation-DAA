"""Run the whole study.

    python experiments/run_all.py --datasets smd,skab,psm,hai --seeds 0,1,2,3,4 --workers 4

One job = one (dataset, seed).  Inside a job the meta-learners and the
static VAE are trained once and shared by every method, every held-out
entity and every drift condition.  Results are appended as JSON lines
to results/raw/<dataset>.jsonl; score traces for the figures go to
results/traces/.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
import traceback
from dataclasses import replace
from multiprocessing import get_context
from pathlib import Path
from typing import Dict, List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from damad.baselines.iforest import run_iforest            # noqa: E402
from damad.baselines.registry import METHODS, MethodSpec   # noqa: E402
from damad.data.cache import load_cached                   # noqa: E402
from damad.data.drift import DriftSpec, default_specs, inject_drift  # noqa: E402
from damad.data.loaders import meta_split                  # noqa: E402
from damad.data.tasks import build_regimes                 # noqa: E402
from damad.data.windows import make_windows, window_labels  # noqa: E402
from damad.eval.metrics import evaluate                    # noqa: E402
from damad.models.meta import MetaConfig, MetaLearner, pretrain_static  # noqa: E402
from damad.online.detector import StreamingDetector        # noqa: E402

W = 8
DATASET_OVERRIDES = {
    # short SKAB runs need a shorter warm-up and refractory period
    "skab": dict(calib_len=100, refractory=100, confirm_horizon=100, memory_segment=150, shadow_len=200),
    # NASA channels are 1k-9k windows long: shorter calibration and shadow periods
    "smap": dict(calib_len=200, refractory=300, memory_segment=200, shadow_len=400),
    "msl": dict(calib_len=200, refractory=300, memory_segment=200, shadow_len=400),
}
META_ITERS = {"smd": 400, "psm": 400, "hai": 400, "skab": 300, "swat": 400, "wadi": 400, "smap": 400, "msl": 400}
STATIC_ITERS = 1500
SHOT_SWEEP_METHODS = ["VAE-S", "VAE-FT", "MAML-1", "MSGD-1", "OML-A", "DAMAD"]
TRACE_METHODS = ["VAE-S", "VAE-INC", "VAE-DFT", "MAML-1", "OML-A", "DAMAD"]
DRIFTS = ["none", "sudden", "gradual", "incremental", "recurring"]


def jsonable(d: Dict) -> Dict:
    out = {}
    for k, v in d.items():
        if isinstance(v, (np.floating, np.integer)):
            v = v.item()
        if isinstance(v, float) and not np.isfinite(v):
            v = None
        out[k] = v
    return out


def stream_for(entity, drift: str, seed: int):
    X, y = entity.X_test, entity.y_test
    if drift == "none":
        return X, y, None, None
    specs = {s.kind: s for s in default_specs(len(X), W)}
    Xd, regime = inject_drift(X, specs[drift], seed)
    return Xd, y, regime, specs[drift].change_points


def run_job(dataset: str, seed: int, methods: List[str], drifts: List[str], shots: List[int],
            out_dir: Path, quick: bool) -> str:
    import torch
    torch.set_num_threads(1)
    t_job = time.time()
    ents = load_cached(dataset)
    split = meta_split(ents, seed)
    mt, ho = split["meta_train"], split["held_out"]
    if quick:
        ho = ho[:2]
    D = W * ents[0].d
    mcfg = MetaConfig()
    over = DATASET_OVERRIDES.get(dataset, {})
    log = lambda *a: print(f"[{dataset} s{seed} {time.time() - t_job:6.0f}s]", *a, flush=True)  # noqa: E731

    # ---- pooled training windows and the static VAE
    rng = np.random.default_rng(seed)
    pooled = np.concatenate([make_windows(s, W, stride=4) for e in mt for s in (getattr(e, "train_segments", None) or [e.X_train])])
    if len(pooled) > 60000:
        pooled = pooled[rng.choice(len(pooled), 60000, replace=False)]
    log(f"pooled windows {pooled.shape}; meta-train {len(mt)} entities, held-out {len(ho)}")
    static = pretrain_static(D, pooled, mcfg, seed, iters=STATIC_ITERS if not quick else 200)
    log("static VAE trained")

    # ---- meta-learners, one per (variant, sampler) that any method needs
    specs = [METHODS[m] for m in methods]
    needed = sorted({(s.meta_variant, s.episode_sampler) for s in specs if s.online is not None and s.online.init == "meta"})
    regimes_cache: Dict[str, list] = {}
    learners: Dict[tuple, MetaLearner] = {}
    for variant, sampler in needed:
        if sampler not in regimes_cache:
            if sampler == "chunk":
                # length-matched to the ADWIN regimes so that only boundary placement differs
                med = int(np.median([len(r) for r in regimes_cache.get("drift") or build_regimes(mt, "drift", W)]))
                regimes_cache["drift"] = regimes_cache.get("drift") or build_regimes(mt, "drift", W)
                regimes_cache[sampler] = build_regimes(mt, "chunk", W, chunk=max(med, 4 * W))
            else:
                regimes_cache[sampler] = build_regimes(mt, sampler, W)
        regs = regimes_cache[sampler]
        ml = MetaLearner(D, replace(mcfg, variant=variant, iters=META_ITERS[dataset] if not quick else 40), seed)
        t0 = time.time()
        losses = ml.meta_train(regs, W)
        learners[(variant, sampler)] = ml
        log(f"meta {variant}/{sampler}: {len(regs)} regimes, {len(losses)} iters, loss {np.mean(losses[:20]):.2f} -> {np.mean(losses[-20:]):.2f}, {time.time() - t0:.0f}s")

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir.parent / "traces").mkdir(parents=True, exist_ok=True)
    fout = open(out_dir / f"{dataset}.jsonl", "a")
    n_runs = 0
    for ent in ho:
        for drift in drifts:
            if dataset == "skab" and drift != "none":
                continue          # SKAB runs are too short for a calibration cycle between changes
            Xs, y, regime, cps = stream_for(ent, drift, seed)
            Xw = make_windows(Xs, W)
            yw = window_labels(y, W)
            regime_w = None if regime is None else regime[W - 1:]
            cps_w = None if cps is None else [c - (W - 1) for c in cps]
            for spec in specs:
                if spec.group == "ablation" and drift == "none":
                    continue      # ablations are scored under drift only
                shot_list = shots if (drift == "none" and spec.name in SHOT_SWEEP_METHODS) else [5]
                if drift != "none" and spec.name in ("IF",) and 5 not in shot_list:
                    shot_list = [5]
                for k in shot_list:
                    try:
                        if spec.online is None:
                            res = run_iforest(pooled, Xw, k, over.get("calib_len", 300), seed)
                        else:
                            cfg = replace(spec.online, k_shot=k, **over)
                            ml = learners.get((spec.meta_variant, spec.episode_sampler))
                            ml = copy.deepcopy(ml) if ml is not None else None   # runs must not share theta*
                            det = StreamingDetector(cfg, W, meta=ml, static_params=static, seed=seed, beta=mcfg.beta)
                            res = det.run(Xw, Xs)
                        m = evaluate(res, yw, regime_w, cps_w)
                        rec = {"dataset": dataset, "seed": seed, "entity": ent.name, "drift": drift,
                               "method": spec.name, "group": spec.group, "k_shot": k, "T": int(len(Xw)), **m}
                        fout.write(json.dumps(jsonable(rec)) + "\n")
                        fout.flush()
                        n_runs += 1
                        if seed == 0 and ent is ho[0] and drift in ("none", "sudden", "recurring") and spec.name in TRACE_METHODS and k == 5:
                            np.savez_compressed(out_dir.parent / "traces" / f"{dataset}_{ent.name}_{drift}_{spec.name}.npz",
                                                scores=res["scores"], tau=res["tau"], alarms=res["alarms"], y=yw,
                                                regime=regime_w if regime_w is not None else np.zeros(len(yw), int),
                                                cps=np.array(cps_w if cps_w else []), eval_start=res["eval_start"],
                                                drift_events=np.array(res["drift_events"]), adapt_events=np.array(res["adapt_events"]))
                    except Exception:  # noqa: BLE001
                        log(f"FAILED {ent.name} {drift} {spec.name} k={k}\n{traceback.format_exc()}")
            log(f"{ent.name} {drift}: done ({n_runs} runs so far)")
    fout.close()
    return f"{dataset} seed {seed}: {n_runs} runs in {time.time() - t_job:.0f}s"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", default="skab,smd,hai,psm,swat,wadi,smap,msl")
    ap.add_argument("--seeds", default="0,1,2,3,4")
    ap.add_argument("--methods", default="all")
    ap.add_argument("--drifts", default=",".join(DRIFTS))
    ap.add_argument("--shots", default="1,5,10")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results/raw")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    methods = list(METHODS) if args.methods == "all" else args.methods.split(",")
    jobs = [(d, int(s), methods, args.drifts.split(","), [int(k) for k in args.shots.split(",")], Path(args.out), args.quick)
            for d in args.datasets.split(",") for s in args.seeds.split(",")]
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    if args.workers == 1:
        for j in jobs:
            print(run_job(*j), flush=True)
        return
    with get_context("spawn").Pool(args.workers) as pool:
        for msg in pool.imap_unordered(_star, jobs):
            print(msg, flush=True)


def _star(j):
    try:
        return run_job(*j)
    except Exception:  # noqa: BLE001
        return f"JOB FAILED {j[0]} seed {j[1]}:\n{traceback.format_exc()}"


if __name__ == "__main__":
    main()
