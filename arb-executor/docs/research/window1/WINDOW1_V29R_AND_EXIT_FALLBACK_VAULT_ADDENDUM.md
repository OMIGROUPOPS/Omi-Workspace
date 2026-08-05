# Window-1 V29-R and exit-fallback rulings — 2026-08-04

This addendum freezes four operator rulings without deploying or touching the
parked engine.

1. The ten-second ask dwell law is provisionally ratified unchanged so the
   result remains comparable with all prior replays. Sensitivity is deferred
   to the holdout era.
2. The silent 15-cent missing-exit-cell fallback is replaced. A missing cell
   must emit a critical alarm receipt and borrow the deterministic nearest
   cell from the same category. If no same-category surface exists, lookup
   raises. The patch is committed for audit only and is not deployed.
3. `DEAD_SPREAD_THRESHOLD = 20` and the live `spread <= 2` posting gates are
   ORPHANS awaiting a separate ruling. This build does not alter them.
4. V29-R is sequential and symmetric. The first credited fill on either side
   arms the other side at `min(99 - first_fill, own live ask at arm)`. Audited
   close is grading-only. Release is driven on every later own-book receipt by
   a coherent own descent ordinal, spread at most one cent, ten-second dwell,
   five displayed contracts, and ask at or below aim. No wall clock or polling
   cadence participates.

The V29-R replay did not improve V28: four second-side streams released earlier
at the same prices V28 later obtained. JOINT remains 65. The independent V11
ceiling denominators are retained but are not silently equated with V28's
current target population.
