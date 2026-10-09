"""Detection experiments on simulated markets.

E1  Detection vs manipulator evasion (train on non-evasive manipulators).
E2  Where the false positives come from (honest agent kinds that get flagged).
E3  Label scarcity: supervised detectors trained on k labelled episodes.
E4  Retraining on a mix of evasion levels, tested on a level never seen in training.

Operating points are fixed on the training data (1% false-positive rate) and then
applied unchanged to the shifted test data, so the reported FPR can drift.
Everything is repeated over independent train/test seed sets; tables show mean (sd).
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from marketsim.detect import (GBM, Logistic, build_dataset, evaluate, false_positive_breakdown, make_detectors,
                              operating_threshold, with_evasion)
from marketsim.sim import SimConfig

EVASION = [0.0, 0.25, 0.5, 0.75, 1.0]


def fmt(series: pd.Series) -> str:
    return f"{series.mean():.2f} ({series.std(ddof=0):.2f})"


def run(n_train: int, n_test: int, reps: int, workers: int) -> dict[str, pd.DataFrame]:
    base = SimConfig()
    e1, e2, e3, e4, e6 = [], [], [], [], []
    for rep in range(reps):
        t0 = time.time()
        off = rep * 100_000
        train_seeds = list(range(off, off + n_train))
        train, _ = build_dataset(train_seeds, with_evasion(base, 0.0), workers)
        dets = make_detectors(seed=rep)
        thr = {}
        for d in dets:
            d.fit(train, train.y.to_numpy())
            thr[d.name] = operating_threshold(d, train)

        for e in EVASION:
            test, pnl = build_dataset(range(off + 50_000, off + 50_000 + n_test), with_evasion(base, e), workers)
            for d in dets:
                r = evaluate(d, test, thr[d.name])
                e1.append(dict(rep=rep, evasion=e, detector=d.name, **r))
                if e == 0.0:
                    fp = false_positive_breakdown(d, test, thr[d.name])
                    for kind, v in fp.items():
                        e2.append(dict(rep=rep, detector=d.name, kind=kind, flagged=v))
            for typ in ("spoof", "pump"):
                tot, shares = pnl[typ]
                imp = np.asarray(pnl["impact"][typ])
                e6.append(dict(rep=rep, evasion=e, type=typ, pnl=tot, shares=shares,
                               impact_sum=imp.sum(), impact_sq=(imp ** 2).sum(), cycles=len(imp)))

            if e in (0.0, 0.75):
                # E3: label scarcity (first k training episodes only)
                for k in (3, 10, n_train):
                    sub = train[train.episode.isin(train_seeds[:k])]
                    if sub.y.sum() < 5:
                        continue
                    for cls in (Logistic, GBM):
                        d = cls() if cls is Logistic else cls(seed=rep)
                        d.fit(sub, sub.y.to_numpy())
                        r = evaluate(d, test, operating_threshold(d, sub))
                        e3.append(dict(rep=rep, evasion=e, detector=d.name, k=k, positives=int(sub.y.sum()), **r))

        # E4: train on evasion 0 and 0.5, test on 0.75 and 1.0 (0.75 and 1.0 never seen)
        mixed = pd.concat([
            train[train.episode.isin(train_seeds[: n_train // 2])],
            build_dataset(range(off + 20_000, off + 20_000 + n_train // 2), with_evasion(base, 0.5), workers)[0],
        ], ignore_index=True)
        d = GBM(seed=rep).fit(mixed, mixed.y.to_numpy())
        thr_m = operating_threshold(d, mixed)
        for e in (0.75, 1.0):
            test, _ = build_dataset(range(off + 50_000, off + 50_000 + n_test), with_evasion(base, e), workers)
            e4.append(dict(rep=rep, evasion=e, detector="gbm_mixed", **evaluate(d, test, thr_m)))
        print(f"rep {rep} done in {time.time() - t0:.0f}s", flush=True)

    return {k: pd.DataFrame(v) for k, v in dict(e1=e1, e2=e2, e3=e3, e4=e4, e6=e6).items()}


def table(df: pd.DataFrame, index: str, columns: str, value: str) -> pd.DataFrame:
    g = df.groupby([index, columns])[value].apply(fmt).unstack(columns)
    return g


def render(res: dict[str, pd.DataFrame], args) -> str:
    out = [f"# Detection experiments\n",
           f"{args.reps} independent repetitions; per repetition {args.n_train} training episodes "
           f"(non-evasive manipulators) and {args.n_test} test episodes per evasion level. "
           f"Cells are mean (sd) over repetitions. Detection unit: one account in one 300-step window.\n"]
    e1 = res["e1"]
    order = ["otr_rule", "iforest", "logreg", "gbm"]
    for value, title in (("recall", "E1a. Recall at the 1% training-FPR operating point"),
                         ("fpr", "E1b. Realised false-positive rate at that same threshold"),
                         ("ap", "E1c. Average precision (threshold-free)")):
        t = table(e1, "detector", "evasion", value).reindex(order)
        out += [f"## {title}\n", "evasion level →\n", t.to_markdown(), "\n"]
    out += ["## E1d. Recall by manipulation type (gbm / iforest)\n"]
    for det in ("gbm", "iforest"):
        sub = e1[e1.detector == det]
        rows = {typ: sub.groupby("evasion")[f"recall_{typ}"].apply(fmt) for typ in ("spoof", "pump", "wash")}
        out += [f"**{det}**\n", pd.DataFrame(rows).T.to_markdown(), "\n"]
    e2 = res["e2"]
    t = e2.groupby(["kind", "detector"]).flagged.mean().unstack("detector").reindex(columns=order)
    out += ["## E2. Share of honest windows flagged, by agent kind (evasion 0)\n",
            "Includes the manipulator accounts' own windows in which they were not manipulating.\n",
            t.round(3).to_markdown(), "\n"]
    e3 = res["e3"]
    out += ["## E3. Label scarcity: recall / average precision vs number of labelled training episodes\n"]
    for e in sorted(e3.evasion.unique()):
        sub = e3[e3.evasion == e]
        t = pd.DataFrame({
            "positives": sub.groupby(["detector", "k"]).positives.mean().round(0),
            "recall": sub.groupby(["detector", "k"]).recall.apply(fmt),
            "ap": sub.groupby(["detector", "k"]).ap.apply(fmt),
        })
        out += [f"evasion = {e}\n", t.to_markdown(), "\n"]
    e4 = res["e4"]
    t4 = e4.groupby("evasion").agg(recall=("recall", fmt), fpr=("fpr", fmt), ap=("ap", fmt))
    out += ["## E4. gbm trained on evasion {0, 0.5}, tested on unseen evasion levels\n", t4.to_markdown(), "\n"]
    e6 = res["e6"]
    g = e6.groupby(["type", "evasion"])[["pnl", "shares", "impact_sum", "impact_sq", "cycles"]].sum()
    g["profit_per_share"] = (g.pnl / g.shares).round(3)
    g["impact_ticks"] = g.impact_sum / g.cycles
    g["impact_se"] = np.sqrt((g.impact_sq / g.cycles - g.impact_ticks ** 2) / g.cycles)
    g["impact"] = g.apply(lambda r: f"{r.impact_ticks:.2f} ± {r.impact_se:.2f}", axis=1)
    out += ["## Validity check: what manipulation achieves, by evasion level (pooled over all test episodes)\n",
            "`impact` = mean price move in the manipulator's intended direction, in ticks (spoof: 8 steps after the "
            "fake orders appear; pump: first to last pump order), ± standard error over cycles. "
            "`profit_per_share` is mark-to-market on tagged trades only. Values near zero mean the simulated "
            "manipulation leaves the behavioural footprint without a demonstrated payoff in this market.\n",
            g[["impact", "cycles", "profit_per_share", "shares"]].unstack("type").to_markdown(), "\n"]
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-train", type=int, default=40)
    ap.add_argument("--n-test", type=int, default=20)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    res = run(args.n_train, args.n_test, args.reps, args.workers)
    out = Path(args.out)
    out.mkdir(exist_ok=True)
    for k, v in res.items():
        v.to_csv(out / f"{k}.csv", index=False)
    (out / "summary.md").write_text(render(res, args))
    print((out / "summary.md").read_text())
