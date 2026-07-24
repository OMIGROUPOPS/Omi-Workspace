# Start-ledger V4 independent-audit incorporation record

Authoritative independent source:
`origin/audit/window1-independent` at
`9919de9462f3df4a0bd33239b7e8f648b71e20fb`,
`arb-executor/docs/research/window1/independent-audit/START_LEDGER_V4_CROSS_REVIEW.md`.
The audit branch was not merged. This record identifies the proved
corrections incorporated into the Codex research lane.

The conserved population is unchanged: 687 start-clock rows + 31 clean
causal intervals + 14 contradictory + 20 schedule-only + 52 live-by-only =
804. The 687 start-clock rows now decompose into 234 official exact starts
and 453 TennisExplorer five-minute-quantized late-detection proxies. No proxy
is exact.

The source-blind calibration has been mechanically rerun. Of the 234 frozen
official starts, 222 have a unique comparable TennisExplorer clock. The
proxy-minus-official median is +300 seconds. The absolute 15-minute central
band contains 207/222 (93.24%); 15/222 (6.76%) form the longer tail. The
signed extrema of that central set produce the frozen asymmetric interval
`[proxy−900s, proxy+600s]`. Positive completion requires the lower edge,
post-start requires the upper edge, and the interior is censored.

Thirteen audit-named proxy rows are censored from positive scoring:
KYMTSI, MAKSEY, NAPBAR, SHESTR, DELFUE, MOLOFN, BURJAC, BURUGO, MATMOR,
COLCER, CORSAC, TRUDAV, and ALTDAR. This named evidence correction changes
the scoring-positive ceiling from 718 to 705 without changing D or the
source-evidence conservation.

The corrected one-sided conflict law retains every causal `live_by` bound
and never permits the rank-3 proxy to overwrite it. Only a strictly
higher-precedence `not_live_through` observation can block a proxy interval.
Ties never promote a proxy to exact. The five formerly mislabeled equal-rank
demotions are consequently no longer called exact controls.

The seven published historical witnesses were recomputed from their
completion exchange clocks. With a stated symmetric 60-second witness guard,
five are strict and three of those are under par. With the frozen calibrated
development guard, one is strict and none is under par. Every row in the
guarded witness artifact carries its guard and leg-level verdict.

The record discloses four prior post-to-strict reversals—TOPUGO, COLVAC,
GRABER, and YEVCAM—the historical permanently-unavailable shrink from 106
legs to 82, and the historical Window-1-leg expansion from 45 to 146.

All of these corrections were completed before candidate scoring. Raw
provider pages remain outside Git; only sanitized ledgers, receipts, hashes,
tests, and reports are committed.
