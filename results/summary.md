# Detection experiments

3 independent repetitions; per repetition 40 training episodes (non-evasive manipulators) and 20 test episodes per evasion level. Cells are mean (sd) over repetitions. Detection unit: one account in one 300-step window.

## E1a. Recall at the 1% training-FPR operating point

evasion level →

| detector   | 0.0         | 0.25        | 0.5         | 0.75        | 1.0         |
|:-----------|:------------|:------------|:------------|:------------|:------------|
| otr_rule   | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |
| iforest    | 0.18 (0.04) | 0.09 (0.05) | 0.08 (0.05) | 0.04 (0.03) | 0.02 (0.02) |
| logreg     | 0.99 (0.01) | 0.99 (0.00) | 0.98 (0.01) | 0.97 (0.01) | 0.86 (0.06) |
| gbm        | 0.99 (0.00) | 0.99 (0.00) | 0.98 (0.01) | 0.98 (0.01) | 0.93 (0.01) |


## E1b. Realised false-positive rate at that same threshold

evasion level →

| detector   | 0.0         | 0.25        | 0.5         | 0.75        | 1.0         |
|:-----------|:------------|:------------|:------------|:------------|:------------|
| otr_rule   | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) | 0.02 (0.00) | 0.02 (0.00) |
| iforest    | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) |
| logreg     | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) |
| gbm        | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) |


## E1c. Average precision (threshold-free)

evasion level →

| detector   | 0.0         | 0.25        | 0.5         | 0.75        | 1.0         |
|:-----------|:------------|:------------|:------------|:------------|:------------|
| otr_rule   | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) | 0.01 (0.00) |
| iforest    | 0.25 (0.02) | 0.18 (0.02) | 0.10 (0.02) | 0.08 (0.01) | 0.05 (0.01) |
| logreg     | 0.98 (0.01) | 0.99 (0.00) | 0.97 (0.01) | 0.96 (0.01) | 0.84 (0.07) |
| gbm        | 0.99 (0.00) | 0.99 (0.00) | 0.97 (0.01) | 0.96 (0.01) | 0.91 (0.01) |


## E1d. Recall by manipulation type (gbm / iforest)

**gbm**

|       | 0.0         | 0.25        | 0.5         | 0.75        | 1.0         |
|:------|:------------|:------------|:------------|:------------|:------------|
| spoof | 1.00 (0.00) | 1.00 (0.00) | 1.00 (0.00) | 1.00 (0.00) | 0.98 (0.02) |
| pump  | 0.98 (0.01) | 0.98 (0.01) | 0.97 (0.01) | 0.97 (0.01) | 0.95 (0.02) |
| wash  | 1.00 (0.00) | 1.00 (0.00) | 0.96 (0.03) | 0.94 (0.02) | 0.79 (0.05) |


**iforest**

|       | 0.0         | 0.25        | 0.5         | 0.75        | 1.0         |
|:------|:------------|:------------|:------------|:------------|:------------|
| spoof | 0.17 (0.11) | 0.01 (0.00) | 0.01 (0.00) | 0.00 (0.00) | 0.00 (0.00) |
| pump  | 0.28 (0.15) | 0.20 (0.12) | 0.19 (0.12) | 0.10 (0.07) | 0.05 (0.05) |
| wash  | 0.01 (0.01) | 0.01 (0.00) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) |


## E2. Share of honest windows flagged, by agent kind (evasion 0)

Includes the manipulator accounts' own windows in which they were not manipulating.

| kind         |   otr_rule |   iforest |   logreg |   gbm |
|:-------------|-----------:|----------:|---------:|------:|
| fundamental  |      0     |     0     |    0.021 | 0.009 |
| imbalance    |      0     |     0     |    0.002 | 0.008 |
| institution  |      0     |     0     |    0.053 | 0.103 |
| market_maker |      0.181 |     0.109 |    0.006 | 0.002 |
| momentum     |      0     |     0     |    0.002 | 0.005 |
| noise        |      0     |     0.002 |    0.008 | 0.011 |
| pump_dump    |      0     |     0.003 |    0.01  | 0.007 |
| spoofer      |      0     |     0.008 |    0.023 | 0.027 |
| wash         |      0     |     0.006 |    0.005 | 0.005 |


