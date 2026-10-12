"""Inference for the HOSE tick-reform difference-in-differences: placebo event dates over 2015-2018, a permutation of the exchange labels
at the true date, a pre-trend test on the weekly differences, and the composition of the sample.

Placebo dates: every `step` trading days, excluding dates whose windows overlap the reform window; the DiD at each placebo date uses the
same 40+40-day windows and the same definition of the treated (HOSE) and control (HNX, UPCoM) stocks.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.realdata import load_panel
from run_tick_reform import EVENT, outcomes, window_means

NAMES = ("CS spread (%)", "zero-return share", "daily range (%)")


def change(df, dates, i0, n_pre, n_post, gap=5):
    pre = window_means(df, dates, max(i0 - n_pre, 0), i0)
    post = window_means(df, dates, i0 + gap, i0 + gap + n_post)
    d = post - pre
    return d[np.isfinite(d)]


def main(args):
    panel = load_panel(Path(args.folder), min_days=100)
    meta = pd.read_csv(args.meta)
    mk = dict(zip(meta.ticker, meta.market.str.upper()))
    cols = list(panel["close"].columns)
    hose = pd.Index([c for c in cols if mk.get(c) == "HOSE"])
    ctrl = pd.Index([c for c in cols if mk.get(c) in ("HNX", "UPCOM")])
    outs = {k: v for k, v in outcomes(panel).items() if k in NAMES}
    dates = outs[NAMES[0]].index
    i_ev = int(np.searchsorted(dates, EVENT))
    n_pre = n_post = args.window
    lo = int(np.searchsorted(dates, pd.Timestamp("2015-01-01")))
    hi = int(np.searchsorted(dates, pd.Timestamp("2019-01-01"))) - (n_post + 5)
    cand = [i for i in range(max(lo, n_pre), hi, args.step) if abs(i - i_ev) > n_pre + n_post + 5]
    rows = []
    for i in cand + [i_ev]:
        for name, df in outs.items():
            d = change(df, dates, i, n_pre, n_post)
            dh, dc = d[d.index.isin(hose)], d[d.index.isin(ctrl)]
            if len(dh) < 50 or len(dc) < 50:
                continue
            rows.append({"date": dates[i], "outcome": name, "DiD": dh.mean() - dc.mean(), "n HOSE": len(dh), "n control": len(dc),
                         "true": i == i_ev})
    r = pd.DataFrame(rows)
    r.to_csv(Path(args.out) / "tick_placebo_dates.csv", index=False)
    text = ["# Tick reform: inference by placebo dates, label permutation and pre-trend test\n",
            f"Placebo dates every {args.step} trading days over 2015-2018 (windows {n_pre}+{n_post} days, gap 5 days), excluding dates whose windows overlap the reform's; "
            f"{r[~r.true].date.nunique()} placebo dates with at least 50 treated and 50 control stocks.\n"]
    summ = []
    for name in NAMES:
        s = r[r.outcome == name]
        true = s[s.true].DiD.iloc[0]
        pl = s[~s.true].DiD
        summ.append({"outcome": name, "true DiD": true, "placebo mean": pl.mean(), "placebo sd": pl.std(), "placebo 2.5%": pl.quantile(.025),
                     "placebo 97.5%": pl.quantile(.975), "share of placebos with DiD <= true": (pl <= true).mean(),
                     "two-sided placebo p": (pl.abs() >= abs(true)).mean(), "z (true vs placebo sd)": (true - pl.mean()) / pl.std(),
                     "number of placebo dates": len(pl)})
    summ = pd.DataFrame(summ)
    summ.to_csv(Path(args.out) / "tick_placebo_summary.csv", index=False)
    text += ["## True estimate against the placebo distribution\n", summ.round(4).to_markdown(index=False), ""]

    # permutation of exchange labels at the true date: random assignment keeping the group sizes
    rng = np.random.default_rng(0)
    perm = []
    for name, df in outs.items():
        d = change(df, dates, i_ev, n_pre, n_post)
        both = d[d.index.isin(hose) | d.index.isin(ctrl)]
        nh = int(both.index.isin(hose).sum())
        true = both[both.index.isin(hose)].mean() - both[both.index.isin(ctrl)].mean()
        v = both.to_numpy()
        sims = []
        for _ in range(args.n_perm):
            p = rng.permutation(len(v))
            sims.append(v[p[:nh]].mean() - v[p[nh:]].mean())
        sims = np.array(sims)
        perm.append({"outcome": name, "true DiD": true, "permutation sd": sims.std(), "two-sided permutation p": (np.abs(sims) >= abs(true)).mean(),
                     "n permutations": args.n_perm})
    perm = pd.DataFrame(perm)
    perm.to_csv(Path(args.out) / "tick_permutation.csv", index=False)
    text += ["## Permutation of the exchange labels at the true date\n", perm.round(4).to_markdown(index=False), ""]

    # pre-trend: weekly differences (HOSE minus control) of the spread, relative to the 40-day pre mean, weeks -8..-1; and a stock-level test
    es = pd.read_csv(Path(args.out) / "tick_reform_eventstudy.csv")
    pre = es[es.week < 0]
    x = pre.week.to_numpy(float)
    y = pre["difference"].to_numpy()
    X = np.c_[np.ones_like(x), x]
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    se = np.sqrt(res @ res / (len(y) - 2) * np.linalg.inv(X.T @ X)[1, 1])
    post = es[es.week >= 1]
    pt = pd.DataFrame([{"pre-period weeks": len(pre), "mean difference pre": y.mean(), "sd of weekly differences pre": y.std(ddof=1),
                        "pre slope per week": beta[1], "slope t-stat": beta[1] / se, "mean difference post (weeks 1-8)": post["difference"].mean(),
                        "post mean in units of the pre sd": post["difference"].mean() / y.std(ddof=1)}])
    pt.to_csv(Path(args.out) / "tick_pretrend.csv", index=False)
    text += ["## Pre-trend of the weekly spread difference (weeks -8 to -1)\n", pt.round(4).to_markdown(index=False), ""]

    # sample composition
    first = panel["close"].apply(lambda s: s.first_valid_index())
    ncnt = lambda g, a, b: int((panel["close"].loc[dates[a]:dates[b - 1], g].notna().sum() >= 20).sum())
    comp = pd.DataFrame([{"group": nm, "with any data (min 100 days)": len(g), "listed before pre-window start": int((first[g] < dates[i_ev - n_pre]).sum()),
                          "20+ days in pre-window": ncnt(g, i_ev - n_pre, i_ev), "20+ days in post-window": ncnt(g, i_ev + 5, i_ev + 5 + n_post)}
                         for nm, g in (("HOSE", hose), ("HNX+UPCoM", ctrl))])
    comp.to_csv(Path(args.out) / "tick_sample.csv", index=False)
    text += ["## Sample composition (stocks)\n", comp.to_markdown(index=False), ""]
    (Path(args.out) / "tick_placebo.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--out", default="results")
    ap.add_argument("--window", type=int, default=40)
    ap.add_argument("--step", type=int, default=10)
    ap.add_argument("--n-perm", type=int, default=5000)
    main(ap.parse_args())
