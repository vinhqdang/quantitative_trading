# Tick reform: inference by placebo dates, label permutation and pre-trend test

Placebo dates every 10 trading days over 2015-2018 (windows 40+40 days, gap 5 days), excluding dates whose windows overlap the reform's; 57 placebo dates with at least 50 treated and 50 control stocks.

## True estimate against the placebo distribution

| outcome           |   true DiD |   placebo mean |   placebo sd |   placebo 2.5% |   placebo 97.5% |   share of placebos with DiD <= true |   two-sided placebo p |   z (true vs placebo sd) |   number of placebo dates |
|:------------------|-----------:|---------------:|-------------:|---------------:|----------------:|-------------------------------------:|----------------------:|-------------------------:|--------------------------:|
| CS spread (%)     |    -0.0613 |        -0.0011 |       0.0536 |        -0.1238 |          0.0794 |                               0.1228 |                0.2632 |                  -1.1232 |                        57 |
| zero-return share |    -0.0709 |        -0.0036 |       0.0157 |        -0.0259 |          0.0353 |                               0      |                0      |                  -4.2841 |                        57 |
| daily range (%)   |    -0.0672 |         0.0167 |       0.2017 |        -0.4153 |          0.324  |                               0.2807 |                0.7018 |                  -0.4163 |                        57 |

## Permutation of the exchange labels at the true date

| outcome           |   true DiD |   permutation sd |   two-sided permutation p |   n permutations |
|:------------------|-----------:|-----------------:|--------------------------:|-----------------:|
| CS spread (%)     |    -0.0613 |           0.0357 |                    0.0836 |             5000 |
| daily range (%)   |    -0.0672 |           0.0834 |                    0.4182 |             5000 |
| zero-return share |    -0.0709 |           0.0117 |                    0      |             5000 |

## Pre-trend of the weekly spread difference (weeks -8 to -1)

|   pre-period weeks |   mean difference pre |   sd of weekly differences pre |   pre slope per week |   slope t-stat |   mean difference post (weeks 1-8) |   post mean in units of the pre sd |
|-------------------:|----------------------:|-------------------------------:|---------------------:|---------------:|-----------------------------------:|-----------------------------------:|
|                  8 |               -0.0017 |                         0.0788 |              -0.0104 |        -0.8403 |                            -0.0613 |                            -0.7781 |

## Sample composition (stocks)

| group     |   with any data (min 100 days) |   listed before pre-window start |   20+ days in pre-window |   20+ days in post-window |
|:----------|-------------------------------:|---------------------------------:|-------------------------:|--------------------------:|
| HOSE      |                            389 |                              282 |                      282 |                       284 |
| HNX+UPCoM |                            926 |                              483 |                      489 |                       500 |
