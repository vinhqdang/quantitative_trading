import numpy as np

from marketsim.coordination import coincidence_scan


def _independent_flow(rng, n=40, T=300, rate=0.05):
    return (rng.random((2, n, T)) < rate).astype(float)


def test_p_values_are_roughly_uniform_when_accounts_are_independent():
    rng = np.random.default_rng(0)
    ps = np.concatenate([coincidence_scan(_independent_flow(rng))[1] for _ in range(15)])
    assert 0.02 < (ps <= 0.05).mean() < 0.09
    assert (ps <= 0.01).mean() < 0.03


def test_planted_group_acting_together_is_detected():
    rng = np.random.default_rng(1)
    hits, honest_flagged = 0, 0
    for _ in range(10):
        flow = _independent_flow(rng)
        steps = rng.choice(300, size=15, replace=False)
        side = rng.integers(0, 2, size=15)
        for acc in range(6):                       # accounts 0..5 act on the same steps and sides
            flow[side, acc, steps] += 1.0
        z, p = coincidence_scan(flow)
        hits += (p[:6] <= 0.02).mean()
        honest_flagged += (p[6:] <= 0.01).mean()
    assert hits / 10 > 0.8
    assert honest_flagged / 10 < 0.03


def test_accounts_without_activity_get_neutral_scores():
    flow = np.zeros((2, 5, 300))
    flow[0, 0, [10, 50, 90]] = 1
    flow[0, 1, [10, 50, 90]] = 1
    z, p = coincidence_scan(flow)
    assert np.isfinite(z).all() and np.isfinite(p).all()
    assert p[0] < 0.1 and p[1] < 0.1
