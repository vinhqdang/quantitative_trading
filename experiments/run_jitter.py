"""Experiments for the block-jitter coincidence test (marketsim/jitter.py).

Stages
  fwer    iid null windows: family-wise error of the Bonferroni rule at alpha for the circular-shift test (p >= 1/T) and the block-jitter test.
  regime  honest accounts that all load on a common directional regime of segment length ell: share with p <= 0.01 for the circular test and for block
          sizes from 150 down to 10 (the jitter null conditions on the regime only when the regime is constant inside a block).
  kmin    Gaussian campaign model of Proposition 3: probability that a member of a ring of K accounts is rejected at family-wise level alpha, and the
          K at which it reaches one half, against N (compared with the closed form of the corollary).
  abm     rings in the agent-based market: rejection at family-wise level 5% and the rank-based catch@5, honest-window family-wise error.
  real    Hyperliquid order flow: share of accounts with p <= 0.01 under circular and jitter nulls (and a regime-stratified permutation null), and the number
          of Bonferroni rejections per window.
"""

from __future__ import annotations

import argparse
import os
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import multiprocessing as mp
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from marketsim.coordination import coincidence_scan, submission_flow_from_events
from marketsim.jitter import _circ_box, jitter_scan

T = 300
TOLS = (1, 5, 15)


def n_draws(m, alpha):
    return int(2 * np.ceil(m / alpha))


def reject_set(f, block, alpha, rng, active=None):
    m = int(f.any(axis=(0, 2)).sum()) if active is None else int(active.sum())
    B = n_draws(m, alpha)
    z, p, e, u = jitter_scan(f, TOLS, block, B, True, rng, active=active, reject_alpha=alpha)
    return z, p, (u == B) & (p <= alpha / max(m, 1))


# ---- fwer ----------------------------------------------------------------------------------------------------------------------------------
def stage_fwer(a):
    rng = np.random.default_rng(a.seed)
    rows = []
    for N in (60, 120, 300, 600):
        for kind in ("iid Gaussian", "Poisson counts"):
            fc = fj = 0
            for _ in range(a.reps):
                if kind == "iid Gaussian":
                    x = rng.normal(size=(N, T))
                else:
                    x = rng.poisson(0.3, size=(N, T)).astype(float) - rng.poisson(0.3, size=(N, T))
                f = np.stack([x, np.zeros_like(x)])
                _, pc = coincidence_scan(f, TOLS, signed=True)
                fc += int((pc <= a.alpha / N).any())
                _, _, rj = reject_set(f, a.block, a.alpha, rng)
                fj += int(rj.any())
            rows.append({"N": N, "flows": kind, "alpha": a.alpha, "min attainable p, circular (1/T)": 1 / T, "Bonferroni level alpha/N": a.alpha / N,
                         "family-wise error, circular": fc / a.reps, "family-wise error, block jitter": fj / a.reps, "windows": a.reps,
                         "surrogates B": n_draws(N, a.alpha)})
            print(rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(Path(a.out) / "jitter_fwer.csv", index=False)


# ---- regime --------------------------------------------------------------------------------------------------------------------------------
def regime_path(rng, ell):
    D = np.zeros(T)
    t = 0
    while t < T:
        L = max(1, int(rng.geometric(1 / ell)))
        D[t:t + L] = rng.choice([-1, 0, 1])
        t += L
    return D


def stage_regime(a):
    rng = np.random.default_rng(a.seed)
    N = 100
    rows = []
    for ell in (15, 40, 100, 300):
        res = {}
        for _ in range(a.reps):
            D = regime_path(rng, ell)
            beta = rng.uniform(0.5, 1.5, size=(N, 1))
            x = beta * D[None, :] + rng.normal(size=(N, T))
            f = np.stack([x, np.zeros_like(x)])
            _, p = coincidence_scan(f, TOLS, signed=True)
            res.setdefault("circular (block = 300)", []).append(p)
            for blk in (150, 100, 50, 25, 10):
                _, p, _, _ = jitter_scan(f, TOLS, blk, 399, True, rng)
                res.setdefault(f"jitter, block {blk}", []).append(p)
        for k, v in res.items():
            v = np.concatenate(v)
            rows.append({"regime segment length": ell, "null": k, "share with p<=0.01": float((v <= 0.01).mean()), "share with p<=0.05": float((v <= 0.05).mean())})
        print(ell, {r["null"]: round(r["share with p<=0.01"], 3) for r in rows[-6:]}, flush=True)
    pd.DataFrame(rows).to_csv(Path(a.out) / "jitter_regime.csv", index=False)


# ---- kmin ----------------------------------------------------------------------------------------------------------------------------------
def make_flows(rng, N, K, eta, pi=0.2):
    x = rng.normal(size=(N, T))
    b = np.sqrt(eta / (pi * (1 - pi)))
    s = (rng.random(T) < pi).astype(float)
    x[:K] += b * s
    return x


def rho_model(N, K, eta):
    return (K - 1) * eta / np.sqrt((1 + eta) * ((N - 1) + (K - 1) ** 2 * eta))


def _kmin_task(args):
    N, K, eta, seed, alpha, block = args
    rng = np.random.default_rng(seed)
    x = make_flows(rng, N, K, eta)
    f = np.stack([x, np.zeros_like(x)])
    z, p, rj = reject_set(f, block, alpha, rng)
    order = np.argsort(-z)
    return {"N": N, "K": K, "eta": eta, "any member rejected": bool(rj[:K].any()), "non-member rejected": bool(rj[K:].any()),
            "catch@5": bool((order[:5] < K).any()), "members rejected": int(rj[:K].sum())}


def stage_kmin(a):
    jobs = []
    for eta in (0.1, 0.3):
        for N in (60, 120, 240, 480, 960):
            for K in (2, 4, 8, 16, 32, 64, 128):
                if K < N / 3:
                    jobs += [(N, K, eta, a.seed * 10_000_000 + 1000 * i + len(jobs), a.alpha, a.block) for i in range(a.reps)]
    with ProcessPoolExecutor(a.workers, mp_context=mp.get_context("spawn")) as pool:
        res = list(pool.map(_kmin_task, jobs, chunksize=8))
    df = pd.DataFrame(res)
    g = df.groupby(["eta", "N", "K"]).agg(power_fwer=("any member rejected", "mean"), false_rejections=("non-member rejected", "mean"),
                                          catch5=("catch@5", "mean"), members_rejected=("members rejected", "mean"), windows=("K", "size")).reset_index()
    g.to_csv(Path(a.out) / "jitter_kmin.csv", index=False)
    print(g.round(3).to_string())


# ---- abm -----------------------------------------------------------------------------------------------------------------------------------
HONEST = dict(n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0))
KEYS = ("n_noise", "n_fund", "mm_activity", "fund_sigma", "mm_imb_sens", "mom_activity")


