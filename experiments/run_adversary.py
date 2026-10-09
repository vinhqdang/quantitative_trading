"""Arms race between an adaptive spoofer and a retrained detector.

Round r: the spoofer searches for parameters that maximise (profit - fine * caught) against the
current detector, the best candidate is validated on fresh episodes, the detector is then retrained
on the original data plus episodes produced by that spoofer, and the same parameters are re-scored
against the retrained detector.

fine = 0 is the control: a spoofer that ignores detection.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.adversary import NAMES, SPOOF_DEFAULT, decode, encode, evaluate_population, evolve, make_pool
from marketsim.detect import GBM, build_dataset, operating_threshold
from marketsim.sim import SimConfig


def fit_detector(train: pd.DataFrame, seed: int):
    det = GBM(seed).fit(train, train.y.to_numpy())
    return det, operating_threshold(det, train)


def run(fine: float, rounds: int, args, base: SimConfig) -> pd.DataFrame:
    train, _ = build_dataset(range(args.n_train), base, args.workers)
    det, thr = fit_detector(train, 0)
    rows = []
    with make_pool(args.workers) as pool:
        # reference: the default spoofer against the round-0 detector
        ref = evaluate_population([decode(encode(SPOOF_DEFAULT))], list(range(900_000, 900_000 + args.n_val)),
                                  base, det, thr, pool)[0]
        rows.append(dict(fine=fine, round=-1, who="default spoofer", **ref))
        for r in range(rounds):
            t0 = time.time()
            res = evolve(det, thr, base, fine, pool, seed=r, pop_size=args.pop, gens=args.gens,
                         k_seeds=args.k_seeds)
            val_seeds = list(range(1_000_000 + r * 1000, 1_000_000 + r * 1000 + args.n_val))
            cands = [res.best, res.mean_params]
            vals = evaluate_population(cands, val_seeds, base, det, thr, pool)
            util = [v["profit"] - fine * v["caught"] for v in vals]
            chosen, v = cands[int(np.argmax(util))], vals[int(np.argmax(util))]
            rows.append(dict(fine=fine, round=r, who="adversary vs detector r", **v,
                             **{f"p_{k}": chosen[k] for k in NAMES}))
            # retrain on the original data plus episodes produced by this spoofer
            aug, _ = build_dataset(range(2_000_000 + r * 1000, 2_000_000 + r * 1000 + args.n_aug),
                                   replace(base, spoof_params=chosen), args.workers)
            train = pd.concat([train, aug], ignore_index=True)
            det, thr = fit_detector(train, r + 1)
            after = evaluate_population([chosen], val_seeds, base, det, thr, pool)[0]
            rows.append(dict(fine=fine, round=r, who="same params vs retrained detector", **after,
                             **{f"p_{k}": chosen[k] for k in NAMES}))
            print(f"fine={fine} round {r} done in {time.time() - t0:.0f}s: profit {v['profit']:.1f} "
                  f"caught {v['caught']:.2f} -> after retrain caught {after['caught']:.2f}", flush=True)
    return pd.DataFrame(rows)


def render(df: pd.DataFrame, args) -> str:
    out = ["# Arms race: adaptive spoofer vs retrained detector\n",
           f"Search: evolution strategy, population {args.pop}, {args.gens} generations, {args.k_seeds} episodes per "
           f"candidate (common random numbers). Validation: {args.n_val} fresh episodes. Detector: gradient boosting at the "
           f"1% training-FPR operating point, retrained each round on the original {args.n_train} episodes plus "
           f"{args.n_aug} episodes per round produced by the spoofer's chosen parameters. Each episode has one spoofer "
           "in an otherwise honest market.\n",
           "`profit` = realised mark-to-market profit of spoofing trades per episode (tick-shares). `caught` = share of "
           "episodes in which at least one spoofing window was flagged. `window_rate` = share of spoofing windows flagged. "
           "`impact` = price move in the intended direction 8 steps after the fake orders (ticks).\n"]
    cols = ["round", "who", "profit", "impact", "window_rate", "caught"] + [f"p_{k}" for k in NAMES]
    for fine, g in df.groupby("fine"):
        out.append(f"## fine = {fine:g}\n")
        g = g[[c for c in cols if c in g.columns]].copy()
        for c in g.columns:
            if c not in ("round", "who"):
                g[c] = g[c].astype(float).round(2)
        out += [g.to_markdown(index=False), "\n"]
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fines", type=float, nargs="+", default=[0.0, 100.0])
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--n-train", type=int, default=30)
    ap.add_argument("--n-aug", type=int, default=12)
    ap.add_argument("--n-val", type=int, default=12)
    ap.add_argument("--pop", type=int, default=12)
    ap.add_argument("--gens", type=int, default=5)
    ap.add_argument("--k-seeds", type=int, default=3)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    base = SimConfig()
    df = pd.concat([run(f, args.rounds, args, base) for f in args.fines], ignore_index=True)
    out = Path(args.out)
    out.mkdir(exist_ok=True)
    df.to_csv(out / "adversary.csv", index=False)
    (out / "adversary.md").write_text(render(df, args))
    print((out / "adversary.md").read_text())
