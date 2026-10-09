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

Vietnam preset (about 450 active accounts per window, 240 steps per day, 3000-step episodes of about 12 trading
days). Every policy faces the same set of 10 ring strategies, including the strongest ones found by evolution-strategy
search under each policy; the ring picks the best on selection episodes and the table reports separate episodes.
`gain` is block value plus trading profit in tick-lots (mean over 10 episodes, standard error in brackets).

| policy | ring gain | caught | net benefit after fine (5x) |
|---|---|---|---|
| no price band | 714k (87k) | - | - |
| band 7% (HOSE today) | 883k (143k) | - | - |
| band 10% or 15% | 714k (87k), identical to no band | - | - |
| band 7% + block priced at 60-step mean | 703k (121k) | - | - |
| band 7% + block priced at 240-step mean (1 day) | 573k (103k) | - | - |
| **band 7% + inspect 1 account per window** | **8k (6k)** | 40% | **-28k: ring prefers not to operate** |
| **band 7% + inspect 3 accounts per window** | **8k (6k)** | 80% | **-51k** |

- Inspection with a calibrated detector is the only lever that removes the benefit. The deterrence condition with a
  fine of m times the gain is a detection probability above 1/m (20% at m = 5, 10% at m = 10); the measured values
  are 40% and 80% with 0.2-0.7% of accounts inspected per window.
- The daily price band does not bind: the ring's price displacement is about 7 ticks (1.5% of price), well inside
  7%. Widening it to 10-15%, which the securities commission is studying, changes nothing for this manipulation.
- A block reference price at the one-day trailing mean cuts displacement to 0.1 tick but gain only by about a fifth
  to a third (within noise), because nearly all remaining gain is trading profit from herd-following, not block
  value. Its honest cost is about 1 tick (0.21% of price) on a block trade (`results/block_rule.md`).

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

## Limits

- The manipulators and the detector features were written by the same author. Separable footprints in the simulator
  say nothing about real manipulation, and no real order-level data has been used. `docs/vietnam_calibration.md` lists
  what could not be calibrated (spread, volatility, order-to-trade ratio). Simulated daily volatility is about 0.4%,
  below the assumed 1.5%.
- Every rule fact is from secondary sources (the exchange rulebooks could not be fetched); check them before reuse.
- Ring search is an evolution strategy with a small budget. Results from a single search run were non-monotone across
  policies (band 10% looked 5.6 times better for the ring than no band), which is why section 2 cross-evaluates a
  shared strategy set; the table is a lower bound on a fully adaptive ring's benefit.
- In the default simulator (no price band) a ring can exploit unbounded price run-ups, so the first set of
  best-response runs there is not reported (`results/notes/`).
- The block value of 3000 lots is an assumption (a stake held beforehand and sold off-book). Gain is dominated by
  trading profit from the simulated herd.
- A ring counts as caught if any member is inspected in any window and finding one member exposes the ring. Detection
  at larger account numbers than about 450 is untested.
- `retail trading cost` in section 3 falls under larger ticks because simulated noise traders mostly post passive
  orders and earn the wider spread, unlike retail investors in practice.
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