## E3. Label scarcity: recall / average precision vs number of labelled training episodes

evasion = 0.0

|                |   positives | recall      | ap          |
|:---------------|------------:|:------------|:------------|
| ('gbm', 3)     |          87 | 0.99 (0.01) | 0.98 (0.01) |
| ('gbm', 10)    |         306 | 0.98 (0.01) | 0.98 (0.01) |
| ('gbm', 40)    |        1132 | 0.99 (0.00) | 0.99 (0.00) |
| ('logreg', 3)  |          87 | 0.98 (0.01) | 0.98 (0.02) |
| ('logreg', 10) |         306 | 0.99 (0.01) | 0.98 (0.02) |
| ('logreg', 40) |        1132 | 0.99 (0.01) | 0.98 (0.01) |


evasion = 0.75

|                |   positives | recall      | ap          |
|:---------------|------------:|:------------|:------------|
| ('gbm', 3)     |          87 | 0.91 (0.05) | 0.87 (0.02) |
| ('gbm', 10)    |         306 | 0.90 (0.07) | 0.90 (0.05) |
| ('gbm', 40)    |        1132 | 0.98 (0.01) | 0.96 (0.01) |
| ('logreg', 3)  |          87 | 0.88 (0.07) | 0.88 (0.06) |
| ('logreg', 10) |         306 | 0.95 (0.02) | 0.94 (0.02) |
| ('logreg', 40) |        1132 | 0.97 (0.01) | 0.96 (0.01) |


## E4. gbm trained on evasion {0, 0.5}, tested on unseen evasion levels

|   evasion | recall      | fpr         | ap          |
|----------:|:------------|:------------|:------------|
|      0.75 | 0.98 (0.01) | 0.01 (0.00) | 0.98 (0.01) |
|      1    | 0.97 (0.01) | 0.01 (0.00) | 0.96 (0.01) |


## Validity check: what manipulation achieves, by evasion level (pooled over all test episodes)

`impact` = mean price move in the manipulator's intended direction, in ticks (spoof: 8 steps after the fake orders appear; pump: first to last pump order), ± standard error over cycles. `profit_per_share` is mark-to-market on tagged trades only. Values near zero mean the simulated manipulation leaves the behavioural footprint without a demonstrated payoff in this market.

|   evasion | ('impact', 'pump')   | ('impact', 'spoof')   |   ('cycles', 'pump') |   ('cycles', 'spoof') |   ('profit_per_share', 'pump') |   ('profit_per_share', 'spoof') |   ('shares', 'pump') |   ('shares', 'spoof') |
|----------:|:---------------------|:----------------------|---------------------:|----------------------:|-------------------------------:|--------------------------------:|---------------------:|----------------------:|
|      0    | 1.63 ± 0.04          | 1.08 ± 0.02           |                  900 |                  2840 |                         -1.752 |                           0.124 |               230579 |                 59277 |
|      0.25 | 1.47 ± 0.05          | 1.01 ± 0.02           |                  857 |                  2579 |                         -1.637 |                           0.124 |               211678 |                 53409 |
|      0.5  | 1.53 ± 0.06          | 0.51 ± 0.01           |                  801 |                  2256 |                         -1.618 |                           0.342 |               197014 |                 44934 |
|      0.75 | 1.35 ± 0.06          | 0.26 ± 0.01           |                  726 |                  2108 |                         -1.606 |                           0.371 |               175259 |                 40904 |
|      1    | 1.47 ± 0.09          | 0.02 ± 0.01           |                  617 |                  1967 |                         -1.705 |                           0.285 |               152674 |                 34621 |

