"""Parsed entities cached as .npz so that a worker process does not spend
a minute re-reading HAI's gzipped CSVs."""
from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np

from .loaders import Entity, load

CACHE = Path("data/cache")


def load_cached(name: str) -> List[Entity]:
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{name}.npz"
    if f.exists():
        z = np.load(f, allow_pickle=True)
        ents = []
        for i in range(int(z["n"])):
            e = Entity(name, str(z[f"name{i}"]), z[f"tr{i}"], z[f"te{i}"], z[f"y{i}"], z[f"mu{i}"], z[f"sd{i}"])
            k = f"nseg{i}"
            if k in z.files:
                e.train_segments = [z[f"seg{i}_{j}"] for j in range(int(z[k]))]  # type: ignore[attr-defined]
            ents.append(e)
        return ents
    ents = load(name)
    pack = {"n": len(ents)}
    for i, e in enumerate(ents):
        pack[f"name{i}"] = e.name
        pack[f"tr{i}"], pack[f"te{i}"], pack[f"y{i}"], pack[f"mu{i}"], pack[f"sd{i}"] = e.X_train, e.X_test, e.y_test, e.mu, e.sd
        segs = getattr(e, "train_segments", None)
        if segs:
            pack[f"nseg{i}"] = len(segs)
            for j, s in enumerate(segs):
                pack[f"seg{i}_{j}"] = s
    np.savez_compressed(f, **pack)
    return ents