def _abm_task(args):
    from marketsim.features import label_windows
    from marketsim.sim import SimConfig, run_episode
    from marketsim.vietnam import vn_config
    name, params, seed, ring, alpha, block = args
    cfg = SimConfig() if params is None else vn_config(**params)
    cfg = replace(cfg, **HONEST, n_ring=(1, 1) if ring else (0, 0))
    ep = run_episode(seed, cfg)
    F = submission_flow_from_events(ep.events, int(ep.agents.aid.max()) + 1, cfg.steps, cfg.warmup, 300)
    rng = np.random.default_rng(seed)
    rows = []
    for w in range(F.shape[0]):
        act = F[w].sum(axis=(0, 2)) > 0
        z, p, rj = reject_set(F[w], block, alpha, rng, active=act)
        zc, pc = coincidence_scan(F[w], TOLS, signed=True)
        rows.append(pd.DataFrame({"agent": np.arange(len(act)), "window": w, "active": act, "z": z, "rej": rj, "z_circ": zc, "p_circ": pc}))
    d = pd.concat(rows)
    d = d[d.active]
    if ring:
        d = label_windows(ep, d[["agent", "window"]].assign(pad=0), 300).merge(d, on=["agent", "window"])
    else:
        d["y"] = 0
    out = []
    for w, g in d.groupby("window"):
        ym = g.y.to_numpy() == 1
        out.append({"market": name, "ring": ring, "window": w, "ring active": bool(ym.any()), "active accounts": len(g),
                    "any rejection": bool(g.rej.any()), "non-member rejected": bool(g.rej.to_numpy()[~ym].any()),
                    "member rejected": bool(g.rej.to_numpy()[ym].any()) if ym.any() else False,
                    "catch@5 (jitter z)": bool(g.nlargest(5, "z").y.sum() > 0) if ym.any() else False,
                    "catch@5 (circular z)": bool(g.nlargest(5, "z_circ").y.sum() > 0) if ym.any() else False,
                    "circular Bonferroni rejects": bool((g.p_circ <= alpha / len(g)).any())})
    return out


