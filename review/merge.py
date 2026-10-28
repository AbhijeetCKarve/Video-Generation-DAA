"""Merge the three database exports into one de-duplicated record table.

Sources (as exported by the authors):
  raw/lens_primary.csv      Lens.org, primary string (meta-learning x anomaly detection x IoT/industrial)
  raw/lens_secondary.csv    Lens.org, secondary string (concept drift x anomaly detection x IoT/industrial)
  raw/ieee_export_*.csv     IEEE Xplore export (2026-09-28)

Output: records_dedup.csv with one row per unique work, the sources it
came from, and two regular-expression pre-screen flags that are only a
reading aid for the manual screening in screen.py.
"""
import glob
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
norm = lambda t: re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()  # noqa: E731


def load_lens(path, query):
    df = pd.read_csv(path, low_memory=False)
    return pd.DataFrame({
        "title": df["Title"], "year": df["Publication Year"], "type": df["Publication Type"],
        "venue": df["Source Title"], "doi": df["DOI"].str.lower().str.strip(), "abstract": df["Abstract"],
        "keywords": df["Keywords"].fillna("") + "; " + df["Fields of Study"].fillna(""),
        "authors": df["Author/s"], "source": "Lens.org", "query": query, "ext_id": df["Lens ID"]})


def load_ieee(path):
    df = pd.read_csv(path, low_memory=False)
    return pd.DataFrame({
        "title": df["Document Title"], "year": df["Publication Year"], "type": df["Document Identifier"],
        "venue": df["Publication Title"], "doi": df["DOI"].str.lower().str.strip(), "abstract": df["Abstract"],
        "keywords": df["Author Keywords"].fillna("") + "; " + df["IEEE Terms"].fillna(""),
        "authors": df["Authors"], "source": "IEEE Xplore", "query": "primary", "ext_id": df["PDF Link"]})


frames = [load_lens(HERE / "raw/lens_primary.csv", "primary"),
          load_lens(HERE / "raw/lens_secondary.csv", "secondary")]
for f in sorted(glob.glob(str(HERE / "raw/ieee_export_*.csv"))):
    frames.append(load_ieee(f))
allrec = pd.concat(frames, ignore_index=True)
allrec["tkey"] = allrec["title"].map(norm)
n_ident = len(allrec)

# de-duplicate: same DOI, else same normalised title
allrec["dkey"] = allrec["doi"].where(allrec["doi"].notna() & (allrec["doi"] != ""), "T:" + allrec["tkey"])
groups = {}
for i, r in allrec.iterrows():
    k = r["dkey"]
    if k not in groups:
        # a title match with an earlier DOI-keyed record also counts as a duplicate
        k2 = next((g for g, rows in groups.items() if allrec.loc[rows[0], "tkey"] == r["tkey"]), None)
        k = k2 or k
    groups.setdefault(k, []).append(i)
rows = []
for k, idx in groups.items():
    sub = allrec.loc[idx]
    best = sub.sort_values("abstract", key=lambda s: s.fillna("").str.len(), ascending=False).iloc[0]
    rows.append({**best.drop(["dkey"]).to_dict(),
                 "sources": "; ".join(sorted(set(sub["source"] + "/" + sub["query"]))), "n_copies": len(idx)})
dedup = pd.DataFrame(rows).reset_index(drop=True)
dedup.insert(0, "rid", [f"R{i + 1:04d}" for i in range(len(dedup))])

META = re.compile(r"meta[- ]?learn|few[- ]?shot|one[- ]?shot|maml|prototypical|learning to learn|siamese|metric[- ]learn|meta[- ]?(sgd|train)", re.I)
AD = re.compile(r"anomal|fault|outlier|intrusion|novelty|defect|abnormal", re.I)
txt = dedup["title"].fillna("") + " " + dedup["abstract"].fillna("") + " " + dedup["keywords"].fillna("")
dedup["pre_meta"] = txt.str.contains(META)
dedup["pre_ad"] = txt.str.contains(AD)
dedup.to_csv(HERE / "records_dedup.csv", index=False)
print(f"identified {n_ident} records -> {len(dedup)} unique ({n_ident - len(dedup)} duplicates removed)")
print("by source(s):"); print(dedup["sources"].value_counts().to_string())
print("year:", dedup["year"].value_counts().sort_index().to_dict())
print("pre-screen: meta&AD", int((dedup.pre_meta & dedup.pre_ad).sum()), "meta only", int((dedup.pre_meta & ~dedup.pre_ad).sum()),
      "AD only", int((~dedup.pre_meta & dedup.pre_ad).sum()), "neither", int((~dedup.pre_meta & ~dedup.pre_ad).sum()))
print("types:", dedup["type"].value_counts().to_dict())
