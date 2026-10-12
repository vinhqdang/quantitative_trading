import numpy as np

from marketsim.coordination import coincidence_scan
from marketsim.jitter import jitter_scan


def _flow(rng, n=60, T=300):
    x = rng.normal(size=(n, T))
    return np.stack([x, np.zeros_like(x)])


def test_single_block_equals_circular_test():
    rng = np.random.default_rng(0)
    f = _flow(rng)
    z, p, _, _ = jitter_scan(f, block=300, n_surr=3000, rng=rng)
    z0, p0 = coincidence_scan(f, (1, 5, 15), signed=True)
    assert np.allclose(z, z0, atol=1e-9)
    assert abs(np.mean(p) - np.mean(p0)) < 0.05


def test_surrogate_statistics_are_standardised_in_closed_form():
    # brute force over all within-block shifts of a short window
    rng = np.random.default_rng(1)
    T, L = 24, 8
    f = _flow(rng, n=5, T=T)
    z, p, e, u = jitter_scan(f, tols=(1,), block=L, n_surr=20000, rng=rng)
    x = f[0][0]
    o = f[0].sum(axis=0) - x
    o = o + np.roll(o, 1) + np.roll(o, -1)
    vals = []
    for s in np.ndindex(*(L,) * (T // L)):
        xs = np.concatenate([np.roll(x[k * L:(k + 1) * L], -s[k]) for k in range(T // L)])
        vals.append(float(xs @ o))
    vals = np.array(vals)
    zb = (float(x @ o) - vals.mean()) / vals.std()
    assert abs(zb - z[0]) < 1e-9
    assert abs((1 + (((vals - vals.mean()) / vals.std()) >= zb).sum() - 1) / len(vals) - p[0]) < 0.02


def test_false_alarm_rates_and_resolution_beyond_one_over_T():
    rng = np.random.default_rng(2)
    ps, fw = [], 0
    for _ in range(40):
        f = _flow(rng, n=100)
        z, p, e, u = jitter_scan(f, block=100, n_surr=999, rng=rng)
        ps.append(p)
    ps = np.concatenate(ps)
    assert 0.03 < (ps <= 0.05).mean() < 0.075
    assert ps.min() < 1 / 300                               # finer than the circular test can resolve


def test_family_wise_error_at_bonferroni_level_and_power():
    rng = np.random.default_rng(3)
    n, B, alpha = 120, 4999, 0.05
    false = 0
    for _ in range(30):
        f = _flow(rng, n=n)
        z, p, e, u = jitter_scan(f, block=100, n_surr=B, rng=rng, reject_alpha=alpha)
        false += int(((u == B) & (p <= alpha / n)).any())
    assert false / 30 <= 0.15                              # nominal 0.05
    hits = 0
    for _ in range(10):                                    # a ring of 10 accounts sharing a strong common signal
        x = rng.normal(size=(n, 300))
        sig = rng.normal(size=300) * 2.0
        x[:10] += sig
        z, p, e, u = jitter_scan(np.stack([x, np.zeros_like(x)]), block=100, n_surr=B, rng=rng, reject_alpha=alpha)
        hits += int(((u == B) & (p <= alpha / n))[:10].any())
    assert hits >= 8
