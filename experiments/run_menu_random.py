"""Is the four-strategy menu of the ring close to its best response? A larger menu of random strategies against three policies.

In each accepted market (index-level, stock-level and trend-free families) the ring faces three policies: the daily band of 7% (reference),
the band with block prices at the trailing 240-step mean, and the band with inspection of 3 accounts per window. It chooses on selection
episodes among (a) the four-strategy menu used in the ensembles and (b) that menu plus `n_random` strategies drawn uniformly in the 11-parameter
strategy space. Selection is in two stages (all strategies on `n_sel` episodes; the menu and the five best then on `n_sel2` more), because a single
stage with few episodes picks noise; the chosen strategies are then scored on separate reporting episodes.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

import run_vn_cross as rvc
from marketsim.policy import Policy
from marketsim.ring_adversary import NAMES, decode, evaluate, make_pool, net_utility
from marketsim.vietnam import vn_config

KEYS = ("n_noise", "n_fund", "mm_activity", "fund_sigma", "mm_imb_sens", "mom_activity")
FAMILIES = {"index level": "vn_ensemble_draws.csv", "stock level": "vn_ensemble_stock_draws.csv", "trend-free": "vn_ensemble_acf_draws.csv"}
POLS = [("band 7%", dict(band=0.07), 1, "none", 0), ("band 7% + block at 240-step mean", dict(band=0.07), 240, "none", 0),
        ("band 7% + inspect 3 per window", dict(band=0.07), 1, "scan", 3)]


def main(args):
    out = Path(args.out)
    menu_all = rvc.strategies(out / "vn_policy.md")
    menu = [menu_all[i] for i in (0, 1, 3, 6)]
    rng = np.random.default_rng(args.seed)
    rand = [decode(rng.uniform(size=len(NAMES))) for _ in range(args.n_random)]
    strats = menu + rand
    rows, cells = [], []
    if args.resume and (out / "menu_random.csv").exists():
        rows = pd.read_csv(out / "menu_random.csv").to_dict("records")
        cells = pd.read_csv(out / "menu_random_selection.csv").to_dict("records")
    done = {(r["family"], r["market"], r["policy"]) for r in rows}
    with make_pool(args.workers) as pool:
        for fam, f in FAMILIES.items():
            d = pd.read_csv(out / f)
            for _, mk in d[d.accepted].head(args.n_markets).iterrows():
                params = {k: (int(mk[k]) if k in ("n_noise", "n_fund") else float(mk[k])) for k in KEYS}
                for label, pol_kw, L, kind, B in POLS:
                    if (fam, int(mk.draw), label) in done:
                        continue
                    base = replace(vn_config(policy=Policy(label, day_len=240, **pol_kw), **params), block_vwap=L)
                    sel = list(range(31_000_000, 31_000_000 + args.n_sel))
                    rep = list(range(32_000_000, 32_000_000 + args.n_rep))
                    rs = evaluate(strats, sel, base, kind, None, pool)
                    sc1 = np.array([rvc.score(r, kind, B) for r in rs])
                    # second stage: the four menu strategies and the five best of the first stage get further selection episodes
                    s2 = sorted(set(range(4)) | set(int(i) for i in np.argsort(-sc1)[:5]))
                    more = evaluate([strats[i] for i in s2], list(range(33_000_000, 33_000_000 + args.n_sel2)), base, kind, None, pool)
                    sc = np.full(len(strats), -np.inf)
                    for i, m2 in zip(s2, more):
                        sc[i] = rvc.score(pd.concat([rs[i], m2], ignore_index=True), kind, B)
                    b4, bn = int(np.argmax(sc[:4])), int(np.argmax(sc))
                    cache = {}
                    for key in {b4, bn}:
                        cache[key] = evaluate([strats[key]], rep, base, kind, None, pool)[0]
                    for name, key in (("menu of 4", b4), (f"menu + {args.n_random} random", bn)):
                        r = cache[key]
                        row = {"family": fam, "market": int(mk.draw), "policy": label, "menu": name, "strategy": key, "selection score": sc[key],
                               "gain": r.gain.mean(), "gain_se": r.gain.std(ddof=1) / np.sqrt(len(r))}
                        if kind != "none":
                            row.update({"caught": r[f"caught{B}"].mean(), "net_U5": net_utility(r, B, 5)})
                        rows.append(row)
                    for i, r in enumerate(rs):
                        cells.append({"family": fam, "market": int(mk.draw), "policy": label, "strategy": i, "gain_sel": r.gain.mean(),
                                      **({"caught_sel": r[f"caught{B}"].mean()} if kind != "none" else {})})
                    print(fam, int(mk.draw), label, "menu4 gain %.0f, big gain %.0f" % (cache[b4].gain.mean(), cache[bn].gain.mean()), flush=True)
                pd.DataFrame(rows).to_csv(out / "menu_random.csv", index=False)
                pd.DataFrame(cells).to_csv(out / "menu_random_selection.csv", index=False)
    pd.DataFrame(rows).to_csv(out / "menu_random.csv", index=False)
    pd.DataFrame(cells).to_csv(out / "menu_random_selection.csv", index=False)
    pd.DataFrame(rand).to_csv(out / "menu_random_strategies.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-random", type=int, default=24)
    ap.add_argument("--n-markets", type=int, default=6)
    ap.add_argument("--n-sel", type=int, default=6)
    ap.add_argument("--n-sel2", type=int, default=12)
    ap.add_argument("--n-rep", type=int, default=12)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--resume", action="store_true", help="skip the cells already in results/menu_random.csv")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
