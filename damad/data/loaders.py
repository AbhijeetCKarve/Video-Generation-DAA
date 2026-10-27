"""Unified loaders for the benchmark datasets.

Each dataset is turned into a list of `Entity` objects.  An entity is one
monitored unit (a server machine, a testbed run, an ICS test campaign)
with a normal-only training stream and a labelled test stream.  Values
are standardised with the entity's own training statistics so that a
window from any entity lives on roughly the same scale.

Datasets
--------
smd   Server Machine Dataset, 28 machines, 38 metrics, 1-minute samples.
psm   Pooled Server Metrics (eBay), 25 features, 1-minute samples.
skab  Skoltech Anomaly Benchmark, 8 sensors on a water-circulation rig,
      1-second samples, 34 short experiments with labelled faults.
hai   HAI 21.03, hardware-in-the-loop ICS testbed (boiler, turbine,
      water treatment), ~79 tags at 1 Hz, 3 training and 5 attack
      campaigns.  Downsampled to 10 s by block means.
smap / msl  NASA telemetry (optional; only if the files are present).
"""
from __future__ import annotations

import gzip
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

DEFAULT_ROOT = Path("data/raw")
CLIP = 10.0   # standardised values are clipped here; a sensor that barely moves in training
              # would otherwise turn ordinary test noise into values in the thousands


@dataclass
class Entity:
    dataset: str
    name: str
    X_train: np.ndarray          # (T_tr, d) standardised, normal only
    X_test: np.ndarray           # (T_te, d) standardised
    y_test: np.ndarray           # (T_te,) 0/1
    mu: np.ndarray = field(repr=False, default=None)
    sd: np.ndarray = field(repr=False, default=None)

    @property
    def d(self) -> int:
        return self.X_train.shape[1]

    def __repr__(self) -> str:  # pragma: no cover
        return (f"Entity({self.dataset}/{self.name}, d={self.d}, "
                f"train={len(self.X_train)}, test={len(self.X_test)}, "
                f"anom={int(self.y_test.sum())})")


def _standardise(train: np.ndarray, *others: np.ndarray):
    mu = train.mean(0)
    sd = train.std(0)
    sd[sd < 1e-6] = 1.0           # constant tags stay constant instead of exploding
    out = [np.clip((a - mu) / sd, -CLIP, CLIP).astype(np.float32) for a in (train, *others)]
    return mu.astype(np.float32), sd.astype(np.float32), out


def _clean(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float64)
    a = pd.DataFrame(a).ffill().bfill().fillna(0.0).to_numpy()
    return np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)


# --------------------------------------------------------------------- SMD
SMD_MACHINES = (
    [f"machine-1-{i}" for i in range(1, 9)]
    + [f"machine-2-{i}" for i in range(1, 10)]
    + [f"machine-3-{i}" for i in range(1, 12)]
)


def load_smd(root: Path = DEFAULT_ROOT) -> List[Entity]:
    base = root / "smd"
    ents = []
    for m in SMD_MACHINES:
        tr = np.loadtxt(base / "train" / f"{m}.txt", delimiter=",")
        te = np.loadtxt(base / "test" / f"{m}.txt", delimiter=",")
        y = np.loadtxt(base / "test_label" / f"{m}.txt").astype(int)
        mu, sd, (tr, te) = _standardise(_clean(tr), _clean(te))
        ents.append(Entity("smd", m, tr, te, y, mu, sd))
    return ents


# --------------------------------------------------------------------- PSM
def load_psm(root: Path = DEFAULT_ROOT) -> List[Entity]:
    base = root / "psm"
    tr = pd.read_csv(base / "train.csv").iloc[:, 1:].to_numpy()
    te = pd.read_csv(base / "test.csv").iloc[:, 1:].to_numpy()
    y = pd.read_csv(base / "test_label.csv").iloc[:, 1].to_numpy().astype(int)
    mu, sd, (tr, te) = _standardise(_clean(tr), _clean(te))
    return [Entity("psm", "psm", tr, te, y, mu, sd)]


# -------------------------------------------------------------------- SKAB
SKAB_FILES = (
    [f"valve1/{i}.csv" for i in range(16)]
    + [f"valve2/{i}.csv" for i in range(4)]
    + [f"other/{i}.csv" for i in range(1, 15)]
)


def load_skab(root: Path = DEFAULT_ROOT) -> List[Entity]:
    """One entity per experiment.  The rig is re-configured between runs
    (the anomaly-free recording sits at a very different flow level from
    most experiments), so each experiment is standardised with the
    statistics of its own normal prefix and that prefix is its training
    stream.  This makes SKAB a genuine few-shot setting: a detector meets
    a new run and has only its first few hundred seconds of normal
    operation to work with."""
    base = root / "skab"
    ents = []
    for f in SKAB_FILES:
        df = pd.read_csv(base / f, sep=";", index_col="datetime")
        y = df["anomaly"].to_numpy().astype(int)
        X = _clean(df.drop(columns=["anomaly", "changepoint"]).to_numpy())
        first = int(np.argmax(y > 0)) if y.any() else len(y)
        prefix = X[: max(first - 10, 0)]
        if len(prefix) < 60:            # one run has almost no normal prefix; skip it
            continue
        mu, sd, (tr, te) = _standardise(prefix, X)
        ents.append(Entity("skab", f.replace("/", "-").replace(".csv", ""), tr, te, y, mu, sd))
    return ents


