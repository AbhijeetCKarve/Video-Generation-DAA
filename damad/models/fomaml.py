"""First-order MAML for nn.Module autoencoders, with the gradient-path
correction made explicit and the broken pattern kept as a control.

The inner loop adapts a *copy* of the meta-model.  In the broken
pattern the query loss is back-propagated on the copy and the outer
optimiser is then stepped on the original: the original's parameters
hold no gradient, the step is a no-op, and the meta-model never leaves
its initialisation while the loss curve looks ordinary.  The corrected
pattern takes the query gradient on the copy and writes it onto the
meta-parameters before the step.  `meta_train` records the parameter
change per outer step so that the difference is measurable, not
asserted.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np
import torch
import torch.nn as nn

from .lstm_ae import param_vector


@dataclass
class FOMAMLConfig:
    inner_lr: float = 0.1
    outer_lr: float = 1e-3
    inner_steps: int = 5
    meta_batch: int = 4
    support: int = 20
    query: int = 20
    outer_steps: int = 1000
    clip: float = 1.0
    broken: bool = False            # reproduce the gradient-path bug


def inner_adapt(model: nn.Module, S: torch.Tensor, steps: int, lr: float) -> nn.Module:
    """K-step SGD adaptation of a fresh copy on support windows."""
    learner = copy.deepcopy(model)
    learner.train()
    opt = torch.optim.SGD(learner.parameters(), lr=lr)
    for _ in range(steps):
        opt.zero_grad()
        learner.loss(S).backward()
        torch.nn.utils.clip_grad_norm_(learner.parameters(), 1.0)
        opt.step()
    learner.eval()
    return learner


def meta_train(model: nn.Module, sample_task: Callable[[np.random.Generator], tuple],
               cfg: FOMAMLConfig, seed: int, val_task: Optional[Callable[[], tuple]] = None,
               log_every: int = 100, verbose: bool = False) -> Dict:
    """`sample_task(rng)` returns (support, query) tensors of one task.
    Returns a history with the train loss, the validation query loss
    after adaptation (if a validation task is given) and the L2 change
    of the meta-parameters at every outer step."""
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    opt = torch.optim.Adam(model.parameters(), lr=cfg.outer_lr)
    hist = {"loss": [], "val": [], "param_change": [], "step": []}
    best_val, best_state = float("inf"), copy.deepcopy(model.state_dict())
    for step in range(1, cfg.outer_steps + 1):
        before = param_vector(model)
        model.train()
        grads = [torch.zeros_like(p) for p in model.parameters()]
        total = 0.0
        for _ in range(cfg.meta_batch):
            S, Q = sample_task(rng)
            learner = inner_adapt(model, S, cfg.inner_steps, cfg.inner_lr)
            learner.train()
            Lq = learner.loss(Q)
            total += float(Lq.detach())
            if cfg.broken:
                # the bug: gradient lands on the copy, never on the meta-model
                Lq.backward()
            else:
                g = torch.autograd.grad(Lq, list(learner.parameters()), allow_unused=True)
                for acc, gi in zip(grads, g):
                    if gi is not None:
                        acc += gi.detach()
        opt.zero_grad()
        if not cfg.broken:
            for p, g in zip(model.parameters(), grads):
                p.grad = g / cfg.meta_batch
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.clip)
        opt.step()
        hist["loss"].append(total / cfg.meta_batch)
        hist["param_change"].append(float((param_vector(model) - before).norm()))
        if val_task is not None and (step % log_every == 0 or step == cfg.outer_steps):
            S, Q = val_task()
            learner = inner_adapt(model, S, cfg.inner_steps, cfg.inner_lr)
            with torch.no_grad():
                v = float(learner.loss(Q))
            hist["val"].append(v)
            hist["step"].append(step)
            if v < best_val:
                best_val, best_state = v, copy.deepcopy(model.state_dict())
            if verbose:
                print(f"    step {step:5d} train {hist['loss'][-1]:.4f} val {v:.4f} "
                      f"|dtheta| {hist['param_change'][-1]:.2e}", flush=True)
    if val_task is not None:
        model.load_state_dict(best_state)
    model.eval()
    hist["best_val"] = best_val
    return hist


def train_static(model: nn.Module, windows: np.ndarray, steps: int, seed: int, batch: int = 64,
                 lr: float = 1e-3, val_frac: float = 0.1) -> Dict:
    """Ordinary training of the same autoencoder on pooled normal windows,
    with early stopping on a held-out slice."""
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    X = torch.as_tensor(windows)
    perm = rng.permutation(len(X))
    n_val = max(32, int(val_frac * len(X)))
    val, tr = X[perm[:n_val]], X[perm[n_val:]]
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    best, best_state, hist = float("inf"), copy.deepcopy(model.state_dict()), []
    for step in range(1, steps + 1):
        model.train()
        idx = torch.as_tensor(rng.integers(0, len(tr), size=batch))
        opt.zero_grad()
        L = model.loss(tr[idx])
        L.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % 100 == 0 or step == steps:
            model.eval()
            with torch.no_grad():
                v = float(model.loss(val[:1024]))
            hist.append((step, float(L.detach()), v))
            if v < best:
                best, best_state = v, copy.deepcopy(model.state_dict())
    model.load_state_dict(best_state)
    model.eval()
    return {"hist": hist, "best_val": best}
