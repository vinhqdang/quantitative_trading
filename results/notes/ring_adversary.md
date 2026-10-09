# R2 / R3: adaptive collusion ring against inspection and a block-price rule

Evolution strategy per row: population 12, 5 generations, 4 episodes per candidate; selection on 16 episodes and reporting on 16 further episodes. One ring per episode (3000 steps). `gain` = benefit of ring manipulation in tick-lots (block of 200 lots times price displacement plus trading profit). `caught` = share of episodes in which at least one member was among the B inspected accounts of some window. `net U (m)` = gain minus m times the gain when caught; a deterred ring has net U <= 0 or retains almost no gain.

| scenario                                     | detector   |   B |   block rule (steps) |      gain |   gain retained |   displacement |   caught |   net U (m=5) |   net U (m=10) |
|:---------------------------------------------|:-----------|----:|---------------------:|----------:|----------------:|---------------:|---------:|--------------:|---------------:|
| ring ignoring detection                      | none       |   0 |                    1 | 978361    |            1    |          15.98 |   nan    |         nan   |          nan   |
| default ring (not adaptive)                  | scan       |   1 |                    1 |  75828.3  |            0.08 |           2.62 |     1    |     -312216   |      -700260   |
| default ring (not adaptive)                  | scan       |   3 |                    1 |  75828.3  |            0.08 |           2.62 |     1    |     -312216   |      -700260   |
| default ring (not adaptive)                  | scan       |  10 |                    1 |  75828.3  |            0.08 |           2.62 |     1    |     -312216   |      -700260   |
| default ring (not adaptive)                  | gbm        |   1 |                    1 |  75828.3  |            0.08 |           2.62 |     1    |     -312216   |      -700260   |
| default ring (not adaptive)                  | gbm        |   3 |                    1 |  75828.3  |            0.08 |           2.62 |     1    |     -312216   |      -700260   |
| default ring (not adaptive)                  | gbm        |  10 |                    1 |  75828.3  |            0.08 |           2.62 |     1    |     -312216   |      -700260   |
| adaptive ring                                | scan       |   1 |                    1 |  11882    |            0.01 |           0.63 |     0.56 |      -47999.6 |      -107881   |
| adaptive ring                                | scan       |   3 |                    1 |  21292.2  |            0.02 |           0.59 |     0.94 |     -122146   |      -265584   |
| adaptive ring                                | scan       |  10 |                    1 |  12059.8  |            0.01 |           0.39 |     1    |      -72025.4 |      -156111   |
| adaptive ring                                | gbm        |   1 |                    1 |  15665.1  |            0.02 |           0.45 |     0.81 |      -94302.9 |      -204271   |
| adaptive ring                                | gbm        |   3 |                    1 |    -99.06 |           -0    |           0.04 |     1    |      -77657.2 |      -155215   |
| adaptive ring                                | gbm        |  10 |                    1 |  12059.8  |            0.01 |           0.39 |     1    |      -72025.4 |      -156111   |
| block priced at trailing mean, no inspection | none       |   0 |                  240 |   9507.3  |            0.01 |           0.24 |   nan    |         nan   |          nan   |
| block rule + scan inspection                 | scan       |   3 |                  240 |   1654.59 |            0    |           0.07 |     1    |      -37434.8 |       -76524.2 |


## Honest cost of the block-price rule

Mean absolute gap between the last mid and the trailing-mean block price in honest markets (ticks): 1 steps: 0.00, 240 steps: 3.53.

## Parameters chosen by the adaptive ring

