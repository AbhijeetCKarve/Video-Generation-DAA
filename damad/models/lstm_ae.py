"""LSTM autoencoder on (L, d) sensor windows, in the encoder-decoder
scheme of Malhotra et al. (2016).

Encoder: LSTM(d->h1) -> LSTM(h1->h2) -> last hidden state -> Linear(h2->z)
Decoder: repeat z over L steps -> LSTM(z->h2) -> LSTM(h2->h1) -> Linear(h1->d)

The anomaly score of a window is its mean squared reconstruction error.
A plain MLP autoencoder on the flattened window is provided as the
"does temporal modelling pay" control.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class LSTMAE(nn.Module):
    def __init__(self, d: int, L: int = 30, h1: int = 64, h2: int = 32, z: int = 16):
        super().__init__()
        self.L = L
        self.enc1 = nn.LSTM(d, h1, batch_first=True)
        self.enc2 = nn.LSTM(h1, h2, batch_first=True)
        self.fc_z = nn.Linear(h2, z)
        self.dec1 = nn.LSTM(z, h2, batch_first=True)
        self.dec2 = nn.LSTM(h2, h1, batch_first=True)
        self.fc_out = nn.Linear(h1, d)

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        o, _ = self.enc1(x)
        _, (h, _) = self.enc2(o)
        return self.fc_z(h[-1])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.encode(x)
        zr = z.unsqueeze(1).expand(-1, self.L, -1)
        o, _ = self.dec1(zr)
        o, _ = self.dec2(o)
        return self.fc_out(o)

    def loss(self, x: torch.Tensor) -> torch.Tensor:
        return ((self(x) - x) ** 2).mean()

    @torch.no_grad()
    def score(self, x: torch.Tensor, batch: int = 512) -> torch.Tensor:
        out = []
        for i in range(0, len(x), batch):
            xb = x[i:i + batch]
            out.append(((self(xb) - xb) ** 2).mean((1, 2)))
        return torch.cat(out)


class MLPAE(nn.Module):
    def __init__(self, d: int, L: int = 30, h: int = 128, z: int = 16):
        super().__init__()
        D = d * L
        self.L, self.d = L, d
        self.net = nn.Sequential(nn.Linear(D, h), nn.ELU(), nn.Linear(h, z), nn.ELU(),
                                 nn.Linear(z, h), nn.ELU(), nn.Linear(h, D))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x.reshape(len(x), -1)).reshape(len(x), self.L, self.d)

    def loss(self, x: torch.Tensor) -> torch.Tensor:
        return ((self(x) - x) ** 2).mean()

    @torch.no_grad()
    def score(self, x: torch.Tensor, batch: int = 2048) -> torch.Tensor:
        out = []
        for i in range(0, len(x), batch):
            xb = x[i:i + batch]
            out.append(((self(xb) - xb) ** 2).mean((1, 2)))
        return torch.cat(out)


def n_params(m: nn.Module) -> int:
    return int(sum(p.numel() for p in m.parameters()))


def param_vector(m: nn.Module) -> torch.Tensor:
    return torch.cat([p.detach().reshape(-1) for p in m.parameters()])
