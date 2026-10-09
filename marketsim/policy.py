"""Regulatory levers applied by the exchange."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Policy:
    name: str = "baseline"
    tick: int = 1             # minimum price increment, in base ticks
    min_rest: int = 0         # steps an order must rest before it can be cancelled
    cancel_fee: float = 0.0   # cash charged per cancelled order
    halt_move: float = 0.0    # circuit breaker: halt if |mid change| over halt_window exceeds this many ticks (0 = off)
    halt_window: int = 20
    halt_len: int = 15        # steps new orders are rejected after a trigger (cancels are still allowed)
    band: float = 0.0         # daily price band as a fraction of the reference price (0 = off); limit orders outside are rejected
    day_len: int = 240        # steps per trading day; the reference price resets to the last mid at each day boundary
