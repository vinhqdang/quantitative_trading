# Telegram pump events (tick data)

701 events from 2 archive(s). Background: minutes between 24 h and 4 h before the pump.

## Profile around the pump (mean over events, 95% bootstrap interval over events)

| period              |   events | mean std. volume   | mean std. buy imbalance   |   mean 10-min log return |
|:--------------------|---------:|:-------------------|:--------------------------|-------------------------:|
| 4h to 3h before     |      701 | 0.19 [0.14, 0.24]  | 0.03 [0.00, 0.07]         |                   0.0006 |
| 3h to 2h before     |      701 | 0.23 [0.19, 0.28]  | 0.05 [0.03, 0.08]         |                   0.0005 |
| 2h to 1h before     |      701 | 0.31 [0.26, 0.35]  | 0.06 [0.03, 0.09]         |                   0.0006 |
| 60 to 30 min before |      701 | 0.31 [0.26, 0.37]  | 0.09 [0.05, 0.13]         |                   0.001  |
| 30 to 10 min before |      701 | 0.48 [0.42, 0.56]  | 0.17 [0.12, 0.23]         |                   0.0025 |
| last 10 min before  |      701 | 0.71 [0.64, 0.80]  | 0.23 [0.18, 0.29]         |                   0.0033 |
| first 10 min after  |      701 | 1.69 [1.60, 1.77]  | 0.50 [0.45, 0.54]         |                   0.0236 |

Alarm rate in the background set to 0.05 per coin-hour (threshold 3.11): alarm in the last hour before the pump for 6.0% of events; median lead 7 min when it fires.

Alarm rate in the background set to 0.1 per coin-hour (threshold 2.86): alarm in the last hour before the pump for 8.3% of events; median lead 8 min when it fires.

Alarm rate in the background set to 0.25 per coin-hour (threshold 2.50): alarm in the last hour before the pump for 16.4% of events; median lead 15 min when it fires.
