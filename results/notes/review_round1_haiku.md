# Referee report, round 1

Manuscript: "Screening for Coordinated Manipulation and Evaluating Exchange Rules in a Vietnam-Calibrated Market Simulator" (single author), submitted to Computational Economics (Springer).

Basis: the compiled PDF (full text, tables and figure captions), the LaTeX sources (equations and captions that the PDF text layer garbles), and the result files the text cites (results/policy.md, policy_matrix.md, vn_policy.md, vn_cross.md, vn_ensemble*.csv/md, tick_reform.md, pump_events.md, real_accounts*.csv/md, case_validation*.md, case_stats.md, ring_ablation.csv). Section and table numbers refer to the manuscript. Verified inconsistencies are stated with the file that shows them. Literature claims were not checked against the cited sources and are flagged as such.

---

## 1. Summary of the submission

The paper proposes a label-free test for groups of accounts that trade in step: each account's signed submissions in a 300-step window are correlated with the aggregate of all other accounts, and a circular-shift randomisation gives a per-account p-value. It adds heuristic results on power (a square-root law in the number of accounts), on deterrence (a capacity condition linking inspection to a fine proportional to the gain), and on a block price set at a trailing mean. It evaluates exchange rules (price band, block reference price, inspection capacity, minimum resting time, cancel fee, tick size) by the best response of a ring over a fixed menu of four strategies, in two families of six simulated markets matched to HOSE moments. The test is also run on public Hyperliquid order flow, and public Vietnamese data are used for ten enforcement cases on daily prices, the 2016 tick reform (difference-in-differences), and 701 pump events. The headline policy claims are that the daily band has no effect, that a block price at a trailing mean removes most of the block value, that inspection deters only with enough capacity, and that minimum resting times and cancel fees do not help.

## 2. Significance and novelty

**New relative to the cited literature:** (i) the combination of a circular-shift coincidence test applied to accounts, with netting of buys against sells and a maximum over tolerances inside one null distribution (Sec 2 "Position"; Sec 4.1); (ii) the closed-form deterrence condition with a fixed inspection budget (Sec 4.5, Table 11); (iii) the calculus of the block reference price (Prop 6, Sec 4.6); (iv) an evaluation design in which rules are compared through the best response of a ring across a family of calibrated markets (Sec 4.7, Sec 6.1).

**Not new, or standard:** the circular-shift and jitter test comes from the neuroscience coincidence literature the paper cites (Grün 2009; Louis et al. 2010; Platkiewicz et al. 2017; Liang et al. 2025). The deterrence logic is Becker (1968) and Polinsky and Shavell (2000). The agent-based rule studies (Leal and Napoletano 2019; Zhang et al. 2016; Zhao et al. 2020) and the spoofing and pump detectors are cited. The theory is elementary (Gaussian approximations, a linear-ramp calculus, a union bound). The contribution for this journal lies mainly in the simulation design and in the failure analysis, not in the propositions.

**Literature gap (suggestion, not verified):** the related-work section does not discuss the economics literature on herding and synchronised trading measures. I would expect a referee in this journal to ask for that positioning.

**Fit:** reasonable for the simulator, the method and the policy experiments. The Vietnamese empirical checks and the policy recommendations are not supported at the level at which they are stated.

---

## 3. Major concerns

### M1. The "best response" is a choice among four fixed strategies, and the search that was not restricted to a menu is not reported

**Where:** Abstract; Sec 1 (contribution iv); Sec 4.7; Sec 6.1 ("Manipulators"); Sec 6.2; Sec 6.4; Sec 8.5; Tables 7–10; Table 14; Appendix C (table labelled Table 2).

**What is wrong.** Sec 6.1 says that every policy faces the same four strategies (the strongest found under different policies in one market, the default ring, and the strongest unconstrained ring), and that the ring picks the best of these on 12 selection episodes. Sec 8.5 says the strategy set "was found in the first market", and Sec 6.2 says the stock-level family uses the same set, "not re-optimised". The search is therefore a menu search, and the abstract's claim that the ring "picks its best strategy against each rule" overstates what was done. The earlier version (Appendix C; results/vn_cross.md) used seven strategies and 20 episodes; the main experiments use four and 12 episodes. The reason for the change is not given.

The one search that is not restricted to a menu is results/vn_policy.md (evolution strategy, population 8, five generations, started from the strongest unconstrained ring, one market). It is not reported in the manuscript; Sec 6.1 says only that single evolution-strategy runs "were noisy and non-monotone across policies". Its gains are 101k (no band), 49k (band 7%), 94k (band 10%), 84k (band 15%), 63k (block at 60 steps) and 24k (block at 240 steps). The band-7% gain is about half the no-band gain, which is the opposite of the "no effect" verdict. The block-60 gain (63k) is higher than the band-7% gain without a block, which a converged search should not produce, since the block credit lowers the payoff of the price path the ring creates (Table 10 shows retained shares below one). The file therefore shows that search noise is of the same order as the effects being interpreted. Nowhere in the paper is it shown that the four-strategy menu is near the optimum for each policy.

A second inconsistency is in Table 4. The 3000-lot gain with the last price as reference is 151k (index) and 297k (stock). Tables 7 and 8 report best-response medians of 110k and 164k for the same families and the no-band policy. If Table 4 pools selection and reporting episodes, it is biased upward by selection, which is the problem Proposition 7 is meant to remove. The caption does not say which episodes are used.

