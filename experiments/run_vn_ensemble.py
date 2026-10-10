"""Do the policy conclusions survive a family of calibrated markets?

Step 1 (approximate Bayesian rejection): draw market parameters (number of noise and fundamental traders, market-maker activity
and depth sensitivity, latent-value volatility, momentum activity) at random, simulate honest-only markets, and keep the draws
whose moments lie within tolerance of the real ones: cancel share 0.27-0.37, daily volatility 0.9-1.4%, retail share 0.66-0.85.
Step 2: in each accepted market, a ring that chooses among a fixed set of strategies (the best-response cross-evaluation of
run_vn_cross.py) faces each policy. The table reports, per policy, the distribution over markets of the ring's gain and of its
detection probability.
"""

from __future__ import annotations

import argparse
import ast
import re
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

import run_vn_cross as rvc
from marketsim.calibrate import episode_moments
from marketsim.policy import Policy
from marketsim.ring_adversary import evaluate, make_pool, net_utility
from marketsim.vietnam import vn_config

HONEST = dict(n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(0, 0))
TOL = {"cancel_share": (0.27, 0.37), "daily_vol_pct": (0.9, 1.4), "retail_share": (0.66, 0.85)}  # index-level; overridden by --vol-lo/--vol-hi
POLICIES = [("no price band", dict(band=0.0), 1, "none", 0), ("band 7% (HOSE today)", dict(band=0.07), 1, "none", 0),
            ("band 7% + block at 60-step mean", dict(band=0.07), 60, "none", 0),
            ("band 7% + block at 240-step mean", dict(band=0.07), 240, "none", 0),
            ("band 7% + inspect 1 per window", dict(band=0.07), 1, "scan", 1),
            ("band 7% + inspect 3 per window", dict(band=0.07), 1, "scan", 3)]


def draw(rng, sigma=(0.4, 1.2)):
    return {"n_noise": int(rng.integers(350, 651)), "n_fund": int(rng.integers(25, 61)), "mm_activity": float(rng.uniform(0.06, 0.14)),
            "fund_sigma": float(rng.uniform(*sigma)), "mm_imb_sens": float(rng.uniform(1.5, 4.0)),
            "mom_activity": float(rng.uniform(0.05, 0.12))}


def sample_markets(n_draw: int, n_keep: int, seed: int, sigma=(0.4, 1.2)) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_draw):
        p = draw(rng, sigma)
        cfg = replace(vn_config(**p), **HONEST)
        m = pd.DataFrame([episode_moments(15_000_000 + 10 * i + j, cfg) for j in range(2)]).mean().to_dict()
        ok = all(TOL[k][0] <= m[k] <= TOL[k][1] for k in TOL)
        rows.append({"draw": i, **p, **{k: m[k] for k in ("cancel_share", "daily_vol_pct", "retail_share", "spread_ticks")}, "accepted": ok})
        print(f"draw {i}: accepted={ok} vol={m['daily_vol_pct']:.2f} cancel={m['cancel_share']:.2f} retail={m['retail_share']:.2f}", flush=True)
        if sum(r["accepted"] for r in rows) >= n_keep:
            break
    return pd.DataFrame(rows)


def main(args):
    TOL["daily_vol_pct"] = (args.vol_lo, args.vol_hi)
    tag = args.tag
    draws = sample_markets(args.n_draw, args.n_markets, args.seed, (args.sigma_lo, args.sigma_hi))
    draws.to_csv(Path(args.out) / f"vn_ensemble{tag}_draws.csv", index=False)
    markets = draws[draws.accepted].head(args.n_markets)
    strats_all = rvc.strategies(Path(args.out) / "vn_policy.md")
    strats = [strats_all[i] for i in args.strategies if i < len(strats_all)]
    rows = []
    with make_pool(args.workers) as pool:
        for _, mk in markets.iterrows():
            params = {k: (int(mk[k]) if k in ("n_noise", "n_fund") else float(mk[k])) for k in
                      ("n_noise", "n_fund", "mm_activity", "fund_sigma", "mm_imb_sens", "mom_activity")}
            for label, pol_kw, L, kind, B in POLICIES:
                base = replace(vn_config(policy=Policy(label, day_len=240, **pol_kw), **params), block_vwap=L)
                sel = list(range(16_000_000, 16_000_000 + args.n))
                rep = list(range(17_000_000, 17_000_000 + args.n))
                rs = evaluate(strats, sel, base, kind, None, pool)
                best = int(np.argmax([rvc.score(r, kind, B) for r in rs]))
                r = evaluate([strats[best]], rep, base, kind, None, pool)[0]
                row = {"market": int(mk.draw), "policy": label, "gain": r.gain.mean(), "gain_se": r.gain.std(ddof=1) / np.sqrt(len(r))}
                if kind != "none":
                    row.update({"caught": r[f"caught{B}"].mean(), "net_U5": net_utility(r, B, 5), "net_U10": net_utility(r, B, 10)})
                rows.append(row)
            print("market", int(mk.draw), "done", flush=True)
            pd.DataFrame(rows).to_csv(Path(args.out) / f"vn_ensemble{tag}.csv", index=False)
    df = pd.DataFrame(rows)
    base = df[df.policy == "no price band"].set_index("market").gain
    df["gain_vs_no_band"] = df.apply(lambda r: r.gain / base[r.market] if base[r.market] > 0 else np.nan, axis=1)
    df.to_csv(Path(args.out) / f"vn_ensemble{tag}.csv", index=False)
    summ = df.groupby("policy", sort=False).agg(markets=("market", "nunique"), gain_median=("gain", "median"), gain_min=("gain", "min"),
                                                 gain_max=("gain", "max"), ratio_median=("gain_vs_no_band", "median"),
                                                 caught_median=("caught", "median"), netU5_max=("net_U5", "max"), netU10_max=("net_U10", "max"))
    text = ["# Policy conclusions across a family of calibrated markets\n",
            f"{len(markets)} markets accepted among {len(draws)} draws (tolerances: cancel share 0.27-0.37, daily volatility {args.vol_lo}-{args.vol_hi}%, retail share "
            f"0.66-0.85). Ring strategy set: {len(strats)} strategies; {args.n} selection and {args.n} reporting episodes per cell. `ratio` is the ring's gain "
            "relative to its gain with no policy in the same market (markets with non-positive baseline gain are left out of the ratio).\n",
            "## Accepted markets\n", markets.round(3).to_markdown(index=False), "\n", "## Per policy, over markets\n", summ.round(2).to_markdown(), ""]
    (Path(args.out) / f"vn_ensemble{tag}.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-draw", type=int, default=40)
    ap.add_argument("--n-markets", type=int, default=6)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--strategies", type=int, nargs="+", default=[0, 1, 3, 6])
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--vol-lo", type=float, default=0.9)
    ap.add_argument("--vol-hi", type=float, default=1.4)
    ap.add_argument("--sigma-lo", type=float, default=0.4)
    ap.add_argument("--sigma-hi", type=float, default=1.2)
    ap.add_argument("--tag", default="")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
