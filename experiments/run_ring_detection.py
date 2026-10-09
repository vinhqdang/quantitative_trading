"""R1: can coordinated rings be found, with and without labels?

Detectors (score per account and 300-step window; higher = more suspicious):
  otr             order-to-trade ratio (exchange practice)
  iforest         isolation forest on account features, no labels
  pairwise        pairwise flow correlation with permutation null, no labels (baseline, fails)
  coincidence     circular-shift coincidence test, no labels (this work)
  coincidence-4w  the same, evidence pooled over the trailing 4 windows
  gbm (labels)    gradient boosting on account features trained on labelled default rings (upper reference)

Metric: with an inspection budget of B accounts per window, `catch@B` = share of ring-active windows in
which at least one of the B top-ranked accounts is a ring member. Calibration: share of honest accounts flagged
at p <= 0.01 in markets without any ring.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.metrics import average_precision_score

from marketsim.baselines import pairwise_scan_episode
from marketsim.coordination import scan_episode
from marketsim.detect import GBM, IsoForest
from marketsim.features import label_windows, window_features
from marketsim.sim import SimConfig, run_episode

BASE = replace(SimConfig(), n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(1, 1))
VARIANTS = {
    "default": {},
    "many small": {"K": 30, "q": 1, "m_push": 1, "p_push": 1.0},
    "jittered": {"K": 20, "q": 2, "m_push": 2, "jitter": 25},
    "stealth": {"K": 30, "q": 1, "m_push": 1, "p_push": 0.6, "jitter": 30, "cross_frac": 0.0, "p_acc": 0.3},
}
BUDGETS = (1, 3, 5, 10)


def _episode(args):
    seed, params = args
    cfg = replace(BASE, n_ring=(0, 0)) if params is None else replace(BASE, ring_params=params)
    ep = run_episode(seed, cfg)
    df = label_windows(ep, window_features(ep, 300), 300)
    sc = scan_episode(ep)
    pw = pairwise_scan_episode(ep, seed=seed)
    df = df.merge(sc[["agent", "window", "z", "p"]], on=["agent", "window"], how="left")
    df = df.merge(pw, on=["agent", "window"], how="left")
    df[["z", "pair_degree"]] = df[["z", "pair_degree"]].fillna(0)
    df["p"] = df.p.fillna(1.0)
    df["episode"] = seed
    return df


def build(seeds, params, workers):
    with ProcessPoolExecutor(workers) as pool:
        return pd.concat(list(pool.map(_episode, [(s, params) for s in seeds])), ignore_index=True)


def add_pooled(df: pd.DataFrame, L: int = 4) -> pd.DataFrame:
    df = df.sort_values(["episode", "agent", "window"]).copy()
    s = norm.isf(np.clip(df.p, 1 / 301, 0.999))
    df["s"] = s
    g = df.groupby(["episode", "agent"]).s
    df["pooled"] = g.transform(lambda x: x.rolling(L, min_periods=1).sum()) / np.sqrt(L)
    return df


def catch_at(df: pd.DataFrame, score: str, B: int) -> float:
    hits = []
    for _, g in df.groupby(["episode", "window"]):
        if g.y.sum() == 0:
            continue
        hits.append(g.nlargest(B, score).y.sum() > 0)
    return float(np.mean(hits)) if hits else float("nan")


def run(args) -> str:
    train = build(range(args.n_train), {}, args.workers)
    train_all = train  # labels used by gbm only
    gbm = GBM(0).fit(train_all, train_all.y.to_numpy())
    iso = IsoForest(0).fit(train_all)
    honest = add_pooled(build(range(900, 900 + args.n_test), None, args.workers))
    cal = pd.Series({
        "honest accounts flagged p<=0.01": (honest.p <= 0.01).mean(),
        "  of which market makers": (honest[honest.kind == "market_maker"].p <= 0.01).mean(),
        "  of which momentum": (honest[honest.kind == "momentum"].p <= 0.01).mean(),
        "  of which noise": (honest[honest.kind == "noise"].p <= 0.01).mean(),
        "honest accounts flagged p<=0.05": (honest.p <= 0.05).mean(),
    }).round(3)
    rows = []
    for name, params in VARIANTS.items():
        df = add_pooled(build(range(1000, 1000 + args.n_test), params, args.workers))
        df["gbm"] = gbm.score(df)
        df["iforest"] = iso.score(df)
        df["otr_s"] = df.otr
        for label, col in (("otr", "otr_s"), ("iforest (no labels)", "iforest"), ("pairwise (no labels)", "pair_degree"),
                           ("coincidence (no labels)", "z"), ("coincidence-4w (no labels)", "pooled"),
                           ("gbm (labels)", "gbm")):
            r = {"ring": name, "detector": label, "AP": average_precision_score(df.y, df[col])}
            for B in BUDGETS:
                r[f"catch@{B}"] = catch_at(df, col, B)
            rows.append(r)
    res = pd.DataFrame(rows)
    out = ["# R1: finding colluding rings\n",
           f"{args.n_train} labelled default-ring episodes for the label-using / fitted detectors; {args.n_test} test episodes "
           "per ring type. Ring accounts act as noise traders outside their active window. "
           "`catch@B`: share of ring-active windows in which one of the B top-ranked accounts (out of about 120 active) "
           "is a ring member.\n",
           "## Calibration of the coincidence test on honest markets\n", cal.to_markdown(), "\n"]
    for name in VARIANTS:
        t = res[res.ring == name].drop(columns="ring").set_index("detector").round(3)
        out += [f"## {name}\n", t.to_markdown(), "\n"]
    return "\n".join(out), res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-train", type=int, default=24)
    ap.add_argument("--n-test", type=int, default=16)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    text, res = run(args)
    out = Path(args.out)
    out.mkdir(exist_ok=True)
    res.to_csv(out / "ring_detection.csv", index=False)
    (out / "ring_detection.md").write_text(text)
    print(text)
