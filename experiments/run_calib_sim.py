"""Simulated daily returns and moments of honest-only markets, for the calibration figure.

For the first accepted market of each family (index level, stock level; see run_vn_ensemble.py) run honest-only episodes and
store the daily returns (mid price every `day_len` steps after warm-up) and the episode moments.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path
import multiprocessing as mp

import numpy as np
import pandas as pd

from marketsim.calibrate import episode_moments
from marketsim.sim import run_episode
from marketsim.vietnam import vn_config

HONEST = dict(n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(0, 0))
KEYS = ("n_noise", "n_fund", "mm_activity", "fund_sigma", "mm_imb_sens", "mom_activity")


def one(args):
    seed, params, steps = args
    cfg = replace(vn_config(**params), **HONEST, steps=steps)
    ep = run_episode(seed, cfg)
    day = cfg.policy.day_len
    m = np.asarray(ep.mids)[cfg.warmup:]
    daily = m[day::day] / m[:-day:day] - 1 if len(m) > day else np.array([])
    # one-step returns inside the day, for volatility clustering
    r1 = np.diff(np.log(m[::10]))
    from marketsim.calibrate import moments_from_events
    kind_of = dict(zip(ep.agents.aid, ep.agents.kind))
    mom = moments_from_events(ep.events, ep.mids, kind_of, cfg.warmup, day)
    mom["spread_ticks"] = ep.quality["spread"]
    return daily, r1, mom


def check_all(args):
    """Moments of every accepted market of both families over many honest episodes (is each inside the tolerance box?)."""
    fam = {"index level": "results/vn_ensemble_draws.csv", "stock level": "results/vn_ensemble_stock_draws.csv"}
    rows = []
    with ProcessPoolExecutor(args.workers, mp_context=mp.get_context("spawn")) as pool:
        for name, path in fam.items():
            d = pd.read_csv(path)
            for _, mk in d[d.accepted].head(6).iterrows():
                params = {k: (int(mk[k]) if k in ("n_noise", "n_fund") else float(mk[k])) for k in KEYS}
                res = list(pool.map(one, [(21_000_000 + 100 * int(mk.draw) + i, params, args.steps) for i in range(args.n)]))
                m = pd.DataFrame([r[2] for r in res])
                rows.append({"family": name, "market": int(mk.draw), "vol at acceptance (%)": mk.daily_vol_pct, "vol, 16-episode mean (%)": m.daily_vol_pct.mean(),
                             "vol s.e. (%)": m.daily_vol_pct.std() / np.sqrt(len(m)), "cancel share": m.cancel_share.mean(), "retail share": m.retail_share.mean(),
                             "spread (ticks)": m.spread_ticks.mean()})
                print(rows[-1], flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(Path(args.out) / "calib_markets.csv", index=False)
    print(df.round(3).to_markdown(index=False))


def main(args):
    if args.check_all:
        return check_all(args)
    fam = {"index level": "results/vn_ensemble_draws.csv", "stock level": "results/vn_ensemble_stock_draws.csv"}
    rows, mom_rows, r1_rows = [], [], []
    ctx = mp.get_context("spawn")
    with ProcessPoolExecutor(args.workers, mp_context=ctx) as pool:
        for name, path in fam.items():
            d = pd.read_csv(path)
            mk = d[d.accepted].iloc[0]
            params = {k: (int(mk[k]) if k in ("n_noise", "n_fund") else float(mk[k])) for k in KEYS}
            res = list(pool.map(one, [(19_000_000 + i, params, args.steps) for i in range(args.n)]))
            for i, (daily, r1, mom) in enumerate(res):
                for j, r in enumerate(daily):
                    rows.append({"family": name, "episode": i, "day": j, "ret": r})
                for j, r in enumerate(r1):
                    r1_rows.append({"family": name, "episode": i, "k": j, "ret": r})
                mom_rows.append({"family": name, "episode": i, **mom})
    pd.DataFrame(rows).to_csv(Path(args.out) / "calib_sim_daily.csv", index=False)
    pd.DataFrame(r1_rows).to_csv(Path(args.out) / "calib_sim_intraday.csv", index=False)
    mom = pd.DataFrame(mom_rows)
    mom.to_csv(Path(args.out) / "calib_sim_moments.csv", index=False)
    print(mom.groupby("family").mean(numeric_only=True).round(3).to_markdown())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--check-all", action="store_true")
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
