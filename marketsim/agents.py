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
        # a fee per cancelled order makes frequent re-quoting less attractive (about 4 cancels per re-quote
        # against a typical gain of 8 per re-quote)
        if self.rng.random() > self.activity / (1 + ex.policy.cancel_fee * 4 / 8):
            return
        self.requote(ex)

    def requote(self, ex: Exchange) -> None:
        r = self.rng
        for oid in list(ex.open[self.aid]):
            ex.cancel(oid)
        if ex.open[self.aid]:
            return  # some quotes are locked by a minimum resting time: stay with them rather than stack new ones
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

    def __init__(self, aid, rng, window: tuple[int, int], evasion: float = 0.0, params: dict | None = None):
        super().__init__(aid, rng, activity=0.03)
        self.window = window
        self.evasion = evasion
        self.params = params or {}
        self.dilute = 0.0  # chance per step of also acting like a noise trader while manipulating
        self._cursor = 0
        self._net = 0

    def apply_params(self) -> None:
        for k, v in self.params.items():
            setattr(self, k, v)

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
            if self.dilute > 0 and self.rng.random() < self.dilute:
                saved, self.activity = self.activity, 1.0
                NoiseTrader.step(self, ex)
                self.activity = saved
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

    def __init__(self, aid, rng, window, evasion: float = 0.0, params: dict | None = None):
        super().__init__(aid, rng, window, evasion, params)
        e = evasion
        self.cool_lo, self.cool_hi, self.timeout = 20, 60, 30
        self.layers = 3 if e < 0.5 else 1 if e > 0.8 else 2
        self.fake_qty = max(20, int(250 * (1 - 0.8 * e)))
        self.dist = 1 + int(4 * e)
        self.hold_extra = 2 + int(15 * e)
        self.real_qty = 10
        self.apply_params()
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
            if self.cancel_at < 0 and (filled or t - self.t0 > self.timeout):
                self.cancel_at = t + self.hold_extra
            if self.cancel_at >= 0 and t >= self.cancel_at:
                for oid in self.fakes:
                    ex.cancel(oid)
                if any(oid in ex.open[self.aid] for oid in self.fakes):
                    return  # still locked: the fake orders stay exposed, retry next step
                ex.cancel(self.real_oid)
                self.state = "unwind"
                self.t0 = t
        elif self.state == "unwind":
            net = self.tagged_net(ex, "spoof_")
            if net == 0 or t - self.t0 > 40:
                self.stop_exit(ex)
                self.state, self.cool_until = "idle", t + int(r.integers(self.cool_lo, self.cool_hi))
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


class RingAccount(Manipulator):
    """One account of a colluding ring: trades like a noise trader unless the ring controller uses it."""

    kind = "ring"

    def step(self, ex: Exchange) -> None:
        NoiseTrader.step(self, ex)


RING_DEFAULT = {"acc_len": 60, "push_len": 25, "dist_len": 50, "p_acc": 0.4, "p_push": 0.8, "m_push": 2, "q": 3,
                "cross_frac": 0.2, "jitter": 0, "cool": 60}


