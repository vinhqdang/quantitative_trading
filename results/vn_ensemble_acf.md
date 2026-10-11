# Policy conclusions across a family of calibrated markets

4 markets accepted among 29 draws (tolerances: cancel share 0.27-0.37, daily volatility 0.9-1.5%, retail share 0.66-0.85). Ring strategy set: 4 strategies; 12 selection and 12 reporting episodes per cell. `ratio` is the ring's gain relative to its gain with no policy in the same market (markets with non-positive baseline gain are left out of the ratio).

## Accepted markets

|   draw |   n_noise |   n_fund |   mm_activity |   fund_sigma |   mm_imb_sens |   mom_activity |   cancel_share |   daily_vol_pct |   retail_share |   spread_ticks |   ret_acf1 | accepted   |
|-------:|----------:|---------:|--------------:|-------------:|--------------:|---------------:|---------------:|----------------:|---------------:|---------------:|-----------:|:-----------|
|      9 |       881 |      186 |         0.258 |        0.272 |         3.624 |          0.078 |          0.355 |           1.052 |          0.622 |          2.43  |      0.198 | True       |
|     11 |       516 |      118 |         0.201 |        0.48  |         3.032 |          0.064 |          0.339 |           1.372 |          0.616 |          2.499 |      0.053 | True       |
|     15 |       691 |      132 |         0.115 |        0.335 |         2.035 |          0.11  |          0.286 |           1.122 |          0.641 |          2.536 |      0.042 | True       |
|     28 |       706 |      137 |         0.22  |        0.433 |         1.993 |          0.115 |          0.335 |           1.352 |          0.651 |          2.563 |      0.026 | True       |


## Per policy, over markets

| policy                           |   markets |   gain_median |   gain_min |   gain_max |   ratio_median |   caught_median |   netU5_max |   netU10_max |
|:---------------------------------|----------:|--------------:|-----------:|-----------:|---------------:|----------------:|------------:|-------------:|
| no price band                    |         4 |      43414.8  |   -40179   |    63882   |           1    |          nan    |       nan   |        nan   |
| band 7% (HOSE today)             |         4 |      48107.7  |   -38472.6 |    64957   |           1.06 |          nan    |       nan   |        nan   |
| band 7% + block at 60-step mean  |         4 |        560.02 |   -58353.9 |    52175.2 |           0.05 |          nan    |       nan   |        nan   |
| band 7% + block at 240-step mean |         4 |       -809.77 |   -51983   |    28364.8 |          -0.01 |          nan    |       nan   |        nan   |
| band 7% + inspect 1 per window   |         4 |      19938.2  |   -19126.5 |    64600.2 |           1.06 |            0.04 |     64600.2 |      64600.2 |
| band 7% + inspect 3 per window   |         4 |       6913.75 |   -19126.5 |    64600.2 |           0.32 |            0.04 |     64600.2 |      64600.2 |
