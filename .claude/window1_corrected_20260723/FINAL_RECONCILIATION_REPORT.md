# Final reconciliation — corrected Window-1 development replay

## Raw event counts first

- D = 804
- strict dual exact-five Window-1 completions = 0
- strict dual exact-five Window-1 completions with negative combined Window-1-close delta = 0
- combined entry cost under par = 0
- both individual-leg deltas negative = 0
- one-leg-only negative delta = 0
- dynamic-floor gap evaluated events = 0
- dynamic-floor gap at or below zero = 0
- nonfill events = 544
- non-Window-1 fill events = 66
- other-quantity fill events = 12
- timing-censored events = 728
- feature-censored events = 804

## Exact leg conservation and per-leg measures

- exact-five filled legs = 258
- other-quantity filled legs = 12
- exact nonfill legs = 870
- lifecycle-censored legs = 468
- proven Window-1 exact-five legs = 13
- proven non-Window-1 filled legs = 75
- 10-contract overfill legs retained as other quantity = 1
- dip/catch evaluated legs = 10
- at or below fitted target = 5
- within four cents of fitted target = 9

## Rates against D = 804

- strict completion rate = 0.000000%
- primary rate = 0.000000%
- combined-cost-under-par rate = 0.000000%
- both-individual-negative rate = 0.000000%
- one-leg-only-negative rate = 0.000000%
- nonfill-event rate = 67.661692%
- non-Window-1-fill-event rate = 8.208955%
- other-quantity-fill-event rate = 1.492537%
- timing-censored-event rate = 90.547264%
- feature-censored-event rate = 100.000000%

## Lawful primary bounds

- strict lower bound = 0 of 804 (0.000000%)
- optimistic upper bound = 240 of 804 (29.850746%)
- unresolved events assumed successful in the upper bound = 240
- distance to the 603-event target at the lower bound = 603
- distance to the 603-event target at the optimistic bound = 363
- lawful-bounds verdict = target_proven_failed

## Start precision

- exact starts = 29
- clean causal intervals capable of proving a positive = 47
- contradictory intervals unable to prove a positive = 32
- live-by events usable only for nonfill or causally proven-not-Window-1 findings = 625
- fully timing-censored events = 71
- positive-Window-1-provable population = 76
- remaining timing-censored population = 728

## Execution and publication conservation

- accepted placements = 3318
- missing-placement witnesses = 42
- failed placement attempts = 14
- cancellation receipts = 3574
- causal nonplacements = 308
- execution mismatches = 0
- duplicate or zero-size fill promotions = 0

The first publication ledger omitted the 14 failed-attempt rows because its
sanitizer used a client-order fallback instead of the kernel's attempt
lineage. `POLICY_DECISION_SUPPLEMENT.jsonl` and
`POLICY_DECISION_LEDGER_COMPLETE.jsonl` repair publication only. The frozen
replay outputs and every metric above remain byte-for-byte unchanged.

## Component coverage and remaining censorship

The chronological adapter retains the calibration inventory: five available,
thirteen partially available, one unavailable, and one excluded component,
plus the available historical-execution binding. All 804 events are
feature-censored because AIM_V2's LATCHCAL prior is excluded, full-depth
ancestry is unavailable, Pinnacle is unavailable, and fixed-snapshot
BBO/top-five features are not exchange-placement-clock aligned. The public
tape remains 4,836,462 positive-size exchange-identified prints. Top-five
coverage remains 6,338 of 6,432 feature rows; bookmaker coverage remains 844
of 6,432; Pinnacle and proven full depth remain zero.

## Preserved baseline comparison

The seven-hour narrow proxy baseline remains unchanged at C = 4 and X = 734;
it is not an OS-performance verdict. The exact historical execution gate's
31 dual exact-five events and 27 combined-cost-under-par events also remain
unchanged, with the required qualifier that all 31 sit on live-by bounds and
none has proven Window-1 timing. This corrected replay promotes neither
population into the strict numerator.

AIM_V2's pinned table first entered Git in `c8c91b33` as the named
operational LATCHCAL artifact. No earlier independent authorization exists,
so its resting-aim/shape-offset feature is censored rather than relabeled.

No candidate search, tuning, threshold selection, parameter sweep, or
ablation ran. No holdout, production, live_v4, configuration, order,
position, Window 2, exit, settlement, or DCA state was opened or changed.
