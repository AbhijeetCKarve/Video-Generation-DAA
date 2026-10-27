"""Episodic meta-training of the VAE.

Three variants share one outer loop:

  fomaml   first-order MAML: one scalar inner learning rate, inner
           gradients treated as constants in the outer step.
  mamlpp   MAML++ ingredients that matter for a small learner on CPU:
           learnable per-layer, per-step inner learning rates (LSLR) and
           the multi-step query loss (MSL) with annealed weights.
  metasgd  Meta-SGD: a learnable per-parameter inner learning rate.

Second-order gradients can be switched on (`second_order=True`); the
default is first-order because the gain is small for this model size and
the cost on CPU is not.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import numpy as np
import torch

from . import vae
from ..data.tasks import Regime, sample_episode


@dataclass
class MetaConfig:
    variant: str = "mamlpp"         # fomaml | mamlpp | metasgd
    inner_steps: int = 3
    inner_lr: float = 0.002
    inner_clip: float = 10.0       # max L2 norm of the inner-loop gradient
    outer_lr: float = 1e-3
    meta_batch: int = 4
    n_query: int = 32
    k_shot: int = 5
    iters: int = 400
    beta: float = 0.1
    second_order: bool = False
    msl_anneal_iters: int = 200     # MAML++ multi-step loss annealing horizon
    hidden: int = 128
    latent: int = 16


class MetaLearner:
    """Holds the meta-initialisation theta* and the learned inner-loop
    learning rates, and knows how to adapt a copy of theta* to a support
    set."""

    def __init__(self, D: int, cfg: MetaConfig, seed: int):
        self.cfg = cfg
        self.D = D
        self.theta = vae.init_params(D, cfg.hidden, cfg.latent, seed)
        self.rng = np.random.default_rng(seed)
        torch.manual_seed(seed)
        self.lr_params: "OrderedDict[str, torch.Tensor]" = OrderedDict()
        if cfg.variant == "mamlpp":
            for layer in vae.LAYERS:
                self.lr_params[layer] = torch.full((cfg.inner_steps,), cfg.inner_lr).requires_grad_(True)
        elif cfg.variant == "metasgd":
            for k, v in self.theta.items():
                self.lr_params[k] = torch.full_like(v, cfg.inner_lr).requires_grad_(True)
        elif cfg.variant != "fomaml":
            raise ValueError(cfg.variant)
        self.history: List[float] = []

    # ------------------------------------------------------------ helpers
    def _lr(self, name: str, step: int) -> torch.Tensor | float:
        if self.cfg.variant == "mamlpp":
            return self.lr_params[name.split(".")[0]][step]
        if self.cfg.variant == "metasgd":
            return self.lr_params[name]
        return self.cfg.inner_lr

    def _inner_step(self, p, S: torch.Tensor, step: int, create_graph: bool):
        L = vae.loss(p, S, self.cfg.beta)
        grads = torch.autograd.grad(L, list(p.values()), create_graph=create_graph, allow_unused=True)
        # clip the inner gradient as a whole: a support set that happens to
        # hold a few clipped-at-the-edge windows would otherwise throw the
        # adapted parameters far away in one step
        norm = torch.sqrt(sum((g ** 2).sum() for g in grads if g is not None) + 1e-12)
        scale = torch.clamp(self.cfg.inner_clip / norm, max=1.0)
        new = OrderedDict()
        for (k, v), g in zip(p.items(), grads):
            if g is None:
                new[k] = v
                continue
            if not create_graph:
                g = g.detach()
                scale = scale.detach()
            new[k] = v - self._lr(k, step) * (g * scale)
        return new, L

    def adapt(self, S: np.ndarray | torch.Tensor, steps: Optional[int] = None,
              theta: Optional["OrderedDict[str, torch.Tensor]"] = None) -> "OrderedDict[str, torch.Tensor]":
        """Deployment-time adaptation: K gradient steps from theta* on a
        support set.  Returns a detached parameter set."""
        S = torch.as_tensor(S, dtype=torch.float32)
        steps = self.cfg.inner_steps if steps is None else steps
        p = vae.clone(theta if theta is not None else self.theta)
        for s in range(steps):
            idx = min(s, self.cfg.inner_steps - 1)   # reuse the last LR beyond trained steps
            p, _ = self._inner_step(p, S, idx, create_graph=False)
            p = OrderedDict((k, v.detach().requires_grad_(True)) for k, v in p.items())
        return OrderedDict((k, v.detach()) for k, v in p.items())

    # ------------------------------------------------------------ training
    def _msl_weights(self, it: int) -> np.ndarray:
        """MAML++ multi-step loss: start uniform over inner steps and anneal
        towards all weight on the final step."""
        n = self.cfg.inner_steps
        if self.cfg.variant != "mamlpp":
            w = np.zeros(n)
            w[-1] = 1.0
            return w
        frac = min(1.0, it / max(1, self.cfg.msl_anneal_iters))
        w = np.full(n, (1.0 - frac) / n)
        w[-1] += frac
        return w

    def meta_train(self, regimes: Sequence[Regime], W: int, iters: Optional[int] = None,
                   k_shot: Optional[int] = None, log_every: int = 50, verbose: bool = False) -> List[float]:
        cfg = self.cfg
        iters = cfg.iters if iters is None else iters
        k_shot = cfg.k_shot if k_shot is None else k_shot
        opt = torch.optim.Adam(list(self.theta.values()) + list(self.lr_params.values()), lr=cfg.outer_lr)
        losses = []
        for it in range(iters):
            opt.zero_grad()
            w_msl = self._msl_weights(it)
            total = 0.0
            for _ in range(cfg.meta_batch):
                reg = regimes[self.rng.integers(len(regimes))]
                S, Q = sample_episode(reg, W, k_shot, cfg.n_query, self.rng)
                S = torch.as_tensor(S)
                Q = torch.as_tensor(Q)
                p = OrderedDict(self.theta)
                task_loss = 0.0
                for s in range(cfg.inner_steps):
                    p, _ = self._inner_step(p, S, s, create_graph=cfg.second_order)
                    if w_msl[s] > 0:
                        task_loss = task_loss + w_msl[s] * vae.loss(p, Q, cfg.beta)
                if not torch.isfinite(task_loss):
                    continue                       # a bad episode must not poison theta*
                (task_loss / cfg.meta_batch).backward()
                total += float(task_loss.detach())
            torch.nn.utils.clip_grad_norm_(list(self.theta.values()), 10.0)
            if all(torch.isfinite(v.grad).all() for v in self.theta.values() if v.grad is not None):
                opt.step()
            with torch.no_grad():
                for v in self.lr_params.values():
                    v.clamp_(1e-4, 0.05)
            losses.append(total / cfg.meta_batch)
            if verbose and (it + 1) % log_every == 0:
                print(f"  meta iter {it + 1}/{iters}  query loss {np.mean(losses[-log_every:]):.3f}")
        self.history.extend(losses)
        return losses

    def state(self) -> Dict:
        return {"theta": {k: v.detach().clone() for k, v in self.theta.items()},
                "lr": {k: v.detach().clone() for k, v in self.lr_params.items()},
                "cfg": self.cfg}


def pretrain_static(D: int, X_windows: np.ndarray, cfg: MetaConfig, seed: int,
                    iters: int = 1500, batch: int = 128, lr: float = 1e-3) -> "OrderedDict[str, torch.Tensor]":
    """Ordinary (non-meta) training of the same VAE on pooled normal
    windows.  Used by the static and incremental baselines, and as the
    starting point of the non-meta fine-tuning baseline."""
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    p = vae.init_params(D, cfg.hidden, cfg.latent, seed)
    opt = torch.optim.Adam(list(p.values()), lr=lr)
    X = torch.as_tensor(X_windows)
    for _ in range(iters):
        idx = torch.as_tensor(rng.integers(0, len(X), size=batch))
        opt.zero_grad()
        L = vae.loss(p, X[idx], cfg.beta)
        L.backward()
        opt.step()
    return OrderedDict((k, v.detach()) for k, v in p.items())
