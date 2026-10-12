# Ensemble conclusions with intervals over markets

Ratio = ring gain with the block-price rule over ring gain with the band alone (markets with positive band-only gain). Bootstrap over markets (5000 draws) for the median; exact two-sided sign test of 'lower gain with the rule'. Inspection: share of markets in which the ring's net benefit at fine multiple 5 stays positive.

|                                              | 0             | 1             | 2             | 3             |
|:---------------------------------------------|:--------------|:--------------|:--------------|:--------------|
| family                                       | index level   | stock level   | trend-free    | all markets   |
| markets                                      | 6             | 6             | 4             | 16            |
| block 60: median ratio                       | 0.368         | 0.429         | 0.045         | 0.36          |
| block 60: 95% CI of median                   | 0.19 to 0.51  | 0.13 to 0.63  | -0.05 to 0.88 | 0.13 to 0.55  |
| block 60: range                              | 0.13 to 0.55  | 0.06 to 0.69  | -0.05 to 0.88 | -0.05 to 0.88 |
| block 60: markets with lower gain            | 6/6           | 6/6           | 3/3           | 15/15         |
| block 60: sign-test p                        | 0.031         | 0.031         | 0.25          | 0.0           |
| block 240: median ratio                      | 0.111         | 0.195         | -0.013        | 0.116         |
| block 240: 95% CI of median                  | 0.01 to 0.22  | -0.01 to 0.42 | -0.02 to 0.48 | -0.01 to 0.24 |
| block 240: range                             | -0.01 to 0.23 | -0.07 to 0.50 | -0.02 to 0.48 | -0.07 to 0.50 |
| block 240: markets with lower gain           | 6/6           | 6/6           | 3/3           | 15/15         |
| block 240: sign-test p                       | 0.031         | 0.031         | 0.25          | 0.0           |
| inspect 3: markets with positive net benefit | 1/6           | 1/6           | 2/4           | 4/16          |
| inspect 3: Wilson 95%                        | 0.03 to 0.56  | 0.03 to 0.56  | 0.15 to 0.85  | 0.10 to 0.49  |
| inspect 3: median caught                     | 0.417         | 0.25          | 0.042         | 0.208         |