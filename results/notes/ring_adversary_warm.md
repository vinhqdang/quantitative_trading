# R2 / R3: adaptive collusion ring against inspection and a block-price rule

Evolution strategy per row: population 12, 7 generations, 4 episodes per candidate; selection on 16 episodes and reporting on 16 further episodes. One ring per episode (3000 steps). `gain` = benefit of ring manipulation in tick-lots (block of 3000 lots times price displacement plus trading profit). `caught` = share of episodes in which at least one member was among the B inspected accounts of some window. `net U (m)` = gain minus m times the gain when caught; a deterred ring has net U <= 0 or retains almost no gain.

| scenario                                 | detector   |   B |   block rule (steps) |            gain |   gain retained |   displacement |   caught |   net U (m=5) |   net U (m=10) |
|:-----------------------------------------|:-----------|----:|---------------------:|----------------:|----------------:|---------------:|---------:|--------------:|---------------:|
| adaptive ring, warm start                | scan       |   1 |                    1 | 20496.2         |            0.02 |           0.57 |     0.75 |     -126463   |      -273422   |
| adaptive ring, warm start                | scan       |   3 |                    1 | 25399.2         |            0.03 |           0.76 |     1    |     -115586   |      -256571   |
| adaptive ring, warm start                | scan       |  10 |                    1 | 25517.4         |            0.03 |           0.92 |     1    |     -136124   |      -297764   |
| adaptive ring, warm start                | gbm        |   1 |                    1 | -9684.22        |           -0.01 |          -0.18 |     0.12 |      -12669.5 |       -15654.8 |
| adaptive ring, warm start                | gbm        |   3 |                    1 | 25399.2         |            0.03 |           0.76 |     1    |     -115586   |      -256571   |
| block rule only, warm start              | none       |   0 |                  240 |     1.39779e+07 |           14.29 |         -77.24 |   nan    |         nan   |          nan   |
| block rule + scan inspection, warm start | scan       |   3 |                  240 |  1436.37        |            0    |           0.15 |     1    |      -38435.2 |       -78306.8 |


## Honest cost of the block-price rule

Mean absolute gap between the last mid and the trailing-mean block price in honest markets (ticks): 1 steps: 0.00.

## Parameters chosen by the adaptive ring

- adaptive ring, warm start / scan / B=1 / rule=1: {'K': 4, 'q': 2, 'm_push': 1, 'p_push': 0.54, 'p_acc': 0.45, 'jitter': 22, 'cross_frac': 0.19, 'acc_len': 47, 'push_len': 40, 'dist_len': 55, 'cool': 45}
- adaptive ring, warm start / scan / B=3 / rule=1: {'K': 23, 'q': 3, 'm_push': 1, 'p_push': 0.56, 'p_acc': 0.47, 'jitter': 23, 'cross_frac': 0.01, 'acc_len': 23, 'push_len': 32, 'dist_len': 50, 'cool': 84}
- adaptive ring, warm start / scan / B=10 / rule=1: {'K': 34, 'q': 1, 'm_push': 1, 'p_push': 0.65, 'p_acc': 0.13, 'jitter': 6, 'cross_frac': 0.27, 'acc_len': 84, 'push_len': 20, 'dist_len': 39, 'cool': 79}
- adaptive ring, warm start / gbm / B=1 / rule=1: {'K': 3, 'q': 1, 'm_push': 1, 'p_push': 0.45, 'p_acc': 0.44, 'jitter': 35, 'cross_frac': 0.25, 'acc_len': 22, 'push_len': 35, 'dist_len': 44, 'cool': 33}
- adaptive ring, warm start / gbm / B=3 / rule=1: {'K': 23, 'q': 3, 'm_push': 1, 'p_push': 0.56, 'p_acc': 0.47, 'jitter': 23, 'cross_frac': 0.01, 'acc_len': 23, 'push_len': 32, 'dist_len': 50, 'cool': 84}
- block rule only, warm start / none / B=0 / rule=240: {'K': 7, 'q': 6, 'm_push': 4, 'p_push': 1.0, 'p_acc': 0.2, 'jitter': 25, 'cross_frac': 0.2, 'acc_len': 26, 'push_len': 50, 'dist_len': 30, 'cool': 30}
- block rule + scan inspection, warm start / scan / B=3 / rule=240: {'K': 8, 'q': 3, 'm_push': 2, 'p_push': 0.83, 'p_acc': 0.12, 'jitter': 39, 'cross_frac': 0.11, 'acc_len': 59, 'push_len': 23, 'dist_len': 51, 'cool': 50}
