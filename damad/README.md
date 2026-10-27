# DAMAD — Drift-Aware Meta-Adaptive Detector

Reference implementation and benchmark harness for the paper
*Meta-learning for few-shot anomaly detection in streaming industrial IoT*.
Everything here runs on a CPU; the full study (4 datasets, 18 methods,
5 seeds) takes a few hours on four cores.

## Layout

```
damad/
  data/        download.py (fetch HAI, SMD, SKAB, PSM), loaders.py (Entity objects),
               windows.py, drift.py (sudden / gradual / incremental / recurring injection),
               tasks.py (regime segmentation and episodes), cache.py
  models/      vae.py (functional MLP-VAE), meta.py (FOMAML, MAML++, Meta-SGD, static pretraining)
  online/      adwin.py, mmd.py, threshold.py (POT), memory.py (regime buffer),
               detector.py (the one streaming loop every method runs through)
  baselines/   registry.py (every method and ablation as a configuration), iforest.py
  eval/        metrics.py (point-wise P/R/F1, AUROC/AUPRC, latency, FPR under drift, adaptation steps)
experiments/
  run_all.py        the study; one job per (dataset, seed)
  make_tables.py    Markdown + LaTeX tables and results/summary.json
  make_figures.py   all figures
paper/              manuscript sources
```

## Reproduce

```bash
pip install torch numpy pandas scipy scikit-learn matplotlib
python -m damad.data.download            # ~750 MB into data/raw
python experiments/run_all.py --workers 4
python experiments/make_tables.py
python experiments/make_figures.py
```

`--quick` runs a few-iteration version of everything in minutes for a
smoke test.  SMAP/MSL are supported by `loaders.load_nasa` if the
telemanom release is placed under `data/raw/nasa/`; SWaT and WADI need a
licence from iTrust and are not fetched.

## How a method is defined

Every method is an `OnlineConfig` (see `damad/online/detector.py`).  The
streaming loop never looks ahead: scoring, drift confirmation, support-set
collection, adaptation, threshold recalibration and the champion/challenger
shadow period all happen in stream order, so the latency and adaptation
numbers in the paper are the numbers an operator would see.

| name       | init   | on drift           | gate        | replay | tau recal | notes                                   |
|------------|--------|--------------------|-------------|--------|-----------|-----------------------------------------|
| IF         | –      | –                  | –           | –      | –         | Isolation Forest on windows             |
| VAE-S      | static | nothing            | –           | –      | –         | pooled normal data, one threshold       |
| VAE-FT     | static | fine-tune once     | –           | –      | –         | K-shot fine-tune at stream start        |
| VAE-INC    | static | SGD every 5 steps  | –           | –      | –         | Wahab-style online learning             |
| VAE-DFT    | static | fine-tune          | ADWIN+MMD   | –      | yes       | drift-aware, no meta-learning           |
| MAML-1     | meta   | nothing            | –           | –      | –         | MAVAE-style, adapt once                 |
| MSGD-1     | meta   | nothing            | –           | –      | –         | Meta-SGD initialisation, adapt once     |
| OML-A      | meta   | K-step adapt       | MMD         | –      | –         | OMLog idea on sensor streams            |
| DAMAD      | meta   | K-step adapt       | ADWIN+MMD   | yes    | yes       | proposed                                |

## Offline meta-learning study (paper2/)

A second study uses the same loaders, metrics and threshold rule for an
offline question: does an LSTM autoencoder trained with first-order MAML
actually train, adapt and detect?  Its code is `damad/models/lstm_ae.py`,
`damad/models/fomaml.py` (corrected FOMAML plus the broken-gradient-path
control), `damad/data/regimes.py` (k-means regimes as tasks) and
`experiments/obj2/`.

```
python experiments/obj2/run_obj2.py --workers 4            # 25 within-plant + 30 transfer jobs
python experiments/obj2/run_obj2.py --datasets hai,swat,wadi --seeds 0,1 --transfer 0 --outer 3000 --tag _long
python experiments/obj2/add_magnitude_baseline.py          # parameter-free reference rows
python experiments/obj2/make_tables_obj2.py                # results/obj2/tables, figures/obj2
```

Raw rows go to `results/obj2/*.jsonl` (not tracked); tables and the
meta-training logs (`results/obj2/meta_*.json`) are tracked.
