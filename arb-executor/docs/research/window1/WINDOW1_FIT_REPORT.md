# Window-1 repaired-source fit and freeze

Freeze time: 2026-07-23T21:08:05.408699Z

Development period: 2026-07-12 through 2026-07-20

Immutable denominator: D=804

Selected candidate: `tminus_8h__corridor_15m__walk_law_simultaneous_hold`

This is a Window-1 entry report. It contains no Window-2, exit, settlement,
realized-exit-P&L, DCA, live-order, or production result.

## Frozen definition

Window 1 begins at the first causal top-five recorder snapshot at or after
eight hours before the contemporaneous exchange-catalog scheduled start.
Both five-contract legs post simultaneously as maker bids at their direct
best bids.

The frozen walk law rests at that price. It may move upward only after a
positive-size, exchange-trade-identified sell-YES print occurs at or through
the current order and a later causal snapshot exposes a higher maker bid.
Each move is capped by the then-current best bid and best ask minus one cent.
There are at most two moves. The order otherwise remains parked. A first-leg
fill does not re-aim the sibling; the sibling holds. Posting and movement stop
at the frozen right edge.

The right edge is the verified real start where an exact authority exists.
For a bounded start, only actions complete by the proven safe pre-start
cutoff are observed Window-1 actions. Ambiguous actions are censored. For the
71 schedule-only events, schedule plus 15 minutes exists only as the frozen
optimistic corridor; it is not an observed close and cannot enter observed
`C`, `NC`, or `IC`.

## Metric contract

The raw counts are:

- `D`: all 804 eligible games.
- `C`: both required legs fill exactly five contracts.
- `PC`: members of `C` whose two entry VWAPs sum to less than 100.
- `NC`: members of `C` whose two individual reference deltas sum below zero.
- `IC`: members of `C` where both individual reference deltas are below zero.
- `X`: censored games, reported separately and retained in `D`.

`PC`, `NC`, and `IC` overlap inside `C`; they do not partition `D`.

Combined cost is the sum of the two five-contract entry VWAPs. The separate
reference delta is entry VWAP minus the leg's final positive-size,
exchange-trade-identified true print at or before the frozen right edge.
Pair delta is the sum of the two leg deltas. Neither yardstick is an exit or
realized-P&L measure.

## Validation result

The actual game/leg lifecycle reproduction gate passed at D=804 with zero
row-level mismatches. Across 1,608 required legs, the actual ledger contains
258 exact five-contract fills, 12 fills at another quantity, 870 proven
nonfills, and 468 censored legs. This validates actual outcomes; it does not
turn same-price counterfactual prints into fills.

The earlier 703 anomalous order IDs remain order-history provenance, not 703
games. Repost IDs are collapsed at the conception/trade/leg lifecycle grain.

The repaired public source contract contains exact top-five objects for all
1,608 leg tickers and cursor-complete true-tape queries for all 1,608. It
contains 4,836,462 positive-size true prints. Of the 39 tickers without a
Spaces `trades/` object, 37 were ingestion gaps recovered by the complete
public-tape export and two were proven complete zero-trade queries. Public
prints do not require private order-receipt IDs.

The 6,432-row feature matrix covers 804 events, 1,608 tickers, and all four
pre-registered left edges. Coverage at the evaluated timestamp is:

- top-five BBO/depth: 6,338 rows;
- pre-July frozen shape cell: 5,423 rows;
- preserved top-20 snapshot context: 4,322 rows;
- bookmaker blend/divergence: 844 rows;
- sequence-valid reconstructed full depth: 0 rows.

The top-20 pass read 175 preserved files, 2,836,510 physical rows, and 51,518
relevant rows with zero parse errors. The separately receipted 14-file,
243,098-row loss remains explicit. Top-20 is limited snapshot context, not a
full causal chain. The exact 215-object WS archive contains deltas and
sequences, but no ladder-bearing snapshot, plus gaps and corrupt objects; it
therefore cannot seed reconstructed full depth.

