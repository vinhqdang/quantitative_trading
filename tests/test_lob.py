from marketsim.lob import BUY, SELL, OrderBook


def test_price_priority_then_time_priority():
    ob = OrderBook()
    ob.submit(1, SELL, 101, 5, 0)
    ob.submit(2, SELL, 100, 5, 1)
    ob.submit(3, SELL, 100, 5, 2)
    _, fills, _ = ob.submit(4, BUY, 101, 12, 3)
    assert [(f.price, f.qty, f.maker.agent) for f in fills] == [(100, 5, 2), (100, 5, 3), (101, 2, 1)]
    assert ob.best(SELL) == 101
    assert ob.qty_at[SELL][101] == 3


def test_limit_order_rests_and_market_remainder_is_dropped():
    ob = OrderBook()
    order, fills, _ = ob.submit(1, BUY, 99, 10, 0)
    assert not fills and ob.best(BUY) == 99
    order, fills, _ = ob.submit(2, SELL, None, 25, 1)
    assert sum(f.qty for f in fills) == 10
    assert ob.best(BUY) is None and ob.best(SELL) is None


def test_non_crossing_limit_does_not_trade():
    ob = OrderBook()
    ob.submit(1, SELL, 101, 5, 0)
    _, fills, _ = ob.submit(2, BUY, 100, 5, 1)
    assert not fills
    assert ob.best(BUY) == 100 and ob.best(SELL) == 101


def test_cancel_removes_liquidity_and_reports_remaining_quantity():
    ob = OrderBook()
    o, _, _ = ob.submit(1, SELL, 100, 10, 0)
    ob.submit(2, BUY, 100, 4, 1)
    cancelled = ob.cancel(o.oid)
    assert cancelled.qty == 6
    assert ob.best(SELL) is None
    assert ob.cancel(o.oid) is None


def test_cancelled_order_is_skipped_by_matching():
    ob = OrderBook()
    a, _, _ = ob.submit(1, SELL, 100, 5, 0)
    ob.submit(2, SELL, 100, 5, 1)
    ob.cancel(a.oid)
    _, fills, _ = ob.submit(3, BUY, 100, 5, 2)
    assert [(f.maker.agent, f.qty) for f in fills] == [(2, 5)]


def test_self_trade_prevention_cancels_resting_order():
    ob = OrderBook()
    ob.submit(1, SELL, 100, 5, 0)
    ob.submit(2, SELL, 101, 5, 1)
    _, fills, stp = ob.submit(1, BUY, 101, 5, 2)
    assert [m.agent for m in stp] == [1]
    assert [(f.maker.agent, f.price) for f in fills] == [(2, 101)]


def test_depth_and_book_consistency_after_random_activity():
    import random
    rng = random.Random(0)
    ob = OrderBook()
    live = []
    for t in range(3000):
        r = rng.random()
        if r < 0.5:
            side = rng.choice([BUY, SELL])
            o, _, _ = ob.submit(rng.randrange(20), side, 1000 + rng.randrange(-5, 6), rng.randrange(1, 10), t)
            live.append(o.oid)
        elif r < 0.7:
            ob.submit(rng.randrange(20), rng.choice([BUY, SELL]), None, rng.randrange(1, 10), t)
        elif live:
            ob.cancel(live.pop(rng.randrange(len(live))))
        bb, ba = ob.best(BUY), ob.best(SELL)
        assert bb is None or ba is None or bb < ba, "book crossed"
    for side in (BUY, SELL):
        for price, qty in ob.qty_at[side].items():
            resting = sum(o.qty for o in ob.orders.values() if o.side == side and o.price == price and o.alive)
            assert qty == resting
