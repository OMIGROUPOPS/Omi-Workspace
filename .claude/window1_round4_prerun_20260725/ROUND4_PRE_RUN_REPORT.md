# Window-1 Round-4 PRE-RUN

## Outcome

Round 4 is frozen as an implementation-only, score-free PRE-RUN on the
immutable July 12-20 D=804 development population. The audited Round-3 result
at `754415bb81a328d671cd327f216d1753802442b1` remains the control and was
not rerun.

No benchmark, scorer, ranking, tuning, ablation, holdout query, or live /
production action occurred. Every one of the 1,608 candidate-event streams
has `scored=false` and `metrics=null`.

## Bound ancestry and metric contract

- Round-3 PRE-RUN: `14e0e846e8922da98f656aef1f43d2c48da96ee7`
- Authorized Round-3 package: `6daab089d1e6c11bd75a684b4e8609e815fec8f4`
- Audited Round-3 result/control: `754415bb81a328d671cd327f216d1753802442b1`
- Independent results audit: `25735d9c9d9775a122da2a067962f45312aa62dc`

`D=804` is immutable and the primary target remains `PC>=603`. `C` requires
both legs to fill exactly five inside their lawful guarded Window 1. `PC`
requires `C` and a strictly negative combined Window-1-close delta. `S`
(combined entry cost below 100) and `IC` (both individual deltas negative)
remain separate diagnostics and never gate policy. The official/exact guard
remains 60 seconds and the proxy guard remains 900 seconds; schedule-only
evidence cannot prove a positive completion.

## Frozen candidates

1. `r4_pair_presence__park_join__causal_headroom_ladder`
2. `r4_full_drift_stack__causal_headroom_ladder`

The pair-presence candidate isolates the causal headroom ladder. The full
drift-stack candidate uses the identical actuator and adds only source-bound
chronological drift, recognition, orientation, reach/atlas, cohort, BBO /
top-five, divot, recut, queue, and own-volume-subtraction mechanics. Macro
NO_CALL never suppresses pair presence; no clock-only repricing exists.

## Real-input capability

| Candidate | eligible | censored | both legs present | decisions | headroom actions | positive prints |
|---|---:|---:|---:|---:|---:|---:|
| `r4_pair_presence__park_join__causal_headroom_ladder` | 799 | 5 | 799 | 28292 | 13003 | 2249391 |
| `r4_full_drift_stack__causal_headroom_ladder` | 799 | 5 | 799 | 32047 | 14556 | 2249391 |

The two aggregate order-decision hashes differ on
`707` real D=804 events,
and the committed difference ledger supplies event-level witnesses. These
are capability and distinctness facts, not performance results.

## Actuator law

Any positive partial fill arms the sibling without creating a budget. The
first leg to reach exactly five freezes its VWAP and contemporaneous
own-subtracted external bid `R1`, giving `b1 = VWAP - R1`. With `F=0`, each
strictly later receipt-identified sibling print may improve at most one cent
and only while `b1 + b2 + F < 0`; integer `b2_max = -b1 - F - 1`.
Maker, positive-price, lawful-band, and exact-quantity guards remain
explicit. Queue surrender from order movement is logged, but estimated queue
never gates the primary fill. Combined cost/S and individual-delta/IC never
gate the actuator.

## Primary fill law

Exact five is the simulated order quantity. Each active order accumulates
chronological receipt-identified positive-size non-self executed volume at
its limit or better, across as many prints as necessary, until its remaining
quantity reaches zero. Displayed depth, full/top-five depth, one-print size,
strict trade-through, and estimated or unknown queue clearance are not fill
gates. Queue observations remain available for placement and a separately
labeled sensitivity diagnostic, but never alter or censor the primary fill.

## Oracle separation

`CAUSAL_REFERENCE_CALIBRATION.json`, the 804-event opportunity ledger, and
`ORACLE_FALSE_NEGATIVE_CENSUS.json` are diagnostic-only. Policy code imports
none of them. The opportunity ledger carries final C/PC/S/IC as null and
marks its ex-post columns as unreachable from policy. No threshold was tuned
from calibration. The independent Round-3 control census reproduces the
supplied 278 naked singles, 92 negative filled legs, allowance counts
75/68/59/40 at >=1/>=2/>=3/>=5 cents, 4-cent median allowance, 12 later
strict price reaches, and 53 post-cutoff sibling fills.

## Unavailable

The sealed dual-divot pair policy, Pinnacle, bookmaker/FV, proved full depth,
lawful independent shape mapping, and unbound schedule revisions remain
unavailable and unproxied.

## Stop condition

`ROUND4_EXECUTION_PACKAGE_INVENTORY.json` lists the exact inputs a later,
separately authorized package must bind. This PRE-RUN contains no execution
ID or executable benchmark command and authorizes no scoring.
