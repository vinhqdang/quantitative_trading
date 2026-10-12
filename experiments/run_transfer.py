"""Does a supervised detector trained in one simulated market transfer to another?

A gradient-boosting detector is trained on labelled default-ring episodes of the generic simulator configuration (the setting of run_ring_detection.py),
and applied, unchanged, to markets of the Vietnam preset: the default preset and accepted markets of the index-level, stock-level and trend-free
families. It is compared with (a) the label-free coincidence test (pooled over four windows) and (b) the same detector trained on labelled episodes of the
test market itself (an upper reference that needs labels from that market). Ring: the default ring. Metric: catch@B (share of ring-active windows in which one of the B
top-ranked accounts is a ring member), the metric used throughout the paper.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import multiprocessing as mp
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from marketsim.coordination import scan_episode
from marketsim.detect import GBM
from marketsim.features import label_windows, window_features
from marketsim.sim import SimConfig, run_episode
from marketsim.vietnam import vn_config

KEYS = ("n_noise", "n_fund", "mm_activity", "fund_sigma", "mm_imb_sens", "mom_activity")
FAMILIES = {"index level": "vn_ensemble_draws.csv", "stock level": "vn_ensemble_stock_draws.csv", "trend-free": "vn_ensemble_acf_draws.csv"}
HONEST_OFF = dict(n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(1, 1))
BUDGETS = (1, 3, 5, 10)


def _episode(args):
    seed, cfg = args
    ep = run_episode(seed, cfg)
    df = label_windows(ep, window_features(ep, 300), 300)
    sc = scan_episode(ep)
    df = df.merge(sc[["agent", "window", "z", "p"]], on=["agent", "window"], how="left")
    df["z"] = df.z.fillna(0)
    df["p"] = df.p.fillna(1.0)
    df["episode"] = seed
    return df


def build(pool, seeds, cfg):
    return pd.concat(list(pool.map(_episode, [(s, cfg) for s in seeds])), ignore_index=True)


def add_pooled(df, L=4):
    df = df.sort_values(["episode", "agent", "window"]).copy()
    df["s"] = norm.isf(np.clip(df.p, 1 / 301, 0.999))
    df["pooled"] = df.groupby(["episode", "agent"]).s.transform(lambda x: x.rolling(L, min_periods=1).sum()) / np.sqrt(L)
    return df


def catch_at(df, score, B):
    hits = [g.nlargest(B, score).y.sum() > 0 for _, g in df.groupby(["episode", "window"]) if g.y.sum() > 0]
    return float(np.mean(hits)) if hits else float("nan")


def main(args):
    out = Path(args.out)
    generic = replace(SimConfig(), **HONEST_OFF)
    markets = [("default preset", "Vietnam preset", vn_config(**HONEST_OFF))]
    for fam, f in FAMILIES.items():
        d = pd.read_csv(out / f)
        for _, mk in d[d.accepted].head(args.n_markets).iterrows():
            params = {k: (int(mk[k]) if k in ("n_noise", "n_fund") else float(mk[k])) for k in KEYS}
            markets.append((fam, f"market {int(mk.draw)}", replace(vn_config(**params), **HONEST_OFF)))
    rows = []
    with ProcessPoolExecutor(args.workers, mp_context=mp.get_context("spawn")) as pool:
        train = build(pool, range(100, 100 + args.n_train), generic)
        gbm_t = GBM(0).fit(train, train.y.to_numpy())
        for fam, name, cfg in markets:
            test = add_pooled(build(pool, range(7000, 7000 + args.n_test), cfg))
            tr_in = build(pool, range(8000, 8000 + args.n_train), cfg)
            gbm_in = GBM(0).fit(tr_in, tr_in.y.to_numpy())
            test["gbm_transfer"] = gbm_t.score(test)
            test["gbm_in"] = gbm_in.score(test)
            for lab, col in (("label-free coincidence", "pooled"), ("GBM trained on generic simulator", "gbm_transfer"), ("GBM trained in this market", "gbm_in")):
                r = {"family": fam, "market": name, "detector": lab, **{f"catch@{B}": catch_at(test, col, B) for B in BUDGETS}}
                rows.append(r)
            print(fam, name, {r["detector"][:12]: round(r["catch@3"], 2) for r in rows[-3:]}, flush=True)
            pd.DataFrame(rows).to_csv(out / "transfer.csv", index=False)
    df = pd.DataFrame(rows)
    df.to_csv(out / "transfer.csv", index=False)
    summ = df.groupby(["family", "detector"], sort=False)[[f"catch@{B}" for B in BUDGETS]].mean()
    text = ["# Transfer of a supervised detector across simulated markets\n",
            f"GBM trained on {args.n_train} labelled default-ring episodes of the generic simulator; test on {args.n_test} ring episodes per market "
            "(default ring). `GBM trained in this market` uses labelled episodes of the test market itself.\n",
            "## Per market\n", df.round(3).to_markdown(index=False), "", "## Mean over markets of each family\n", summ.round(3).to_markdown(), ""]
    (out / "transfer.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-train", type=int, default=24)
    ap.add_argument("--n-test", type=int, default=16)
    ap.add_argument("--n-markets", type=int, default=3)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
