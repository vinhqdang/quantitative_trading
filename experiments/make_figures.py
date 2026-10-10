"""Figures for the paper, drawn from the CSV outputs in results/."""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd

R = Path("results")
OUT = Path("paper/figures")
OUT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, AQUA, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "text.color": INK,
                     "pdf.fonttype": 42, "figure.dpi": 150})


def parse(s: str):
    m = re.match(r"([\d.]+) \[([\d.]+), ([\d.]+)\]", str(s))
    return tuple(float(x) for x in m.groups())


def fig_robust():
    df = pd.read_csv(R / "ring_robust.csv")
    scen = list(dict.fromkeys(df.scenario))
    det = [("coincidence, unsigned (no labels)", "unsigned test (no labels)", ORANGE, "s"),
           ("coincidence, signed (no labels)", "signed test (no labels)", BLUE, "o"),
           ("gradient boosting (trained with labels, clean market)", "gradient boosting (labels)", MUTED, "D")]
    fig, ax = plt.subplots(figsize=(5.4, 2.7))
    w = 0.26
    for k, (name, label, col, mk) in enumerate(det):
        vals = [parse(df[(df.scenario == s) & (df.detector == name)]["catch@5"].iloc[0]) for s in scen]
        x = np.arange(len(scen)) + (k - 1) * w
        m = np.array([v[0] for v in vals])
        err = np.array([[v[0] - v[1] for v in vals], [v[2] - v[0] for v in vals]])
        ax.bar(x, m, w * 0.92, color=col, label=label, hatch=["//", "", ".."][k], edgecolor="white", linewidth=0.6)
        ax.errorbar(x, m, yerr=err, fmt="none", ecolor=INK, elinewidth=0.7, capsize=1.5)
    ax.set_xticks(np.arange(len(scen)))
    ax.set_xticklabels([s.replace("+ ", "+\n").replace("all three", "all three\ngroups") for s in scen])
    ax.set_ylabel("ring caught in top-5 of a window")
    ax.set_ylim(0, 1.08)
    ax.axhline(5 / 120, color=MUTED, lw=0.6, ls=":")
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=7, ncol=3, columnspacing=1.0, handlelength=1.4)
    fig.tight_layout()
    fig.savefig(OUT / "robust.pdf")


def fig_sensitivity():
    df = pd.read_csv(R / "ring_ablation.csv")
    fig, axes = plt.subplots(1, 3, figsize=(6.4, 2.2))
    specs = [("noise traders (accounts)", "accounts per window", "accounts per window", True),
             ("ring size K", None, "ring size K", False), ("ring push probability", None, "push probability", False)]
    for ax, (factor, xcol, xl, log) in zip(axes, specs):
        g = df[df.factor == factor]
        x = g[xcol].to_numpy() if xcol else g.level.astype(float).to_numpy()
        for col, key, mk, lab in ((BLUE, "catch@5", "o", "top 5"), (ORANGE, "catch@1", "s", "top 1")):
            v = [parse(s) for s in g[key]]
            ax.errorbar(x, [a[0] for a in v], yerr=[[a[0] - a[1] for a in v], [a[2] - a[0] for a in v]], color=col, marker=mk,
                        ms=3, lw=1, capsize=1.5, elinewidth=0.6, label=lab)
        ax.set_xlabel(xl)
        ax.set_ylim(0, 1.05)
        if log:
            ax.set_xscale("log")
            ax.set_xticks([100, 200, 400, 800])
            ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
            ax.minorticks_off()
    axes[0].set_ylabel("ring caught")
    axes[0].legend(frameon=False, fontsize=7, loc="lower left")
    for a, t in zip(axes, "abc"):
        a.set_title(f"({t})", loc="left", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "sensitivity.pdf")


def fig_pump():
    p = pd.read_csv(R / "pump_profile.csv")
    fig, axes = plt.subplots(1, 2, figsize=(5.6, 2.2), sharex=True)
    for ax, (series, col, lab) in zip(axes, (("volume", BLUE, "standardised volume"), ("buy imbalance", ORANGE, "standardised buy imbalance"))):
        g = p[p.series == series].sort_values("minute")
        ax.fill_between(g.minute / 60, g.lo, g.hi, color=col, alpha=0.25, lw=0)
        ax.plot(g.minute / 60, g["mean"], color=col, lw=1.2)
        ax.axvline(0, color=MUTED, lw=0.7, ls="--")
        ax.axhline(0, color=MUTED, lw=0.5)
        ax.set_xlabel("hours relative to the pump")
        ax.set_ylabel(lab)
    axes[0].text(0.06, 0.04, "pump", color=MUTED, fontsize=7, transform=axes[0].get_xaxis_transform())
    fig.tight_layout()
    fig.savefig(OUT / "pump.pdf")


