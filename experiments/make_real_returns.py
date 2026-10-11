"""Pooled standardised daily returns of HOSE stocks since 2022 (for the calibration figure)."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.realdata import load_panel


def main(a):
    P = load_panel(Path(a.folder), min_days=100)
    meta = pd.read_csv(a.meta)
    hose = set(meta[meta.market.str.upper() == "HOSE"].ticker)
    c = P["close"]
    ret = np.log(c).diff().loc["2022-01-01":"2025-09-30"]
    active = (P["volume"].loc[ret.index] > 0)
    out = []
    for t in ret.columns:
        if t in hose:
            r = ret[t][active[t]].dropna()
            r = r[np.isfinite(r)]
            if len(r) > 400 and r.std() > 0:
                out.append(((r - r.mean()) / r.std()).rename("ret").to_frame().assign(ticker=t))
    d = pd.concat(out)
    acf = {l: np.nanmean([x.ret.autocorr(l) for x in out]) for l in range(1, 6)}
    tab = pd.DataFrame({"lag": list(acf), "mean autocorrelation of daily returns, HOSE stocks": list(acf.values())})
    if a.index:
        idx = pd.read_csv(a.index, usecols=["time", "close"])
        idx["t"] = pd.to_datetime(idx.time, unit="s")
        r = np.log(idx.set_index("t").sort_index().close["2023-01-01":]).diff().dropna()
        tab["autocorrelation of daily returns, VN30 index"] = [r.autocorr(l) for l in range(1, 6)]
    tab.to_csv(Path(a.out) / "calib_real_acf.csv", index=False)
    print(acf)
    d.sample(n=min(len(d), 40000), random_state=0).to_csv(Path(a.out) / "calib_real_stock_returns.csv", index=False)
    print(len(out), "stocks;", len(d), "returns")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--index", default=None, help="VN30 daily CSV (time, close)")
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
