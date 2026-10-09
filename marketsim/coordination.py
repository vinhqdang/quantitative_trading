"""Label-free detection of coordinated accounts: a circular-shift coincidence test.

Accounts in a ring act at (nearly) the same moments and on the same side more often than independent
accounts would. For every account and window the statistic counts its order submissions that coincide
(within a tolerance, same side) with submissions by *any other* account. Pooling over partners gives far more
power than testing account pairs, which fails when each member acts only a few times per window.

The null distribution is exact: the account's own submission times are cyclically shifted over all
possible offsets while everyone else stays fixed. That preserves the account's own rhythm and the market's
activity pattern and destroys only the alignment between them, so the p-value is calibrated without labels and
without knowing who the manipulators are. Three tolerances are combined by taking the maximum of the
standardised statistics, and the same maximum is applied to every shift, so the p-value stays exact.
No labels, simulator knowledge or manipulation examples are used.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .exchange import MKT, NEW
from .sim import Episode


def signed_flow(ep: Episode, window: int = 300, bin_len: int = 10) -> tuple[np.ndarray, np.ndarray]:
    """Tensor [window, agent, bin] of signed submitted quantity, and the agent ids (row order)."""
    cfg = ep.config
    ev = ep.events
    ev = ev[(ev.t >= cfg.warmup) & ev.kind.isin([NEW, MKT])]
    n_win = int((cfg.steps - cfg.warmup) // window)
    n_bin = window // bin_len
    rel = (ev.t.to_numpy() - cfg.warmup)
    w = rel // window
    b = (rel % window) // bin_len
    keep = w < n_win
    n_agent = int(ep.agents.aid.max()) + 1
    X = np.zeros((n_win, n_agent, n_bin))
    np.add.at(X, (w[keep], ev.agent.to_numpy()[keep], b[keep]), (ev.side * ev.qty).to_numpy()[keep])
    return X, ep.agents.aid.to_numpy()


def _circ_box(x: np.ndarray, tol: int) -> np.ndarray:
    """Sum of x over offsets -tol..+tol along the last axis (circular)."""
    out = x.copy()
    for d in range(1, tol + 1):
        out += np.roll(x, d, axis=-1) + np.roll(x, -d, axis=-1)
    return out


def coincidence_scan(flow: np.ndarray, tols=(1, 5, 15)) -> tuple[np.ndarray, np.ndarray]:
    """flow: [side(2), agent, step] submission counts of one window. Returns (z, p) per agent.

    z is the observed maximum standardised coincidence statistic; p is its exact circular-shift p-value.
    """
    n, T = flow.shape[1], flow.shape[2]
    total = flow.sum(axis=1)                                   # [side, step]
    stats = []
    for tol in tols:
        corr = np.zeros((n, T))
        for sd in range(2):
            others = _circ_box(total[sd][None, :] - flow[sd], tol)   # everyone else, widened
            Fo = np.fft.rfft(others, axis=1)
            Fa = np.fft.rfft(flow[sd], axis=1)
            corr += np.fft.irfft(Fo * np.conj(Fa), n=T, axis=1)      # corr[:, k] = statistic at shift k
        mu = corr.mean(axis=1, keepdims=True)
        sdv = corr.std(axis=1, keepdims=True)
        stats.append((corr - mu) / np.where(sdv > 0, sdv, 1.0))
    zmax = np.max(stats, axis=0)                               # [agent, shift]; shift 0 is the observed alignment
    obs = zmax[:, 0]
    p = (zmax >= obs[:, None]).mean(axis=1)
    return obs, p


def submission_flow_from_events(events: pd.DataFrame, n_agent: int, steps: int, warmup: int = 0,
                                window: int = 300) -> np.ndarray:
    """Tensor [window, side(2), agent, step] of order submission counts (limit and market orders).

    `events` needs columns t, kind, agent, side (see exchange.EVENT_COLUMNS); agent ids are 0..n_agent-1.
    """
    ev = events[(events.t >= warmup) & events.kind.isin([NEW, MKT])]
    n_win = int((steps - warmup) // window)
    rel = ev.t.to_numpy() - warmup
    w, st = rel // window, rel % window
    keep = w < n_win
    F = np.zeros((n_win, 2, n_agent, window))
    side = (ev.side.to_numpy() < 0).astype(int)
    np.add.at(F, (w[keep], side[keep], ev.agent.to_numpy()[keep], st[keep]), 1.0)
    return F


def scan_events(events: pd.DataFrame, n_agent: int, steps: int, warmup: int = 0, window: int = 300,
                tols=(1, 5, 15)) -> pd.DataFrame:
    """Per (agent, window) coincidence z-score and p-value from raw order events (agents without submissions get p=1)."""
    F = submission_flow_from_events(events, n_agent, steps, warmup, window)
    rows = []
    for w in range(F.shape[0]):
        z, p = coincidence_scan(F[w], tols)
        active = F[w].sum(axis=(0, 2)) > 0
        rows.append(pd.DataFrame({"agent": np.arange(F.shape[2]), "window": w,
                                  "z": np.where(active, z, 0.0), "p": np.where(active, p, 1.0), "active": active}))
    return pd.concat(rows, ignore_index=True)


def scan_episode(ep: Episode, window: int = 300, tols=(1, 5, 15), **_) -> pd.DataFrame:
    """Per (agent, window) coincidence z-score and p-value for a simulated episode."""
    cfg = ep.config
    return scan_events(ep.events, int(ep.agents.aid.max()) + 1, cfg.steps, cfg.warmup, window, tols)
