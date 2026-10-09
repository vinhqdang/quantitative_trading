import numpy as np

from marketsim.features import FEATURES, label_windows, window_features
from marketsim.sim import SimConfig, run_episode

SMALL = SimConfig(steps=1500, warmup=200, n_noise=30, n_mm=3, n_fund=4, n_mom=4, n_imb=4, n_inst=1,
                  window_len=(600, 900))


def test_episode_is_deterministic_given_seed():
    a, b = run_episode(7, SMALL), run_episode(7, SMALL)
    assert a.events.equals(b.events)
    assert np.array_equal(a.mids, b.mids)


def test_different_seeds_differ():
    assert not run_episode(1, SMALL).events.equals(run_episode(2, SMALL).events)


def test_trades_conserve_quantity_and_cash():
    ep = run_episode(3, SMALL)
    tr = ep.events[ep.events.kind == 3]
    buys = tr[tr.side == 1].qty.sum()
    sells = tr[tr.side == -1].qty.sum()
    assert buys == sells
    assert abs(ep.pnl.pnl.sum()) < 1e-6 * max(1, tr.price.mean() * buys)  # zero-sum before marking


def test_manipulators_leave_tagged_orders():
    ep = run_episode(11, SMALL)
    assert set(ep.agents.kind) >= {"spoofer", "pump_dump"}
    assert len(ep.gt_orders) > 0


def test_labels_cover_only_manipulator_accounts():
    ep = run_episode(11, SMALL)
    df = label_windows(ep, window_features(ep, 300), 300)
    pos = df[df.y == 1]
    assert len(pos) > 0
    assert pos.kind.isin(["spoofer", "pump_dump", "wash"]).all()
    assert not df[FEATURES].isna().any().any()


def test_features_do_not_reference_ground_truth():
    assert not {"kind", "type", "y", "tag"} & set(FEATURES)
