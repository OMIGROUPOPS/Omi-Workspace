# Independent V3 PRE-RUN audit instruction

Audit the score-free Window-1 T2 scoring-package V3 as a blind,
execution-readiness repair. Do not run the scorer and do not authorize it.

1. Hash and parse the raw V5 boundary ledger before opening any V3 expected
   summary. Independently derive `boundary_contract(raw)` and
   `guarded_cutoff(raw)` for all 804 events.
2. Independently derive all 1,608 Window-1-close references from the full raw
   V5 rows and guarded-cache true prints using the audited V2 reference law.
   Freeze your counts, hashes, mismatch identities, availability, tie, and
   ambiguity census before opening V3 compatibility/reference summaries.
3. Independently run the real-input path only through the boundary immediately
   before the first scorer call. Require zero scorer invocations and no results
   directory.
4. Only after the independent receipt is immutable, compare it with
   `REFERENCE_BOUNDARY_COMPATIBILITY_RECEIPT.json`,
   `REFERENCE_LEDGER_CENSUS.json`, and
   `EXECUTION_READINESS_NO_SCORE_RECEIPT.json`.
5. Any mismatch is BLOCK. Do not reconcile post hoc to an expected value.
6. Verify the V2 failure binding, the Eastern-time discrepancy, rejection of
   the consumed authorization/execution ID, additions-only lineage, two-build
   determinism, null metrics, sealed holdout, and forbidden-access claims.

Return PASS or BLOCK. A PASS is package-readiness evidence only; execution
still requires a new separately bound one-use authorization.
