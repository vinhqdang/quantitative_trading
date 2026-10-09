# Case validation on public daily data

11 cases with a documented period were considered, 10 stocks are in the price panel (1D data, 1551 stocks, 2015-10-01 to 2025-09-30; about 1363 stocks have scores on a typical recent date). Window 20 trading days. Random-stock null: 300 stocks per case. Chance level: 0.5 superiority, 5% of cases with p < 0.05, and for the top-B lists the share of random stocks that reach the list on some date of the same period (reported next to each detector).

| detector             |   cases |   median peak percentile |   share of cases >= 0.99 |   mean superiority vs random stock |   share with p < 0.05 |   in top 10 on some date |   chance (random stock) top 10 |   in top 20 on some date |   chance (random stock) top 20 |   in top 50 on some date |   chance (random stock) top 50 |
|:---------------------|--------:|-------------------------:|-------------------------:|-----------------------------------:|----------------------:|-------------------------:|-------------------------------:|-------------------------:|-------------------------------:|-------------------------:|-------------------------------:|
| abnormal return only |      10 |                    0.996 |                      0.8 |                              0.886 |                   0.4 |                      0.8 |                          0.146 |                      1   |                          0.274 |                      1   |                          0.529 |
| combined (Fisher)    |      10 |                    0.997 |                      0.6 |                              0.78  |                   0.3 |                      0.6 |                          0.217 |                      0.6 |                          0.351 |                      1   |                          0.576 |
| isolation forest     |      10 |                    0.997 |                      0.7 |                              0.779 |                   0.1 |                      0.7 |                          0.213 |                      0.8 |                          0.335 |                      0.9 |                          0.536 |
| round trip only      |      10 |                    0.992 |                      0.6 |                              0.703 |                   0   |                      0.9 |                          0.761 |                      1   |                          0.807 |                      1   |                          0.895 |
| volume surge only    |      10 |                    0.631 |                      0   |                              0.327 |                   0   |                      0   |                          0.033 |                      0   |                          0.053 |                      0   |                          0.131 |


## By case (combined score)

| ticker   |   days |   peak percentile |   p vs random stocks |   superiority | top10   |   chance top10 | top20   |   chance top20 | top50   |   chance top50 |
|:---------|-------:|------------------:|---------------------:|--------------:|:--------|---------------:|:--------|---------------:|:--------|---------------:|
| FIR      |    113 |             0.975 |                0.317 |         0.683 | False   |          0.11  | False   |          0.207 | True    |          0.407 |
| SJS      |    192 |             0.981 |                0.373 |         0.627 | False   |          0.17  | False   |          0.3   | True    |          0.523 |
| PDR      |     83 |             0.999 |                0.033 |         0.967 | True    |          0.08  | True    |          0.163 | True    |          0.317 |
| PSH      |    332 |             1     |                0.053 |         0.973 | True    |          0.29  | True    |          0.457 | True    |          0.733 |
| AGG      |    531 |             0.982 |                0.653 |         0.347 | False   |          0.383 | False   |          0.593 | True    |          0.853 |
| PPT      |    587 |             0.997 |                0.257 |         0.745 | True    |          0.393 | True    |          0.567 | True    |          0.803 |
| CRC      |    106 |             0.981 |                0.203 |         0.797 | False   |          0.08  | False   |          0.173 | True    |          0.357 |
| GKM      |    128 |             0.998 |                0.037 |         0.963 | True    |          0.14  | True    |          0.25  | True    |          0.447 |
| PAS      |    507 |             0.996 |                0.287 |         0.713 | True    |          0.4   | True    |          0.577 | True    |          0.863 |
| HCI      |    146 |             1     |                0.023 |         0.988 | True    |          0.127 | True    |          0.223 | True    |          0.453 |
