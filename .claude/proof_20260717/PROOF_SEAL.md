# PROOF_PASS — STAGE 5 SEAL WIRE, candidate SHA `0b329001`

**Prior art (C45):** Stage 3/4 C50s (the tables + the drill), Phase C
cohort engine (the consult site), LOCKED_DOWN_ENTRY.md (the ceremony doc).

## LANE 1 — MECHANISM
- The wire is a FALLBACK-ONLY read: `_cohort_read` returns live cohort
  cells and labeled borrows FIRST (unchanged code paths); the sealed table
  is consulted only when both miss AND `entry_table_prior_enabled` — and
  then only SEALED rows speak (4 bands, receipts attached); REFUSE rows
  hold the current aim and log `table_refuse_hold`; FAILED-HOLDOUT/THIN
  rows return thin exactly as before the wire (behavior identical).
- Downstream unchanged: cohort_aim logging, band clamps, floors, races.
  Lint PASS; local suite PASS (same pre-existing red).
- Blast radius: thin-cohort conceptions in 3 cats gain a labeled prior;
  everything else byte-identical.
## LANE 2 — SETTLEMENT
n/a at wire (prior speaks only where nothing else did); pre-registered
scoreboard = SEALED-TABLE consult count + steered fill quality, nightly.

- OUTCOME_PROOF = this doc, cites `0b329001`; doc-only commits after.
