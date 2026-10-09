"""Order-level policy levers: cost to honest participants and effect on fixed (non-adaptive) manipulators.

For each policy:
  quality   honest-only markets: spread, depth, volatility, tracking error, retail cost, volume, halted share
  static    the default spoofer and pump-and-dump agents: price impact and profit

The manipulators here do not adapt to the policy, so a reduction in their profit is an upper bound on what the
policy achieves against an adaptive manipulator (see run_vn_cross.py for best responses of a collusion ring).
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.detect import build_dataset
from marketsim.policy import Policy
from marketsim.sim import SimConfig, run_episode

POLICIES = [
    Policy("baseline"),
    Policy("tick x2", tick=2),
    Policy("tick x4", tick=4),
    Policy("min rest 5", min_rest=5),
    Policy("min rest 15", min_rest=15),
    Policy("cancel fee 0.5", cancel_fee=0.5),
    Policy("cancel fee 2", cancel_fee=2.0),
    Policy("circuit breaker 6", halt_move=6.0),
]

HONEST = dict(n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0))


def _quality(args):
    seed, cfg = args
    return run_episode(seed, cfg).quality


def run(args) -> pd.DataFrame:
    rows = []
    with ProcessPoolExecutor(args.workers) as pool:
        for pol in POLICIES:
            base = replace(SimConfig(), policy=pol)
            q = pd.DataFrame(list(pool.map(_quality, [(s, replace(base, **HONEST)) for s in
                                                      range(3_000_000, 3_000_000 + args.n_quality)])))
            row = {"policy": pol.name, **q.mean().to_dict()}
            _, st = build_dataset(range(4_000_000, 4_000_000 + args.n_static), base, args.workers)
            row["spoof_profit"] = st["spoof"][0] / args.n_static
            row["spoof_impact"] = float(np.mean(st["impact"]["spoof"])) if st["impact"]["spoof"] else np.nan
            row["pump_impact"] = float(np.mean(st["impact"]["pump"])) if st["impact"]["pump"] else np.nan
            rows.append(row)
            print(row["policy"], flush=True)
    return pd.DataFrame(rows)


def render(df: pd.DataFrame, args) -> str:
    base = df[df.policy == "baseline"].iloc[0]
    out = ["# Order-level policy levers\n",
           f"{args.n_quality} honest-only episodes per policy for market quality; {args.n_static} episodes with the default manipulators "
           "(same seeds across policies). Market makers respond to the policy (they skip re-quoting while any quote is locked and re-quote less "
           "often under a cancel fee); other honest agents do not adapt. Manipulators do not adapt either.\n",
           "Market quality (honest-only markets). Lower is better for spread, volatility, tracking error and retail cost; higher is better for depth and volume. "
           "`noise_cost` includes cancel fees paid.\n"]
    cols = ["spread", "depth", "vol", "tracking_error", "noise_cost", "volume", "halted"]
    out += [df.set_index("policy")[cols].round(3).to_markdown(), "\n"]
    out += ["Fixed manipulators. `spoof_profit` = realised spoofing profit per episode (tick-shares); impacts in ticks in the manipulator's intended direction.\n"]
    out += [df.set_index("policy")[["spoof_profit", "spoof_impact", "pump_impact"]].round(2).to_markdown(), "\n"]
    keys = ["spread", "depth", "vol", "tracking_error", "noise_cost", "volume", "spoof_impact", "pump_impact"]
    rel = (df.set_index("policy")[keys] / base[keys].astype(float) - 1) * 100
    out += ["Change relative to baseline (percent):\n", rel.round(0).to_markdown(), "\n"]
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-quality", type=int, default=10)
    ap.add_argument("--n-static", type=int, default=16)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    df = run(args)
    out = Path(args.out)
    out.mkdir(exist_ok=True)
    df.to_csv(out / "policy.csv", index=False)
    (out / "policy.md").write_text(render(df, args))
    print((out / "policy.md").read_text())
