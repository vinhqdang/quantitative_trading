"""Intervals over markets for the ensemble conclusions (the unit of replication is the market).

For each family and pooled over all accepted markets: the ring's gain under block pricing relative to the band alone (median and 95% bootstrap
interval over markets, minimum and maximum), the share of markets in which the block rule lowers the gain (exact sign test against 1/2), and the
share of markets in which inspection leaves a ring with positive net benefit at fine multiple 5 (Wilson interval).
"""

from __future__ import annotations

from math import sqrt
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest

FAM = {"index level": "vn_ensemble.csv", "stock level": "vn_ensemble_stock.csv", "trend-free": "vn_ensemble_acf.csv"}


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def boot_median(x, rng, n=5000):
    x = np.asarray(x)
    m = [np.median(x[rng.integers(0, len(x), len(x))]) for _ in range(n)]
    return np.percentile(m, 2.5), np.percentile(m, 97.5)


def main():
    out = Path("results")
    rng = np.random.default_rng(0)
    frames = []
    for fam, f in FAM.items():
        d = pd.read_csv(out / f)
        d["family"] = fam
        frames.append(d)
    allm = pd.concat(frames)
    rows = []
    for fam, d in list(allm.groupby("family", sort=False)) + [("all markets", allm)]:
        piv = d.pivot_table(index=["family", "market"], columns="policy", values="gain")
        band = piv["band 7% (HOSE today)"]
        r = {"family": fam, "markets": len(piv)}
        for lab, col in (("block 60", "band 7% + block at 60-step mean"), ("block 240", "band 7% + block at 240-step mean")):
            ok = band > 0
            ratio = (piv[col][ok] / band[ok]).to_numpy()
            lo, hi = boot_median(ratio, rng)
            r[f"{lab}: median ratio"] = np.median(ratio)
            r[f"{lab}: 95% CI of median"] = f"{lo:.2f} to {hi:.2f}"
            r[f"{lab}: range"] = f"{ratio.min():.2f} to {ratio.max():.2f}"
            k = int((piv[col][ok] < band[ok]).sum())
            r[f"{lab}: markets with lower gain"] = f"{k}/{ok.sum()}"
            r[f"{lab}: sign-test p"] = binomtest(k, int(ok.sum()), 0.5).pvalue
        ins = d[d.policy == "band 7% + inspect 3 per window"]
        k = int((ins.net_U5 > 0).sum())
        lo, hi = wilson(k, len(ins))
        r["inspect 3: markets with positive net benefit"] = f"{k}/{len(ins)}"
        r["inspect 3: Wilson 95%"] = f"{lo:.2f} to {hi:.2f}"
        r["inspect 3: median caught"] = ins.caught.median()
        rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv(out / "ensemble_intervals.csv", index=False)
    text = ["# Ensemble conclusions with intervals over markets\n",
            "Ratio = ring gain with the block-price rule over ring gain with the band alone (markets with positive band-only gain). Bootstrap over markets "
            "(5000 draws) for the median; exact two-sided sign test of 'lower gain with the rule'. Inspection: share of markets in which the ring's net "
            "benefit at fine multiple 5 stays positive.\n", df.round(3).T.to_markdown()]
    (out / "ensemble_intervals.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    main()
