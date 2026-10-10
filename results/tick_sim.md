# Simulated tick-size reduction (Vietnam preset, honest-only markets)

8 episodes per tick size. Tick multiplier m: prices are multiples of m base ticks; the base tick is 0.2% of the price, so m = 10 is about the pre-reform relative tick of a 25,000 VND stock (500 VND) and m = 1 the post-reform one (50 VND).

## Levels

|                   |      1 |      2 |      5 |     10 |
|:------------------|-------:|-------:|-------:|-------:|
| CS spread (%)     | 0.3353 | 0.4219 | 0.9548 | 2.2403 |
| daily range (%)   | 1.9563 | 2.1077 | 2.8314 | 3.9473 |
| |return| (%)      | 1.0085 | 1.0448 | 1.5618 | 1.8107 |
| zero-return share | 0.0739 | 0.1193 | 0.1307 | 0.3352 |
| log volume        | 9.2818 | 9.354  | 9.3925 | 9.5077 |
| quoted spread (%) | 0.636  | 0.847  | 1.8096 | 2.8967 |

## Changes

| tick reduction   | outcome           |   level before |   level after |   change |   s.e. |
|:-----------------|:------------------|---------------:|--------------:|---------:|-------:|
| 2 -> 1           | CS spread (%)     |         0.4219 |        0.3353 |  -0.0866 | 0.0711 |
| 2 -> 1           | daily range (%)   |         2.1077 |        1.9563 |  -0.1514 | 0.1092 |
| 2 -> 1           | |return| (%)      |         1.0448 |        1.0085 |  -0.0363 | 0.0945 |
| 2 -> 1           | zero-return share |         0.1193 |        0.0739 |  -0.0455 | 0.0283 |
| 2 -> 1           | log volume        |         9.354  |        9.2818 |  -0.0722 | 0.0267 |
| 2 -> 1           | quoted spread (%) |         0.847  |        0.636  |  -0.211  | 0.0324 |
| 5 -> 1           | CS spread (%)     |         0.9548 |        0.3353 |  -0.6195 | 0.099  |
| 5 -> 1           | daily range (%)   |         2.8314 |        1.9563 |  -0.8751 | 0.1224 |
| 5 -> 1           | |return| (%)      |         1.5618 |        1.0085 |  -0.5533 | 0.105  |
| 5 -> 1           | zero-return share |         0.1307 |        0.0739 |  -0.0568 | 0.0233 |
| 5 -> 1           | log volume        |         9.3925 |        9.2818 |  -0.1107 | 0.0246 |
| 5 -> 1           | quoted spread (%) |         1.8096 |        0.636  |  -1.1736 | 0.0587 |
| 10 -> 1          | CS spread (%)     |         2.2403 |        0.3353 |  -1.905  | 0.1577 |
| 10 -> 1          | daily range (%)   |         3.9473 |        1.9563 |  -1.991  | 0.2051 |
| 10 -> 1          | |return| (%)      |         1.8107 |        1.0085 |  -0.8022 | 0.1401 |
| 10 -> 1          | zero-return share |         0.3352 |        0.0739 |  -0.2614 | 0.0363 |
| 10 -> 1          | log volume        |         9.5077 |        9.2818 |  -0.2259 | 0.0221 |
| 10 -> 1          | quoted spread (%) |         2.8967 |        0.636  |  -2.2607 | 0.1371 |
