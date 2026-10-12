"""Figures for the block-jitter test and the maximin allocation (results of run_jitter.py, analyse_jitter.py and run_allocation.py)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from make_figures2 import AQUA, BLUE, INK, MUTED, ORANGE, OUT, PLUM, R, panel, plain_log  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm


def fig_jitter():
    fw = pd.read_csv(R / "jitter_fwer.csv")
    rg = pd.read_csv(R / "jitter_regime.csv")
    km = pd.read_csv(R / "jitter_kmin_summary.csv")
    fig, axes = plt.subplots(1, 3, figsize=(5.15, 2.45))
    ax = axes[0]
    g = fw[fw.flows == "iid Gaussian"]
    x = np.arange(len(g))
    ax.bar(x - 0.2, g["family-wise error, circular"], 0.38, color=MUTED, label="circular shifts")
    ax.bar(x + 0.2, g["family-wise error, block jitter"], 0.38, color=BLUE, label="block jitter")
    ax.axhline(0.05, color=ORANGE, lw=1, ls="--")
    ax.set_xticks(x); ax.set_xticklabels(g.N)
    ax.set_xlabel("accounts N"); ax.set_ylabel("family-wise error"); ax.set_ylim(0, 0.14); ax.text(0.03, 0.97, "circular shifts: no\nrejection possible (0)", fontsize=5.5, color=MUTED, va="top", transform=ax.transAxes); ax.legend(frameon=False, loc="upper right", fontsize=5.5, bbox_to_anchor=(1.0, 0.8)); panel(ax, "a")
    ax = axes[1]
    order = {"circular (block = 300)": 300, "jitter, block 150": 150, "jitter, block 100": 100, "jitter, block 50": 50, "jitter, block 25": 25, "jitter, block 10": 10}
    rg = rg.assign(block=rg["null"].map(order))
    for ell, c in zip((15, 40, 100, 300), (ORANGE, PLUM, AQUA, BLUE)):
        s = rg[rg["regime segment length"] == ell].sort_values("block")
        ax.plot(s.block, s["share with p<=0.01"], marker="o", ms=3, lw=1, color=c, label=f"regime {ell} steps")
    ax.axhline(0.01, color=MUTED, lw=0.8, ls=":")
    plain_log(ax, [10, 25, 50, 100, 300])
    ax.set_ylim(0, 1.5); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0]); ax.set_xlabel("block length"); ax.set_ylabel("share with p ≤ 0.01"); ax.legend(frameon=False, loc="upper center", ncol=2, fontsize=5.5, columnspacing=0.8, handlelength=1.2); panel(ax, "b")
    ax = axes[2]
    for eta, mk, ls in ((0.3, "o", "-"), (0.1, "s", "--")):
        s = km[km.eta == eta].dropna(subset=["K at power 1/2, family-wise rejection (simulated)"])
        ax.plot(s.N, s["K at power 1/2, family-wise rejection (simulated)"], marker=mk, ms=3, lw=1, ls=ls, color=BLUE, label=f"flag, η = {eta}")
        ax.plot(s.N, s["K at power 1/2, family-wise rejection (formula)"], lw=0.8, ls=":", color=BLUE)
        s2 = km[km.eta == eta]
        ax.plot(s2.N, s2["K at catch@5 = 1/2 (simulated)"], marker=mk, ms=3, lw=1, ls=ls, color=ORANGE, label=f"top 5, η = {eta}")
    plain_log(ax, [60, 120, 240, 480, 960]); plain_log(ax, [4, 8, 16, 32, 64], "y")
    ax.set_ylim(2.5, 900); ax.set_xlabel("accounts N"); ax.set_ylabel("ring size at power 1/2"); ax.legend(frameon=False, loc="upper left", ncol=1, fontsize=5, handlelength=1.2, labelspacing=0.25); panel(ax, "c")
    fig.tight_layout(w_pad=0.7)
    fig.savefig(OUT / "jitter.pdf")


def fig_alloc():
    st = pd.read_csv(R / "allocation_stocks.csv")
    sh = pd.read_csv(R / "allocation_shown.csv")
    sm = pd.read_csv(R / "allocation_summary.csv")
    ep = pd.read_csv(R / "allocation_episodes.csv")
    fig, axes = plt.subplots(1, 3, figsize=(5.15, 2.35))
    ax = axes[0]
    for N, c in zip((100, 400, 1000, 2500), (BLUE, AQUA, PLUM, ORANGE)):
        r = ep[ep.n_noise == N]["rank"].to_numpy()
        bs = np.unique(np.round(np.geomspace(1, N / 2, 25)).astype(int))
        ax.plot(bs, [(r <= b).mean() for b in bs], color=c, lw=1.1, label=f"N = {N}")
        S = float(st[st.N_w == N]["S scaling law"].iloc[0])
        Q = 1 - (1 - norm.cdf(S + norm.ppf(np.clip(bs / N, 1e-9, 1 - 1e-9)))) ** 8
        ax.plot(bs, Q, color=c, lw=0.8, ls=":")
    ax.axhline(0.2, color=MUTED, lw=0.6, ls="--")
    plain_log(ax, [1, 10, 100, 1000]); ax.set_xlabel("accounts inspected b"); ax.set_ylabel("ring caught"); ax.legend(frameon=False, loc="upper left"); panel(ax, "a")
    ax = axes[1]
    s = sh[(sh.m == 5)]
    names = [("uniform", MUTED, "uniform"), ("proportional to N", AQUA, "∝ N"), ("rule, signal from scaling law", BLUE, "rule"), ("oracle (empirical curves)", ORANGE, "oracle")]
    xs = np.arange(s.n_noise.nunique())
    for i, (nm, c, lab) in enumerate(names):
        t = s[s.allocation == nm].sort_values("N_w")
        ax.bar(xs + (i - 1.5) * 0.2, t.b_w, 0.2, color=c, label=lab)
    ax.set_xticks(xs); ax.set_xticklabels(sorted(s.N_w.unique().astype(int)), rotation=60)
    ax.set_yscale("symlog", linthresh=1); ax.set_xlabel("accounts in the stock"); ax.set_ylabel("inspected per period"); ax.legend(frameon=False, loc="upper left", ncol=2); panel(ax, "b")
    ax = axes[2]
    for nm, c, lab in names:
        t = sm[(sm.m == 5) & (sm.allocation == nm)].sort_values("capacity C")
        ax.plot(t["capacity C"], t["mean"] / 1e3, color=c, lw=1.1, label=lab)
        ax.fill_between(t["capacity C"], (t["mean"] - t["std"]) / 1e3, (t["mean"] + t["std"]) / 1e3, color=c, alpha=0.12, lw=0)
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_xscale("log"); ax.set_xticks([16, 64, 256, 1024]); ax.set_xticklabels([16, 64, 256, 1024])
    ax.set_xlabel("total capacity C"); ax.set_ylabel("ring's best net benefit (k)"); panel(ax, "c")
    fig.tight_layout(w_pad=0.7)
    fig.savefig(OUT / "alloc.pdf")


if __name__ == "__main__":
    which = sys.argv[1:] or ["jitter", "alloc"]
    for w in which:
        {"jitter": fig_jitter, "alloc": fig_alloc}[w]()
        print("done", w)
