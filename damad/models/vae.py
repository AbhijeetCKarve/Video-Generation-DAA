"""A small variational autoencoder written in functional style.

Parameters live in an ordered dict of tensors so that an inner-loop
update can produce a fresh parameter set without touching the module,
which is what MAML-style training needs.  The architecture is a plain
MLP on flattened windows: D -> H -> (mu, logvar) -> H -> D.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Dict, Tuple

import torch
import torch.nn.functional as F

Params = "OrderedDict[str, torch.Tensor]"


def init_params(D: int, H: int, Z: int, seed: int) -> "OrderedDict[str, torch.Tensor]":
    g = torch.Generator().manual_seed(seed)

    def lin(i, o):
        w = torch.randn(o, i, generator=g) * (2.0 / (i + o)) ** 0.5
        return w.requires_grad_(True), torch.zeros(o).requires_grad_(True)

    p = OrderedDict()
    p["enc1.w"], p["enc1.b"] = lin(D, H)
    p["enc2.w"], p["enc2.b"] = lin(H, H // 2)
    p["mu.w"], p["mu.b"] = lin(H // 2, Z)
    p["lv.w"], p["lv.b"] = lin(H // 2, Z)
    p["dec1.w"], p["dec1.b"] = lin(Z, H // 2)
    p["dec2.w"], p["dec2.b"] = lin(H // 2, H)
    p["out.w"], p["out.b"] = lin(H, D)
    return p


LAYERS = ["enc1", "enc2", "mu", "lv", "dec1", "dec2", "out"]


def encode(p, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    h = F.elu(F.linear(x, p["enc1.w"], p["enc1.b"]))
    h = F.elu(F.linear(h, p["enc2.w"], p["enc2.b"]))
    mu = F.linear(h, p["mu.w"], p["mu.b"])
    lv = F.linear(h, p["lv.w"], p["lv.b"]).clamp(-8.0, 6.0)
    return mu, lv


def decode(p, z: torch.Tensor) -> torch.Tensor:
    h = F.elu(F.linear(z, p["dec1.w"], p["dec1.b"]))
    h = F.elu(F.linear(h, p["dec2.w"], p["dec2.b"]))
    return F.linear(h, p["out.w"], p["out.b"])


def loss(p, x: torch.Tensor, beta: float = 0.1, sample: bool = True) -> torch.Tensor:
    """Negative ELBO per window, averaged over the batch."""
    mu, lv = encode(p, x)
    z = mu + torch.randn_like(mu) * torch.exp(0.5 * lv) if sample else mu
    xr = decode(p, z)
    rec = ((xr - x) ** 2).sum(1)
    kl = -0.5 * (1 + lv - mu ** 2 - lv.exp()).sum(1)
    return (rec + beta * kl).mean()


@torch.no_grad()
def score(p, x: torch.Tensor) -> torch.Tensor:
    """Anomaly score: mean squared reconstruction error through the
    posterior mean.  Deterministic so that two calls agree."""
    mu, _ = encode(p, x)
    xr = decode(p, mu)
    return ((xr - x) ** 2).mean(1)


@torch.no_grad()
def embed(p, x: torch.Tensor) -> torch.Tensor:
    return encode(p, x)[0]


def clone(p) -> "OrderedDict[str, torch.Tensor]":
    return OrderedDict((k, v.detach().clone().requires_grad_(True)) for k, v in p.items())


def n_params(p) -> int:
    return int(sum(v.numel() for v in p.values()))