def fig_policy():
    df = pd.read_csv(R / "vn_cross.csv")
    labels = {"no price band": "no price band", "band 7% (HOSE today)": "band 7% (HOSE today)", "band 10%": "band 10%", "band 15%": "band 15%",
              "band 7% + block at 60-step mean": "band 7% + block price,\n60-step mean", "band 7% + block at 240-step mean": "band 7% + block price,\n240-step mean (1 day)",
              "band 7% + inspect 1 per window": "band 7% + inspect\n1 account per window", "band 7% + inspect 3 per window": "band 7% + inspect\n3 accounts per window"}
    fig, ax = plt.subplots(figsize=(5.4, 2.9))
    y = np.arange(len(df))[::-1]
    cols = [BLUE if "inspect" not in s else ORANGE for s in df.scenario]
    ax.barh(y, df.gain / 1e3, xerr=df["gain se"] / 1e3, color=cols, height=0.6, ecolor=INK, error_kw={"elinewidth": 0.7, "capsize": 2})
    ax.set_yticks(y)
    ax.set_yticklabels([labels[s] for s in df.scenario], fontsize=7)
    ax.set_xlabel("best-responding ring's gain (thousand tick-lots, mean ± s.e.)")
    ax.axvline(0, color=MUTED, lw=0.6)
    for yi, (_, r) in zip(y, df.iterrows()):
        if "caught" in r and pd.notna(r["caught"]):
            ax.text(r.gain / 1e3 + r["gain se"] / 1e3 + 2, yi, f"caught {r['caught']:.0%}", va="center", fontsize=7, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "policy.pdf")


def fig_ensemble():
    """Ring gain relative to its gain with no policy, one dot per calibrated market."""
    fams = [("", "index-level markets (daily volatility 0.9-1.4%)", BLUE), ("_stock", "stock-level markets (daily volatility 1.8-2.8%)", ORANGE)]
    fams = [f for f in fams if (R / f"vn_ensemble{f[0]}.csv").exists()]
    if not fams:
        return
    labels = ["no price band", "band 7% (HOSE today)", "band 7% + block at 60-step mean", "band 7% + block at 240-step mean",
              "band 7% + inspect 1 per window", "band 7% + inspect 3 per window"]
    short = ["no band", "band 7%\n(today)", "block price\n60-step mean", "block price\n240-step mean", "inspect 1\nper window", "inspect 3\nper window"]
    fig, ax = plt.subplots(figsize=(6.2, 2.9))
    rng = np.random.default_rng(0)
    for k, (tag, lab, col) in enumerate(fams):
        df = pd.read_csv(R / f"vn_ensemble{tag}.csv")
        base = df[df.policy == "no price band"].set_index("market").gain
        df["ratio"] = df.apply(lambda r: r.gain / base[r.market] if r.market in base and base[r.market] > 0 else np.nan, axis=1)
        for i, pol in enumerate(labels):
            v = df[df.policy == pol].ratio.dropna().to_numpy()
            x = i + (k - (len(fams) - 1) / 2) * 0.3
            ax.scatter(x + rng.uniform(-0.05, 0.05, len(v)), v, s=14, color=col, alpha=0.8, label=lab if i == 0 else None,
                       marker="o" if k == 0 else "s", edgecolor="white", linewidth=0.4)
            if len(v):
                ax.hlines(np.median(v), x - 0.12, x + 0.12, color=INK, lw=1.2)
    ax.axhline(1, color=MUTED, lw=0.6, ls=":")
    ax.axhline(0, color=MUTED, lw=0.5)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(short, fontsize=7)
    ax.set_ylabel("ring gain / gain with no policy")
    ax.legend(frameon=False, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "ensemble.pdf")


if __name__ == "__main__":
    fig_robust(); fig_sensitivity(); fig_pump(); fig_policy(); fig_ensemble()
    print(sorted(p.name for p in OUT.glob("*.pdf")))
