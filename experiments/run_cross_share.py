"""Power of the signed and unsigned coincidence tests against the cross-trade share of the ring.

Cross trades are orders between ring members at the same step on opposite sides; the signed statistic nets them away. One ring per
episode in a clean market (default simulator); the ring parameter `cross_frac` is varied, everything else is the default.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from run_ring_ablation import evaluate


def main(a):
    seeds = range(30_000, 30_000 + a.n)
    rows = []
    for cf in (0.0, 0.2, 0.35, 0.5):
        r = evaluate(seeds, {}, {"cross_frac": cf}, {}, 300, a.workers)
        rows.append({"cross share": cf, **r})
        print(cf, r["catch@5"], r["catch@1"], flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(Path(a.out) / "ring_cross_share.csv", index=False)
    (Path(a.out) / "ring_cross_share.md").write_text("# Signed test against the ring's cross-trade share\n\n" + df.to_markdown(index=False) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=24)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
