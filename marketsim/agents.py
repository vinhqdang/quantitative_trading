"""Heterogeneous agents.

Honest agents: noise traders, market makers, fundamental traders, momentum
traders, order-book-imbalance traders and institutions slicing parent orders.
Manipulators: spoofer, pump-and-dump, wash-trading pair. Each manipulator has
an `evasion` level in [0, 1] that makes it smaller, slower and less
cancellation-heavy, and trades honestly (as a noise trader) outside its active
window.
"""

from __future__ import annotations

import math

import numpy as np

from .exchange import Exchange
from .lob import BUY, SELL


class Agent:
    kind = "base"
    manipulator = False

    def __init__(self, aid: int, rng: np.random.Generator):
        self.aid = aid
        self.rng = rng

    def step(self, ex: Exchange) -> None:  # pragma: no cover - interface
        raise NotImplementedError


# --------------------------------------------------------------------------
# honest agents
# --------------------------------------------------------------------------
class NoiseTrader(Agent):
    kind = "noise"

    def __init__(self, aid, rng, activity: float = 0.05):
        super().__init__(aid, rng)
        self.activity = activity

    def step(self, ex: Exchange) -> None:
        r = self.rng
        if r.random() > self.activity:
            return
        open_ids = ex.open[self.aid]
        if open_ids and r.random() < 0.15:
            ex.cancel(next(iter(open_ids)))
            return
        if len(open_ids) >= 5:
            return
        side = BUY if r.random() < 0.5 else SELL
        qty = 1 + int(r.exponential(3))
        if r.random() < 0.35:
            ex.market(self.aid, side, qty)
        else:
            off = 1 + int(r.exponential(4))
            mid = ex.mid()
            price = math.floor(mid) - off if side == BUY else math.ceil(mid) + off
            ex.limit(self.aid, side, price, qty)


class MarketMaker(Agent):
    """Re-quotes both sides at two levels, shifting with displayed depth imbalance; cancels all its quotes."""

    kind = "market_maker"

    def __init__(self, aid, rng, activity: float = 0.3, inv_limit: int = 60, imb_sens: float = 2.5):
        super().__init__(aid, rng)
        self.activity = activity
        self.inv_limit = inv_limit
        self.imb_sens = imb_sens
        self.half = 1 + int(rng.integers(0, 2))

    def step(self, ex: Exchange) -> None:
        r = self.rng
        if r.random() > self.activity:
            return
        for oid in list(ex.open[self.aid]):
            ex.cancel(oid)
        inv = ex.inv[self.aid]
        # depth shown on one side is read as pressure: quotes shift towards the heavier side's opposite
        mid = ex.mid() + self.imb_sens * ex.imbalance(5)
        skew = 0.05 * inv
        qty = 4 + int(r.integers(0, 9))
        for lvl, extra in enumerate((0, 2)):
            bid = math.floor(mid - self.half - extra - skew)
            ask = math.ceil(mid + self.half + extra - skew)
            if inv < self.inv_limit:
                ex.limit(self.aid, BUY, bid, qty)
            if inv > -self.inv_limit:
                ex.limit(self.aid, SELL, ask, qty)


class FundamentalTrader(Agent):
    kind = "fundamental"

    def __init__(self, aid, rng, activity: float = 0.08, noise: float = 3.0):
        super().__init__(aid, rng)
        self.activity = activity
        self.noise = noise

    def step(self, ex: Exchange) -> None:
        r = self.rng
        if r.random() > self.activity:
            return
        gap = ex.fund + r.normal(0, self.noise) - ex.mid()
        qty = 1 + int(r.integers(0, 5))
        if abs(gap) < 2:
            return
        side = BUY if gap > 0 else SELL
        if abs(gap) > 4:
            ex.market(self.aid, side, qty)
        else:
            ex.limit(self.aid, side, round(ex.mid()) - side, qty)


class MomentumTrader(Agent):
    kind = "momentum"

    def __init__(self, aid, rng, activity: float = 0.08, lookback: int = 20, thr: float = 3.0, cap: float = 12.0):
        super().__init__(aid, rng)
        self.activity, self.lookback, self.thr, self.cap = activity, lookback, thr, cap

    def step(self, ex: Exchange) -> None:
        if self.rng.random() > self.activity:
            return
        move = ex.mid() - ex.mid_at(self.lookback)
        # follows moves between thr and cap ticks; larger moves are treated as overextended
        if self.thr <= abs(move) <= self.cap:
            ex.market(self.aid, BUY if move > 0 else SELL, 1 + int(self.rng.integers(0, 5)))


