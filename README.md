# marketsim

An agent-based limit order book simulator for designing and stress-testing market surveillance and exchange
rules from the regulator's side, with a preset calibrated to the Ho Chi Minh Stock Exchange (HOSE).

Questions it is built to answer:

1. Can manipulation by many colluding accounts be found when there are no labelled cases?
2. Against a manipulator that adapts, which regulatory lever actually removes the benefit: inspection capacity,
   the daily price band, a reference-price rule for off-book block trades, order-level rules?
3. What does each lever cost honest participants?

## What is new and what is not

Not new: adversarial detection-versus-evasion loops on agent-based markets
([Wellman and Wang, IJCAI 2020](https://humancompatible.ai/?p=37)), graph-network detection of coordinated trading
(for example [Losavio et al. 2026](https://arxiv.org/pdf/2604.24590)), and inspection or audit games with limited
budgets. The searches behind this list were not exhaustive.

What this repository adds, as far as a literature search found:

- **A label-free coordination detector with exact false-alarm control** (`marketsim/coordination.py`). For each account
  and window it counts submissions that coincide in time and side with *any other* account and tests the count against
  the exact circular-shift distribution. The p-value is calibrated without labels and without knowing who the
  manipulators are, so the false-alarm rate can be set from the inspection capacity. Pooling over accounts gives far
  more power than pairwise tests, which fail when a ring fragments its trading over many accounts.
- **Best-response evaluation of rules and inspection against an adaptive ring** in a simulator whose tick size, price
  band, lot size, participant mix and cancel share follow HOSE (`docs/vietnam_calibration.md`), with penalties set by
  the Vietnamese fine cap of 5 or 10 times the illegal gain.

Not claimed: that any number here describes the real market. See the limits section.

## Results

All tables are in `results/`. Rings: 6-30 accounts, fragmented orders, phases of accumulation, coordinated push,
distribution; outside the campaign each account trades like a noise trader.

### 1. Finding rings without labels (`results/ring_detection.md`)

16 test episodes per ring type; `catch@5` is the share of ring-active windows in which one of the 5 top-ranked accounts
(out of about 120 active) is a ring member.

| detector | default ring | many small accounts | jittered timing | stealth |
|---|---|---|---|---|
| order-to-trade ratio (exchange practice) | 0.00 | 0.00 | 0.00 | 0.00 |
| isolation forest, no labels | 0.02 | 0.07 | 0.02 | 0.16 |
| pairwise flow correlation, no labels | 0.00 | 0.00 | 0.00 | 0.00 |
| **coincidence test, no labels** | **0.90** | **0.88** | **0.88** | **0.73** |
| coincidence test, 4 windows pooled, no labels | 0.92 | 0.86 | 0.92 | 0.77 |
| gradient boosting trained on labelled default rings | 0.99 | 0.90 | 0.99 | 0.91 |

Calibration on markets without rings: 1.1% of honest accounts have p <= 0.01 (market makers 0.7%, momentum traders
2.7%). Where labels exist, supervised boosting is as good or better; the coincidence test is the only detector here
that works without them.

### 2. Which lever removes a ring's benefit (`results/vn_cross.md`)

Vietnam preset recalibrated on real data (about 580 active accounts per window, simulated daily volatility 1.14% against 1.16% measured
for VN30, 240 steps per day, 3000-step episodes of about 12 trading days). Every policy faces the same set of 7 ring strategies,
including the strongest ones found by evolution-strategy search under each policy; the ring picks the best on 20 selection episodes
and the table reports 20 separate episodes. `gain` is block value plus trading profit in tick-lots (mean, standard error in brackets).

| policy | ring gain | caught | net benefit after fine (5x) |
|---|---|---|---|
| no price band | 82k (28k) | - | - |
| band 7% (HOSE today) | 79k (29k) | - | - |
| band 10% or 15% | 81k (28k) and 82k (28k) | - | - |
| band 7% + block priced at 60-step mean | 22k (28k) | - | - |
| band 7% + block priced at 240-step mean (1 day) | 6k (21k) | - | - |
| band 7% + inspect 1 account per window | 14k (11k) | 20% | -36k |
| band 7% + inspect 3 accounts per window | 14k (11k) | 45% | -49k |

- The daily price band does not bind: the ring's price displacement is about 2.5 ticks (0.5% of price), far inside 7%. Widening it to
  10-15%, which the securities commission is studying, changes nothing for this manipulation.
- Inspection cuts the best ring's gain by about 83% and makes the expected net benefit negative at fines of 5 and 10 times the gain
  (-36k and -85k at B = 1), with 0.17-0.5% of accounts inspected per window. The deterrence condition is a detection probability
  above 1/m (20% at m = 5, 10% at m = 10).
- Pricing off-book block trades at a trailing mean cuts the best ring's gain by 73% (60 steps) to 93% (240 steps) at the point
  estimate; the 60-step reduction is 1.4 standard errors and the 240-step one 2. The honest cost is the gap between the last price
  and the trailing mean: 0.17% of price for 60 steps and 0.50% for 240 steps (`results/block_rule.md`).
- In the first, uncalibrated preset (daily volatility 0.4%) the ring's prize was ten times larger and the block rule looked weak;
  those results are kept in `results/notes/vn_preset_v1/`. The ranking of levers depends on the market's volatility.

### 3. Order-level levers against a fixed spoofer (`results/policy.md`)

Default spoofer and pump-and-dump agents that do not adapt; 16 episodes per policy, same seeds.

| policy | spread | volatility | retail trading cost | spoofing price impact | spoofing profit per episode |
|---|---|---|---|---|---|
| baseline | 2.6 ticks | 0.21 | 2.2 | 1.07 | 56 |
| tick size x4 | +124% | +50% | -54% (see limits) | -25% | 687 |
| minimum resting time 5 steps | 0% | -4% | +11% | +1% | 13 |
| minimum resting time 15 steps | +3% | +4% | +16% | -17% | -346 |
| cancel fee 2 | +1% | -1% | +36% | -5% | 128 |
| circuit breaker (6 ticks) | +1% | +2% | -6% | +3% | 43 |

A short minimum resting time removes the fixed spoofer's profit at small cost; larger ticks hurt quality without
stopping it; cancel fees are costly and ineffective. Spoofing is not what Vietnamese enforcement has prosecuted
(multi-account collusion dominates), and these manipulators do not adapt.

### 4. Single-account manipulation (`results/summary.md`)

Spoofing, pump-and-dump and wash trading with account-level features. Gradient boosting reaches recall 0.93-0.99 at
1% false positives even against less extreme (evasive) manipulators; isolation forest 0.02-0.18; the order-to-trade
rule 0. Evasive spoofing loses its price effect (1.08 ticks at evasion 0, 0.02 at evasion 1.0). This was the first
experiment; its manipulators are easy to separate by construction.

## Real data

Account-level order data, the input the coincidence test needs, is not public: only the exchanges (HOSE, HNX), the depository (VSDC)
and the securities commission hold it, so no real ring has been tested. What was obtained from public sources
(`results/real_data_stats.md`, `docs/vietnam_calibration.md`): VN30, VN-Index and VN100 bars from 2012 and 1.56 million
VN30 futures ticks with best bid and ask from 2024-2025 (Kaggle `keithvo/vnstockdata`, `khimduong/vn30-market-making`). They
fixed the volatility target (daily sd 1.16%) and showed that the real spread is one tick in 73% of quotes. Ways to get account-level
data: a data-sharing agreement with HOSE, HNX or the commission; the per-account trade tables in published case files (SJS with 26
accounts, FIR with 76); or academic access to account-level data in another market, to test the method there.

## Limits

- The manipulators and the detector features were written by the same author. Separable footprints in the simulator say nothing
  about real manipulation, and the detectors have not seen real order-level data.
- The Vietnam preset matches cancel share, relative tick and daily volatility but not the spread (3 ticks against a measured 1 tick),
  tail heaviness (excess kurtosis 4-5 daily, 40 at one minute) or volatility clustering; retail share is 0.72 against 0.75-0.82
  published. Every rule fact is from secondary sources (the exchange rulebooks could not be fetched).
- Ring search is an evolution strategy with a small budget. Single search runs were non-monotone across policies, so section 2
  cross-evaluates a shared strategy set; it is a lower bound on a fully adaptive ring's benefit. With 20 episodes per cell the standard
  errors are 20-100% of the means, so only the large differences (inspection, the 240-step block rule) are distinguishable from noise.
- In the default simulator (no price band) a ring can exploit unbounded price run-ups, so best-response runs there are not
  reported (`results/notes/`). The block value of 3000 lots is an assumption (stock held beforehand and sold off-book).
- A ring counts as caught if any member is inspected in any window, and finding one member exposes the ring. Detection was only tested at
  about 120 accounts (section 1) and about 580 accounts (section 2) per window, with different adversaries, so how it scales with the
  number of accounts is not established.
- Section 1 was measured in the default simulator (about 120 accounts), not the Vietnam preset.
- `retail trading cost` in section 3 falls under larger ticks because simulated noise traders mostly post passive orders and earn the
  wider spread, unlike retail investors in practice.
- The spoofer-versus-retrained-detector loop was stopped after three rounds (`results/notes/`).

## Run

```
pip install -e ".[dev]"
pytest                                            # 21 tests
python experiments/run_ring_detection.py          # section 1, about 10 minutes
python experiments/run_vn_policy.py               # strategy search per policy, about 15 minutes
python experiments/run_vn_cross.py                # section 2, about 15 minutes (reads results/vn_policy.md)
python experiments/run_policy.py                  # section 3
python experiments/run_block_rule.py
python experiments/real_data_stats.py --indices DIR --futures VN30F1M_data.csv   # needs the two Kaggle datasets
python experiments/run_experiments.py             # section 4
```

On real order-level data: convert to the event schema in `marketsim/exchange.py` and call
`marketsim.coordination.scan_events`; `marketsim.calibrate.moments_from_events` computes the calibration moments.

## Layout

```
marketsim/lob.py            matching engine (price-time priority, self-trade prevention)
marketsim/exchange.py       event log, positions, policy levers (tick, minimum rest, cancel fee, halt, band)
marketsim/agents.py         honest agents, spoofer, pump-and-dump, wash pair, collusion ring
marketsim/sim.py            episode runner, market-quality and manipulation diagnostics
marketsim/coordination.py   label-free coincidence test
marketsim/baselines.py      pairwise correlation baseline
marketsim/features.py       account-window features and labels
marketsim/detect.py         account-level detectors and evaluation
marketsim/ring_adversary.py adaptive ring: search space, inspection, evolution strategy
marketsim/adversary.py      adaptive spoofer
marketsim/calibrate.py      calibration moments
marketsim/vietnam.py        HOSE mid-cap preset
docs/vietnam_calibration.md rules, statistics, sources and confidence
experiments/  results/  tests/
```
