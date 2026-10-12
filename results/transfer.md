# Transfer of a supervised detector across simulated markets

GBM trained on 24 labelled default-ring episodes of the generic simulator; test on 16 ring episodes per market (default ring). `GBM trained in this market` uses labelled episodes of the test market itself.

## Per market

| family         | market         | detector                         |   catch@1 |   catch@3 |   catch@5 |   catch@10 |
|:---------------|:---------------|:---------------------------------|----------:|----------:|----------:|-----------:|
| default preset | Vietnam preset | label-free coincidence           |     0.147 |     0.275 |     0.367 |      0.495 |
| default preset | Vietnam preset | GBM trained on generic simulator |     0.752 |     0.899 |     0.917 |      0.945 |
| default preset | Vietnam preset | GBM trained in this market       |     0.927 |     0.954 |     0.954 |      0.963 |
| index level    | market 1       | label-free coincidence           |     0.188 |     0.375 |     0.464 |      0.589 |
| index level    | market 1       | GBM trained on generic simulator |     0.732 |     0.866 |     0.902 |      0.946 |
| index level    | market 1       | GBM trained in this market       |     0.964 |     0.973 |     0.982 |      0.982 |
| index level    | market 5       | label-free coincidence           |     0.153 |     0.297 |     0.369 |      0.441 |
| index level    | market 5       | GBM trained on generic simulator |     0.685 |     0.874 |     0.919 |      0.919 |
| index level    | market 5       | GBM trained in this market       |     0.937 |     0.964 |     0.964 |      0.973 |
| index level    | market 11      | label-free coincidence           |     0.27  |     0.459 |     0.559 |      0.712 |
| index level    | market 11      | GBM trained on generic simulator |     0.865 |     0.946 |     0.946 |      0.946 |
| index level    | market 11      | GBM trained in this market       |     0.973 |     0.973 |     0.973 |      0.982 |
| stock level    | market 14      | label-free coincidence           |     0.132 |     0.333 |     0.465 |      0.579 |
| stock level    | market 14      | GBM trained on generic simulator |     0.781 |     0.921 |     0.947 |      0.965 |
| stock level    | market 14      | GBM trained in this market       |     0.974 |     0.974 |     0.974 |      0.974 |
| stock level    | market 19      | label-free coincidence           |     0.069 |     0.147 |     0.224 |      0.345 |
| stock level    | market 19      | GBM trained on generic simulator |     0.828 |     0.922 |     0.931 |      0.94  |
| stock level    | market 19      | GBM trained in this market       |     0.931 |     0.966 |     0.974 |      0.974 |
| stock level    | market 23      | label-free coincidence           |     0.361 |     0.602 |     0.694 |      0.806 |
| stock level    | market 23      | GBM trained on generic simulator |     0.935 |     0.972 |     0.972 |      0.972 |
| stock level    | market 23      | GBM trained in this market       |     0.981 |     0.981 |     0.981 |      1     |
| trend-free     | market 9       | label-free coincidence           |     0     |     0     |     0     |      0     |
| trend-free     | market 9       | GBM trained on generic simulator |     0.838 |     0.906 |     0.923 |      0.932 |
| trend-free     | market 9       | GBM trained in this market       |     0.957 |     0.966 |     0.966 |      0.983 |
| trend-free     | market 11      | label-free coincidence           |     0.009 |     0.009 |     0.017 |      0.034 |
| trend-free     | market 11      | GBM trained on generic simulator |     0.828 |     0.905 |     0.914 |      0.922 |
| trend-free     | market 11      | GBM trained in this market       |     0.922 |     0.948 |     0.966 |      0.974 |
| trend-free     | market 15      | label-free coincidence           |     0     |     0.019 |     0.029 |      0.057 |
| trend-free     | market 15      | GBM trained on generic simulator |     0.514 |     0.771 |     0.838 |      0.933 |
| trend-free     | market 15      | GBM trained in this market       |     0.943 |     0.971 |     0.981 |      0.981 |

## Mean over markets of each family

|                                                        |   catch@1 |   catch@3 |   catch@5 |   catch@10 |
|:-------------------------------------------------------|----------:|----------:|----------:|-----------:|
| ('default preset', 'label-free coincidence')           |     0.147 |     0.275 |     0.367 |      0.495 |
| ('default preset', 'GBM trained on generic simulator') |     0.752 |     0.899 |     0.917 |      0.945 |
| ('default preset', 'GBM trained in this market')       |     0.927 |     0.954 |     0.954 |      0.963 |
| ('index level', 'label-free coincidence')              |     0.204 |     0.377 |     0.464 |      0.581 |
| ('index level', 'GBM trained on generic simulator')    |     0.761 |     0.895 |     0.922 |      0.937 |
| ('index level', 'GBM trained in this market')          |     0.958 |     0.97  |     0.973 |      0.979 |
| ('stock level', 'label-free coincidence')              |     0.187 |     0.361 |     0.461 |      0.576 |
| ('stock level', 'GBM trained on generic simulator')    |     0.848 |     0.939 |     0.95  |      0.959 |
| ('stock level', 'GBM trained in this market')          |     0.962 |     0.974 |     0.976 |      0.983 |
| ('trend-free', 'label-free coincidence')               |     0.003 |     0.009 |     0.015 |      0.031 |
| ('trend-free', 'GBM trained on generic simulator')     |     0.726 |     0.861 |     0.892 |      0.929 |
| ('trend-free', 'GBM trained in this market')           |     0.941 |     0.962 |     0.971 |      0.979 |
