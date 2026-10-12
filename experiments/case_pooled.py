"""Pooled test over the documented cases: is the number of cases that reach the daily top-B list more than expected by chance?

Under the null each case stock reaches the list on some date with the probability that a random stock does (`chance topB`, measured per case in
run_case_validation.py). The number of hits is then Poisson-binomial; the exact upper-tail probability is reported with the chance-expected number of hits.
Fisher's method is also applied to the per-case p-values against random stocks (cases are different stocks and periods, treated as independent).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2


def pb_tail(p, k):
    pmf = np.array([1.0])
    for x in p:
        pmf = np.convolve(pmf, [1 - x, x])
    return float(pmf[k:].sum())


def main():
    rows = []
    for tag, w in (("", 20), ("_w10", 10), ("_w60", 60)):
        d = pd.read_csv(f"results/case_validation{tag}_cases.csv")
        for det in d.detector.unique():
            s = d[d.detector == det]
            r = {"window": w, "detector": det, "cases": len(s)}
            for b in (10, 20, 50):
                k = int(s[f"top{b}"].sum())
                p = s[f"chance top{b}"].to_numpy()
                r[f"top{b}: hits"] = k
                r[f"top{b}: expected by chance"] = float(p.sum())
                r[f"top{b}: p"] = pb_tail(p, k)
            pv = np.clip(s["p vs random stocks"].to_numpy(), 1 / 301, 1)
            r["Fisher p (vs random stocks)"] = float(chi2.sf(-2 * np.log(pv).sum(), 2 * len(pv)))
            rows.append(r)
    df = pd.DataFrame(rows)
    df.to_csv("results/case_pooled.csv", index=False)
    Path("results/case_pooled.md").write_text("# Pooled test over documented cases\n\n" + df.round(3).to_markdown(index=False) + "\n")
    print(df[df.window == 20].round(3).to_markdown(index=False))
    print(df[df.detector == "combined (Fisher)"].round(3).to_markdown(index=False))


if __name__ == "__main__":
    main()
