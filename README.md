# marketsim

An agent-based limit order book simulator for designing and stress-testing market surveillance and exchange rules from
the regulator's side, with presets calibrated to the Ho Chi Minh Stock Exchange (HOSE), and public-data checks on real
Vietnamese markets. The paper draft is in `paper/` (`main_sn.tex` with `sections/`, `main_sn.pdf`; Springer Nature class `sn-jnl`); every table and figure in it is generated from
the CSV files in `results/` by `experiments/make_tables.py`, `make_figures.py` and `make_figures2.py`.

Questions it is built to answer:

1. Can manipulation by many colluding accounts be found when there are no labelled cases?
2. Against a manipulator that adapts, which regulatory lever removes the benefit: inspection capacity, the daily price
   band, a reference-price rule for off-book block trades, order-level rules, tick size?
3. What does each lever cost honest participants?
4. Do the answers survive a family of calibrated markets, and what can public data say about them?

## What is new and what is not

Not new: adversarial detection-versus-evasion loops on agent-based markets (Wang and Wellman, 2020), graph-network
detection of coordinated trading, audit games with limited budgets, time-shift and jitter tests for coincident events
(for example Liang et al., 2025). The searches behind this list were not exhaustive.

What this repository adds:

- **A label-free coincidence test with exact false-alarm control** (`marketsim/coordination.py`). For each account and
  window, signed order flow is compared with the aggregate flow of all other accounts through a tolerance-box filter; the
  statistic is compared with its exact circular-shift distribution, with the maximum taken over tolerances. The p-value is
  super-uniform under cyclic exchangeability, without labels. A signed variant nets buys against sells and is robust to
  honest groups that act in step (market-making desks, funds splitting parent orders, bot fleets).
- **Best-response evaluation of rules** against an adaptive ring (evolution-strategy search, cross-evaluated over a fixed
  strategy set) in a family of calibrated markets rather than one, with penalties tied to the Vietnamese fine cap of 5 or
  10 times the illegal gain (Becker deterrence condition: detection probability above 1/m).
- **Theory, verified by simulation** (`experiments/theory_checks.py`, `fit_power_law.py`): exactness of the shift test and its
  resolution limit when many accounts are ranked (Propositions 1-2), a power law in the number of accounts and the number of
  co-active members (Proposition 3, checked by Monte Carlo and fitted to the agent-based sensitivity results), the cancellation of
  symmetric market-making flow by netting (Proposition 4), a deterrence-capacity formula (Proposition 5) and a law for the
  block reference price (Proposition 6, checked by exact ex-post evaluation in `run_block_static.py`).
- **A stress test on real account-level order flow** (`experiments/run_real_accounts.py`): Hyperliquid order submissions
  (Zenodo 18184441) and fills; the exchangeability condition fails for a large share of accounts there, and a ring planted in
  the real flow is found only when it makes up about a fifth of the flow.
- **Public-data checks**: documented enforcement cases against a 1,551-stock daily panel (with random-stock and same-stock
  time placebos), Telegram pump events in tick data, and a difference-in-differences on the HOSE tick reform of
  September 2016 compared with simulated tick changes.

Not claimed: that any number from the simulator describes the real market, or that the detector works on real Vietnamese
accounts.

## Main results

All figures below are from `results/`; intervals are bootstrap intervals over episodes where stated.

### Detection (`results/ring_robust.md`, `ring_ablation.md`, `ring_detection.md`)

Catch@5 = share of ring-active windows in which a ring member is among the 5 top-ranked accounts of about 120-170.

| scenario | coincidence, unsigned | coincidence, signed | gradient boosting trained with labels |
|---|---|---|---|
| clean market | 0.85 | 0.87 | 1.00 |
| + market-making desks | 0.32 | 0.88 | 1.00 |
| + fund splitting orders | 0.71 | 0.74 | 0.99 |
| + bot fleet | 0.86 | 0.85 | - |
| all three honest groups | 0.23 | 0.52 | 0.98 |

- Without labels, the coincidence test finds rings where the order-to-trade ratio, isolation forest and pairwise correlation
  find none; false alarms are 1.1% of honest accounts at p <= 0.01.
- Honest synchronised groups crowd out the unsigned test (market-making desks flagged in 71% of windows); the signed
  variant removes that (0% for desks alone, 18% with all three groups).
- Where labels exist, supervised boosting is better everywhere. The test is useful only when labelled cases do not exist.
- Power falls with the number of accounts: catch@5 is 0.91, 0.84, 0.64, 0.28 at 100, 206, 373, 708 accounts.

### Policy levers (`results/vn_ensemble.md`, `vn_ensemble_stock.md`, `policy_matrix.md`)

