"""Simulator preset for a mid-cap stock on the Ho Chi Minh Stock Exchange (HOSE).

Mapping, with sources and confidence in docs/vietnam_calibration.md:
  1 price tick   = 1 HOSE tick (50 VND on the 10,000-49,950 VND band); reference price 25,000 VND = 500 ticks
  1 quantity unit = one round lot (100 shares)
  1 step         = about one trading minute; a trading day = 240 steps
  daily price band +/-7% of the previous close
Participant mix, cancel share and relative tick are matched to published figures (retail 0.795 vs 0.80, cancel
share 0.323 vs 0.318, relative tick 20 bps). Spread and volatility are not matched: no published spread was found,
and the simulated daily volatility (about 0.4%) is below the assumed 1.5% of a typical stock.
"""

from __future__ import annotations

from dataclasses import replace

from .policy import Policy
from .sim import SimConfig

VN_POLICY = Policy("HOSE band 7%", band=0.07, day_len=240)


def vn_config(**overrides) -> SimConfig:
    base = SimConfig(start_price=500, policy=VN_POLICY, n_noise=400, mm_activity=0.05)
    return replace(base, **overrides)
