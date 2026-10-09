from marketsim.exchange import Exchange
from marketsim.lob import BUY, SELL
from marketsim.policy import Policy
from marketsim.sim import SimConfig, run_episode


def test_tick_rounds_against_the_submitter():
    ex = Exchange(policy=Policy(tick=5))
    b = ex.limit(1, BUY, 10_003, 1)
    s = ex.limit(2, SELL, 10_012, 1)
    assert ex.book.orders[b].price == 10_000
    assert ex.book.orders[s].price == 10_015


def test_min_rest_blocks_early_cancel_only():
    ex = Exchange(policy=Policy(min_rest=3))
    oid = ex.limit(1, BUY, 9_990, 5)
    assert not ex.cancel(oid)
    for _ in range(3):
        ex.end_step()
    assert ex.cancel(oid)


def test_cancel_fee_is_charged_per_cancelled_order():
    ex = Exchange(policy=Policy(cancel_fee=2.5))
    a, b = ex.limit(1, BUY, 9_990, 5), ex.limit(1, BUY, 9_989, 5)
    ex.cancel(a)
    ex.cancel(b)
    assert ex.cash[1] == -5.0


def test_circuit_breaker_rejects_new_orders_but_allows_cancels():
    ex = Exchange(policy=Policy(halt_move=3, halt_window=2, halt_len=4))
    rest = ex.limit(1, BUY, 9_990, 5)
    ex.limit(2, SELL, 10_000, 5)
    ex.end_step()
    ex.book.cancel(rest)  # move the mid sharply without going through the exchange
    ex.limit(1, BUY, 9_999, 1)
    ex.end_step()
    ex.fund = 0
    ex.mids[-1] = 10_020  # force a large move
    ex.end_step()
    assert ex.t < ex.halt_until
    assert ex.limit(3, BUY, 9_999, 1) == -1
    assert ex.market(3, BUY, 1) == -1


def test_baseline_policy_is_identical_to_default():
    small = SimConfig(steps=800, warmup=100, n_noise=20, n_mm=3, n_fund=3, n_mom=3, n_imb=3, n_inst=1,
                      window_len=(300, 500))
    a = run_episode(5, small)
    b = run_episode(5, SimConfig(**{**small.__dict__, "policy": Policy()}))
    assert a.events.equals(b.events)