def stage_abm(a):
    out = Path(a.out)
    markets = [("generic simulator", None)]
    for fam, f in (("index level", "vn_ensemble_draws.csv"), ("stock level", "vn_ensemble_stock_draws.csv"), ("trend-free", "vn_ensemble_acf_draws.csv")):
        d = pd.read_csv(out / f)
        for _, mk in d[d.accepted].head(a.n_markets).iterrows():
            markets.append((f"{fam} {int(mk.draw)}", {k: (int(mk[k]) if k in ("n_noise", "n_fund") else float(mk[k])) for k in KEYS}))
    jobs = []
    for name, params in markets:
        for i in range(a.reps):
            jobs.append((name, params, 41_000_000 + i, True, a.alpha, a.block))
            jobs.append((name, params, 42_000_000 + i, False, a.alpha, a.block))
    with ProcessPoolExecutor(a.workers, mp_context=mp.get_context("spawn")) as pool:
        res = [r for rr in pool.map(_abm_task, jobs, chunksize=2) for r in rr]
    df = pd.DataFrame(res)
    df.to_csv(out / "jitter_abm_windows.csv", index=False)
    summ = []
    for (mk, ring), g in df.groupby(["market", "ring"], sort=False):
        act = g[g["ring active"]]
        summ.append({"market": mk, "ring in market": ring, "windows": len(g), "mean active accounts": g["active accounts"].mean(),
                     "family-wise error (non-member rejected)": g["non-member rejected"].mean(),
                     "ring windows": len(act), "member rejected": act["member rejected"].mean() if len(act) else np.nan,
                     "catch@5 (jitter z)": act["catch@5 (jitter z)"].mean() if len(act) else np.nan,
                     "catch@5 (circular z)": act["catch@5 (circular z)"].mean() if len(act) else np.nan,
                     "circular Bonferroni rejects any": g["circular Bonferroni rejects"].mean()})
    s = pd.DataFrame(summ)
    s.to_csv(out / "jitter_abm.csv", index=False)
    print(s.round(3).to_markdown(index=False))


# ---- real ----------------------------------------------------------------------------------------------------------------------------------
def stratified_p(F, wreg, Q, tols, B, rng):
    x_all = F[0] - F[1]
    n, Tn = x_all.shape
    tot = x_all.sum(0)
    act = np.flatnonzero(F.sum(axis=(0, 2)) >= 3)
    p = np.ones(n)
    for i in act:
        x = x_all[i]
        o = tot - x
        reg = _circ_box(o[None], wreg)[0]
        qs = np.quantile(reg, np.linspace(0, 1, Q + 1)[1:-1])
        stratum = np.searchsorted(qs, reg, side="right")
        a_ = np.argsort(stratum, kind="stable")
        O = [_circ_box(o[None], t)[0] for t in tols]
        st = np.empty((B + 1, len(tols)))
        st[0] = [x @ Ot for Ot in O]
        keys = rng.random((B, Tn))
        for b in range(B):
            bb = np.lexsort((keys[b], stratum))
            xg = np.empty(Tn)
            xg[a_] = x[bb]
            st[b + 1] = [xg @ Ot for Ot in O]
        sd = st.std(0)
        z = ((st - st.mean(0)) / np.where(sd > 0, sd, 1)).max(1)
        p[i] = (1 + (z[1:] >= z[0]).sum()) / (B + 1)
    return p[act]


def stage_real(a):
    """Bonferroni rejections at family-wise level 5% on real order flow, per window, circular and block-jitter nulls."""
    from run_real_accounts import load_orders, windows
    S = Path(os.environ.get("MARKETSIM_DATA", "external_data")) / "acct_data"
    d = load_orders(S / "zenodo_hl_l4_sample/first_member.bin")
    Fl = list(windows(d, 0.5, T))
    rng = np.random.default_rng(a.seed)
    rows = []
    for wi, F in enumerate(Fl):
        sel = F.sum(axis=(0, 2)) >= 3
        m = int(sel.sum())
        z, pc = coincidence_scan(F, TOLS, signed=True)
        r = {"window": wi, "accounts tested": m, "rejections, circular Bonferroni": int((pc[sel] <= 0.05 / m).sum())}
        for blk, tols in ((100, TOLS), (30, (1, 2, 3))):
            B = n_draws(m, 0.05)
            z, p, e, u = jitter_scan(F, tols, blk, B, True, rng, active=sel, reject_alpha=0.05)
            r[f"rejections, jitter block {blk}"] = int(((u == B) & (p <= 0.05 / m) & sel).sum())
        rows.append(r)
        print(r, flush=True)
    pd.DataFrame(rows).to_csv(Path(a.out) / "jitter_real_bonferroni.csv", index=False)


