# Ring detection with honest groups acting in step

24 clean labelled episodes for the fitted detectors; 24 test episodes per scenario; 95% bootstrap intervals over episodes in brackets. Chance for catch@B is about B divided by the number of active accounts (roughly 120-170).

## clean

| detector                                              |    AP | catch@1           | catch@3           | catch@5           | catch@10          |
|:------------------------------------------------------|------:|:------------------|:------------------|:------------------|:------------------|
| order-to-trade ratio                                  | 0.031 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.03 [0.01, 0.06] |
| isolation forest (no labels)                          | 0.035 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.07 [0.03, 0.10] |
| coincidence, unsigned (no labels)                     | 0.218 | 0.47 [0.39, 0.54] | 0.76 [0.67, 0.83] | 0.85 [0.78, 0.91] | 0.90 [0.83, 0.94] |
| coincidence, signed (no labels)                       | 0.242 | 0.58 [0.49, 0.65] | 0.82 [0.77, 0.87] | 0.87 [0.81, 0.92] | 0.91 [0.86, 0.95] |
| gradient boosting (trained with labels, clean market) | 0.917 | 0.98 [0.97, 1.00] | 0.99 [0.97, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |


## + MM desks

| detector                                              |    AP | catch@1           | catch@3           | catch@5           | catch@10          |
|:------------------------------------------------------|------:|:------------------|:------------------|:------------------|:------------------|
| order-to-trade ratio                                  | 0.028 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| isolation forest (no labels)                          | 0.031 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.03 [0.01, 0.05] |
| coincidence, unsigned (no labels)                     | 0.1   | 0.07 [0.03, 0.11] | 0.09 [0.04, 0.16] | 0.32 [0.20, 0.46] | 0.80 [0.70, 0.89] |
| coincidence, signed (no labels)                       | 0.274 | 0.57 [0.50, 0.64] | 0.84 [0.78, 0.89] | 0.88 [0.82, 0.92] | 0.92 [0.88, 0.95] |
| gradient boosting (trained with labels, clean market) | 0.935 | 0.98 [0.96, 0.99] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |


## + fund splitting orders

| detector                                              |    AP | catch@1           | catch@3           | catch@5           | catch@10          |
|:------------------------------------------------------|------:|:------------------|:------------------|:------------------|:------------------|
| order-to-trade ratio                                  | 0.028 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.05 [0.03, 0.08] |
| isolation forest (no labels)                          | 0.028 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.04 [0.02, 0.07] |
| coincidence, unsigned (no labels)                     | 0.117 | 0.34 [0.28, 0.42] | 0.59 [0.51, 0.67] | 0.71 [0.65, 0.77] | 0.82 [0.77, 0.87] |
| coincidence, signed (no labels)                       | 0.124 | 0.37 [0.30, 0.45] | 0.65 [0.57, 0.74] | 0.74 [0.66, 0.80] | 0.84 [0.78, 0.89] |
| gradient boosting (trained with labels, clean market) | 0.882 | 0.99 [0.97, 1.00] | 0.99 [0.98, 1.00] | 0.99 [0.98, 1.00] | 0.99 [0.98, 1.00] |


## + bot fleet

| detector                                              |    AP | catch@1           | catch@3           | catch@5           | catch@10          |
|:------------------------------------------------------|------:|:------------------|:------------------|:------------------|:------------------|
| order-to-trade ratio                                  | 0.03  | 0.03 [0.01, 0.07] | 0.08 [0.02, 0.15] | 0.13 [0.05, 0.22] | 0.18 [0.08, 0.28] |
| isolation forest (no labels)                          | 0.031 | 0.01 [0.00, 0.02] | 0.01 [0.00, 0.02] | 0.01 [0.00, 0.03] | 0.10 [0.06, 0.14] |
| coincidence, unsigned (no labels)                     | 0.219 | 0.45 [0.35, 0.53] | 0.74 [0.68, 0.79] | 0.86 [0.80, 0.91] | 0.92 [0.89, 0.95] |
| coincidence, signed (no labels)                       | 0.217 | 0.47 [0.40, 0.54] | 0.77 [0.71, 0.83] | 0.85 [0.79, 0.90] | 0.92 [0.89, 0.96] |
| gradient boosting (trained with labels, clean market) | 0.911 | 0.98 [0.96, 0.99] | 0.98 [0.96, 1.00] | 0.98 [0.96, 1.00] | 0.99 [0.98, 1.00] |


## all three

| detector                                              |    AP | catch@1           | catch@3           | catch@5           | catch@10          |
|:------------------------------------------------------|------:|:------------------|:------------------|:------------------|:------------------|
| order-to-trade ratio                                  | 0.026 | 0.03 [0.01, 0.05] | 0.07 [0.02, 0.11] | 0.09 [0.04, 0.14] | 0.17 [0.10, 0.24] |
| isolation forest (no labels)                          | 0.023 | 0.01 [0.00, 0.02] | 0.01 [0.00, 0.03] | 0.02 [0.00, 0.03] | 0.05 [0.02, 0.09] |
| coincidence, unsigned (no labels)                     | 0.061 | 0.03 [0.01, 0.06] | 0.10 [0.04, 0.16] | 0.23 [0.15, 0.31] | 0.58 [0.49, 0.67] |
| coincidence, signed (no labels)                       | 0.075 | 0.20 [0.14, 0.28] | 0.41 [0.30, 0.52] | 0.52 [0.42, 0.63] | 0.69 [0.60, 0.78] |
| gradient boosting (trained with labels, clean market) | 0.89  | 0.98 [0.96, 0.99] | 0.98 [0.97, 1.00] | 0.98 [0.97, 1.00] | 0.99 [0.98, 1.00] |


## Honest group members flagged at p <= 0.01 (nominal 1%)

| scenario                | group     |   members scored |   flagged, unsigned |   flagged, signed |
|:------------------------|:----------|-----------------:|--------------------:|------------------:|
| + MM desks              | mm_desk   |             2622 |               0.711 |             0     |
| + fund splitting orders | fund_sub  |             5277 |               0.061 |             0.063 |
| + bot fleet             | bot_fleet |             3571 |               0.013 |             0.016 |
| all three               | mm_desk   |             2698 |               0.665 |             0.182 |
| all three               | fund_sub  |             5202 |               0.05  |             0.053 |
| all three               | bot_fleet |             3732 |               0.029 |             0.037 |
