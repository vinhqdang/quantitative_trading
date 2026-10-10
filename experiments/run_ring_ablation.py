"""Ablations and sensitivity of the signed coincidence test (clean market, one ring per episode, no labels used).

Varies: tolerance set, window length, number of accounts, ring size and ring activity. Reports catch@5 (and catch@1) with 95%
bootstrap intervals over episodes, and the honest false-alarm rate at p <= 0.01.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.coordination import scan_episode
from marketsim.features import label_windows, window_features
from marketsim.sim import SimConfig, run_episode

BASE = replace(SimConfig(), n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(1, 1))
RING_DEFAULT = {}


def _one(args):
    seed, cfg_kw, ring_params, scan_kw, window = args
    cfg = replace(BASE, ring_params=ring_params or None, **cfg_kw)
    ep = run_episode(seed, cfg)
    lab = label_windows(ep, window_features(ep, window), window)[["agent", "window", "y", "kind"]]
    sc = scan_episode(ep, window=window, signed=True, **scan_kw)
    d = lab.merge(sc[["agent", "window", "z", "p"]], on=["agent", "window"], how="left").fillna({"z": 0, "p": 1})
    d["episode"] = seed
    return d


def evaluate(seeds, cfg_kw, ring_params, scan_kw, window, workers):
    with ProcessPoolExecutor(workers) as pool:
        d = pd.concat(list(pool.map(_one, [(s, cfg_kw, ring_params, scan_kw, window) for s in seeds])), ignore_index=True)
    per_ep = {}
    for (e, w), g in d.groupby(["episode", "window"]):
        if g.y.sum() > 0:
            per_ep.setdefault(e, []).append((bool(g.nlargest(5, "z").y.sum() > 0), bool(g.nlargest(1, "z").y.sum() > 0)))
    eps = list(per_ep)
    flat = np.array([h for e in eps for h in per_ep[e]], dtype=float)
    rng = np.random.default_rng(0)
    bs = []
    for _ in range(300):
        pick = rng.choice(len(eps), size=len(eps), replace=True)
        bs.append(np.mean([h for i in pick for h in per_ep[eps[i]]], axis=0))
    bs = np.array(bs)
    hon = d[(d.y == 0) & (d.kind.isin(["noise", "fundamental", "momentum", "imbalance", "market_maker"]))]
    return {"catch@5": f"{flat[:, 0].mean():.2f} [{np.percentile(bs[:, 0], 2.5):.2f}, {np.percentile(bs[:, 0], 97.5):.2f}]",
            "catch@1": f"{flat[:, 1].mean():.2f} [{np.percentile(bs[:, 1], 2.5):.2f}, {np.percentile(bs[:, 1], 97.5):.2f}]",
            "honest flagged p<=0.01": float((hon.p <= 0.01).mean()), "accounts per window": float(d.groupby(["episode", "window"]).size().mean()),
            "ring windows": len(flat)}


def main(args):
    seeds = range(20_000, 20_000 + args.n)
    runs = []
    for tols in [(1,), (1, 5), (1, 5, 15), (1, 5, 15, 30)]:
        runs.append(("tolerances", str(tols), {}, {}, {"tols": tols}, 300))
    for win in (150, 300, 600):
        runs.append(("window length (steps)", str(win), {}, {}, {}, win))
    for n in (80, 200, 400, 800):
        runs.append(("noise traders (accounts)", str(n), {"n_noise": n}, {}, {}, 300))
    for k in (4, 8, 16, 30):
        runs.append(("ring size K", str(k), {}, {"K": k}, {}, 300))
    for pp in (0.2, 0.4, 0.8):
        runs.append(("ring push probability", str(pp), {}, {"p_push": pp, "p_acc": pp / 2}, {}, 300))
    rows = []
    for factor, level, cfg_kw, ring_params, scan_kw, win in runs:
        r = evaluate(seeds, cfg_kw, ring_params, scan_kw, win, args.workers)
        rows.append({"factor": factor, "level": level, **r})
        print(factor, level, r["catch@5"], flush=True)
    df = pd.DataFrame(rows)
    text = ["# Ablations and sensitivity of the signed coincidence test\n",
            f"Clean market, one ring per episode, {args.n} episodes per row, no labels used. Default: tolerances (1, 5, 15), window 300, 500 "
            "default accounts are not used here (default simulator: about 120 accounts), ring size 6-20, default activity.\n"]
    for f, g in df.groupby("factor", sort=False):
        text += [f"## {f}\n", g.drop(columns="factor").round(3).to_markdown(index=False), ""]
    Path(args.out).mkdir(exist_ok=True)
    df.to_csv(Path(args.out) / "ring_ablation.csv", index=False)
    (Path(args.out) / "ring_ablation.md").write_text("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
