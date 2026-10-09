"""Policy levers against a best-responding collusion ring, in the Vietnam preset (500-tick price, 240-step day).

Rows: daily price band (none, 7%, 10%, 15%), a block reference-price rule, and budgeted inspection with the
label-free coincidence scan. The ring re-optimises its parameters for each row (evolution strategy started from
the strongest ring found elsewhere). Honest cost of each band is read from markets without rings.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

import run_ring_adversary as rra
from marketsim.policy import Policy
from marketsim.ring_adversary import make_pool, net_utility
from marketsim.sim import run_episode
from marketsim.vietnam import vn_config

ROWS = [
    ("no price band", dict(band=0.0), 1, "none", 0),
    ("band 7% (HOSE today)", dict(band=0.07), 1, "none", 0),
    ("band 10%", dict(band=0.10), 1, "none", 0),
    ("band 15%", dict(band=0.15), 1, "none", 0),
    ("band 7% + block priced at 60-step mean", dict(band=0.07), 60, "none", 0),
    ("band 7% + block priced at 240-step mean", dict(band=0.07), 240, "none", 0),
    ("band 7% + inspect 1 account per window", dict(band=0.07), 1, "scan", 1),
    ("band 7% + inspect 3 accounts per window", dict(band=0.07), 1, "scan", 3),
]


def honest_quality(pol: Policy, n: int) -> dict:
    cfg = replace(vn_config(policy=pol), n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(0, 0))
    q = pd.DataFrame([run_episode(s, cfg).quality for s in range(12_000_000, 12_000_000 + n)])
    return q.mean().to_dict()


def run(args):
    rows, quality = [], []
    t0 = time.time()
    with make_pool(args.workers) as pool:
        for label, pol_kw, L, kind, B in ROWS:
            pol = Policy(label, day_len=240, **pol_kw)
            base = replace(vn_config(policy=pol), block_vwap=L)
            chosen, r = rra.best_response(base, kind, None, B, 5.0, pool, args, 200 + len(rows), init=rra.UNCONSTRAINED)
            row = {"scenario": label, "detector": kind, "B": B, "block rule (steps)": L,
                   "gain": r.gain.mean(), "displacement": r.displacement.mean(), "params": chosen}
            if kind != "none":
                row.update({"caught": r[f"caught{B}"].mean(), "net U (m=5)": net_utility(r, B, 5),
                            "net U (m=10)": net_utility(r, B, 10)})
            rows.append(row)
            print(f"{label}: gain {r.gain.mean():.0f} disp {r.displacement.mean():.1f} "
                  + (f"caught {row['caught']:.2f} " if kind != "none" else "") + f"({time.time() - t0:.0f}s)", flush=True)
    for pol_kw in ({"band": 0.0}, {"band": 0.07}, {"band": 0.10}, {"band": 0.15}):
        pol = Policy(f"band {pol_kw['band']}", day_len=240, **pol_kw)
        quality.append({"band": pol_kw["band"], **honest_quality(pol, args.n_quality)})
    return pd.DataFrame(rows), pd.DataFrame(quality)


def render(df, quality, args):
    out = ["# Policy levers against a best-responding ring (Vietnam preset)\n",
           f"Evolution strategy per row: population {args.pop}, {args.gens} generations, {args.k_seeds} episodes per candidate, started from the "
           f"strongest ring found without any policy; selection on {args.n_val} episodes and reporting on {args.n_val} further episodes. "
           "One ring per episode (3000 steps), 3000-lot block sold off-book at the end of each push. `gain` in tick-lots; `caught` = share of episodes in "
           "which a member was among the inspected accounts of some window (about 500 active accounts per window); `net U (m)` = gain minus m times the "
           "gain when caught (m = 5 for individuals, 10 for organisations under Decree 156/2020).\n"]
    show = df.drop(columns="params").copy()
    for c in show.columns:
        if c not in ("scenario", "detector"):
            show[c] = show[c].astype(float).round(2)
    out += [show.to_markdown(index=False), "\n", "## Honest cost of the price band (markets without rings)\n",
            "`at_limit` is the share of steps with the mid at the band edge; `tracking_error` the mean distance between mid and latent value (ticks).\n",
            quality.round(3).to_markdown(index=False), "\n", "## Parameters chosen by the ring\n"]
    for _, r in df.iterrows():
        out.append(f"- {r.scenario}: { {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.params.items()} }")
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-val", type=int, default=12)
    ap.add_argument("--pop", type=int, default=8)
    ap.add_argument("--gens", type=int, default=5)
    ap.add_argument("--k-seeds", type=int, default=3)
    ap.add_argument("--n-quality", type=int, default=4)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    df, quality = run(args)
    out = Path(args.out)
    out.mkdir(exist_ok=True)
    df.drop(columns="params").to_csv(out / "vn_policy.csv", index=False)
    quality.to_csv(out / "vn_quality.csv", index=False)
    (out / "vn_policy.md").write_text(render(df, quality, args))
    print((out / "vn_policy.md").read_text())
