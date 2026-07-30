# Table-free aims through the full live_v4 OS

**Instrument:** unchanged `live_v4.LiveV3`, executed by the full replay scheduler for all 804 game rows per mode. Twelve rows have a non-positive retained interval and are explicit no-window results; live_v4 executes on the other 792. Only `interim_entry_aim_mode` changes.

The prior 51-completion wider comparison was a lighter first-order touch harness and is not used as outcome evidence here. ATLAS is rerun below as the full-OS baseline.

**Ruling:** the old six-to-one completion headline does not survive the full OS. JOIN completes 86 games versus ATLAS's 54 (1.59x). JOIN is better on the value tests - 23 versus 2 negative-combined-delta completions (11.5x), and 10 versus 2 with both legs below their own closes (5x) - but it captures only 23/580 and 10/340 of the requested tape ceilings. JOIN is the best of these three table-free rules, not a sufficient replacement for the missing lawful aim surface.

**Fill model:** RESTING_TOUCH_FILL_V1: a resting order fills in full when a later true print or opposite BBO touches or passes its limit; no depth, capacity, or five-contract proof gate.

## Outcomes

| rule | completed / 804 | negative combined close delta / 580 ceiling | both legs below own close / 340 ceiling | filled legs with lawful low | median fill-low | p90 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| JOIN | 86 | 23 / 580 | 10 / 340 | 460 | 1.0 | 4.0 | 25.0 |
| TOUCH_MINUS_1 | 60 | 4 / 580 | 2 / 340 | 162 | 0.0 | 3.0 | 15.0 |
| ONE_SPREAD_BELOW_MID | 60 | 4 / 580 | 2 / 340 | 156 | 0.0 | 3.0 | 9.0 |
| ATLAS | 54 | 2 / 580 | 2 / 340 | 108 | 1.0 | 6.0 | 29.0 |

A fill-low gap of 0c means the OS filled at that leg's own independent-touch floor. Positive values mean it paid above the best price the full lawful tape proved fillable. Unfilled legs have no achieved fill-minus-low gap and remain null in the JSON.

Evaluator coverage is 693 games with a positive lawful window. The other 111 are unmeasurable here: 99 have no resolved evaluator boundary and 12 have no positive retained replay interval. The latter are explicit no-window rows, not runtime input failures.

## Ceiling definitions

- Requested legacy comparison - 580: games where the retained true-print receipt oracle proves a negative combined delta to the two authoritative Window-1 closes.
- Requested legacy comparison - 340: games where that true-print receipt oracle proves both legs individually reachable strictly below their own Window-1 close.
- 622 games have both an authoritative two-leg close and a two-leg true-print receipt floor. No value is fabricated for the remainder.
- Fill-model-matched ceiling (true print **or opposite BBO**, no depth gate): 598 negative combined; 372 both legs below own close; 622 defined two-leg comparisons.

## The 8,072 ATLAS alarms

All 8072 are repeated `FIT_CONSULT_KEY_MISMATCH` invocations from ATLAS, spanning 785 games. They are not 8,072 independent market events.
- 31 unique legs in 27 games actually crossed an ATLAS broad page. Those games account for 142 alarm invocations.
- The other 7930 invocations are repeated same-page or otherwise non-page-crossing fit-key mismatches. They are still contract wrongness, but not 7,930 distinct page crossings.
- Separate surfaces: COHORT emitted 8,072 `FIT_CONTRACT_MISSING` invocations; contention emitted 942 `VERDICT_IGNORED` invocations; fitted surfaces emitted 15 thin-row alarms.

## Retention

The VPS WebSocket depth recorder remained running throughout this study. This replay did not restart or alter it.
