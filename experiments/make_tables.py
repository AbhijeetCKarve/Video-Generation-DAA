"""Aggregate results/raw/*.jsonl into the tables used in the manuscript.

Every number is mean ± std over seeds, where each seed's value is first
averaged over the held-out entities of that dataset.  Output goes to
results/tables/ as Markdown and LaTeX, and results/summary.json keeps
the numbers for the figure script and for the text.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

RAW = Path(os.environ.get("DAMAD_RAW", "results/raw"))
OUT = Path("results/tables")
DATASETS = ["skab", "smd", "psm", "hai"]
DATASET_LABEL = {"skab": "SKAB", "smd": "SMD", "psm": "PSM", "hai": "HAI"}
BASELINE_ORDER = ["IF", "VAE-S", "VAE-FT", "VAE-INC", "VAE-DFT", "MAML-1", "MSGD-1", "OML-A", "DAMAD"]
ABLATION_ORDER = ["DAMAD", "DAMAD-rndM1", "DAMAD-noM1", "DAMAD+mmd", "DAMAD-mmd", "DAMAD-noM3", "DAMAD-noM4", "DAMAD-noAcc", "DAMAD-fo", "DAMAD-msgd"]
DRIFTS = ["none", "sudden", "gradual", "incremental", "recurring"]


def load_all() -> pd.DataFrame:
    rows = []
    for f in sorted(RAW.glob("*.jsonl")):
        with open(f) as fh:
            rows.extend(json.loads(l) for l in fh if l.strip())
    df = pd.DataFrame(rows)
    return df


def agg(df: pd.DataFrame, metric: str, by: List[str]) -> pd.DataFrame:
    """mean over entities within a seed, then mean and std over seeds."""
    per_seed = df.groupby(by + ["seed"])[metric].mean().reset_index()
    g = per_seed.groupby(by)[metric]
    out = g.agg(["mean", "std", "count"]).reset_index()
    return out


def fmt(mean: float, std: float, nd: int = 3, pct: bool = False) -> str:
    if mean is None or not np.isfinite(mean):
        return "–"
    if pct:
        return f"{100 * mean:.1f} ± {100 * (std if np.isfinite(std) else 0):.1f}"
    return f"{mean:.{nd}f} ± {(std if np.isfinite(std) else 0):.{nd}f}"


def pivot_table(df: pd.DataFrame, metric: str, methods: List[str], cols: List[str], col_key: str,
                nd: int = 3, pct: bool = False, bold_max: bool = True) -> pd.DataFrame:
    a = agg(df, metric, ["method", col_key])
    tab = pd.DataFrame(index=methods, columns=cols, dtype=object)
    best = {}
    for c in cols:
        sub = a[(a[col_key] == c) & (a["method"].isin(methods)) & a["mean"].notna()]
        if len(sub):
            best[c] = sub.loc[sub["mean"].idxmax(), "method"] if bold_max else sub.loc[sub["mean"].idxmin(), "method"]
    for m in methods:
        for c in cols:
            r = a[(a["method"] == m) & (a[col_key] == c)]
            if len(r):
                s = fmt(float(r["mean"].iloc[0]), float(r["std"].iloc[0]), nd, pct)
                if best.get(c) == m:
                    s = f"**{s}**"
                tab.loc[m, c] = s
            else:
                tab.loc[m, c] = "–"
    return tab


def to_markdown(tab: pd.DataFrame, index_name: str, col_labels: Dict[str, str] | None = None) -> str:
    cols = [col_labels.get(c, c) if col_labels else c for c in tab.columns]
    lines = ["| " + index_name + " | " + " | ".join(cols) + " |",
             "|" + "---|" * (len(cols) + 1)]
    for idx, row in tab.iterrows():
        lines.append("| " + str(idx) + " | " + " | ".join(str(v) for v in row.values) + " |")
    return "\n".join(lines)


def to_latex(tab: pd.DataFrame, index_name: str, caption: str, label: str, col_labels: Dict[str, str] | None = None) -> str:
    cols = [col_labels.get(c, c) if col_labels else c for c in tab.columns]
    body = []
    for idx, row in tab.iterrows():
        cells = [str(v).replace("**", "").replace("±", "$\\pm$") for v in row.values]
        cells = [f"\\textbf{{{c}}}" if str(v).startswith("**") else c for v, c in zip(row.values, cells)]
        body.append(str(idx) + " & " + " & ".join(cells) + " \\\\")
    return "\n".join([
        "\\begin{table}[t]", "\\centering", "\\small", f"\\caption{{{caption}}}", f"\\label{{{label}}}",
        "\\begin{tabular}{l" + "c" * len(cols) + "}", "\\toprule",
        index_name + " & " + " & ".join(cols) + " \\\\", "\\midrule", *body, "\\bottomrule", "\\end{tabular}", "\\end{table}"])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_all()
    if df.empty:
        raise SystemExit("no results found")
    df["dataset"] = pd.Categorical(df["dataset"], DATASETS)
    datasets = [d for d in DATASETS if d in set(df["dataset"].astype(str))]
    dl = DATASET_LABEL
    summary: Dict = {"n_runs": int(len(df)), "seeds": sorted(df["seed"].unique().tolist()),
                     "datasets": datasets, "entities": {d: sorted(df[df.dataset == d]["entity"].unique().tolist()) for d in datasets}}
    md: List[str] = []
    tex: List[str] = []

    # ---- Table A: few-shot cold start on held-out entities, no injected drift, K = 5
    sub = df[(df.drift == "none") & (df.k_shot == 5)]
    for metric, nd, pct, name in [("f1", 1, True, "F1"), ("auroc", 1, True, "AUROC"), ("auprc", 1, True, "AUPRC")]:
        tab = pivot_table(sub, metric, BASELINE_ORDER, datasets, "dataset", nd, pct)
        md.append(f"### Table A-{name}: {name} (%) on held-out entities, no injected drift, K = 5, point-wise, threshold set by each method\n\n" + to_markdown(tab, "Method", dl))
        tex.append(to_latex(tab, "Method", f"{name} (\\%) on held-out entities without injected drift (K=5). Mean $\\pm$ std over seeds; strictly point-wise.", f"tab:cold_{metric}", dl))
    tab = pivot_table(sub, "best_f1", BASELINE_ORDER, datasets, "dataset", 1, True)
    md.append("### Table A-bestF1: oracle-threshold F1 (%) for context only\n\n" + to_markdown(tab, "Method", dl))

    # ---- Table B: streaming drift, K = 5
    sub = df[(df.k_shot == 5) & (df.method.isin(BASELINE_ORDER))]
    for metric, nd, pct, name, bold_max in [("f1", 1, True, "F1", True), ("fpr_drift", 1, True, "FPR under drift", False),
                                            ("adaptation_steps", 0, False, "adaptation steps", False),
                                            ("latency_mean", 0, False, "detection latency (steps)", False),
                                            ("segment_detection_rate", 1, True, "segment detection rate", True)]:
        for d in datasets:
            tab = pivot_table(sub[sub.dataset == d], metric, BASELINE_ORDER, DRIFTS, "drift", nd, pct, bold_max)
            md.append(f"### Table B-{name}-{dl[d]}: {name} on {dl[d]} by drift condition (K = 5)\n\n" + to_markdown(tab, "Method"))
            tex.append(to_latex(tab, "Method", f"{name} on {dl[d]} by drift condition (K=5).", f"tab:drift_{metric}_{d}"))
        # pooled over datasets
        tab = pivot_table(sub, metric, BASELINE_ORDER, DRIFTS, "drift", nd, pct, bold_max)
        md.append(f"### Table B-{name}-ALL: {name}, pooled over datasets, by drift condition (K = 5)\n\n" + to_markdown(tab, "Method"))
        tex.append(to_latex(tab, "Method", f"{name} pooled over the four datasets, by drift condition (K=5).", f"tab:drift_{metric}_all"))

    # ---- Table C: shots
    sub = df[(df.drift == "none") & (df.method.isin(["VAE-S", "VAE-FT", "MAML-1", "MSGD-1", "OML-A", "DAMAD"]))]
    sub = sub.assign(k_shot=sub.k_shot.astype(int))
    for d in datasets:
        tab = pivot_table(sub[sub.dataset == d], "f1", ["VAE-S", "VAE-FT", "MAML-1", "MSGD-1", "OML-A", "DAMAD"], [1, 5, 10], "k_shot", 1, True)
        md.append(f"### Table C-{dl[d]}: F1 (%) versus number of shots on {dl[d]} (no injected drift)\n\n" + to_markdown(tab, "Method", {1: "1-shot", 5: "5-shot", 10: "10-shot"}))
        tex.append(to_latex(tab, "Method", f"F1 (\\%) versus shots on {dl[d]}.", f"tab:shots_{d}", {1: "1-shot", 5: "5-shot", 10: "10-shot"}))

    # ---- Table D: ablations, drift conditions pooled (excluding none), K = 5
    sub = df[(df.k_shot == 5) & (df.method.isin(ABLATION_ORDER)) & (df.drift != "none")]
    for metric, nd, pct, name, bold_max in [("f1", 1, True, "F1", True), ("fpr_drift", 1, True, "FPR under drift", False), ("adaptation_steps", 0, False, "adaptation steps", False)]:
        tab = pivot_table(sub, metric, ABLATION_ORDER, datasets, "dataset", nd, pct, bold_max)
        md.append(f"### Table D-{name}: ablations, {name}, drift conditions pooled (K = 5)\n\n" + to_markdown(tab, "Variant", dl))
        tex.append(to_latex(tab, "Variant", f"Ablations: {name} with the four drift conditions pooled (K=5).", f"tab:abl_{metric}", dl))

    # ---- Table E: cost
    sub = df[(df.k_shot == 5) & (df.method.isin(BASELINE_ORDER))]
    cost = sub.groupby("method").agg(ms_per_window=("ms_per_window", "mean"), adapt_s=("adapt_s_total", "mean"),
                                     meta_update_s=("meta_update_s_total", "mean"), n_adapt=("n_adapt", "mean"),
                                     memory_kb=("memory_bytes", lambda x: x.mean() / 1024), n_params=("n_params", "max")).reindex(BASELINE_ORDER)
    md.append("### Table E: computational cost per run (means over all runs with K = 5)\n\n" + to_markdown(cost.round(3), "Method"))
    tex.append(to_latex(cost.round(3), "Method", "Computational cost per run.", "tab:cost"))
    summary["cost"] = cost.round(4).to_dict(orient="index")

    # ---- gate statistics
    sub = df[(df.k_shot == 5) & (df.method == "DAMAD")]
    gate = sub.groupby(["dataset", "drift"], observed=True)["n_drift_events"].mean().unstack()
    md.append("### Table F: mean number of confirmed drift events per DAMAD run\n\n" + to_markdown(gate.round(2), "Dataset"))
    summary["gate_events"] = {str(k): {str(kk): float(vv) for kk, vv in v.items()} for k, v in gate.round(3).to_dict(orient="index").items()}

    # ---- summary numbers for the text
    def headline(metric, drift_filter):
        s = df[(df.k_shot == 5) & drift_filter(df)]
        a = agg(s, metric, ["method", "dataset"])
        return {m: {str(d): [round(float(r["mean"]), 4), round(float(r["std"]), 4)] for d, r in a[a.method == m].set_index("dataset").iterrows()} for m in a.method.unique()}
    summary["cold_f1"] = headline("f1", lambda d: d.drift == "none")
    summary["cold_auroc"] = headline("auroc", lambda d: d.drift == "none")
    summary["drift_f1"] = headline("f1", lambda d: d.drift != "none")
    summary["drift_fpr"] = headline("fpr_drift", lambda d: d.drift != "none")
    summary["drift_adapt"] = headline("adaptation_steps", lambda d: d.drift != "none")
    pooled = agg(df[(df.k_shot == 5)], "f1", ["method", "drift"])
    summary["f1_by_drift_pooled"] = {m: {str(d): [round(float(r["mean"]), 4), round(float(r["std"]), 4)] for d, r in pooled[pooled.method == m].set_index("drift").iterrows()} for m in pooled.method.unique()}
    pooled = agg(df[(df.k_shot == 5)], "fpr_drift", ["method", "drift"])
    summary["fpr_by_drift_pooled"] = {m: {str(d): [round(float(r["mean"]), 4), round(float(r["std"]), 4)] for d, r in pooled[pooled.method == m].set_index("drift").iterrows()} for m in pooled.method.unique()}
    shots = agg(df[(df.drift == "none")], "f1", ["method", "k_shot", "dataset"])
    summary["shots_f1"] = {m: {f"{int(k)}/{d}": [round(float(r["mean"]), 4), round(float(r["std"]), 4)] for (k, d), r in shots[shots.method == m].set_index(["k_shot", "dataset"]).iterrows()} for m in shots.method.unique()}

    (OUT / "tables.md").write_text("\n\n".join(md) + "\n")
    (OUT / "tables.tex").write_text("\n\n".join(tex) + "\n")
    (Path("results") / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    print(f"{len(df)} runs, {len(md)} tables -> {OUT}")


if __name__ == "__main__":
    main()
