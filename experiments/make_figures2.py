"""Additional figures: theory checks, deterrence frontier, block rule, trade-offs, real-data event studies, schematic.

All numbers come from CSV files in results/ produced by the experiment scripts.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).parent))
R = Path("results")
OUT = Path("paper/figures")
OUT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, AQUA, INK, MUTED, PLUM = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#8b4f9f"
plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "text.color": INK,
                     "pdf.fonttype": 42, "figure.dpi": 150})


def panel(ax, letter):
    ax.text(-0.14, 1.04, f"({letter})", transform=ax.transAxes, fontsize=8, fontweight="bold")


def fig_framework():
    fig, ax = plt.subplots(figsize=(6.6, 2.5))
    ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.axis("off")
    boxes = [(2, 22, 22, 14, "Calibrated market\nlimit order book,\nhonest agents and groups", BLUE),
             (28, 22, 22, 14, "Ring of accounts\nbest-responds to\neach rule (strategy set)", ORANGE),
             (54, 22, 22, 14, "Label-free screening\ncoincidence test,\ntop-B inspection, fine m", AQUA),
             (78, 22, 20, 14, "Policy levers\nband, block price,\ninspection, order rules", PLUM),
             (2, 2, 30, 14, "Family of calibrated markets\n(index level, stock level;\nrejection on real moments)", BLUE),
             (36, 2, 30, 14, "Theory\nvalidity, power law, deterrence\nfrontier, block-rule law", MUTED),
             (70, 2, 28, 14, "Public real data\ncases, tick reform, pump\nevents, prices (no accounts)", INK)]
    for x, y, w, h, t, c in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5", fc="white", ec=c, lw=1.2))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=6.8)
    for (x0, y0, x1, y1) in [(24.6, 29, 27.6, 29), (50.6, 29, 53.6, 29), (76.6, 29, 77.6, 29), (13, 17, 13, 21.4), (51, 17, 62, 21.4), (84, 17, 88, 21.4)]:
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=7, color=MUTED, lw=0.9))
    fig.savefig(OUT / "framework.pdf", bbox_inches="tight")


def fig_theory():
    v = pd.read_csv(R / "theory_validity.csv")
    b = pd.read_csv(R / "theory_budget.csv")
    p = pd.read_csv(R / "theory_power.csv")
    fig, axes = plt.subplots(1, 4, figsize=(6.8, 2.1))
    ax = axes[0]
    styles = {"iid Gaussian": (BLUE, "o", "-"), "iid Poisson counts": (AQUA, "s", "-"),
              "bursty (shared regime), signed": (ORANGE, "D", "--"), "bursty (shared regime), unsigned": (PLUM, "^", "--")}
    for k, g in v.groupby("flows", sort=False):
        c, m, ls = styles[k]
        ax.plot(g.alpha, g["rejection rate"], color=c, marker=m, ms=3, ls=ls, lw=1,
                label=k.replace("bursty (shared regime), ", "bursty, ").replace("iid ", ""))
    ax.plot([0, 0.1], [0, 0.1], color=MUTED, lw=0.6, ls=":")
    ax.set_xlabel("nominal level"); ax.set_ylabel("rejection rate"); ax.set_xlim(0, 0.105); ax.set_ylim(0, 1.0)
    ax.legend(frameon=False, fontsize=5.5, loc="upper left")
    panel(ax, "a")
    ax = axes[1]
    for a, c, mk in [(0.01, BLUE, "o"), (0.05, ORANGE, "s")]:
        g = b[b.alpha == a]
        ax.plot(g["bound N*alpha"], g["mean flagged per window"], color=c, marker=mk, ms=3, lw=0, label=f"level {a}")
    mx = float(b["bound N*alpha"].max())
    ax.plot([0, mx], [0, mx], color=MUTED, lw=0.6, ls=":")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel(r"bound $N\alpha$"); ax.set_ylabel("honest accounts flagged\nper window")
    ax.legend(frameon=False, fontsize=6)
    panel(ax, "b")
    ax = axes[2]
    x = p["mean z ring"] - p["honest z mean"]
    for N, mk in zip(sorted(p.N.unique()), ["o", "s", "^", "D"]):
        g = p[p.N == N]
        ax.plot(g.rho_model, g["mean z ring"] - g["honest z mean"], marker=mk, ms=3, lw=0, color=BLUE, mfc="white" if N in (200, 800) else BLUE, label=f"N={int(N)}")
    c = float(p["sqrt(T_eff) fitted"].iloc[0])
    xs = np.linspace(0, p.rho_model.max() * 1.05, 20)
    ax.plot(xs, c * xs, color=ORANGE, lw=1, label=rf"slope {c:.1f}")
    ax.set_xlabel(r"model correlation $\rho$"); ax.set_ylabel("mean shift of the statistic")
    ax.legend(frameon=False, fontsize=5, ncol=1, loc="upper left")
    panel(ax, "c")
    ax = axes[3]
    ax.plot(p["catch@5"], p["catch@5 predicted"], marker="o", ms=3, lw=0, color=BLUE)
    ax.plot([0, 1], [0, 1], color=MUTED, lw=0.6, ls=":")
    ax.set_xlabel("simulated catch@5"); ax.set_ylabel("predicted catch@5")
    ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.03, 1.03)
    panel(ax, "d")
    fig.tight_layout(w_pad=0.8)
    fig.savefig(OUT / "theory.pdf")


def fig_power_abm():
    fit = pd.read_csv(R / "power_law_fit.csv")
    grid = pd.read_csv(R / "power_law_grid.csv")
    fig, axes = plt.subplots(1, 4, figsize=(6.8, 2.1))
    ax = axes[0]
    for K, c, ls in [(4, ORANGE, "--"), (12, BLUE, "-"), (32, AQUA, "-.")]:
        g = grid[grid.K == K]
        ax.plot(g.N, g["catch@5 (model)"], color=c, ls=ls, lw=1, label=f"K={K}")
    g = fit[fit.sweep == "accounts"]
    ax.plot(g.N, g.catch, "o", color=INK, ms=3.5, label="agent-based")
    ax.plot(g.N, g["predicted (held-out sweep)"], "x", color=ORANGE, ms=4, label="held-out prediction")
    ax.set_xscale("log"); ax.set_xlabel("accounts per window N"); ax.set_ylabel("catch@5"); ax.set_ylim(0, 1.03)
    ax.legend(frameon=False, fontsize=5.5, loc="lower left"); panel(ax, "a")
    ax = axes[1]
    g = fit[fit.sweep == "ring size"]
    ax.plot(g.K, g.catch, "o", color=INK, ms=3.5, label="agent-based")
    ax.plot(g.K, g.predicted, "-", color=BLUE, lw=1, label="model")
    ax.plot(g.K, g["predicted (held-out sweep)"], "x", color=ORANGE, ms=4, label="held-out")
    ax.set_xscale("log"); ax.set_xlabel("ring size K"); ax.set_ylim(0, 1.03); ax.legend(frameon=False, fontsize=5.5, loc="lower right")
    panel(ax, "b")
    ax = axes[2]
    g = fit[fit.sweep == "push probability"]
    ax.plot(g.push, g.catch, "o", color=INK, ms=3.5)
    ax.plot(g.push, g.predicted, "-", color=BLUE, lw=1)
    ax.plot(g.push, g["predicted (held-out sweep)"], "x", color=ORANGE, ms=4)
    ax.set_xlabel("push probability"); ax.set_ylim(0, 1.03); panel(ax, "c")
    ax = axes[3]
    piv = grid.pivot(index="K", columns="N", values="catch@5 (model)")
    im = ax.imshow(piv.values, origin="lower", aspect="auto", cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(piv.columns))); ax.set_xticklabels([int(x) for x in piv.columns], fontsize=6)
    ax.set_yticks(range(len(piv.index))); ax.set_yticklabels([int(x) for x in piv.index], fontsize=6)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            ax.text(j, i, f"{piv.values[i, j]:.1f}", ha="center", va="center", fontsize=5, color="white" if piv.values[i, j] > 0.6 else INK)
    ax.set_xlabel("accounts per window N"); ax.set_ylabel("ring size K"); panel(ax, "d")
    fig.tight_layout(w_pad=0.8)
    fig.savefig(OUT / "power_abm.pdf")


def required_inspection(N, K, W, m, s0=1.2, push=0.8, T_scale=100.0):
    """B*(N): smallest B with 1 - (1 - r(B))^W >= 1/m, r = 1 - (1 - q_B)^K, q_B = Phi(S - Phi^{-1}(1 - B/N)), S = s0 (100/N)^(1/2)."""
    S = s0 * push / 0.8 * np.sqrt(T_scale / N)
    r_star = 1 - (1 - 1 / m) ** (1 / W)
    q_star = 1 - (1 - r_star) ** (1 / K)
    return N * norm.cdf(norm.ppf(q_star) - S)


def detection_prob(N, K, W, B, s0=1.2, push=0.8):
    """Probability that some member is among the B top-ranked accounts in some of W windows (members and windows treated as independent)."""
    S = s0 * push / 0.8 * np.sqrt(100.0 / N)
    q = norm.cdf(S - norm.ppf(1 - np.minimum(B, N - 1e-9) / N))
    r = 1 - (1 - q) ** K
    return 1 - (1 - r) ** W


def fig_frontier():
    par = pd.read_csv(R / "power_law_params.csv").iloc[0]
    s0 = float(par.s0)
    fig, axes = plt.subplots(1, 3, figsize=(6.8, 2.3))
    ax = axes[0]
    Bs = np.geomspace(0.3, 30, 80)
    for (K, W), c, ls in [((3, 4), ORANGE, "--"), ((12, 8), BLUE, "-")]:
        ax.plot(Bs, detection_prob(600, K, W, Bs, s0), color=c, ls=ls, lw=1.1, label=f"model: K={K}, {W} windows")
    for m, ls in [(5, ":"), (10, "-.")]:
        ax.axhline(1 / m, color=MUTED, lw=0.7, ls=ls)
        ax.text(0.32, 1 / m + 0.015, f"1/m, m={m}", fontsize=5.5, color=MUTED)
    for fam, f, mk, c in [("index level", "vn_ensemble.csv", "o", INK), ("stock level", "vn_ensemble_stock.csv", "s", PLUM)]:
        e = pd.read_csv(R / f)
        for B, lab in [(1, "inspect 1 per window"), (3, "inspect 3 per window")]:
            v = e[e.policy == f"band 7% + {lab}"].caught.median()
            ax.plot(B, v, mk, color=c, ms=4.5, label=f"simulated best response, {fam}" if B == 1 else None)
    ax.set_xscale("log"); ax.set_xlabel("accounts inspected per window B"); ax.set_ylabel("probability that the ring is caught"); ax.set_ylim(0, 1.03)
    ax.legend(frameon=False, fontsize=5, loc="upper left"); panel(ax, "a")
    ax = axes[1]
    Ns = np.geomspace(60, 3000, 60)
    for m, c, ls in [(5, BLUE, "-"), (10, ORANGE, "--")]:
        ax.plot(Ns, required_inspection(Ns, 3, 4, m, s0), color=c, ls=ls, lw=1.1, label=f"screening, fine {m}x gain")
        ax.plot(Ns, required_inspection(Ns, 3, 4, m, 0.0), color=c, ls=ls, lw=0.7, alpha=0.5)
    ax.plot([], [], color=MUTED, lw=0.7, alpha=0.6, label="random inspection (thin)")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("accounts per window N"); ax.set_ylabel("accounts inspected per window\nfor deterrence (K=3, 4 windows)")
    ax.legend(frameon=False, fontsize=5.5, loc="upper left"); panel(ax, "b")
    ax = axes[2]
    for (K, W), c, ls in [((3, 4), BLUE, "-"), ((12, 8), ORANGE, "--"), ((30, 24), AQUA, "-.")]:
        ax.plot(Ns, required_inspection(Ns, K, W, 5, 0.0) / required_inspection(Ns, K, W, 5, s0), color=c, ls=ls, lw=1.1, label=f"K={K}, {W} windows")
    ax.axhline(1, color=MUTED, lw=0.6, ls=":")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("accounts per window N"); ax.set_ylabel("inspections saved by screening\n(random / screening, m=5)")
    ax.legend(frameon=False, fontsize=5.5); panel(ax, "c")
    fig.tight_layout(w_pad=0.8)
    fig.savefig(OUT / "frontier.pdf")


def fig_tradeoff():
    d = pd.read_csv(R / "policy_matrix.csv")
    base = d.iloc[0]
    d = d.iloc[1:].copy()
    d["dvol"] = (d.vol / base.vol - 1) * 100
    d["dspread"] = (d.spread / base.spread - 1) * 100
    d["dspoof"] = (d["spoof profit"] / base["spoof profit"] - 1) * 100
    d["dring"] = (d["ring gain"] / base["ring gain"] - 1) * 100
    d["dpump"] = (d["pump impact"] / base["pump impact"] - 1) * 100
    fig, axes = plt.subplots(1, 3, figsize=(6.8, 2.3))
    marks = ["o", "s", "^", "D", "v", "P", "X", "*"]
    cols = [BLUE, ORANGE, AQUA, PLUM, MUTED, INK, "#c9a227", "#d13b8a"]
    for ax, (yk, yl, letter) in zip(axes, [("dspoof", "spoofing profit (% change)", "a"), ("dpump", "pump impact (% change)", "b"), ("dring", "ring gain (% change)", "c")]):
        for i, (_, r) in enumerate(d.iterrows()):
            ax.plot(r.dvol, r[yk], marks[i % len(marks)], color=cols[i % len(cols)], ms=4.5, label=r.policy)
        ax.axhline(0, color=MUTED, lw=0.5); ax.axvline(0, color=MUTED, lw=0.5)
        ax.set_xlabel("volatility (% change)"); ax.set_ylabel(yl); panel(ax, letter)
    axes[0].legend(frameon=False, fontsize=5, loc="upper left", ncol=1, handletextpad=0.2)
    fig.tight_layout(w_pad=0.8)
    fig.savefig(OUT / "tradeoff.pdf")


def fig_cases():
    ev = pd.read_csv(R / "case_eventstudy.csv")
    mean = pd.read_csv(R / "case_eventstudy_mean.csv")
    fig, axes = plt.subplots(1, 3, figsize=(6.8, 2.3))
    ax = axes[0]
    for t, g in ev.groupby("ticker"):
        ax.plot(g.rel_day, g.car, color=MUTED, lw=0.5, alpha=0.7)
    ax.plot(mean.rel_day, mean.car, color=BLUE, lw=1.6, label="mean of cases")
    ax.axvline(0, color=INK, lw=0.6, ls=":"); ax.set_ylim(-0.6, 2.2)
    ax.set_xlabel("trading days from start of period"); ax.set_ylabel("cumulative market-adjusted return"); ax.legend(frameon=False, fontsize=6, loc="upper left"); panel(ax, "a")
    ax = axes[1]
    for col, c, ls, lab in [("pct_return_score", BLUE, "-", "abnormal return"), ("pct_surge_score", ORANGE, "--", "volume surge"), ("pct_fisher", AQUA, "-.", "combined score")]:
        ax.plot(mean.rel_day, mean[col], color=c, ls=ls, lw=1.2, label=lab)
    ax.axhline(0.5, color=MUTED, lw=0.5, ls=":"); ax.axvline(0, color=INK, lw=0.6, ls=":")
    ax.set_xlabel("trading days from start of period"); ax.set_ylabel("mean percentile among stocks"); ax.set_ylim(0.2, 1.0)
    ax.legend(frameon=False, fontsize=5.5, loc="lower right"); panel(ax, "b")
    ax = axes[2]
    pers = ev.groupby("ticker").period_days.first()
    for t, g in ev.groupby("ticker"):
        ax.plot(g.rel_day, g.pct_return_score.rolling(5, min_periods=1).mean() + 0.0, lw=0.6, color=MUTED, alpha=0.7)
    ax.plot(mean.rel_day, mean.pct_return_score.rolling(5, min_periods=1).mean(), color=BLUE, lw=1.6)
    ax.axhline(0.99, color=ORANGE, lw=0.6, ls="--"); ax.axvline(0, color=INK, lw=0.6, ls=":")
    ax.set_xlabel("trading days from start of period"); ax.set_ylabel("abnormal-return percentile\n(5-day mean)"); panel(ax, "c")
    fig.tight_layout(w_pad=0.8)
    fig.savefig(OUT / "cases.pdf")


def fig_tick():
    es = pd.read_csv(R / "tick_reform_eventstudy.csv")
    sim = pd.read_csv(R / "tick_sim.csv")
    did = pd.read_csv(R / "tick_reform_did.csv")
    fig, axes = plt.subplots(1, 3, figsize=(6.8, 2.2))
    ax = axes[0]
    ax.plot(es.week, es.HOSE, color=BLUE, marker="o", ms=3, lw=1, label="HOSE")
    ax.plot(es.week, es.controls, color=ORANGE, marker="s", ms=3, lw=1, ls="--", label="HNX and UPCoM")
    ax.axvline(0, color=INK, lw=0.6, ls=":"); ax.axhline(0, color=MUTED, lw=0.5)
    ax.set_xlabel("weeks from the reform"); ax.set_ylabel("spread estimate vs pre-reform\n(percentage points)"); ax.legend(frameon=False, fontsize=6); panel(ax, "a")
    for ax, outcome, letter in [(axes[1], "zero-return share", "b"), (axes[2], "CS spread (%)", "c")]:
        s = sim[sim.outcome == outcome]
        rel = [(r["tick reduction"], r.change / r["level before"] * 100) for _, r in s.iterrows()]
        real = did[did.outcome == outcome].iloc[0]
        x = np.arange(len(rel))
        ax.bar(x, [v for _, v in rel], 0.55, color=BLUE, hatch="//", edgecolor="white", label="simulated tick cut")
        ax.axhline(real.DiD / real["pre-period HOSE mean"] * 100, color=ORANGE, lw=1.4, ls="--", label="observed (HOSE vs controls)")
        lo, hi = real.ci_lo / real["pre-period HOSE mean"] * 100, real.ci_hi / real["pre-period HOSE mean"] * 100
        ax.axhspan(lo, hi, color=ORANGE, alpha=0.15, lw=0)
        ax.set_xticks(x); ax.set_xticklabels([r.replace(" -> ", "→") for r, _ in rel])
        ax.set_ylabel("change (% of level before)"); ax.set_xlabel("tick reduction (times)")
        panel(ax, letter)
    axes[1].legend(frameon=False, fontsize=5.5, loc="lower left")
    fig.tight_layout(w_pad=0.8)
    fig.savefig(OUT / "tick.pdf")


def fig_roc():
    from sklearn.metrics import precision_recall_curve, roc_curve
    scen = [("clean", "clean"), ("plus_MM_desks", "+ market-making desks"), ("all_three", "all three honest groups")]
    dets = [("z_unsigned", "unsigned test", ORANGE, "--"), ("z_signed", "signed test", BLUE, "-"), ("gbm", "boosting (labels)", MUTED, "-."),
            ("iforest", "isolation forest", AQUA, ":")]
    fig, axes = plt.subplots(2, 3, figsize=(6.8, 4.1))
    for j, (fn, title) in enumerate(scen):
        d = pd.read_csv(R / f"ring_robust_scores_{fn}.csv.gz")
        for col, lab, c, ls in dets:
            fpr, tpr, _ = roc_curve(d.y, d[col])
            axes[0, j].plot(fpr, tpr, color=c, ls=ls, lw=1.1, label=lab)
            pr, rc, _ = precision_recall_curve(d.y, d[col])
            axes[1, j].plot(rc, pr, color=c, ls=ls, lw=1.1)
        axes[0, j].plot([0, 1], [0, 1], color=MUTED, lw=0.5, ls=":")
        axes[0, j].set_xlabel("false-positive rate"); axes[1, j].set_xlabel("recall")
        axes[0, j].set_xscale("symlog", linthresh=0.01); axes[0, j].set_xlim(0, 1)
        axes[0, j].set_title(title, fontsize=7.5)
        panel(axes[0, j], "abc"[j]); panel(axes[1, j], "def"[j])
    axes[0, 0].set_ylabel("true-positive rate"); axes[1, 0].set_ylabel("precision")
    axes[0, 0].legend(frameon=False, fontsize=5.5, loc="lower right")
    fig.tight_layout(h_pad=1.0, w_pad=0.8)
    fig.savefig(OUT / "roc.pdf")


def fig_block():
    d = pd.read_csv(R / "block_static.csv")
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.4), sharey=True)
    for ax, (fam, letter) in zip(axes, [("index level", "a"), ("stock level", "b")]):
        g = d[d.family == fam]
        for mk, gm in g.groupby("market"):
            ax.plot(gm.L, gm["block term ratio (static)"], color=ORANGE, lw=0.5, alpha=0.35)
        med = g.groupby("L")[["static ratio", "adaptive ratio", "block term ratio (static)", "linear-ramp law"]].median()
        ax.plot(med.index, med["block term ratio (static)"], color=ORANGE, lw=1.5, marker="s", ms=3, label="block term (median)")
        ax.plot(med.index, med["linear-ramp law"], color=INK, lw=1.0, ls=":", label="linear-ramp law")
        ax.plot(med.index, med["static ratio"], color=AQUA, lw=1.2, ls="--", marker="^", ms=3, label="total gain, ring keeps strategy")
        ax.plot(med.index, med["adaptive ratio"], color=BLUE, lw=1.4, marker="o", ms=3, label="total gain, ring re-selects")
        ax.set_xscale("log"); ax.set_xlabel("reference window L (steps; 240 = one day)")
        ax.axhline(0, color=MUTED, lw=0.5); ax.set_ylim(-0.5, 1.12); panel(ax, letter)
    axes[0].set_ylabel("share retained relative to last price")
    axes[0].legend(frameon=False, fontsize=5.2, loc="lower left")
    fig.tight_layout(w_pad=0.8)
    fig.savefig(OUT / "block.pdf")


def fig_real_accounts():
    summ = pd.read_csv(R / "real_accounts_summary.csv")
    cal = pd.read_csv(R / "real_accounts_calibration.csv.gz")
    pl = pd.read_csv(R / "real_accounts_planted2.csv")
    fig, axes = plt.subplots(2, 3, figsize=(6.8, 4.2))
    ax = axes[0, 0]
    g = summ[(summ.data == "orders SOL (L4)") & summ.accounts.isin(["3-9", "10-99", ">=100"])]
    x = np.arange(len(g)); w = 0.38
    ax.bar(x - w / 2, g["unsigned p<=0.01"], w, color=ORANGE, hatch="//", edgecolor="white", label="unsigned")
    ax.bar(x + w / 2, g["signed p<=0.01"], w, color=BLUE, edgecolor="white", label="signed")
    ax.axhline(0.01, color=INK, lw=0.7, ls=":")
    ax.set_xticks(x); ax.set_xticklabels(g.accounts); ax.set_xlabel("submissions in the window"); ax.set_ylabel("share with p \u2264 0.01")
    ax.legend(frameon=False, fontsize=6); panel(ax, "a")
    ax = axes[0, 1]
    o = cal[cal.data == "orders SOL (L4)"]
    ax.hist(o.p_signed, bins=20, range=(0, 1), color=BLUE, alpha=0.85, edgecolor="white", linewidth=0.4)
    ax.axhline(len(o) / 20, color=INK, lw=0.7, ls=":")
    ax.set_xlabel("p-value (signed test)"); ax.set_ylabel("account-windows"); panel(ax, "b")
    ax = axes[0, 2]
    q = pl[pl.sweep == "orders per push"]
    ax.plot(np.maximum(q.q, 1), q["signed global@5"], "o-", color=BLUE, ms=3.5, lw=1.1, label="signed")
    ax.plot(np.maximum(q.q, 1), q["unsigned global@5"], "s--", color=ORANGE, ms=3.5, lw=1.1, label="unsigned")
    ax.set_xscale("log"); ax.set_xlabel("orders per member and push"); ax.set_ylabel("catch@5 of a planted ring"); ax.set_ylim(-0.03, 1.03)
    ax.legend(frameon=False, fontsize=6, loc="upper left"); panel(ax, "c")
    ax = axes[1, 0]
    q = pl[pl.sweep == "accounts"]
    ax.plot(q.N, q["signed global@5"], "o-", color=BLUE, ms=3.5, lw=1.1)
    ax.plot(q.N, q["unsigned global@5"], "s--", color=ORANGE, ms=3.5, lw=1.1)
    ax.set_xscale("log"); ax.set_xlabel("accounts per window N (real accounts dropped)"); ax.set_ylabel("catch@5"); ax.set_ylim(-0.03, 1.03); panel(ax, "d")
    ax = axes[1, 1]
    q = pl[pl.sweep == "ring size"]
    ax.plot(q.K, q["signed global@5"], "o-", color=BLUE, ms=3.5, lw=1.1)
    ax.plot(q.K, q["unsigned global@5"], "s--", color=ORANGE, ms=3.5, lw=1.1)
    ax.set_xscale("log"); ax.set_xlabel("ring size K"); ax.set_ylim(-0.03, 1.03); panel(ax, "e")
    ax = axes[1, 2]
    q = pl[pl.sweep == "pushes per window"]
    ax.plot(q.n_push, q["signed global@5"], "o-", color=BLUE, ms=3.5, lw=1.1)
    ax.plot(q.n_push, q["unsigned global@5"], "s--", color=ORANGE, ms=3.5, lw=1.1)
    ax.set_xscale("log"); ax.set_xlabel("pushes per window"); ax.set_ylim(-0.03, 1.03); panel(ax, "f")
    fig.tight_layout(h_pad=1.0, w_pad=0.8)
    fig.savefig(OUT / "real_accounts.pdf")


def fig_calib():
    """Calibration: simulated against real daily returns (QQ, absolute-return autocorrelation) and moments."""
    from scipy import stats as st
    import os
    base = Path(os.environ.get("MARKETSIM_DATA", "external_data")) / "data"
    idx = pd.read_csv(base / "x_keithvo_vnstockdata" / "HOSEVN301D.csv", usecols=["time", "close"])
    idx["t"] = pd.to_datetime(idx.time, unit="s")
    r_idx = np.log(idx.set_index("t").sort_index().close["2023-01-01":]).diff().dropna()
    sim = pd.read_csv(R / "calib_sim_daily.csv")
    mom = pd.read_csv(R / "calib_sim_moments.csv")
    real_stock = pd.read_csv(R / "calib_real_stock_returns.csv") if (R / "calib_real_stock_returns.csv").exists() else None
    fig, axes = plt.subplots(1, 4, figsize=(6.8, 2.2))
    def qq(ax, x, c, lab, mk):
        x = np.sort((x - x.mean()) / x.std())
        q = st.norm.ppf((np.arange(1, len(x) + 1) - 0.5) / len(x))
        ax.plot(q, x, mk, color=c, ms=2.2, label=lab)
    ax = axes[0]
    qq(ax, r_idx.to_numpy(), INK, "VN30 index (real)", "o")
    qq(ax, sim[sim.family == "index level"].ret.to_numpy(), BLUE, "simulated, index level", "s")
    ax.plot([-3, 3], [-3, 3], color=MUTED, lw=0.5, ls=":"); ax.set_xlabel("normal quantile"); ax.set_ylabel("standardised daily return")
    ax.legend(frameon=False, fontsize=5.5, loc="lower right"); panel(ax, "a")
    ax = axes[1]
    if real_stock is not None:
        qq(ax, real_stock.ret.to_numpy(), INK, "HOSE stocks, pooled (real)", "o")
    qq(ax, sim[sim.family == "stock level"].ret.to_numpy(), ORANGE, "simulated, stock level", "s")
    ax.plot([-3, 3], [-3, 3], color=MUTED, lw=0.5, ls=":"); ax.set_xlabel("normal quantile"); ax.legend(frameon=False, fontsize=5.5, loc="lower right"); panel(ax, "b")
    ax = axes[2]
    def pooled_acf(groups, nl=5):
        num = np.zeros(nl); den = 0.0
        for g in groups:
            a = g - g.mean(); den += (a * a).sum()
            for l in range(1, nl + 1):
                num[l - 1] += (a[:-l] * a[l:]).sum()
        return num / den
    lags = np.arange(1, 6)
    ax.plot(lags, pooled_acf([r_idx.to_numpy()]), "o-", color=INK, ms=3, lw=1, label="VN30 (real)")
    if (R / "calib_real_acf.csv").exists():
        ra = pd.read_csv(R / "calib_real_acf.csv")
        ax.plot(ra.lag, ra.iloc[:, 1], "^-", color=MUTED, ms=3, lw=1, label="HOSE stocks (real, mean)")
    for fam, c, mk in [("index level", BLUE, "s"), ("stock level", ORANGE, "D")]:
        ax.plot(lags, pooled_acf([g.ret.to_numpy() for _, g in sim[sim.family == fam].groupby("episode") if len(g) > 12]), mk + "--", color=c, ms=3, lw=1, label=f"simulated, {fam}")
    ax.axhline(0, color=MUTED, lw=0.5); ax.set_xlabel("lag (days)"); ax.set_ylabel("autocorrelation of daily returns"); ax.legend(frameon=False, fontsize=5.2); panel(ax, "c")
    ax = axes[3]
    labels = ["cancel\nshare", "retail\nshare", "spread\n(ticks)\n/10"]
    real_v = [0.318, 0.785, 0.1]
    sim_v = [mom[mom.family == "index level"].cancel_share.mean(), mom[mom.family == "index level"].retail_share.mean(), mom[mom.family == "index level"].spread_ticks.mean() / 10]
    x = np.arange(3); w = 0.36
    ax.bar(x - w / 2, real_v, w, color=INK, label="real"); ax.bar(x + w / 2, sim_v, w, color=BLUE, hatch="//", edgecolor="white", label="simulated")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=6); ax.set_ylim(0, 1.0); ax.legend(frameon=False, fontsize=5.5, loc="upper center", ncol=2); panel(ax, "d")
    fig.tight_layout(w_pad=0.8)
    fig.savefig(OUT / "calibration.pdf")


if __name__ == "__main__":
    which = sys.argv[1:] or ["framework", "theory", "power_abm", "frontier", "tradeoff", "cases", "tick", "roc", "block", "real_accounts"]
    for w in which:
        {"framework": fig_framework, "theory": fig_theory, "power_abm": fig_power_abm, "frontier": fig_frontier, "tradeoff": fig_tradeoff,
         "cases": fig_cases, "tick": fig_tick, "roc": fig_roc, "block": fig_block, "real_accounts": fig_real_accounts, "calib": fig_calib}[w]()
        print("done", w)
