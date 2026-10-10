"""How do the documented case stocks differ from the market, and do the daily price bands bind in their manipulation periods?

For each case: daily volatility and share of zero-return days in the year before the period and during it, the price change over the
period, the number of days within 0.5 percentage points of the ceiling of the exchange's daily band (HOSE 7%, HNX 10%, UPCoM 15%) and the
longest run of such days. Market reference: median stock since 2022.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.realdata import load_panel

BAND = {"HOSE": 0.07, "HNX": 0.10, "UPCOM": 0.15}


def main(args):
    P = load_panel(Path(args.folder), min_days=100)
    meta = pd.read_csv(args.meta)
    mk = dict(zip(meta.ticker, meta.market.str.upper()))
    c = P["close"]
    ret = np.log(c).diff()
    cases = pd.read_csv(args.cases)
    cases = cases[cases.include.astype(str).str.lower() == "yes"]
    rows = []
    for _, r in cases.iterrows():
        t = r.ticker
        if t not in c.columns:
            continue
        s, e = pd.Timestamp(r.start), pd.Timestamp(r.end)
        pre = ret.loc[s - pd.Timedelta(days=365):s - pd.Timedelta(days=1), t].dropna()
        inn = ret.loc[s:e, t].dropna()
        if len(pre) < 60 or len(inn) < 5:
            continue
        ex = mk.get(t, "unknown")
        b = BAND.get(ex, 0.07)
        flag = (inn >= b - 0.005)
        run = mx = 0
        for x in flag:
            run = run + 1 if x else 0
            mx = max(mx, run)
        cp = c[t].dropna()
        total = np.log(cp[:e].iloc[-1] / cp[:s].iloc[-1]) * 100
        rows.append({"ticker": t, "exchange": ex, "days": len(inn), "pre vol %": pre.std() * 100, "case vol %": inn.std() * 100,
                     "pre zero-return share": float((pre == 0).mean()), "price change %": total,
                     "ceiling days": int(flag.sum()), "longest ceiling run": mx})
    df = pd.DataFrame(rows)
    allv = ret.loc["2022-01-01":"2025-09-30"]
    hose = [x for x in c.columns if mk.get(x) == "HOSE"]
    ref = {"market median stock daily vol %": allv.std().median() * 100, "HOSE median stock daily vol %": allv[hose].std().median() * 100,
           "HOSE median zero-return share": (allv[hose] == 0).mean().median(),
           "cases median pre-period vol %": df["pre vol %"].median(), "cases median zero-return share": df["pre zero-return share"].median()}
    out = Path(args.out)
    df.to_csv(out / "case_stats.csv", index=False)
    text = ["# Case stocks against the market\n", df.round(2).to_markdown(index=False), "", "## Reference\n",
            pd.Series(ref).round(3).to_markdown(), ""]
    (out / "case_stats.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--cases", default="data/cases.csv")
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
