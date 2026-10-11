"""Does the scaling law of Proposition 3 explain the agent-based sensitivity results?

Proposition 3 (Gaussian-flow model, verified in theory_checks.py): the mean shift of a ring member's statistic is proportional to
rho = (k-1) eta / sqrt((1 + eta)(N - 1 + (k-1)^2 eta)) for k accounts that share a signal of relative strength eta among N accounts,
which is about (k-1) eta / sqrt((1 + eta) N) when N is large: the shift falls like N^(-1/2) and grows with the number of co-active
members. In the agent-based ring only the m_push members of a push act together, so the number of co-active members does not
change with the ring size K, and the signal is proportional to the share of steps with a push. The model fitted here is therefore

    shift = s0 * (p_push / 0.8) * (100 / N)^gamma,  gamma = 1/2 (theory),
    catch@B = a * (1 - (1 - q)^K),  q = 1 - F0(t_B - shift),  t_B = F0^{-1}(1 - B/N),

with F0 the null distribution of the statistic (honest Gaussian flows through the real implementation). Constants s0 and a are
fitted to the three one-factor sweeps of results/ring_ablation.csv (11 points); the fit is cross-validated by holding out one
sweep. In the held-out 'accounts' sweep the N^(-1/2) law is a pure prediction. gamma is also fitted freely as a check.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from theory_checks import scan_gauss

B = 5
K_DEFAULT = 12


def null_grid(rng, windows=800, N=100, T=300):
    z = np.concatenate([scan_gauss(rng.normal(size=(N, T)))[0] for _ in range(windows)])
    p = np.linspace(0.0005, 0.9995, 400)
    return np.quantile(z, p), p, z


def load_points(path):
    df = pd.read_csv(path)
    num = lambda s: float(re.match(r"([\d.]+)", str(s)).group(1))
    pts = []
    for _, r in df.iterrows():
        catch, N = num(r["catch@5"]), float(r["accounts per window"])
        if r.factor == "noise traders (accounts)":
            pts.append({"sweep": "accounts", "level": round(N), "N": N, "K": K_DEFAULT, "push": 0.8, "catch": catch})
        elif r.factor == "ring size K":
            pts.append({"sweep": "ring size", "level": float(r.level), "N": N, "K": float(r.level), "push": 0.8, "catch": catch})
        elif r.factor == "ring push probability":
            pts.append({"sweep": "push probability", "level": float(r.level), "N": N, "K": K_DEFAULT, "push": float(r.level), "catch": catch})
    return pd.DataFrame(pts)


class Model:
    def __init__(self, grid, cdf, z):
        self.grid, self.cdf, self.z = grid, cdf, np.sort(z)

    def F0(self, x):
        return np.interp(x, self.grid, self.cdf, left=0.0, right=1.0)

    def predict(self, pts, s0, a, gamma=0.5):
        out = []
        for _, r in pts.iterrows():
            shift = s0 * (r.push / 0.8) * (100.0 / r.N) ** gamma
            t = np.quantile(self.z, 1 - B / r.N)
            q = 1 - self.F0(t - shift)
            out.append(a * (1 - (1 - q) ** r.K))
        return np.array(out)

    def fit(self, pts, free_gamma=False):
        best = None
        for s in (0.5, 1.0, 2.0, 4.0):
            f = (lambda p: self.predict(pts, p[0], p[1], p[2]) - pts.catch.to_numpy()) if free_gamma else \
                (lambda p: self.predict(pts, p[0], p[1]) - pts.catch.to_numpy())
            x0, lb, ub = ([s, 0.95, 0.5], [0.05, 0.5, 0.0], [20, 1.0, 2.0]) if free_gamma else ([s, 0.95], [0.05, 0.5], [20, 1.0])
            r = least_squares(f, x0, bounds=(lb, ub))
            if best is None or r.cost < best.cost:
                best = r
        return best.x


def main():
    rng = np.random.default_rng(0)
    grid, cdf, z = null_grid(rng)
    m = Model(grid, cdf, z)
    pts = load_points("results/ring_ablation.csv")
    p = m.fit(pts)
    pts["predicted"] = m.predict(pts, *p)
    pg = m.fit(pts, free_gamma=True)
    cv = []
    for held in pts.sweep.unique():
        tr, te = pts[pts.sweep != held], pts[pts.sweep == held]
        pp = m.fit(tr)
        pred = m.predict(te, *pp)
        pts.loc[te.index, "predicted (held-out sweep)"] = pred
        cv.append({"held-out sweep": held, "s0": pp[0], "ceiling a": pp[1], "mean abs. error": float(np.abs(pred - te.catch.to_numpy()).mean())})
    cvd = pd.DataFrame(cv)
    grid_rows = []
    for N in (50, 100, 200, 400, 700, 1000):
        for K in (2, 4, 8, 12, 16, 24, 32):
            g = pd.DataFrame([{"N": N, "K": K, "push": 0.8}])
            grid_rows.append({"N": N, "K": K, "catch@5 (model)": float(m.predict(g, *p)[0])})
    pd.DataFrame(grid_rows).to_csv("results/power_law_grid.csv", index=False)
    pts.to_csv("results/power_law_fit.csv", index=False)
    pd.DataFrame([{"s0": p[0], "a": p[1], "mae_all": float(np.abs(pts.predicted - pts.catch).mean()), "gamma_free": pg[2],
                   "s0_free": pg[0], "a_free": pg[1]}]).to_csv("results/power_law_params.csv", index=False)
    text = ["# Scaling law against the agent-based sensitivity results\n",
            f"Two fitted constants: s0 = {p[0]:.2f} (shift in standard units of the statistic at N = 100 and push probability 0.8) and a ceiling "
            f"a = {p[1]:.2f} (share of ring-active windows in which the signal is present). Mean absolute error over the 11 points: "
            f"{np.abs(pts.predicted - pts.catch).mean():.3f}. With the exponent of N left free: gamma = {pg[2]:.2f} (theory 0.5).\n",
            pts.round(3).to_markdown(index=False), "\n## Cross-validation by held-out sweep\n", cvd.round(3).to_markdown(index=False), ""]
    Path("results/power_law_fit.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    main()