**Why it matters.** Every policy verdict (band, block, inspection, frictions) is conditional on the menu, and the paper's own search shows that the verdicts can change with the search.

**What would resolve it.** Report the per-policy search with standard errors and held-out evaluation, or show that the menu gain is within a stated tolerance of a converged per-policy optimum (larger menu, converged search). Explain why the menu shrank from seven to four. State which episodes each table uses. Otherwise, restate every policy conclusion as conditional on four fixed ring strategies, in the abstract, Sec 8 and Sec 9.

### M2. The direction of the bound in Proposition 7 is reversed, so the deterrence and rule claims are optimistic rather than conservative

**Where:** Sec 4.7 (text after Proposition 7: "deterrence results are upper bounds on what a regulator can claim"); Sec 6.1 ("Proposition 7: a lower bound on a fully adaptive ring"); Sec 8.5 ("the reported effects of the rules are lower bounds on what an adaptive ring gains").

**What is wrong.** Proposition 7 correctly gives E[Û | θ̂] = U(θ̂) ≤ V = sup over Θ of U. The reported ring benefit is therefore a lower bound on V, not an upper bound. A policy is deterring when V ≤ 0 (Sec 4.7). Showing a reported value ≤ 0 does not establish V ≤ 0; it is consistent with V > 0. The deterrence results (Tables 7–9, Fig 10, Table 11) are therefore optimistic for the regulator. The same holds for rule effects: an understated ring gain overstates how much a rule removes (Table 10, Sec 8.1). The "conservative" wording in Sec 4.7 and Sec 6.1, and the "lower bounds" wording in Sec 8.5, have the wrong sign.

**What would resolve it.** Produce an upper confidence bound on V (for example from a larger search checked on held-out episodes), or report the gap between the menu and a converged search (see M1). Until then, describe the reported values as lower bounds on the ring's benefit only, and remove the claim that they are upper bounds on what a regulator can claim.

### M3. The deterrence results rest on an independence assumption that the paper's own numbers violate, and the capacity figures are not like-for-like

**Where:** Sec 4.5 (Proposition 5 and proof); Sec 6.2 (stock-level family); Sec 6.5, Table 11, Fig 10; Sec 8.1 ("Inspection capacity and the fine are exchangeable"); the Appendix C table (labelled Table 2).

**Arithmetic.** Proposition 5 gives U = E[g] − mQ·E[g⁺] only if the detection event D is independent of the gain g given θ. The Appendix C table reports, for one inspected account per window, a mean gain of 13.8k with s.e. 11.4k over 20 episodes, a caught share of 20%, and U at m = 5 of −35.6k (and −85.1k at m = 10). Both m values imply E[g⁺·1_D] ≈ 9.9k. The s.e. implies a standard deviation of about 51k across episodes, so E|g| ≤ √(51² + 13.8²) ≈ 52.8k and E[g⁺] ≤ (52.8 + 13.8)/2 ≈ 33.3k. Under independence, E[g⁺·1_D] = Q·E[g⁺] ≤ 0.2 × 33.3k ≈ 6.7k, which is below 9.9k. So the detected episodes carry about three times the average positive gain, and independence cannot hold for these numbers. With four caught episodes out of 20 the estimate of Q is noisy, but the bound on the means does not depend on that. results/vn_cross.md contains the same figures. In the family runs the dependence goes the other way in some markets: in results/vn_ensemble.csv, market 26 has caught = 0.167 and net U(5) equal to the gain, so the detected episodes have no positive gain. The sign and size of the gain–detection covariance vary by market, and the closed form cannot be used without it.

**Further points in the same section.**
- Sec 6.2 explains the stock-level deterrence by "the ring's remaining gain is smaller relative to the fine". Under Proposition 5 (g ≥ 0) the threshold is Q ≥ 1/m and does not depend on the size of the gain. With a median detection probability of 8% and m = 5, mQ ≈ 0.4, yet three of six stock-level markets have U ≤ 0. The explanation is not in the theory.
- Sec 5.2 says the independent-members approximation overstates catch@5 by 0.13 on average. Q and the capacities in Table 11 are therefore biased toward too little capacity.
- Table 11 and Fig 10a use W = 4 windows for K = 3. The simulator exposes a ring in any window of an episode (Sec 3.2), and episodes have 19–20 windows (Sec 5). The model–simulator comparison in Fig 10a is not like-for-like, and the authors note this only for the ring's size.
- The capacities in Table 11 are fractional. At N = 100 the screening requirement is 0.05 accounts per window and the saving is 36.5 (50.2 at the 10× fine). With B rounded up to an integer, the saving at N = 100 is about 2.
- The "2.4-fold" saving in Sec 8.1 and the N = 2000 entries of Table 11 extrapolate the N^(−1/2) law beyond the simulated range (100–1000). The free exponent in Sec 5.2 is 0.32, not 0.5.
- The fine multiples m = 5 and m = 10 come from press summaries of Decree 156/2020 (Appendix B), not from the decree. Every capacity and deterrence result depends on them.

**What would resolve it.** Report E[g⁺·1_D] and E[g | D] in the simulator. Restate Proposition 5 with the covariance term. Use integer capacities with intervals, the simulator's own W and K, and an explicit uncertainty on the exponent. Check m against the decree text.