Six index-level markets (daily volatility 0.9-1.4%) and a stock-level family (1.8-2.8%), each accepted by rejection against
cancel share, volatility and retail share. Ring gain relative to the no-policy case, median over markets (index level):

| policy | ratio to no policy | detection probability | deterred at fine 5x gain |
|---|---|---|---|
| daily price band 7% (HOSE today) | 0.97 | - | - |
| block trades priced at 60-step mean | 0.35 | - | - |
| block trades priced at 1-day mean | 0.11 | - | - |
| inspect 1 account per window | 0.17 | 17% | 2 of 6 markets |
| inspect 3 accounts per window | 0.18 | 42% | 5 of 6 markets |

Stock-level family (`results/vn_ensemble_stock.md`, six markets, no-policy gain median 164k): band 0.99; block at 60 / 240 steps 0.45 / 0.20 (one market still gains 131k at 240 steps); inspection of 1 / 3 accounts per window: detection 8% / 25%, ring deterred at fine 5x gain in 3 / 5 of 6 markets (the ring shrinks its operation to about 3% of baseline gain). Policy matrix in the first market, effects on honest quality
and on fixed manipulators: spoofing profit is not reduced by minimum resting time or cancel fees in the Vietnam preset
(the strictest settings raise spread by 7-8% and volatility by 21-24%); doubling the tick raises spread by about 35% and cuts depth by 10%; wash-trade
share is unaffected by all order-level levers; only the block reference price cuts the ring's gain.

### Theory checks and the power law (`results/theory_checks.md`, `power_law_fit.md`)

- Exact false-alarm control per account holds for the implemented test (rejection 0.0100 at the 1% level for Gaussian and 0.0102 for
  Poisson flows); with a shared bursty regime the unsigned test rejects 65% and the signed test 1.5%. A Bonferroni rule needs T >= N/alpha
  shifts, so with T = 300 it flags nothing for any N tested (50 to 1200).
- In a Gaussian-flow model the shift of the statistic is linear in the model correlation (R^2 = 0.993); the same law with two fitted
  constants explains the dependence of the agent-based catch@5 on the number of accounts, ring size and push probability (mean absolute
  error 0.043; held-out sweeps 0.045 to 0.088).
- Doubling the fine multiple from 5 to 10 cuts the capacity needed to deter a small ring by a factor of about 2.4 (3.0 to 1.2 accounts per
  window at 600 active accounts); the saving from screening over random inspection falls from 3.7 at 600 accounts to 2.0 at 2000.
- A trailing-mean reference price removes 58-61% of the block value at 60 steps and 87-98% at one day (the total gain falls to 28-44% at
  one day); the linear-ramp law has the right shape and overstates the retained value by 0.04 to 0.2.

### Real account-level order flow (`results/real_accounts.md`)

On Hyperliquid order submissions (SOL perpetual, 577,918 orders, 1,909 accounts), 28.5% of accounts with at least 3 orders in a window have
p <= 0.01 (signed; 33.4% unsigned) against a nominal 1%; the effective number of accounts, aggregate variance over the variance of a quiet
account, is about 10^6 against 470 accounts. A ring of 12 quiet accounts planted in the real flow is found in the top five in 80% of trials at
100 orders per member and push (20% of the flow of the window) and in none at 30 orders (6%). On fills the statistic is mechanically
contaminated by counterparty mirroring and must be applied to submissions. These data are from a crypto derivatives venue dominated by
automated accounts, not a Vietnamese market.

### Real data (public, no accounts)

- **Cases** (`results/case_validation*.md`): ten enforcement cases with documented periods. Market-adjusted abnormal return
  beats random stocks with probability 0.89 and the same stock on other dates with 0.87; 8 of 10 cases enter the daily
  top 10 of about 1,360 stocks (chance 15%). Volume surge looks uninformative against random stocks (0.33) but not against
  the same stock's other dates (0.90): the case stocks are ordinary HOSE stocks. 10, 20 and 60-day windows agree.
- **Telegram pumps** (`results/pump_events.md`, 701 events): standardised volume rises from 0.19 to 0.71 and buy imbalance
  from 0.03 to 0.23 in the last hours before the announcement; a detector with 0.05 false alarms per coin-hour fires in the
  last hour for 6% of events (16% at 0.25).
- **HOSE tick reform, 12 September 2016** (`results/tick_reform.md`, `tick_sim.md`): 282 HOSE stocks against 489 control
  stocks. Share of zero-return days falls by 0.071 [0.050, 0.092]; the Corwin-Schultz spread falls by 0.061 points
  [-0.133, 0.008] (about 8%), concentrated in low-priced stocks. The simulator predicts larger effects than observed for
  cuts of the tick by 5 to 10 times and similar ones for a halving. The reform's old tick could not be established.

