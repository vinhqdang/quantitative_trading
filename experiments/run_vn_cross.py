"""Cross-evaluated best response: the ring's strategy set is the union of strategies found anywhere.

Evolution-strategy runs are noisy, so gains differ across policies by search luck. Here every policy is
faced with the same finite set of ring strategies (the ones found in results/vn_policy.md plus the default and the
strongest unconstrained ring). The ring picks the strategy with the best result on selection episodes, and the
numbers reported come from separate episodes. The result is a lower bound on a fully adaptive ring's benefit.
"""

from __future__ import annotations

import argparse
import ast
import re
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.policy import Policy
from marketsim.ring_adversary import DEFAULT, evaluate, make_pool, net_utility
from marketsim.vietnam import vn_config

UNCONSTRAINED = {"K": 18, "q": 5, "m_push": 3, "p_push": 1.0, "p_acc": 0.29, "jitter": 2, "cross_frac": 0.0,
                 "acc_len": 37, "push_len": 46, "dist_len": 46, "cool": 67}
ROWS = [
    ("no price band", dict(band=0.0), 1, "none", 0),
    ("band 7% (HOSE today)", dict(band=0.07), 1, "none", 0),
    ("band 10%", dict(band=0.10), 1, "none", 0),
    ("band 15%", dict(band=0.15), 1, "none", 0),
    ("band 7% + block at 60-step mean", dict(band=0.07), 60, "none", 0),
    ("band 7% + block at 240-step mean", dict(band=0.07), 240, "none", 0),
    ("band 7% + inspect 1 per window", dict(band=0.07), 1, "scan", 1),
    ("band 7% + inspect 3 per window", dict(band=0.07), 1, "scan", 3),
]


def strategies(path: Path) -> list[dict]:
    found = [UNCONSTRAINED, DEFAULT]
    for line in path.read_text().splitlines():
        m = re.match(r"- .*?: (\{.*\})$", line)
        if m:
            found.append(ast.literal_eval(m.group(1)))
    uniq = []
    for p in found:
        if p not in uniq:
            uniq.append(p)
    return uniq


def score(r: pd.DataFrame, kind: str, B: int, m: float = 5.0) -> float:
    return net_utility(r, B, m) if kind != "none" else float(r.gain.mean())


def main(args):
    strats = strategies(Path(args.out) / "vn_policy.md")
    print(len(strats), "strategies", flush=True)
    rows = []
    with make_pool(args.workers) as pool:
        for i, (label, pol_kw, L, kind, B) in enumerate(ROWS):
            base = replace(vn_config(policy=Policy(label, day_len=240, **pol_kw)), block_vwap=L)
            sel = list(range(13_000_000, 13_000_000 + args.n))
            rep = list(range(14_000_000, 14_000_000 + args.n))
            rs = evaluate(strats, sel, base, kind, None, pool)
            best = int(np.argmax([score(r, kind, B) for r in rs]))
            r = evaluate([strats[best]], rep, base, kind, None, pool)[0]
            se = float(r.gain.std(ddof=1) / np.sqrt(len(r)))
            row = {"scenario": label, "B": B, "block rule (steps)": L, "best strategy": best,
                   "gain": r.gain.mean(), "gain se": se, "displacement": r.displacement.mean()}
            if kind != "none":
                row.update({"caught": r[f"caught{B}"].mean(), "net U (m=5)": net_utility(r, B, 5),
                            "net U (m=10)": net_utility(r, B, 10)})
            rows.append(row)
            print(label, {k: (round(v, 1) if isinstance(v, float) else v) for k, v in row.items() if k != "scenario"}, flush=True)
    df = pd.DataFrame(rows)
    text = ["# Cross-evaluated best response of a collusion ring (Vietnam preset)\n",
            f"Strategy set: {len(strats)} ring parameter sets (the strongest unconstrained ring, the default ring, and the strategies found by the "
            f"evolution-strategy runs in `vn_policy.md`). For each policy the ring picks the strategy with the best result on {args.n} selection episodes; the "
            f"numbers come from {args.n} separate episodes (`gain se` = standard error over them). Lower gain is better for the regulator. "
            "A ring whose net U is negative would rather not operate.\n",
            df.round(2).to_markdown(index=False), ""]
    Path(args.out, "vn_cross.csv").write_text(df.to_csv(index=False))
    Path(args.out, "vn_cross.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
