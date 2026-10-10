# Policy conclusions across a family of calibrated markets

6 markets accepted among 62 draws (tolerances: cancel share 0.27-0.37, daily volatility 1.8-2.8%, retail share 0.66-0.85). Ring strategy set: 4 strategies; 12 selection and 12 reporting episodes per cell. `ratio` is the ring's gain relative to its gain with no policy in the same market (markets with non-positive baseline gain are left out of the ratio).

## Accepted markets

|   draw |   n_noise |   n_fund |   mm_activity |   fund_sigma |   mm_imb_sens |   mom_activity |   cancel_share |   daily_vol_pct |   retail_share |   spread_ticks | accepted   |
|-------:|----------:|---------:|--------------:|-------------:|--------------:|---------------:|---------------:|----------------:|---------------:|---------------:|:-----------|
|     14 |       643 |       46 |         0.138 |        1.787 |         3.475 |          0.054 |          0.275 |           2.025 |          0.725 |          3.434 | True       |
|     19 |       369 |       43 |         0.104 |        1.198 |         2.738 |          0.059 |          0.284 |           2.189 |          0.686 |          3.31  | True       |
|     23 |       368 |       28 |         0.104 |        1.921 |         2.907 |          0.102 |          0.298 |           2.478 |          0.7   |          3.609 | True       |
|     39 |       403 |       45 |         0.113 |        1.324 |         3.174 |          0.093 |          0.271 |           2.188 |          0.688 |          3.346 | True       |
|     49 |       430 |       41 |         0.111 |        1.669 |         2.383 |          0.096 |          0.28  |           2.424 |          0.662 |          3.087 | True       |
|     61 |       555 |       49 |         0.13  |        1.231 |         1.621 |          0.078 |          0.28  |           1.843 |          0.726 |          3.344 | True       |


## Per policy, over markets

| policy                           |   markets |   gain_median |   gain_min |   gain_max |   ratio_median |   caught_median |   netU5_max |   netU10_max |
|:---------------------------------|----------:|--------------:|-----------:|-----------:|---------------:|----------------:|------------:|-------------:|
| no price band                    |         6 |     164402    |  101165    |   261417   |           1    |          nan    |      nan    |       nan    |
| band 7% (HOSE today)             |         6 |     154894    |  111867    |   261071   |           0.99 |          nan    |      nan    |       nan    |
| band 7% + block at 60-step mean  |         6 |      66473.9  |    8387.13 |   179032   |           0.45 |          nan    |      nan    |       nan    |
| band 7% + block at 240-step mean |         6 |      33677    |   -7940.87 |   130986   |           0.2  |          nan    |      nan    |       nan    |
| band 7% + inspect 1 per window   |         6 |       6332.94 |   -9138.5  |    40826.9 |           0.03 |            0.08 |    40826.9  |     40826.9  |
| band 7% + inspect 3 per window   |         6 |       6332.94 |   -9138.5  |    40826.9 |           0.03 |            0.25 |     6939.17 |      6939.17 |
