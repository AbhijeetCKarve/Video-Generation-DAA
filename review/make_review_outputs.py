"""Final corpus, PRISMA counts, taxonomy tables, the gap-map figure and
the supplementary corpus table, all from screening.csv."""
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
S = pd.read_csv(HERE / "screening.csv")
D = pd.read_csv(HERE / "records_dedup.csv").set_index("rid")

# --- recodes: FT and OTH are few-shot methods without a meta-learning paradigm; UNK = not stated in abstract
S["D1"] = S["D1"].replace({"FT": "NML", "OTH": "NML", "UNK": "NS"})
S.loc[S.rid == "R0018", "D4"] = "IOV"          # telemetry, but no named benchmark
S.loc[S.rid == "R0045", "venue"] = "2020 International Conference on Electrical Machines and Systems (ICEMS)"
S.loc[S.rid == "R0045", "doi"] = "10.23919/ICEMS50442.2020.9291099"

# --- three papers from our own reference list that meet the criteria but were not retrieved by the strings
ADD = [
    {"rid": "A001", "title": "Anomaly detection using a model-agnostic meta-learning-based variational auto-encoder for facility management",
     "year": 2023, "venue": "Journal of Building Engineering", "doi": "10.1016/j.jobe.2023.106099", "authors": "Moon, Noh, Jung, Lee, Hwang",
     "D1": "OPT", "D2": "REC", "D3": "STA", "D4": "GEN", "type": "journal article"},
    {"rid": "A002", "title": "Meta-UAD: A meta-learning scheme for user-level network traffic anomaly detection",
     "year": 2024, "venue": "arXiv 2408.17031", "doi": "", "authors": "Feng et al.",
     "D1": "OPT", "D2": "DIS", "D3": "STA", "D4": "IOV", "type": "preprint"},
    {"rid": "A003", "title": "Meta learning-based few-shot intrusion detection for 5G-enabled industrial internet",
     "year": 2024, "venue": "Complex & Intelligent Systems", "doi": "10.1007/s40747-024-01388-1", "authors": "Yan et al.",
     "D1": "MET", "D2": "DIS", "D3": "STA", "D4": "IOV", "type": "journal article"},
]
# Meta-UAD is a preprint and fails EC4; it stays out of the corpus and is cited only as context
ADD = [a for a in ADD if a["type"] != "preprint"]
for a in ADD:
    S = pd.concat([S, pd.DataFrame([{**a, "stage": "reference list", "decision": "INC", "reason": "known paper meeting the criteria, not retrieved by the strings",
                                     "sources": "reference list", "note": ""}])], ignore_index=True)
S.to_csv(HERE / "screening_final.csv", index=False)
inc = S[S.decision == "INC"].copy()

# --- PRISMA counts
raw = {"lens_primary": 124, "lens_secondary": 476, "ieee": 188}
counts = {
    "identified": sum(raw.values()), "raw": raw, "duplicates": sum(raw.values()) - len(D), "unique": len(D),
    "keyword_excluded": int((S.stage == "keyword").sum()), "type_excluded_EC4": int((S.stage == "type").sum()),
    "read_manually": int((S.stage == "manual").sum()),
    "manual": S[S.stage == "manual"].decision.value_counts().to_dict(),
    "reference_list_added": len(ADD), "corpus": len(inc),
    "years": inc.year.value_counts().sort_index().to_dict(),
    "D1": inc.D1.value_counts().to_dict(), "D2": inc.D2.value_counts().to_dict(),
    "D3": inc.D3.value_counts().to_dict(), "D4": inc.D4.value_counts().to_dict(),
    "D1xD3": {f"{a}|{b}": int(v) for (a, b), v in pd.crosstab(inc.D1, inc.D3).stack().items() if v},
    "sources_of_corpus": inc.sources.value_counts().to_dict(),
}
json.dump(counts, open(HERE / "review_counts.json", "w"), indent=1, default=int)
print(json.dumps({k: counts[k] for k in ["identified", "unique", "keyword_excluded", "type_excluded_EC4", "read_manually", "manual", "corpus", "years", "D1", "D2", "D3", "D4"]}, default=int))

# --- supplementary corpus table
inc = inc.sort_values(["year", "rid"])
first = inc.authors.fillna("").str.split(";").str[0].str.strip().str.replace(",", "")
rows = ["| # | Year | First author | Title | Venue | D1 | D2 | D3 | D4 | DOI |", "|---|---|---|---|---|---|---|---|---|---|"]
for i, (_, r) in enumerate(inc.iterrows(), 1):
    rows.append(f"| {i} | {int(r.year)} | {first.loc[_]} | {str(r.title).strip()} | {str(r.venue)[:60]} | {r.D1} | {r.D2} | {r.D3} | {r.D4} | {r.doi if isinstance(r.doi, str) else ''} |")
(HERE / "corpus_table.md").write_text("\n".join(rows) + "\n")

# --- D1 x D3 gap map
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
D1 = ["OPT", "MET", "MOD", "HYB", "NML", "NS"]
D3 = ["STA", "INC", "DAW", "OMA"]
M = np.zeros((len(D1), len(D3)), int)
for (a, b), v in pd.crosstab(inc.D1, inc.D3).stack().items():
    M[D1.index(a), D3.index(b)] = v
fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.imshow(M, cmap="Blues", vmin=0, vmax=M.max())
for i in range(len(D1)):
    for j in range(len(D3)):
        ax.text(j, i, str(M[i, j]) if M[i, j] else "–", ha="center", va="center",
                color="white" if M[i, j] > M.max() / 2 else "#333", fontsize=11)
ax.set_xticks(range(len(D3)))
ax.set_xticklabels(["STA\nstatic", "INC\nincre-\nmental", "DAW\ndrift-\naware", "OMA\nonline\nmeta-\nadaptive"], fontsize=8.5)
ax.set_yticks(range(len(D1)))
ax.set_yticklabels(["OPT optimisation-based", "MET metric-based", "MOD model-based", "HYB hybrid", "NML few-shot, no meta-learning", "NS paradigm not stated"], fontsize=9)
ax.set_xlabel("D3: streaming and drift capability")
ax.set_ylabel("D1: paradigm")
ax.set_title(f"The {len(inc)} reviewed papers on the D1 × D3 plane", fontsize=10, pad=10)
ax.add_patch(plt.Rectangle((2.5, -0.5), 1, len(D1), fill=False, edgecolor="#C0392B", lw=2, ls="--"))
ax.text(3, len(D1) - 0.62, "empty", ha="center", color="#C0392B", fontsize=9)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(ROOT / "figures" / "fig_gapmap.png", dpi=200)
fig.savefig(ROOT / "figures" / "fig_gapmap.pdf")
print("wrote corpus_table.md, review_counts.json, figures/fig_gapmap.png")
