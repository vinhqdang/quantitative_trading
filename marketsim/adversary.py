"""Adaptive spoofer: black-box search over spoofing parameters against a detector.

The adversary has query access to the detector (it can run episodes and observe whether its
windows would be flagged), which makes it a stronger attacker than a real manipulator who only
observes enforcement outcomes. Search is a simple evolution strategy with common random numbers
within each generation.

Utility per episode = realised spoofing profit - fine * 1[at least one manipulation window flagged].
"""

from __future__ import annotations

import math
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field, replace

import numpy as np
import pandas as pd

from .detect import WINDOW
from .features import label_windows, window_features
from .sim import SimConfig, manipulation_impact, run_episode, tagged_pnl_per_share

# name -> (low, high, kind)
SPOOF_SPACE = {
    "layers": (1, 4, "int"),
    "fake_qty": (10, 400, "log"),
    "dist": (1, 6, "int"),
    "hold_extra": (0, 25, "int"),
    "real_qty": (5, 40, "log"),
    "cool_lo": (10, 150, "int"),
    "dilute": (0.0, 0.6, "float"),
}
SPOOF_DEFAULT = {"layers": 3, "fake_qty": 250, "dist": 1, "hold_extra": 2, "real_qty": 10, "cool_lo": 20,
                 "dilute": 0.0}
NAMES = list(SPOOF_SPACE)


def decode(u: np.ndarray) -> dict:
    out = {}
    for x, name in zip(np.clip(u, 0, 1), NAMES):
        lo, hi, kind = SPOOF_SPACE[name]
        if kind == "log":
            out[name] = float(math.exp(math.log(lo) + x * (math.log(hi) - math.log(lo))))
        elif kind == "int":
            out[name] = int(round(lo + x * (hi - lo)))
        else:
            out[name] = float(lo + x * (hi - lo))
    out["fake_qty"] = int(out["fake_qty"])
    out["real_qty"] = int(out["real_qty"])
    out["cool_hi"] = out["cool_lo"] + 40
    return out


def encode(params: dict) -> np.ndarray:
    u = []
    for name in NAMES:
        lo, hi, kind = SPOOF_SPACE[name]
        v = params[name]
        u.append((math.log(v) - math.log(lo)) / (math.log(hi) - math.log(lo)) if kind == "log" else (v - lo) / (hi - lo))
    return np.clip(np.array(u), 0, 1)


def spoof_only_config(base: SimConfig, params: dict | None) -> SimConfig:
    """One spoofer in an otherwise honest market, so profit and detection are attributable to it."""
    return replace(base, steps=3000, n_spoof=(1, 1), n_pump=(0, 0), n_wash_pairs=(0, 0), window_len=(1800, 2400),
                   spoof_params=params)


class NullDetector:
    """Flags nothing: used to find the profit-maximising spoofer when detection is not in play."""

    def score(self, X):
        return np.zeros(len(X))


def make_pool(workers: int = 4) -> ProcessPoolExecutor:
    """Pool for tasks that call a fitted sklearn model.

    Workers must be spawned: forking after OpenMP has run in the parent deadlocks on predict.
    """
    return ProcessPoolExecutor(workers, mp_context=mp.get_context("spawn"))


def _task(args):
    params, seed, base, detector, thr = args
    cfg = spoof_only_config(base, params)
    ep = run_episode(seed, cfg)
    df = label_windows(ep, window_features(ep, WINDOW), WINDOW)
    score = detector.score(df)
    df = df.assign(flag=score >= thr)
    pos = df[df.type == "spoof"]
    per_share, shares = tagged_pnl_per_share(ep, "spoof_")
    imp = manipulation_impact(ep)["spoof"]
    return {
        "profit": 0.0 if shares == 0 else per_share * shares,
        "shares": shares,
        "impact": float(np.mean(imp)) if imp else 0.0,
        "pos": len(pos),
        "flagged": int(pos.flag.sum()),
        "caught": int(pos.flag.any()) if len(pos) else 0,
        "active": int(len(pos) > 0),
    }


def evaluate_population(pop: list[dict], seeds, base: SimConfig, detector, thr: float, pool) -> list[dict]:
    """Aggregate per-parameter results over `seeds` (common random numbers across candidates)."""
    tasks = [(p, s, base, detector, thr) for p in pop for s in seeds]
    res = list(pool.map(_task, tasks, chunksize=2))
    k = len(seeds)
    out = []
    for i in range(len(pop)):
        r = pd.DataFrame(res[i * k:(i + 1) * k])
        out.append({
            "profit": r.profit.mean(),
            "impact": r.impact.mean(),
            "pos_windows": r.pos.mean(),
            "window_rate": r.flagged.sum() / max(1, r.pos.sum()),
            "caught": r.caught.sum() / max(1, r.active.sum()),
        })
    return out


@dataclass
class SearchResult:
    best: dict
    mean_params: dict
    history: pd.DataFrame
    final: dict = field(default_factory=dict)


def evolve(detector, thr: float, base: SimConfig, fine: float, pool, seed: int = 0, pop_size: int = 16,
           gens: int = 8, k_seeds: int = 4, sigma0: float = 0.3, init: dict | None = None) -> SearchResult:
    rng = np.random.default_rng(seed)
    mean = encode(init or SPOOF_DEFAULT)
    sigma = sigma0
    rows = []
    best_u, best_val = mean, -np.inf
    for g in range(gens):
        cand = np.clip(mean + sigma * rng.normal(size=(pop_size, len(NAMES))), 0, 1)
        cand[0] = mean  # keep the incumbent in the population
        params = [decode(u) for u in cand]
        seeds = [int(x) for x in rng.integers(10**6, 10**7, size=k_seeds)]
        res = evaluate_population(params, seeds, base, detector, thr, pool)
        util = np.array([r["profit"] - fine * r["caught"] for r in res])
        for u, p, r, v in zip(cand, params, res, util):
            rows.append({"gen": g, "utility": v, **r, **{f"p_{k}": p[k] for k in NAMES}})
        order = np.argsort(-util)
        elite = cand[order[: max(2, pop_size // 4)]]
        mean = elite.mean(axis=0)
        if util[order[0]] > best_val:
            best_val, best_u = util[order[0]], cand[order[0]]
        sigma *= 0.85
    return SearchResult(decode(best_u), decode(mean), pd.DataFrame(rows))
