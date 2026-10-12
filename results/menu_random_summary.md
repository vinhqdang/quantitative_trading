# Larger strategy menu (4 strategies against 4 + 24 random)

Two-stage selection on separate episodes, reported gains on 12 further episodes per cell; medians over markets.

|                                                                        | 0           | 1           | 2          | 3           |
|:-----------------------------------------------------------------------|:------------|:------------|:-----------|:------------|
| family                                                                 | index level | stock level | trend-free | all markets |
| markets                                                                | 6           | 6           | 4          | 16          |
| band 7%: gain, menu of 4 (median)                                      | 124473.396  | 223576.708  | 33802.167  | 106438.833  |
| band 7%: gain, larger menu (median)                                    | 124473.396  | 223576.708  | 30261.083  | 106438.833  |
| band 7%: markets where larger menu gives more                          | 0           | 0           | 0          | 0           |
| band 7% + block at 240-step mean: gain, menu of 4 (median)             | 28378.417   | 92991.271   | 5609.021   | 23049.375   |
| band 7% + block at 240-step mean: gain, larger menu (median)           | 28378.417   | 92991.271   | 2013.719   | 23049.375   |
| band 7% + block at 240-step mean: markets where larger menu gives more | 0           | 0           | 0          | 0           |
| band 7% + inspect 3 per window: gain, menu of 4 (median)               | 9830.938    | 20116.583   | 16644.333  | 18054.854   |
| band 7% + inspect 3 per window: gain, larger menu (median)             | 14138.188   | 17262.812   | 5356.583   | 15293.646   |
| band 7% + inspect 3 per window: markets where larger menu gives more   | 2           | 2           | 1          | 5           |
| block 240 / band, menu of 4: median                                    | 0.249       | 0.412       | 0.367      | 0.321       |
| block 240 / band, menu of 4: markets lower                             | 6/6         | 6/6         | 4/4        | 16/16       |
| block 240 / band, menu + random: median                                | 0.249       | 0.412       | 0.232      | 0.321       |
| block 240 / band, menu + random: markets lower                         | 6/6         | 6/6         | 4/4        | 16/16       |
| inspect 3, menu of 4: markets with net U5>0                            | 1/6         | 0/6         | 2/4        | 3/16        |
| inspect 3, menu of 4: median caught                                    | 0.25        | 0.25        | 0.125      | 0.25        |
| inspect 3, menu + random: markets with net U5>0                        | 1/6         | 0/6         | 3/4        | 4/16        |
| inspect 3, menu + random: median caught                                | 0.25        | 0.375       | 0.083      | 0.25        |