class ImbalanceTrader(Agent):
    """Trades in the direction of near-touch depth imbalance.

    This is the mechanism through which displayed-but-fake liquidity moves
    prices; without it spoofing would not be profitable.
    """

    kind = "imbalance"

    def __init__(self, aid, rng, activity: float = 0.15, thr: float = 0.5):
        super().__init__(aid, rng)
        self.activity, self.thr = activity, thr

    def step(self, ex: Exchange) -> None:
        if self.rng.random() > self.activity:
            return
        imb = ex.imbalance(5)
        if abs(imb) >= self.thr:
            ex.market(self.aid, BUY if imb > 0 else SELL, 1 + int(self.rng.integers(0, 4)))


class Institution(Agent):
    """Slices a large parent order into market-order child orders (legit lookalike of accumulation)."""

    kind = "institution"

    def __init__(self, aid, rng, mean_gap: int = 900):
        super().__init__(aid, rng)
        self.mean_gap = mean_gap
        self.remaining = 0
        self.side = BUY
        self.end = -1
        self.next_start = int(rng.exponential(mean_gap)) + 300

    def step(self, ex: Exchange) -> None:
        r = self.rng
        if self.remaining <= 0:
            if ex.t >= self.next_start:
                self.remaining = int(r.integers(150, 300))
                self.side = BUY if r.random() < 0.5 else SELL
                self.end = ex.t + int(r.integers(60, 120))
                self.next_start = self.end + int(r.exponential(self.mean_gap))
            return
        if ex.t >= self.end:
            self.remaining = 0
            return
        if r.random() < 0.5:
            qty = min(self.remaining, 2 + int(r.integers(0, 5)))
            ex.market(self.aid, self.side, qty)
            self.remaining -= qty


# --------------------------------------------------------------------------
# manipulators
# --------------------------------------------------------------------------
class Manipulator(NoiseTrader):
    """Base: honest noise trading outside the active window."""

    manipulator = True

    def __init__(self, aid, rng, window: tuple[int, int], evasion: float = 0.0):
        super().__init__(aid, rng, activity=0.03)
        self.window = window
        self.evasion = evasion
        self._cursor = 0
        self._net = 0

    def tagged_net(self, ex: Exchange, prefix: str) -> int:
        """Net position (buys minus sells) built through this agent's tagged orders."""
        trades = ex.gt_trades
        for a, tag, side, _, qty, _t in trades[self._cursor:]:
            if a == self.aid and tag.startswith(prefix):
                self._net += side * qty
        self._cursor = len(trades)
        return self._net

    def exit_step(self, ex: Exchange, net: int, tag: str, patience: int = 8) -> None:
        """Reduce `net` by joining the touch passively; cross the spread if it is not filled in time."""
        d = SELL if net > 0 else BUY
        oid = getattr(self, "exit_oid", -1)
        if oid in ex.open[self.aid]:
            if ex.t - self.exit_t > patience:
                ex.cancel(oid)
                self.exit_oid = -1
                ex.market(self.aid, d, min(abs(net), 10), tag=tag)
            return
        touch = ex.best_ask() if d == SELL else ex.best_bid()
        if touch is None:
            return
        self.exit_oid = ex.limit(self.aid, d, touch, min(abs(net), 10), tag=tag)
        self.exit_t = ex.t

    def stop_exit(self, ex: Exchange) -> None:
        oid = getattr(self, "exit_oid", -1)
        if oid in ex.open[self.aid]:
            ex.cancel(oid)
        self.exit_oid = -1

    def active(self, ex: Exchange) -> bool:
        return self.window[0] <= ex.t < self.window[1]

    def step(self, ex: Exchange) -> None:
        if self.active(ex):
            self.manipulate(ex)
        else:
            NoiseTrader.step(self, ex)

    def manipulate(self, ex: Exchange) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class Spoofer(Manipulator):
    """Layered spoofing: show large orders on one side, trade the other, cancel.

    To buy cheaply it places large *sell* orders a few ticks above the best
    ask. Imbalance traders sell into the apparent supply, a small genuine buy
    order is filled at the lower price, the fake orders are cancelled and the
    inventory is sold back once the price recovers.
    """

    kind = "spoofer"

    def __init__(self, aid, rng, window, evasion: float = 0.0):
        super().__init__(aid, rng, window, evasion)
        e = evasion
        self.layers = 3 if e < 0.5 else 1 if e > 0.8 else 2
        self.fake_qty = max(20, int(250 * (1 - 0.8 * e)))
        self.dist = 1 + int(4 * e)
        self.hold_extra = 2 + int(15 * e)
        self.real_qty = 10
        self.state = "idle"
        self.cool_until = window[0]
        self.fakes: list[int] = []
        self.real_oid = -1
        self.t0 = 0
        self.cancel_at = 0
        self.direction = BUY

    def manipulate(self, ex: Exchange) -> None:
        t, r = ex.t, self.rng
        if self.state == "idle":
            if t < self.cool_until or ex.best_bid() is None or ex.best_ask() is None:
                return
            self.direction = BUY if r.random() < 0.5 else SELL
            d = self.direction
            base = ex.best_ask() if d == BUY else ex.best_bid()
            self.fakes = []
            for i in range(self.layers):
                price = base + (self.dist + i) * d
                self.fakes.append(ex.limit(self.aid, -d, price, self.fake_qty, tag="spoof_fake"))
            real_price = ex.best_bid() if d == BUY else ex.best_ask()
            self.real_oid = ex.limit(self.aid, d, real_price, self.real_qty, tag="spoof_real")
            self.t0, self.cancel_at, self.state = t, -1, "spoofing"
        elif self.state == "spoofing":
            filled = self.real_oid not in ex.open[self.aid]
            if self.cancel_at < 0 and (filled or t - self.t0 > 30):
                self.cancel_at = t + self.hold_extra
            if self.cancel_at >= 0 and t >= self.cancel_at:
                for oid in self.fakes:
                    ex.cancel(oid)
                ex.cancel(self.real_oid)
                self.state = "unwind"
                self.t0 = t
        elif self.state == "unwind":
            net = self.tagged_net(ex, "spoof_")
            if net == 0 or t - self.t0 > 40:
                self.stop_exit(ex)
                self.state, self.cool_until = "idle", t + int(r.integers(20, 60))
                return
            self.exit_step(ex, net, "spoof_unwind")


