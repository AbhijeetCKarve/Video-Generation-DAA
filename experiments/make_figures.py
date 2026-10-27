"""Figures for the manuscript, built from results/raw, results/traces and
results/summary.json.  Written to figures/ as PDF and PNG.

  fig_architecture   the DAMAD pipeline (drawn, not a screenshot)
  fig_trace          residual, threshold and alarms around injected drift
                     for VAE-S, VAE-DFT and DAMAD on one stream
  fig_drift_f1       F1 and FPR-under-drift by drift condition, pooled
  fig_shots          F1 versus shots per dataset
  fig_ablation       ablation bars
  fig_gapmap         the taxonomy gap map (D1 x D3), kept from the survey
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

RAW = Path(os.environ.get("DAMAD_RAW", "results/raw"))
TRACES = Path("results/traces")
FIG = Path("figures")
FIG.mkdir(exist_ok=True)

plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight"})
C = {"VAE-S": "#8c8c8c", "VAE-FT": "#b5b5b5", "VAE-INC": "#d4a017", "VAE-DFT": "#1f77b4", "MAML-1": "#2ca02c",
     "MSGD-1": "#98df8a", "OML-A": "#9467bd", "DAMAD": "#d62728", "IF": "#c7c7c7"}
DL = {"skab": "SKAB", "smd": "SMD", "psm": "PSM", "hai": "HAI"}
DRIFTS = ["none", "sudden", "gradual", "incremental", "recurring"]


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png")
    plt.close(fig)


def load_df() -> pd.DataFrame:
    rows = []
    for f in sorted(RAW.glob("*.jsonl")):
        rows.extend(json.loads(l) for l in open(f) if l.strip())
    return pd.DataFrame(rows)


def per_seed(df, metric, by):
    s = df.groupby(by + ["seed"])[metric].mean().reset_index()
    return s.groupby(by)[metric].agg(["mean", "std"]).reset_index()


# ------------------------------------------------------------------ 1
def fig_architecture():
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    def box(x, y, w, h, text, fc, title=None):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec="#333", lw=0.8))
        if title:
            ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top", fontsize=8, weight="bold")
            ax.text(x + w / 2, y + h / 2 - 0.15, text, ha="center", va="center", fontsize=7.2)
        else:
            ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7.5)

    def arrow(p, q, style="-|>", color="#333", ls="-", lw=0.9, conn="arc3,rad=0"):
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, color=color, lw=lw, ls=ls, mutation_scale=9, connectionstyle=conn))

    box(0.1, 3.2, 1.5, 1.2, "stream\n$x_t$", "#e8f0e8", "Sensor input")
    box(2.0, 3.2, 2.2, 1.2, "VAE $\\theta$ from $\\theta^*$\nK-step adaptation", "#dbe9f6", "M2  Meta-learner")
    box(4.6, 3.2, 2.0, 1.2, "residual $r_t$\n$r_t > \\tau$ ?", "#f6e3d5", "Scoring")
    box(7.0, 3.2, 2.9, 1.2, "POT fit on post-change\nresiduals; gated", "#ece4f5", "M4  Threshold $\\tau$")
    box(2.0, 0.6, 2.6, 1.3, "ADWIN on block-mean\nlog residual (rise only)\n+ MMD on embeddings", "#fbe9c8", "M1  Drift gate")
    box(5.2, 0.6, 2.4, 1.3, "one entry per regime:\nsegment, moments, $\\tau$", "#f8d7da", "M3  Regime memory")
    box(8.0, 0.6, 1.9, 1.3, "replay episodes\n$\\theta^* \\leftarrow$ update", "#dbe9f6", "Meta-update")
    arrow((1.6, 3.8), (2.0, 3.8))
    arrow((4.2, 3.8), (4.6, 3.8))
    arrow((6.6, 3.8), (7.0, 3.8))
    arrow((5.6, 3.2), (3.3, 1.9), color="#b33", ls="--")
    ax.text(4.1, 2.55, "residual, embedding", fontsize=6.5, color="#b33", rotation=28)
    arrow((3.3, 1.9), (3.1, 3.2), color="#b33")
    ax.text(2.35, 2.45, "confirmed change:\nadapt from $\\theta^*$", fontsize=6.5, color="#b33")
    arrow((4.6, 1.25), (5.2, 1.25), color="#b33")
    ax.text(4.65, 1.45, "store old\nregime", fontsize=6.3, color="#b33")
    arrow((7.6, 1.25), (8.0, 1.25), color="#b33")
    arrow((8.95, 1.9), (3.2, 3.15), color="#b33", ls=":", conn="arc3,rad=-0.25")
    ax.text(6.3, 2.75, "refreshed $\\theta^*$", fontsize=6.5, color="#b33")
    arrow((4.0, 1.9), (8.4, 3.2), color="#7a4ea3", ls="--", conn="arc3,rad=0.2")
    ax.text(5.7, 2.2, "recalibrate $\\tau$", fontsize=6.5, color="#7a4ea3")
    ax.text(0.1, 0.25, "solid: steady-state path, every step.   dashed: fires only on a confirmed regime change.", fontsize=6.8, color="#444")
    save(fig, "fig_architecture")


# ------------------------------------------------------------------ 2
def fig_trace(dataset="smd", drift="sudden"):
    files = sorted(TRACES.glob(f"{dataset}_*_{drift}_DAMAD.npz"))
    if not files:
        print("no trace for", dataset, drift)
        return
    ent = files[0].name.split("_")[1]
    methods = ["VAE-S", "VAE-DFT", "DAMAD"]
    fig, axes = plt.subplots(len(methods), 1, figsize=(7.2, 1.55 * len(methods) + 0.4), sharex=True)
    for ax, m in zip(axes, methods):
        f = TRACES / f"{dataset}_{ent}_{drift}_{m}.npz"
        if not f.exists():
            ax.set_visible(False)
            continue
        z = np.load(f)
        s, tau, y, e0 = z["scores"], z["tau"], z["y"], int(z["eval_start"])
        t = np.arange(len(s))
        ax.plot(t, np.log10(s + 1e-6), lw=0.4, color=C[m], label="log residual")
        ax.plot(t, np.log10(tau + 1e-6), lw=0.9, color="k", ls="--", label="log $\\tau$")
        ylo, yhi = ax.get_ylim()
        ax.fill_between(t, ylo, yhi, where=y > 0, color="#f4b942", alpha=0.35, lw=0, label="labelled anomaly")
        for cp in z["cps"]:
            ax.axvline(cp, color="#555", lw=0.8, ls=":")
        for ev in z["adapt_events"]:
            ax.axvline(ev, color="#d62728", lw=0.8, alpha=0.8)
        ax.axvspan(0, e0, color="#ddd", alpha=0.5, lw=0)
        ax.set_ylabel("log$_{10}$ score")
        ax.set_title(m, loc="left", fontsize=8.5, weight="bold")
        ax.set_ylim(ylo, yhi)
    axes[-1].set_xlabel("window index")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=3, loc="upper right", fontsize=7, frameon=False, bbox_to_anchor=(0.99, 1.0))
    fig.text(0.01, 0.995, f"{DL[dataset]} {ent}, {drift} drift. Dotted: injected change points. Red: adaptation events. Grey: warm-up.", fontsize=7, va="top")
    save(fig, f"fig_trace_{dataset}_{drift}")


# ------------------------------------------------------------------ 3
def fig_drift(df):
    order = ["VAE-S", "VAE-INC", "VAE-DFT", "MAML-1", "OML-A", "DAMAD"]
    sub = df[(df.k_shot == 5) & df.method.isin(order)]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.6))
    for ax, metric, lab in zip(axes, ["f1", "fpr_drift"], ["F1 (point-wise)", "false-alarm rate after drift"]):
        a = per_seed(sub, metric, ["method", "drift"])
        drifts = [d for d in DRIFTS if not (metric == "fpr_drift" and d == "none")]
        x = np.arange(len(drifts))
        wdt = 0.8 / len(order)
        for i, m in enumerate(order):
            r = a[a.method == m].set_index("drift").reindex(drifts)
            ax.bar(x + (i - len(order) / 2 + 0.5) * wdt, r["mean"], wdt, yerr=r["std"].fillna(0), color=C[m], label=m, error_kw=dict(lw=0.6, capsize=1.5))
        ax.set_xticks(x)
        ax.set_xticklabels(drifts)
        ax.set_ylabel(lab)
        ax.set_ylim(0, 1)
    axes[0].legend(fontsize=6.5, ncol=2, frameon=False)
    save(fig, "fig_drift")


# ------------------------------------------------------------------ 4
def fig_shots(df):
    order = ["VAE-FT", "MAML-1", "MSGD-1", "OML-A", "DAMAD"]
    datasets = [d for d in DL if d in set(df.dataset)]
    sub = df[(df.drift == "none") & df.method.isin(order)]
    fig, axes = plt.subplots(1, len(datasets), figsize=(1.8 * len(datasets) + 0.6, 2.3), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, d in zip(axes, datasets):
        a = per_seed(sub[sub.dataset == d], "f1", ["method", "k_shot"])
        for m in order:
            r = a[a.method == m].sort_values("k_shot")
            ax.errorbar(r["k_shot"], r["mean"], yerr=r["std"].fillna(0), color=C[m], marker="o", ms=3, lw=1, capsize=1.5, label=m)
        base = per_seed(df[(df.drift == "none") & (df.dataset == d) & (df.method == "VAE-S") & (df.k_shot == 5)], "f1", ["method"])
        if len(base):
            ax.axhline(base["mean"].iloc[0], color=C["VAE-S"], ls="--", lw=0.8, label="VAE-S")
        ax.set_title(DL[d], fontsize=9)
        ax.set_xticks([1, 5, 10])
        ax.set_xlabel("shots K")
    axes[0].set_ylabel("F1")
    axes[-1].legend(fontsize=6, frameon=False)
    save(fig, "fig_shots")


# ------------------------------------------------------------------ 5
def fig_ablation(df):
    order = ["DAMAD", "DAMAD-rndM1", "DAMAD-noM1", "DAMAD-adwin", "DAMAD-mmd", "DAMAD-noM3", "DAMAD-noM4", "DAMAD-noAcc", "DAMAD-fo", "DAMAD-msgd"]
    labels = ["full", "random\nepisodes", "chunk\nepisodes", "ADWIN\nonly", "MMD\nonly", "no\nreplay", "no τ\nrecal.", "no accept.\ntest", "FOMAML\ninit", "Meta-SGD\ninit"]
    sub = df[(df.k_shot == 5) & (df.drift != "none") & df.method.isin(order)]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4))
    for ax, metric, lab in zip(axes, ["f1", "fpr_drift", "adaptation_steps"], ["F1", "false-alarm rate after drift", "adaptation steps"]):
        a = per_seed(sub, metric, ["method"]).set_index("method").reindex(order)
        cols = ["#d62728"] + ["#7f7f7f"] * (len(order) - 1)
        ax.bar(np.arange(len(order)), a["mean"], yerr=a["std"].fillna(0), color=cols, error_kw=dict(lw=0.6, capsize=1.5))
        ax.set_xticks(np.arange(len(order)))
        ax.set_xticklabels(labels, fontsize=6)
        ax.set_ylabel(lab)
    save(fig, "fig_ablation")


# ------------------------------------------------------------------ 6
def fig_gapmap():
    rows = ["D1-OPT\n(n=48)", "D1-MET\n(n=27)", "D1-MOD\n(n=10)", "D1-HYB\n(n=2)"]
    cols = ["D3-STA\n(static)", "D3-INC\n(incremental)", "D3-DAW\n(drift-aware)", "D3-OMA\n(online meta-adaptive)"]
    levels = [[3, 2, 1, 0], [3, 2, 1, 0], [2, 1, 1, 0], [1, 0, 0, -1]]
    text = [["many", "few", "rare", "gap"], ["many", "few", "rare", "gap"], ["few", "rare", "rare", "gap"], ["rare", "gap", "gap", "this work"]]
    colors = {3: "#1f4e79", 2: "#4f8fcc", 1: "#bdd7ee", 0: "#fbe3e8", -1: "#d62728"}
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    for i in range(4):
        for j in range(4):
            lv = levels[i][j]
            ax.add_patch(FancyBboxPatch((j, 3 - i), 0.94, 0.94, boxstyle="round,pad=0,rounding_size=0.04", fc=colors[lv], ec="white"))
            ax.text(j + 0.47, 3 - i + 0.47, text[i][j], ha="center", va="center", fontsize=8, weight="bold",
                    color="white" if lv in (3, 2, -1) else "#8b1d2b")
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_xticks(np.arange(4) + 0.47)
    ax.set_xticklabels(cols, fontsize=7.5)
    ax.set_yticks(np.arange(4) + 0.47)
    ax.set_yticklabels(rows[::-1], fontsize=7.5)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    save(fig, "fig_gapmap")


def main():
    fig_architecture()
    fig_gapmap()
    df = load_df()
    if df.empty:
        print("no results; drew architecture and gap map only")
        return
    fig_drift(df)
    fig_shots(df)
    fig_ablation(df)
    for d in DL:
        for dr in ("sudden", "recurring"):
            fig_trace(d, dr)
    print("figures written to", FIG)


if __name__ == "__main__":
    main()
