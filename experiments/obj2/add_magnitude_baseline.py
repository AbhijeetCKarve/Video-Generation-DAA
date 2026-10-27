"""A detector with no learned parameters: the mean squared standardised
value of the window.  It is the reference that tells how much of a
reconstruction detector's score comes from the size of the deviation
alone.  Rows go to within_magnitude_<dataset>.jsonl in the same format
as the learned methods, so the table script picks them up."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "obj2"))
from damad.data.cache import load_cached                      # noqa: E402
from damad.data.loaders import meta_split                     # noqa: E402
from run_obj2 import CALIB, OUT, SHOTS, evaluate_scores, jsonable, labels_last, windows3d  # noqa: E402

datasets = sys.argv[1].split(",") if len(sys.argv) > 1 else ["swat", "wadi", "hai", "smap", "msl"]
seeds = [int(s) for s in (sys.argv[2].split(",") if len(sys.argv) > 2 else "0,1,2,3,4".split(","))]
for dataset in datasets:
    ents = load_cached(dataset)
    with open(OUT / f"within_magnitude_{dataset}.jsonl", "w") as fout:
        n = 0
        for seed in seeds:
            for ent in meta_split(ents, seed)["held_out"]:
                Xw = windows3d(ent.X_test)
                yw = labels_last(ent.y_test)
                sc = (Xw ** 2).mean((1, 2)).astype(np.float64)
                for K in SHOTS:
                    if K + CALIB[dataset] + 50 >= len(Xw):
                        continue
                    m = evaluate_scores(sc, yw, K, CALIB[dataset])
                    rec = {"dataset": dataset, "seed": seed, "entity": ent.name, "method": "Magnitude", "adapt": "none",
                           "k_shot": K, "T": int(len(Xw)), "adapt_s_total": 0.0, **m}
                    fout.write(json.dumps(jsonable(rec)) + "\n")
                    n += 1
    print(dataset, n, "rows")