### M4. Theory: what is correct, what is approximate, and what is missing

The checks requested in item (a) of the brief. I re-derived the algebra; the results are as follows.

- **Proposition 1 (exact per-account validity).** The proof is correct: the rank argument (at most r indices m satisfy R_m ≤ r) and the averaging over shifts are valid. The premise is strong: the joint law of (x_i, y_{−i}) must be invariant under a cyclic shift of x_i alone. This fails for any flow with intraday seasonality (open and close, time-of-day pattern) and for a trend inside the window, and wrap-around creates artificial adjacency between the end and the start of the window. Sec 4.2 says the condition is strong, but the paper does not say whether real or simulated flows are deseasonalised before testing.
- **Proposition 2.** Correct. The bound and the Bonferroni arithmetic (N_max = α₀T = 15) are right, and the guarantee is correctly described as per account.
- **Proposition 3.** I checked the algebra of (3), the saturation level √(η/(1+η)) in (i), the N^(−1/2) rate in (ii), and the detectable size in (iii) with √T_eff; these are correct as written in the source. The text labels the result an approximation (Sec 4.3). The approximation ignores the maximum over tolerances and the correlation induced by the box filter. The fitted constant (√T_eff = 7.3, i.e. T_eff ≈ 53 against about 100 from the theory) is off by roughly a factor of two. R² = 0.993 in Fig 3c is uncentred, from a regression through the origin, and is not comparable with a centred R².
- **Proposition 4.** Correct under the stated symmetric model. The argument relies on common drivers entering both sides equally. Sec 7.1 notes that real market makers do not behave this way, so the netting argument does not carry over to the real data. This is stated, which is fine.
- **Proposition 5.** Correct as a conditional statement; the independence premise is the problem (M3).
- **Closed form (6).** I checked it. With Q = 1 − (1 − q)^{KW} and the definitions of r* and q*, q* = 1 − (1 − 1/m)^{1/(KW)}, which is the solution of Q = 1/m. The formula for B* then follows from (4).
- **Proposition 6.** Correct for the ramp. Under the stated convention the discrete sum gives D_L/D_1 = (a+1)/(2L) for L ≥ a, not a/(2L); the difference is about 1% for a = 72–83. The ramp is an approximation to the real price path, and the text says so (Sec 6.4).
- **Proposition 7.** The statement is correct; the interpretation is reversed (M2).

### M5. The simulator is called Vietnam-calibrated, but the spread and the serial correlation are off, and the family used to test trending is small and confounded

**Where:** Title; Abstract; Sec 3.3 and Table 4; Sec 6.3 and Table 9; Sec 6.7; Sec 8.5.

**What is wrong.** Table 4 gives the share of quotes at one tick as 0 in the simulator against 0.73 in VN30 futures quotes, and the text says the simulated spread is three ticks. A market that never quotes at one tick does not match the tick experiment (Sec 6.7, Table 13) or the spread costs in Table 12. The lag-1 autocorrelation of daily returns is 0.49 at index level and 0.60 at stock level, against −0.03 and 0.03 in the data. Sec 6.3 says that a ring may profit from the trending. The no-trend family, which is the only test of this, has four markets, a widened retail-share tolerance (0.55–0.85), an acceptance rate of 4 of 29, and about 630–1070 noise and fundamental traders against 400–670 in the main families. The trending comparison and the account-count comparison are therefore confounded. The paper acknowledges the confound for inspection only.

**What would resolve it.** Calibrate spread and autocorrelation jointly, or drop "Vietnam-calibrated" from the title and state the mismatch in the abstract. Build a no-trend family that varies N separately, with enough accepted markets (ideally 20 or more) to report a distribution, and report whether the block-price and band conclusions survive.

### M6. The signed statistic is blind by construction to a threat the paper's own cases describe: cross trading among accounts

**Where:** Sec 3.1 (ring: "with some cross trades"); Table 2 (cross share 0–0.5); Sec 4.4 (netting); Table 5 and the Appendix D ablations (tolerances, window, noise traders, ring size, push probability; no cross share); Sec 7.2 and Appendix A (types); Sec 8.2.

**What is wrong.** The signed statistic correlates same-side flow. If one member buys and another sells the same quantity in the same step, the pair appears as opposite-side flow, which lowers the statistic. Netting therefore removes the signal of cross trading. Appendix A describes four of the ten scored cases as cross trading or cross-matched orders among own accounts (FIR, PDR, CRC, HCI), and one more (PSH) as negotiated trades within a group. The unsigned variant does not count the buy–sell pair as a coincidence either. Some best responses in results/vn_policy.md use cross shares of 0.09, 0.17 and 0.2, so a ring can exploit the blind spot. The paper gives no power curve against cross share. The planted-ring test (Sec 7.1) adds buy orders only, so it does not test this either. Sec 4.4 treats netting as a cost in power for a ring that submits unrelated opposite-side orders. The cross-trade case is a different and more important issue, because it is the pattern the regulator most needs to see.

**What would resolve it.** Power as a function of cross share (0 to 0.5) in the simulator. A planted cross-trading ring on real flow (matched buy and sell pairs at common steps). A clear statement in Sec 4.4 and Sec 8.2 that the signed test does not detect cross trades, and consideration of a pair-based statistic.

