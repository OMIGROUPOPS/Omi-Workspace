# V52g Iteration 6 - joint target conservation

Date: 2026-08-13

## Part 1: provenance-only repairs

The canonical onset input is the runtime materialized receipt stream resampled
by the frozen 60-second onset adapter. This is the executing machine's input
grain and preserves frozen clause 1. The fit-local minute grid remains an
analysis reconstruction and is not substituted into policy. All 27 divergent
legs from `68a58029c0a6b84eda7750b185861f75d381cd49` are re-attested at the
runtime grain. None of the 11 sleeper offers becomes retroactively reachable;
all 11 would become reachable only under the rejected grid counterfactual.

MATMOR and CORSAC have inverted pre-match spans: the left edge is later than
the right edge. Consequently no in-span two-sided-book receipt reached the
gate, so no gate evaluation existed to count. The four missing leg rows are
re-emitted as `TERMINAL_GATE_BLOCK_PROVENANCE` with
`NO_GATE_EVALUATION / PRE_MATCH_SPAN_INVALID_LEFT_AFTER_RIGHT`. This repairs
recording only; it does not fabricate a PASS or FLAG and changes no policy or
score artifact. Two clean receipt builds are byte-identical across seven
files.

## Part 2: V52g clause 6

V52g adds one clause to frozen V52f. At each receipt, any two
decision-time-known bought/standing values must satisfy
`target_A_cents + target_B_cents <= 99`. Existing level authorities evaluate
first. When the identity binds, only the newly evaluated standing value is
bounded by `99 - counterpart_cents`. After one side is bought, the clause
degenerates to V52f's frozen settlement identity. Clauses 1-5, N9 continuous
CLEAN priors, trades-as-truth crediting, scavenger OFF, and `REFLEX_POST=0`
remain frozen.

Each game owns exactly one minimal `PAIR_BUDGET_RECORD`. Its shell exists for
all 30 games and becomes born at the first licensed standing value. It stores
only the current bought/standing split and the complete receipt-ordered
revision chain with license fields. It contains no goals, predictions, or
plan. That deliberately empty plan-organ surface awaits an operator design
ruling.

The observation scope is five frozen pins plus 25 fresh deterministic events,
with zero fresh-event overlap against V52b, V52c, V52d, V52e, and V52f. The
cohort seed SHA-256 is
`7f09caecfc2ec7abd0bc118dcca3ab5af41cc75e90350a65ed8df2ff10f91c26`.
Across 2,128 record revisions there are zero joint-sum violations; all 30
games have exactly one record and complete revision chains. All four former
`COMPLETE_AT_LOSS` identities remain lawful, no new loss completion appears,
the five pins are unharmed, and SANDAN is at-or-better.

The outcome is observation, not adjudication: frozen V52f completes 12/30 at
delta; V52g completes 10/30 at delta. V52g has 11 partial and nine neither.
No policy edit was made from this observation and no 804 disposition was run.

Two clean V52g builds are byte-identical across 52 files. Fifteen inherited
and focused test files pass 456 assertions with zero failures, omissions, or
deselections. The candidate decision trace contains 384,101 rows. No sealed,
holdout, deployment, authorization, live, network-runtime, order, position,
exit, settlement, or DCA action occurred.

Canonical packages:

- `.claude/window1_live_v4_replay/v52g_provenance_repairs_20260813/`
- `.claude/window1_live_v4_replay/v52g_joint_target_conservation_20260813/`
