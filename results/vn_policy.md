# Policy levers against a best-responding ring (Vietnam preset)

Evolution strategy per row: population 8, 5 generations, 3 episodes per candidate, started from the strongest ring found without any policy; selection on 12 episodes and reporting on 12 further episodes. One ring per episode (3000 steps), 3000-lot block sold off-book at the end of each push. `gain` in tick-lots; `caught` = share of episodes in which a member was among the inspected accounts of some window (about 500 active accounts per window); `net U (m)` = gain minus m times the gain when caught (m = 5 for individuals, 10 for organisations under Decree 156/2020).

| scenario                                | detector   |   B |   block rule (steps) |      gain |   displacement |   caught |   net U (m=5) |   net U (m=10) |
|:----------------------------------------|:-----------|----:|---------------------:|----------:|---------------:|---------:|--------------:|---------------:|
| no price band                           | none       |   0 |                    1 | 101128    |           2.23 |   nan    |        nan    |         nan    |
| band 7% (HOSE today)                    | none       |   0 |                    1 |  49223.9  |           2.01 |   nan    |        nan    |         nan    |
| band 10%                                | none       |   0 |                    1 |  93594    |           2.6  |   nan    |        nan    |         nan    |
| band 15%                                | none       |   0 |                    1 |  84198.6  |           2.4  |   nan    |        nan    |         nan    |
| band 7% + block priced at 60-step mean  | none       |   0 |                   60 |  62582.9  |           1.2  |   nan    |        nan    |         nan    |
| band 7% + block priced at 240-step mean | none       |   0 |                  240 |  23982.2  |           0.38 |   nan    |        nan    |         nan    |
| band 7% + inspect 1 account per window  | scan       |   1 |                    1 |  39132.9  |           0.92 |     0.25 |      21636.9  |        4140.83 |
| band 7% + inspect 3 accounts per window | scan       |   3 |                    1 |   6876.33 |           0.66 |     0.17 |       4053.62 |        1230.92 |


## Honest cost of the price band (markets without rings)

`at_limit` is the share of steps with the mid at the band edge; `tracking_error` the mean distance between mid and latent value (ticks).

|   band |   spread |   depth |   vol |   tracking_error |   noise_cost |   volume |   halted |   at_limit |
|-------:|---------:|--------:|------:|-----------------:|-------------:|---------:|---------:|-----------:|
|   0    |    2.835 | 2647.49 | 0.406 |            4.612 |        2.747 |   19.793 |        0 |          0 |
|   0.07 |    2.825 | 2658.04 | 0.403 |            4.608 |        2.657 |   19.665 |        0 |          0 |
|   0.1  |    2.841 | 2661.97 | 0.411 |            4.631 |        2.748 |   19.716 |        0 |          0 |
|   0.15 |    2.835 | 2647.49 | 0.406 |            4.612 |        2.747 |   19.793 |        0 |          0 |


## Parameters chosen by the ring

- no price band: {'K': 7, 'q': 5, 'm_push': 3, 'p_push': 0.86, 'p_acc': 0.44, 'jitter': 1, 'cross_frac': 0.09, 'acc_len': 57, 'push_len': 44, 'dist_len': 74, 'cool': 34}
- band 7% (HOSE today): {'K': 18, 'q': 5, 'm_push': 3, 'p_push': 1.0, 'p_acc': 0.29, 'jitter': 2, 'cross_frac': 0.0, 'acc_len': 37, 'push_len': 46, 'dist_len': 46, 'cool': 67}
- band 10%: {'K': 30, 'q': 6, 'm_push': 3, 'p_push': 1.0, 'p_acc': 0.44, 'jitter': 10, 'cross_frac': 0.0, 'acc_len': 28, 'push_len': 44, 'dist_len': 41, 'cool': 45}
- band 15%: {'K': 18, 'q': 5, 'm_push': 3, 'p_push': 1.0, 'p_acc': 0.29, 'jitter': 2, 'cross_frac': 0.0, 'acc_len': 37, 'push_len': 46, 'dist_len': 46, 'cool': 67}
- band 7% + block priced at 60-step mean: {'K': 18, 'q': 5, 'm_push': 3, 'p_push': 1.0, 'p_acc': 0.29, 'jitter': 2, 'cross_frac': 0.0, 'acc_len': 37, 'push_len': 46, 'dist_len': 46, 'cool': 67}
- band 7% + block priced at 240-step mean: {'K': 22, 'q': 5, 'm_push': 4, 'p_push': 0.83, 'p_acc': 0.18, 'jitter': 10, 'cross_frac': 0.2, 'acc_len': 21, 'push_len': 40, 'dist_len': 57, 'cool': 39}
- band 7% + inspect 1 account per window: {'K': 3, 'q': 3, 'm_push': 2, 'p_push': 0.59, 'p_acc': 0.64, 'jitter': 6, 'cross_frac': 0.09, 'acc_len': 31, 'push_len': 41, 'dist_len': 64, 'cool': 30}
- band 7% + inspect 3 accounts per window: {'K': 3, 'q': 4, 'm_push': 2, 'p_push': 0.7, 'p_acc': 0.4, 'jitter': 5, 'cross_frac': 0.17, 'acc_len': 90, 'push_len': 22, 'dist_len': 32, 'cool': 89}
