"""Sensitivity of the block-price rule results to the assumed block size (an assumption of the simulator).

The block size enters only the payoff, gain_L(b) = (b / b0) * block term + trading profit, so the effect of a different size is computed
exactly from the episodes of run_block_static.py (b0 = 3000 lots).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

R = Path("results")
B0 = 3000
BLOCKS = [300, 1000, 3000, 10000]
LS = [60, 240]


def main():
    d = pd.read_csv(R / "block_static_episodes.csv")
    rows = []
    for b in BLOCKS:
        f = b / B0
        for L in [1] + LS:
            d[f"g{L}_{b}"] = f * d[f"block_{L}"] + (d[f"gain_{L}"] - d[f"block_{L}"])
        for fam, gf in d.groupby("family"):
            ratios = {L: [] for L in LS}
            ratios_ad = {L: [] for L in LS}
            base_gain, positive = [], 0
            for mk, g in gf.groupby("market"):
                sel = g[g.part == "sel"].groupby("strategy").mean(numeric_only=True)
                rep = g[g.part == "rep"].groupby("strategy").mean(numeric_only=True)
                s0 = int(sel[f"g1_{b}"].idxmax())
                base = rep.loc[s0, f"g1_{b}"]
                base_gain.append(base)
                if base > 0:
                    positive += 1
                    for L in LS:
                        ratios[L].append(rep.loc[s0, f"g{L}_{b}"] / base)
                        sa = int(sel[f"g{L}_{b}"].idxmax())
                        ratios_ad[L].append(rep.loc[sa, f"g{L}_{b}"] / base)
            row = {"block size (lots)": b, "family": fam, "median gain, last-price reference": float(np.median(base_gain)), "markets with positive gain (of 6)": positive}
            for L in LS:
                row[f"median share kept, L={L}, ring keeps strategy"] = float(np.median(ratios[L])) if ratios[L] else np.nan
                row[f"median share kept, L={L}, ring re-selects"] = float(np.median(ratios_ad[L])) if ratios_ad[L] else np.nan
            rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(R / "block_size_sensitivity.csv", index=False)
    (R / "block_size_sensitivity.md").write_text("# Block-price rule against the assumed block size\n\n" + out.round(3).to_markdown(index=False) + "\n")
    print(out.round(3).to_string())


if __name__ == "__main__":
    main()
