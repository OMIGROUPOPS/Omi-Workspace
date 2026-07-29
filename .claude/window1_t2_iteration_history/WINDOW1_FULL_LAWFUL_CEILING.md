# Full-lawful Window-1 ceiling

**Evaluator boundary fixed:** the OS policy edge remains `min(scheduled horizon, guarded cutoff)`, while tape evaluation continues to the positive guarded actual-start cutoff.

Primary fill model: **resting limit order; first true-price touch fills; no depth proof; no five-contract capacity gate.**

## Corrected ladder

| ceiling | ≤93 | ≤95 | ≤97 | <100 | any |
|---|---:|---:|---:|---:|---:|
| independent two-leg touch | 32 | 56 | 133 | 451 | 680 |
| second leg only after first touch | 32 | 56 | 133 | 451 | 680 |

All tier comparisons include the published maker fee for five contracts on each leg.

## Boundary census

- Positive guarded boundary: **705**
- Undefined boundary: **99**
- Positive but zero-length selected window: **12**
- Strictly measurable nonzero Window 1: **693**

## Start evidence

| source class | all | positive | earlier / equal / later | min | median | p90 | max |
|---|---:|---:|---:|---:|---:|---:|---:|
| contradictory | 14 | 0 | 0 / 0 / 0 | n/a | n/a | n/a | n/a |
| inferred_quantized_proxy | 453 | 440 | 326 / 2 / 112 | -200.0 | -125.0 | 1315.0 | 3175.0 |
| live_by_only | 52 | 0 | 0 / 0 / 0 | n/a | n/a | n/a | n/a |
| observed_bounded_interval | 31 | 31 | 30 / 0 / 1 | -645.7 | -465.5 | -160.5 | 959.8 |
| observed_official_exact | 234 | 234 | 162 / 0 / 72 | -281.0 | -91.0 | 1349.0 | 3204.0 |
| schedule_only | 20 | 0 | 0 / 0 / 0 | n/a | n/a | n/a | n/a |

Cutoff movements are minutes relative to the scheduled start. Negative means the evaluator cutoff is earlier; positive means later.

The copied `observed_starts.db` contains **130** rows, including **57** from July 14-20. It stores only a three-letter leg code, not a full event id, so it cannot be directly joined to the 804.

## Why 111 games are unmeasurable

- 52: `one_sided_live_by_bound_without_not_live_through_bound`
- 20: `schedule_only_no_independent_start_evidence`
- 14: `contradictory_start_evidence`
- 13: `named_start_evidence_conflict`
- 12: `guarded_cutoff_at_or_before_contemporaneous_T_minus_8_left`

None of the 111 can be assigned a strict actual-start boundary from the existing tape. The 12 zero-length rows were also checked against the full normalized print tape; zero had both legs inside an actual-start-anchored alternative Window 1.

Per-game reasons for all **111** unmeasurable rows are in the companion JSON.
