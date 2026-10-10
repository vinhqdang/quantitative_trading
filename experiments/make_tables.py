"""LaTeX table fragments for the paper, generated from the CSV outputs in results/ (no numbers are typed by hand)."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

R, OUT = Path("results"), Path("paper/tables")
OUT.mkdir(parents=True, exist_ok=True)


def tex_escape(s) -> str:
    return str(s).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")


def fmt_ci(s: str) -> str:
    m = re.match(r"([\d.]+) \[([\d.]+), ([\d.]+)\]", str(s))
    p, lo, hi = m.groups()
    return rf"{p}\,{{\scriptsize[{lo}, {hi}]}}"


def robust():
    df = pd.read_csv(R / "ring_robust.csv")
    scen = list(dict.fromkeys(df.scenario))
    names = [("order-to-trade ratio", "order-to-trade ratio"), ("isolation forest (no labels)", "isolation forest (no labels)"),
             ("coincidence, unsigned (no labels)", "coincidence test, unsigned (no labels)"),
             ("coincidence, signed (no labels)", "coincidence test, signed (no labels)"),
             ("gradient boosting (trained with labels, clean market)", "gradient boosting (labels, clean market)")]
    head = " & ".join(["detector"] + [tex_escape(s).replace("+ ", "+") for s in scen])
    rows = [head + r" \\", r"\midrule"]
    for key, label in names:
        cells = [fmt_ci(df[(df.scenario == s) & (df.detector == key)]["catch@5"].iloc[0]) for s in scen]
        rows.append(" & ".join([label] + cells) + r" \\")
    body = "\n".join(rows)
    (OUT / "robust.tex").write_text("\\begin{tabular}{l" + "c" * len(scen) + "}\n\\toprule\n" + body + "\n\\bottomrule\n\\end{tabular}\n")


def policy():
    df = pd.read_csv(R / "vn_cross.csv")
    rows = [r"policy & ring gain (mean, s.e.) & caught & net benefit after fine, $m=5$ & $m=10$ \\", r"\midrule"]
    for _, r in df.iterrows():
        gain = f"{r.gain / 1e3:.1f}k ({r['gain se'] / 1e3:.1f}k)"
        if pd.notna(r.get("caught")):
            rows.append(" & ".join([tex_escape(r.scenario), gain, f"{r.caught:.0%}".replace("%", r"\%"),
                                    f"{r['net U (m=5)'] / 1e3:.1f}k", f"{r['net U (m=10)'] / 1e3:.1f}k"]) + r" \\")
        else:
            rows.append(" & ".join([tex_escape(r.scenario), gain, "--", "--", "--"]) + r" \\")
    (OUT / "policy.tex").write_text("\\begin{tabular}{lrrrr}\n\\toprule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")


def cases():
    df = pd.read_csv(R / "case_validation_cases.csv")
    order = ["abnormal return only", "combined (Fisher)", "isolation forest", "round trip only", "volume surge only"]
    label = {"abnormal return only": "market-adjusted abnormal return", "combined (Fisher)": "combined six-feature score",
             "isolation forest": "isolation forest, same features", "round trip only": "round trip (run-up, retracement)",
             "volume surge only": "volume surge"}
    rows = [r"detector & superiority & top 10 & chance & top 20 & chance & top 50 & chance \\", r"\midrule"]
    n = df.groupby("detector").size().iloc[0]
    for d in order:
        g = df[df.detector == d]
        cells = [label[d], f"{g.superiority.mean():.2f}"]
        for b in (10, 20, 50):
            cells += [f"{int(g[f'top{b}'].sum())}/{len(g)}", f"{g[f'chance top{b}'].mean():.0%}".replace("%", r"\%")]
        rows.append(" & ".join(cells) + r" \\")
    (OUT / "cases.tex").write_text("\\begin{tabular}{lrrrrrrr}\n\\toprule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")


def ablation():
    df = pd.read_csv(R / "ring_ablation.csv")
    rows = [r"factor & level & catch@5 & catch@1 & honest flagged & accounts per window \\", r"\midrule"]
    last = None
    for _, r in df.iterrows():
        f = tex_escape(r.factor) if r.factor != last else ""
        last = r.factor
        rows.append(" & ".join([f, tex_escape(r.level), fmt_ci(r["catch@5"]), fmt_ci(r["catch@1"]),
                                f"{r['honest flagged p<=0.01']:.3f}", f"{r['accounts per window']:.0f}"]) + r" \\")
    (OUT / "ablation.tex").write_text("\\begin{tabular}{llcccr}\n\\toprule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")


def case_list():
    df = pd.read_csv("data/cases.csv")
    df = df[df.include.astype(str).str.lower() == "yes"]
    rows = [r"ticker & period & accounts & decided & type \\", r"\midrule"]
    for _, r in df.iterrows():
        rows.append(" & ".join([r.ticker, f"{r.start} to {r.end}", str(r.accounts), tex_escape(r.decided), tex_escape(r.type)]) + r" \\")
    (OUT / "caselist.tex").write_text("\\begin{tabular}{llrll}\n\\toprule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    return df


def window_sensitivity():
    rows = [r"window (days) & detector & superiority vs random stocks & superiority vs same stock & cases in top 10 / 10 \\", r"\midrule"]
    for tag, w in (("_w10", 10), ("", 20), ("_w60", 60)):
        f = R / f"case_validation{tag}_cases.csv"
        if not f.exists():
            continue
        df = pd.read_csv(f)
        for d, lab in (("abnormal return only", "abnormal return"), ("combined (Fisher)", "combined score"), ("volume surge only", "volume surge")):
            g = df[df.detector == d]
            rows.append(" & ".join([str(w), lab, f"{g.superiority.mean():.2f}", f"{g['superiority vs same stock'].mean():.2f}", f"{int(g.top10.sum())}"]) + r" \\")
    (OUT / "window_sensitivity.tex").write_text("\\begin{tabular}{llrrr}\n\\toprule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")


def tick_compare():
    did, sim = R / "tick_reform_did.csv", R / "tick_sim.csv"
    if not (did.exists() and sim.exists()):
        return
    d = pd.read_csv(did).set_index("outcome")
    s = pd.read_csv(sim)
    rows = [r"outcome & real DiD (95\% interval) & real, relative to HOSE pre-period level & sim: tick $2\to1$ & $5\to1$ & $10\to1$ \\", r"\midrule"]
    for out in ["CS spread (%)", "daily range (%)", "|return| (%)", "zero-return share", "log volume"]:
        r = d.loc[out]
        rel = r["DiD"] / r["pre-period HOSE mean"] * 100 if "log" not in out else float("nan")
        cells = [tex_escape(out), f"{r['DiD']:.3f} [{r.ci_lo:.3f}, {r.ci_hi:.3f}]", "--" if np.isnan(rel) else f"{rel:.0f}\\%"]
        for old in ("2 -> 1", "5 -> 1", "10 -> 1"):
            x = s[(s["tick reduction"] == old) & (s.outcome == out)].iloc[0]
            cells.append("--" if "log" in out else f"{x.change / x['level before'] * 100:.0f}\\%")
        rows.append(" & ".join(cells) + r" \\")
    (OUT / "tick_compare.tex").write_text("\\begin{tabular}{lccccc}\n\\toprule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")


def ensemble(tag, name):
    f = R / f"vn_ensemble{tag}.csv"
    if not f.exists():
        return
    df = pd.read_csv(f)
    if "gain_vs_no_band" not in df:
        base = df[df.policy == "no price band"].set_index("market").gain
        df["gain_vs_no_band"] = df.apply(lambda r: r.gain / base[r.market] if r.market in base and base[r.market] > 0 else np.nan, axis=1)
    n = df.market.nunique()
    rows = [r"policy & median gain & range over markets & median ratio to no policy & median detection prob. & deterred at $m=5$ \\", r"\midrule"]
    for pol, g in df.groupby("policy", sort=False):
        ratio = g.gain_vs_no_band.median()
        caught = g.caught.median() if "caught" in g and g.caught.notna().any() else float("nan")
        det = f"{int((g.net_U5 <= 0).sum())}/{len(g)}" if "net_U5" in g and g.net_U5.notna().any() else "--"
        rows.append(" & ".join([tex_escape(pol), f"{g.gain.median() / 1e3:.1f}k", f"{g.gain.min() / 1e3:.1f}k to {g.gain.max() / 1e3:.1f}k",
                                "--" if np.isnan(ratio) else f"{ratio:.2f}", "--" if np.isnan(caught) else f"{caught:.0%}".replace("%", r"\%"), det]) + r" \\")
    (OUT / f"ensemble{name}.tex").write_text("\\begin{tabular}{lrrrrr}\n\\toprule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
    return n


def matrix():
    f = R / "policy_matrix.csv"
    if not f.exists():
        return
    df = pd.read_csv(f)
    base = df.iloc[0]
    rows = [r"policy & spread & depth & volatility & retail cost & volume & spoof impact & pump impact & wash share & ring gain \\", r"\midrule"]
    for _, r in df.iterrows():
        rel = lambda k: f"{(r[k] / base[k] - 1) * 100:+.0f}\\%"
        rows.append(" & ".join([tex_escape(r.policy), rel("spread"), rel("depth"), rel("vol"), rel("noise_cost"), rel("volume"),
                                f"{r['spoof impact']:.2f}", f"{r['pump impact']:.2f}", f"{r['wash volume share']:.3f}", f"{r['ring gain'] / 1e3:.0f}k"]) + r" \\")
    (OUT / "matrix.tex").write_text("\\begin{tabular}{lrrrrrrrrr}\n\\toprule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")


def case_stats():
    f = R / "case_stats.csv"
    if not f.exists():
        return
    df = pd.read_csv(f)
    rows = [r"stock & exchange & days & pre-period vol. (\%) & vol. in period (\%) & zero-return share & log price change ($\times100$) & ceiling days & longest run \\", r"\midrule"]
    for _, r in df.iterrows():
        rows.append(" & ".join([tex_escape(r.ticker), tex_escape(r.exchange), str(int(r.days)), f"{r['pre vol %']:.2f}", f"{r['case vol %']:.2f}",
                                f"{r['pre zero-return share']:.2f}", f"{r['price change %']:+.0f}", str(int(r['ceiling days'])),
                                str(int(r['longest ceiling run']))]) + r" \\")
    (OUT / "casestats.tex").write_text("\\begin{tabular}{llrrrrrrr}\n\\toprule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")


if __name__ == "__main__":
    robust(); policy(); cases(); ablation(); case_list(); window_sensitivity(); tick_compare(); ensemble("", ""); ensemble("_stock", "_stock"); matrix(); case_stats()
    print(sorted(p.name for p in OUT.glob("*.tex")))
