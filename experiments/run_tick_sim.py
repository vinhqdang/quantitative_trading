"""Simulated counterpart of the 2016 HOSE tick reform: what does the simulator predict for the same daily-data outcomes?

Honest-only Vietnam-preset markets with the tick multiplied by m (prices are rounded to multiples of m base ticks). Daily bars are built
from trade prices (240 steps per day) and the same outcomes as in run_tick_reform.py are computed: Corwin-Schultz spread, daily range,
absolute return, share of zero-return days, log volume. Changes are reported for the reductions 10 -> 1, 5 -> 1 and 2 -> 1.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.exchange import TRADE
from marketsim.policy import Policy
from marketsim.sim import run_episode
from marketsim.vietnam import vn_config

from run_tick_reform import corwin_schultz

HONEST = dict(n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(0, 0))


def daily_outcomes(seed: int, m: int) -> dict:
    cfg = replace(vn_config(policy=Policy(f"tick x{m}", tick=m, band=0.07, day_len=240)), **HONEST)
    ep = run_episode(seed, cfg)
    tr = ep.events[(ep.events.kind == TRADE) & (ep.events.t >= cfg.warmup)]
    tr = tr.assign(day=(tr.t - cfg.warmup) // 240)
    g = tr.groupby("day")
    bars = pd.DataFrame({"high": g.price.max(), "low": g.price.min(), "close": g.price.last(), "volume": g.qty.sum()})
    bars = bars[bars.index < bars.index.max()]                      # drop the last, partial day
    cs = corwin_schultz(bars[["high"]].rename(columns={"high": "x"}), bars[["low"]].rename(columns={"low": "x"}))["x"] * 100
    ret = np.log(bars.close).diff()
    return {"CS spread (%)": cs.mean(), "daily range (%)": (np.log(bars.high / bars.low) * 100).mean(), "|return| (%)": (ret.abs() * 100).mean(),
            "zero-return share": float((ret.dropna() == 0).mean()), "log volume": float(np.log1p(bars.volume).mean()),
            "quoted spread (%)": ep.quality["spread"] / ep.mids.mean() * 100}


def main(args):
    ms = [1, 2, 5, 10]
    with ProcessPoolExecutor(args.workers) as pool:
        res = {m: pd.DataFrame(list(pool.map(daily_outcomes, range(18_000_000, 18_000_000 + args.n), [m] * args.n))) for m in ms}
    means = pd.DataFrame({m: r.mean() for m, r in res.items()})
    ses = pd.DataFrame({m: r.std(ddof=1) / np.sqrt(len(r)) for m, r in res.items()})
    rows = []
    for old in (2, 5, 10):
        for out in means.index:
            d = means.loc[out, 1] - means.loc[out, old]
            se = np.sqrt(ses.loc[out, 1] ** 2 + ses.loc[out, old] ** 2)
            rows.append({"tick reduction": f"{old} -> 1", "outcome": out, "level before": means.loc[out, old], "level after": means.loc[out, 1],
                         "change": d, "s.e.": se})
    ch = pd.DataFrame(rows)
    text = ["# Simulated tick-size reduction (Vietnam preset, honest-only markets)\n",
            f"{args.n} episodes per tick size. Tick multiplier m: prices are multiples of m base ticks; the base tick is 0.2% of the price, so m = 10 is "
            "about the pre-reform relative tick of a 25,000 VND stock (500 VND) and m = 1 the post-reform one (50 VND).\n",
            "## Levels\n", means.round(4).to_markdown(), "", "## Changes\n", ch.round(4).to_markdown(index=False), ""]
    Path(args.out).mkdir(exist_ok=True)
    ch.to_csv(Path(args.out) / "tick_sim.csv", index=False)
    (Path(args.out) / "tick_sim.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
