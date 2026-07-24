# Window-1 receipt correction and official-start gate

## Start gate — FAIL

- D = 804
- exact starts = 234
- clean causal intervals = 31
- live-by-only = 450
- contradictory = 26
- schedule-only = 63
- unresolved = 0
- positive-Window-1-provable population = 265
- required = 603
- shortfall = 338

Only exact starts and clean causal intervals can prove a positive Window-1
dual.  The remaining 539 events are
blocked by timing: 450 have only a live-by upper bound,
26 have conflicting causal bounds, and
63 have only a schedule bound.  Passing requires
338 additional event-resolved official starts or clean
two-sided causal intervals.

The complete official-provider export queried all 804 D events:
230 produced accepted exact starts.  The raw milestone
shadow contributed 50 exact candidate records; after
source precedence and deduplication, four events selected that source.
Schedule was never promoted to an exact start.

## Historical re-adjudication

- historical dual exact-five witnesses = 31
- witnesses with a receipt-proven post-start leg = 26
- permanently post-start filled legs/events = 106 / 93
- newly recovered strict Window-1 historical duals = 0
- ten-contract overfill outside exact-five = 1

No placement, cancellation, fill, price, or quantity was changed.

## Corrected historical receipt bound

The published 240-event upper bound remains preserved as prior evidence.
The corrected receipts-only upper bound is 226
of 804 (28.109453%), with strict lower bound
0; it is 377 events below
603.  This rejects the frozen historical behavior only.  It is not a market
ceiling or a full-OS-family result.

## Development candidate preflight

The chronological OS-family contracts validate: 6
families and 24 mechanically allowlisted policy IDs,
with no free numeric parameters.  AIM_V2, Pinnacle, unproven reconstructed
full depth, future information, proxy substitution, Window 2, exits,
settlement, and DCA are excluded.  Raw non-LATCHCAL shape-corpus observations
retain their independent pre-AIM derivation lineage; all AIM_V2-derived
cells, offsets, targets, and fallback tables remain excluded.

No candidate result was opened, no scoring or tuning ran, and no holdout was
opened.  The preflight stops mechanically because the start gate is below
603.  The July 24–26 baseline holdout remains preserved and unopened; no new
prospective dates have been selected.
