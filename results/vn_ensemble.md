# Policy conclusions across a family of calibrated markets

6 markets accepted among 27 draws (tolerances: cancel share 0.27-0.37, daily volatility 0.9-1.4%, retail share 0.66-0.85). Ring strategy set: 4 strategies; 12 selection and 12 reporting episodes per cell. `ratio` is the ring's gain relative to its gain with no policy in the same market (markets with non-positive baseline gain are left out of the ratio).

## Accepted markets

|   draw |   n_noise |   n_fund |   mm_activity |   fund_sigma |   mm_imb_sens |   mom_activity |   cancel_share |   daily_vol_pct |   retail_share |   spread_ticks | accepted   |
|-------:|----------:|---------:|--------------:|-------------:|--------------:|---------------:|---------------:|----------------:|---------------:|---------------:|:-----------|
|      1 |       449 |       40 |         0.098 |        0.528 |         3.336 |          0.058 |          0.315 |           1.076 |          0.694 |          2.97  | True       |
|      5 |       549 |       46 |         0.098 |        1.019 |         1.576 |          0.099 |          0.282 |           1.133 |          0.711 |          3.157 | True       |
|     11 |       394 |       34 |         0.105 |        0.72  |         3.032 |          0.064 |          0.33  |           1.085 |          0.693 |          3.094 | True       |
|     19 |       369 |       43 |         0.104 |        0.559 |         2.738 |          0.059 |          0.338 |           1.174 |          0.697 |          2.97  | True       |
|     20 |       627 |       42 |         0.103 |        1.019 |         2.484 |          0.051 |          0.275 |           0.932 |          0.758 |          3.437 | True       |
|     26 |       488 |       36 |         0.109 |        0.866 |         1.761 |          0.081 |          0.3   |           1.182 |          0.718 |          3.236 | True       |


## Per policy, over markets

| policy                           |   markets |   gain_median |   gain_min |   gain_max |   ratio_median |   caught_median |   netU5_max |   netU10_max |
|:---------------------------------|----------:|--------------:|-----------:|-----------:|---------------:|----------------:|------------:|-------------:|
| no price band                    |         6 |      110041   |   86720.7  |   162126   |           1    |          nan    |      nan    |        nan   |
| band 7% (HOSE today)             |         6 |      105031   |   89247.2  |   164567   |           0.97 |          nan    |      nan    |        nan   |
| band 7% + block at 60-step mean  |         6 |       38419.8 |   11680.8  |    90825.8 |           0.35 |          nan    |      nan    |        nan   |
| band 7% + block at 240-step mean |         6 |       15291.8 |    -909.35 |    23544.3 |           0.11 |          nan    |      nan    |        nan   |
| band 7% + inspect 1 per window   |         6 |       16817.1 |    4494.42 |    51583.8 |           0.17 |            0.17 |    51583.8  |      51583.8 |
| band 7% + inspect 3 per window   |         6 |       16817.1 |    4494.42 |    51583.8 |           0.18 |            0.42 |     1449.79 |     -17963.5 |
