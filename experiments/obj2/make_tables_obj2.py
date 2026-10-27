"""Tables, figures and a summary JSON for the offline meta-learning study.

Aggregation: every (method, adaptation setting, K) is first averaged over
the held-out entities of a dataset within a seed, then mean and standard
deviation are taken over the seeds.  Paired tests compare methods on the
same (seed, entity, K) cells.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "results" / "obj2"
TAB = RAW / "tables"
FIG = ROOT / "figures" / "obj2"
TAB.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

DS_ORDER = ["swat", "wadi", "hai", "smap", "msl"]
DS_NAME = {"swat": "SWaT", "wadi": "WADI", "hai": "HAI", "smap": "SMAP", "msl": "MSL"}
METRICS = ["auroc", "auprc", "f1", "precision", "recall", "best_f1"]


def load(pattern: str) -> pd.DataFrame:
    rows = []
    for f in sorted(RAW.glob(pattern)):
        if f.stem.startswith("within_long") and "long" not in pattern:
            continue                                   # the long variant has its own table
        tag = f.stem.replace("within_", "").replace("magnitude_", "")
        tag = tag.split("_")[0] if "_" in tag else ""      # e.g. within_long_hai -> "long"
        with open(f) as fh:
            for l in fh:
                if l.strip():
                    r = json.loads(l)
                    if tag:
                        r["method"] = r["method"] + f" [{tag}]"
                    rows.append(r)
    df = pd.DataFrame(rows)
    if len(df):
        df["key"] = df["method"] + np.where(df["adapt"].eq("none"), "", " (" + df["adapt"] + ")")
    return df


def seed_mean(df: pd.DataFrame, by, cols):
    """mean over entities within seed, then mean/sd over seeds"""
    per_seed = df.groupby(by + ["seed"])[cols].mean().reset_index()
    g = per_seed.groupby(by)[cols]
    return g.mean(), g.std(ddof=0), per_seed


def fmt(m, s):
    return f"{m:.3f} ± {s:.3f}" if np.isfinite(m) else "–"


def md_table(df: pd.DataFrame, path: Path, floatfmt="{:.3f}"):
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join([df.index.name or ""] + cols) + " |",
             "|" + "---|" * (len(cols) + 1)]
    for idx, row in df.iterrows():
        vals = [floatfmt.format(v) if isinstance(v, (float, np.floating)) else str(v) for v in row]
        lines.append("| " + " | ".join([str(idx)] + vals) + " |")
    path.write_text("\n".join(lines) + "\n")


# ------------------------------------------------------------------ within
W = load("within_*.jsonl")
summary = {}
if len(W):
    W["dataset"] = pd.Categorical(W["dataset"], DS_ORDER)
    main_keys = ["Magnitude", "IsoForest", "MLP-AE", "Static-AE", "Static-AE+FT (matched)", "MAML-AE-noadapt", "MAML-AE (matched)",
                 "MAML-AE (heavy)", "MAML-AE-broken (matched)", "Scratch-noadapt", "Scratch (matched)"]
    for metric in ["auroc", "auprc", "f1", "best_f1"]:
        m, s, _ = seed_mean(W[W.key.isin(main_keys)], ["dataset", "k_shot", "key"], [metric])
        tab = m[metric].unstack("k_shot")
        sd = s[metric].unstack("k_shot")
        out = tab.copy().astype(object)
        for c in tab.columns:
            out[c] = [fmt(a, b) for a, b in zip(tab[c], sd[c])]
        out = out.reindex(pd.MultiIndex.from_product([DS_ORDER, main_keys], names=["dataset", "key"])).dropna(how="all")
        out.index = [f"{DS_NAME[d]} / {k}" for d, k in out.index]
        out.index.name = "dataset / method"
        md_table(out, TAB / f"within_{metric}.md", "{}")
    # compact headline table: AUROC and AUPRC at K=20, all datasets, mean over seeds
    m, s, _ = seed_mean(W[W.key.isin(main_keys)], ["dataset", "k_shot", "key"], ["auroc", "auprc", "f1"])
    head = m.xs(20, level="k_shot")
    hs = s.xs(20, level="k_shot")
    rows = []
    for key in main_keys:
        r = {"method": key}
        for d in DS_ORDER:
            if (d, key) in head.index:
                r[DS_NAME[d] + " AUROC"] = fmt(head.loc[(d, key), "auroc"], hs.loc[(d, key), "auroc"])
                r[DS_NAME[d] + " AUPRC"] = fmt(head.loc[(d, key), "auprc"], hs.loc[(d, key), "auprc"])
        rows.append(r)
    md_table(pd.DataFrame(rows).set_index("method"), TAB / "within_k20_headline.md", "{}")

    # ---- adaptation effect
    A = W[W.adapt.ne("none")].copy()
    base_key = {"Static-AE+FT": "Static-AE", "MAML-AE": "MAML-AE-noadapt", "MAML-AE-broken": "Scratch-noadapt",
                "Scratch": "Scratch-noadapt"}
    # delta AUROC relative to the un-adapted model, on the same cell
    base = W[W.adapt.eq("none")].set_index(["dataset", "seed", "entity", "k_shot", "method"])["auroc"]
    A["base_auroc"] = [base.get((d, s, e, k, base_key[m]), np.nan) for d, s, e, k, m in
                       zip(A.dataset, A.seed, A.entity, A.k_shot, A.method)]
    A["d_auroc"] = A["auroc"] - A["base_auroc"]
    cols = ["rel_param_change", "score_spearman", "score_mean_ratio", "d_auroc"]
    m, s, _ = seed_mean(A, ["method", "adapt", "k_shot"], cols)
    out = m.copy().astype(object)
    for c in cols:
        out[c] = [fmt(a, b) for a, b in zip(m[c], s[c])]
    out.index = [f"{a} / {b} / K={c}" for a, b, c in out.index]
    out.index.name = "method / setting / K"
    md_table(out, TAB / "adaptation_effect.md", "{}")
    m2, s2, _ = seed_mean(A, ["dataset", "method", "adapt"], cols)
    out = m2.copy().astype(object)
    for c in cols:
        out[c] = [fmt(a, b) for a, b in zip(m2[c], s2[c])]
    out.index = [f"{DS_NAME[a]} / {b} / {c}" for a, b, c in out.index]
    out.index.name = "dataset / method / setting"
    md_table(out, TAB / "adaptation_effect_by_dataset.md", "{}")

    # ---- paired comparisons on (dataset, seed, entity, K) cells: MAML-AE (matched) vs rivals
    cell = W.set_index(["dataset", "seed", "entity", "k_shot", "key"])["auroc"].unstack("key")
    pairs = [("MAML-AE (matched)", "Static-AE"), ("MAML-AE (matched)", "Static-AE+FT (matched)"),
             ("MAML-AE (matched)", "MAML-AE-noadapt"), ("MAML-AE (matched)", "MAML-AE-broken (matched)"),
             ("MAML-AE (matched)", "IsoForest"), ("MAML-AE (matched)", "MLP-AE"), ("Static-AE", "MLP-AE"),
             ("MAML-AE (heavy)", "MAML-AE-noadapt"), ("MAML-AE-broken (matched)", "Scratch (matched)"), ("Static-AE", "Magnitude"), ("MAML-AE (matched)", "Magnitude"),
             ("Scratch-noadapt", "Magnitude")]
    rows = []
    for d in DS_ORDER:
        if d not in cell.index.get_level_values(0):
            continue
        c = cell.xs(d, level="dataset")
        for a, b in pairs:
            if a not in c or b not in c:
                continue
            x = (c[a] - c[b]).dropna()
            if len(x) < 5:
                continue
            try:
                p = stats.wilcoxon(x).pvalue if (x != 0).any() else 1.0
            except ValueError:
                p = float("nan")
            rows.append({"dataset": DS_NAME[d], "A": a, "B": b, "n_cells": len(x), "mean_dAUROC": x.mean(),
                         "wins": int((x > 0).sum()), "losses": int((x < 0).sum()), "wilcoxon_p": p})
    P = pd.DataFrame(rows)
    if len(P):
        md_table(P.set_index("dataset"), TAB / "paired_tests.md", "{:.4f}")

    # ---- task diversity vs meta-learning gain (NASA channels + plants)
    div_rows = []
    for f in sorted(RAW.glob("meta_*.json")):
        mj = json.load(open(f))
        d, seed = mj["dataset"], mj["seed"]
        c = cell.xs(d, level="dataset")
        if d in ("smap", "msl"):
            for ent, info in mj.get("per_channel", {}).items():
                sub = c[c.index.get_level_values("entity") == ent]
                sub = sub[sub.index.get_level_values("seed") == seed]
                if len(sub) and "MAML-AE (matched)" in sub and "Static-AE" in sub:
                    g = (sub["MAML-AE (matched)"] - sub["Static-AE"]).mean()
                    g2 = (sub["MAML-AE-noadapt"] - sub["Static-AE"]).mean()
                    div_rows.append({"dataset": d, "seed": seed, "entity": ent, "silhouette": info["silhouette"],
                                     "k": info["k"], "gain_auroc": g, "gain_noadapt": g2})
        else:
            sub = c[c.index.get_level_values("seed") == seed]
            if len(sub):
                div_rows.append({"dataset": d, "seed": seed, "entity": "plant", "silhouette": mj["silhouette"],
                                 "k": mj["regime_k"], "gain_auroc": (sub["MAML-AE (matched)"] - sub["Static-AE"]).mean(),
                                 "gain_noadapt": (sub["MAML-AE-noadapt"] - sub["Static-AE"]).mean()})
    D = pd.DataFrame(div_rows)
    if len(D):
        D.to_csv(TAB / "diversity_vs_gain.csv", index=False)
        nasa = D[D.dataset.isin(["smap", "msl"])]
        if len(nasa) > 5:
            r = stats.spearmanr(nasa.silhouette, nasa.gain_auroc)
            summary["diversity_spearman_nasa"] = {"rho": float(r.correlation), "p": float(r.pvalue), "n": int(len(nasa))}
        per_ds = {}
        for d, g in D.groupby("dataset"):
            per_ds[d] = {"silhouette_mean": float(g.silhouette.mean()), "silhouette_sd": float(g.silhouette.std(ddof=0)),
                         "gain_mean": float(g.gain_auroc.mean()), "n": int(len(g))}
        summary["diversity_by_dataset"] = per_ds

    # ---- gradient-path control evidence
    ctrl = []
    for f in sorted(RAW.glob("meta_*.json")):
        mj = json.load(open(f))
        ctrl.append({"dataset": DS_NAME[mj["dataset"]], "seed": mj["seed"],
                     "corrected |dθ| per step": mj["maml_hist"]["param_change_mean"],
                     "corrected zero-step frac": mj["maml_hist"]["param_change_zero_frac"],
                     "corrected best val": mj["maml_hist"]["best_val"],
                     "broken |dθ| per step": mj["broken_hist"]["param_change_mean"],
                     "broken zero-step frac": mj["broken_hist"]["param_change_zero_frac"],
                     "broken max |θ−θ0|": mj["broken_hist"]["max_abs_param_diff_from_init"],
                     "broken val (first, last)": f"{mj['broken_hist']['val'][0]:.4f}, {mj['broken_hist']['val'][-1]:.4f}",
                     "static best val": mj["static_best_val"], "regimes k": mj["regime_k"], "silhouette": mj["silhouette"]})
    C = pd.DataFrame(ctrl)
    if len(C):
        md_table(C.set_index("dataset"), TAB / "gradient_path_control.md", "{:.4g}")
        summary["control"] = {"n_runs": int(len(C)), "broken_zero_frac_min": float(C["broken zero-step frac"].min()),
                              "broken_max_abs_diff_max": float(C["broken max |θ−θ0|"].max()),
                              "corrected_step_mean": float(C["corrected |dθ| per step"].mean())}

    # ---- deployed vs oracle threshold
    m, s, _ = seed_mean(W[W.key.isin(["Static-AE", "MAML-AE (matched)", "IsoForest", "Magnitude"])], ["dataset", "key", "k_shot"],
                        ["f1", "best_f1", "precision", "recall", "alarm_rate", "anomaly_rate"])
    out = m.copy()
    out.index = [f"{DS_NAME[a]} / {b} / K={c}" for a, b, c in out.index]
    out.index.name = "dataset / method / K"
    md_table(out, TAB / "threshold_gap.md")

    # ---- headline numbers for the text
    m, s, _ = seed_mean(W, ["dataset", "k_shot", "key"], ["auroc", "auprc", "f1", "best_f1"])
    summary["within"] = {f"{d}|{k}|{key}": {"auroc": float(r.auroc), "auprc": float(r.auprc), "f1": float(r.f1),
                                             "best_f1": float(r.best_f1), "auroc_sd": float(s.loc[(d, k, key), "auroc"])}
                         for (d, k, key), r in m.iterrows()}
    summary["n_within_rows"] = int(len(W))
    summary["within_entities"] = {d: int(W[W.dataset == d].entity.nunique()) for d in DS_ORDER if (W.dataset == d).any()}

# ------------------------------------------------------------ long variant
LG = load("within_long_*.jsonl")
if len(LG) and len(W):
    seeds = sorted(LG.seed.unique())
    keys = ["MAML-AE-noadapt", "MAML-AE (matched)", "MAML-AE (heavy)", "Static-AE"]
    rows = []
    for d in sorted(LG.dataset.unique()):
        for k in keys:
            a = LG[(LG.dataset == d) & (LG.key.str.replace(" [long]", "", regex=False) == k)]
            b = W[(W.dataset == d) & (W.key == k) & W.seed.isin(seeds)]
            rows.append({"dataset": DS_NAME[d], "method": k, "AUROC 600 steps": b.groupby("seed").auroc.mean().mean(),
                         "AUROC 3000 steps": a.groupby("seed").auroc.mean().mean(),
                         "AUPRC 600": b.groupby("seed").auprc.mean().mean(), "AUPRC 3000": a.groupby("seed").auprc.mean().mean()})
    md_table(pd.DataFrame(rows).set_index("dataset"), TAB / "long_variant.md")
    summary["long_variant_seeds"] = [int(x) for x in seeds]

# ---------------------------------------------------------------- transfer
T = load("transfer.jsonl")
if len(T):
    T["dir"] = T["source"].map(DS_NAME) + "→" + T["target"].map(DS_NAME)
    tkeys = ["Target-static", "Source-static-noadapt", "Static-transfer (matched)", "Static-transfer (heavy)",
             "MAML-transfer-noadapt", "MAML-transfer (matched)", "MAML-transfer (heavy)", "Scratch (matched)"]
    for metric in ["auroc", "auprc", "f1"]:
        m, s, _ = seed_mean(T[T.key.isin(tkeys)], ["dir", "k_shot", "key"], [metric])
        tab = m[metric].unstack("dir")
        sd = s[metric].unstack("dir")
        out = tab.copy().astype(object)
        for c in tab.columns:
            out[c] = [fmt(a, b) for a, b in zip(tab[c], sd[c])]
        out.index = [f"{k} / K={K}" for K, k in out.index]
        out.index.name = "method / K"
        md_table(out, TAB / f"transfer_{metric}.md", "{}")
    cell = T.set_index(["dir", "seed", "entity", "k_shot", "key"])["auroc"].unstack("key")
    rows = []
    for d in sorted(T["dir"].unique()):
        c = cell.xs(d, level="dir")
        for a, b in [("MAML-transfer (matched)", "Static-transfer (matched)"), ("MAML-transfer (matched)", "Target-static"),
                     ("MAML-transfer (matched)", "MAML-transfer-noadapt"), ("MAML-transfer (heavy)", "Static-transfer (heavy)"),
                     ("Static-transfer (matched)", "Scratch (matched)"), ("MAML-transfer (matched)", "Scratch (matched)")]:
            if a in c and b in c:
                x = (c[a] - c[b]).dropna()
                if len(x) >= 5:
                    try:
                        p = stats.wilcoxon(x).pvalue if (x != 0).any() else 1.0
                    except ValueError:
                        p = float("nan")
                    rows.append({"direction": d, "A": a, "B": b, "n_cells": len(x), "mean_dAUROC": x.mean(),
                                 "wins": int((x > 0).sum()), "losses": int((x < 0).sum()), "wilcoxon_p": p})
    if rows:
        md_table(pd.DataFrame(rows).set_index("direction"), TAB / "transfer_paired_tests.md", "{:.4f}")
    m, s, _ = seed_mean(T, ["dir", "k_shot", "key"], ["auroc", "auprc", "f1"])
    summary["transfer"] = {f"{d}|{k}|{key}": {"auroc": float(r.auroc), "auprc": float(r.auprc), "f1": float(r.f1),
                                              "auroc_sd": float(s.loc[(d, k, key), "auroc"])} for (d, k, key), r in m.iterrows()}
    summary["pca_var"] = {d: float(v) for d, v in T.groupby("source")["pca_var_source"].mean().items()}
    summary["n_transfer_rows"] = int(len(T))

json.dump(summary, open(RAW / "summary_obj2.json", "w"), indent=1, default=float)
print("tables written to", TAB)

# ---------------------------------------------------------------- figures
if "--no-fig" in sys.argv or not len(W):
    sys.exit(0)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
COL = {"Static-AE": "#4477AA", "Static-AE+FT (matched)": "#66CCEE", "MAML-AE-noadapt": "#CCBB44",
       "MAML-AE (matched)": "#EE6677", "MAML-AE (heavy)": "#AA3377", "MAML-AE-broken (matched)": "#BBBBBB",
       "Scratch (matched)": "#000000", "IsoForest": "#228833", "MLP-AE": "#999933", "Magnitude": "#DDAA33"}

# Fig 1: AUROC vs K per dataset
m, s, _ = seed_mean(W, ["dataset", "k_shot", "key"], ["auroc"])
fig, axes = plt.subplots(1, len(DS_ORDER), figsize=(13, 2.9), sharey=False)
for ax, d in zip(axes, DS_ORDER):
    for key, col in COL.items():
        try:
            y = m.xs((d, key), level=("dataset", "key"))["auroc"]
            e = s.xs((d, key), level=("dataset", "key"))["auroc"]
        except KeyError:
            continue
        ax.errorbar(y.index, y.values, yerr=e.values, label=key, color=col, marker="o", ms=3, lw=1, capsize=2)
    ax.set_xscale("log")
    ax.set_xticks([1, 5, 20, 100])
    ax.set_xticklabels(["1", "5", "20", "100"])
    ax.set_title(DS_NAME[d])
    ax.set_xlabel("support windows K")
axes[0].set_ylabel("AUROC")
h, l = axes[-1].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=5, fontsize=7, frameon=False, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.1, 1, 1))
fig.savefig(FIG / "fig_auroc_vs_k.png", dpi=200)
fig.savefig(FIG / "fig_auroc_vs_k.pdf")
plt.close(fig)

# Fig 2: adaptation effect by setting
A = W[W.adapt.ne("none") & W.method.isin(["Static-AE+FT", "MAML-AE"])]
m, s, _ = seed_mean(A, ["dataset", "method", "adapt"], ["rel_param_change", "score_spearman", "score_mean_ratio"])
fig, axes = plt.subplots(1, 3, figsize=(11, 2.9))
for ax, c, lab in zip(axes, ["rel_param_change", "score_spearman", "score_mean_ratio"],
                      ["relative parameter change", "Spearman ρ of scores (before vs after)", "mean score ratio (after / before)"]):
    xs = np.arange(len(DS_ORDER))
    w = 0.13
    i = 0
    for meth, hatch in [("Static-AE+FT", ""), ("MAML-AE", "//")]:
        for ad, col in [("draft", "#CCBB44"), ("matched", "#EE6677"), ("heavy", "#AA3377")]:
            ys = [m.loc[(d, meth, ad), c] if (d, meth, ad) in m.index else np.nan for d in DS_ORDER]
            es = [s.loc[(d, meth, ad), c] if (d, meth, ad) in s.index else 0 for d in DS_ORDER]
            ax.bar(xs + (i - 2.5) * w, ys, w, yerr=es, color=col, hatch=hatch, edgecolor="k", lw=0.3,
                   label=f"{meth} / {ad}", capsize=1.5)
            i += 1
    ax.set_xticks(xs)
    ax.set_xticklabels([DS_NAME[d] for d in DS_ORDER])
    ax.set_title(lab, fontsize=9)
    if c == "rel_param_change":
        ax.set_yscale("log")
axes[0].legend(fontsize=5.5, frameon=False, ncol=2)
fig.tight_layout()
fig.savefig(FIG / "fig_adaptation_effect.png", dpi=200)
fig.savefig(FIG / "fig_adaptation_effect.pdf")
plt.close(fig)

# Fig 3: gradient-path control: validation loss and per-step parameter change
fig, axes = plt.subplots(1, 2, figsize=(8, 2.9))
for f in sorted(RAW.glob("meta_*_s0.json")):
    mj = json.load(open(f))
    d = mj["dataset"]
    axes[0].plot(mj["maml_hist"]["step"], mj["maml_hist"]["val"], label=f"{DS_NAME[d]} corrected", lw=1)
    axes[0].plot(mj["broken_hist"]["step"], mj["broken_hist"]["val"], ls="--", lw=1, label=f"{DS_NAME[d]} broken")
axes[0].set_xlabel("outer step")
axes[0].set_ylabel("post-adaptation query loss (val)")
axes[0].legend(fontsize=5, frameon=False, ncol=2)
C = pd.DataFrame([{"dataset": DS_NAME[json.load(open(f))["dataset"]],
                   "corrected": json.load(open(f))["maml_hist"]["param_change_mean"],
                   "broken": json.load(open(f))["broken_hist"]["param_change_mean"]} for f in sorted(RAW.glob("meta_*.json"))])
g = C.groupby("dataset").mean().reindex([DS_NAME[d] for d in DS_ORDER]).dropna()
xs = np.arange(len(g))
axes[1].bar(xs - 0.2, g["corrected"], 0.4, label="corrected FOMAML", color="#EE6677")
axes[1].bar(xs + 0.2, g["broken"] + 1e-12, 0.4, label="broken pattern", color="#BBBBBB")
axes[1].set_xticks(xs)
axes[1].set_xticklabels(g.index)
axes[1].set_ylabel("mean ‖Δθ‖ per outer step")
axes[1].legend(fontsize=7, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=2)
axes[1].text(len(g) / 2 - 0.5, 0.004, "broken pattern: 0.0 on every step", ha="center", fontsize=7, color="#555555")
fig.tight_layout()
fig.savefig(FIG / "fig_gradient_path.png", dpi=200)
fig.savefig(FIG / "fig_gradient_path.pdf")
plt.close(fig)

# Fig 4: transfer heat map (AUROC, K=20, MAML-transfer matched minus Static-transfer matched, and absolute)
if len(T):
    m, s, _ = seed_mean(T, ["source", "target", "k_shot", "key"], ["auroc"])
    plants = ["swat", "wadi", "hai"]
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.0))
    fig.subplots_adjust(wspace=0.45, right=0.88)
    for ax, key in zip(axes, ["Static-transfer (matched)", "MAML-transfer (matched)", "Target-static"]):
        M = np.full((3, 3), np.nan)
        for i, a in enumerate(plants):
            for j, b in enumerate(plants):
                if (a, b, 20, key) in m.index:
                    M[i, j] = m.loc[(a, b, 20, key), "auroc"]
        im = ax.imshow(M, vmin=0.4, vmax=1.0, cmap="viridis")
        for i in range(3):
            for j in range(3):
                if np.isfinite(M[i, j]):
                    ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", color="w", fontsize=8)
        ax.set_xticks(range(3))
        ax.set_xticklabels([DS_NAME[p] for p in plants])
        ax.set_yticks(range(3))
        ax.set_yticklabels([DS_NAME[p] for p in plants])
        ax.set_xlabel("target")
        ax.set_title(key, fontsize=9)
    axes[0].set_ylabel("source")
    cax = fig.add_axes([0.905, 0.2, 0.015, 0.6])
    fig.colorbar(im, cax=cax, label="AUROC (K=20)")
    fig.savefig(FIG / "fig_transfer.png", dpi=200, bbox_inches="tight")
    fig.savefig(FIG / "fig_transfer.pdf", bbox_inches="tight")
    plt.close(fig)

# Fig 5: diversity vs gain
if len(D):
    fig, ax = plt.subplots(figsize=(4.2, 3))
    for d, mk in [("smap", "o"), ("msl", "s"), ("swat", "^"), ("wadi", "v"), ("hai", "D")]:
        g = D[D.dataset == d]
        if len(g):
            ax.scatter(g.silhouette, g.gain_auroc, s=14, marker=mk, label=DS_NAME[d], alpha=0.7)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xlabel("task diversity (silhouette of regime clustering)")
    ax.set_ylabel("AUROC gain over Static-AE")
    ax.set_title("MAML-AE (matched) minus Static-AE, per held-out stream", fontsize=8)
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "fig_diversity_gain.png", dpi=200)
    fig.savefig(FIG / "fig_diversity_gain.pdf")
    plt.close(fig)
print("figures written to", FIG)
