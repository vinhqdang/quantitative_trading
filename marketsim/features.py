"""Account-level surveillance features over fixed time windows.

Everything here uses only what a regulator sees in order-level data: account
id, order id, side, price, quantity, counterparty and the prevailing mid at the
time of each event. Ground-truth tags and agent kinds are used only to build
labels and for diagnostic breakdowns, never as inputs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .exchange import CANCEL, MKT, NEW, TRADE
from .sim import Episode

FEATURES = [
    "n_new", "n_cancel", "n_trade", "cancel_ratio", "otr", "cancel_qty_ratio",
    "qty_rel_mean", "qty_rel_max", "dist_mean", "life_med", "frac_cancel_fast", "fill_ratio",
    "imb_new", "imb_cancel", "imb_exec", "place_exec_disagree", "cancel_exec_disagree",
    "aggr_share", "top_cpty_share", "n_cpty", "net_over_vol", "vol_share",
    "impact5", "reversal25", "burst",
]


def window_features(ep: Episode, window: int = 300, min_events: int = 5) -> pd.DataFrame:
    cfg = ep.config
    ev = ep.events
    ev = ev[ev.t >= cfg.warmup].copy()
    ev["w"] = (ev.t - cfg.warmup) // window
    mids = ep.mids
    last = len(mids) - 1

    new = ev[ev.kind == NEW]
    mkt = ev[ev.kind == MKT]
    can = ev[ev.kind == CANCEL]
    trd = ev[ev.kind == TRADE]

    # lifetime of cancelled limit orders
    born = ev[ev.kind == NEW].set_index("oid").t
    can = can.assign(life=can.t.to_numpy() - born.reindex(can.oid).to_numpy())

    # market-level normalisers per window
    med_qty = new.groupby("w").qty.median().rename("med_qty")
    mkt_vol = trd.groupby("w").qty.sum().rename("mkt_vol") / 2  # each trade appears once per party

    keys = ["agent", "w"]
    out = pd.DataFrame(index=pd.MultiIndex.from_frame(ev[keys].drop_duplicates()))

    n = new.assign(dist=(new.price - new.mid).abs(), sq=new.side * new.qty,
                   rel=new.qty / new.w.map(med_qty))
    g = n.groupby(keys)
    out["n_new"] = g.size()
    out["new_qty"] = g.qty.sum()
    out["qty_rel_mean"] = g.rel.mean()
    out["qty_rel_max"] = g.rel.max()
    out["dist_mean"] = g.dist.mean()
    out["imb_new"] = g.sq.sum() / out.new_qty

    n_m = mkt.groupby(keys).size()
    out["n_mkt"] = n_m

    c = can.assign(sq=can.side * can.qty, fast=(can.life <= 5).astype(float))
    gc = c.groupby(keys)
    out["n_cancel"] = gc.size()
    out["cancel_qty"] = gc.qty.sum()
    out["life_med"] = gc.life.median()
    out["frac_cancel_fast"] = gc.fast.mean()
    out["imb_cancel"] = gc.sq.sum() / out.cancel_qty

    t_ = trd.copy()
    t_["sq"] = t_.side * t_.qty
    # impact of own trades: signed mid change over the next 5 steps, and the reversal over steps 5..25
    tt = np.minimum(t_.t.to_numpy(), last)
    t_["r5"] = t_.side * (mids[np.minimum(tt + 5, last)] - mids[tt])
    t_["r25"] = t_.side * (mids[np.minimum(tt + 25, last)] - mids[np.minimum(tt + 5, last)])
    t_["wq5"] = t_.r5 * t_.qty
    t_["wq25"] = t_.r25 * t_.qty
    gt = t_.groupby(keys)
    out["n_trade"] = gt.size()
    out["vol"] = gt.qty.sum()
    out["aggr_share"] = gt.apply(lambda d: (d.aggr * d.qty).sum() / d.qty.sum(), include_groups=False)
    out["imb_exec"] = gt.sq.sum() / out.vol
    out["net_over_vol"] = gt.sq.sum().abs() / out.vol
    cp = t_.groupby(keys + ["cpty"]).qty.sum()
    out["top_cpty_share"] = cp.groupby(keys).max() / out.vol
    out["n_cpty"] = cp.groupby(keys).size()
    out["impact5"] = gt.wq5.sum() / out.vol
    out["reversal25"] = gt.wq25.sum() / out.vol
    out["vol_share"] = out.vol / (out.index.get_level_values("w").map(mkt_vol).to_numpy())

    # burstiness of order entry: largest 10-step bin share of the account's orders
    ent = pd.concat([new, mkt])
    ent = ent.assign(bin=ent.t // 10)
    bins = ent.groupby(keys + ["bin"]).size()
    out["burst"] = bins.groupby(keys).max() / bins.groupby(keys).sum()

    out = out.fillna({"n_new": 0, "n_cancel": 0, "n_trade": 0, "n_mkt": 0, "new_qty": 0, "cancel_qty": 0, "vol": 0})
    total = out.n_new + out.n_mkt + out.n_cancel + out.n_trade
    out = out[total >= min_events]
    out["cancel_ratio"] = out.n_cancel / out.n_new.clip(lower=1)
    out["otr"] = (out.n_new + out.n_mkt) / (out.n_trade + 1)
    out["cancel_qty_ratio"] = out.cancel_qty / out.new_qty.clip(lower=1)
    out["fill_ratio"] = out.vol / (out.new_qty + out.n_mkt).clip(lower=1)
    out["place_exec_disagree"] = -out.imb_new.fillna(0) * out.imb_exec.fillna(0)
    out["cancel_exec_disagree"] = -out.imb_cancel.fillna(0) * out.imb_exec.fillna(0)
    out["life_med"] = out.life_med.fillna(1000.0)
    out["frac_cancel_fast"] = out.frac_cancel_fast.fillna(0.0)
    for col in FEATURES:
        out[col] = out[col].fillna(0.0)

    out = out.reset_index()
    out["window"] = out["w"]
    return out[["agent", "window"] + FEATURES]


def label_windows(ep: Episode, feats: pd.DataFrame, window: int = 300, min_tagged: int = 2) -> pd.DataFrame:
    """Attach ground truth: manipulation type if the account submitted >= min_tagged tagged orders in the window."""
    cfg = ep.config
    ev = ep.events
    sub = ev[(ev.t >= cfg.warmup) & (ev.kind.isin([NEW, MKT]))].merge(ep.gt_orders, on="oid")
    sub["window"] = (sub.t - cfg.warmup) // window
    sub["type"] = sub.tag.str.split("_").str[0].map({"spoof": "spoof", "pd": "pump", "wash": "wash", "ring": "ring"})
    cnt = sub.groupby(["agent", "window", "type"]).size().rename("n").reset_index()
    need = cnt.type.map({"ring": 1}).fillna(min_tagged)  # ring members act rarely each: one tagged order counts
    cnt = cnt[cnt.n >= need].sort_values("n").drop_duplicates(["agent", "window"], keep="last")
    df = feats.merge(cnt[["agent", "window", "type"]], on=["agent", "window"], how="left")
    df = df.merge(ep.agents.rename(columns={"aid": "agent"})[["agent", "kind"]], on="agent")
    df["type"] = df["type"].fillna("none")
    df["y"] = (df["type"] != "none").astype(int)
    return df
