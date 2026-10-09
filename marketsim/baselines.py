"""Baseline coordination detector: pairwise correlation of signed flow with a permutation null.

This is the obvious way to look for coordinated accounts. It is kept to show why it fails when a ring
fragments its trading over many accounts: each member acts only a few times per window, so pairwise
correlations carry almost no signal while correlated honest accounts (market makers) dominate the links.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .coordination import signed_flow
from .sim import Episode


def _pairwise_window(X: np.ndarray, rng: np.random.Generator, alpha: float = 1e-3, n_shifts: int = 60,
                     min_active: int = 3) -> np.ndarray:
    n, B = X.shape
    X = X - X.mean(axis=0, keepdims=True)
    active = (X != 0).sum(axis=1) >= min_active
    Z = X - X.mean(axis=1, keepdims=True)
    sd = Z.std(axis=1, keepdims=True)
    ok = active & (sd[:, 0] > 0)
    deg = np.zeros(n)
    idx = np.flatnonzero(ok)
    if len(idx) < 3:
        return deg
    Za = Z[idx] / sd[idx]
    R = Za @ Za.T / B
    iu = np.triu_indices(len(idx), 1)
    shifts = rng.integers(0, B, size=(n_shifts, len(idx)))
    null = []
    for s in range(n_shifts):
        cols = (np.arange(B)[None, :] - shifts[s][:, None]) % B
        Zs = np.take_along_axis(Za, cols, axis=1)
        null.append((Zs @ Zs.T / B)[iu])
    thr = np.quantile(np.concatenate(null), 1 - alpha)
    edges = (R > thr) & ~np.eye(len(idx), dtype=bool)
    deg[idx] = edges.sum(axis=1)
    return deg


def pairwise_scan_episode(ep: Episode, window: int = 300, seed: int = 0) -> pd.DataFrame:
    X, aids = signed_flow(ep, window)
    rng = np.random.default_rng(seed)
    rows = []
    for w in range(X.shape[0]):
        rows.append(pd.DataFrame({"agent": aids, "window": w, "pair_degree": _pairwise_window(X[w], rng)}))
    return pd.concat(rows, ignore_index=True)
