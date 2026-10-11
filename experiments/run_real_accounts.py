"""The coincidence test on real account-level order flow (Hyperliquid, public data, no labels).

Two public data sets with an account identifier on every record:
  * order submissions: Zenodo 18184441 ("An Open Book", Albers, Cucuringu, Howison, Shestopaloff; CC BY 4.0), SOL perpetual,
    first member of sol_orders_202512 (about 24 minutes of 1 December 2025); one record per order id, side = isAsk;
  * fills: a Hugging Face table of Hyperliquid fills (address, side, ms timestamps), one 91-minute slice (5 June 2026), perpetual
    coins HYPE, BTC, ETH; side = buy or sell of the account.
Both are pseudonymous addresses: one operator can control several. There are no manipulation labels.

R1 (calibration on real flow): share of accounts with p <= 0.01 and <= 0.05 per window, by activity tier and by whether the account
   trades both sides, for the unsigned and the signed statistic. Under exact validity the share would be at most the level; real bots
   that act on the same signal violate the exchangeability condition, so the excess measures real coordination (or its absence).
R2 (planted ring in real flow): a ring of K accounts picked among real active accounts adds, in each window, `n_push` common
   push bins at which every member submits `q` buy orders (jittered by +-j bins); catch@B = a member is among the B top-ranked accounts.
   Vary N by dropping real accounts at random (a smaller market), and K, q.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.coordination import coincidence_scan

L4_DT = np.dtype([('ts', '<u8'), ('userId', '<u4'), ('isBuilder', '?'), ('statusId', '<u1'), ('isAsk', '?'), ('limitPx', '<u4'), ('sz', '<u4'),
                  ('oid', '<u8'), ('timestampDiff', '<u4'), ('triggerCondition', '<i4'), ('triggered', '?'), ('isTrigger', '?'),
                  ('hasChildren', '?'), ('isPositionTpsl', '?'), ('reduceOnly', '?'), ('orderTypeId', '<u1'), ('tifId', '<u1'),
                  ('triggerPx', '<u4'), ('origSz', '<u4')])


def load_orders(path: Path) -> pd.DataFrame:
    a = np.fromfile(path, dtype=L4_DT)
    d = pd.DataFrame({"t": a["ts"].astype("int64") / 1e9, "user": a["userId"], "side": np.where(a["isAsk"], -1, 1), "oid": a["oid"]})
    d = d.drop_duplicates("oid")                      # one record per submitted order
    d["t"] -= d.t.min()
    return d[["t", "user", "side"]]


def load_fills(path: Path, coin: str) -> pd.DataFrame:
    f = pd.read_parquet(path, columns=["coin", "timestamp", "side", "address", "direction"])
    f = f[(f.coin == coin) & ~f.direction.astype(str).str.contains("Dust|Liquidat", regex=True)]
    ts = pd.to_datetime(f.timestamp)
    t = (ts - ts.min()).dt.total_seconds()
    d = pd.DataFrame({"t": t, "user": f.address.astype("category").cat.codes, "side": np.where(f.side == "buy", 1, -1)})
    return d


def windows(d: pd.DataFrame, bin_len: float, T: int):
    """Yield flow tensors [2, n, T] (buys, sells) of accounts active in each window of T bins."""
    w = T * bin_len
    n_win = int(d.t.max() // w)
    for i in range(n_win):
        g = d[(d.t >= i * w) & (d.t < (i + 1) * w)]
        users, inv = np.unique(g.user.to_numpy(), return_inverse=True)
        b = ((g.t.to_numpy() - i * w) // bin_len).astype(int).clip(0, T - 1)
        F = np.zeros((2, len(users), T))
        np.add.at(F, ((g.side.to_numpy() < 0).astype(int), inv, b), 1.0)
        yield F


def calibration(name, d, bin_len, T):
    rows = []
    for wi, F in enumerate(windows(d, bin_len, T)):
        n = F.shape[1]
        tot = F.sum(axis=(0, 2))
        both = np.minimum(F[0].sum(axis=1), F[1].sum(axis=1))
        res = {}
        for sg in (False, True):
            z, p = coincidence_scan(F, signed=sg)
            res["signed" if sg else "unsigned"] = (z, p)
        for i in range(n):
            if tot[i] >= 3:
                rows.append({"data": name, "window": wi, "n_active": n, "events": tot[i], "two_sided": both[i] >= 3,
                             "p_unsigned": res["unsigned"][1][i], "p_signed": res["signed"][1][i],
                             "z_unsigned": res["unsigned"][0][i], "z_signed": res["signed"][0][i]})
    return pd.DataFrame(rows)


def plant(F, rng, K, q, n_push, jitter, N_keep=None, pool="all"):
    """Return (flow with ring planted, member indices) after optionally keeping only N_keep accounts."""
    n = F.shape[1]
    tot = F.sum(axis=(0, 2))
    elig = np.flatnonzero((tot >= 3) & (tot < 16) if pool == "low" else tot >= 3)
    if len(elig) < K + 2:
        return None, None
    members = rng.choice(elig, size=K, replace=False)
    keep = np.arange(n)
    if N_keep is not None and N_keep < n:
        others = np.setdiff1d(np.arange(n), members)
        keep = np.sort(np.concatenate([members, rng.choice(others, size=max(N_keep - K, 0), replace=False)]))
    G = F[:, keep, :].copy()
    pos = {a: i for i, a in enumerate(keep)}
    T = G.shape[2]
    for _ in range(n_push):
        b0 = int(rng.integers(0, T))
        for m in members:
            b = (b0 + int(rng.integers(-jitter, jitter + 1))) % T
            G[0, pos[m], b] += q
    return G, np.array([pos[m] for m in members])


TIER_EDGES = [3, 6, 16, 51, 1e9]


def tier_score(z, tot):
    """Percentile of z among accounts of similar activity (tiers by submissions in the window), ties broken by z."""
    score = np.full(len(z), -np.inf)
    tier = np.digitize(tot, TIER_EDGES) - 1
    for t in range(len(TIER_EDGES) - 1):
        idx = np.flatnonzero((tier == t) & (tot >= 3))
        if len(idx):
            r = np.argsort(np.argsort(z[idx])) + 1
            score[idx] = r / len(idx) + 1e-9 * z[idx]
    return score


def catch_stats(F_list, rng, K, q, n_push, jitter, reps, N_keep=None, Bs=(1, 5, 10), pool="all"):
    modes = [("unsigned", "global"), ("signed", "global"), ("signed", "tier")]
    out = {f"{sg} {rk}@{B}": [] for sg, rk in modes for B in Bs}
    flagged = {"unsigned": [], "signed": []}
    for F in F_list:
        for _ in range(reps):
            G, mem = plant(F, rng, K, q, n_push, jitter, N_keep, pool)
            if G is None:
                continue
            tot = G.sum(axis=(0, 2))
            zs = {}
            for sg in ("unsigned", "signed"):
                z, p = coincidence_scan(G, signed=(sg == "signed"))
                zs[sg] = z
                flagged[sg].append(float((p[mem] <= 0.01).mean()))
            for sg, rk in modes:
                sc = zs[sg] if rk == "global" else tier_score(zs[sg], tot)
                order = np.argsort(-sc)
                for B in Bs:
                    out[f"{sg} {rk}@{B}"].append(bool(np.isin(order[:B], mem).any()))
    res = {k: float(np.mean(v)) for k, v in out.items() if v}
    res.update({f"member flagged p<=0.01 ({k})": float(np.mean(v)) for k, v in flagged.items() if v})
    res["n trials"] = len(out["signed global@5"])
    return res


def planted2(a):
    """Planted ring among low-activity real accounts, with a no-planting control (q = 0) and stronger pushes."""
    rng = np.random.default_rng(a.seed + 1)
    d = load_orders(Path(a.orders))
    F_list = list(windows(d, 0.5, a.T))
    n_med = int(np.median([f.shape[1] for f in F_list]))
    rows = []
    def run(sweep, N_keep, K, q, n_push):
        r = catch_stats(F_list, rng, K, q, n_push, a.jitter, a.reps, N_keep, pool="low")
        rows.append({"sweep": sweep, "N": N_keep or n_med, "K": K, "q": q, "n_push": n_push, **r})
        print(sweep, N_keep, K, q, n_push, {k: round(v, 3) for k, v in r.items() if "signed global@5" in k}, flush=True)
    for q in (0, 3, 10, 30, 100, 300):
        run("orders per push", None, a.K, q, a.n_push)
    for N_keep in (100, 200, 400, None):
        run("accounts", N_keep, a.K, 100, a.n_push)
    for K in (4, 8, 16, 32):
        run("ring size", None, K, 100, a.n_push)
    for n_push in (3, 10, 30):
        run("pushes per window", None, a.K, 100, n_push)
    pd.DataFrame(rows).to_csv(Path(a.out) / "real_accounts_planted2.csv", index=False)


def main(a):
    if a.stage == "planted2":
        return planted2(a)
    rng = np.random.default_rng(a.seed)
    datasets = []
    if a.orders:
        datasets.append(("orders SOL (L4)", load_orders(Path(a.orders)), 0.5))
    if a.fills:
        for coin in a.coins:
            datasets.append((f"fills {coin}", load_fills(Path(a.fills), coin), 1.0))
    cal, plant_rows = [], []
    for name, d, bl in datasets:
        c = calibration(name, d, bl, a.T)
        cal.append(c)
        F_list = list(windows(d, bl, a.T))
        print(name, "windows", len(F_list), "accounts per window", [f.shape[1] for f in F_list][:12], flush=True)
        n_med = int(np.median([f.shape[1] for f in F_list]))
        if name.startswith("orders"):
            for pool in ("all", "low"):
                for N_keep in [100, 200, 400, None]:
                    r = catch_stats(F_list, rng, a.K, a.q, a.n_push, a.jitter, a.reps, N_keep, pool=pool)
                    plant_rows.append({"data": name, "members": pool, "sweep": "accounts", "N": N_keep or n_med, "K": a.K, "q": a.q, **r})
                for K in (4, 8, 16, 32):
                    r = catch_stats(F_list, rng, K, a.q, a.n_push, a.jitter, a.reps, None, pool=pool)
                    plant_rows.append({"data": name, "members": pool, "sweep": "ring size", "N": n_med, "K": K, "q": a.q, **r})
                for q in (1, 2, 5):
                    r = catch_stats(F_list, rng, a.K, q, a.n_push, a.jitter, a.reps, None, pool=pool)
                    plant_rows.append({"data": name, "members": pool, "sweep": "orders per push", "N": n_med, "K": a.K, "q": q, **r})
        print(name, "planted done", flush=True)
    cal = pd.concat(cal, ignore_index=True)
    cal.to_csv(Path(a.out) / "real_accounts_calibration.csv.gz", index=False)
    pl = pd.DataFrame(plant_rows)
    pl.to_csv(Path(a.out) / "real_accounts_planted.csv", index=False)
    summ = []
    for name, g in cal.groupby("data"):
        tiers = pd.cut(g.events, [2, 9, 99, 1e9], labels=["3-9", "10-99", ">=100"])
        for key, sub in list(g.groupby(tiers, observed=True)) + [("all", g)] + [("two-sided", g[g.two_sided])]:
            summ.append({"data": name, "accounts": key, "n account-windows": len(sub),
                         "unsigned p<=0.01": (sub.p_unsigned <= 0.01).mean(), "signed p<=0.01": (sub.p_signed <= 0.01).mean(),
                         "unsigned p<=0.05": (sub.p_unsigned <= 0.05).mean(), "signed p<=0.05": (sub.p_signed <= 0.05).mean()})
    summ = pd.DataFrame(summ)
    summ.to_csv(Path(a.out) / "real_accounts_summary.csv", index=False)
    text = ["# The coincidence test on real account-level order flow\n",
            "Data: Hyperliquid (see the module docstring). Accounts with at least 3 submissions in a window of T = %d bins are tested; under exact validity "
            "the share with p <= level would be at most the level.\n" % a.T,
            "## R1: share of accounts flagged\n", summ.round(4).to_markdown(index=False),
            "\n## R2: planted ring in real flow\n", pl.round(3).to_markdown(index=False), ""]
    (Path(a.out) / "real_accounts.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    import os
    S = str(Path(os.environ.get("MARKETSIM_DATA", "external_data")) / "acct_data")
    ap.add_argument("--orders", default=f"{S}/zenodo_hl_l4_sample/first_member.bin")
    ap.add_argument("--fills", default=f"{S}/hl_fills_raw_sample/rg0.parquet")
    ap.add_argument("--coins", nargs="+", default=["HYPE", "BTC", "ETH"])
    ap.add_argument("--T", type=int, default=300)
    ap.add_argument("--K", type=int, default=12)
    ap.add_argument("--q", type=int, default=3)
    ap.add_argument("--n-push", type=int, default=10)
    ap.add_argument("--jitter", type=int, default=1)
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--stage", default="main")
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