### M7. The conclusions on order-level frictions and on the band rest on non-adaptive manipulators, and an uncalibrated-simulator result contradicts the main text without discussion

**Where:** Abstract (last sentences); Sec 6.6; Table 12 and caption; Table 14 row "minimum resting time, cancel fee"; Sec 8.1 ("Do not use order-level frictions or the band against rings"); Sec 9; the Appendix D table labelled Table 6.

- (a) The Table 12 caption says "Manipulators do not adapt." The claim that frictions do not reduce what manipulators achieve is therefore a claim about fixed strategies. A best response could change order sizes or timing, and that is not tested. The recommendation in Sec 8.1 does not follow from this evidence.
- (b) The abstract says the frictions "leave fixed manipulators' gains unchanged". Table 12 shows spoofing profit rising from 872 to 1,091–1,380 under minimum resting times and cancel fees (+25% to +58%) and pump impact falling from 0.47 to 0.31 under cancel fees. Only the ring's gain is unchanged.
- (c) The Appendix D table (source: results/policy.md, the "uncalibrated" simulator) shows a minimum resting time of 15 steps cutting spoofing profit from 56 to −346. The entries are absolute values, although the header says "changes relative to the baseline". The appendix says the main text does not use that simulator. The disagreement between the two simulators on the same question is the most relevant evidence for the recommendation, and it is not discussed. The paper should say which calibration is right and how the recommendation depends on that.
- (d) Honest costs are measured by spread, depth and volatility, not by welfare. The retail-cost column moves in the wrong direction under larger ticks and fees; the paper calls this an artefact but keeps the column. Sec 8.1 says a doubled tick "costs honest participants a third of the spread", but the simulator widens the spread by 35%. Sec 6.6 says depth falls by 10%, while Table 12 shows −9%.
- (e) The block rule's effect scales with the assumed 3000-lot off-book block, for which no daily volume is given. The Appendix D block-size table (labelled Table 4) shows the retained share at L = 240 moving from 19–21% at 10,000 lots, to 28–44% at 3,000 and 60–64% at 1,000. The "0.2–0.5%" cost is the gap between the last price and the trailing mean, not a cost measured on negotiated trades (Sec 8.1 says so). The feasibility of setting a reference price for negotiated trades is not discussed. The statement that the rule is "the only one that cuts the ring's gain through a mechanism that can be written down" needs the qualification in M1.

**What would resolve it.** State the non-adaptive assumption where the frictions conclusions appear (abstract, Sec 8.1, Sec 9). Put the uncalibrated results in the main text with the disagreement explained, or remove them. Report the block size relative to volume and the conditions under which the rule is feasible. Use a welfare measure or drop the welfare language.

### M8. The 2016 tick-reform estimate is not identified well enough for the policy advice drawn from it

**Where:** Sec 6.7; Table 13; Fig 12; Sec 8.1 ("Do not undo the 2016 tick reform"); Table 14 (row "tick size").

- (a) **Inference.** There is one reform date. The variation in time is a single event, and the variation across stocks is by exchange. The bootstrap over stocks (results/tick_reform.md) treats the 282 HOSE stocks as independent draws and does not account for the common shock on the reform date. Inference over time is needed: a placebo distribution over many dates, or a synthetic control on the index.
- (b) **Placebos.** Four placebo dates are used. For the spread, the placebo of 14 March 2016 gives a DiD of −0.055 (CI −0.127 to +0.006), almost the same as the reform estimate (−0.061). For the daily range, the placebos are −0.36 (14 March 2016) and +0.44 (13 June 2016), both with intervals excluding zero. The design noise is large relative to the reform estimate, and "a larger change than in any of four placebo dates" needs a magnitude.
- (c) **Windows.** The spread DiD is −0.028 with 20-day windows (CI −0.115 to +0.050), −0.061 with 40-day windows (−0.133 to +0.008) and −0.072 with 60-day windows (−0.141 to −0.006). Sec 6.7 reports the 60-day spread and the 20-day zero-return share, but not the 20-day spread. The zero-return share falls under all windows; the spread does not.
- (d) **Pre-trends.** The weekly pre-reform differences in the spread range from −0.145 to +0.092 points, comparable in size with the post-reform differences (about −0.02 to −0.11). A joint pre-trend test is needed.
- (e) **Controls and sample.** HNX and UPCoM stocks differ from HOSE stocks in size and liquidity. The file shows 389 HOSE and 926 control stocks with data, and the analysis uses 282 and 489. The reason for the drop (listing, data gaps, survivorship) is not given.
- (f) **Magnitude of the tick change.** The old tick is unknown (Sec 6.7). The simulated factors of 2, 5 and 10 are therefore not tied to the actual change. The price-tercile result (the spread effect is concentrated in low-priced stocks) could serve as a dose-response check if the tick cuts differed by tier. The tiers in Appendix B suggest that they might, but the paper does not establish it.
- (g) **Simulator comparison.** The simulated spread response to a halved tick (−21%) is about 2.6 times the real estimate (−8%), and the simulated spread is about three ticks against one tick for most real quotes (M5). The simulated zero-return response is also larger (−38% against −24%). The signs agree, but the simulator is not validated on magnitude.
- (h) **Policy.** "Do not undo the 2016 tick reform" and "we found no evidence that it deters rings" (Sec 8.1) are not supported. The spread estimate is not significant at 20 days. The simulator's tick test for rings is one non-adaptive ring in one market (Table 12: ring gain 30k against 34k), and Table 14 itself says the tick was "not tested for rings".

