# Independent Window-1 T2 scoring-package V4 audit

Do not run or authorize the scorer. Blindly verify before opening expected
receipts:

1. Recompute the V3 failure commit, its parent, all five artifact hashes, exact
   stack, one runner invocation, one scorer-call attempt, zero completed event
   rows, and zero completed candidates.
2. Independently load all raw V5 and normalized boundary rows. For every event,
   compare `boundary_contract(raw)` to normalized and compare
   `guarded_cutoff(raw)` to the operative normalized status/cutoff/guard.
3. Iterate `iter_prepared_scorer_calls` for all 6,432 candidate-event calls.
   Freeze hashes/counts before opening V4 summaries. Prove each exact
   `score_kwargs["boundary"]` is the full raw V5 row, never normalized.
4. Independently inject a scorer exception and prove attempt count persistence
   precedes entry while completed row/candidate counts remain zero.
5. Compare only after freezing independent receipts. Any mismatch is BLOCK;
   no post-hoc reconciliation is permitted.
6. Verify additions-only lineage, consumed V2/V3 authorization rejection,
   null metrics, results-directory absence, holdout/non-live fences, complete
   tests, and two-build determinism.

A PASS certifies a score-free PRE-RUN only. V4 execution requires a new,
separately bound one-use authorization.
