# Feature panel: full-universe atlas screen

Bench only. No engine, pool, pricing, conduct or face change.

## Protocol

- ATP_MAIN and ATP_CHALL remain separate, using corrected baseline receipts
  c7825925 and 969111f3 and the pinned tick-library/print-count sidecar.
- All available gates from the baseline's 15-gate atlas are evaluated for every
  query. No observed change-point receipts are added. A gate preceding a
  query's first tick is unavailable, not backfilled. Both carried-state floors
  and strictly-later positive-size-print floors retain their own denominators.
- All six cumulative variants and six leave-one-block-out variants remain.
  FIRST is unchanged. R0 results here are explicitly **GATE-SIM**, not evidence
  about repricing between gates or a replacement for full-cadence proof.
- Nested earlier-only fitting, equal-game CRPS, walk-forward membership,
  leave-self/date-out and receipt-time roles remain as filed. April's missing
  earlier training and May's missing inner validation are explicit outcomes,
  never evidence that a feature has zero effect.
- June is the operator-approved new-experiment holdout, not historically
  unseen. Strict June freezes weights, scales AND the member library before
  its earliest query formation. June outcomes cannot choose finalists.
- The non-June selection accumulator uses the identical filed criterion at
  each side/gate/target: minimum matched games and strict-win share are read
  from the bound receipt, not independently typed. Ties are not wins. Primary
  full-universe and strict-June tables are also reported, without conflating
  their denominators with selection.
- Only variants with qualifying non-June evidence advance. Each finalist still
  requires full-universe, full-receipt, two-pass proof against unchanged FIRST.
  A screen result or a subset determinism check is not that proof.

## Exact cache

The raw member feature-state key is `(source manifest scope, member identity,
exact float64 minutes-to-bell bytes, span SHA256)`. The span digest contains both
legs' formation and bell clocks. No rounding, interpolation shortcut, member
cap, missing-value imputation or future-query timestamp enters the cache.
Eviction changes only execution cost. Tests cover adjacent float clocks,
negative zero, span changes, eviction and repeated-run byte identity.

## Numerical stall repair

The original projected-gradient fit is retained. An OBJECTIVE_STALLED result
is not accepted as convergence. Stalled fits receive a bounded Newton polish
using finite differences of the existing analytic CRPS gradient. The objective,
nonnegative coefficients, original Armijo test and original projected-gradient
tolerance remain unchanged. Small objective improvement alone no longer ends
the refinement. No global optimum is claimed.

Every block/month reports its inner optimizer status, any original stall and
refinement, gradient residual, validation cohort size, selected coefficients
and refit outcome. CONVERGED, STALLED, ZERO_WEIGHT_BY_VALIDATION,
NO_INNER_VALIDATION and NO_EARLIER_TRAINING are distinct.

## Files and execution

`feature_panel_atlas_run.py` wraps the existing hash-bound launcher in its own
process. It does not rewrite the frozen full-pass modules; MAIN pass 2 can
finish unchanged. Screen workers are one coordinator with a shared state
cache. Private inputs/diagnostics remain outside Git.

Use the original feature launcher arguments, substituting the atlas launcher,
and add `--state-cache-mib 128 --workers 1`. Use a fresh private output directory
per category. Do not import old fitted models or full-run checkpoints: the
repaired learner must actually fit. A failed cheap screen restarts; partial
outputs are never published as complete.

`feature_panel_atlas_publish.py --run <private screen> --out <public category>`
verifies source/output hashes, all-query coverage, gate-only receipt counts,
held-out population and the selection contract. For MAIN add `--main-full
<completed full feature pass>` to verify exact FIRST gate-score parity.

Published JSON/Markdown contains aggregates, optimizer outcomes and provenance.
No source prints, feature arrays, fitted-sample caches or per-receipt diagnostics
are copied. The inactive Actions matrix, exact local input hash allowlist and
required deployment approvals are documented in ACTIONS_APPROVAL.md.

## Executed-source provenance

`source/feature_panel_atlas_run.executed.py` preserves the exact launcher bytes
bound by both screen receipts. After launch, the current launcher received one
report-only correction: its private summary now reads `r0_conduct` rather than
the nonexistent `conduct` key. The public publisher already projected the
correct R0 data directly from the scoreboard. No fitting, forecast, scoring,
selection, clock or cache logic changed; the running processes retain the
executed version recorded in their receipts.
