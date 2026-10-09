"""Descriptive statistics of real Vietnamese market data, to calibrate what published sources do not give.

Inputs (downloaded separately, not stored in this repository):
  --indices DIR   CSVs of VN30 / VN-Index bars (time in epoch seconds, open/high/low/close, optional volume)
  --futures CSV   VN30F1M ticks: datetime, tickersymbol, price, best-bid, best-ask, spread, date, close
Output: results/real_data_stats.md
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def bars(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["time", "close"])
    df["t"] = pd.to_datetime(df.time, unit="s") + pd.Timedelta(hours=7)  # exchange time (UTC+7)
    return df.set_index("t").sort_index()


def ret_stats(close: pd.Series) -> dict:
    r = np.log(close).diff().dropna()
    r = r[np.isfinite(r)]
    a = r.abs()
    return {"n": len(r), "sd %": r.std() * 100, "excess kurtosis": r.kurt(), "autocorr |r| lag1": a.autocorr(1),
            "autocorr |r| lag5": a.autocorr(5), "share |r| > 3 sd": float((r.abs() > 3 * r.std()).mean())}


def index_section(d: Path) -> list[str]:
    rows = []
    for name, fn in [("VN30 daily", "HOSE_DLY_VN301D.csv"), ("VN-Index daily", "HOSE_DLY_VNINDEX1D.csv"),
                     ("VN100 daily", "HOSE_DLY_VN1001D.csv")]:
        p = d / fn
        if not p.exists():
            continue
        c = bars(p).close
        full = ret_stats(c)
        recent = ret_stats(c[c.index >= "2023-01-01"])
        rows.append({"series": name, "from": c.index[0].date(), "to": c.index[-1].date(), "sd % (all)": full["sd %"],
                     "sd % (2023+)": recent["sd %"], "excess kurtosis": full["excess kurtosis"],
                     "autocorr |r| lag1": full["autocorr |r| lag1"], "autocorr |r| lag5": full["autocorr |r| lag5"]})
    out = ["## Index returns\n", pd.DataFrame(rows).round(3).to_markdown(index=False), ""]
    p = d / "HOSE_DLY_VN3030.csv"
    if p.exists():
        c = bars(p).close
        c = c[c.index >= "2023-01-01"]
        per_day = c.groupby(c.index.date).size().median()
        r = np.log(c).diff()
        same_day = r[pd.Series(c.index.date, index=c.index).shift(1) == pd.Series(c.index.date, index=c.index)]
        out += [f"VN30 30-minute bars since 2023: median {per_day:.0f} bars per day, intraday 30-minute return sd "
                f"{same_day.std() * 100:.3f}%.\n"]
    return out


def futures_section(path: Path) -> list[str]:
    df = pd.read_csv(path, usecols=["datetime", "price", "best-bid", "best-ask", "spread"])
    df["datetime"] = pd.to_datetime(df.datetime)
    df = df[(df["best-ask"] > df["best-bid"]) & (df.spread > 0)]
    df["day"] = df.datetime.dt.date
    tick = 0.1
    spread_ticks = (df.spread / tick).round()
    dist = spread_ticks.clip(upper=5).value_counts(normalize=True).sort_index()
    daily_close = df.groupby("day").price.last()
    dr = np.log(daily_close).diff().dropna()
    one_min = df.set_index("datetime").price.resample("1min").last().dropna()
    same_day = one_min.groupby(one_min.index.date).apply(lambda s: np.log(s).diff()).dropna()
    per_day = df.groupby("day").size()
    mid = (df["best-bid"] + df["best-ask"]) / 2
    out = ["## VN30F1M ticks (real)\n",
           f"{len(df):,} quote-bearing ticks over {df.day.nunique()} trading days ({df.datetime.min().date()} to {df.datetime.max().date()}); "
           f"index price about {df.price.median():.0f} points, tick 0.1 point, so one tick is {tick / df.price.median() * 1e4:.1f} bp.\n",
           f"- Spread in ticks (share of ticks): " + ", ".join(f"{int(k)}{'+' if k >= 5 else ''}: {v:.3f}" for k, v in dist.items()),
           f"- Mean spread {df.spread.mean():.3f} points = {df.spread.mean() / df.price.median() * 1e4:.1f} bp; median {spread_ticks.median():.0f} tick.",
           f"- Ticks per trading day: median {per_day.median():.0f}; mean gap between ticks {(df.groupby('day').datetime.apply(lambda s: s.diff().dt.total_seconds().median())).median():.1f} s (median).",
           f"- Daily return sd {dr.std() * 100:.3f}% (from last tick of each day), excess kurtosis {dr.kurt():.2f}.",
           f"- One-minute return sd {same_day.std() * 100:.4f}%; excess kurtosis {same_day.kurt():.1f}.",
           f"- Price changes per tick: share of non-zero changes {(df.price.diff().fillna(0) != 0).mean():.3f}; "
           f"mean absolute change {df.price.diff().abs().mean() / tick:.2f} ticks.",
           ""]
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--indices", type=Path)
    ap.add_argument("--futures", type=Path)
    ap.add_argument("--out", type=Path, default=Path("results"))
    a = ap.parse_args()
    text = ["# Real-data statistics (Vietnam)\n",
            "Index bars: Kaggle dataset `keithvo/vnstockdata` (ODbL). Futures ticks: Kaggle dataset `khimduong/vn30-market-making` "
            "(license not stated; provenance of the ticks not documented). Neither contains account identifiers or order-level "
            "events. Raw files are not stored in this repository.\n"]
    if a.indices:
        text += index_section(a.indices)
    if a.futures:
        text += futures_section(a.futures)
    a.out.mkdir(exist_ok=True)
    (a.out / "real_data_stats.md").write_text("\n".join(text))
    print("\n".join(text))
