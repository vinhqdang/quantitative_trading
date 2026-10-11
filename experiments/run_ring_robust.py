"""Robustness of ring detection to honest groups that act in step with each other.

Scenarios (one ring per episode unless noted): clean market; plus market-making desks that re-quote together;
plus a fund splitting orders across sub-accounts; plus a bot fleet reacting to one price signal; all three.
Detectors: coincidence test without sign (same-side counts), with sign (buys net of sells per step), isolation forest
without labels, gradient boosting trained with labels on clean-market rings only, order-to-trade ratio.
Metric: catch@B = share of ring-active windows in which one of the B top-ranked accounts is a ring member; 95%
confidence intervals by bootstrap over episodes. Also the share of honest group members with p <= 0.01.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from marketsim.coordination import scan_episode
from marketsim.detect import GBM, IsoForest
from marketsim.features import label_windows, window_features
from marketsim.sim import SimConfig, run_episode

BASE = replace(SimConfig(), n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(1, 1))
SCENARIOS = {
    "clean": {},
    "+ MM desks": {"n_desks": (1, 2)},
    "+ fund splitting orders": {"n_slice": (1, 2)},
    "+ bot fleet": {"n_fleet": (1, 1)},
    "all three": {"n_desks": (1, 2), "n_slice": (1, 2), "n_fleet": (1, 1)},
}
BUDGETS = (1, 3, 5, 10)
HONEST_GROUPS = ["mm_desk", "fund_sub", "bot_fleet"]


def _episode(args):
    seed, extra = args
    cfg = replace(BASE, **extra)
    ep = run_episode(seed, cfg)
    df = label_windows(ep, window_features(ep, 300), 300)
    for name, sg in (("unsigned", False), ("signed", True)):
        sc = scan_episode(ep, signed=sg)
        df = df.merge(sc[["agent", "window", "z", "p"]].rename(columns={"z": "z_" + name, "p": "p_" + name}),
                      on=["agent", "window"], how="left")
    df[["z_unsigned", "z_signed"]] = df[["z_unsigned", "z_signed"]].fillna(0)
    df[["p_unsigned", "p_signed"]] = df[["p_unsigned", "p_signed"]].fillna(1)
    df["episode"] = seed
    return df


def build(seeds, extra, workers):
    with ProcessPoolExecutor(workers) as pool:
        return pd.concat(list(pool.map(_episode, [(s, extra) for s in seeds])), ignore_index=True)


def catch(df: pd.DataFrame, col: str, B: int, boot: int = 300, seed: int = 0):
    per_ep = {}
    for (e, w), g in df.groupby(["episode", "window"]):
        if g.y.sum() > 0:
            per_ep.setdefault(e, []).append(bool(g.nlargest(B, col).y.sum() > 0))
    eps = list(per_ep)
    point = float(np.mean([h for e in eps for h in per_ep[e]]))
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(boot):
        pick = rng.choice(len(eps), size=len(eps), replace=True)
        vals = [h for i in pick for h in per_ep[eps[i]]]
        bs.append(np.mean(vals))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return point, lo, hi


def main(args):
    train = build(range(args.n_train), {}, args.workers)
    gbm = GBM(0).fit(train, train.y.to_numpy())
    iso = IsoForest(0).fit(train)
    rows, groups = [], []
    for name, extra in SCENARIOS.items():
        df = build(range(10_000, 10_000 + args.n_test), extra, args.workers)
        df["gbm"] = gbm.score(df)
        df["iforest"] = iso.score(df)
        df["otr_s"] = df.otr
        keep = [c for c in ("episode", "window", "agent", "kind", "y", "z_unsigned", "z_signed", "p_unsigned", "p_signed", "gbm", "iforest", "otr_s") if c in df]
        df[keep].to_csv(Path(args.out) / f"ring_robust_scores_{name.replace(' ', '_').replace('+', 'plus')}.csv.gz", index=False)
        for label, col in (("order-to-trade ratio", "otr_s"), ("isolation forest (no labels)", "iforest"),
                           ("coincidence, unsigned (no labels)", "z_unsigned"),
                           ("coincidence, signed (no labels)", "z_signed"),
                           ("gradient boosting (trained with labels, clean market)", "gbm")):
            r = {"scenario": name, "detector": label, "AP": average_precision_score(df.y, df[col])}
            for B in BUDGETS:
                p, lo, hi = catch(df, col, B)
                r[f"catch@{B}"] = f"{p:.2f} [{lo:.2f}, {hi:.2f}]"
            rows.append(r)
        for kind in HONEST_GROUPS:
            sub = df[df.kind == kind]
            if len(sub):
                groups.append({"scenario": name, "group": kind, "members scored": len(sub),
                               "flagged, unsigned": (sub.p_unsigned <= 0.01).mean(),
                               "flagged, signed": (sub.p_signed <= 0.01).mean()})
        print(name, "done", flush=True)
    res, grp = pd.DataFrame(rows), pd.DataFrame(groups)
    text = ["# Ring detection with honest groups acting in step\n",
            f"{args.n_train} clean labelled episodes for the fitted detectors; {args.n_test} test episodes per scenario; "
            "95% bootstrap intervals over episodes in brackets. Chance for catch@B is about B divided by the number of active accounts "
            "(roughly 120-170).\n"]
    for name in SCENARIOS:
        text += [f"## {name}\n", res[res.scenario == name].drop(columns="scenario").set_index("detector").round(3).to_markdown(), "\n"]
    text += ["## Honest group members flagged at p <= 0.01 (nominal 1%)\n", grp.round(3).to_markdown(index=False), ""]
    Path(args.out).mkdir(exist_ok=True)
    res.to_csv(Path(args.out) / "ring_robust.csv", index=False)
    (Path(args.out) / "ring_robust.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-train", type=int, default=24)
    ap.add_argument("--n-test", type=int, default=24)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
