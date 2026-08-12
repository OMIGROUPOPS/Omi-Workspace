# V52c Iteration 2 - full post-onset evidence horizon

Date: 2026-08-12

## One-clause scope

V52c changes clause 2 only. At each evaluation receipt, the machine read may
consume every causal exchange-print and book receipt observed since the
already-frozen stability onset. Evidence is recency-weighted by causal receipt
rank: all prior post-onset evidence retains positive weight, and there is no
fixed time cutoff or replacement tuning constant. `READ_ABSENT` is returned
only until the evidence contains a causal book transition, print transition,
or print-to-book comparison capable of supporting a read.

Clauses 1, 3, and 4 are frozen from V52b. Clause 1 remains stamped
`CODEX-INTERIM`. V52c inherits the V52b `machineReadLevel`, `gateDecision`, and
`firstFailure` functions by object identity. Trades-as-truth crediting is
unchanged, scavenger is OFF, and `REFLEX_POST` is zero. The full evidence span,
receipt counts, source counts, first/last evidence, weighted direction scores,
and insufficiency reason are attached to every read license.

## Deterministic observation cohort

The population is the five frozen pins plus a fresh 25-event development
cohort. The new 25 exclude all 25 events used by V52b and are stratified by
category and paired queue/formation/reflex census stamps. The seed material is
`V52C_ITERATION2_COHORT25|98d07986fd916c1d75beb45095c75752bbc65102`;
its SHA-256 is
`ca37c21c3a83904bb079d5b82d1c6b97c8db427508926c5e7e5bee2d0dd4f61e`.
The exact 30 events and event-list hash are frozen in the cohort receipt.

## Mechanical result

- All five flow assertions pass; every post carries all four license fields.
- No post occurs before onset or on `READ_ABSENT`; no displayed bid becomes
  level authority; scavenger is OFF and `REFLEX_POST` is zero.
- Frozen clauses 1, 3, and 4 have zero receipt-law differences.
- Across the 55 legs where frozen V52b emitted at least one `READ_ABSENT`, the
  count falls from 103,397 receipt decisions to 55. Across all 60 legs, V52c
  emits 57 `READ_ABSENT` decisions.
- The baseline trace has 510,043 rows and V52c has 512,913. Clause-2 behavior
  changes 514,088 decision receipts and 44 leg action streams.
- The missing ARSMAR `MAR` side is exported as a 1,041-row gate trace.
- MERDRO's formation-era 6-cent prints are not credit receipts. Its post-onset
  DRO credit follows a fully licensed post and is lawful under the corrected
  authoring statement.
- Two clean builds compare 21 pre-determinism artifacts byte-for-byte.
- Focused and inherited tests pass: 25 V52c unit, 40 V52c package, 17 V52b,
  and 14 V52 tests (96 total).

## Observations only

On this fresh 30-game cohort, frozen V52b completes 10 under-par pairs and
V52c completes 9. These are observations, not an acceptance bar or
disposition-804 adjudication, and no policy edit was made from them. ARSMAR
remains incomplete; POLKUH's KUH side credits; MERDRO satisfies the corrected
authoring statement.

No disposition-804 run, deployment, authorization, holdout access, live
access, network runtime, order action, or position action occurred.
