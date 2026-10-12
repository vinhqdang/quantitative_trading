"""Tables for the real account-level experiments."""

from pathlib import Path

import pandas as pd

R, OUT = Path("results"), Path("paper/tables")

TOP = "\\begin{tabular}{%s}\n\\toprule\n"
BOT = "\n\\bottomrule\n\\end{tabular}\n"


def real_calibration():
    f = R / "real_accounts_summary.csv"
    if not f.exists():
        return
    d = pd.read_csv(f)
    head = r"data & accounts & account-windows & unsigned, $p\le0.01$ & signed, $p\le0.01$ & unsigned, $p\le0.05$ & signed, $p\le0.05$ \\"
    rows = [head, r"\midrule"]
    names = {"orders SOL (L4)": "order submissions, SOL", "fills BTC": "fills, BTC", "fills ETH": "fills, ETH", "fills HYPE": "fills, HYPE"}
    accs = {"3-9": "3--9 submissions", "10-99": "10--99", ">=100": r"$\ge100$", "all": r"all with $\ge3$", "two-sided": "both sides"}
    for _, r in d.iterrows():
        if r.data.startswith("fills") and r.accounts != "all":
            continue
        cells = [names[r.data], accs[r.accounts], str(int(r["n account-windows"])), f"{r['unsigned p<=0.01']:.3f}", f"{r['signed p<=0.01']:.3f}",
                 f"{r['unsigned p<=0.05']:.3f}", f"{r['signed p<=0.05']:.3f}"]
        rows.append(" & ".join(cells) + r" \\")
    (OUT / "real_calibration.tex").write_text(TOP % "llrrrrr" + "\n".join(rows) + BOT)


def real_planted():
    f = R / "real_accounts_planted2.csv"
    if not f.exists():
        return
    d = pd.read_csv(f)
    head = r"sweep & $N$ & $K$ & orders per push & pushes & unsigned @5 & signed @1 & signed @5 & signed @10 & members with $p\le0.01$ \\"
    rows = [head, r"\midrule"]
    for _, r in d.iterrows():
        cells = [r.sweep, str(int(r.N)), str(int(r.K)), str(int(r.q)), str(int(r.n_push)), f"{r['unsigned global@5']:.2f}", f"{r['signed global@1']:.2f}",
                 f"{r['signed global@5']:.2f}", f"{r['signed global@10']:.2f}", f"{r['member flagged p<=0.01 (signed)']:.2f}"]
        rows.append(" & ".join(cells) + r" \\")
    (OUT / "real_planted.tex").write_text(TOP % "lrrrrrrrrr" + "\n".join(rows) + BOT)


def calib_markets():
    f = R / "calib_markets.csv"
    if not f.exists():
        return
    d = pd.read_csv(f)
    head = r"family & market (draw) & volatility at acceptance (\%) & volatility, 16 episodes (\%) & cancel share & retail share & spread (ticks) \\"
    rows = [head, r"\midrule"]
    for _, r in d.iterrows():
        cells = [r.family, str(int(r.market)), f"{r['vol at acceptance (%)']:.2f}", f"{r['vol, 16-episode mean (%)']:.2f} ({r['vol s.e. (%)']:.2f})",
                 f"{r['cancel share']:.3f}", f"{r['retail share']:.3f}", f"{r['spread (ticks)']:.2f}"]
        rows.append(" & ".join(cells) + r" \\")
    (OUT / "calib_markets.tex").write_text(TOP % "llrrrrr" + "\n".join(rows) + BOT)


def block_size():
    f = R / "block_size_sensitivity.csv"
    if not f.exists():
        return
    d = pd.read_csv(f)
    rows = [r"& \multicolumn{3}{c}{index level} & \multicolumn{3}{c}{stock level} \\", r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}",
            r"block size (lots) & gain, last price & kept at $L=60$ & kept at $L=240$ & gain, last price & kept at $L=60$ & kept at $L=240$ \\", r"\midrule"]
    for b in sorted(d["block size (lots)"].unique()):
        cells = [str(int(b))]
        for fam in ("index level", "stock level"):
            r = d[(d["block size (lots)"] == b) & (d.family == fam)].iloc[0]
            cells += [f"{r['median gain, last-price reference'] / 1e3:.0f}k", f"{r['median share kept, L=60, ring keeps strategy']:.2f}", f"{r['median share kept, L=240, ring keeps strategy']:.2f}"]
        rows.append(" & ".join(cells) + r" \\")
    (OUT / "block_size.tex").write_text(TOP % "lrrrrrr" + "\n".join(rows) + BOT)


