# V52d Iteration 3 - disagreement referee

Date: 2026-08-12

## One-clause scope

V52d changes clause 4 only. When the full post-onset read and the Jul 6
depth-pressure read disagree, the gate compares their causal backing at the
same receipt. The strict comparison order is evidence class (print-backed over
quote-path over depth-pressure), then backing-receipt recency, then magnitude
of the evidencing move. A strictly stronger reading is licensed and the full
winner, loser, and comparison are written into the birth license. An exact tie
keeps the frozen disagreement block.

Clauses 1, 2, and 3 remain frozen. V52d inherits V52c's
`fullPostOnsetRead` and `fullPostOnsetAuthority`, and V52b's
`machineReadLevel`, `gateDecision`, and `firstFailure`, by exact function
identity. The pair-under-par check and trades-as-truth crediting are unchanged;
scavenger is OFF and `REFLEX_POST` is zero. The referee consumes no Palantir,
N9, post-bell, historical, or out-of-game input.

## Deterministic observation cohort

The population is the five frozen pins plus a fresh 25-event development
cohort. The fresh 25 have zero overlap with both prior V52b and V52c fresh
cohorts and are stratified by category and paired queue/formation/reflex census
stamps. Seed material is
`V52D_ITERATION3_COHORT25|9f00b35f414d3f9a4011886bb8cb4e6cbe7da474`;
seed SHA-256 is
`680c78dbbd28581661addf44c6dee5bc1766fe54484c1e10909572320b892d79`.

## Mechanical result

- All flow assertions pass; no post precedes onset or occurs on a missing read,
  no displayed bid becomes an unlicensed level, and every post binds all four
  license fields.
- The baseline emits 15,755 order-masked `FIRING_DISAGREEMENT_ACTIVE`
  decisions. V52d emits zero.
- V52d records 69,471 referee firings. All 69,471 have strictly stronger
  backing under the ordered law; the observation cohort contains zero exact
  ties.
- On the receipt universe where onset, a read, and the pair-under-par check are
  available, the observed disagreement firing share is 77.2080%, not a
  coerced 43%.
- The operator's pre-stated ARSMAR count of 127 is not the frozen trace's row
  grain. Frozen V52c has 510 ARSMAR disagreement blocks. V52d records 951
  ARSMAR referee firings and leaves zero disagreement blocks. ARSMAR remains
  incomplete; completion was explicitly a hoped conversion, not the
  falsifiable claim.
- The candidate changes 80,967 decision receipts and 55 leg action streams,
  all downstream of clause-4 adjudication.
- Frozen V52c completes 9 of 30; V52d also completes 9. Credited legs move
  from 32 to 34 and five-lot locked cents from 65 to 70. These are observations
  only.

Two clean builds are byte-identical across 25 pre-determinism artifacts.
Focused and inherited tests pass: 31 V52d unit, 41 V52d package, 25 V52c unit,
17 V52b unit, and 14 V52 unit assertions (128 total). No disposition-804 run
occurred. No deployment, authorization, holdout or live access, network
runtime, order action, or position action occurred.

The operator reads the frozen traces before separately ordering the full-804
bell. This build does not trigger it.
