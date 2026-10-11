"""Block-price rule: exact ex-post evaluation of a rule that only changes the payoff.

The reference price of the off-book block (mean mid over the last L steps) enters only the ring's payoff, not the market
dynamics, so for a given ring strategy the same simulated episodes can be scored for every L (`sim.ring_utility(ep, vwap=L)`).
For each calibrated market (both families) and each strategy of the ring's strategy set the script simulates selection and
reporting episodes once and then, for every L:
  * static ring: the strategy that is best with the last price as reference (L = 1), its gain at L relative to L = 1;
  * adaptive ring: the strategy that is best at L on the selection episodes, its gain on the reporting episodes;
and reports the mean push duration `a` and the linear-ramp prediction of Proposition 6 (D a / (2 L) for L >= a; D (1 - L / (2a)) for L < a)
for the block term. Common random numbers across L make the curve smooth.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.policy import Policy
from marketsim.ring_adversary import make_pool, ring_only_config
from marketsim.sim import ring_utility, run_episode
from marketsim.vietnam import vn_config

import run_vn_cross as rvc

LS = [1, 5, 15, 30, 60, 120, 240, 480]
KEYS = ("n_noise", "n_fund", "mm_activity", "fund_sigma", "mm_imb_sens", "mom_activity")


def one(args):
    seed, params, strat = args
    base = vn_config(policy=Policy("band 7%", day_len=240, band=0.07), **params)
    ep = run_episode(seed, ring_only_config(base, strat))
    cyc = [c for c in ep.extras.get("ring_cycles", []) if "end_push" in c]
    out = {"seed": seed, "cycles": len(cyc),
           "push_len": float(np.mean([c["end_push"] - c["start"] for c in cyc])) if cyc else np.nan}
    for L in LS:
        u = ring_utility(ep, vwap=L)
        out[f"gain_{L}"] = u["gain"]
        out[f"block_{L}"] = u["gain"] - u["trading"]
    return out


def main(args):
    strats_all = rvc.strategies(Path(args.out) / "vn_policy.md")
    strats = [strats_all[i] for i in args.strategies if i < len(strats_all)]
    fams = {"index level": "results/vn_ensemble_draws.csv", "stock level": "results/vn_ensemble_stock_draws.csv"}
    jobs, meta = [], []
    for fam, path in fams.items():
        d = pd.read_csv(path)
        d = d[d.accepted].head(args.n_markets)
        for _, mk in d.iterrows():
            params = {k: (int(mk[k]) if k in ("n_noise", "n_fund") else float(mk[k])) for k in KEYS}
            for si, strat in enumerate(strats):
                for part, off in (("sel", 0), ("rep", 500)):
                    for i in range(args.n):
                        jobs.append((20_000_000 + 10_000 * int(mk.draw) + 1000 * si + off + i, params, strat))
                        meta.append({"family": fam, "market": int(mk.draw), "strategy": si, "part": part})
    with make_pool(args.workers) as pool:
        res = list(pool.map(one, jobs, chunksize=2))
    df = pd.concat([pd.DataFrame(meta), pd.DataFrame(res)], axis=1)
    df.to_csv(Path(args.out) / "block_static_episodes.csv", index=False)
    rows = []
    for (fam, mk), g in df.groupby(["family", "market"]):
        sel = g[g.part == "sel"].groupby("strategy").mean(numeric_only=True)
        rep = g[g.part == "rep"].groupby("strategy").mean(numeric_only=True)
        s_static = int(sel["gain_1"].idxmax())
        base = rep.loc[s_static, "gain_1"]
        a = rep.loc[s_static, "push_len"]
        for L in LS:
            s_ad = int(sel[f"gain_{L}"].idxmax())
            blk1 = rep.loc[s_static, "block_1"]
            law = (a / (2 * L) if L >= a else 1 - L / (2 * a))
            rows.append({"family": fam, "market": mk, "L": L, "static strategy": s_static, "adaptive strategy": s_ad,
                         "gain no rule": base, "static gain": rep.loc[s_static, f"gain_{L}"], "adaptive gain": rep.loc[s_ad, f"gain_{L}"],
                         "static ratio": rep.loc[s_static, f"gain_{L}"] / base if base > 0 else np.nan,
                         "adaptive ratio": rep.loc[s_ad, f"gain_{L}"] / base if base > 0 else np.nan,
                         "block term ratio (static)": rep.loc[s_static, f"block_{L}"] / blk1 if blk1 > 0 else np.nan,
                         "push duration a": a, "linear-ramp law": law})
    out = pd.DataFrame(rows)
    out.to_csv(Path(args.out) / "block_static.csv", index=False)
    summ = out.groupby(["family", "L"])[["static ratio", "adaptive ratio", "block term ratio (static)", "linear-ramp law"]].median().round(3)
    text = ["# Block-price rule: exact ex-post evaluation\n",
            f"{args.n} selection and {args.n} reporting episodes per strategy and market; strategy set of {len(strats)}. Medians over markets of the "
            "gain with the block priced at the trailing mean over L steps relative to L = 1.\n", summ.to_markdown(), "\n## Per market\n",
            out.round(3).to_markdown(index=False), ""]
    (Path(args.out) / "block_static.md").write_text("\n".join(text))
    print("\n".join(text[:4]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--n-markets", type=int, default=6)
    ap.add_argument("--strategies", type=int, nargs="+", default=[0, 1, 3, 6])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