- ring ignoring detection / none / B=0 / rule=1: {'K': 18, 'q': 5, 'm_push': 3, 'p_push': 1.0, 'p_acc': 0.29, 'jitter': 2, 'cross_frac': 0.0, 'acc_len': 37, 'push_len': 46, 'dist_len': 46, 'cool': 67}
- default ring (not adaptive) / scan / B=1 / rule=1: {'K': 12, 'q': 3, 'm_push': 2, 'p_push': 0.8, 'p_acc': 0.4, 'jitter': 0, 'cross_frac': 0.2, 'acc_len': 60, 'push_len': 25, 'dist_len': 50, 'cool': 60}
- default ring (not adaptive) / scan / B=3 / rule=1: {'K': 12, 'q': 3, 'm_push': 2, 'p_push': 0.8, 'p_acc': 0.4, 'jitter': 0, 'cross_frac': 0.2, 'acc_len': 60, 'push_len': 25, 'dist_len': 50, 'cool': 60}
- default ring (not adaptive) / scan / B=10 / rule=1: {'K': 12, 'q': 3, 'm_push': 2, 'p_push': 0.8, 'p_acc': 0.4, 'jitter': 0, 'cross_frac': 0.2, 'acc_len': 60, 'push_len': 25, 'dist_len': 50, 'cool': 60}
- default ring (not adaptive) / gbm / B=1 / rule=1: {'K': 12, 'q': 3, 'm_push': 2, 'p_push': 0.8, 'p_acc': 0.4, 'jitter': 0, 'cross_frac': 0.2, 'acc_len': 60, 'push_len': 25, 'dist_len': 50, 'cool': 60}
- default ring (not adaptive) / gbm / B=3 / rule=1: {'K': 12, 'q': 3, 'm_push': 2, 'p_push': 0.8, 'p_acc': 0.4, 'jitter': 0, 'cross_frac': 0.2, 'acc_len': 60, 'push_len': 25, 'dist_len': 50, 'cool': 60}
- default ring (not adaptive) / gbm / B=10 / rule=1: {'K': 12, 'q': 3, 'm_push': 2, 'p_push': 0.8, 'p_acc': 0.4, 'jitter': 0, 'cross_frac': 0.2, 'acc_len': 60, 'push_len': 25, 'dist_len': 50, 'cool': 60}
- adaptive ring / scan / B=1 / rule=1: {'K': 3, 'q': 3, 'm_push': 2, 'p_push': 0.22, 'p_acc': 0.51, 'jitter': 22, 'cross_frac': 0.21, 'acc_len': 60, 'push_len': 23, 'dist_len': 55, 'cool': 93}
- adaptive ring / scan / B=3 / rule=1: {'K': 12, 'q': 2, 'm_push': 2, 'p_push': 0.27, 'p_acc': 0.1, 'jitter': 19, 'cross_frac': 0.19, 'acc_len': 47, 'push_len': 19, 'dist_len': 48, 'cool': 72}
- adaptive ring / scan / B=10 / rule=1: {'K': 33, 'q': 1, 'm_push': 1, 'p_push': 0.75, 'p_acc': 0.36, 'jitter': 1, 'cross_frac': 0.33, 'acc_len': 53, 'push_len': 10, 'dist_len': 42, 'cool': 93}
- adaptive ring / gbm / B=1 / rule=1: {'K': 13, 'q': 1, 'm_push': 3, 'p_push': 0.58, 'p_acc': 0.54, 'jitter': 9, 'cross_frac': 0.22, 'acc_len': 62, 'push_len': 10, 'dist_len': 59, 'cool': 51}
- adaptive ring / gbm / B=3 / rule=1: {'K': 18, 'q': 2, 'm_push': 2, 'p_push': 0.22, 'p_acc': 0.1, 'jitter': 19, 'cross_frac': 0.14, 'acc_len': 52, 'push_len': 31, 'dist_len': 64, 'cool': 87}
- adaptive ring / gbm / B=10 / rule=1: {'K': 33, 'q': 1, 'm_push': 1, 'p_push': 0.75, 'p_acc': 0.36, 'jitter': 1, 'cross_frac': 0.33, 'acc_len': 53, 'push_len': 10, 'dist_len': 42, 'cool': 93}
- block priced at trailing mean, no inspection / none / B=0 / rule=240: {'K': 3, 'q': 2, 'm_push': 3, 'p_push': 0.95, 'p_acc': 0.32, 'jitter': 0, 'cross_frac': 0.0, 'acc_len': 33, 'push_len': 20, 'dist_len': 65, 'cool': 40}
- block rule + scan inspection / scan / B=3 / rule=240: {'K': 13, 'q': 5, 'm_push': 3, 'p_push': 0.82, 'p_acc': 0.19, 'jitter': 16, 'cross_frac': 0.16, 'acc_len': 84, 'push_len': 12, 'dist_len': 30, 'cool': 31}
