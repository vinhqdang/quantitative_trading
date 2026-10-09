"""Simulator preset for a mid-cap stock on the Ho Chi Minh Stock Exchange (HOSE).

Mapping, with sources and confidence in docs/vietnam_calibration.md:
  1 price tick   = 1 HOSE tick (50 VND on the 10,000-49,950 VND band); reference price 25,000 VND = 500 ticks
  1 quantity unit = one round lot (100 shares)
  1 step         = about one trading minute; a trading day = 240 steps
  daily price band +/-7% of the previous close
Matched: cancel share (0.321 vs published 0.318), relative tick (21 vs 20 bp), daily volatility (1.14% vs 1.16% measured
for VN30 since 2023; see results/real_data_stats.md). Retail share is 0.72 against a published 0.75-0.82. Not matched:
the spread (3 ticks against a measured 1 tick in 73% of VN30 futures quotes), tail heaviness and volatility clustering.
"""

from __future__ import annotations

from dataclasses import replace

from .policy import Policy
from .sim import SimConfig

VN_POLICY = Policy("HOSE band 7%", band=0.07, day_len=240)


def vn_config(**overrides) -> SimConfig:
    base = SimConfig(start_price=500, policy=VN_POLICY, n_noise=500, n_fund=40, mm_activity=0.10)
    return replace(base, **overrides)
