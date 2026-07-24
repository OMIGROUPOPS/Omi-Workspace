# Window-1 start-gated development contract

## Authority and scope

This lane incorporates the independent semantic audit at
`56ab6cfd724dc1659b1d44b58c4026642408eed3`.  It preserves the published
corrected replay under `.claude/window1_corrected_20260723/` and issues new
semantic-correction artifacts; prior receipts are never overwritten.

The immutable development population is all 804 floor-passing big-4 events
dated July 12–20, 2026.  July 24–26 remains preserved and unopened.  No
production, `live_v4`, configuration, order, position, Window 2, exit,
settlement, or DCA surface is an input or output of this lane.

## Execution order

1. `window1_replay_receipt_correction.py` corrects only the published
   historical bound and post-start semantics.  It performs no replay or
   policy evaluation.
2. `window1_real_start_recovery_v3.py` constructs the start ledger without
   reading any placement, fill, policy, or candidate outcome.  Raw provider
   responses remain outside Git; only sanitized identities, bounds, source
   receipts, and hashes are published.
3. `window1_start_replay_adjudication.py` classifies the already-frozen
   historical receipts against the frozen start ledger.  It cannot change
   placement, cancellation, fill, price, or quantity.
4. `window1_os_family_tuning_runner.py` validates and hashes the predeclared
   OS-family contracts.  It checks the 603-event start gate before it can
   open any candidate result or market-outcome input.
5. `window1_start_lane_finalize.py` publishes the combined machine and human
   receipts and asserts that a failed gate has not become a strategy verdict.

## Start law

Source precedence is:

1. exact official-provider match-start timestamp;
2. raw `milestone_shadow`;
3. `tennis.db` start or live-score observation;
4. historical `live_v3`/`live_v4` log;
5. mapped score-onset interval;
6. genuinely event-resolved exchange lifecycle transition;
7. true-tape regime interval;
8. schedule as a last-resort bound.

An exact point, or a noncontradictory interval with both a causal
not-live-through lower bound and causal live-by upper bound, can prove a
positive Window-1 event.  A live-by-only or schedule-only timestamp cannot.
Contradictory evidence remains contradictory.

The historical-log class excludes
`engine_regime_transition:self_fill`: an actual own fill is a policy outcome,
not an independent start source.  It cannot supply even a negative-only
live-by bound in the policy-blind extraction.

The gate passes only when at least 603 events have a positive-capable
boundary.  Below 603, no development candidate result may be opened and no
75% strategy verdict may be issued.

## Frozen candidate family

`WINDOW1_OS_FAMILY_CANDIDATES_V1.json` mechanically declares all permitted
policy IDs and parameter ranges.  It contains no free numeric parameters;
numeric values may only come from its named pre-existing frozen surfaces.
The adapter, feature allowlist, fill kernel, metric contract, prospective
holdout declaration, runner, and candidate specification are hashed as
committed LF Git blobs.

AIM_V2 and SHA-256
`6183ddec56eaab2ad48432aa7c802ea6265e608fa26cdd960aa1dde866824356`
are prohibited.  Raw non-LATCHCAL observations from the shape corpus have an
independent lineage beginning at `f853daf8`, before the AIM_V2 derivation
commits.  No AIM_V2 cells, offsets, aims, targets, or fallback hierarchy may
be consumed.  Missing causal features disable only that feature at that
timestamp; they do not censor the event or invoke a proxy.

The runner also excludes Pinnacle, unproven reconstructed full depth, future
information, the narrow walk-law proxy, Window 2, exits, settlement, and DCA.

## Reproduction check

The targeted validation set is:

```text
python -m pytest \
  arb-executor/tests/test_window1_replay_receipt_correction.py \
  arb-executor/tests/test_window1_real_start_recovery_v3.py \
  arb-executor/tests/test_window1_os_family_tuning_runner.py \
  arb-executor/tests/test_window1_start_lane_finalize.py \
  arb-executor/tests/test_window1_recovery_manifest.py \
  arb-executor/tests/test_window1_fit_benchmark.py \
  arb-executor/tests/test_window1_policy_runner.py -q
```

The final test module is retained only to prove that the deprecated proxy
runner is marked non-authoritative; its tests are intentionally skipped.
