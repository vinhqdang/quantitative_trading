"""Allocating a fixed inspection capacity over stocks (windows) that differ in size and in the ring's prize (Proposition on maximin allocation).

sim    A ring (default strategy) acts in each of W simulated "stocks" with different numbers of noise traders (hence active accounts N_w) and a block of
       shares proportional to the stock's size (the ring's prize). Per episode we store the ring's gain and the rank of its best-placed member among all
       active accounts in every window, so that for any number b of accounts inspected per window the ring is caught iff that rank is <= b.
solve  Evaluate allocations of a total capacity C over the stocks: uniform, proportional to N_w, the rule of the proposition (equalise the ring's net
       benefit, using the model q_B = Phi(S + Phi^-1(b/N)) with S from the fitted scaling law or fitted per stock), and an oracle that equalises the
       empirical net benefit on the selection episodes (even-numbered episodes); every rule is scored on the held-out (odd-numbered) episodes.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import multiprocessing as mp
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq, least_squares
from scipy.stats import norm

from marketsim.coordination import scan_episode
from marketsim.ring_adversary import _pooled, ring_only_config
from marketsim.sim import SimConfig, ring_utility, run_episode

STOCKS = [(n, 8 * n) for n in (50, 100, 200, 300, 450, 600, 800, 1000)]       # (noise traders, block of shares in lots)
S0, GAMMA, CEIL, K_RING = 1.20, 0.5, 0.90, 12


def _ep(args):
    n_noise, block, seed = args
    cfg = ring_only_config(replace(SimConfig(), n_noise=n_noise, ring_block=block), None)
    cfg = replace(cfg, steps=3000, n_ring=(1, 1))
    ep = run_episode(seed, cfg)
    u = ring_utility(ep)
    members = set(a for ms in ep.extras["ring_members"] for a in ms)
    df = _pooled(scan_episode(ep))
    best, n_act = np.inf, []
    for _, g in df.groupby("window"):
        order = g.sort_values("score", ascending=False).agent.to_numpy()
        n_act.append(len(order))
        hit = [i + 1 for i, a in enumerate(order) if a in members]
        if hit:
            best = min(best, hit[0])
    return {"n_noise": n_noise, "block": block, "seed": seed, "gain": u["gain"], "rank": best, "active": float(np.mean(n_act))}


def stage_sim(a):
    jobs = [(n, blk, 51_000_000 + 1000 * i + j) for i, (n, blk) in enumerate(STOCKS) for j in range(a.reps)]
    with ProcessPoolExecutor(a.workers, mp_context=mp.get_context("spawn")) as pool:
        res = list(pool.map(_ep, jobs, chunksize=2))
    pd.DataFrame(res).to_csv(Path(a.out) / "allocation_episodes.csv", index=False)
    print(pd.DataFrame(res).groupby("n_noise").agg(gain=("gain", "mean"), active=("active", "mean"), caught5=("rank", lambda r: (r <= 5).mean())))


# ---- model -------------------------------------------------------------------------------------------------------------------------------------
def q_rank(b, N, S):
    u = np.clip(b / N, 1e-12, 1 - 1e-12)
    return norm.cdf(S + norm.ppf(u))


def Q_ring(b, N, S, K=K_RING, ceil=CEIL):
    return ceil * (1 - (1 - q_rank(b, N, S)) ** K)


def b_for_Q(Qt, N, S, K=K_RING, ceil=CEIL):
    """Smallest (real) b with ring detection probability Qt, or inf if Qt exceeds what b = N can give."""
    if Qt <= 0:
        return 0.0
    if Qt >= Q_ring(N - 1e-9, N, S, K, ceil):
        return np.inf
    return brentq(lambda b: Q_ring(b, N, S, K, ceil) - Qt, 1e-9, N - 1e-9)


def rule_allocation(C, N, g, S, m, K=K_RING, ceil=CEIL):
    """Equalise the ring's net benefit g_w (1 - m Q_w(b_w)) at a common level v: b_w(v) = Q_w^{-1}((1 - v/g_w)/m); sum b_w(v) = C.

    Returns the real-valued allocation (sums to C unless even v = 0 needs less than C, in which case the surplus is spread proportionally to N).
    """
    W = len(N)

    def alloc(v):
        out = np.zeros(W)
        for w in range(W):
            if g[w] <= v:
                continue
            Qt = (1 - v / g[w]) / m
            out[w] = b_for_Q(Qt, N[w], S[w], K, ceil)
        return out

    if alloc(0.0).sum() <= C:
        b = alloc(0.0)
        return b + (C - b.sum()) * N / N.sum()
    lo, hi = 0.0, float(np.max(g))
    for _ in range(60):
        v = 0.5 * (lo + hi)
        s = alloc(v).sum()
        if s > C:
            lo = v
        else:
            hi = v
    return alloc(hi)


def integerise(b, C):
    b = np.where(np.isfinite(b), b, 0)
    f = np.floor(b).astype(int)
    rem = int(C - f.sum())
    for i in np.argsort(-(b - f))[:max(rem, 0)]:
        f[i] += 1
    return f


def net_benefit(df_w, b, m):
    g = df_w.gain.to_numpy()
    caught = (df_w["rank"].to_numpy() <= b)
    return float(np.mean(g - m * np.maximum(g, 0) * caught))


def oracle_allocation(curves, C):
    """Greedy water-filling on empirical net-benefit curves U_w(b): add one unit to the stock with the largest current net benefit."""
    W = len(curves)
    b = np.zeros(W, dtype=int)
    for _ in range(C):
        cur = np.array([curves[w][min(b[w], len(curves[w]) - 1)] for w in range(W)])
        w = int(np.argmax(cur))
        b[w] += 1
    return b


def stage_solve(a):
    d = pd.read_csv(Path(a.out) / "allocation_episodes.csv")
    stocks = sorted(d.n_noise.unique())
    W = len(stocks)
    Nw = np.array([d[d.n_noise == s].active.mean() for s in stocks])
    sel = {s: d[(d.n_noise == s) & (d.seed % 2 == 0)] for s in stocks}
    tst = {s: d[(d.n_noise == s) & (d.seed % 2 == 1)] for s in stocks}
    gw = np.array([sel[s].gain.clip(lower=0).mean() for s in stocks])
    bmax = int(Nw.max())
    # per-stock fitted signal S_w by least squares of the model onto the empirical probability of being caught on the selection episodes
    S_fit = []
    for s, N in zip(stocks, Nw):
        r = sel[s]["rank"].to_numpy()
        bs = np.array([1, 2, 3, 5, 8, 12, 20, 40, 80, 160])
        bs = bs[bs < N]
        emp = np.array([(r <= b).mean() for b in bs])
        res = least_squares(lambda S: Q_ring(bs, N, S[0]) - emp, [1.0], bounds=(-3, 6))
        S_fit.append(float(res.x[0]))
    S_fit = np.array(S_fit)
    S_law = S0 * (100.0 / Nw) ** GAMMA
    curves = {m: [np.array([net_benefit(sel[s], b, m) for b in range(bmax + 1)]) for s in stocks] for m in (5, 10)}
    rows, alloc_rows = [], []
    for m in (5, 10):
        for C in a.capacities:
            allocs = {"uniform": integerise(np.full(W, C / W), C), "proportional to N": integerise(C * Nw / Nw.sum(), C),
                      "rule, signal from scaling law": integerise(rule_allocation(C, Nw, gw, S_law, m), C),
                      "rule, signal fitted per stock": integerise(rule_allocation(C, Nw, gw, S_fit, m), C),
                      "oracle (empirical curves)": oracle_allocation(curves[m], C)}
            for name, b in allocs.items():
                u = np.array([net_benefit(tst[s], int(bw), m) for s, bw in zip(stocks, b)])
                rows.append({"m": m, "capacity C": C, "allocation": name, "ring's best net benefit": float(u.max()), "stock where it acts": int(stocks[int(np.argmax(u))]),
                             "mean net benefit over stocks": float(u.mean()), "stocks with net benefit > 0": int((u > 0).sum())})
                if C == a.show_C:
                    alloc_rows += [{"m": m, "capacity C": C, "allocation": name, "n_noise": s, "N_w": N, "prize g_w": g, "b_w": int(bw)}
                                   for s, N, g, bw in zip(stocks, Nw, gw, b)]
    df = pd.DataFrame(rows)
    df.to_csv(Path(a.out) / "allocation_results.csv", index=False)
    pd.DataFrame(alloc_rows).to_csv(Path(a.out) / "allocation_shown.csv", index=False)
    pd.DataFrame({"n_noise": stocks, "N_w": Nw, "prize g_w": gw, "S fitted": S_fit, "S scaling law": S_law}).to_csv(Path(a.out) / "allocation_stocks.csv", index=False)
    # capacity needed to leave the ring no positive net benefit on the held-out episodes
    need = []
    for m in (5, 10):
        for name in ["uniform", "proportional to N", "rule, signal from scaling law", "rule, signal fitted per stock", "oracle (empirical curves)"]:
            g = df[(df.m == m) & (df.allocation == name)].sort_values("capacity C")
            ok = g[g["ring's best net benefit"] <= 0]
            need.append({"m": m, "allocation": name, "smallest capacity with no positive net benefit": int(ok["capacity C"].min()) if len(ok) else np.nan})
    need = pd.DataFrame(need)
    need.to_csv(Path(a.out) / "allocation_capacity.csv", index=False)
    print(pd.DataFrame({"n_noise": stocks, "N_w": Nw.round(0), "g_w": gw.round(0), "S_fit": S_fit.round(2), "S_law": S_law.round(2)}).to_string(index=False))
    print(need.to_string(index=False))
    print(df[df.m == 5].pivot_table(index="capacity C", columns="allocation", values="ring's best net benefit").round(0).to_string())


def main(a):
    {"sim": stage_sim, "solve": stage_solve}[a.stage](a)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--capacities", type=int, nargs="+", default=[8, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512])
    ap.add_argument("--show-C", type=int, default=64)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
