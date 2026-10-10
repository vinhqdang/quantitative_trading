"""Natural experiment: the HOSE tick-size reform of 12 September 2016 on public daily prices.

HOSE stocks are treated (before the reform the minimum tick was 500 VND for all prices; afterwards 10, 50 and 100 VND below 10,000,
between 10,000 and 49,950 and above 50,000 VND, according to Vo and Doan, PLOS ONE 2023); HNX and UPCoM stocks are controls.
Outcomes come from daily open/high/low/close/volume only: the Corwin-Schultz high-low spread estimator, the daily range, the absolute
return, the share of zero-return days and log volume. Difference-in-differences of stock-level window means, with a bootstrap over
stocks, placebo event dates, and a weekly event study. Prices in the panel are adjusted, so price bands are approximate (terciles).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.realdata import load_panel

EVENT = pd.Timestamp("2016-09-12")


def corwin_schultz(high: pd.DataFrame, low: pd.DataFrame) -> pd.DataFrame:
    ok = (high > 0) & (low > 0) & (high >= low)
    h, l = high.where(ok), low.where(ok)
    hl = np.log(h / l) ** 2
    beta = hl + hl.shift(-1)
    h2 = np.maximum(h, h.shift(-1))
    l2 = np.minimum(l, l.shift(-1))
    gamma = np.log(h2 / l2) ** 2
    k = 3 - 2 * np.sqrt(2)
    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / k - np.sqrt(gamma / k)
    s = 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))
    return s.clip(lower=0)


def outcomes(panel):
    c, h, l, v = panel["close"], panel["high"], panel["low"], panel["volume"]
    ret = np.log(c).diff()
    return {"CS spread (%)": corwin_schultz(h, l) * 100, "daily range (%)": (np.log(h / l)).where(h >= l) * 100,
            "|return| (%)": ret.abs() * 100, "zero-return share": (ret == 0).astype(float).where(ret.notna()),
            "log volume": np.log1p(v)}


def window_means(df: pd.DataFrame, dates: pd.DatetimeIndex, lo: int, hi: int, min_days: int = 20) -> pd.Series:
    sub = df.loc[dates[lo:hi]]
    m = sub.mean()
    return m.where(sub.notna().sum() >= min_days)


def did(outs, event, hose, ctrl, n_pre=40, n_post=40, gap_days=5, n_boot=500, seed=0, names=None):
    dates = outs["CS spread (%)"].index
    i0 = int(np.searchsorted(dates, event))        # first trading day on or after the event
    rows = []
    rng = np.random.default_rng(seed)
    for name, df in outs.items():
        pre = window_means(df, dates, i0 - n_pre, i0)
        post = window_means(df, dates, i0 + gap_days, i0 + gap_days + n_post)
        d = (post - pre)
        d = d[np.isfinite(d)]
        dh, dc = d[d.index.isin(hose)], d[d.index.isin(ctrl)]
        est = dh.mean() - dc.mean()
        bs = [dh.iloc[rng.integers(0, len(dh), len(dh))].mean() - dc.iloc[rng.integers(0, len(dc), len(dc))].mean() for _ in range(n_boot)]
        rows.append({"outcome": name, "HOSE change": dh.mean(), "control change": dc.mean(), "DiD": est,
                     "ci_lo": np.percentile(bs, 2.5), "ci_hi": np.percentile(bs, 97.5), "n HOSE": len(dh), "n control": len(dc),
                     "pre-period HOSE mean": pre[pre.index.isin(hose)].mean()})
    return pd.DataFrame(rows)


def main(args):
    panel = load_panel(Path(args.folder), min_days=100)
    meta = pd.read_csv(args.meta)
    mk = dict(zip(meta.ticker, meta.market.str.upper()))
    cols = list(panel["close"].columns)
    hose = pd.Index([c for c in cols if mk.get(c) == "HOSE"])
    ctrl = pd.Index([c for c in cols if mk.get(c) in ("HNX", "UPCOM")])
    outs = outcomes(panel)
    text = ["# Natural experiment: HOSE tick-size reform, 12 September 2016\n",
            f"Treated: {len(hose)} HOSE stocks with data; controls: {len(ctrl)} HNX and UPCoM stocks. Windows of 40 trading days before the reform and "
            "40 days starting one week after it. DiD = change of HOSE stocks minus change of controls; 95% interval by bootstrap over stocks.\n"]
    base = did(outs, EVENT, hose, ctrl)
    text += ["## Main estimate\n", base.round(4).to_markdown(index=False), ""]
    rob = []
    for npre, npost in ((20, 20), (60, 60)):
        r = did(outs, EVENT, hose, ctrl, n_pre=npre, n_post=npost)
        r.insert(0, "window", f"{npre}+{npost}")
        rob.append(r)
    text += ["## Other window lengths\n", pd.concat(rob).round(4).to_markdown(index=False), ""]
    pl = []
    for d in ("2016-03-14", "2016-06-13", "2016-12-05", "2017-03-13"):
        r = did(outs, pd.Timestamp(d), hose, ctrl)
        r.insert(0, "placebo date", d)
        pl.append(r[r.outcome.isin(["CS spread (%)", "daily range (%)", "zero-return share"])])
    text += ["## Placebo event dates (no reform)\n", pd.concat(pl).round(4).to_markdown(index=False), ""]
    # by price tercile (adjusted price just before the event)
    c = panel["close"]
    px = c.loc[:EVENT - pd.Timedelta(days=1)].iloc[-1]
    px = px[px.index.isin(hose)].dropna()
    q = pd.qcut(px.rank(method="first"), 3, labels=["low price", "middle price", "high price"])
    tier = []
    for lab in q.cat.categories:
        h = pd.Index(q[q == lab].index)
        r = did({k: v for k, v in outs.items() if k in ("CS spread (%)", "daily range (%)")}, EVENT, h, ctrl)
        r.insert(0, "price tercile (adjusted price)", lab)
        tier.append(r)
    text += ["## By price tercile of the treated stocks (adjusted prices, approximate bands)\n", pd.concat(tier).round(4).to_markdown(index=False), ""]
    # event study by week for the CS spread
    cs = outs["CS spread (%)"]
    dates = cs.index
    i0 = int(np.searchsorted(dates, EVENT))
    pre_mean = cs.iloc[i0 - 40:i0]
    ref_h, ref_c = pre_mean[hose].mean(), pre_mean[ctrl].mean()
    rows = []
    for w in range(-8, 9):
        a, b = i0 + 5 * w, i0 + 5 * w + 5
        if a < 0 or b > len(dates):
            continue
        sl = cs.iloc[a:b]
        rows.append({"week": w, "HOSE": sl[hose].mean().mean() - ref_h.mean(), "controls": sl[ctrl].mean().mean() - ref_c.mean()})
    es = pd.DataFrame(rows)
    es["difference"] = es.HOSE - es.controls
    es.to_csv(Path(args.out) / "tick_reform_eventstudy.csv", index=False)
    text += ["## Weekly event study of the CS spread (percentage points relative to the 40-day pre-period mean)\n", es.round(3).to_markdown(index=False), ""]
    base.to_csv(Path(args.out) / "tick_reform_did.csv", index=False)
    (Path(args.out) / "tick_reform.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
