# Cross-evaluated best response of a collusion ring (Vietnam preset)

Strategy set: 10 ring parameter sets (the strongest unconstrained ring, the default ring, and the strategies found by the evolution-strategy runs in `vn_policy.md`). For each policy the ring picks the strategy with the best result on 10 selection episodes; the numbers come from 10 separate episodes (`gain se` = standard error over them). Lower gain is better for the regulator. A ring whose net U is negative would rather not operate.

| scenario                         |   B |   block rule (steps) |   best strategy |      gain |   gain se |   displacement |   caught |   net U (m=5) |   net U (m=10) |
|:---------------------------------|----:|---------------------:|----------------:|----------:|----------:|---------------:|---------:|--------------:|---------------:|
| no price band                    |   0 |                    1 |               5 | 713862    |  87424.4  |           7.3  |    nan   |         nan   |          nan   |
| band 7% (HOSE today)             |   0 |                    1 |               4 | 883097    | 142762    |           7.38 |    nan   |         nan   |          nan   |
| band 10%                         |   0 |                    1 |               5 | 713862    |  87424.4  |           7.3  |    nan   |         nan   |          nan   |
| band 15%                         |   0 |                    1 |               5 | 713862    |  87424.4  |           7.3  |    nan   |         nan   |          nan   |
| band 7% + block at 60-step mean  |   0 |                   60 |               4 | 703007    | 120531    |           3.15 |    nan   |         nan   |          nan   |
| band 7% + block at 240-step mean |   0 |                  240 |               4 | 573431    | 103050    |           0.11 |    nan   |         nan   |          nan   |
| band 7% + inspect 1 per window   |   1 |                    1 |               9 |   7839.15 |   5674.36 |           0.22 |      0.4 |      -27923.8 |       -63686.8 |
| band 7% + inspect 3 per window   |   3 |                    1 |               9 |   7839.15 |   5674.36 |           0.22 |      0.8 |      -51018.6 |      -109876   |
