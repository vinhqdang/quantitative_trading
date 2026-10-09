import numpy as np
import pandas as pd

from marketsim.realdata import compute_features, scores


def _panel(n_days=700, n_stocks=60, seed=0):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2020-01-01", periods=n_days)
    cols = [f"S{i}" for i in range(n_stocks)]
    ret = rng.normal(0, 0.015, (n_days, n_stocks))
    vol = rng.lognormal(10, 0.3, (n_days, n_stocks))
    # stock S0: pump over days 600-619 with volume surge, then retrace
    ret[600:610, 0] += 0.03
    ret[610:620, 0] -= 0.03
    vol[600:620, 0] *= 8
    close = 20 * np.exp(np.cumsum(ret, axis=0))
    high, low = close * 1.01, close * 0.99
    mk = lambda a: pd.DataFrame(a, index=dates, columns=cols)
    return {"open": mk(close), "high": mk(high), "low": mk(low), "close": mk(close), "volume": mk(vol)}, dates


def test_planted_pump_ranks_at_the_top_of_its_cross_section():
    panel, dates = _panel()
    s = scores(compute_features(panel, window=20))
    fisher = pd.DataFrame(s["fisher"], index=dates, columns=panel["close"].columns)
    pct = fisher.rank(axis=1, pct=True)
    assert pct.iloc[600:625, 0].max() > 0.97


def test_features_use_only_past_data():
    panel, dates = _panel()
    f1 = compute_features(panel, window=20)
    cut = {k: v.iloc[:650] for k, v in panel.items()}
    f2 = compute_features(cut, window=20)
    for k in f1:
        a, b = f1[k][:650], f2[k]
        both = np.isfinite(a) & np.isfinite(b)
        assert np.allclose(a[both], b[both])