class PumpAndDump(Manipulator):
    """Accumulate quietly, push the price with aggressive buys, sell into the momentum."""

    kind = "pump_dump"

    def __init__(self, aid, rng, window, evasion: float = 0.0):
        super().__init__(aid, rng, window, evasion)
        self.speed = 1 - 0.6 * evasion
        self.state = "idle"
        self.cool_until = window[0]
        self.phase_end = 0

    def manipulate(self, ex: Exchange) -> None:
        t, r = ex.t, self.rng
        if self.state == "idle":
            if t >= self.cool_until:
                self.state, self.phase_end = "accumulate", t + int(r.integers(30, 50) / self.speed)
            return
        if self.state == "accumulate":
            if t >= self.phase_end:
                self.state, self.phase_end = "pump", t + int(r.integers(10, 20) / self.speed)
            elif r.random() < 0.5 * self.speed:
                qty = 2 + int(r.integers(0, 3))
                ex.market(self.aid, BUY, qty, tag="pd_accumulate")
        elif self.state == "pump":
            if t >= self.phase_end:
                self.state, self.phase_end = "dump", t + 60
            else:
                qty = max(1, int((5 + int(r.integers(0, 6))) * self.speed))
                ex.market(self.aid, BUY, qty, tag="pd_pump")
        elif self.state == "dump":
            pos = self.tagged_net(ex, "pd_")
            if pos <= 0 or t >= self.phase_end:
                self.stop_exit(ex)
                self.state, self.cool_until = "idle", t + int(r.integers(40, 100))
                return
            self.exit_step(ex, pos, "pd_dump", patience=5)


class WashPair:
    """Two colluding accounts that trade with each other to fake volume."""

    def __init__(self, a: "WashAccount", b: "WashAccount", rng: np.random.Generator, window, evasion: float = 0.0):
        self.a, self.b, self.rng, self.window = a, b, rng, window
        self.prob = 0.25 * (1 - 0.8 * evasion)
        self.qty_range = (5, 16) if evasion < 0.5 else (2, 6)

    def cross(self, ex: Exchange) -> None:
        r = self.rng
        if not (self.window[0] <= ex.t < self.window[1]) or r.random() > self.prob:
            return
        bid, ask = ex.best_bid(), ex.best_ask()
        if bid is None or ask is None or ask - bid < 2:
            return
        price = int(r.integers(bid + 1, ask))
        seller, buyer = (self.a, self.b) if r.random() < 0.5 else (self.b, self.a)
        qty = int(r.integers(*self.qty_range))
        ex.limit(seller.aid, SELL, price, qty, tag="wash")
        ex.limit(buyer.aid, BUY, price, qty, tag="wash")


class WashAccount(Manipulator):
    kind = "wash"

    def __init__(self, aid, rng, window, evasion: float = 0.0):
        super().__init__(aid, rng, window, evasion)
        self.pair: WashPair | None = None

    def step(self, ex: Exchange) -> None:
        # the pair controller drives the collusive trades; otherwise act honestly
        NoiseTrader.step(self, ex)
