# Scaling law against the agent-based sensitivity results

Two fitted constants: s0 = 1.20 (shift in standard units of the statistic at N = 100 and push probability 0.8) and a ceiling a = 0.90 (share of ring-active windows in which the signal is present). Mean absolute error over the 11 points: 0.043. With the exponent of N left free: gamma = 0.32 (theory 0.5).

| sweep            |   level |       N |   K |   push |   catch |   predicted |   predicted (held-out sweep) |
|:-----------------|--------:|--------:|----:|-------:|--------:|------------:|-----------------------------:|
| accounts         |   100   | 100.253 |  12 |    0.8 |    0.91 |       0.899 |                        0.908 |
| accounts         |   206   | 205.549 |  12 |    0.8 |    0.84 |       0.806 |                        0.736 |
| accounts         |   373   | 372.934 |  12 |    0.8 |    0.64 |       0.551 |                        0.462 |
| accounts         |   708   | 708.046 |  12 |    0.8 |    0.28 |       0.274 |                        0.223 |
| ring size        |     4   |  93.47  |   4 |    0.8 |    0.79 |       0.813 |                        0.813 |
| ring size        |     8   |  97.102 |   8 |    0.8 |    0.88 |       0.89  |                        0.865 |
| ring size        |    16   | 103.609 |  16 |    0.8 |    0.94 |       0.9   |                        0.87  |
| ring size        |    30   | 114.914 |  30 |    0.8 |    0.94 |       0.9   |                        0.87  |
| push probability |     0.2 |  99.816 |  12 |    0.2 |    0.46 |       0.647 |                        0.671 |
| push probability |     0.4 | 100.217 |  12 |    0.4 |    0.79 |       0.815 |                        0.841 |
| push probability |     0.8 | 100.253 |  12 |    0.8 |    0.91 |       0.899 |                        0.912 |

## Cross-validation by held-out sweep

| held-out sweep   |    s0 |   ceiling a |   mean abs. error |
|:-----------------|------:|------------:|------------------:|
| accounts         | 0.963 |       0.918 |             0.085 |
| ring size        | 1.312 |       0.87  |             0.045 |
| push probability | 1.284 |       0.913 |             0.088 |
