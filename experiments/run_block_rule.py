"""Honest cost of pricing off-book block trades at a trailing mean instead of the last price.

For each window length L: mean absolute gap between the last mid and the mean of the trailing L mids, in ticks and in
percent of price, in Vietnam-preset markets without rings. What the rule does to a ring is measured in run_vn_cross.py.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.sim import run_episode
from marketsim.vietnam import vn_config

LS = [1, 15, 30, 60, 120, 240, 480]


def _mids(seed):
    cfg = replace(vn_config(), n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(0, 0))
    return run_episode(seed, cfg).mids[cfg.warmup:]


def main(n: int, workers: int, out: Path) -> str:
    with ProcessPoolExecutor(workers) as pool:
        mids = list(pool.map(_mids, range(11_000_000, 11_000_000 + n)))
    price = vn_config().start_price
    rows = []
    for L in LS:
        gaps = []
        for m in mids:
            c = np.cumsum(np.r_[0, m])
            tm = (c[L:] - c[:-L]) / L if L > 1 else m
            gaps.append(np.abs(m[L - 1:] - tm))
        gap = float(np.mean(np.concatenate(gaps)))
        rows.append({"rule L (steps)": L, "L in trading days": round(L / 240, 2), "honest gap (ticks)": gap,
                     "honest gap (% of price)": gap / price * 100})
    df = pd.DataFrame(rows)
    text = ["# Honest cost of a trailing-mean block price\n",
            f"{n} Vietnam-preset markets without rings (price {price} ticks, 240 steps per day).\n",
            df.round(3).to_markdown(index=False), ""]
    out.mkdir(exist_ok=True)
    df.to_csv(out / "block_rule.csv", index=False)
    (out / "block_rule.md").write_text("\n".join(text))
    return "\n".join(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    print(main(a.n, a.workers, Path(a.out)))
