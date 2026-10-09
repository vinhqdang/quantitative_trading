"""Evaluate regulatory policies against honest participants and against manipulators.

For each policy:
  quality      honest-only markets: spread, depth, volatility, tracking error, retail cost, volume
  static       the default (non-adaptive) manipulators: spoofing and pump-and-dump effect and profit
  best-reply   a spoofer that re-optimises its parameters for profit under that policy (no detection),
               validated on fresh episodes

A policy that cuts the static manipulators' profit but not the best-replying spoofer's has only
changed which strategy they use.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.adversary import NullDetector, decode, encode, SPOOF_DEFAULT, evaluate_population, evolve, make_pool
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
    Policy("min rest 5 + fee 0.5", min_rest=5, cancel_fee=0.5),
]

HONEST = dict(n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0))


def _quality(args):
    seed, cfg = args
    return run_episode(seed, cfg).quality


def run(args) -> pd.DataFrame:
    rows = []
    null = NullDetector()
    with make_pool(args.workers) as pool:
        for pol in POLICIES:
            t0 = time.time()
            base = replace(SimConfig(), policy=pol)
            q = pd.DataFrame(list(pool.map(_quality, [(s, replace(base, **HONEST)) for s in
                                                      range(3_000_000, 3_000_000 + args.n_quality)])))
            row = {"policy": pol.name, **q.mean().to_dict()}

            _, st = build_dataset(range(4_000_000, 4_000_000 + args.n_static), base, args.workers)
            row["spoof_profit_static"] = st["spoof"][0] / args.n_static
            row["spoof_impact_static"] = float(np.mean(st["impact"]["spoof"])) if st["impact"]["spoof"] else np.nan
            row["pump_impact_static"] = float(np.mean(st["impact"]["pump"])) if st["impact"]["pump"] else np.nan

            res = evolve(null, 1.0, base, 0.0, pool, seed=11, pop_size=args.pop, gens=args.gens, k_seeds=args.k_seeds)
            val = list(range(5_000_000, 5_000_000 + args.n_val))
            cands = [res.best, res.mean_params, decode(encode(SPOOF_DEFAULT))]
            vals = evaluate_population(cands, val, base, null, 1.0, pool)
            best = int(np.argmax([v["profit"] for v in vals[:2]]))
            row["spoof_profit_best"] = vals[best]["profit"]
            row["spoof_impact_best"] = vals[best]["impact"]
            row["spoof_profit_default_check"] = vals[2]["profit"]
            row["best_params"] = {k: round(v, 2) if isinstance(v, float) else v for k, v in cands[best].items()}
            rows.append(row)
            print(f"{pol.name}: {time.time() - t0:.0f}s  best-reply profit {row['spoof_profit_best']:.1f}", flush=True)
    return pd.DataFrame(rows)


def render(df: pd.DataFrame, args) -> str:
    base = df[df.policy == "baseline"].iloc[0]
    out = ["# Policy evaluation\n",
           f"{args.n_quality} honest-only episodes per policy for market quality; {args.n_static} episodes with the default "
           f"manipulators; best-reply spoofer found by evolution strategy (population {args.pop}, {args.gens} "
           f"generations, {args.k_seeds} episodes per candidate) and validated on {args.n_val} fresh episodes. "
           "Market makers respond to the policy (they skip re-quoting while any quote is locked, and re-quote less "
           "often under a cancel fee); other honest agents do not adapt.\n",
           "Market quality (honest-only markets). Lower is better for spread, volatility, tracking error and retail cost; "
           "higher is better for depth and volume.\n"]
    cols = ["spread", "depth", "vol", "tracking_error", "noise_cost", "volume", "halted"]
    q = df.set_index("policy")[cols].round(3)
    out += [q.to_markdown(), "\n"]
    out += ["Manipulation outcomes. `profit` = realised spoofing profit per episode (tick-shares), `impact` = price move in "
            "the manipulator's intended direction (ticks).\n"]
    m = df.set_index("policy")[["spoof_profit_static", "spoof_impact_static", "pump_impact_static",
                                "spoof_profit_best", "spoof_impact_best"]].round(2)
    out += [m.to_markdown(), "\n"]
    out += ["Best-reply spoofer parameters per policy:\n"]
    for _, r in df.iterrows():
        out.append(f"- {r.policy}: {r.best_params}")
    out.append("")
    out += ["Change relative to baseline (percent):\n"]
    keys = ["spread", "depth", "vol", "tracking_error", "noise_cost", "volume", "spoof_profit_static", "spoof_profit_best"]
    rel = (df.set_index("policy")[keys] / base[keys].astype(float) - 1) * 100
    out += [rel.round(0).to_markdown(), "\n"]
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-quality", type=int, default=8)
    ap.add_argument("--n-static", type=int, default=12)
    ap.add_argument("--n-val", type=int, default=16)
    ap.add_argument("--pop", type=int, default=12)
    ap.add_argument("--gens", type=int, default=5)
    ap.add_argument("--k-seeds", type=int, default=3)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    df = run(args)
    out = Path(args.out)
    out.mkdir(exist_ok=True)
    df.to_csv(out / "policy.csv", index=False)
    (out / "policy.md").write_text(render(df, args))
    print((out / "policy.md").read_text())
