"""Do public price and volume data single out stocks in documented manipulation periods?

Protocol (fixed before the cases were scored):
  * universe: every stock in the daily panel; scores for (stock, date) use only data up to that date
  * label-free detectors rank stocks against each other on every date (marketsim.realdata)
  * a case is a stock with a manipulation period from an enforcement decision (data/cases.csv)
  * case score: the highest cross-sectional percentile reached on any trading date inside the period
  * null: the same statistic for randomly drawn stocks over the same dates; superiority = probability that the case stock
    beats a random stock (0.5 is chance)
  * budgeted view: share of cases in which the stock is among the B highest-scoring stocks of its date on at least one
    date of the period (B inspections per date out of about N active stocks)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from marketsim.realdata import FEATURES, compute_features, cross_percentiles, load_panel, scores


def iforest_scores(feats: dict[str, np.ndarray], seed: int = 0) -> np.ndarray:
    X = np.stack([np.nan_to_num(feats[k], nan=0.0) for k in FEATURES], axis=-1)
    ok = np.isfinite(feats["up"])
    flat = X[ok]
    mu, sd = np.nanmean(flat, axis=0), np.nanstd(flat, axis=0) + 1e-9
    rng = np.random.default_rng(seed)
    sub = flat[rng.choice(len(flat), size=min(200_000, len(flat)), replace=False)]
    iso = IsolationForest(n_estimators=100, random_state=seed, n_jobs=2).fit((sub - mu) / sd)
    out = np.full(ok.shape, np.nan)
    out[ok] = -iso.score_samples((flat - mu) / sd)
    return out


def peak_percentile(pct: np.ndarray, rows: np.ndarray, col: int) -> float:
    v = pct[rows, col]
    return float(np.nanmax(v)) if np.isfinite(v).any() else np.nan


def evaluate(cases: pd.DataFrame, panel, det: dict[str, np.ndarray], n_null: int, B: list[int], seed: int = 0):
    dates = panel["close"].index
    cols = {c: i for i, c in enumerate(panel["close"].columns)}
    rng = np.random.default_rng(seed)
    pct = {name: cross_percentiles(s) for name, s in det.items()}
    res = []
    for _, c in cases.iterrows():
        if c.ticker not in cols:
            continue
        rows = np.flatnonzero((dates >= pd.Timestamp(c.start)) & (dates <= pd.Timestamp(c.end)))
        if len(rows) < 5:
            continue
        j = cols[c.ticker]
        for name, P in pct.items():
            peak = peak_percentile(P, rows, j)
            if not np.isfinite(peak):
                continue
            valid = np.flatnonzero(np.isfinite(P[rows]).mean(axis=0) > 0.5)
            pool = valid[valid != j]
            draw = rng.choice(pool, size=min(n_null, len(pool)), replace=False)
            null = np.array([peak_percentile(P, rows, k) for k in draw])
            null = null[np.isfinite(null)]
            # time placebo: the same stock over periods of the same length that do not overlap the case period
            L = len(rows)
            valid_start = [s0 for s0 in range(0, P.shape[0] - L)
                           if (s0 + L < rows.min() - L or s0 > rows.max() + L) and np.isfinite(P[s0:s0 + L, j]).mean() > 0.5]
            tnull = np.array([peak_percentile(P, np.arange(s0, s0 + L), j) for s0 in
                              rng.choice(valid_start, size=min(n_null, len(valid_start)), replace=False)]) if len(valid_start) > 20 else np.array([])
            tnull = tnull[np.isfinite(tnull)]
            r = {"ticker": c.ticker, "detector": name, "days": len(rows), "peak percentile": peak,
                 "p vs random stocks": float((null >= peak).mean()),
                 "superiority": float((null < peak).mean() + 0.5 * (null == peak).mean()),
                 "p vs same stock, other dates": float((tnull >= peak).mean()) if len(tnull) else np.nan,
                 "superiority vs same stock": float((tnull < peak).mean() + 0.5 * (tnull == peak).mean()) if len(tnull) else np.nan}
            raw = det[name][rows]
            filled = np.nan_to_num(raw, nan=-1e9)
            srt = np.sort(filled, axis=1)
            for b in B:
                kth = srt[:, -b]
                r[f"top{b}"] = bool((filled[:, j] >= kth).any())
                r[f"chance top{b}"] = float((filled[:, draw] >= kth[:, None]).any(axis=0).mean())
            res.append(r)
    return pd.DataFrame(res)


def summarise(df: pd.DataFrame, B: list[int]) -> pd.DataFrame:
    g = df.groupby("detector")
    out = pd.DataFrame({
        "cases": g.size(),
        "median peak percentile": g["peak percentile"].median(),
        "share of cases >= 0.99": g["peak percentile"].apply(lambda s: (s >= 0.99).mean()),
        "mean superiority vs random stock": g.superiority.mean(),
        "share with p < 0.05": g["p vs random stocks"].apply(lambda s: (s < 0.05).mean()),
        "superiority vs same stock, other dates": g["superiority vs same stock"].mean(),
        "share with p < 0.05 vs same stock": g["p vs same stock, other dates"].apply(lambda s: (s < 0.05).mean()),
    })
    for b in B:
        out[f"in top {b} on some date"] = g[f"top{b}"].mean()
        out[f"chance (random stock) top {b}"] = g[f"chance top{b}"].mean()
    return out


def main(args):
    panel = load_panel(Path(args.folder))
    feats = compute_features(panel, window=args.window)
    sc = scores(feats)
    det = {"combined (Fisher)": sc["fisher"], "volume surge only": feats["surge"],
           "abnormal return only": np.fmax(np.nan_to_num(feats["up"]), np.nan_to_num(feats["down"])) + 0 * feats["up"],
           "round trip only": feats["roundtrip"], "isolation forest": iforest_scores(feats)}
    cases = pd.read_csv(args.cases)
    cases = cases[cases.include.astype(str).str.lower().isin(["yes", "true", "1"])]
    B = [10, 20, 50]
    n_active = int(np.nanmedian(np.isfinite(feats["up"]).sum(axis=1)[-500:]))
    res = evaluate(cases, panel, det, args.n_null, B)
    summ = summarise(res, B)
    covered = res.ticker.nunique()
    text = ["# Case validation on public daily data\n",
            f"{len(cases)} cases with a documented period were considered, {covered} stocks are in the price panel "
            f"(1D data, {panel['close'].shape[1]} stocks, {panel['close'].index.min().date()} to {panel['close'].index.max().date()}; "
            f"about {n_active} stocks have scores on a typical recent date). Window {args.window} trading days. "
            f"Random-stock null: {args.n_null} stocks per case. Chance level: 0.5 superiority, 5% of cases with p < 0.05, and for "
            "the top-B lists the share of random stocks that reach the list on some date of the same period (reported next to each detector).\n", summ.round(3).to_markdown(), "\n",
            "## By case (combined score)\n",
            res[res.detector == "combined (Fisher)"].drop(columns="detector").round(3).to_markdown(index=False), ""]
    Path(args.out).mkdir(exist_ok=True)
    res.to_csv(Path(args.out) / f"case_validation{args.tag}_cases.csv", index=False)
    (Path(args.out) / f"case_validation{args.tag}.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True, help="folder of per-ticker daily parquet files")
    ap.add_argument("--cases", default="data/cases.csv")
    ap.add_argument("--window", type=int, default=20)
    ap.add_argument("--n-null", type=int, default=300)
    ap.add_argument("--out", default="results")
    ap.add_argument("--tag", default="")
    main(ap.parse_args())
