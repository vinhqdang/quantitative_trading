# Order-level policy levers

10 honest-only episodes per policy for market quality; 16 episodes with the default manipulators (same seeds across policies). Market makers respond to the policy (they skip re-quoting while any quote is locked and re-quote less often under a cancel fee); other honest agents do not adapt. Manipulators do not adapt either.

Market quality (honest-only markets). Lower is better for spread, volatility, tracking error and retail cost; higher is better for depth and volume. `noise_cost` includes cancel fees paid.

| policy            |   spread |   depth |   vol |   tracking_error |   noise_cost |   volume |   halted |
|:------------------|---------:|--------:|------:|-----------------:|-------------:|---------:|---------:|
| baseline          |    2.605 | 587.165 | 0.213 |            5.272 |        2.187 |    3.985 |    0     |
| tick x2           |    3.786 | 544.403 | 0.255 |            5.385 |        1.796 |    4.274 |    0     |
| tick x4           |    5.839 | 567.51  | 0.318 |            5.482 |        1.012 |    4.668 |    0     |
| min rest 5        |    2.596 | 589.703 | 0.203 |            5.495 |        2.437 |    3.977 |    0     |
| min rest 15       |    2.687 | 593.424 | 0.222 |            5.691 |        2.527 |    3.918 |    0     |
| cancel fee 0.5    |    2.609 | 588.123 | 0.215 |            5.603 |        2.288 |    4.022 |    0     |
| cancel fee 2      |    2.637 | 585.763 | 0.21  |            5.297 |        2.977 |    3.958 |    0     |
| circuit breaker 6 |    2.625 | 585.471 | 0.217 |            5.161 |        2.064 |    3.958 |    0.005 |


Fixed manipulators. `spoof_profit` = realised spoofing profit per episode (tick-shares); impacts in ticks in the manipulator's intended direction.

| policy            |   spoof_profit |   spoof_impact |   pump_impact |
|:------------------|---------------:|---------------:|--------------:|
| baseline          |          55.56 |           1.07 |          1.53 |
| tick x2           |         184.38 |           0.9  |          1.53 |
| tick x4           |         687.25 |           0.8  |          1.57 |
| min rest 5        |          13.44 |           1.08 |          1.31 |
| min rest 15       |        -346.47 |           0.89 |          1.14 |
| cancel fee 0.5    |          56.31 |           1.13 |          1.5  |
| cancel fee 2      |         127.94 |           1.02 |          1.41 |
| circuit breaker 6 |          42.62 |           1.1  |          1.5  |


Change relative to baseline (percent):

| policy            |   spread |   depth |   vol |   tracking_error |   noise_cost |   volume |   spoof_impact |   pump_impact |
|:------------------|---------:|--------:|------:|-----------------:|-------------:|---------:|---------------:|--------------:|
| baseline          |        0 |       0 |     0 |                0 |            0 |        0 |              0 |             0 |
| tick x2           |       45 |      -7 |    20 |                2 |          -18 |        7 |            -16 |             0 |
| tick x4           |      124 |      -3 |    50 |                4 |          -54 |       17 |            -25 |             3 |
| min rest 5        |       -0 |       0 |    -4 |                4 |           11 |       -0 |              1 |           -14 |
| min rest 15       |        3 |       1 |     4 |                8 |           16 |       -2 |            -17 |           -25 |
| cancel fee 0.5    |        0 |       0 |     1 |                6 |            5 |        1 |              5 |            -2 |
| cancel fee 2      |        1 |      -0 |    -1 |                0 |           36 |       -1 |             -5 |            -8 |
| circuit breaker 6 |        1 |      -0 |     2 |               -2 |           -6 |       -1 |              3 |            -2 |

