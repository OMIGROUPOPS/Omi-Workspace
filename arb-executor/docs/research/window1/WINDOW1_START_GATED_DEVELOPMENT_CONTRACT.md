# Window-1 start-gated development contract

## Authority and scope

This lane incorporates the independent start-ledger cross-review from
`origin/audit/window1-independent` at
`9919de9462f3df4a0bd33239b7e8f648b71e20fb`, specifically
`START_LEDGER_V4_CROSS_REVIEW.md`. It preserves the published
corrected replay under `.claude/window1_corrected_20260723/` and issues new
semantic-correction artifacts; prior receipts are never overwritten.

The immutable development population is all 804 floor-passing big-4 events
dated July 12–20, 2026.  July 24–26 remains preserved and unopened.  No
production, `live_v4`, configuration, order, position, Window 2, exit,
settlement, or DCA surface is an input or output of this lane.

## Execution order

1. `window1_start_guard_calibration.py` derives the asymmetric proxy guard
   from the frozen official-start calibration without reading performance.
2. `window1_start_guard_repair.py` relabels all 453 five-minute-grid
   TennisExplorer clocks, retains stronger causal bounds, censors the 13
   named conflicts, and re-adjudicates the seven historical witnesses.
3. The corrected ledger, adapter, metric contract, candidate allowlist,
   feature allowlist, runner, code, data, and parameter-surface hashes are
   committed and pushed in a PRE-RUN commit.
4. Only after that remote PRE-RUN commit exists may
   `window1_os_family_search.py` read development market evidence and execute
   the deterministic 24-policy grid plus its predeclared ablations.
5. Results and sanitized event/candidate ledgers are committed and pushed;
   work stops for independent audit.

## Start law

The source-evidence conservation is immutable:

- 687 start-clock rows (234 official exact and 453 quantized proxies);
- 31 clean causal intervals;
- 14 contradictory;
- 20 schedule-only;
- 52 live-by-only;
- total 804.

Source precedence is:

1. exact official-provider match-start timestamp;
2. raw `milestone_shadow`;
3. `tennis.db` start or live-score observation;
4. historical `live_v3`/`live_v4` log;
5. mapped score-onset interval;
6. genuinely event-resolved exchange lifecycle transition;
7. true-tape regime interval;
8. schedule as a last-resort bound.

An official exact point, or a noncontradictory interval with both a causal
not-live-through lower bound and causal live-by upper bound, can prove a
positive Window-1 event.  A live-by-only or schedule-only timestamp cannot.
Contradictory evidence remains contradictory. TennisExplorer clocks are
never exact. The calibrated central interval is
`[proxy_clock-900s, proxy_clock+600s]`: a positive requires completion at or
before the lower edge, a post-start ruling requires completion at or after
the upper edge, and the interior is censored. Official points and clean
interval edges use a strict 60-second guard.

A pre-clock causal `live_by` bound is retained regardless of whether its
source rank is numerically weaker than the rank-3 proxy. The proxy cannot
overwrite it. Only a strictly higher-precedence `not_live_through` bound can
block the proxy interval; a tie never promotes the proxy to exact.

The historical-log class excludes
`engine_regime_transition:self_fill`: an actual own fill is a policy outcome,
not an independent start source.  It cannot supply even a negative-only
live-by bound in the policy-blind extraction.

The pre-correction population gate remains 718. The independent audit names
13 proxy rows that are not positively cleared; the guarded scoring ceiling
is therefore 705 named positive-capable events. This evidence-backed shrink
does not change D and remains above 603.

## Frozen candidate family

`WINDOW1_OS_FAMILY_CANDIDATES_V1.json` mechanically declares all permitted
policy IDs and parameter ranges.  It contains no free numeric parameters;
numeric values may only come from its named pre-existing frozen surfaces.
The adapter, feature allowlist, fill kernel, metric contract, prospective
holdout declaration, runner, and candidate specification are hashed as
committed LF Git blobs.  Every named fixed parameter surface receives its
own committed-blob receipt; the exact policy allowlist and parameter-range
objects receive independent canonical hashes as well.

AIM_V2 and SHA-256
`6183ddec56eaab2ad48432aa7c802ea6265e608fa26cdd960aa1dde866824356`
are prohibited.  Raw non-LATCHCAL observations from the shape corpus have an
independent lineage beginning at `f853daf8`, before the AIM_V2 derivation
commits.  No AIM_V2 cells, offsets, aims, targets, or fallback hierarchy may
be consumed.  Missing causal features disable only that feature at that
timestamp; they do not censor the event or invoke a proxy.

The runner also excludes Pinnacle, unproven reconstructed full depth, future
information, narrow proxy substitution, feature-gap imputation, schedule as
start, Window 2, exits, settlement, and DCA. Top-five pressure, bookmaker/FV,
shape, cohort, orientation, own-order, and contributed-volume features each
carry per-event coverage; absence disables only the named feature.

## Metric contract

`D=804`. `C` is a dual exact-five completion inside the guarded Window 1.
`PC` is a member of C with negative combined Window-1-close delta. `S` is a
member of C with combined cost below 100 cents. `IC` is a member of C with
both individual deltas negative. The per-leg reference is the last
positive-size exchange-identified deduplicated true print at or before the
event's strict positive cutoff. Missing references never become success.
The target is fixed at `PC>=603`.

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
