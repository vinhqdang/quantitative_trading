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


if __name__ == "__main__":
    robust(); policy(); cases(); ablation(); case_list()
    print(sorted(p.name for p in OUT.glob("*.tex")))
