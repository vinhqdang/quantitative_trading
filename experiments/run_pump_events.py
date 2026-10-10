"""Event study of Telegram-organised pump-and-dump events on tick data (no account identifiers).

Each file holds the trades of one coin from about 24 hours before the pump time (given in the file name) to shortly after it.
Questions: is there accumulation before the pump (abnormal volume and buy imbalance in the hours before), and how far ahead of the
pump can a label-free calibrated score raise an alarm?

Score at minute t: the larger of the standardised volume and of the standardised buy imbalance of the last 10 minutes, standardised
against the same coin's own first 20 hours (a background that precedes the pump by at least four hours). The alarm threshold is
set so that the background of all events raises false alarms at a given rate per coin-hour.
"""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


def load_event(zf: zipfile.ZipFile, name: str):
    m = re.search(r"_(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2})\.(\d{1,2})\.csv$", name)
    if not m:
        return None
    y, mo, d, h, mi = map(int, m.groups())
    t0 = pd.Timestamp(year=y, month=mo, day=d, hour=h, minute=mi, tz="UTC")
    df = pd.read_csv(zf.open(name), usecols=["timestamp", "side", "price", "amount", "btc_volume"])
    df["t"] = pd.to_datetime(df.timestamp, unit="ms", utc=True)
    return t0, df


def minute_series(df: pd.DataFrame, t0: pd.Timestamp, pre_min: int = 24 * 60, post_min: int = 30):
    idx = pd.date_range(t0 - pd.Timedelta(minutes=pre_min), t0 + pd.Timedelta(minutes=post_min), freq="1min", tz="UTC")
    d = df.set_index("t")
    sgn = np.where(d.side == "buy", 1.0, -1.0)
    vol = pd.Series(d.btc_volume.to_numpy(), index=d.index).resample("1min").sum().reindex(idx, fill_value=0.0)
    net = pd.Series(d.btc_volume.to_numpy() * sgn, index=d.index).resample("1min").sum().reindex(idx, fill_value=0.0)
    px = d.price.resample("1min").last().reindex(idx).ffill().bfill()
    return pd.DataFrame({"vol": vol, "net": net, "px": px})


def scores(ms: pd.DataFrame, t0: pd.Timestamp, win: int = 10, bg_hours: int = 20):
    """Standardised volume and imbalance of rolling `win`-minute windows against the first bg_hours of the file."""
    v = ms.vol.rolling(win).sum()
    nrm = (ms.net.rolling(win).sum() / (v + 1e-12)).where(v > 0)
    bg_end = ms.index[0] + pd.Timedelta(hours=bg_hours)
    bgv, bgn = np.log1p(v[:bg_end] * 1e4), nrm[:bg_end]
    zv = (np.log1p(v * 1e4) - bgv.mean()) / (bgv.std() + 1e-9)
    zn = (nrm - bgn.mean()) / (bgn.std() + 1e-9)
    return zv, zn.fillna(0.0), bg_end


