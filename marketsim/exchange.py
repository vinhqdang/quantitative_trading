"""Exchange wrapper: order book + event log + positions + ground-truth tags.

The event log is what a regulator would see (account id, order id, side, price,
quantity, counterparty). Ground-truth tags are stored separately and are never
exposed to the detection features.
"""

from __future__ import annotations

from collections import defaultdict

from .lob import BUY, SELL, OrderBook

# event kinds
NEW, MKT, CANCEL, TRADE = 0, 1, 2, 3
EVENT_COLUMNS = ["t", "kind", "agent", "oid", "side", "price", "qty", "mid", "cpty", "aggr"]


class Exchange:
    def __init__(self, start_price: int = 10_000):
        self.book = OrderBook()
        self.t = 0
        self.last_price = start_price
        self.fund = float(start_price)
        self.events: list[tuple] = []
        self.mids: list[float] = []
        self.open: dict[int, set[int]] = defaultdict(set)
        self.cash: dict[int, float] = defaultdict(float)
        self.inv: dict[int, int] = defaultdict(int)
        self.tags: dict[int, str] = {}
        self.gt_trades: list[tuple] = []  # (agent, tag, side, price, qty, t)

    # -- market data -------------------------------------------------------
    def best_bid(self):
        return self.book.best(BUY)

    def best_ask(self):
        return self.book.best(SELL)

    def mid(self) -> float:
        b, a = self.best_bid(), self.best_ask()
        if b is not None and a is not None:
            return (b + a) / 2
        if b is not None:
            return float(b)
        if a is not None:
            return float(a)
        return float(self.last_price)

    def spread(self) -> int | None:
        b, a = self.best_bid(), self.best_ask()
        return None if b is None or a is None else a - b

    def imbalance(self, ticks: int = 5) -> float:
        """(bid - ask) / (bid + ask) for resting depth within `ticks` of the best price on each side."""
        bb, ba = self.best_bid(), self.best_ask()
        if bb is None or ba is None:
            return 0.0
        bid = sum(q for p, q in self.book.qty_at[BUY].items() if p >= bb - ticks)
        ask = sum(q for p, q in self.book.qty_at[SELL].items() if p <= ba + ticks)
        return 0.0 if bid + ask == 0 else (bid - ask) / (bid + ask)

    def mid_at(self, lag: int) -> float:
        """Mid price `lag` steps ago (clamped to the available history)."""
        if not self.mids:
            return self.mid()
        return self.mids[max(0, len(self.mids) - lag)]

    # -- order entry -------------------------------------------------------
    def limit(self, agent: int, side: int, price: int, qty: int, tag: str | None = None) -> int:
        return self._submit(agent, side, int(price), int(qty), tag, NEW)

    def market(self, agent: int, side: int, qty: int, tag: str | None = None) -> int:
        return self._submit(agent, side, None, int(qty), tag, MKT)

    def _submit(self, agent, side, price, qty, tag, kind) -> int:
        mid = self.mid()
        order, fills, stp = self.book.submit(agent, side, price, qty, self.t)
        if tag is not None:
            self.tags[order.oid] = tag
        self.events.append((self.t, kind, agent, order.oid, side, price if price is not None else 0, qty, mid, -1, 0))
        for m in stp:
            self.open[m.agent].discard(m.oid)
            self.events.append((self.t, CANCEL, m.agent, m.oid, m.side, m.price, m.qty, mid, -1, 0))
        for f in fills:
            self._record_fill(f, mid)
        if order.alive and order.qty > 0 and price is not None:
            self.open[agent].add(order.oid)
        return order.oid

    def _record_fill(self, f, mid) -> None:
        buyer, seller = (f.taker, f.maker) if f.taker.side == BUY else (f.maker, f.taker)
        self.last_price = f.price
        for o, side in ((buyer, BUY), (seller, SELL)):
            other = seller if o is buyer else buyer
            self.cash[o.agent] -= side * f.price * f.qty
            self.inv[o.agent] += side * f.qty
            aggr = 1 if o is f.taker else 0
            self.events.append((self.t, TRADE, o.agent, o.oid, side, f.price, f.qty, mid, other.agent, aggr))
            tag = self.tags.get(o.oid)
            if tag is not None:
                self.gt_trades.append((o.agent, tag, side, f.price, f.qty, self.t))
        if not f.maker.alive:
            self.open[f.maker.agent].discard(f.maker.oid)

    def cancel(self, oid: int) -> bool:
        order = self.book.cancel(oid)
        if order is None:
            return False
        self.open[order.agent].discard(oid)
        self.events.append((self.t, CANCEL, order.agent, oid, order.side, order.price, order.qty, self.mid(), -1, 0))
        return True

    def end_step(self) -> None:
        self.mids.append(self.mid())
        self.t += 1
