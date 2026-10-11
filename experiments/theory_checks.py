"""Monte Carlo checks of the propositions in the paper (no agent-based market involved).

A. Validity (Proposition 1): for flows that are exchangeable under cyclic shifts, P(p <= alpha) <= alpha for the actual
   implementation (signed and unsigned, max over tolerances). Also with autocorrelated, bursty honest flows.
B. Inspection budget (Proposition 2): the number of honest accounts with p <= alpha among N is at most N*alpha in expectation,
   and p >= 1/T, so a Bonferroni threshold alpha/N is unreachable when N > alpha*T.
C. Power scaling law (Proposition 3): in a Gaussian-flow model with a common campaign signal shared by K members among N
   accounts, E[Z(0)] ~ sqrt(T_eff) * rho with rho = (K-1) eta / sqrt((1+eta) (N-1 + (K-1)^2 eta)); the predicted catch@B is
   compared with Monte Carlo.
D. Signed netting (Proposition 4): desks that re-quote both sides at the same moments are flagged by the unsigned statistic and
   not by the signed one; one-directional coordination is flagged by both.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from marketsim.coordination import coincidence_scan

T_DEFAULT = 300
TOLS = (1, 5, 15)


def scan_gauss(x: np.ndarray, tols=TOLS):
    """x: [N, T] signed flows -> z, p from the signed test."""
    flow = np.stack([x, np.zeros_like(x)])
    return coincidence_scan(flow, tols, signed=True)


def exp_validity(rng, n_windows=300, N=60, T=T_DEFAULT):
    rows = []
    for kind in ["iid Gaussian", "iid Poisson counts", "bursty (shared regime), unsigned", "bursty (shared regime), signed"]:
        ps = []
        for _ in range(n_windows):
            if kind == "iid Gaussian":
                x = rng.normal(size=(N, T))
            elif kind == "iid Poisson counts":
                x = rng.poisson(0.3, size=(N, T)).astype(float) - rng.poisson(0.3, size=(N, T))
            else:
                regime = (rng.random(T) < 0.15).astype(float)           # shared bursts: violates the null
                act = 1 + 4 * regime
                x = rng.poisson(0.3 * act, size=(N, T)).astype(float) - rng.poisson(0.3 * act, size=(N, T))
            if kind.startswith("bursty") and kind.endswith("unsigned"):
                a = np.maximum(x, 0); b = np.maximum(-x, 0)
                _, p = coincidence_scan(np.stack([a, b]), TOLS, signed=False)
            else:
                _, p = scan_gauss(x)
            ps.append(p)
        ps = np.concatenate(ps)
        for a in [0.001, 0.005, 0.01, 0.05, 0.1]:
            rows.append({"flows": kind, "alpha": a, "rejection rate": float((ps <= a).mean()), "n tests": len(ps)})
    return pd.DataFrame(rows)


def exp_budget(rng, n_windows=200, T=T_DEFAULT):
    rows = []
    for N in [50, 150, 300, 600, 1200]:
        c = {a: 0 for a in (0.01, 0.05)}
        minp, tot = [], 0
        for _ in range(n_windows):
            _, p = scan_gauss(rng.normal(size=(N, T)))
            for a in c:
                c[a] += int((p <= a).sum())
            minp.append(p.min())
            tot += 1
        for a, v in c.items():
            rows.append({"N": N, "alpha": a, "mean flagged per window": v / tot, "bound N*alpha": N * a,
                         "share of windows with any flag at Bonferroni alpha/N": float(np.mean(np.array(minp) <= a / N)),
                         "min attainable p = 1/T": 1.0 / T})
    return pd.DataFrame(rows)


def rho_model(N, K, eta):
    return (K - 1) * eta / np.sqrt((1 + eta) * ((N - 1) + (K - 1) ** 2 * eta))


def make_flows(rng, N, K, eta, T=T_DEFAULT, pi=0.2, jitter=0):
    """Honest noise N(0,1); K members add b*s_j[t], s a common Bernoulli(pi) campaign signal (jittered per member)."""
    x = rng.normal(size=(N, T))
    b = np.sqrt(eta / (pi * (1 - pi)))
    s = (rng.random(T) < pi).astype(float)
    for j in range(K):
        sj = np.roll(s, rng.integers(-jitter, jitter + 1)) if jitter else s
        x[j] += b * sj
    return x


def exp_power(rng, R=120, T=T_DEFAULT, B=5):
    rows = []
    grid = [(N, K, eta) for N in (100, 200, 400, 800) for K in (4, 8, 16, 32) for eta in (0.1, 0.3)]
    for N, K, eta in grid:
        zr, caught, zh = [], [], []
        for _ in range(R):
            x = make_flows(rng, N, K, eta, T)
            z, p = scan_gauss(x)
            order = np.argsort(-z)
            caught.append(bool((order[:B] < K).any()))
            zr.append(z[:K].mean())
            zh.append(z[K:])
        zh = np.concatenate(zh)
        rows.append({"N": N, "K": K, "eta": eta, "rho_model": rho_model(N, K, eta), "mean z ring": float(np.mean(zr)),
                     "catch@5": float(np.mean(caught)), "honest z q(1-B/N)": float(np.quantile(zh, 1 - B / N)),
                     "honest z mean": float(zh.mean())})
    df = pd.DataFrame(rows)
    # one fitted constant: E[z] = c * rho  (c = sqrt(T_eff))
    c = float((df["mean z ring"] - df["honest z mean"]).dot(df.rho_model) / df.rho_model.dot(df.rho_model))
    df["sqrt(T_eff) fitted"] = c
    df["z predicted"] = df["honest z mean"] + c * df.rho_model
    # predicted catch: member exceeds the honest (1-B/N) quantile; members treated as independent
    q = 1 - norm.cdf(df["honest z q(1-B/N)"] - df["z predicted"])
    df["catch@5 predicted"] = 1 - (1 - q) ** df.K
    return df


def exp_netting(rng, R=200, N=100, T=T_DEFAULT):
    rows = []
    for scenario in ["market-making desks (both sides, same moments)", "one-directional ring"]:
        zu, zs = [], []
        for _ in range(R):
            buy = rng.poisson(0.3, size=(N, T)).astype(float)
            sell = rng.poisson(0.3, size=(N, T)).astype(float)
            moment = (rng.random(T) < 0.15)
            for j in range(6):                                          # six accounts share the same moments
                if scenario.startswith("market"):
                    buy[j] += 3 * moment * rng.random(T); sell[j] += 3 * moment * rng.random(T)
                else:
                    buy[j] += 3 * moment * rng.random(T)
            z_u, p_u = coincidence_scan(np.stack([buy, sell]), TOLS, signed=False)
            z_s, p_s = coincidence_scan(np.stack([buy, sell]), TOLS, signed=True)
            zu.append(np.mean(p_u[:6] <= 0.01)); zs.append(np.mean(p_s[:6] <= 0.01))
        rows.append({"scenario": scenario, "share flagged (p<=0.01), unsigned": float(np.mean(zu)),
                     "share flagged (p<=0.01), signed": float(np.mean(zs))})
    return pd.DataFrame(rows)


def main(a):
    rng = np.random.default_rng(a.seed)
    out = Path(a.out); out.mkdir(exist_ok=True)
    v = exp_validity(rng, a.n_windows); v.to_csv(out / "theory_validity.csv", index=False)
    b = exp_budget(rng, max(50, a.n_windows // 2)); b.to_csv(out / "theory_budget.csv", index=False)
    p = exp_power(rng, a.reps); p.to_csv(out / "theory_power.csv", index=False)
    n = exp_netting(rng); n.to_csv(out / "theory_netting.csv", index=False)
    text = ["# Monte Carlo checks of the propositions\n", "## Validity (Proposition 1)\n", v.round(4).to_markdown(index=False),
            "\n## Inspection budget (Proposition 2)\n", b.round(4).to_markdown(index=False),
            "\n## Power scaling law (Proposition 3)\n", p.round(3).to_markdown(index=False),
            f"\nCorrelation between predicted and simulated catch@5: {np.corrcoef(p['catch@5'], p['catch@5 predicted'])[0, 1]:.3f}; "
            f"mean absolute error {np.abs(p['catch@5'] - p['catch@5 predicted']).mean():.3f}.\n",
            "\n## Signed netting (Proposition 4)\n", n.round(3).to_markdown(index=False)]
    (out / "theory_checks.md").write_text("\n".join(text))
    print("\n".join(text))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-windows", type=int, default=300)
    ap.add_argument("--reps", type=int, default=120)
    ap.add_argument("--out", default="results")
    main(ap.parse_args())
