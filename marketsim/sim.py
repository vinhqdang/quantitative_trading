"""Episode runner: many heterogeneous agents trading in one limit order book."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .agents import (FundamentalTrader, ImbalanceTrader, Institution, MarketMaker, MomentumTrader, NoiseTrader,
                     PumpAndDump, Spoofer, WashAccount, WashPair)
from .exchange import EVENT_COLUMNS, Exchange


@dataclass
class SimConfig:
    steps: int = 6000
    warmup: int = 300
    n_noise: int = 80
    n_mm: int = 6
    n_fund: int = 10
    n_mom: int = 10
    n_imb: int = 10
    mm_imb_sens: float = 2.5
    mom_activity: float = 0.08
    mom_thr: float = 3.0
    n_inst: int = 2
    # manipulators per episode: (min, max) count drawn uniformly
    n_spoof: tuple[int, int] = (1, 2)
    n_pump: tuple[int, int] = (1, 2)
    n_wash_pairs: tuple[int, int] = (0, 1)
    evasion: float = 0.0
    fund_sigma: float = 0.5
    jump_prob: float = 0.002
    jump_sigma: float = 8.0
    window_len: tuple[int, int] = (1200, 2400)


@dataclass
class Episode:
    events: pd.DataFrame
    mids: np.ndarray
    agents: pd.DataFrame          # aid, kind, manipulator (ground truth, analysis only)
    gt_orders: pd.DataFrame       # oid, tag (ground truth, analysis only)
    gt_trades: pd.DataFrame       # agent, tag, side, price, qty
    pnl: pd.DataFrame             # per-agent mark-to-market pnl and traded volume
    config: SimConfig = field(repr=False, default_factory=SimConfig)


def run_episode(seed: int, cfg: SimConfig | None = None) -> Episode:
    cfg = cfg or SimConfig()
    rng = np.random.default_rng(seed)
    ex = Exchange()

    def child() -> np.random.Generator:
        return np.random.default_rng(rng.integers(2**63))

    agents: list = []

    def add(cls, n, **kw):
        for _ in range(n):
            agents.append(cls(len(agents), child(), **kw))

    add(NoiseTrader, cfg.n_noise)
    add(MarketMaker, cfg.n_mm, imb_sens=cfg.mm_imb_sens)
    add(FundamentalTrader, cfg.n_fund)
    add(MomentumTrader, cfg.n_mom, activity=cfg.mom_activity, thr=cfg.mom_thr)
    add(ImbalanceTrader, cfg.n_imb)
    add(Institution, cfg.n_inst)

    def window() -> tuple[int, int]:
        length = int(rng.integers(*cfg.window_len))
        start = int(rng.integers(cfg.warmup, max(cfg.warmup + 1, cfg.steps - length)))
        return start, min(cfg.steps, start + length)

    pairs: list[WashPair] = []
    for _ in range(int(rng.integers(cfg.n_spoof[0], cfg.n_spoof[1] + 1))):
        agents.append(Spoofer(len(agents), child(), window(), cfg.evasion))
    for _ in range(int(rng.integers(cfg.n_pump[0], cfg.n_pump[1] + 1))):
        agents.append(PumpAndDump(len(agents), child(), window(), cfg.evasion))
    for _ in range(int(rng.integers(cfg.n_wash_pairs[0], cfg.n_wash_pairs[1] + 1))):
        w = window()
        a = WashAccount(len(agents), child(), w, cfg.evasion)
        agents.append(a)
        b = WashAccount(len(agents), child(), w, cfg.evasion)
        agents.append(b)
        a.pair = b.pair = WashPair(a, b, child(), w, cfg.evasion)
        pairs.append(a.pair)

    order = np.arange(len(agents))
    for t in range(cfg.steps):
        ex.fund += rng.normal(0, cfg.fund_sigma)
        if rng.random() < cfg.jump_prob:
            ex.fund += rng.normal(0, cfg.jump_sigma)
        rng.shuffle(order)
        for i in order:
            agents[i].step(ex)
        for p in pairs:
            p.cross(ex)
        ex.end_step()

    events = pd.DataFrame(ex.events, columns=EVENT_COLUMNS)
    meta = pd.DataFrame({"aid": [a.aid for a in agents], "kind": [a.kind for a in agents],
                         "manipulator": [a.manipulator for a in agents]})
    gt_orders = pd.DataFrame(list(ex.tags.items()), columns=["oid", "tag"])
    gt_trades = pd.DataFrame(ex.gt_trades, columns=["agent", "tag", "side", "price", "qty", "t"])
    final = ex.mids[-1]
    traded = events[events.kind == 3].groupby("agent").qty.sum()
    pnl = pd.DataFrame({
        "aid": meta.aid,
        "pnl": [ex.cash[a] + ex.inv[a] * final for a in meta.aid],
        "traded": [int(traded.get(a, 0)) for a in meta.aid],
    })
    return Episode(events, np.asarray(ex.mids), meta, gt_orders, gt_trades, pnl, cfg)


def tagged_pnl_per_share(ep: Episode, prefix: str) -> tuple[float, int]:
    """Mark-to-market profit per share traded across trades whose order carried a tag with `prefix`.

    Per account, any open tagged inventory is valued at the mid at that account's last tagged
    trade, so unrelated drift after the manipulation ended does not enter the number.
    Returns (profit_per_share, shares_traded).
    """
    tr = ep.gt_trades[ep.gt_trades.tag.str.startswith(prefix)]
    if tr.empty:
        return float("nan"), 0
    total = 0.0
    for _, g in tr.groupby("agent"):
        mark = ep.mids[int(g.t.max())]
        total += float((-g.side * g.price * g.qty).sum() + (g.side * g.qty).sum() * mark)
    shares = int(tr.qty.sum())
    return total / shares, shares


def manipulation_impact(ep: Episode, horizon: int = 8, gap: int = 20) -> dict[str, list[float]]:
    """Price effect of each manipulation cycle, in ticks, signed so that positive = the intended direction.

    spoof: mid change `horizon` steps after the first fake order of a cycle, signed by the direction
           the spoofer wants the price to move (opposite to the side of the fake orders).
    pump:  mid change from the first to the last aggressive pump order of a cycle.
    """
    ev = ep.events.merge(ep.gt_orders, on="oid")
    m, last = ep.mids, len(ep.mids) - 1
    out = {"spoof": [], "pump": []}
    fakes = ev[(ev.tag == "spoof_fake") & (ev.kind == 0)]
    for _, g in fakes.groupby("agent"):
        ts = np.sort(g.t.unique())
        for t0 in ts[np.r_[True, np.diff(ts) > gap]]:
            intended = g[g.t == t0].side.iloc[0]  # fakes on the buy side push the price up
            out["spoof"].append(float(intended * (m[min(t0 + horizon, last)] - m[t0])))
    pumps = ev[(ev.tag == "pd_pump") & (ev.kind == 1)]
    for _, g in pumps.groupby("agent"):
        ts = np.sort(g.t.unique())
        cuts = np.flatnonzero(np.r_[True, np.diff(ts) > gap])
        for a, b in zip(cuts, list(cuts[1:]) + [len(ts)]):
            seg = ts[a:b]
            out["pump"].append(float(m[min(seg[-1] + 1, last)] - m[seg[0]]))
    return out
