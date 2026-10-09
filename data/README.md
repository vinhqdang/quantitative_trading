# Cases

`cases.csv`: manipulation periods of listed stocks from enforcement decisions of the State Securities Commission and from
criminal cases, used as weak labels for `experiments/run_case_validation.py`.

Collected from press reports that quote the decisions or court findings; the decision documents on ssc.gov.vn were not opened,
so dates may differ slightly from the originals and some decision numbers are unverified. `include = yes` marks the cases used in the
analysis: an exact start and end day from a major source. The Louis Holdings case concerns BII and TGG (not TGM). Periods are
the dates of the manipulation as stated, not of the decision.

Eight further decisions name a ticker without a period (TTB, C69, MPT, IBC, DL1, DPS, DTL, TAR) and are not used.