def stage_real_calib(a):
    """Share of accounts with p <= 0.01 and 0.05 under each null (fixed number of surrogates, no early drop)."""
    from run_real_accounts import load_orders, windows
    S = Path(os.environ.get("MARKETSIM_DATA", "external_data")) / "acct_data"
    d = load_orders(S / "zenodo_hl_l4_sample/first_member.bin")
    Fl = list(windows(d, 0.5, T))
    rng = np.random.default_rng(a.seed)
    rows = []
    for name, kw in [("circular shifts (block 300)", dict(block=300, tols=TOLS)), ("jitter, block 150", dict(block=150, tols=TOLS)), ("jitter, block 75", dict(block=75, tols=TOLS)),
                     ("jitter, block 30, tolerances 1-3", dict(block=30, tols=(1, 2, 3))), ("jitter, block 15, tolerances 1-3", dict(block=15, tols=(1, 2, 3)))]:
        n01 = n05 = tot = 0
        for F in Fl:
            sel = F.sum(axis=(0, 2)) >= 3
            z, p, e, u = jitter_scan(F, kw["tols"], kw["block"], 999, True, rng, active=sel)
            n01 += int((p[sel] <= 0.01).sum()); n05 += int((p[sel] <= 0.05).sum()); tot += int(sel.sum())
        rows.append({"null": name, "accounts tested": tot, "share with p<=0.01": n01 / tot, "share with p<=0.05": n05 / tot})
        print(rows[-1], flush=True)
    for wreg, Q in ((15, 5), (5, 10)):
        ps = np.concatenate([stratified_p(F, wreg, Q, (1, 3), 299, rng) for F in Fl[:4]])
        rows.append({"null": f"stratified permutation (regime proxy: others' flow smoothed over {wreg} bins, {Q} strata), first 4 windows", "accounts tested": len(ps),
                     "share with p<=0.01": float((ps <= 0.01).mean()), "share with p<=0.05": float((ps <= 0.05).mean())})
        print(rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(Path(a.out) / "jitter_real_calibration.csv", index=False)


# ---- maxt ----------------------------------------------------------------------------------------------------------------------------------
def _stats(x):
    tot = x.sum(0)
    return np.array([(x * _circ_box(tot[None] - x, tol)).sum(1) for tol in TOLS])          # [tolerances, accounts]


def _joint_draw(x, rng, block):
    N = x.shape[0]
    xs = np.empty_like(x)
    for a_ in range(0, T, block):
        b_ = min(a_ + block, T)
        L = b_ - a_
        idx = (np.arange(L)[None, :] + rng.integers(0, L, size=N)[:, None]) % L
        xs[:, a_:b_] = np.take_along_axis(x[:, a_:b_], idx, axis=1)
    return xs


def stage_maxt(a):
    """Westfall-Young step-down max-T with all accounts shifted jointly, against Bonferroni with the per-account jitter p-values.

    Subset pivotality fails: the reference distribution shifts the ring's members too, which removes the bursts they put into every honest account's
    aggregate of others, so the honest accounts look extreme against it. Family-wise error = share of windows in which a non-member is rejected.
    """
    rng = np.random.default_rng(a.seed)
    rows = []
    for N, K, eta in ((100, 0, 0.3), (100, 6, 0.3), (100, 12, 0.3), (100, 12, 1.0), (100, 24, 1.0)):
        fb = fw = pb = pw = 0
        for _ in range(a.reps):
            x = make_flows(rng, N, K, eta)
            f = np.stack([x, np.zeros_like(x)])
            _, p, rb = reject_set(f, a.block, a.alpha, rng)
            obs = _stats(x)
            G = np.array([_stats(_joint_draw(x, rng, a.block)) for _ in range(a.n_joint)])
            mu, sd = G.mean(0), G.std(0)
            Zobs = ((obs - mu) / sd).max(0)
            Zg = ((G - mu[None]) / sd[None]).max(1)
            order = np.argsort(-Zobs)
            rw = np.zeros(N, bool)
            prev = 0.0
            for r, i in enumerate(order):
                padj = max(prev, (1 + (Zg[:, order[r:]].max(1) >= Zobs[i]).sum()) / (a.n_joint + 1))
                prev = padj
                if padj <= a.alpha:
                    rw[i] = True
                else:
                    break
            fb += int(rb[K:].any()); fw += int(rw[K:].any()); pb += int(rb[:K].any()) if K else 0; pw += int(rw[:K].any()) if K else 0
        rows.append({"N": N, "ring size K": K, "eta": eta, "windows": a.reps, "family-wise error, Bonferroni with jitter p": fb / a.reps,
                     "family-wise error, joint-shift max-T step-down": fw / a.reps, "ring detected, Bonferroni": pb / a.reps if K else np.nan,
                     "ring detected, max-T": pw / a.reps if K else np.nan})
        print(rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(Path(a.out) / "jitter_maxt.csv", index=False)


def main(a):
    {"fwer": stage_fwer, "regime": stage_regime, "kmin": stage_kmin, "abm": stage_abm, "real": stage_real, "real_calib": stage_real_calib, "maxt": stage_maxt}[a.stage](a)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--block", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--n-markets", type=int, default=2)
    ap.add_argument("--n-joint", type=int, default=500)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