**What would resolve it.** Time-series inference and a joint pre-trend test. All window results in the table. The reason for the sample drop. A fuller history of tick sizes by tier. Removal of the policy sentences, or narrowing them to the liquidity evidence.

### M9. The real account-level stress test (Sec 7.1) cannot establish the null, and the planted ring is narrow

**Where:** Sec 7.1; Table 15; Table 16; Fig 13; Sec 8.2; Abstract ("the exchangeability condition fails for more than a quarter of the active accounts ... a planted ring of 12 quiet accounts is found only when it makes up about a fifth of the flow").

- (a) **Null.** The accounts are pseudonymous addresses on a crypto perpetual venue, and the text says one operator may use several addresses. The honest background is therefore not a set of independent agents. The paper's reading of Table 15 is that exchangeability is violated because accounts "react to the same signals". That is one explanation of the excess rejections, but genuine coordination among real accounts produces the same excess, and the data cannot separate the two. Table 15 shows that the null is miscalibrated; it does not show the mechanism.
- (b) **Sample.** A single 23.6-minute slice of one perpetual on one day, with nine windows. The 180 trials in Table 16 are nine windows times 20 draws and are not independent. No replication across days or assets is reported.
- (c) **Planted ring.** Buy orders only, at ten common bins, with no price impact and no reaction by other accounts. Results depend strongly on the member tier. For three orders per push at N = 468, catch@5 is 0.24 when members are drawn from all accounts and 0.00 when drawn from quiet accounts (results/real_accounts_planted.csv). Table 16 does not state which tier it uses; the text describes quiet accounts. The abstract's "about a fifth of the flow" applies to quiet members only.
- (d) **Reference configuration.** The configuration N = 468, K = 12, 100 orders, 10 pushes appears in three rows of Table 16 with different values: unsigned catch@5 of 0.87, 0.82 and 0.83, and signed catch@5 of 0.80, 0.79 and 0.79 (results/real_accounts_planted2.csv). With 180 correlated trials, differences of this size are plausible noise, but one reference value with an interval should be shown, and the seeds should be stated.
- (e) **Neff.** The effective number of accounts, Neff ≈ 106 (Sec 7.1, cross-referenced to Sec 4.3), is computed as the variance of the aggregate divided by a quiet account's variance. This is not the Neff of Sec 4.3, which is a ratio of the other accounts' variances, and it assumes independence of the other accounts, which the paper says does not hold.
- (f) **Hypothesis presented as a finding.** "Netting buys against sells barely lowers the rate, unlike in the simulator: real market makers ... shift both quotes in the direction of the last price move." No test is reported.
- (g) **Overstated support.** Sec 2 says the synchrony finding of Saavedra et al. (2011) "is borne out on real order flow (Section 7.1)". Sec 7.1 does not measure the profitability of synchronised accounts, so it does not test that finding.

**What would resolve it.** State the tier and the seeds. Report block-bootstrap intervals over windows and days. Add a second asset or day. Test buy–sell pairs (M6). Remove "borne out", or add a profitability test. Describe the planted ring as a best case for detection, since it has no price impact and no reaction.

### M10. The enforcement-case analysis (Sec 7.2) measures price run-ups, and the stability claim is contradicted by Table 18

**Where:** Sec 7.2; Tables 17–19; Fig 14; Abstract ("a price-based rank puts 8 of 10 documented cases in the daily top ten"); Appendix A.

- (a) **Criterion.** The score is the best daily rank a stock reaches on any date in its documented period, and the periods last 83–587 trading days. With long periods the criterion has many chances to succeed. Table 17 gives a top-50 chance of 54% for the abnormal-return rank, so the top-B criterion is weakly selective. A per-day rate of top-B membership within the case period, compared with matched non-case periods, would be a fairer test.
- (b) **Stability.** Table 18 gives the top-10 count for the abnormal-return rank as 9/10 (10-day window), 8/10 (20-day) and 3/10 (60-day). The chance falls from 0.23 to 0.14 to 0.07 (results/case_validation_w10.md, _w60.md). The text says "the abnormal-return result is stable across window lengths", referring to superiority only. The count is not stable.
- (c) **Direction of prices.** In Table 19 (log return times 100), three of the nine stocks with pre-period history fell over their periods: PDR −119, PAS −87 and PSH −12. The text says "the price runs up" (Sec 7.2, Fig 14). The average path rises, but the three falling cases are not discussed, and an absolute-return score would flag them as well.
- (d) **Case counts.** The same-stock comparison (superiority 0.87 in Table 17) appears to use seven cases. In the per-case table of results/case_validation.md the same-stock columns are empty for AGG, PPT and PAS. The number of cases behind each statistic should be stated.
- (e) **Period definitions.** The periods come from press reports, and each start date is likely to have been set partly from the price path. The event-time analysis (Fig 14) is then partly circular. The paper should say how each period was defined.
- (f) **Pre-registration.** "Fixed before the cases were scored" needs a dated record (commit or pre-registration).
- (g) **Sample.** Table 19 includes PAS (UPCoM), GKM (HNX) and HCI (exchange not identified), but the text calls the case stocks "ordinary HOSE stocks" (Sec 3.3, Sec 7.2). PPT is absent from Table 19 without explanation.
- (h) **Abstract.** "8 of 10 ... in the daily top ten" should say "on at least one day of the period" and appear next to the chance levels.

