# V52b Iteration 1 — evidence-backed read-level authority

Date: 2026-08-12

## Scope

V52b changes exactly clause ③ of frozen V52. A licensed level may be named by
the frozen incumbent machine's receipt-local read only when the read has bound
directional and evaluation receipts, both are post-onset, the incumbent
authority is a live V41/V43 placement authority, and the proposed cents value
lies within prices observed after onset. The post-onset true-trade diary stays
in every license as `RECORDED_REFERENCE_INPUT_NOT_SOLE_LEVEL_AUTHORITY`.

Clauses ①, ②, and ④ remain frozen. Clause ① is restamped `CODEX-INTERIM`
without changing its selected A-or-B onset or timestamp. Clause ④ is proved by
evaluating frozen V52 and V52b on the same coherence input at every shared
receipt; both return the same failure result. Crediting remains frozen
trades-as-truth, scavenger remains OFF, and `REFLEX_POST` is zero.

## Deterministic cohort

The observation population is the five frozen pins plus 25 fresh development
events. Selection is stratified by category and the paired queue/formation/
reflex census stamps from commit
`1d5564b5cdd25de32cfa9244cf21486245ab5b55`. Within strata, events are
hash-ranked and round-robin selected. The seed is derived from the immutable
controlling parent `e20fbe6ce8bfe2619b6718e7554087fd9b900f0f`:

`SHA256("V52B_ITERATION1_COHORT25|e20fbe6ce8bfe2619b6718e7554087fd9b900f0f")`

which equals
`8cd44b2feb7d49010e7d47bbc03696d4dd768ba85d03bc1617d3214379c85735`.
The exact 30-event list and its independent list hash are frozen in
`COHORT_SELECTION_RECEIPT.json`.

## Mechanical proofs

- 669,823 frozen-V52 and 613,394 V52b per-receipt decisions are retained.
- Clauses ① and ② and scavenger match at every shared receipt; clause ④ passes
  the same-input differential at every shared receipt.
- Every V52b post has a post-onset evidence-backed machine read and all four
  license fields; no post consumes an unlicensed displayed-bid anchor.
- 676,184 decision rows differ after including authorized clause-③ decisions
  and post-divergence stream endings; 48 of 60 leg action streams change.
- Two clean builds compare 18 pre-determinism artifacts byte-for-byte.
- Focused tests pass: 17 V52b clause tests, 34 package tests, and 14 inherited
  V52 tests. The package test line-streams both full traces without flattening
  them into a monolithic string.

## Outcome observations, not adjudication

The frozen V52 baseline completes 4 of 30 observation games under par. V52b
completes 8 of 30 under par. These values grade nothing and do not authorize a
full-804 disposition.

Named observations are frozen without tuning: SANDAN's DAN level is not
derived from a displayed premium; PUTJEA uses licensed read levels or lawful
sit-out; POLKUH produces KUH licensed credit and POL lawful abstention. ARSMAR
does not complete, and MERDRO is credited. Those two named targets therefore
do not hold in Iteration 1. The construction remains an observational
mechanical pass awaiting separate disposition-804 adjudication; the outcome
failures caused no behavioral edit.

No deployment, authorization, live access, holdout access, order action,
position action, or full-development scoring run occurred.
