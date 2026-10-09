"""Adaptive collusion ring against budgeted inspection.

Each window the regulator inspects the B highest-scoring accounts. A ring is caught if any member is
inspected in any window of the episode (finding one member exposes the ring, as account linkage does in
practice). The ring searches for parameters that maximise its expected net benefit

    U = gain - m * max(gain, 0) * caught,

where `gain` is the benefit of ring_utility() and m is the penalty multiple on the illegal gain
(Vietnamese administrative fines are capped at 5x the gain for individuals and 10x for organisations).
Candidates are scored on common random numbers within a generation (evolution strategy).
"""

from __future__ import annotations

import math
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np
import pandas as pd
from scipy.stats import norm

from .coordination import scan_episode
from .features import window_features
from .sim import SimConfig, ring_utility, run_episode

SPACE = {
    "K": (3, 40, "int"), "q": (1, 6, "int"), "m_push": (1, 4, "int"), "p_push": (0.2, 1.0, "float"),
    "p_acc": (0.1, 0.8, "float"), "jitter": (0, 40, "int"), "cross_frac": (0.0, 0.5, "float"),
    "acc_len": (20, 100, "int"), "push_len": (10, 50, "int"), "dist_len": (30, 80, "int"), "cool": (30, 120, "int"),
}
DEFAULT = {"K": 12, "q": 3, "m_push": 2, "p_push": 0.8, "p_acc": 0.4, "jitter": 0, "cross_frac": 0.2,
           "acc_len": 60, "push_len": 25, "dist_len": 50, "cool": 60}
NAMES = list(SPACE)
BUDGETS = (1, 3, 5, 10)


def decode(u) -> dict:
    out = {}
    for x, name in zip(np.clip(u, 0, 1), NAMES):
        lo, hi, kind = SPACE[name]
        v = lo + x * (hi - lo)
        out[name] = int(round(v)) if kind == "int" else float(v)
    return out


def encode(params: dict) -> np.ndarray:
    return np.clip(np.array([(params[n] - SPACE[n][0]) / (SPACE[n][1] - SPACE[n][0]) for n in NAMES]), 0, 1)


def ring_only_config(base: SimConfig, params: dict | None) -> SimConfig:
    return replace(base, steps=3000, n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(1, 1),
                   window_len=(1800, 2400), ring_params=params)


def make_pool(workers: int = 4) -> ProcessPoolExecutor:
    return ProcessPoolExecutor(workers, mp_context=mp.get_context("spawn"))


def _pooled(sc: pd.DataFrame, L: int = 4) -> pd.DataFrame:
    sc = sc.sort_values(["agent", "window"]).copy()
    sc["s"] = norm.isf(np.clip(sc.p, 1 / 301, 0.999))
    sc["score"] = sc.groupby("agent").s.transform(lambda x: x.rolling(L, min_periods=1).sum()) / math.sqrt(L)
    return sc[sc.active]


def caught_flags(ep, kind: str, detector=None, budgets=BUDGETS) -> dict[int, bool]:
    members = set(a for ms in ep.extras["ring_members"] for a in ms)
    if kind == "scan":
        df = _pooled(scan_episode(ep))
    elif kind == "gbm":
        df = window_features(ep, 300)
        df["score"] = detector.score(df)
    else:
        return {B: False for B in budgets}
    out = {B: False for B in budgets}
    for _, g in df.groupby("window"):
        order = g.sort_values("score", ascending=False).agent.to_numpy()
        for B in budgets:
            if members.intersection(order[:B]):
                out[B] = True
    return out


def _task(args):
    params, seed, base, kind, detector = args
    ep = run_episode(seed, ring_only_config(base, params))
    u = ring_utility(ep)
    flags = caught_flags(ep, kind, detector)
    return {"gain": u["gain"], "displacement": u["displacement"], **{f"caught{B}": float(f) for B, f in flags.items()}}


def evaluate(pop: list[dict], seeds, base, kind, detector, pool) -> list[pd.DataFrame]:
    res = list(pool.map(_task, [(p, s, base, kind, detector) for p in pop for s in seeds], chunksize=2))
    k = len(seeds)
    return [pd.DataFrame(res[i * k:(i + 1) * k]) for i in range(len(pop))]


def net_utility(r: pd.DataFrame, B: int, m: float) -> float:
    g = r.gain.to_numpy()
    return float(np.mean(g - m * np.maximum(g, 0) * r[f"caught{B}"].to_numpy()))


def evolve(base, kind, detector, B: int, m: float, pool, seed: int = 0, pop_size: int = 12, gens: int = 5,
           k_seeds: int = 4, sigma0: float = 0.3, init: dict | None = None):
    rng = np.random.default_rng(seed)
    mean, sigma = encode(init or DEFAULT), sigma0
    archive, best_u, best_val = [], mean, -np.inf
    for g in range(gens):
        cand = np.clip(mean + sigma * rng.normal(size=(pop_size, len(NAMES))), 0, 1)
        cand[0] = mean
        params = [decode(u) for u in cand]
        seeds = [int(x) for x in rng.integers(10**6, 10**7, size=k_seeds)]
        res = evaluate(params, seeds, base, kind, detector, pool)
        util = np.array([net_utility(r, B, m) if kind != "none" else r.gain.mean() for r in res])
        for p, r, v in zip(params, res, util):
            archive.append({"gen": g, "utility": v, "gain": r.gain.mean(), "displacement": r.displacement.mean(),
                            "caught": r[f"caught{B}"].mean() if f"caught{B}" in r else np.nan, **p})
        order = np.argsort(-util)
        mean = cand[order[: max(2, pop_size // 4)]].mean(axis=0)
        if util[order[0]] > best_val:
            best_val, best_u = util[order[0]], cand[order[0]]
        sigma *= 0.85
    return decode(best_u), decode(mean), pd.DataFrame(archive)
