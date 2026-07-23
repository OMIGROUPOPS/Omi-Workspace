# Window-1 lifecycle and boundary validation

Status: validation gate passed at game/leg lifecycle grain; no policy,
performance, target-distance, or ceiling verdict.

## Exact actual-outcome gate

The private lifecycle join remains authoritative for actual order outcomes.
It is complete by day for private-fill pagination and position
reconciliation, preserves `D=804`, and has zero row-level validation
mismatches after collapsing churn/repost order IDs to conception/event/leg
lineage.

Across 1,608 required legs:

- 258 exact five-contract fills;
- 12 exact fills at another quantity;
- 870 exact nonfills;
- 468 censored lifecycles.

This gate uses official private fills for `FILL`. A no-fill ruling requires
complete fills export, no position increase, no entry-fill attribution,
supporting cancellation/sweep evidence, and no unmatched settlement.
Everything else remains censored. The 703 anomalous order-history IDs are
provenance inside these lifecycles, not 703 games and not manufactured
nonfills.

## Repaired start-bound application

The eight-hour-left-edge actual-reproduction pass joined the exact lifecycle
ledger to the repaired start ledger and complete public tape. It processed
804 events and 1,608 legs with no instrument error:

- gate: pass;
- observed/proven `C=0`, `PC=0`, `NC=0`, `IC=0`;
- `X=456`;
- completion bound: `C` 0 observed / 240 best;
- `PC`, `NC`, and `IC` bounds: 0 observed / 240 best each.

The leg rulings are:

- 870 exact Window-1 nonfills;
- 468 censored lifecycles;
- 238 exact five-contract fills censored by start-bound uncertainty;
- 20 exact filled legs proven not complete before the start bound;
- 12 exact fills at a quantity other than five.

The observed zero is not evidence of zero market fillability. It means none
of the actual pair-complete inventory can simultaneously be proved to satisfy
the five-contract law and the repaired pre-start boundary with the retained
start evidence. Likewise, the 240 best bound is an incomplete-evidence
reproduction bound, not candidate performance or an empirical ceiling.

The public tape supplies only the frozen close reference. It never turns a
touch, same-price print, or trade-through into an actual historical fill.

## Metric and bound law

`PC`, `NC`, and `IC` overlap within `C`. `X` is separate and remains inside
`D`. A known positive exact metric is not allowed to become a favorable best
case: best-case `PC`/`NC`/`IC` additions come only from censored games whose
completion itself remains possible.

The actual-event ledger SHA-256 is
`f47b9b91239dd777ee9e71ae49f002d609f21edb5586472ec180451c394396ad`.
The actual-leg ledger SHA-256 is
`3f8f6f6eb33520e1a53c323d242e759ecc55b8f661f4a52848e56bb7ea50bf4b`.

