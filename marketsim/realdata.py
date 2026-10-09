"""Stock-level anomaly scores from public daily price and volume data (no account information).

Everything is computed for every stock and every date over a trailing window of W trading days, so a score for
(stock, date) uses only data up to that date. Scores are ranked against all other stocks on the same date, which removes
market-wide regimes. No labels are used.

Features (all relative to the stock's own history and to the market on the same days):
  up, down     market-adjusted cumulative return over the window, in units of the stock's own volatility
  surge        log of mean window volume over the stock's median volume in the preceding 120 days
  roundtrip    smaller of the run-up to the window high and the retracement from it, in own-volatility units
  tilt         absolute mean position of the close inside the day's range minus one half (closing-price pushing)
  limits       number of days with a move of at least 6.5% (near the HOSE daily band)
  range        mean daily range over its own preceding median
The combined score is the Fisher statistic -sum(log(1 - percentile)) over the cross-sectional percentiles of the features.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

FEATURES = ["up", "down", "surge", "roundtrip", "tilt", "limits", "range"]


def load_panel(folder: Path, min_days: int = 400) -> dict[str, pd.DataFrame]:
    """Wide tables date x ticker for open, high, low, close, volume from per-ticker parquet files (1D folder)."""
    frames = []
    for f in sorted(Path(folder).glob("*.parquet")):
        df = pd.read_parquet(f, columns=["time", "close", "open", "high", "low", "volume", "symbol"])
        if len(df) >= min_days:
            frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df["time"] = pd.to_datetime(df.time)
    df = df.drop_duplicates(["time", "symbol"])
    return {c: df.pivot(index="time", columns="symbol", values=c).sort_index() for c in
            ["open", "high", "low", "close", "volume"]}


def _roll_sum(x: np.ndarray, w: int) -> np.ndarray:
    c = np.nancumsum(np.nan_to_num(x), axis=0)
    out = np.full_like(c, np.nan)
    out[w:] = c[w:] - c[:-w]
    out[w - 1] = c[w - 1]
    return out


def _roll_apply(x: pd.DataFrame, w: int, fn: str, shift: int = 0, minp: int | None = None) -> np.ndarray:
    r = x.rolling(w, min_periods=minp or w // 2)
    out = getattr(r, fn)()
    return out.shift(shift).to_numpy()


def compute_features(panel: dict[str, pd.DataFrame], window: int = 20) -> dict[str, np.ndarray]:
    close, high, low, vol = panel["close"], panel["high"], panel["low"], panel["volume"]
    ret = np.log(close).diff()
    ret = ret.where(np.isfinite(ret))
    active = (vol > 0) & close.notna()
    mkt = ret.where(active).median(axis=1)
    ex = ret.sub(mkt, axis=0)
    sig = ex.rolling(250, min_periods=120).std().shift(window)           # own volatility before the window
    cum = ex.rolling(window, min_periods=window // 2).sum()
    scale = sig * np.sqrt(window)
    z = cum / scale
    up, down = z.clip(lower=0), (-z).clip(lower=0)

    mean_vol = vol.rolling(window, min_periods=window // 2).mean()
    base_vol = vol.rolling(120, min_periods=60).median().shift(window)
    surge = np.log((mean_vol + 1) / (base_vol + 1))

    lc = np.log(close)
    wmax = lc.rolling(window, min_periods=window // 2).max()
    wmin = lc.rolling(window, min_periods=window // 2).min()
    first = lc.shift(window - 1)
    runup = (wmax - first) / scale
    retrace = (wmax - lc) / scale
    roundtrip = np.minimum(runup.clip(lower=0), retrace.clip(lower=0))

    rng = (high - low)
    pos = ((close - low) / rng).where(rng > 0)
    tilt = (pos.rolling(window, min_periods=window // 2).mean() - 0.5).abs()

    limits = (ret.abs() >= 0.065).astype(float).where(ret.notna()).rolling(window, min_periods=window // 2).sum()

    drange = (rng / close)
    range_ratio = drange.rolling(window, min_periods=window // 2).mean() / drange.rolling(120, min_periods=60).median().shift(window)

    feats = {"up": up, "down": down, "surge": surge, "roundtrip": roundtrip, "tilt": tilt, "limits": limits,
             "range": range_ratio}
    liquid = (vol.rolling(window, min_periods=window // 2).mean() > 0) & sig.notna()
    return {k: v.where(liquid & np.isfinite(v)).to_numpy() for k, v in feats.items()}


def cross_percentiles(x: np.ndarray) -> np.ndarray:
    """Percentile of each stock among stocks on the same date (NaN stays NaN)."""
    return pd.DataFrame(x).rank(axis=1, pct=True).to_numpy()


def scores(feats: dict[str, np.ndarray], use: list[str] | None = None) -> dict[str, np.ndarray]:
    """Per-feature cross-sectional percentiles and the combined Fisher score.

    A stock-date is scored if its return features exist; a feature that cannot be computed (for example the close
    position on days with no price range) counts as no evidence (p = 1).
    """
    use = use or FEATURES
    pct = {k: cross_percentiles(feats[k]) for k in use}
    n = np.isfinite(feats["up"]).sum(axis=1, keepdims=True).astype(float)
    fisher = np.zeros_like(pct[use[0]])
    for k in use:
        p = np.clip(1 - pct[k], 1.0 / np.maximum(n, 1), 1.0)
        fisher += np.where(np.isfinite(pct[k]), -np.log(p), 0.0)
    fisher[~np.isfinite(feats["up"])] = np.nan
    out = dict(pct)
    out["fisher"] = fisher
    return out
