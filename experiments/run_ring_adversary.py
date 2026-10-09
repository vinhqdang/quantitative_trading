"""R2/R3: how much can an adaptive ring still gain against budgeted inspection and a block-price rule?

Every row is a best response: the ring re-optimises its parameters (evolution strategy) against the
detector, inspection budget B per window, penalty multiple m on the illegal gain, and block reference-price
rule given in the row. Reported numbers are measured on episodes never used in the search.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.detect import GBM, build_dataset
from marketsim.ring_adversary import DEFAULT, NAMES, evaluate, evolve, make_pool, net_utility, ring_only_config
from marketsim.sim import SimConfig, run_episode

BASE = SimConfig()


def validate(params: dict, base, kind, det, B, seeds, pool):
    r = evaluate([params], seeds, base, kind, det, pool)[0]
    return r


def best_response(base, kind, det, B, m, pool, args, seed, init=None):
    best, mean, archive = evolve(base, kind, det, B, m, pool, seed=seed, pop_size=args.pop, gens=args.gens,
                                 k_seeds=args.k_seeds, init=init)
    if init is not None:  # the starting point is a candidate too
        best = best if net_utility_of(best, base, kind, det, B, m, pool, args) >= net_utility_of(init, base, kind, det, B, m, pool, args) else init
    sel = list(range(8_000_000 + seed * 100, 8_000_000 + seed * 100 + args.n_val))
    cands = [best, mean]
    rs = evaluate(cands, sel, base, kind, det, pool)
    score = [net_utility(r, B, m) if kind != "none" else r.gain.mean() for r in rs]
    chosen = cands[int(np.argmax(score))]
    test = list(range(9_000_000 + seed * 100, 9_000_000 + seed * 100 + args.n_val))
    return chosen, evaluate([chosen], test, base, kind, det, pool)[0]


def net_utility_of(params, base, kind, det, B, m, pool, args):
    seeds = list(range(8_500_000, 8_500_000 + args.n_val))
    r = evaluate([params], seeds, base, kind, det, pool)[0]
    return net_utility(r, B, m) if kind != "none" else r.gain.mean()


def row(label, kind, B, m, rule, chosen, r, g_star):
    keyp = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in chosen.items()}
    out = {"scenario": label, "detector": kind, "B": B, "block rule (steps)": rule,
           "gain": r.gain.mean(), "gain retained": r.gain.mean() / g_star if g_star else np.nan,
           "displacement": r.displacement.mean(), "params": keyp}
    if kind != "none":
        out["caught"] = r[f"caught{B}"].mean()
        out["net U (m=5)"] = net_utility(r, B, 5)
        out["net U (m=10)"] = net_utility(r, B, 10)
    return out


def staleness_cost(Ls, n=6, workers=4):
    """Honest cost of a trailing-mean block price: mean |mid - trailing mean| in ticks, honest-only markets."""
    cfg = replace(BASE, n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(0, 0))
    mids = [run_episode(s, cfg).mids[cfg.warmup:] for s in range(7_000_000, 7_000_000 + n)]
    out = {}
    for L in Ls:
        d = []
        for m in mids:
            c = np.cumsum(np.r_[0, m])
            tm = (c[L:] - c[:-L]) / L if L > 1 else m
            d.append(np.abs(m[L - 1:] - tm))
        out[L] = float(np.mean(np.concatenate(d)))
    return out


UNCONSTRAINED = {"K": 18, "q": 5, "m_push": 3, "p_push": 1.0, "p_acc": 0.29, "jitter": 2, "cross_frac": 0.0,
                 "acc_len": 37, "push_len": 46, "dist_len": 46, "cool": 67}


def run_warm(args) -> tuple[pd.DataFrame, dict]:
    """Stronger adversary: evolution starts from the parameters that were optimal without any detection."""
    g_star = float(pd.read_csv(Path(args.out) / "ring_adversary.csv").query("scenario == 'ring ignoring detection'").gain.iloc[0])
    ring_cfg = replace(BASE, n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(1, 2))
    train, _ = build_dataset(range(args.n_train), ring_cfg, args.workers)
    gbm = GBM(0).fit(train, train.y.to_numpy())
    rows = []
    t0 = time.time()
    with make_pool(args.workers) as pool:
        for kind, det, Bs in (("scan", None, args.budgets), ("gbm", gbm, [1, 3])):
            for B in Bs:
                chosen, r = best_response(BASE, kind, det, B, 5.0, pool, args, 100 + B, init=UNCONSTRAINED)
                rows.append(row("adaptive ring, warm start", kind, B, 5, 1, chosen, r, g_star))
                print(f"warm {kind} B={B}: gain {r.gain.mean():.0f} caught {r[f'caught{B}'].mean():.2f} "
                      f"({time.time() - t0:.0f}s)", flush=True)
        for L in args.vwap:
            base = replace(BASE, block_vwap=L)
            chosen, r = best_response(base, "none", None, 0, 0, pool, args, 140 + L, init=UNCONSTRAINED)
            rows.append(row("block rule only, warm start", "none", 0, 0, L, chosen, r, g_star))
            print(f"warm vwap {L}: gain {r.gain.mean():.0f} ({time.time() - t0:.0f}s)", flush=True)
            chosen, r = best_response(base, "scan", None, 3, 5.0, pool, args, 150 + L, init=UNCONSTRAINED)
            rows.append(row("block rule + scan inspection, warm start", "scan", 3, 5, L, chosen, r, g_star))
            print(f"warm vwap {L} + scan B=3: gain {r.gain.mean():.0f} caught {r['caught3'].mean():.2f} "
                  f"({time.time() - t0:.0f}s)", flush=True)
    return pd.DataFrame(rows), {}


def run(args) -> tuple[pd.DataFrame, dict]:
    ring_cfg = replace(BASE, n_spoof=(0, 0), n_pump=(0, 0), n_wash_pairs=(0, 0), n_ring=(1, 2))
    train, _ = build_dataset(range(args.n_train), ring_cfg, args.workers)
    gbm = GBM(0).fit(train, train.y.to_numpy())
    rows = []
    with make_pool(args.workers) as pool:
        t0 = time.time()
        # reference: unconstrained ring, and the default (non-adaptive) ring against each detector
        chosen, r = best_response(BASE, "none", None, 0, 0, pool, args, 1)
        g_star = r.gain.mean()
        rows.append(row("ring ignoring detection", "none", 0, 0, 1, chosen, r, g_star))
        print(f"unconstrained: gain {g_star:.0f} ({time.time() - t0:.0f}s)", flush=True)
        for kind, det in (("scan", None), ("gbm", gbm)):
            r = evaluate([dict(DEFAULT)], list(range(9_500_000, 9_500_000 + args.n_val)), BASE, kind, det, pool)[0]
            for B in args.budgets:
                rows.append(row("default ring (not adaptive)", kind, B, 5, 1, DEFAULT, r, g_star))
        for kind, det in (("scan", None), ("gbm", gbm)):
            for B in args.budgets:
                chosen, r = best_response(BASE, kind, det, B, 5.0, pool, args, 10 + B)
                rows.append(row("adaptive ring", kind, B, 5, 1, chosen, r, g_star))
                print(f"{kind} B={B}: gain {r.gain.mean():.0f} caught {r[f'caught{B}'].mean():.2f} "
                      f"({time.time() - t0:.0f}s)", flush=True)
        # block reference-price rule
        for L in args.vwap:
            base = replace(BASE, block_vwap=L)
            chosen, r = best_response(base, "none", None, 0, 0, pool, args, 40 + L)
            rows.append(row(f"block priced at trailing mean, no inspection", "none", 0, 0, L, chosen, r, g_star))
            print(f"vwap {L}: gain {r.gain.mean():.0f} ({time.time() - t0:.0f}s)", flush=True)
            chosen, r = best_response(base, "scan", None, 3, 5.0, pool, args, 50 + L)
            rows.append(row("block rule + scan inspection", "scan", 3, 5, L, chosen, r, g_star))
            print(f"vwap {L} + scan B=3: gain {r.gain.mean():.0f} caught {r['caught3'].mean():.2f} "
                  f"({time.time() - t0:.0f}s)", flush=True)
    stale = staleness_cost([1] + list(args.vwap), workers=args.workers)
    return pd.DataFrame(rows), stale


def render(df: pd.DataFrame, stale: dict, args) -> str:
    out = ["# R2 / R3: adaptive collusion ring against inspection and a block-price rule\n",
           f"Evolution strategy per row: population {args.pop}, {args.gens} generations, {args.k_seeds} episodes per candidate; "
           f"selection on {args.n_val} episodes and reporting on {args.n_val} further episodes. One ring per episode "
           "(3000 steps). `gain` = benefit of ring manipulation in tick-lots (block of 3000 lots times price displacement "
           "plus trading profit). `caught` = share of episodes in which at least one member was among the B inspected "
           "accounts of some window. `net U (m)` = gain minus m times the gain when caught; a deterred ring has net U <= 0 "
           "or retains almost no gain.\n"]
    show = df.copy()
    for c in ("gain", "displacement", "gain retained", "caught", "net U (m=5)", "net U (m=10)"):
        if c in show:
            show[c] = show[c].astype(float).round(2)
    cols = ["scenario", "detector", "B", "block rule (steps)", "gain", "gain retained", "displacement", "caught",
            "net U (m=5)", "net U (m=10)"]
    out += [show[[c for c in cols if c in show]].to_markdown(index=False), "\n"]
    out += ["## Honest cost of the block-price rule\n",
            "Mean absolute gap between the last mid and the trailing-mean block price in honest markets (ticks): "
            + ", ".join(f"{L} steps: {v:.2f}" for L, v in stale.items()) + ".\n"]
    out += ["## Parameters chosen by the adaptive ring\n"]
    for _, r in df.iterrows():
        out.append(f"- {r.scenario} / {r.detector} / B={r.B} / rule={r['block rule (steps)']}: {r.params}")
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-train", type=int, default=24)
    ap.add_argument("--n-val", type=int, default=16)
    ap.add_argument("--pop", type=int, default=12)
    ap.add_argument("--gens", type=int, default=5)
    ap.add_argument("--k-seeds", type=int, default=4)
    ap.add_argument("--budgets", type=int, nargs="+", default=[1, 3, 10])
    ap.add_argument("--vwap", type=int, nargs="+", default=[240])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    ap.add_argument("--warm", action="store_true", help="only the stronger warm-start adversaries")
    args = ap.parse_args()
    if args.warm:
        df, _ = run_warm(args)
        out = Path(args.out)
        df.drop(columns="params").to_csv(out / "ring_adversary_warm.csv", index=False)
        (out / "ring_adversary_warm.md").write_text(render(df, {1: 0.0}, args))
        print((out / "ring_adversary_warm.md").read_text())
        raise SystemExit
    df, stale = run(args)
    out = Path(args.out)
    out.mkdir(exist_ok=True)
    df.drop(columns="params").to_csv(out / "ring_adversary.csv", index=False)
    (out / "ring_adversary.md").write_text(render(df, stale, args))
    print((out / "ring_adversary.md").read_text())
