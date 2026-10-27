"""Every method in the study expressed as a configuration of the one
streaming loop, plus the Isolation Forest baseline which has its own
scorer.

Naming used in the paper:

  IF           Isolation Forest on windows, static
  VAE-S        VAE trained on pooled normal data, no adaptation
  VAE-FT       VAE-S fine-tuned on the K-shot support set, then static
  VAE-INC      VAE-S updated online on every non-alarmed window (Wahab-style)
  VAE-DFT      drift-aware fine-tuning: ADWIN+MMD gate, fine-tune VAE-S on
               the post-drift support, recalibrate tau (no meta-learning)
  MAML-1       MAML++-initialised VAE, adapted once at the start (MAVAE-style)
  MSGD-1       Meta-SGD-initialised VAE, adapted once at the start
  OML-A        MMD-triggered meta-adaptation, no memory, no recalibration
               (OMLog-style transfer of the idea to sensor streams)
  DAMAD        the full method

Ablations:
  DAMAD-noM1   episodes from fixed chunks instead of ADWIN-bounded regimes
  DAMAD-rndM1  episodes drawn from anywhere in the stream
  DAMAD-noM3   no replay from the regime memory
  DAMAD-noM4   no threshold recalibration
  DAMAD-noAcc  no acceptance test on adaptations (SP3 disambiguation off)
  DAMAD-adwin  ADWIN only as the gate
  DAMAD-mmd    MMD only as the gate
  DAMAD-fo     FOMAML initialisation instead of MAML++
  DAMAD-msgd   Meta-SGD initialisation instead of MAML++
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict

from ..online.detector import OnlineConfig


@dataclass(frozen=True)
class MethodSpec:
    name: str
    online: OnlineConfig | None       # None for Isolation Forest
    meta_variant: str = "mamlpp"      # which meta-learner to use, if any
    episode_sampler: str = "drift"    # how meta-training regimes are cut
    group: str = "baseline"           # baseline | proposed | ablation


_D = OnlineConfig(name="DAMAD")

METHODS: Dict[str, MethodSpec] = {
    "IF": MethodSpec("IF", None, group="baseline"),
    "VAE-S": MethodSpec("VAE-S", OnlineConfig(name="VAE-S", init="static", adapt_on_start=False, drift_policy="none", detector="none")),
    "VAE-FT": MethodSpec("VAE-FT", OnlineConfig(name="VAE-FT", init="static", adapt_on_start=True, drift_policy="finetune", detector="none")),
    "VAE-INC": MethodSpec("VAE-INC", OnlineConfig(name="VAE-INC", init="static", adapt_on_start=False, drift_policy="incremental", detector="none", inc_every=5)),
    "VAE-DFT": MethodSpec("VAE-DFT", OnlineConfig(name="VAE-DFT", init="static", adapt_on_start=True, drift_policy="finetune", detector="adwin+mmd", recalibrate=True)),
    "MAML-1": MethodSpec("MAML-1", OnlineConfig(name="MAML-1", init="meta", adapt_on_start=True, drift_policy="none", detector="none"), meta_variant="mamlpp"),
    "MSGD-1": MethodSpec("MSGD-1", OnlineConfig(name="MSGD-1", init="meta", adapt_on_start=True, drift_policy="none", detector="none"), meta_variant="metasgd"),
    "OML-A": MethodSpec("OML-A", OnlineConfig(name="OML-A", init="meta", adapt_on_start=True, drift_policy="meta_adapt", detector="mmd", replay=False, recalibrate=False), meta_variant="mamlpp"),
    "DAMAD": MethodSpec("DAMAD", _D, group="proposed"),
    "DAMAD-noM1": MethodSpec("DAMAD-noM1", replace(_D, name="DAMAD-noM1"), episode_sampler="chunk", group="ablation"),
    "DAMAD-rndM1": MethodSpec("DAMAD-rndM1", replace(_D, name="DAMAD-rndM1"), episode_sampler="random", group="ablation"),
    "DAMAD-noM3": MethodSpec("DAMAD-noM3", replace(_D, name="DAMAD-noM3", replay=False), group="ablation"),
    "DAMAD-noM4": MethodSpec("DAMAD-noM4", replace(_D, name="DAMAD-noM4", recalibrate=False), group="ablation"),
    "DAMAD-noAcc": MethodSpec("DAMAD-noAcc", replace(_D, name="DAMAD-noAcc", accept_test=False), group="ablation"),
    "DAMAD-adwin": MethodSpec("DAMAD-adwin", replace(_D, name="DAMAD-adwin", detector="adwin"), group="ablation"),
    "DAMAD-mmd": MethodSpec("DAMAD-mmd", replace(_D, name="DAMAD-mmd", detector="mmd"), group="ablation"),
    "DAMAD-fo": MethodSpec("DAMAD-fo", replace(_D, name="DAMAD-fo"), meta_variant="fomaml", group="ablation"),
    "DAMAD-msgd": MethodSpec("DAMAD-msgd", replace(_D, name="DAMAD-msgd"), meta_variant="metasgd", group="ablation"),
}

BASELINES = [m for m, s in METHODS.items() if s.group == "baseline"]
ABLATIONS = [m for m, s in METHODS.items() if s.group == "ablation"]


def needs_meta(spec: MethodSpec) -> bool:
    return spec.online is not None and spec.online.init == "meta"


def needs_static(spec: MethodSpec) -> bool:
    return spec.online is not None and spec.online.init == "static"