The real-start ledger contains 29 verified exact starts, 79 bounded start
intervals, 625 one-sided live-by bounds, and 71 schedule-only censored
events. It records 32 contradictions, 76 events with at least one definitely
pre-start scorable action, and 775 boundary-censored events. First market
trade is never used alone as match start.

Mayo/Michelsen is outside D. Its official start was 2026-07-21T23:00:00Z.
Mayo posted at 23:36:19.955995Z; the sibling posted at 23:36:21.502612Z; the
known Mayo fill/adoption record was at 23:37:30.792977Z; and the sibling
cancelled at 2026-07-22T02:01:12.049553Z. All were post-start. The retired
input treated a 22:00 ET expiration/end field as a 19:00 ET match start.

## Development fit result

Raw integers precede every interpretation:

| Count | Observed | Optimistic bound |
|---|---:|---:|
| D | 804 | 804 |
| C | 4 | 252 |
| PC | 0 | 215 |
| NC | 3 | 251 |
| IC | 0 | 248 |
| X | 734 | reported separately |

Observed rates are:

- `C/D = 4/804 = 0.498%`;
- `PC/C = 0/4 = 0%`, and `PC/D = 0/804 = 0%`;
- `NC/C = 3/4 = 75%`, and `NC/D = 3/804 = 0.373%`;
- `IC/C = 0/4 = 0%`, and `IC/D = 0/804 = 0%`;
- `X/D = 734/804 = 91.294%`.

The survivor-slice `NC/C` value is not a success claim. The operating target
requires 603 negative-delta completed pairs in D. The observed shortfall is
600. Even the optimistic candidate bound is 251, a shortfall of 352. Thus the
frozen candidate family does not support the target on development evidence.
Because `X` is positive, that statement is not an empirical market ceiling
and is not a claim that every possible Window-1 policy must fail.

The four observed completed pairs had mean combined cost 100.25, median
100.00, and no strict under-par pair. Their pair reference delta had mean
-0.75 cents, median -1.00, and three negative observations. Across the eight
individual legs, mean delta was -0.375 cents, median was 0, and 3/8 (37.5%)
were negative. No completed pair had both individual legs negative.

The lower-bound failure funnel, excluding the four observed `C` rows, is 313
both-leg nonfills, 311 one-fill/one-nonfill states, 102 conditionally
filled/filled states that remain boundary-censored, 57 missing-placement
states, and 17 windows whose left edge was already at or after known live.

## Ablations

Removing true-print decision flow from the selected walk law changed
`C 4→2`, `NC 3→1`, and `X 734→735`; it also changed the small-sample
composition to `PC=1`, `IC=1`. Verified print-driven movement is the only
selected-policy family that changed raw `C` or `NC`.

Removing macrostructure, limited-depth pressure, first-leg state,
own-order attribution, or full-depth sequence state changed no selected raw
count. Own-order attribution and full-depth sequence were explicitly
inactive because the evidence could not identify them lawfully.

Holding the causal-stack mechanics fixed, the BBO-plus-prints baseline was
`C=2, PC=1, NC=2, IC=0, X=734`. Adding top-five pressure reduced `X` by
three but did not change `C`, `PC`, `NC`, or `IC`. Adding preserved top-20
pressure, then the available macro stack, produced no further raw change.
These sparse observed counts do not justify a general claim that the
families are useless.

## Freeze and holdout

The fit freeze binds the policy, boundary, denominator, reference, metrics,
source hashes, and fit summary. The one allowed holdout is registered as the
first three UTC dates after the freeze: 2026-07-24, 2026-07-25, and
2026-07-26. It may not be opened until all three are complete, no earlier
than 2026-07-27T00:00:00Z. It has not been viewed or run. The dates may not
be extended or replaced if their D is small.

Window 2 and exits remain untouched.
