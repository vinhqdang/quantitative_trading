# Policy matrix (Vietnam preset)

10 honest-only episodes and 24 episodes with one spoofer, one pump-and-dump agent, one wash pair and one ring (non-adaptive strategies) per policy. Standard errors in the csv.

## Cost to honest participants (change relative to band 7%)

| policy                |   spread (%) |   depth (%) |   vol (%) |   tracking_error (%) |   noise_cost (%) |   volume (%) |
|:----------------------|-------------:|------------:|----------:|---------------------:|-----------------:|-------------:|
| band 7% (today)       |          0   |         0   |       0   |                  0   |              0   |          0   |
| band 10%              |         -0.1 |        -0.2 |       0.1 |                  1.2 |             -2.5 |         -0.2 |
| tick x2               |         34.8 |        -9.5 |      28   |                  4   |            -15.8 |          7   |
| min rest 5            |          2.1 |        -0.7 |       5.9 |                 -0.6 |             -5.2 |         -0.3 |
| min rest 15           |          7.2 |        -3.1 |      20.8 |                  1.1 |            -11.6 |          0.8 |
| cancel fee 0.5        |          2   |        -1.8 |       5.6 |                 -1.8 |             -4.6 |          1   |
| cancel fee 2          |          7.9 |        -5.9 |      24.4 |                 -3.2 |             -5.5 |          5.2 |
| circuit breaker 6     |         -0   |        -0.3 |      -0   |                 -0   |              1.3 |         -0   |
| block at 60-step mean |          0   |         0   |       0   |                  0   |              0   |          0   |

## What the manipulators achieve

| policy                |   spoof profit |   spoof impact |   pump impact |   wash volume share |   ring gain |   ring displacement |
|:----------------------|---------------:|---------------:|--------------:|--------------------:|------------:|--------------------:|
| band 7% (today)       |        871.938 |          0.114 |         0.468 |               0.033 |     33570.4 |               1.037 |
| band 10%              |        972.771 |          0.137 |         0.429 |               0.033 |     32069.2 |               1.001 |
| tick x2               |        491.458 |          0.211 |         0.397 |               0.031 |     30365.8 |               0.966 |
| min rest 5            |       1090.58  |          0.156 |         0.399 |               0.033 |     34094.8 |               1.068 |
| min rest 15           |       1302.44  |          0.261 |         0.402 |               0.032 |     32643.1 |               1.023 |
| cancel fee 0.5        |       1314.94  |          0.176 |         0.312 |               0.032 |     33342.9 |               1.048 |
| cancel fee 2          |       1379.81  |          0.204 |         0.309 |               0.031 |     35586.3 |               1.129 |
| circuit breaker 6     |        889.417 |          0.149 |         0.453 |               0.033 |     33288.1 |               1.032 |
| block at 60-step mean |        871.938 |          0.114 |         0.468 |               0.033 |     19523.6 |               0.549 |