def main(zips, out, bg_hours=20):
    curves, rows = [], []
    for zpath in zips:
        with zipfile.ZipFile(zpath) as zf:
            for name in zf.namelist():
                ev = load_event(zf, name) if name.endswith(".csv") else None
                if ev is None:
                    continue
                t0, df = ev
                if len(df) < 300:
                    continue
                ms = minute_series(df, t0)
                zv, zn, bg_end = scores(ms, t0, bg_hours=bg_hours)
                if ms.vol[: bg_end].sum() <= 0:
                    continue
                s = np.maximum(zv, zn)
                rel = ((s.index - t0) / pd.Timedelta(minutes=1)).astype(int)
                curves.append(pd.DataFrame({"rel": rel, "zv": zv.to_numpy(), "zn": zn.to_numpy(), "s": s.to_numpy(),
                                            "ret": np.log(ms.px / ms.px.shift(10)).to_numpy(), "event": name}))
                rows.append({"event": name, "t0": t0, "n_trades": len(df)})
    c = pd.concat(curves, ignore_index=True)
    n_events = c.event.nunique()
    c = c.replace([np.inf, -np.inf], np.nan).dropna(subset=["s"])
    bg = c[c.rel < -(24 * 60 - bg_hours * 60) * -1 - 0] if False else c[(c.rel >= -24 * 60) & (c.rel < -4 * 60)]  # >= 4 h before the pump
    bg_in = c[(c.rel >= -24 * 60) & (c.rel < -4 * 60)]
    text = [f"# Telegram pump events (tick data)\n", f"{n_events} events from {len(zips)} archive(s). Background: minutes between 24 h and 4 h before the pump.\n"]
    prof = []
    for lo, hi, lab in [(-240, -180, "4h to 3h before"), (-180, -120, "3h to 2h before"), (-120, -60, "2h to 1h before"),
                        (-60, -30, "60 to 30 min before"), (-30, -10, "30 to 10 min before"), (-10, 0, "last 10 min before"),
                        (0, 10, "first 10 min after")]:
        sub = c[(c.rel >= lo) & (c.rel < hi)]
        g = sub.groupby("event")[["zv", "zn", "ret"]].mean()
        rng = np.random.default_rng(0)
        bs = [g.iloc[rng.integers(0, len(g), len(g))].mean() for _ in range(300)]
        bs = pd.DataFrame(bs)
        prof.append({"period": lab, "events": len(g),
                     "mean std. volume": f"{g.zv.mean():.2f} [{bs.zv.quantile(.025):.2f}, {bs.zv.quantile(.975):.2f}]",
                     "mean std. buy imbalance": f"{g.zn.mean():.2f} [{bs.zn.quantile(.025):.2f}, {bs.zn.quantile(.975):.2f}]",
                     "mean 10-min log return": f"{g.ret.mean():.4f}"})
    text += ["## Profile around the pump (mean over events, 95% bootstrap interval over events)\n", pd.DataFrame(prof).to_markdown(index=False), ""]
    # numeric profile for figures: per minute relative to the pump, mean over events with bootstrap interval
    rows = []
    rng2 = np.random.default_rng(1)
    cc = c[(c.rel >= -240) & (c.rel <= 30)]
    piv_v = cc.pivot_table(index="event", columns="rel", values="zv")
    piv_n = cc.pivot_table(index="event", columns="rel", values="zn")
    for name, piv in (("volume", piv_v), ("buy imbalance", piv_n)):
        arr = piv.to_numpy()
        for j, rel in enumerate(piv.columns):
            col = arr[:, j]
            col = col[np.isfinite(col)]
            bs = [col[rng2.integers(0, len(col), len(col))].mean() for _ in range(100)]
            rows.append({"series": name, "minute": int(rel), "mean": col.mean(), "lo": np.percentile(bs, 2.5), "hi": np.percentile(bs, 97.5)})
    Path(out).mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(Path(out) / "pump_profile.csv", index=False)
    # detection before the pump at calibrated false-alarm rates (alarm if score exceeds a threshold)
    for per_hour in (0.05, 0.1, 0.25):
        bgs = bg_in.groupby("event").s.apply(lambda s: s.to_numpy())
        thr = np.quantile(np.concatenate(bgs.to_list()), 1 - per_hour / 60)  # alarms per coin-hour of background minutes
        det = []
        for ev, g in c.groupby("event"):
            pre = g[(g.rel >= -60) & (g.rel < 0)]
            first = pre[pre.s >= thr].rel.min() if (pre.s >= thr).any() else np.nan
            det.append(first)
        det = pd.Series(det)
        text += [f"Alarm rate in the background set to {per_hour} per coin-hour (threshold {thr:.2f}): alarm in the last hour before the "
                 f"pump for {det.notna().mean():.1%} of events; median lead {(-det.dropna()).median():.0f} min when it fires.\n"]
    Path(out).mkdir(exist_ok=True)
    (Path(out) / "pump_events.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--zips", nargs="+", required=True)
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    main(a.zips, a.out)
