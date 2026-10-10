"""Policy levers x manipulation types x cost to honest investors, in the Vietnam preset.

For each policy: (1) honest-only markets give market-quality metrics; (2) markets with one spoofer, one pump-and-dump agent, one
wash pair and one ring (default, non-adaptive strategies) give what each manipulation achieves: spoofing and pump price impact and
profit, the share of traded volume that is wash volume, and the ring's gain. Adaptive best responses for the ring are in
run_vn_cross.py and run_vn_ensemble.py; here the manipulators do not adapt, so reductions are upper bounds.
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
from marketsim.sim import SimConfig, manipulation_impact, ring_utility, run_episode, tagged_pnl_per_share
from marketsim.vietnam import vn_config

POLICIES = [
    ("band 7% (today)", dict(band=0.07), 1),
    ("band 10%", dict(band=0.10), 1),
    ("tick x2", dict(band=0.07, tick=2), 1),
    ("min rest 5", dict(band=0.07, min_rest=5), 1),
    ("min rest 15", dict(band=0.07, min_rest=15), 1),
    ("cancel fee 0.5", dict(band=0.07, cancel_fee=0.5), 1),
    ("cancel fee 2", dict(band=0.07, cancel_fee=2.0), 1),
    ("circuit breaker 6", dict(band=0.07, halt_move=6.0), 1),
    ("block at 60-step mean", dict(band=0.07), 60),
]
HONEST = dict(n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(0, 0))
ALL = dict(n_spoof=(1, 1), n_pump=(1, 1), n_wash_pairs=(1, 1), n_ring=(1, 1))


def _honest(args):
    seed, cfg = args
    return run_episode(seed, cfg).quality


def _manip(args):
    seed, cfg = args
    ep = run_episode(seed, cfg)
    out = {}
    sp, shares = tagged_pnl_per_share(ep, "spoof_")
    out["spoof profit"] = 0.0 if shares == 0 else sp * shares
    imp = manipulation_impact(ep)
    out["spoof impact"] = float(np.mean(imp["spoof"])) if imp["spoof"] else np.nan
    out["pump impact"] = float(np.mean(imp["pump"])) if imp["pump"] else np.nan
    gt = ep.gt_trades
    tr = ep.events[(ep.events.kind == TRADE) & (ep.events.t >= ep.config.warmup)]
    out["wash volume share"] = float(gt[gt.tag == "wash"].qty.sum() / max(1, tr.qty.sum()))
    ru = ring_utility(ep)
    out["ring gain"] = ru["gain"]
    out["ring displacement"] = ru["displacement"]
    return out


def main(args):
    rows = []
    with ProcessPoolExecutor(args.workers) as pool:
        for label, pol_kw, L in POLICIES:
            pol = Policy(label, day_len=240, **pol_kw)
            base = replace(vn_config(policy=pol), block_vwap=L)
            q = pd.DataFrame(list(pool.map(_honest, [(s, replace(base, **HONEST)) for s in range(19_000_000, 19_000_000 + args.n_quality)])))
            m = pd.DataFrame(list(pool.map(_manip, [(s, replace(base, **ALL)) for s in range(20_000_000, 20_000_000 + args.n_manip)])))
            row = {"policy": label, **{k: q[k].mean() for k in ("spread", "depth", "vol", "tracking_error", "noise_cost", "volume")},
                   **{k: m[k].mean() for k in m.columns}, **{k + " se": m[k].std(ddof=1) / np.sqrt(len(m)) for k in m.columns}}
            rows.append(row)
            print(label, flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(Path(args.out) / "policy_matrix.csv", index=False)
    base = df.iloc[0]
    rel = pd.DataFrame({"policy": df.policy})
    for k in ("spread", "depth", "vol", "tracking_error", "noise_cost", "volume"):
        rel[k + " (%)"] = (df[k] / base[k] - 1) * 100
    text = ["# Policy matrix (Vietnam preset)\n",
            f"{args.n_quality} honest-only episodes and {args.n_manip} episodes with one spoofer, one pump-and-dump agent, one wash pair and one ring "
            "(non-adaptive strategies) per policy. Standard errors in the csv.\n", "## Cost to honest participants (change relative to band 7%)\n",
            rel.round(1).to_markdown(index=False), "", "## What the manipulators achieve\n",
            df[["policy", "spoof profit", "spoof impact", "pump impact", "wash volume share", "ring gain", "ring displacement"]].round(3).to_markdown(index=False), ""]
    (Path(args.out) / "policy_matrix.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-quality", type=int, default=10)
    ap.add_argument("--n-manip", type=int, default=24)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