**What would resolve it.** A per-day test with matched-period nulls. The window table reported as it is, with the stability and "price runs up" statements corrected. A per-case table of period definitions and case counts. A clear sample description.

### M11. The pump-event analysis is not Vietnamese and has no control group

**Where:** Intro item (v) ("what public data on Vietnam can say: documented enforcement cases and pump events"); Sec 7.3; Table 3 (row "701 Telegram-organised pumps"); Appendix B; Sec 2 (channel pumps and "which coin will be pumped").

- (a) **Venue.** Sec 7.3 uses "coin" and "coin-hour", and the Sec 2 description of channel pumps refers to coins. The events appear to be cryptocurrency pumps. Sec 7.3 does not give the venue or country, and the introduction lists the events under public data on Vietnam. This needs correction.
- (b) **Baseline.** The baseline is the same coin's background from 24 to 4 hours before the pump. Intraday seasonality and the clustering of pumps in active hours are not removed. There is no control group of non-pumped coins at the same clock times.
- (c) **Pump time.** The text does not define the pump time. If it is set at the price jump (Fig 15 shows a return of about +2.4% in the first 10 minutes), the volume and imbalance rise just before it are partly mechanical.
- (d) **Early warning.** The figures of 6.0%, 8.3% and 16.4% of events alarmed in the last hour depend on a threshold set from an assumed background alarm rate (0.05, 0.10 and 0.25 per coin-hour; results/pump_events.md). The detection statistic is not described in the main text. The conclusion "It does not give early warning" depends on both.
- (e) **Inference.** "This supports the accumulate–push structure of the simulated ring" is an inference from averages without a placebo.

**What would resolve it.** Name the venue, define the pump time, add a matched control of non-pumped coins at the same clock times, describe the alarm statistic, and move the analysis out of the Vietnamese checks.

### M12. Statistical reporting: six markets per family, approximate Bayesian acceptance, multiplicity, and interval claims

**Where:** Sec 5 (preamble); Sec 5.5; Sec 6.1; Sec 6.3; Tables 5 and 7–9; Table 3 of Appendix D.

- (a) **Sample size.** Family-level statements (medians, "deterred in 5 of 6 markets", "range over markets") rest on six markets per family, or four in the no-trend family. No interval is reported over markets. Counts of 2, 3 or 5 out of 6 are not distinguishable at this sample size.
- (b) **Acceptance.** The approximate Bayesian rejection accepts draws on two-episode estimates of volatility, cancel share and retail share. On re-measurement over 16 episodes, one of six index-level markets and two of six stock-level markets fall outside the volatility tolerance (Appendix D Table 3; Sec 6.1). The accepted set is therefore not a posterior sample. "The distribution of the ring's value over markets" is a distribution over six noisy draws. This should be described as such, and sensitivity to the tolerances should be reported.
- (c) **Episode counts.** Bootstrap intervals use 24 episodes in Sec 5 and Fig 6, 16 in Fig 7 and Table 5, and 12 selection plus 12 reporting episodes in Sec 6. Episode lengths are 6000 steps in Sec 5 and 3000 steps in results/vn_policy.md. Each table's design should be stated.
- (d) **Sensitivity claim.** Sec 5.5 says "the tolerance set and the window length matter little (catch@5 between 0.88 and 0.91)". The Appendix D ablation table shows catch@1 moving from 0.41 to 0.56 to 0.58 across windows of 150, 300 and 600 steps, and from 0.44 to 0.55 to 0.56 across tolerance sets. Proposition 3 says the window length should matter (through √T_eff). The sentence should be qualified with catch@1.
- (e) **Multiplicity.** The tick DiD reports five outcomes, three windows and four placebos. The case analysis uses six features, three windows and four detectors. No adjustment or discussion is given.

**What would resolve it.** Intervals across markets (for example a hierarchical or bootstrap summary over markets). An explicit sensitivity analysis of the acceptance step. Uniform reporting of episode counts. Qualified sensitivity statements. An account of multiplicity.

### M13. Claims in the abstract, introduction, discussion and conclusion go beyond what the results show

