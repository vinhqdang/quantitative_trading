# Policy levers against a best-responding ring (Vietnam preset)

Evolution strategy per row: population 8, 5 generations, 3 episodes per candidate, started from the strongest ring found without any policy; selection on 12 episodes and reporting on 12 further episodes. One ring per episode (3000 steps), 3000-lot block sold off-book at the end of each push. `gain` in tick-lots; `caught` = share of episodes in which a member was among the inspected accounts of some window (about 500 active accounts per window); `net U (m)` = gain minus m times the gain when caught (m = 5 for individuals, 10 for organisations under Decree 156/2020).

| scenario                                | detector   |   B |   block rule (steps) |             gain |   displacement |   caught |   net U (m=5) |   net U (m=10) |
|:----------------------------------------|:-----------|----:|---------------------:|-----------------:|---------------:|---------:|--------------:|---------------:|
| no price band                           | none       |   0 |                    1 | 226742           |           4.73 |   nan    |         nan   |          nan   |
| band 7% (HOSE today)                    | none       |   0 |                    1 | 152400           |           3.6  |   nan    |         nan   |          nan   |
| band 10%                                | none       |   0 |                    1 |      1.26453e+06 |           8.85 |   nan    |         nan   |          nan   |
| band 15%                                | none       |   0 |                    1 | 669516           |           7.56 |   nan    |         nan   |          nan   |
| band 7% + block priced at 60-step mean  | none       |   0 |                   60 | 161945           |           2.25 |   nan    |         nan   |          nan   |
| band 7% + block priced at 240-step mean | none       |   0 |                  240 | 116246           |           0.56 |   nan    |         nan   |          nan   |
| band 7% + inspect 1 account per window  | scan       |   1 |                    1 |  11780.5         |           0.54 |     1    |      -53086.2 |      -117953   |
| band 7% + inspect 3 accounts per window | scan       |   3 |                    1 |   6610           |           0.17 |     0.58 |      -23673.8 |       -53957.5 |


## Honest cost of the price band (markets without rings)

`at_limit` is the share of steps with the mid at the band edge; `tracking_error` the mean distance between mid and latent value (ticks).

|   band |   spread |   depth |   vol |   tracking_error |   noise_cost |   volume |   halted |   at_limit |
|-------:|---------:|--------:|------:|-----------------:|-------------:|---------:|---------:|-----------:|
|   0    |    3.426 | 2708.91 | 0.498 |           12.67  |        0.308 |   13.599 |        0 |          0 |
|   0.07 |    3.454 | 2634.5  | 0.512 |           13.702 |        0.401 |   13.795 |        0 |          0 |
|   0.1  |    3.439 | 2647.95 | 0.501 |           13.419 |        0.414 |   13.694 |        0 |          0 |
|   0.15 |    3.439 | 2717.79 | 0.503 |           12.664 |        0.312 |   13.615 |        0 |          0 |


## Parameters chosen by the ring

- no price band: {'K': 30, 'q': 6, 'm_push': 4, 'p_push': 1.0, 'p_acc': 0.23, 'jitter': 5, 'cross_frac': 0.0, 'acc_len': 85, 'push_len': 50, 'dist_len': 55, 'cool': 47}
- band 7% (HOSE today): {'K': 18, 'q': 5, 'm_push': 4, 'p_push': 0.88, 'p_acc': 0.26, 'jitter': 0, 'cross_frac': 0.02, 'acc_len': 32, 'push_len': 50, 'dist_len': 53, 'cool': 74}
- band 10%: {'K': 28, 'q': 6, 'm_push': 4, 'p_push': 0.98, 'p_acc': 0.67, 'jitter': 1, 'cross_frac': 0.21, 'acc_len': 24, 'push_len': 49, 'dist_len': 33, 'cool': 41}
- band 15%: {'K': 21, 'q': 6, 'm_push': 4, 'p_push': 1.0, 'p_acc': 0.32, 'jitter': 0, 'cross_frac': 0.07, 'acc_len': 27, 'push_len': 50, 'dist_len': 45, 'cool': 30}
- band 7% + block priced at 60-step mean: {'K': 25, 'q': 6, 'm_push': 4, 'p_push': 0.98, 'p_acc': 0.55, 'jitter': 8, 'cross_frac': 0.05, 'acc_len': 41, 'push_len': 49, 'dist_len': 31, 'cool': 106}
- band 7% + block priced at 240-step mean: {'K': 18, 'q': 5, 'm_push': 4, 'p_push': 0.95, 'p_acc': 0.24, 'jitter': 3, 'cross_frac': 0.14, 'acc_len': 20, 'push_len': 49, 'dist_len': 52, 'cool': 46}
- band 7% + inspect 1 account per window: {'K': 14, 'q': 1, 'm_push': 2, 'p_push': 0.95, 'p_acc': 0.38, 'jitter': 8, 'cross_frac': 0.09, 'acc_len': 65, 'push_len': 39, 'dist_len': 69, 'cool': 111}
- band 7% + inspect 3 accounts per window: {'K': 7, 'q': 1, 'm_push': 1, 'p_push': 0.69, 'p_acc': 0.24, 'jitter': 2, 'cross_frac': 0.23, 'acc_len': 45, 'push_len': 17, 'dist_len': 52, 'cool': 74}