# --------------------------------------------------------------------- HAI
def _read_hai(path: Path) -> pd.DataFrame:
    with gzip.open(path, "rb") as fh:
        raw = fh.read()
    return pd.read_csv(io.BytesIO(raw))


def _block_mean(X: np.ndarray, y: Optional[np.ndarray], k: int):
    n = (len(X) // k) * k
    Xb = X[:n].reshape(-1, k, X.shape[1]).mean(1)
    yb = None if y is None else y[:n].reshape(-1, k).max(1)
    return Xb, yb


def load_hai(root: Path = DEFAULT_ROOT, step: int = 10) -> List[Entity]:
    """HAI 21.03.  Training = the three attack-free campaigns pooled;
    one entity per test campaign.  The attack column is the label.  All
    streams are downsampled by block means over `step` seconds."""
    base = root / "hai"
    trains = [_read_hai(base / f"train{i}.csv.gz") for i in (1, 2, 3)]
    cols = [c for c in trains[0].columns if c.lower() != "time" and not c.lower().startswith("attack")]
    tr_parts = []
    for df in trains:
        X = _clean(df[cols].to_numpy())
        Xb, _ = _block_mean(X, None, step)
        tr_parts.append(Xb)
    tr_all = np.concatenate(tr_parts, 0)
    mu = tr_all.mean(0)
    sd = tr_all.std(0)
    sd[sd < 1e-6] = 1.0
    ents = []
    for i in (1, 2, 3, 4, 5):
        df = _read_hai(base / f"test{i}.csv.gz")
        lab = df["attack"].to_numpy().astype(int)
        X = _clean(df[cols].to_numpy())
        Xb, yb = _block_mean(X, lab, step)
        te = np.clip((Xb - mu) / sd, -CLIP, CLIP).astype(np.float32)
        tr = np.clip((tr_all - mu) / sd, -CLIP, CLIP).astype(np.float32)
        ents.append(Entity("hai", f"test{i}", tr, te, yb.astype(int), mu.astype(np.float32), sd.astype(np.float32)))
    # keep the per-campaign training streams so that regimes can be carved
    # from them separately (they were recorded weeks apart)
    for e in ents:
        e.train_segments = [np.clip((p - mu) / sd, -CLIP, CLIP).astype(np.float32) for p in tr_parts]  # type: ignore[attr-defined]
    return ents


# --------------------------------------------------------------- SMAP/MSL
def load_nasa(which: str, root: Path = DEFAULT_ROOT) -> List[Entity]:
    """Optional.  Expects data/raw/nasa/{train,test}/<chan>.npy and
    data/raw/nasa/labeled_anomalies.csv from the telemanom release."""
    base = root / "nasa"
    meta = base / "labeled_anomalies.csv"
    if not meta.exists():
        return []
    df = pd.read_csv(meta)
    df = df[df["spacecraft"] == which.upper()]
    ents = []
    for _, row in df.iterrows():
        ch = row["chan_id"]
        tr = np.load(base / "train" / f"{ch}.npy")
        te = np.load(base / "test" / f"{ch}.npy")
        y = np.zeros(len(te), dtype=int)
        for a, b in eval(row["anomaly_sequences"]):
            y[a:b + 1] = 1
        mu, sd, (tr, te) = _standardise(_clean(tr), _clean(te))
        ents.append(Entity(which.lower(), ch, tr, te, y, mu, sd))
    return ents


LOADERS = {
    "smd": load_smd,
    "psm": load_psm,
    "skab": load_skab,
    "hai": load_hai,
    "smap": lambda root=DEFAULT_ROOT: load_nasa("smap", root),
    "msl": lambda root=DEFAULT_ROOT: load_nasa("msl", root),
}


def load(name: str, root: Path = DEFAULT_ROOT) -> List[Entity]:
    return LOADERS[name](root)


# ------------------------------------------------------------------ splits
def meta_split(ents: List[Entity], seed: int, holdout_frac: float = 0.3) -> Dict[str, List[Entity]]:
    """Split entities into meta-train and held-out sets.  Single-entity
    datasets (psm) and HAI (shared training pool) return everything as
    held-out with the training pool used for meta-training."""
    if len(ents) == 1 or ents[0].dataset == "hai":
        return {"meta_train": ents, "held_out": ents}
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(ents))
    n_ho = max(1, int(round(holdout_frac * len(ents))))
    ho = sorted(idx[:n_ho])
    mt = sorted(idx[n_ho:])
    return {"meta_train": [ents[i] for i in mt], "held_out": [ents[i] for i in ho]}
