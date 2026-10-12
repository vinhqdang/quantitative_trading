"""Summary of run_menu_random.py: does a larger strategy menu change the conclusions?"""

from pathlib import Path

import numpy as np
import pandas as pd

out = Path("results")
d = pd.read_csv(out / "menu_random.csv")
d["menu"] = d.menu.where(d.menu == "menu of 4", "menu + random")
rows = []
for fam, g in list(d.groupby("family", sort=False)) + [("all markets", d)]:
    piv = g.pivot_table(index=["family", "market"], columns=["policy", "menu"], values="gain")
    r = {"family": fam, "markets": len(piv)}
    for pol in ("band 7%", "band 7% + block at 240-step mean", "band 7% + inspect 3 per window"):
        a, b = piv[(pol, "menu of 4")], piv[(pol, "menu + random")]
        r[f"{pol}: gain, menu of 4 (median)"] = a.median()
        r[f"{pol}: gain, larger menu (median)"] = b.median()
        r[f"{pol}: markets where larger menu gives more"] = int((b > a).sum())
    for m in ("menu of 4", "menu + random"):
        band, blk = piv[("band 7%", m)], piv[("band 7% + block at 240-step mean", m)]
        ok = band > 0
        ratio = (blk[ok] / band[ok]).to_numpy()
        r[f"block 240 / band, {m}: median"] = float(np.median(ratio))
        r[f"block 240 / band, {m}: markets lower"] = f"{int((blk[ok] < band[ok]).sum())}/{int(ok.sum())}"
    ins = g[g.policy == "band 7% + inspect 3 per window"]
    for m in ("menu of 4", "menu + random"):
        x = ins[ins.menu == m]
        r[f"inspect 3, {m}: markets with net U5>0"] = f"{int((x.net_U5 > 0).sum())}/{len(x)}"
        r[f"inspect 3, {m}: median caught"] = float(x.caught.median())
    rows.append(r)
df = pd.DataFrame(rows)
df.to_csv(out / "menu_random_summary.csv", index=False)
text = ["# Larger strategy menu (4 strategies against 4 + 24 random)\n",
        "Two-stage selection on separate episodes, reported gains on 12 further episodes per cell; medians over markets.\n", df.round(3).T.to_markdown()]
(out / "menu_random_summary.md").write_text("\n".join(text))
print("\n".join(text))