## Limits

- No account-level data. The manipulators and detector features were written by the same author; separable footprints in
  the simulator say nothing about real manipulation, and the coincidence test has not seen real order data.
- The calibrated markets match cancel share, relative tick, volatility and retail share but not the spread (3 ticks against
  1 tick measured), tail heaviness or the near-zero serial correlation of daily returns (simulated lag-1 autocorrelation 0.49 at index level and 0.60 at stock level against -0.03 for VN30). Rule facts come from secondary sources (broker summaries,
  press); the exchange rulebooks were not fetched. The block size of 3000 lots is an assumption.
- The ring strategy set was found in the first market and is not re-optimised in each market of the families, so effects of
  rules are lower bounds on an adaptive ring's gain. A ring is counted as caught if any member is inspected.
- Case periods come from press reports quoting decisions (decision documents not opened); the price panel holds only
  currently listed stocks. Case stocks hit the daily band in their manipulation periods, which simulated rings (displacement
  about 0.5%) never do, so the band's null effect is a statement about rings of the simulated size.
- Superseded or default-simulator-only runs (including order-level lever results from the uncalibrated simulator and the
  first preset) are kept in `results/notes/` and do not carry over to the Vietnam preset.

Data sources used (public; not committed): Kaggle `keithvo/vnstockdata`, `khimduong/vn30-market-making`,
`vuthinh/vietnam-stock-market-ohlc-price-data`; Hugging Face `kjhq/Vietnam-Stock-Symbols-and-Metadata`,
`Go3x3/pump_and_dump_dataset`. See `data/README.md` and `docs/vietnam_calibration.md`.

## Run

```
pip install -e ".[dev]"
pytest
python experiments/run_ring_detection.py                 # base detection
python experiments/run_ring_robust.py                    # honest groups, signed test
python experiments/run_ring_ablation.py                  # accounts, ring size, push probability
python experiments/run_vn_policy.py && python experiments/run_vn_cross.py   # single-market best response
python experiments/run_vn_ensemble.py                    # index-level family
python experiments/run_vn_ensemble.py --vol-lo 1.8 --vol-hi 2.8 --sigma-lo 1.0 --sigma-hi 2.0 --tag _stock --n-draw 80
python experiments/run_policy_matrix.py                  # all levers, quality and manipulators
python experiments/run_block_static.py                   # block reference price: exact ex-post evaluation
python experiments/theory_checks.py && python experiments/fit_power_law.py   # propositions by Monte Carlo, power law fit
MARKETSIM_DATA=DIR python experiments/run_real_accounts.py          # real order flow (DIR/acct_data/...); --stage planted2 for the planted ring
python experiments/run_calib_sim.py [--check-all]        # simulated returns and re-measured moments of the accepted markets
python experiments/run_case_eventstudy.py --folder DIR   # cases in event time
python experiments/run_tick_sim.py                       # simulated tick cuts
python experiments/run_tick_reform.py --folder DIR       # real tick-reform DiD (daily panel)
python experiments/run_case_validation.py --folder DIR   # real enforcement cases (add --window 10/60 --tag _w10/_w60)
python experiments/case_stats.py --folder DIR            # case stocks against the market
python experiments/run_pump_events.py                    # needs the Telegram pump archives
python experiments/make_tables.py && python experiments/make_figures.py && python experiments/make_figures2.py
cd paper && pdflatex main_sn && bibtex main_sn && pdflatex main_sn && pdflatex main_sn   # Springer Nature template (sn-jnl, sn-basic)
```

On real order-level data: convert to the event schema in `marketsim/exchange.py` and call
`marketsim.coordination.scan_events`; `marketsim.calibrate.moments_from_events` computes calibration moments.

## Layout

```
marketsim/lob.py            matching engine (price-time priority, self-trade prevention)
marketsim/exchange.py       event log, positions, policy levers (tick, minimum rest, cancel fee, halt, band, block reference)
marketsim/agents.py         honest agents and groups, spoofer, pump-and-dump, wash pair, collusion ring
marketsim/sim.py            episode runner, market quality and manipulation diagnostics
marketsim/coordination.py   label-free coincidence test (unsigned and signed)
marketsim/baselines.py      pairwise correlation baseline
marketsim/features.py       account-window features and labels
marketsim/realdata.py       stock-level scores from public daily prices
marketsim/detect.py         account-level detectors and evaluation
marketsim/ring_adversary.py adaptive ring: search space, inspection, evolution strategy
marketsim/adversary.py      adaptive spoofer
marketsim/calibrate.py      calibration moments
marketsim/vietnam.py        HOSE preset
docs/vietnam_calibration.md rules, statistics, sources and confidence
paper/  experiments/  results/  tests/  data/
```
