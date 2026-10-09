# Cross-evaluated best response of a collusion ring (Vietnam preset)

Strategy set: 7 ring parameter sets (the strongest unconstrained ring, the default ring, and the strategies found by the evolution-strategy runs in `vn_policy.md`). For each policy the ring picks the strategy with the best result on 20 selection episodes; the numbers come from 20 separate episodes (`gain se` = standard error over them). Lower gain is better for the regulator. A ring whose net U is negative would rather not operate.

| scenario                         |   B |   block rule (steps) |   best strategy |     gain |   gain se |   displacement |   caught |   net U (m=5) |   net U (m=10) |
|:---------------------------------|----:|---------------------:|----------------:|---------:|----------:|---------------:|---------:|--------------:|---------------:|
| no price band                    |   0 |                    1 |               3 | 81734.6  |   28287.7 |           2.46 |   nan    |         nan   |          nan   |
| band 7% (HOSE today)             |   0 |                    1 |               3 | 79431.7  |   29254.1 |           2.44 |   nan    |         nan   |          nan   |
| band 10%                         |   0 |                    1 |               3 | 81109.8  |   28241.3 |           2.44 |   nan    |         nan   |          nan   |
| band 15%                         |   0 |                    1 |               3 | 81734.6  |   28287.7 |           2.46 |   nan    |         nan   |          nan   |
| band 7% + block at 60-step mean  |   0 |                   60 |               3 | 21691.7  |   27613.4 |           0.99 |   nan    |         nan   |          nan   |
| band 7% + block at 240-step mean |   0 |                  240 |               3 |  5837.32 |   21372.3 |           0.59 |   nan    |         nan   |          nan   |
| band 7% + inspect 1 per window   |   1 |                    1 |               6 | 13803.7  |   11405.7 |           0.6  |     0.2  |      -35630.3 |       -85064.3 |
| band 7% + inspect 3 per window   |   3 |                    1 |               6 | 13803.7  |   11405.7 |           0.6  |     0.45 |      -48886.7 |      -111577   |
