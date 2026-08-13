# V52h Iteration 7 - remove pair-lows market proof

Date: 2026-08-13

V52h removes exactly one licensing precondition from frozen V52g: a pair's
post-onset traded lows no longer must already sum below 100 before a rest may
be licensed. Those lows remain recorded telemetry. The clause-4 disagreement
referee remains fully intact. Clauses 1, 2, 3, 5, and 6, N9 CLEAN-store
consumption, trades-as-truth crediting, scavenger OFF, and `REFLEX_POST=0`
are frozen. Clause 6 continues to enforce `target_A + target_B <= 99` at
every receipt, so completed-at-loss remains structurally unavailable.

The observation scope is the five frozen pins plus 25 deterministic fresh
events. Its seed SHA-256 is
`bd33dc89cbb7a279eb77bc228b6eee8c27650bbd299b4ed7beb19edf09a20005`.
The fresh 25 has zero overlap with the V52b, V52c, V52d, V52e, V52f, and
V52g fresh cohorts. SMIILA was already used by V52b, so it is bound honestly
as a separately replayed named observation outside the fresh-25 score cohort.

On the 30-game observation, V52g records 10 complete-at-delta, 15 partial,
and five neither. V52h records 16 complete-at-delta, 12 partial, and two
neither. Both conserve to 30; V52h records zero `COMPLETE_AT_LOSS`. SMIILA
converts from incomplete under 5,786 market-proof blocks to a lawful 98-cent
completion, with zero remaining market-proof blocks.

The removal creates six new one-sided exposures where the second side never
trades through the licensed rest. Their exposure-to-edge duration totals
187,448.932 seconds; median is 6,573.041 seconds and maximum is 113,232.758
seconds. This is reported as a first-class consequence, not folded into a
completion count.

Every behavior change starts at or after the deleted precondition. The
disagreement referee has zero violations, all pins are unharmed, the 30 pair
budget records conserve over 3,091 revisions with zero joint-sum violation,
and `REFLEX_POST` remains zero. Two clean builds are byte-identical across 55
files. Seventeen focused and inherited suites pass 522 assertions with zero
failures, omissions, or deselections.

This is an observation-only iteration, not a full-804 disposition or an
operative ruling. No sealed population, deployment, authorization, live,
network-runtime, order, position, exit, settlement, or DCA action occurred.

Canonical packages:

- `.claude/window1_live_v4_replay/v52h_remove_pair_lows_precondition_20260813/`
- `.claude/window1_live_v4_replay/v52h_smiila_named_observation_20260813/`