def transfer():
    f = R / "transfer.csv"
    if not f.exists():
        return
    d = pd.read_csv(f)
    names = {"label-free coincidence": "label-free test", "GBM trained on generic simulator": r"boosting, trained on the generic simulator",
             "GBM trained in this market": r"boosting, trained in this market"}
    rows = [r"market family (markets) & detector & catch@1 & catch@3 & catch@5 & catch@10 \\", r"\midrule"]
    for fam, g in d.groupby("family", sort=False):
        n = g.market.nunique()
        m = g.groupby("detector", sort=False)[["catch@1", "catch@3", "catch@5", "catch@10"]].mean()
        for i, (det, r) in enumerate(m.iterrows()):
            lab = f"{fam} ({n})" if i == 0 else ""
            rows.append(" & ".join([lab, names[det]] + [f"{r[c]:.2f}" for c in m.columns]) + r" \\")
        rows.append(r"\addlinespace")
    (OUT / "transfer.tex").write_text(TOP % "llrrrr" + "\n".join(rows[:-1]) + BOT)


def menu_random():
    f = R / "menu_random_summary.csv"
    if not f.exists():
        return
    d = pd.read_csv(f)
    rows = [r"& & \multicolumn{2}{c}{gain, band only (thousand)} & \multicolumn{2}{c}{block at 240 steps: ratio to band only} & \multicolumn{2}{c}{inspection of 3: markets with net benefit $>0$} \\",
            r"\cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}",
            r"family & markets & menu of 4 & larger menu & menu of 4 & larger menu & menu of 4 & larger menu \\", r"\midrule"]
    for _, r in d.iterrows():
        cells = [r.family, str(int(r.markets)), f"{r['band 7%: gain, menu of 4 (median)'] / 1e3:.0f}", f"{r['band 7%: gain, larger menu (median)'] / 1e3:.0f}",
                 f"{r['block 240 / band, menu of 4: median']:.2f}", f"{r['block 240 / band, menu + random: median']:.2f}",
                 r["inspect 3, menu of 4: markets with net U5>0"], r["inspect 3, menu + random: markets with net U5>0"]]
        rows.append(" & ".join(cells) + r" \\")
    (OUT / "menu_random.tex").write_text(TOP % "lrrrrrrr" + "\n".join(rows) + BOT)


def allocation():
    f, g = R / "allocation_capacity.csv", R / "allocation_summary.csv"
    if not f.exists() or not g.exists():
        return
    cap = pd.read_csv(f)
    sm = pd.read_csv(g)
    names = [("uniform", "uniform"), ("proportional to N", r"proportional to $N_w$"), ("rule, signal from scaling law", r"rule, signal from Proposition~\ref{prop:power}"),
             ("rule, signal fitted per stock", "rule, signal fitted per stock"), ("oracle (empirical curves)", "oracle (selection episodes)")]
    rows = [r"allocation & \multicolumn{2}{c}{capacity that leaves no positive net benefit} & \multicolumn{2}{c}{ring's best net benefit at $C=64$ (thousand)} \\",
            r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}", r"& $m=5$ & $m=10$ & $m=5$ & $m=10$ \\", r"\midrule"]
    for key, lab in names:
        cells = [lab]
        for m in (5, 10):
            c = cap[(cap.m == m) & (cap.allocation == key)]["smallest capacity with no positive net benefit"]
            cells.append(f"{c.median():.0f} ({c.min():.0f}--{c.max():.0f})")
        for m in (5, 10):
            r = sm[(sm.m == m) & (sm.allocation == key) & (sm["capacity C"] == 64)].iloc[0]
            cells.append(f"{r['mean'] / 1e3:.1f} ({r['std'] / 1e3:.1f})")
        rows.append(" & ".join(cells) + r" \\")
    (OUT / "allocation.tex").write_text(TOP % "lrrrr" + "\n".join(rows) + BOT)


def jitter_abm():
    parts = {}
    for blk, f in ((100, "jitter_abm.csv"), (25, "jitter_abm_b25.csv")):
        if not (R / f).exists():
            return
        parts[blk] = pd.read_csv(R / f)
    def fam(m):
        return "generic simulator" if m.startswith("generic") else m.rsplit(" ", 1)[0]
    rows = [r"& & \multicolumn{2}{c}{block 100} & \multicolumn{2}{c}{block 25} & \\", r"\cmidrule(lr){3-4}\cmidrule(lr){5-6}",
            r"markets & accounts per window & honest family-wise error & member rejected & honest family-wise error & member rejected & member in top 5 \\", r"\midrule"]
    d100, d25 = parts[100], parts[25]
    for d in (d100, d25):
        d["fam"] = d.market.map(fam)
    for f in ["generic simulator", "index level", "stock level", "trend-free"]:
        a = d100[d100.fam == f]
        b = d25[d25.fam == f]
        cells = [f if f == "generic simulator" else f"{f} (2)", f"{a[a['ring in market']]['mean active accounts'].mean():.0f}",
                 f"{a[~a['ring in market']]['family-wise error (non-member rejected)'].mean():.3f}", f"{a[a['ring in market']]['member rejected'].mean():.3f}",
                 f"{b[~b['ring in market']]['family-wise error (non-member rejected)'].mean():.3f}", f"{b[b['ring in market']]['member rejected'].mean():.3f}",
                 f"{a[a['ring in market']]['catch@5 (jitter z)'].mean():.2f}"]
        rows.append(" & ".join(cells) + r" \\")
    (OUT / "jitter_abm.tex").write_text(TOP % "lrrrrrr" + "\n".join(rows) + BOT)
