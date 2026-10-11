"""Moments for calibrating the simulator, computed identically for simulated and real order-level data.

Real data must be converted to the event schema in `exchange.EVENT_COLUMNS`
(t, kind, agent, oid, side, price, qty, mid, cpty, aggr) plus a mid-price series and, for the
participant mix, a map from account to investor group. The same `moments_from_events` then applies.
"""

from __future__ import annotations

import itertools
from dataclasses import replace

import numpy as np
import pandas as pd

from .exchange import CANCEL, MKT, NEW, TRADE
from .sim import SimConfig, run_episode

RETAIL_KINDS = ("noise", "momentum", "imbalance")

# Published or derived targets (see docs/vietnam_calibration.md for sources and confidence)
VN_TARGETS = {
    "retail_share": 0.80,    # share of traded value by individual investors, 2024-2025 press estimates 75-82%
    "cancel_share": 0.3176,  # amendments + cancellations as a share of orders, HOSE Dec 2020 (pre-KRX)
    "rel_tick_bps": 20.0,    # tick / price for a 25,000 VND stock on the 10,000-49,950 band (50 VND tick)
}


def moments_from_events(events: pd.DataFrame, mids: np.ndarray, kind_of: dict[int, str] | None = None,
                        warmup: int = 0, day_len: int = 240, tick: float = 1.0) -> dict:
    ev = events[events.t >= warmup]
    orders = ev[ev.kind.isin([NEW, MKT])]
    out = {
        "cancel_share": float((ev.kind == CANCEL).sum() / max(1, len(orders))),
        "rel_tick_bps": float(tick / np.mean(mids[warmup:]) * 1e4),
    }
    m = np.asarray(mids)[warmup:]
    if len(m) > day_len:
        r = (m[day_len:] - m[:-day_len]) / m[:-day_len]
        out["daily_vol_pct"] = float(np.std(r) * 100)
        rd = m[day_len::day_len] / m[:-day_len:day_len] - 1        # non-overlapping daily returns
        if len(rd) > 3:
            a = rd - rd.mean()
            out["acf_num"], out["acf_den"] = float((a[:-1] * a[1:]).sum()), float((a * a).sum())
    if kind_of is not None:
        tr = ev[ev.kind == TRADE]
        kinds = tr.agent.map(kind_of)
        vol = tr.qty.groupby(kinds).sum()
        out["retail_share"] = float(vol.reindex(list(RETAIL_KINDS)).fillna(0).sum() / vol.sum())
    return out


def episode_moments(seed: int, cfg: SimConfig) -> dict:
    ep = run_episode(seed, cfg)
    kind_of = dict(zip(ep.agents.aid, ep.agents.kind))
    mom = moments_from_events(ep.events, ep.mids, kind_of, cfg.warmup, cfg.policy.day_len)
    mom["spread_ticks"] = ep.quality["spread"]
    return mom


def distance(mom: dict, targets: dict = VN_TARGETS, keys=("retail_share", "cancel_share")) -> float:
    return float(sum(((mom[k] - targets[k]) / targets[k]) ** 2 for k in keys))


def grid_search(base: SimConfig, grid: dict[str, list], n_episodes: int = 3, seed0: int = 7_000_000,
                targets: dict = VN_TARGETS, keys=("retail_share", "cancel_share")) -> pd.DataFrame:
    """Coarse moment matching over SimConfig fields on honest-only markets."""
    honest = dict(n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0))
    rows = []
    names = list(grid)
    for values in itertools.product(*grid.values()):
        cfg = replace(base, **honest, **dict(zip(names, values)))
        moms = pd.DataFrame([episode_moments(seed0 + i, cfg) for i in range(n_episodes)]).mean().to_dict()
        rows.append({**dict(zip(names, values)), **moms, "distance": distance(moms, targets, keys)})
    return pd.DataFrame(rows).sort_values("distance").reset_index(drop=True)
