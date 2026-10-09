# R1: finding colluding rings

24 labelled default-ring episodes for the label-using / fitted detectors; 16 test episodes per ring type. Ring accounts act as noise traders outside their active window. `catch@B`: share of ring-active windows in which one of the B top-ranked accounts (out of about 120 active) is a ring member.

## Calibration of the coincidence test on honest markets

|                                 |     0 |
|:--------------------------------|------:|
| honest accounts flagged p<=0.01 | 0.011 |
| of which market makers          | 0.007 |
| of which momentum               | 0.027 |
| of which noise                  | 0.01  |
| honest accounts flagged p<=0.05 | 0.061 |


## default

| detector                   |    AP |   catch@1 |   catch@3 |   catch@5 |   catch@10 |
|:---------------------------|------:|----------:|----------:|----------:|-----------:|
| otr                        | 0.031 |     0     |     0     |     0     |      0.019 |
| iforest (no labels)        | 0.032 |     0     |     0     |     0.019 |      0.056 |
| pairwise (no labels)       | 0.042 |     0     |     0     |     0     |      0.019 |
| coincidence (no labels)    | 0.208 |     0.463 |     0.806 |     0.898 |      0.981 |
| coincidence-4w (no labels) | 0.498 |     0.722 |     0.889 |     0.917 |      0.963 |
| gbm (labels)               | 0.925 |     0.991 |     0.991 |     0.991 |      0.991 |


## many small

| detector                   |    AP |   catch@1 |   catch@3 |   catch@5 |   catch@10 |
|:---------------------------|------:|----------:|----------:|----------:|-----------:|
| otr                        | 0.082 |     0     |     0     |     0     |      0.204 |
| iforest (no labels)        | 0.071 |     0.028 |     0.037 |     0.065 |      0.343 |
| pairwise (no labels)       | 0.084 |     0     |     0     |     0     |      0.037 |
| coincidence (no labels)    | 0.137 |     0.389 |     0.796 |     0.88  |      0.954 |
| coincidence-4w (no labels) | 0.184 |     0.509 |     0.787 |     0.861 |      0.991 |
| gbm (labels)               | 0.154 |     0.537 |     0.824 |     0.898 |      0.991 |


## jittered

| detector                   |    AP |   catch@1 |   catch@3 |   catch@5 |   catch@10 |
|:---------------------------|------:|----------:|----------:|----------:|-----------:|
| otr                        | 0.056 |     0     |     0     |     0     |      0.084 |
| iforest (no labels)        | 0.045 |     0     |     0.009 |     0.019 |      0.084 |
| pairwise (no labels)       | 0.064 |     0     |     0     |     0     |      0.019 |
| coincidence (no labels)    | 0.168 |     0.495 |     0.748 |     0.879 |      0.972 |
| coincidence-4w (no labels) | 0.336 |     0.664 |     0.86  |     0.916 |      0.981 |
| gbm (labels)               | 0.377 |     0.869 |     0.972 |     0.991 |      0.991 |


## stealth

| detector                   |    AP |   catch@1 |   catch@3 |   catch@5 |   catch@10 |
|:---------------------------|------:|----------:|----------:|----------:|-----------:|
| otr                        | 0.072 |     0     |     0     |     0     |      0.234 |
| iforest (no labels)        | 0.064 |     0.019 |     0.056 |     0.159 |      0.402 |
| pairwise (no labels)       | 0.075 |     0     |     0     |     0     |      0.009 |
| coincidence (no labels)    | 0.09  |     0.262 |     0.561 |     0.729 |      0.916 |
| coincidence-4w (no labels) | 0.098 |     0.28  |     0.598 |     0.766 |      0.953 |
| gbm (labels)               | 0.122 |     0.346 |     0.757 |     0.907 |      0.972 |

