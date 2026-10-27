"""Fetch the public benchmark datasets used in the DAMAD experiments.

Everything comes from raw.githubusercontent.com, so no credentials are
needed.  SWaT and WADI are licence-gated by iTrust (SUTD) and are not
downloaded here; SMAP/MSL live on an S3 bucket that is not always
reachable, so the loader accepts a manually placed copy instead.

Usage:
    python -m damad.data.download [--root data/raw] [--only hai,smd,skab,psm]
"""
from __future__ import annotations

import argparse
import sys
import time
import urllib.request
from pathlib import Path

RAW = "https://raw.githubusercontent.com"

HAI_21_03 = [f"{RAW}/icsdataset/hai/master/hai-21.03/{f}" for f in (
    "train1.csv.gz", "train2.csv.gz", "train3.csv.gz",
    "test1.csv.gz", "test2.csv.gz", "test3.csv.gz", "test4.csv.gz", "test5.csv.gz",
)]

SMD_MACHINES = (
    [f"machine-1-{i}" for i in range(1, 9)]
    + [f"machine-2-{i}" for i in range(1, 10)]
    + [f"machine-3-{i}" for i in range(1, 12)]
)
SMD = [
    f"{RAW}/NetManAIOps/OmniAnomaly/master/ServerMachineDataset/{part}/{m}.txt"
    for m in SMD_MACHINES
    for part in ("train", "test", "test_label")
]

SKAB = (
    [f"{RAW}/waico/SKAB/master/data/anomaly-free/anomaly-free.csv"]
    + [f"{RAW}/waico/SKAB/master/data/valve1/{i}.csv" for i in range(16)]
    + [f"{RAW}/waico/SKAB/master/data/valve2/{i}.csv" for i in range(4)]
    + [f"{RAW}/waico/SKAB/master/data/other/{i}.csv" for i in range(1, 15)]
)

PSM = [f"{RAW}/eBay/RANSynCoders/main/data/{f}" for f in ("train.csv", "test.csv", "test_label.csv")]

SOURCES = {"hai": HAI_21_03, "smd": SMD, "skab": SKAB, "psm": PSM}


def _dest(root: Path, name: str, url: str) -> Path:
    # keep the path after the repository branch so files stay organised
    tail = url.split("/master/", 1)[-1] if "/master/" in url else url.split("/main/", 1)[-1]
    if name == "hai":
        tail = tail.replace("hai-21.03/", "")
    if name == "smd":
        tail = tail.replace("ServerMachineDataset/", "")
    if name == "skab":
        tail = tail.replace("data/", "")
    if name == "psm":
        tail = tail.replace("data/", "")
    return root / name / tail


def fetch(url: str, dest: Path, retries: int = 4) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    delay = 2.0
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(dest, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            return True
        except Exception as e:  # noqa: BLE001
            print(f"  retry {attempt + 1}/{retries} for {url}: {e}", file=sys.stderr)
            if dest.exists():
                dest.unlink()
            time.sleep(delay)
            delay *= 2
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/raw")
    ap.add_argument("--only", default="hai,smd,skab,psm")
    args = ap.parse_args()
    root = Path(args.root)
    failed = []
    for name in args.only.split(","):
        urls = SOURCES[name]
        print(f"[{name}] {len(urls)} files")
        for url in urls:
            dest = _dest(root, name, url)
            ok = fetch(url, dest)
            print(f"  {'ok ' if ok else 'ERR'} {dest}")
            if not ok:
                failed.append(url)
    if failed:
        print(f"{len(failed)} files failed:\n  " + "\n  ".join(failed), file=sys.stderr)
        return 1
    print("all files present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
