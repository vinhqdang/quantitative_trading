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
