"""Limit order book with price-time priority and self-trade prevention.

Prices are integer ticks. Cancelled orders are removed lazily from their price
level, so every operation is amortised O(log n) in the number of price levels.
"""

from __future__ import annotations

import heapq
from collections import deque

BUY, SELL = 1, -1


class Order:
    __slots__ = ("oid", "agent", "side", "price", "qty", "ts", "alive")

    def __init__(self, oid: int, agent: int, side: int, price: int | None, qty: int, ts: int):
        self.oid = oid
        self.agent = agent
        self.side = side
        self.price = price
        self.qty = qty
        self.ts = ts
        self.alive = True


class Fill:
    __slots__ = ("price", "qty", "maker", "taker")

    def __init__(self, price: int, qty: int, maker: Order, taker: Order):
        self.price = price
        self.qty = qty
        self.maker = maker
        self.taker = taker


class OrderBook:
    def __init__(self) -> None:
        self.levels: dict[int, dict[int, deque[Order]]] = {BUY: {}, SELL: {}}
        self.qty_at: dict[int, dict[int, int]] = {BUY: {}, SELL: {}}
        self._heaps: dict[int, list[int]] = {BUY: [], SELL: []}
        self.orders: dict[int, Order] = {}
        self._next_oid = 0

    # -- queries -----------------------------------------------------------
    def best(self, side: int) -> int | None:
        heap, qty = self._heaps[side], self.qty_at[side]
        while heap:
            price = -heap[0] if side == BUY else heap[0]
            if qty.get(price, 0) > 0:
                return price
            heapq.heappop(heap)
        return None

    def depth(self, side: int, n: int) -> list[tuple[int, int]]:
        """Top-n (price, qty) levels, best first."""
        prices = sorted(self.qty_at[side], reverse=(side == BUY))[:n]
        return [(p, self.qty_at[side][p]) for p in prices]

    # -- mutation ----------------------------------------------------------
    def _rest(self, order: Order) -> None:
        side, price = order.side, order.price
        level = self.levels[side].get(price)
        if level is None:
            level = self.levels[side][price] = deque()
        level.append(order)
        if self.qty_at[side].get(price, 0) <= 0:
            heapq.heappush(self._heaps[side], -price if side == BUY else price)
            self.qty_at[side][price] = 0
        self.qty_at[side][price] += order.qty
        self.orders[order.oid] = order

    def _reduce(self, order: Order, amount: int) -> None:
        side, price = order.side, order.price
        order.qty -= amount
        self.qty_at[side][price] -= amount
        if self.qty_at[side][price] <= 0:
            del self.qty_at[side][price]
            self.levels[side].pop(price, None)
        if order.qty <= 0:
            order.alive = False
            self.orders.pop(order.oid, None)

    def cancel(self, oid: int) -> Order | None:
        order = self.orders.get(oid)
        if order is None or not order.alive:
            return None
        remaining = order.qty
        self._reduce(order, remaining)
        order.qty = remaining  # keep the cancelled quantity for the caller
        order.alive = False
        return order

    def _execute(self, taker: Order, fills: list[Fill], stp: list[Order]) -> None:
        opp = -taker.side
        while taker.qty > 0:
            best = self.best(opp)
            if best is None:
                break
            if taker.price is not None:
                if (taker.side == BUY and best > taker.price) or (taker.side == SELL and best < taker.price):
                    break
            level = self.levels[opp][best]
            while level and not level[0].alive:
                level.popleft()
            if not level:
                self.qty_at[opp].pop(best, None)
                self.levels[opp].pop(best, None)
                continue
            maker = level[0]
            if maker.agent == taker.agent:
                level.popleft()
                cancelled_qty = maker.qty
                self._reduce(maker, cancelled_qty)
                maker.qty = cancelled_qty
                maker.alive = False
                stp.append(maker)
                continue
            qty = min(maker.qty, taker.qty)
            fills.append(Fill(best, qty, maker, taker))
            taker.qty -= qty
            self._reduce(maker, qty)
            if maker.qty <= 0:
                level.popleft()

    def submit(self, agent: int, side: int, price: int | None, qty: int, ts: int):
        """Submit a limit order (price given) or market order (price None).

        Returns (order, fills, self_trade_cancels). A limit order's remainder
        rests in the book; a market order's remainder is discarded.
        """
        order = Order(self._next_oid, agent, side, price, qty, ts)
        self._next_oid += 1
        fills: list[Fill] = []
        stp: list[Order] = []
        self._execute(order, fills, stp)
        if order.qty > 0 and price is not None:
            self._rest(order)
        return order, fills, stp
