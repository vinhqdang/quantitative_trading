# Submission log

## Computational Economics (Springer): submitted 2026-10-12

| item | value |
|---|---|
| journal | Computational Economics (Springer) |
| title | Screening for Coordinated Manipulation and Evaluating Exchange Rules in a Calibrated Market Simulator |
| author | Quang-Vinh Dang (sole author), British University Vietnam |
| submitted version | repository commit `092eea6` on `main` (tag `submitted-compecon-2026-10-12`) |
| files uploaded | `submission/manuscript_latex.zip` (LaTeX source only), `submission/cover_letter.pdf`; title, abstract, keywords and JEL codes in `submission/title_abstract.txt` |
| checksums (md5) | zip `9e58f9379156794e3e23f971908d6611`, cover letter `a98bff9f47821c2ac5826e46ea3c7014` |
| format | Springer Nature `sn-jnl` class (`sn-basic` reference style), 59 pages, abstract 248 words |
| declarations | funding: none; competing interests: none; author contributions: sole author (also in the manuscript and in the cover letter) |
| manuscript number / status | to be filled in from the submission system |

## What the submitted version claims (for answering reviewers)

- Test: label-free coincidence test, exact per-account circular-shift null (Prop. 1); ranking cannot carry a family-wise guarantee (Prop. 2, p >= 1/T); block-jitter surrogates give exact p-values of any resolution under local exchangeability (Prop. 8, Cor. 9), at the price of a ring two to three times larger than top-five ranking; joint-shift max-T (Westfall-Young) is not valid (family-wise error 0.2 to 1.0 with a ring).
- Power law (Prop. 3): shift of the statistic ~ N^(-1/2); deterrence condition linking capacity to the fine (Prop. 5); block reference price law (Prop. 6); best response on a finite menu is a lower bound (Prop. 7); maximin allocation of capacity over stocks (Prop. 10; about a third of the capacity of equal shares in a synthetic model).
- Policy results (simulated markets matching a HOSE stock, three families): price band no effect; trailing-mean block price removes most of the block value (gain falls in all 15 markets with a positive baseline, median share kept 0.12); inspection deters only with enough capacity; resting times and cancel fees do not help.
- Real data: order flow from a public derivatives venue violates exchangeability (about a quarter of accounts flagged; block jitter does not repair it); HOSE tick reform of 2016 (zero-return share down 7 points, none of 57 placebo dates as extreme; spread effect not distinguishable from noise); 8 of 10 documented cases reach the daily top ten on at least one day (pooled test p < 0.001).

## Known weaknesses a reviewer is likely to raise (from the internal review round and the later experiments)

1. No real account-level data from a stock exchange; the detector's failure profile on real flow is documented but not repaired.
2. The simulator does not match the spread or the absence of serial correlation in daily returns (a third family without trending addresses the second); the word "calibrated" refers to moments only.
3. Ring strategy set: a menu of four strategies plus 24 random ones; not shown to be near the optimum; deterrence results are upper bounds for the regulator.
4. Few markets per family (6, 6, 4); intervals over markets are wide.
5. The allocation rule is tested only in a synthetic Gaussian model; in the agent-based markets every rule deters at the smallest capacity.
6. Block-jitter power is very low against the default ring in the calibrated markets; honest family-wise error is inflated at block length 100.
7. Cases and rules come from press reports and broker summaries; decisions were not opened.

## Still open at submission

- Missing page ranges in two references (McMahan 2003; Lanctot 2017) and one author's first name (Leal 2019).
- Repository visibility and a persistent identifier (the manuscript points to the GitHub repository).

## After submission

- Record the manuscript number and the dates of each status change in the table above.
- On a revision request: rebuild with `paper/make_submission.sh`, keep the response letter in `submission/`, tag the revised commit.
