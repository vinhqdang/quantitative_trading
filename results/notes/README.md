# Notes on earlier runs

These outputs come from the default simulator (price 10,000 ticks, no daily price band) and are kept for the record. They are
superseded by `../vn_policy.md` and `../vn_cross.md` for the policy comparisons.

- `ring_adversary*.md|csv`: evolution-strategy rings against inspection. In the default simulator a ring can exploit
  unbounded price run-ups (one row reports a gain of 14 million with a negative price displacement, i.e. profit from marking
  inventory in a runaway market). The `gain retained` column divides by a poor unconstrained search result and should not be
  read. The finding that holds is the sign of the net utility under inspection: no strategy found has a positive expected net
  benefit once at least one account per window is inspected.
- `spoofer_arms_race_partial.log`: three rounds of the spoofer-versus-retrained-detector loop (fine = 0) before the run was
  stopped. The searched spoofer reaches 176-253 profit per episode against 44 for the default one, and is caught in every episode
  by the gradient-boosting detector, including after retraining.
