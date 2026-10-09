"""Simulator preset for a mid-cap stock on the Ho Chi Minh Stock Exchange (HOSE).

Mapping, with sources and confidence in docs/vietnam_calibration.md:
  1 price tick   = 1 HOSE tick (50 VND on the 10,000-49,950 VND band); reference price 25,000 VND = 500 ticks
  1 quantity unit = one round lot (100 shares)
  1 step         = about one trading minute; a trading day = 240 steps
  daily price band +/-7% of the previous close
Participant mix, cancel share and relative tick are matched to published figures; spread and volatility are
not (no published figures were found).
"""

from __future__ import annotations

from dataclasses import replace

from .policy import Policy
from .sim import SimConfig

VN_POLICY = Policy("HOSE band 7%", band=0.07, day_len=240)


def vn_config(**overrides) -> SimConfig:
    base = SimConfig(start_price=500, policy=VN_POLICY)
    return replace(base, **overrides)
