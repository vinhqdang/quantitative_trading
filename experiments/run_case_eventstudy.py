"""Event-time paths of documented manipulation cases on public daily data.

For each included case, trading days are indexed relative to the first day of the documented period (day 0). Reported per day:
the cumulative market-adjusted log return since day -60 (market = median stock return of the day), the stock's cross-sectional
percentile of the market-adjusted-return score, of the volume-surge score and of the combined (Fisher) score (all computed from
data up to that day, 20-day windows), and the daily share of ceiling days. Also the average over cases at each event day.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.realdata import compute_features, cross_percentiles, load_panel, scores

PRE, POST = 60, 180


def main(a):
    panel = load_panel(Path(a.folder))
    feats = compute_features(panel, window=20)
    sc = scores(feats)
    pct_up = cross_percentiles(np.fmax(np.nan_to_num(feats["up"]), np.nan_to_num(feats["down"])) + 0 * feats["up"])
    pct_surge = cross_percentiles(feats["surge"])
    pct_fisher = cross_percentiles(sc["fisher"])
    close = panel["close"]
    dates = close.index
    ret = np.log(close).diff()
    mkt = ret.where((panel["volume"] > 0) & close.notna()).median(axis=1)
    ex = ret.sub(mkt, axis=0)
    cols = {c: i for i, c in enumerate(close.columns)}
    cases = pd.read_csv(a.cases)
    cases = cases[cases.include.astype(str).str.lower().isin(["yes", "true", "1"])]
    rows = []
    for _, c in cases.iterrows():
        if c.ticker not in cols:
            continue
        j = cols[c.ticker]
        start = np.searchsorted(dates, pd.Timestamp(c.start))
        end = np.searchsorted(dates, pd.Timestamp(c.end), side="right") - 1
        lo, hi = max(0, start - PRE), min(len(dates) - 1, start + POST)
        if start - lo < 20:
            continue
        base_idx = max(lo, start - PRE)
        car = ex.iloc[base_idx:hi + 1, j].fillna(0).cumsum()
        for k, d in enumerate(range(lo, hi + 1)):
            rows.append({"ticker": c.ticker, "rel_day": d - start, "in_period": bool(start <= d <= end),
                         "car": float(car.iloc[d - base_idx]) if d >= base_idx else np.nan,
                         "pct_return_score": pct_up[d, j], "pct_surge_score": pct_surge[d, j], "pct_fisher": pct_fisher[d, j],
                         "ceiling": float(abs(ret.iloc[d, j]) >= 0.065) if np.isfinite(ret.iloc[d, j]) else np.nan,
                         "period_days": end - start + 1})
    df = pd.DataFrame(rows)
    df.to_csv(Path(a.out) / "case_eventstudy.csv", index=False)
    avg = df.groupby("rel_day")[["car", "pct_return_score", "pct_surge_score", "pct_fisher", "ceiling"]].mean()
    avg["n"] = df.groupby("rel_day").size()
    avg.to_csv(Path(a.out) / "case_eventstudy_mean.csv")
    print(df.ticker.nunique(), "cases;", len(df), "rows")
    print(avg.loc[[-60, -20, 0, 20, 60, 120]].round(3))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--cases", default="data/cases.csv")
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