- **Abstract, "the law fits an agent-based market."** The free exponent is 0.32, the held-out error is 0.085 against an in-sample 0.043, and the law is a two-constant fit to 11 points (Sec 5.2). The conclusion ("power falls like the inverse square root") states it as a result.
- **Abstract, "is unaffected by the daily price band."** This is conditional on the four-strategy menu (M1) and on a market with trending that the paper itself calls non-representative (M5). The one per-policy search (results/vn_policy.md) does not confirm it.
- **Abstract, "minimum resting times and cancel fees leave fixed manipulators' gains unchanged."** See M7(b).
- **Abstract, "in simulated markets matching moments of the Ho Chi Minh Stock Exchange."** See M5.
- **Abstract and Sec 7.2, "8 of 10 ... top ten."** See M10(a), (h).
- **Intro item (v), "public data on Vietnam ... pump events."** See M11(a).
- **Sec 2, "borne out on real order flow."** See M9(g).
- **Sec 4.7, Sec 6.1 and Sec 8.5, "conservative" and "lower bounds."** See M2.
- **Sec 6.2, stock-level deterrence "not worse" because the gain is smaller relative to the fine.** See M3.
- **Sec 7.2, "stable across window lengths."** See M10(b).
- **Sec 8.1, "Do not undo the 2016 tick reform" and "no evidence that it deters rings."** See M8(h).
- **Sec 8.4, "the structure that drives the results is not specific to Vietnam."** The results depend on Vietnamese rules and calibrations (band, tick, cancel share, retail share, fine caps) and on the ring design. The paper's own list (Sec 8.4) of what must be re-estimated for another market confirms that the results need recalibration.
- **Sec 5.4 and Sec 8.5, the case for a label-free test.** The paper argues that a supervised model trained in simulation may not transfer to real rings, but it never tests transfer across its own simulator configurations. The supervised model trained only on clean rings reaches AUC 0.98 with all three honest groups (Fig 6c), so the honest groups that defeat the label-free test do not defeat the supervised model in this simulator. A transfer test (train on one family or configuration, test on another) would test the premise directly.
- **Sec 5.3 and Sec 8.2, the order-splitting fund.** Sec 5.3 calls it "genuinely coordinated"; Sec 8.2 calls it an "honest fund" flagged at six times the nominal rate. Choose one label. If it is honest, its flags are false positives and the per-account false-flag rate should be reported; if coordinated, the table should not count it as an error.

**What would resolve it.** Revise each sentence to match the evidence, or add the analysis that would support it.

### M14. Reproducibility and data availability

- (a) **Data.** The Vietnamese source data (the Kaggle and Hugging Face sets listed in Appendix B) are not in the repository, which holds only data/README.md and data/cases.csv. I did not find code that downloads or preprocesses them (a search of experiments/, marketsim/, data/ and README.md for kaggle, huggingface and hf_hub returned nothing). Tables 13 and 17–19 therefore cannot be regenerated from the repository alone. Provide the download and preprocessing scripts, checksums, and the licence status.
- (b) **Unverified inputs.** Several inputs come from press or broker summaries and are not checked against primary documents: the tick tiers, the HCI band, the fine caps, and the December 2020 cancel share used as a 2022–25 moment (Sec 3.3, Table 4, Appendix B). Conclusions that depend on them (Table 11, Sec 6.7) should say so where they are stated.
- (c) **Stale header.** results/vn_ensemble_acf.md states the retail tolerance as 0.66–0.85, while Sec 6.3 says 0.55–0.85. The header is hard-coded and the run used a command-line override. The header should be generated from the run's parameters.
- (d) **Configurations.** Two simulator configurations appear in the results: the "Vietnam preset" (results/policy_matrix.md, Table 12) and the "uncalibrated" default (results/policy.md, Appendix D table). The Appendix C design (seven strategies, 20 episodes; results/vn_cross.md) differs from the main design (four strategies, 12 episodes). The text does not map each table to a configuration, and it should.
- (e) **Licence.** The fills source "declares no licence" (Appendix B) and is used. Justify the use or state the terms.
- (f) **Links and names.** The code URL in the Code availability statement contains a space ("quantitative trading"), so it is broken. "docs/vietnam calibration.md" is named docs/vietnam_calibration.md in the repository.
- (g) **Seeds.** The statement that all results "can be regenerated with the code and fixed random seeds" should be checked table by table. Table 16 gives three values for one configuration (M9(d)), and the seeds are not stated per table.

---

## 4. Minor concerns

