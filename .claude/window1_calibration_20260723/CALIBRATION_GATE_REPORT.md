# Window-1 execution-calibration gate

Status: **PASS**. This is a calibration
result, not candidate scoring and not an OS-performance verdict.

## Real-start ledger

All 804 D events and 1,608 legs are retained. Precision classes are:

- exact official/milestone: 29
- causal start interval: 79
- causal live-by bound: 625
- schedule-only bound: 71

Schedule-only starts promoted to exact: 0.
Archived `market_lifecycle_v2` rows:
1421960; valid live-transition events:
0. Missing start
precision censors the boundary; it does not remove an event from D.

## Causal market receipts

The canonical public tape has
4,836,462 exchange-identified,
positive-size true prints across
1606 tickers;
queries are cursor-complete for all 1,608 and the other
2
tickers are proven zero-trade. Recovered WS
trade receipt rows: 3,322,756;
unique identities:
3,322,756 across
1601 tickers;
7 tickers
have no recovered WS trade. Exact
WS/public identity matches: 3,322,756; reconciliation
mismatches: 0. Recorder read errors remain named
coverage censoring. Full depth is unavailable and no full-depth feature is
enabled.

## Exact historical execution replay

The shared kernel consumed 3,318
accepted placement receipts plus 14 failed
attempts, validated 3,332 prices,
quantities, and local timestamps, consumed
3,574 cancellation receipts and
338 official fill receipts. The 42
unattributed private-fill lineages remain censored.

Across 1,608 legs the replay produced exactly:

- 258 exact-five filled legs
- 12 other-quantity filled legs
- 870 exact nonfills
- 468 legitimately censored legs

Completed dual exact-five events:
31; of those, combined actual
entry cost under par: 27.
Execution mismatches: 0. Schedule fields consumed
by this replay: false.

## OS research adapter

The adapter inventories 20 chronological
components. Status counts:
{"available": 5, "excluded": 1, "partially_available": 13, "unavailable": 1}. AIM_V2 is excluded.
Pinnacle is unavailable; bookmaker/FV is partial; top-five pressure is
partial; full depth is unavailable; own-order contribution is partial.
Every missing input censors its named feature. No narrow proxy is substituted.

## Stop law

No C, PC, NC, IC, X, dynamic-floor gap, dip/catch performance, candidate,
ablation, tuning, or holdout result was computed. No production surface was
read as a mutation target or changed.

If this gate is accepted, the smallest lawful scoring run is one deterministic,
predeclared corrected-instrument replay over all 804 development events, with
one fixed adapter version and one fixed execution kernel. It must report C,
PC, NC, IC, X, dynamic-floor gap, and per-leg dip/catch separately; it may not
tune, ablate, inspect a holdout, or shrink D. Only after that instrument passes
validation may a new prospective holdout be frozen.