class RingController:
    """A ring of K accounts that fragments a price-pushing campaign across accounts.

    Phases per cycle: accumulate (passive buys by random members), push (near-simultaneous aggressive buys by
    several members plus cross trades between members), distribute (passive sells of inventory). Members only
    sell what they hold (no short selling). `jitter` spreads the members' actions over time, which weakens the
    synchrony between accounts at the cost of a weaker push.

    The ring's benefit is a block it sells off-book at the end of each push, valued at the price displacement
    achieved: utility = block * displacement + trading profit.
    """

    def __init__(self, members: list[RingAccount], rng: np.random.Generator, window: tuple[int, int],
                 params: dict | None = None, block: int = 200):
        self.members = members
        self.rng = rng
        self.window = window
        self.block = block
        self.p = {**RING_DEFAULT, **(params or {})}
        self.state = "idle"
        self.cool_until = window[0]
        self.phase_end = 0
        self.queue: list[tuple[int, int, str, int]] = []  # (due step, member index, action, qty)
        self.cycles: list[dict] = []
        self._cursor = 0
        self._inv = {m.aid: 0 for m in members}

    def _update_inventory(self, ex: Exchange) -> None:
        ids = self._inv
        for a, tag, side, _, qty, _t in ex.gt_trades[self._cursor:]:
            if a in ids and tag.startswith("ring_"):
                ids[a] += side * qty
        self._cursor = len(ex.gt_trades)

    def _schedule(self, ex: Exchange, member: int, action: str, qty: int) -> None:
        j = self.p["jitter"]
        due = ex.t + (int(self.rng.integers(0, j + 1)) if j else 0)
        self.queue.append((due, member, action, qty))

    def _run_due(self, ex: Exchange) -> None:
        keep = []
        for due, mi, action, qty in self.queue:
            if due > ex.t:
                keep.append((due, mi, action, qty))
                continue
            m = self.members[mi]
            if action == "acc" and ex.best_bid() is not None:
                ex.limit(m.aid, BUY, ex.best_bid(), qty, tag="ring_acc")
            elif action == "push":
                ex.market(m.aid, BUY, qty, tag="ring_push")
            elif action == "dist" and self._inv[m.aid] > 0 and ex.best_ask() is not None:
                ex.limit(m.aid, SELL, ex.best_ask(), min(qty, self._inv[m.aid]), tag="ring_dist")
        self.queue = keep

    def step(self, ex: Exchange) -> None:
        r, p, t = self.rng, self.p, ex.t
        self._update_inventory(ex)
        self._run_due(ex)
        if not (self.window[0] <= t < self.window[1]):
            return
        K = len(self.members)
        if self.state == "idle":
            if t >= self.cool_until:
                self.state, self.phase_end = "acc", t + p["acc_len"]
                self.cycles.append({"start": t, "mid0": ex.mid()})
            return
        if self.state == "acc":
            if t >= self.phase_end:
                self.state, self.phase_end = "push", t + p["push_len"]
            elif r.random() < p["p_acc"]:
                self._schedule(ex, int(r.integers(K)), "acc", p["q"])
        elif self.state == "push":
            if t >= self.phase_end:
                self.cycles[-1].update(end_push=t, mid1=ex.mid())
                self.state, self.phase_end = "dist", t + p["dist_len"]
            elif r.random() < p["p_push"]:
                for mi in r.choice(K, size=min(K, p["m_push"]), replace=False):
                    self._schedule(ex, int(mi), "push", p["q"])
                if r.random() < p["cross_frac"] and K >= 2:
                    self._cross(ex)
        elif self.state == "dist":
            held = [i for i, m in enumerate(self.members) if self._inv[m.aid] > 0]
            if t >= self.phase_end or not held:
                self.state, self.cool_until = "idle", t + p["cool"]
                return
            if r.random() < 0.5:
                self._schedule(ex, int(r.choice(held)), "dist", p["q"])

    def _cross(self, ex: Exchange) -> None:
        bid, ask = ex.best_bid(), ex.best_ask()
        if bid is None or ask is None or ask - bid < 2:
            return
        holders = [i for i, m in enumerate(self.members) if self._inv[m.aid] > 0]
        if not holders:
            return  # no short selling: only a member holding stock can sell to another
        a = int(self.rng.choice(holders))
        b = int(self.rng.choice([i for i in range(len(self.members)) if i != a]))
        price = int(self.rng.integers(bid + 1, ask))
        qty = min(int(self.p["q"]), self._inv[self.members[a].aid])
        ex.limit(self.members[a].aid, SELL, price, qty, tag="ring_cross")
        ex.limit(self.members[b].aid, BUY, price, qty, tag="ring_cross")


# --------------------------------------------------------------------------
# honest groups that act in step with each other (confounders for coordination tests)
# --------------------------------------------------------------------------
class GroupMember(NoiseTrader):
    """Sub-account of an honest group: trades like a noise trader unless its group acts."""

    kind = "group_member"


class SliceFund:
    """One institution splitting parent orders across sub-accounts: one-way, same-step child orders, no round trip."""

    kind = "fund_sub"

    def __init__(self, members, rng, mean_gap: int = 450):
        self.members, self.rng, self.mean_gap = members, rng, mean_gap
        self.remaining, self.side, self.end = 0, BUY, -1
        self.next_start = 300 + int(rng.exponential(mean_gap))

    def step(self, ex: Exchange) -> None:
        r = self.rng
        if self.remaining <= 0:
            if ex.t >= self.next_start:
                self.remaining = int(r.integers(400, 1200))
                self.side = BUY if r.random() < 0.5 else SELL
                self.end = ex.t + int(r.integers(100, 250))
                self.next_start = self.end + int(r.exponential(self.mean_gap))
            return
        if ex.t >= self.end:
            self.remaining = 0
            return
        if r.random() < 0.5:
            for mi in r.choice(len(self.members), size=min(len(self.members), int(r.integers(2, 4))), replace=False):
                qty = min(self.remaining, 3 + int(r.integers(0, 4)))
                if qty > 0:
                    ex.market(self.members[mi].aid, self.side, qty)
                    self.remaining -= qty


class BotFleet:
    """Bots that react to the same public price signal with small latency differences, in either direction."""

    kind = "bot_fleet"

    def __init__(self, members, rng, thr: float = 3.0, lookback: int = 10):
        self.members, self.rng, self.thr, self.lookback = members, rng, thr, lookback
        self.queue: list[tuple[int, int, int]] = []

    def step(self, ex: Exchange) -> None:
        r = self.rng
        keep = []
        for due, mi, side in self.queue:
            if due <= ex.t:
                ex.market(self.members[mi].aid, side, 1 + int(r.integers(0, 3)))
            else:
                keep.append((due, mi, side))
        self.queue = keep
        move = ex.mid() - ex.mid_at(self.lookback)
        if abs(move) >= self.thr:
            side = BUY if move > 0 else SELL
            for mi in range(len(self.members)):
                if r.random() < 0.5:
                    self.queue.append((ex.t + int(r.integers(0, 3)), mi, side))


class MMDesks:
    """Several market-making desks of one firm that re-quote together (same steps, both sides)."""

    kind = "mm_desk"

    def __init__(self, desks, rng, period: tuple[int, int] = (8, 15)):
        self.desks, self.rng, self.period = desks, rng, period
        self.next = 0

    def step(self, ex: Exchange) -> None:
        if ex.t >= self.next:
            for d in self.desks:
                d.requote(ex)
            self.next = ex.t + int(self.rng.integers(*self.period))
