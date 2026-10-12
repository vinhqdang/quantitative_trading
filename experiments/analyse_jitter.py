"""Summaries of the jitter experiments: ring size at which a member is rejected with probability one half, against the closed form."""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from marketsim.jitter import jitter_scan

R = Path("results")
ALPHA = 0.05


def null_quantiles(rng, Ns, windows=300, T=300):
    """Null distribution of the observed statistic Zmax (honest iid flows) pooled over windows; return quantile function."""
    z = []
    for N in (240, 480, 960):
        for _ in range(windows // 3):
            x = rng.normal(size=(N, T))
            zz, _, _, _ = jitter_scan(np.stack([x, np.zeros_like(x)]), (1, 5, 15), 100, 0, True, rng)
            z.append(zz)
    z = np.sort(np.concatenate(z))
    return z


def rho(N, K, eta):
    return (K - 1) * eta / np.sqrt((1 + eta) * ((N - 1) + (K - 1) ** 2 * eta))


def crossing(Ks, p, level=0.5):
    Ks, p = np.asarray(Ks, float), np.asarray(p, float)
    ok = np.flatnonzero(p >= level)
    if len(ok) == 0:
        return np.nan
    j = ok[0]
    if j == 0:
        return Ks[0]
    # linear interpolation of the power on the log K scale
    x0, x1 = np.log(Ks[j - 1]), np.log(Ks[j])
    return float(np.exp(x0 + (level - p[j - 1]) / (p[j] - p[j - 1]) * (x1 - x0)))


def main():
    rng = np.random.default_rng(0)
    d = pd.read_csv(R / "jitter_kmin.csv")
    z0 = null_quantiles(rng, None)
    th = pd.read_csv(R / "theory_power.csv")
    c, h = float(th["sqrt(T_eff) fitted"].iloc[0]), float(th["honest z mean"].mean())
    rows = []
    for (eta, N), g in d.groupby(["eta", "N"]):
        g = g.sort_values("K")
        # critical value of the Bonferroni rule: the honest (1 - alpha/N) quantile of Zmax; beyond the sample use a Gaussian-tail extrapolation of the upper 2%
        lvl = 1 - ALPHA / N
        t_c = float(np.quantile(z0, lvl)) if (1 - lvl) * len(z0) > 30 else None
        if t_c is None:
            top = z0[int(0.98 * len(z0)):]
            mu_, sd_ = top.mean(), top.std()
            t_c = float(norm.ppf(lvl))  # fallback: standard normal tail, shifted by the honest mean
            t_c += h
        t_b = float(np.quantile(z0, 1 - 5 / N))
        Ks = np.arange(2, 400)
        q = 1 - norm.cdf(t_c - (h + c * rho(N, Ks, eta)))
        pred_fw = 1 - (1 - q) ** Ks
        q5 = 1 - norm.cdf(t_b - (h + c * rho(N, Ks, eta)))
        pred_r5 = 1 - (1 - q5) ** Ks
        rows.append({"eta": eta, "N": N, "K at power 1/2, family-wise rejection (simulated)": crossing(g.K, g.power_fwer),
                     "K at power 1/2, family-wise rejection (formula)": crossing(Ks, pred_fw), "K at catch@5 = 1/2 (simulated)": crossing(g.K, g.catch5),
                     "K at catch@5 = 1/2 (formula)": crossing(Ks, pred_r5), "critical value alpha/N": t_c, "critical value top 5": t_b,
                     "non-member rejected (family-wise error)": g.false_rejections.mean()})
    df = pd.DataFrame(rows)
    df["ratio family-wise / catch@5 (simulated)"] = df.iloc[:, 2] / df["K at catch@5 = 1/2 (simulated)"]
    # scaling exponent of K against N
    ex = []
    for eta, g in df.groupby("eta"):
        for col in ("K at power 1/2, family-wise rejection (simulated)", "K at catch@5 = 1/2 (simulated)", "K at power 1/2, family-wise rejection (formula)"):
            v = g[["N", col]].dropna()
            sl = np.polyfit(np.log(v.N), np.log(v[col]), 1)[0]
            ex.append({"eta": eta, "quantity": col, "exponent of N": sl, "points": len(v)})
    ex = pd.DataFrame(ex)
    df.to_csv(R / "jitter_kmin_summary.csv", index=False)
    ex.to_csv(R / "jitter_kmin_exponents.csv", index=False)
    print(df.round(2).to_string())
    print(ex.round(2).to_string())
    print("sqrt(T_eff) =", round(c, 2), "honest mean z =", round(h, 2))


if __name__ == "__main__":
    main()
