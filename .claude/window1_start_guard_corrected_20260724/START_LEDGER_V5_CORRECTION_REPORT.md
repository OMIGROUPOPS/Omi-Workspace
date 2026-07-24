# Corrected Window-1 start ledger and witness adjudication

Independent-review provenance: `origin/audit/window1-independent` at `9919de9462f3df4a0bd33239b7e8f648b71e20fb`, artifact `START_LEDGER_V4_CROSS_REVIEW.md`.

## Frozen source conservation

- D = 804
- start-clock rows = 687 (234 official exact + 453 five-minute-quantized late-detection proxies)
- clean causal intervals = 31
- contradictory = 14
- schedule-only = 20
- live-by-only = 52
- positive-capable after 13 named evidence censors = 705 (the pre-correction population gate was 718)

## Boundary law

- official point and clean-interval boundaries use a strict 60-second guard;
- TE proxy strict W1 requires completion at or before proxy−900 seconds;
- TE proxy strict post-start requires completion at or after proxy+600 seconds;
- the interior is censored; the 13 named conflicts are censored;
- schedule is never a start, and a retained causal live-by bound is never overwritten by the rank-3 proxy.

## Seven historical witnesses

| event | cost | 60s guard | frozen −900/+600 guard |
|---|---:|---|---|
| KXATPCHALLENGERMATCH-26JUL13YEVCAM | 98 | strict | censored |
| KXATPCHALLENGERMATCH-26JUL14ALCTAB | 100 | strict | strict |
| KXATPCHALLENGERMATCH-26JUL14SMIILA | 98 | strict | censored |
| KXATPCHALLENGERMATCH-26JUL20MARBIT | 97 | strict | censored |
| KXATPMATCH-26JUL14TOPUGO | 97 | censored | censored |
| KXATPMATCH-26JUL17COLVAC | 100 | strict | censored |
| KXWTACHALLENGERMATCH-26JUL13GRABER | 97 | censored | censored |

Recomputed result: under the explicitly requested strict 60-second witness guard, 5 are strict and 3 are under par. Under the frozen calibrated development guard, 1 are strict and 0 are under par.

The record also discloses all four prior post→strict reversals (TOPUGO, COLVAC, GRABER, YEVCAM), the permanently unavailable historical-leg shrink from 106 to 82, and the W1-leg expansion from 45 to 146. These are semantic changes, not performance.

No candidate result, placement, fill beyond the already-published historical witness ledger, delta, or holdout evidence was read to derive this law.
