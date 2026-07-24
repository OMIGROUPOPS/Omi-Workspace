# Corrected Window-1 deterministic development replay

## Raw counts first

- D = 804
- strict dual exact-five Window-1 completions = 0
- strict dual exact-five Window-1 completions with negative combined Window-1-close delta = 0
- combined entry cost under par = 0
- both individual-leg deltas negative = 0
- one-leg-only negative delta = 0
- dynamic-floor gap evaluated events = 0
- dynamic-floor gap at or below zero = 0
- per-leg dip/catch evaluated = 10
- per-leg at or below fitted target = 5
- per-leg within four cents of fitted target = 9
- nonfill events = 544
- non-Window-1 fill events = 66
- other-quantity fill events = 12
- timing-censored events = 728
- feature-censored events = 804

## Start precision

- exact starts = 29
- clean causal intervals capable of proving a positive = 47
- contradictory intervals unable to prove a positive = 32
- live-by events usable only for nonfill or proven-not-Window-1 = 625
- fully timing-censored events = 71
- positive-Window-1-provable population = 76
- remaining timing-censored population = 728

## Primary bounds against D = 804

- strict lower bound = 0 (0.000000%)
- optimistic upper bound = 240 (29.850746%)
- distance from the 75% target at the strict lower bound = 603 events
- distance from the 75% target at the optimistic upper bound = 363 events
- lawful-bounds verdict = target_proven_failed

Every rate in `RESULTS.json` is also printed against D = 804. Censored events remain in D and are not observed successes.

## Causality and contamination

Positive Window-1 classifications require an exchange placement clock for every filled order, exchange fill/completion clocks, and an exact or clean-interval safe pre-start cutoff. Schedule values, local receipt clocks, missing completion clocks, and hardcoded defaults prove neither a positive nor a post-start ruling.

AIM_V2 and its byte-identical LATCHCAL prior are excluded. The independent recut-cell surface is consumed only for dynamic-floor and dip/catch reporting. No walk-law or touch proxy is executable.

The historical 10-contract overfill remains an other-quantity fill and never counts toward exact-five completion.

No holdout, Window 2, exit, settlement, DCA, production, live_v4, configuration, order, or position input was consumed or changed.
