# V52o benchmarked early-role instrument addendum — 2026-08-17

## Status

V52o is an observation-only iteration whose exact Git parent is V52n `74a702c8b100dedcba69a3637531ce6d77896eb2` and whose behavioral baseline is operator-adopted V52l `6678fd0c13dcc4de2bc153bbf769f5a2a9227ccc`. V52m and V52n are retained as observation controls and do not govern V52o. This addendum does not adopt V52o or authorize the full 804, sealed evaluation, deployment, live access, orders, or positions.

## Bound instrument

V52o binds the taxonomy benchmark's exact published causal early-role rule from `e269779b0ec025d55f67d576e3cfb0cb575d5890`: drift is the last true print available at or before the decision receipt minus the post-formation true-print open; drift at least +2 cents is `ROLE_UP`, drift at most -2 cents is `ROLE_DOWN`, and the interval between is `ABSTAIN`. The threshold and abstention are reused literally; V52o adds no classifier constant and consumes neither the completed path nor the right edge.

`ROLE_DOWN` consumes a per-category frequency-weighted mean of the existing down-family median depths in `PER_SHAPE_FLOOR_DEPTH_TABLES` at `8ab4f2d9e8c831235dc7cb4570c88daa3caded50`. No row is borrowed or interpolated. The resulting depths are 8.670454545454545 cents for ATP_MAIN, 8.367816091954023 for ATP_CHALL, 8.904761904761905 for WTA_MAIN, and 10.214285714285714 for WTA_CHALL. Current touch and clause 6 bound the target. `ROLE_UP` catches at the incumbent V52l evidence-backed level; `ABSTAIN` retains V52l and is re-evaluated as evidence accrues.

Clauses 1–2 and 4–6, the disagreement referee, trades-as-truth crediting, scavenger OFF, and `REFLEX_POST=0` remain frozen. Every role call records the drift operands, rule SHA, and any aggregate depth row consumed.

## Observation set and findings

The cohort is five standing pins plus a deterministic fresh 25 with zero overlap against all V52b–V52n fresh cohorts. Seed SHA-256 is `0471aac319c43789874b21878b9278a62a23d27da3a3152f37fce5b87cf27f19`.

The pre-stated outcome claims are reported without tuning. On benchmark-truth legs, the instrument calls 7 of 26 (26.9231%), below the 70–90% target band, and 6 of those 7 calls are correct (85.7143%), below the 95.1% benchmark reference. Across all 60 cohort legs, 16 are called (26.6667%). Seven credited `ROLE_DOWN` legs have a 2-cent median gap to the bound ground-truth floor, above the 1.5-cent claim. Up/still V52l credits fall from 39 to 36. Gradeable completed-at-delta pairs fall from 16 to 13, while mean banked delta rises from 1.9375 to 2.384615 cents and clears the 1.83-cent comparison. Four one-sided exposures are created and none resolved. One `UNKNOWN_BELL` game remains separate and non-gradeable.

These misses are observations, not mechanical faults. No post-hoc classifier, threshold, cohort, depth row, or policy edit was made. Adoption remains an operator decision.

## Verification and safety

The complete inherited-plus-V52o suite passes 609 assertions across 16 files with zero failures, omissions, or deselections. All mechanical flow assertions pass, including exact drift arithmetic, causal receipt bounds, aggregate and SHA consumption, V52l fallback for `ROLE_UP`/`ABSTAIN`, touch and clause-6 bounds, role re-evaluation, lawful pins, and `REFLEX_POST=0`.

Two clean builds compare 77 pre-receipt artifacts byte-for-byte with zero mismatches. The frozen package is `.claude/window1_live_v4_replay/v52o_benchmarked_role_instrument_20260817/`. No full-804, sealed, deployment, live, network-runtime, order, or position action occurred.

VAULTED: V52o literally binds the benchmarked ±2-cent early-role instrument and category-weighted down-family depth surface over V52l, retains V52m/n as observations, and passes every mechanical fence; the fresh-30 observation misses coverage, accuracy, down-gap, up/still-preservation, and completion claims while improving mean banked delta, so it remains unadopted pending operator adjudication.
