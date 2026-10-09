# Real-data statistics (Vietnam)

Index bars: Kaggle dataset `keithvo/vnstockdata` (ODbL). Futures ticks: Kaggle dataset `khimduong/vn30-market-making` (license not stated; provenance of the ticks not documented). Neither contains account identifiers or order-level events. Raw files are not stored in this repository.

## Index returns

| series         | from       | to         |   sd % (all) |   sd % (2023+) |   excess kurtosis |   autocorr |r| lag1 |   autocorr |r| lag5 |
|:---------------|:-----------|:-----------|-------------:|---------------:|------------------:|--------------------:|--------------------:|
| VN30 daily     | 2012-09-10 | 2025-12-12 |        1.194 |          1.157 |             4.749 |               0.195 |               0.165 |
| VN-Index daily | 2000-07-28 | 2025-12-12 |        1.438 |          1.089 |             3.58  |               0.46  |               0.363 |
| VN100 daily    | 2014-01-27 | 2025-12-12 |        1.191 |          1.191 |             5.217 |               0.234 |               0.172 |

VN30 30-minute bars since 2023: median 10 bars per day, intraday 30-minute return sd 0.302%.

## VN30F1M ticks (real)

1,562,136 quote-bearing ticks over 319 trading days (2024-01-02 to 2025-04-28); index price about 1302 points, tick 0.1 point, so one tick is 0.8 bp.

- Spread in ticks (share of ticks): 1: 0.730, 2: 0.158, 3: 0.063, 4: 0.025, 5+: 0.024
- Mean spread 0.150 points = 1.1 bp; median 1 tick.
- Ticks per trading day: median 4937; mean gap between ticks 2.1 s (median).
- Daily return sd 1.163% (from last tick of each day), excess kurtosis 15.09.
- One-minute return sd 0.0536%; excess kurtosis 42.4.
- Price changes per tick: share of non-zero changes 0.668; mean absolute change 1.14 ticks.