- **Numbering.** The appendix tables are numbered 1 (Appendix A), 2 (Appendix C) and 3–6 (Appendix D), which collide with main-text Tables 1–6. Appendix C's figure is labelled "Fig. 1", the same as the overview figure. Use separate numbering (A.1, C.1, D.1).
- **Table 15 caption** is cut off after "would be at most the level"; the α is missing.
- **Table 13** row label "—return— (%)" should read "|return| (%)", as in results/tick_reform.md.
- **Table 14** says tick size is "not tested for rings", but Table 12 has a tick ×2 ring gain.
- **Table 16** should show the member tier and the seeds, and report intervals. Its first numeric column is unsigned catch@5, which is easy to misread against the caption ("ranking by the signed statistic").
- **Table 12 and Sec 6.6.** The caption's "10 honest-only and 24 manipulated episodes" matches results/policy_matrix.md. Sec 6.6 says depth falls by 10%; the table shows 9%.
- **Table 4.** The simulated spread row ("share of quotes at one tick") is 0 in the simulator and 0.73 in the data. The 2020 cancel share sits in a column of 2022–25 moments; make the periods explicit.
- **Sec 5 ("episodes of 6000 steps (19 windows of 300 steps)").** 6000/300 = 20. Explain the 19 if a warm-up window is removed.
- **Sec 5.4.** The signed test's AUC is 0.85 (clean), 0.87 (desks) and 0.73 (all three). The desks scenario scores higher than the clean market, which the netting argument does not predict. Explain.
- **Sec 5.2 and Table 5.** "0.28 at 708" uses accounts per window (from 800 noise traders); Fig 4 uses N for accounts per window. Use one convention.
- **Sec 6.4 and Table 12.** The 3000-lot block should be related to daily volume. "Ring displacement" in Table 12 is unitless or in unstated units; the text says "about 0.5%". State the units.
- **Sec 6.5 and Sec 8.1.** The "2.4-fold" saving is computed from the fitted exponent; say so in the sentence.
- **Sec 7.2.** "Ten decisions": Appendix A lists eleven rows (HNG listed, not scored), and FIR is two decisions counted once. State the counts plainly; the AGG decision year is "inferred".
- **Sec 7.2 and Table 19.** "The nine case stocks with price history": PPT is not in Table 19, and PAS (UPCoM) and GKM (HNX) are not HOSE stocks (see M10(g)).
- **Appendix B and Sec 8.4.** "The system of the Korea Exchange (KRX) went live on 5 May 2025" is ambiguous next to "a new trading system in Vietnam in May 2025". Say which exchange and which system.
- **Sec 3.3.** The cancel share (31.76%) is from December 2020, which is set out in Appendix B, but the calibration table presents it with 2022–25 moments.
- **Notation.** T is the window length (steps) and 𝒯 the tolerance set; m is the fine multiple, but also the shift index in the proof of Proposition 1 (R_m, g^m), the mean-price operator m_L(t), and the number of members per push (m_push). Use separate symbols.
- **Proposition 6.** State the discrete convention (a+1)/(2L) or label a/(2L) as the continuous approximation.
- **Sec 4.2.** "Exact per account" holds only under the invariance premise, which the paper says is violated. Use "exact under the null of Proposition 1".
- **Sec 5.1.** "Rejection is zero at the 0.1% level because p ≥ 1/T" is correct; say that the test cannot be used at that level.
- **Sec 3.2.** "The caps of Vietnamese administrative fines, Appendix B" should say "press summaries of Decree 156/2020".
- **Figure captions.** Fig 2: state the division of the spread by 10 on the axis. Fig 6: check "24 test episodes each" against the table. Fig 9: the lower panel has negative values at L = 480, which the caption should mention. Fig 14: "cumulative market-adjusted log return" in the caption and "cumulative market-adjusted return" in the text should agree.
- **Literature (not verified against the sources).** The following are used as support for specific claims, and I did not open them: Cong et al. (2023) "above 70%"; Comerton-Forde and Putniņš (2014) "about 1%"; Saavedra et al. (2011) "less likely to lose money"; Cartea et al. (2020) "a larger fine ... until it disappears"; Vo and Doan (2023) "lower trading costs". Several entries are arXiv preprints (Fabre and Challet 2025; Jaeger et al. 2025; Liang et al. 2025; Tuccella et al. 2021), and the time-shift guarantee of Liang et al. (2025) is central to Sec 4.2. Check the wording against the sources and the final versions.
- **Typesetting.** "Teff" appears where the square root is lost in extraction; the source has √T_eff, so this is a PDF text-layer issue, not an error in the paper. The Palshikar and Apte DOI break is only typesetting.

---

## 5. Questions to the author

1. Why is the per-policy evolution-strategy run in results/vn_policy.md not reported (for example, band 7% at 49k against 101k with no band)? Can you show that the four-strategy menu is within a stated tolerance of a converged per-policy optimum? Why did the menu shrink from seven strategies (Appendix C) to four?
2. For the Appendix C single-market result (one inspected account per window: gain 13.8k, caught 20%, U(5) = −35.6k), what are E[g⁺·1_D] and E[g | D]? How is that consistent with the independence premise of Proposition 5, given the reported s.e.?
3. What is the signed test's power as a function of cross share (0 to 0.5), and does a ring with matched buy–sell pairs evade it? Why is cross share absent from the ablations in Table 5?
4. For the best-responding rings in the simulator, what are K and the number of windows in which a member is exposed? Why is the closed form in Fig 10a computed with W = 4?
5. From which exchange and asset do the 701 pump events come? Are they cryptocurrency pumps? How is the pump time defined, and what is the control group?
6. For the tick reform, what inference accounts for a single common event? Please report the 20-day spread estimate with its interval. What are the old tick sizes by price tier? Why does the sample shrink from 389 and 926 stocks to 282 and 489?
7. Why is the simulated spread about three ticks when 73% of real quotes are at one tick, and how would the tick and cost results change if the spread were matched? Which of the two simulator configurations (Table 12 against the Appendix D table) supports the frictions recommendation, and why?
8. Which episodes produce the gains in Table 4 (151k and 297k at 3000 lots) and in Tables 7–8 (110k and 164k)? Why does the fixed-strategy gain exceed the best-response median?
9. In Table 16, which member tier is used, why do three rows for one configuration differ, and what are the intervals over windows and days?
10. Could you test the transfer of the supervised model across simulator configurations (for example, train on the default preset and test on the no-trend family or the stock-level family)? That is the comparison that would justify a label-free test, and it is not reported.

---

## 6. Recommendation

**Major revision.** The statistic, the simulator and the policy-evaluation design are a potentially useful contribution for a computational economics readership, and the paper reports several of its failure modes candidly. However, the policy recommendations depend on a fixed four-strategy menu, a reversed bound (Proposition 7), a deterrence result whose independence premise the author's own numbers violate, and Vietnamese checks (tick reform, pump events, case analysis) that do not identify what they are said to identify, so the fixes need new adaptive experiments and a reframing of the claims, not editing alone.

**Confidence: medium.** The arithmetic and file-level inconsistencies above are verified against the files; the judgments about the literature and about the adequacy of the simulator for the policy questions are less certain, and a reject-and-resubmit decision would also be defensible.
