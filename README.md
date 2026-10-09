# marketsim

An agent-based limit order book simulator for studying whether market manipulation can be
detected from order-level data, from the point of view of a securities regulator.

Many heterogeneous agents trade in one price-time-priority order book. Some of them manipulate.
Detectors see only what a regulator sees (account, order id, side, price, quantity, counterparty);
ground truth is kept separate and used only for labels and diagnostics.

## What is simulated

| Agents | Behaviour |
|---|---|
| noise traders | random market and limit orders, random cancels |
| market makers | re-quote two levels per side, cancel all quotes each time, shift quotes with displayed depth imbalance (legitimate, very high order-to-trade ratio) |
| fundamental traders | trade against a noisy view of a latent value with random-walk and jump dynamics |
| momentum traders | follow price moves between 3 and 12 ticks |
| imbalance traders | trade in the direction of near-touch depth imbalance |
| institutions | slice a large parent order into market orders (legitimate lookalike of accumulation) |
| **spoofer** | layers large orders on one side, trades the other side, cancels, exits passively |
| **pump-and-dump** | accumulates, pushes with aggressive buys, sells into the move |
| **wash pair** | two colluding accounts trade with each other inside the spread |

Manipulators trade honestly (as noise traders) outside their active window. Each has an `evasion`
parameter in [0, 1]: smaller, farther from the touch, longer-lived, less cancellation-heavy orders.

Detection unit: one account in one 300-step window, 25 account-level features
(cancel ratios, relative order size, distance from mid, order lifetime, placed-versus-executed
side disagreement, counterparty concentration, price impact and reversal of own trades, ...).
Windows are labelled positive when the account submitted at least two manipulation orders in them.

Detectors: order-to-trade ratio rule, isolation forest (no labels), logistic regression, gradient boosting.
Evaluation splits by episode, fixes the operating point at 1% false positives on the training data
and applies it unchanged to shifted test data.

## Results

Full tables: [`results/summary.md`](results/summary.md). 3 independent repetitions, 40 training
episodes (non-evasive manipulators) and 20 test episodes per evasion level each.

Recall at the 1% training-FPR operating point (mean over repetitions):

| detector | evasion 0 | 0.5 | 1.0 |
|---|---|---|---|
| order-to-trade rule | 0.00 | 0.00 | 0.00 |
| isolation forest (unsupervised) | 0.18 | 0.08 | 0.02 |
| logistic regression | 0.99 | 0.98 | 0.86 |
| gradient boosting | 0.99 | 0.98 | 0.93 |

Mean price move of a spoofing cycle in the intended direction, 8 steps after the fake orders appear:
1.08 ticks at evasion 0, 0.51 at 0.5, 0.02 at 1.0.

What this says, within the simulation:

- The classic order-to-trade ratio is useless here: legitimate market makers sit far above the manipulators, so the 1%-FPR threshold is set by them.
- Unsupervised anomaly detection finds a minority of manipulation and flags market makers instead; it collapses as manipulators become less extreme.
- With only 87 labelled positive windows (3 episodes), supervised recall is 0.98 to 0.99 at evasion 0 and 0.88 to 0.91 at evasion 0.75. Training on a mix of evasion levels 0 and 0.5 generalises to levels not seen in training (recall 0.97 at evasion 1.0).
- For spoofing, the evasion levels that lower detection also remove the price effect: impact falls to zero at evasion 1.0 while gradient boosting still catches 98% of spoofing windows. Wash trading is the hardest to catch under evasion (recall 0.79 at evasion 1.0).

## Limits of these results

- The manipulators are written by the same author as the detectors' features. A strong supervised result shows the simulated footprints are separable, not that real manipulation is.
- Labels are complete and clean. Real surveillance has almost no ground truth.
- Evasion is a fixed one-dimensional knob, not an adversary that learns against the detector.
- Pump-and-dump loses money here (about -1.7 per share) and wash trading has no payoff mechanism, so those two are behavioural patterns, not equilibrium strategies. Spoofing earns a small positive amount (about 0.1 to 0.4 per share) that was not tested for significance.
- Honest behaviour is stylised; only market makers and institutions are hard negatives.
- No claim is made about any real market.

## Run

```
pip install -e ".[dev]"
pytest
python experiments/run_experiments.py --n-train 40 --n-test 20 --reps 3
```

`python experiments/run_experiments.py --n-train 8 --n-test 4 --reps 1` finishes in about a minute.

## Layout

```
marketsim/lob.py        matching engine
marketsim/exchange.py   event log, positions, ground-truth tags
marketsim/agents.py     honest agents and manipulators
marketsim/sim.py        episode runner, impact and profit diagnostics
marketsim/features.py   account-window features and labels
marketsim/detect.py     detectors and evaluation
experiments/            experiment runner
results/                tables from the last full run
tests/
```
