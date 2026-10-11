# Paper audit: factual consistency of main_sn.tex and sections/*.tex

Snapshot note: main_sn.tex, sections/policy.tex, sections/discussion.tex and all tables/*.tex were rewritten between 02:13 and 02:14 on 2026-10-11 while this audit was running. Those files were re-read afterwards; line numbers refer to the versions on disk at about 02:16. Results files used: theory_checks.md/csv, power_law_fit.md, ring_robust.md, ring_ablation.md, ring_robust_scores_*.csv.gz (AUC recomputed), vn_ensemble*.md/csv, block_static.md/csv, block_size_sensitivity.md, policy.md, policy_matrix.md/csv, vn_cross.md, block_rule.md, tick_reform.md, tick_sim.md, real_accounts.md, real_accounts_planted2.csv, case_validation*.md, case_stats.md/csv, case_eventstudy_mean.csv, pump_events.md, calib_markets.csv, calib_sim_*.csv, calib_real_acf.csv, notes/account_data_search.md, data/cases.csv, docs/vietnam_calibration.md.

Verified with no discrepancy beyond last-digit rounding (not listed below): validity rejection rates, bursty-flow rates, budget table, power-law fit (7.3, 53, R2 0.993, 0.964 correlation, 0.128 over-prediction), s0/a/MAE/held-out errors/gamma 0.32, catch@5 0.91/0.28, all robustness/ablation/groups numbers, AUC and AP values (recomputed from score files), ensemble and stock-family tables, capacity table (recomputed: 2.99/1.25, 36.5 ... 2.0), detection probs 8%/20%, block-rule table and block-size sensitivity, matrix numbers, appendix order-level table, tick DiD and simulator percentages, real-account calibration and planted-ring tables, case-study superiority/top-B/window tables, event-study means, pump profile and alarm rates, re-measured calibration counts (5/6, 4/6, 5/6, 5/6, all).

## 1. Numbers

Differ or not matched:

- sections/method.tex:116 "a one-day reference (L=240) pays a ring that pushes for a~60 steps a quarter of what the last price pays": Eq. (blocklaw) gives a/(2L)=60/480=0.125 (an eighth); the law column of block_static.md at L=240 is 0.161 for a=72-83. Source: block_static.md/csv, method.tex:107.
- sections/real_cases.tex:5 "against 15% for random stocks": case_validation.md gives 0.141 (14.1%); tables/cases.tex prints 14%.
- sections/policy.tex:41 "episode-to-episode standard errors of about a third of the mean in gain": median gain_se/|gain| over markets is 0.47-0.55 with no rule, 1.2-2.5 for block rules, 1.4-3.9 for inspection (vn_ensemble.csv, vn_ensemble_stock.csv).
- sections/method.tex:98 "with N=2000 accounts and a ring of three the saving is less than a factor of two": tables/capacity.tex prints 2.0 (m=5) and 2.1 (m=10); recomputed 1.99 and 2.14. Borderline; the text of policy.tex:60 and discussion.tex:9 says 2.0.
- sections/setting.tex:73,75 (Table calib), simulator column "0.321 cancel share, 21 bp, 1.14% daily volatility": not found in any results file; calib_sim_moments.csv (first accepted index-level market, 16 episodes) gives 0.318, 19.8 bp, 1.05%. Only retail 0.72 (0.717) and spread 3 (3.08) match.
- sections/setting.tex:79 and :40 VN30 lag-1 autocorrelation "-0.03": no results file holds it (calib_real_acf.csv has only the HOSE-stock mean, 0.035; real_data_stats.md has absolute-return autocorrelation only). Simulated 0.49/0.60 match (0.488/0.604 from calib_sim_daily.csv).
- sections/method.tex:63 and sections/real.tex:9 "N_eff ~ 10^6": no results file, log or script contains this number. The "about 470 accounts" is the median active accounts per window (468; real_accounts.log), the mean is 508.
- sections/real.tex:7 "61,000 orders on average" per window: not in any results file (577,918 orders in 23.6 minutes is in account_data_search.md). The 5.9% and 19.5% shares are consistent only with a mean of about 61,500.
- sections/real.tex:7 "nine windows with 351 to 715 active accounts" matches real_accounts.log, but Table realcal and the 28.5% use only accounts with at least 3 orders (2,170 account-windows, about 241 per window); the text does not say that the 468/470 refers to all active accounts.
- main_sn.tex:30 (abstract) "exchangeability condition fails for a quarter of the active accounts": real_accounts.md gives 28.5% signed, 33.4% unsigned at the 1% level; the text of real.tex:9,17 says "more than a quarter". Loose, not wrong.
- sections/policy.tex:27 "in the remaining market with one inspected account the ring still nets up to 41k": with one inspected account only 3 of 6 markets are deterred, so three markets remain; 41k (40.8k) is the maximum over those three. With three inspected accounts one market remains (6.9k, matches).
- sections/policy.tex:27 "where each window has fewer accounts to cover" (index family): the accepted markets have n_noise 369-627 (index) and 368-643 (stock) in vn_ensemble.md and vn_ensemble_stock.md; no per-window account count is reported to support it.
- sections/policy.tex:9 "excursions are of one to two standard errors": stock market 49 volatility is 2.87% against an upper bound of 2.8%, 0.3 s.e. (calib_markets.csv); cancel-share excursions (0.262, 0.265 against 0.27) have no s.e. reported.
- sections/policy.tex:76 "wash volume is 3.3% of volume under every rule": policy_matrix.md gives 3.1% for tick x2 and cancel fee 2, 3.2% for min rest 15 and cancel fee 0.5.
- sections/policy.tex:76 "pump impact is lower under cancel fees (0.31 against 0.47, within about 1.3 standard errors)": 1.3 holds for fee 0.5; for fee 2 the difference is 1.6 s.e. (policy_matrix.csv).
- sections/policy.tex:41 "(adaptive) changes the median only slightly": block_static.md shows adaptive minus static of +0.095 (index, L=120), +0.12 (index, L=480), -0.11 (stock, L=120), -0.125 (stock, L=480).
- sections/policy.tex:41 "69% ... at stock level" (60 steps, total gain static): block_static.md 0.685; tables/block.tex prints 0.68. Round-off, but text and table differ.
- sections/policy.tex:60 and discussion.tex:9 "1.2" for 10x fine at N=600: table value 1.25 (rounds to 1.2 or 1.3; round-off).
- sections/policy.tex:76 "cuts depth by 10%": policy_matrix.md -9.5% (table prints -9%); round-off.
- main_sn.tex:74 (Appendix B) "877 million records per day": account_data_search.md says "about 880 million records per day" (SCHEMA.md); no source for 877 found.
- sections/real_cases.tex:37 "intervals excluding zero" for buy imbalance: first bin is 0.03 [0.00, 0.07] (pump_events.md), the interval touches zero.
- sections/detect.tex:3 "default simulator (about 120 accounts in a window)": ring_ablation.md default row has 100.25 accounts per window (its own header also says "about 120"); ring_robust.md says 120-170.
- sections/setting.tex:42, real_cases.tex:27, discussion.tex:11 case-stock band statistics ("median five days", "12 in a row") are computed over 9 stocks, not 10 (PPT is missing from case_stats.csv and tables/casestats.tex, caption says "Case stocks"), and the 12-day run is HCI whose exchange is "unknown" with an assumed 7% band (case_stats.py applies b=0.07 to unknown exchanges, uses log returns >= b-0.005).
- sections/setting.tex:42 and sections/real_cases.tex:27 "median daily volatility 1.75% in the year before": median of the same 9 stocks (PSH, exchange unknown).
- sections/intro.tex:3 "ten recent decisions ... (Appendix~\ref{app:cases}) ... between 5 and 164 accounts (median 24.5)": 5-164 and 24.5 hold for the 10 scored cases; the appendix table (tables/caselist.tex) lists 11 rows (adds HNG, 42 accounts, 2015-16, which is outside the panel and not scored); with 11 the median is 26.
- main_sn.tex:59,63 Appendix A title "Documented cases used in Section real": HNG is listed but is not used (data/cases.csv note: "drops out by coverage").
- sections/setting.tex:51 Table data "VN30, VN-Index, VN100 bars from 2012": real_data_stats.md has VN-Index from 2000-07-28, VN30 from 2012-09-10, VN100 from 2014-01-27.

## 2. Citations (related.tex unless noted; against results/notes/reference_notes.md)

- related.tex:13 \citep{becker1968}: block is ABSTRACT NOT FOUND; "deterrence depends on the probability of detection and the size of the sanction" is supported only by polinsky2000, not by Becker's title ("Crime and Punishment: An Economic Approach").
- related.tex:13 \citep{avenhaus2002}: ABSTRACT NOT FOUND; title "Inspection games" does not support "formalise limited inspection capacity".
- related.tex:13 \citep{mcmahan2003}: ABSTRACT NOT FOUND; title "Planning in the presence of cost functions controlled by an adversary" does not support "double-oracle methods compute equilibria of games with an adversary".
- related.tex:13 \citep{lanctot2017}: abstract is multiagent RL (policy-space response oracles, joint-policy correlation) and names double oracle only as a special case; it does not say double oracle computes equilibria of games with an adversary. Same sentence cited again in discussion.tex:63.
- related.tex:13 \citep{nguyen2017} "For Vietnam ... insider trading around stock splits": ABSTRACT NOT FOUND; title says "an emerging market" and "stock splits", not Vietnam.
- related.tex:13 \citep{khwaja2005} "price manipulation by intermediaries in an emerging market": ABSTRACT NOT FOUND; only the title ("Unchecked intermediaries: price manipulation in an emerging stock market") supports it, nothing beyond.
- related.tex:7 \citet{saavedra2011} "show that synchrony is a common trait of honest traders ... so synchrony alone does not signal collusion": abstract says higher synchronous trading goes with lower probability of losing money and with messaging patterns; "honest", "common trait" and the collusion inference are not in the abstract.
- related.tex:5 \citep{cao2016} "loops of matched orders": abstract (notes) says suspiciously matched orders and collusions found by dynamic programming on a directed graph; "loops" is not stated.
- related.tex:5 "These methods need labels (announcements, cases) or counterparty-level records": contradicted for cong2023 (exchange-level statistical regularities, no labels, no counterparties) and kamps2018 (anomaly detection on trade data, no labels stated); also Table positioning row "wash-trading detection: counterparty-level trades".
- related.tex:5 \citep{fabre2025} "three-day sample": abstract gives 2024-12-04 to 2024-12-07; "three-day" is not stated.
- related.tex:7 \citet{jaeger2025} "2.9 million filings": abstract says 2.9 million trades reported to the SEC.
- related.tex:9 \citet{platkiewicz2017} "prove that interval jitter gives an exact test": abstract states the result for "processes with no temporal structure" and mentions explicit examples and numerics; the condition and the word "prove" are not in the notes.
- related.tex:11 \citet{zhang2016} "when upper limits bind": abstract says price discovery is delayed when upper limits are imposed (not "bind"); \citet{zhao2020} "especially for small caps, as it grows" merges two separate findings (small caps lowest quality; quality weakens as tick grows).
- related.tex:9 grun2009 "main lesson of our real-data test: common drivers make the null false for most active accounts": real_accounts.md gives 28.5% (signed) of accounts with >=3 orders, 6.6% for 3-9 orders; "most" holds only for the >=100-order tier (51.8%).
- policy.tex:91 (tick section) \citep[according to][]{vo2023} for the new tick values (10, 50, 100 VND by price band) and for "HNX and UPCoM stocks were not affected": vo2023 abstract (notes) states only the change of 12 September 2016 and lower trading cost; the tick tiers come from docs/vietnam_calibration.md (broker summary), the control-group claim has no source in the notes.
- intro.tex:3 "Spoofing and layering, the focus of most of the detection literature \citep{tuccella2021,fabre2025}": the two abstracts do not support "most"; related.tex:5 itself cites six pump-and-dump, three wash-trading and three collusion papers against two on spoofing.
- main_sn.tex:74 and real.tex:7 \citet{albers2026}: no block in reference_notes.md (record details are only in account_data_search.md).
- Key/year mismatches in notes: hu2022 -> 2023, vyetrenko2019 -> 2020, nguyen2023 -> 2024 (printed year follows bib; no textual claim affected).

## 3. Internal consistency

- main_sn.tex:30 (abstract), intro.tex:5, discussion.tex:67 (Conclusion): "a ring that re-optimises against each rule across simulated markets" versus policy.tex:7 (ring picks among the same four fixed strategies, not re-optimised per market) and discussion.tex:59 ("strategies were not re-optimised in each market").
- main_sn.tex:30 and discussion.tex:67: "minimum resting times and cancel fees do not deter" is placed under the best-responding ring, but policy.tex:76 and the matrix caption evaluate them with fixed, non-adaptive spoofer/pump/wash/ring in one market (vn_cross-based ring gain 30-36k vs 34k); no family-level or best-response result for these rules exists.
- sections/policy.tex:35-37 contains only "\textit{(pending)}" under \subsection{Markets without trending}\label{sec:acf}; setting.tex:40 and discussion.tex:59 say a family with calibrated-away trending is "analysed in Section~\ref{sec:acf}". Only vn_ensemble_acf.log exists in results; no results .md/.csv, table or figure for it.
- sections/intro.tex:7 contribution (v) puts "a natural experiment on the tick size" under Section~\ref{sec:real}; the tick experiment is in policy.tex (sec:tick, Experiments II); Section real contains accounts, cases and pumps only.
- sections/method.tex:116 calls the block reference "an exponentially-flat memory"; Proposition block (method.tex:105) and discussion.tex:7 say increments are discounted linearly with age.
- main_sn.tex:154 Data availability "No account-level or other non-public data were used" contradicts real.tex (account-identified Hyperliquid orders and fills, tab:data last two rows). Also main_sn.tex:26 uses \equalcont for the ORCID.
- sections/discussion.tex:45 "retail investors, who cross the spread, pay most" and "the block-price rule falls on ... institutions and insiders, not on retail": no result supports either; tables/matrix.tex and policy.md show retail (noise) cost falling under larger ticks and fees (-16%, -5%, -12%), and the table caption itself says noise traders mostly post passive orders. No simulated agent is an "insider".
- sections/discussion.tex:55 "Section real-accounts suggests that a larger share of automated accounts weakens the coincidence test": real.tex does not vary the automated share; it shows high flag rates and N_eff on one crypto venue.
- sections/discussion.tex:13 "lowered ... the estimated spread by about 8%, in the direction the simulator predicts": the spread DiD interval is -0.13 to 0.01 (includes zero) and placebo dates range -0.06 to +0.09 (policy.tex:93), so only the zero-return result separates from placebos; the heading "Do not undo the 2016 tick reform" rests on that plus an unrelated intraday paper.
- sections/discussion.tex:7 and the Table options row ("removes 87-98% of block value; total gain falls to 28-44%") are for the assumed 3000-lot block; block_size_sensitivity.md shows the one-day retained gain at 300 lots is 83-87% (policy.tex:43 and the discussion now say so, but main_sn.tex:30 and discussion.tex:67 still state "loses most of the block value ... remove most of the ring's expected benefit" without the qualifier).
- sections/discussion.tex:9 and policy.tex:60 headline capacity numbers (3 accounts per window at N=600) depend on s0 fitted in a simulator with about 100 accounts, extrapolated by N^(-1/2); the fitted exponent is 0.32 (detect.tex:25) and real flow has N_eff far above N (real.tex:9). The text states both facts but the Table options row and the abstract treat the 2.4 factor as a result.
- sections/method.tex:38 "a Vietnamese stock has hundreds of active accounts in a window of 300 minutes" and the N=600 baseline: no Vietnamese account data are used (limitations, discussion.tex:59).
- sections/detect.tex:3 claims Section detect checks "every statement of Section method"; the block-price law and deterrence law are checked in policy.tex, and Proposition 6 (best response) is not checked by simulation.
- sections/intro.tex:7 (ii) "show that it explains the dependence on the number of accounts in the agent-based market" versus detect.tex:25 (free exponent 0.32, "we cannot say"; held-out error for N sweep 0.085 vs 0.043 in-sample).
- sections/intro.tex:3 "Spoofing and layering ... do not appear among these cases": tables/caselist.tex lists GKM and HNG as "fake supply and demand" (the legal wording that can include spoofing-like orders); the press-report types cannot rule it out.
- sections/policy.tex:27 "deterrence is not worse" at stock level versus Table: one inspected account deters 2/6 (index) vs 3/6 (stock), three deter 5/6 in both; consistent, but "yet" and the attribution "we have not separated the two effects" are the only support.

## 4. LaTeX

- sections/policy.tex:37 placeholder text "\textit{(pending)}" in a numbered subsection (compiles).
- main_sn.tex:26 \equalcont{ORCID: ...} misuses the macro intended for equal-contribution notes (renders an "equal contribution" style footnote).
- Compile of 02:14 (main_sn.log): no undefined references or citations; only "h float specifier changed to ht" (appendix tables), hyperref bookmark-level warnings and rsfs font-size substitutions. build.log (2026-10-10 14:05) is stale: it reports 13 pages, main.pdf and undefined references from a first pass.

## Counts

- Numbers: 27 findings (about 15 substantive differences or unmatched values, about 12 round-off or loose-wording items).
- Citations: 18 findings (6 where the block is ABSTRACT NOT FOUND or title-only, 12 statements that go beyond or contradict the notes, or a cited key with no block).
- Internal consistency: 16 findings.
- LaTeX: 3 findings (1 placeholder, 1 macro misuse, 1 stale build log; the 02:14 compile has no undefined references).
