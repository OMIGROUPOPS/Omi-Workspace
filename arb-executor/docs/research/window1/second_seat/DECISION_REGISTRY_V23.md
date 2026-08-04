# The decision registry — V23, every knob in the decision trace

Analysis seat only. Descriptive. Read-only. A machine-readable inventory of every
predicate / constant / threshold appearing in the frozen V23 decision trace
(`decision_trace_v23_20260804/DECISION_TRACE_1608.json` @ commit 6b9c0ff), one row
per name, with its site, inputs, threshold, and the authorizing ruling/receipt —
or ORPHAN. Rows in `DECISION_REGISTRY_V23.csv`; summary in
`DECISION_REGISTRY_V23_SUMMARY.json`.

## Premise correction (a finding in itself)

The task said "from live_v4 source." **None of these predicates are in
`live_v4.py`** — a grep for the predicate tokens returns 0. They are implemented in
the quote-shape-elimination **replay pricer** JS modules
(`window1_quote_shape_stable_signer_v4`, `…_micro_position_v2`, `…_pair_wiring_v3`,
`…_persistence_floor_v11`, `window1_v23_isolated_rearm_policies_v27`) plus the
fitted shape library. `live_v4.py` is the live trading organ (ATLAS aim, staircase
hold, gun) and carries a *different* knob set that never enters this trace. The
registry cites the actual replay-pricer source.

## Conservation

The trace's predicate-name universe is **41 distinct names** (keys of every
`predicates` block plus every `failed_predicates` token, over all 1,608 rows).
**The registry has exactly 41 rows — every trace name appears once, none missing,
none invented.** Roles: **22 gates · 9 failure-tokens · 10 feature-inputs.**

Sites (trace execution order): ADMISSION · BOOK · IDENTITY · FLOOR · VERDICT ·
ANCHOR · SIBLING_PAIR · PLACEMENT_CAP · FILL · COMPLETION. (The 41 named
predicates land at FLOOR, VERDICT, ANCHOR, and SIBLING_PAIR; the later sites flag
by layer, not by named predicate.)

## The ORPHAN — the one tuned number with no ruling

**The 10-second same-price dwell.** `window1_v23_isolated_rearm_policies_v27.js`
hardcodes `const DWELL_SECONDS = 10;`. No vault ruling or receipt authorizes ten
seconds — it is a hand-set constant. It appears in the trace under **three names**,
all ORPHAN:

| name | role | threshold | authority |
|---|---|---|---|
| `ask_dwell_at_least_10_seconds` | gate | 10 s | **ORPHAN** |
| `ASK_DWELL_BELOW_10_SECONDS` | failure-token | 10 s | **ORPHAN** |
| `ask_dwell_at_least_existing_threshold` | gate (alias) | 10 s | **ORPHAN** |

Every leg's qualifying floor is gated on this number; it decides whether a resting
ask is "stable enough" to sign. Nothing behind it is written down. This is the
build-queue's standing input for a ruling.

## What IS authorized

- **5-contract capacity** (`top_ask_capacity_at_least_five`, `QUANTITY = 5`) —
  authorized by the LIVING_VAULT **"five-contract-proven floor"** (exact
  five-contract `FILLABLE_AT_X`). The other tuned constant has a ruling; the dwell
  does not.
- **Shape verdicts** (`unanimous_floor`, `unanimous_lower`, `upstream_consensus_ready`,
  `SHAPE_VERDICT_STILL_LOWER`, `fitted_descent_ordinal_unavailable`,
  `fitted_leave_one_leg_out_persistence_exhausted`,
  `zero_leave_one_leg_out_future_qualified_lower_support`,
  `unanimous_lower_before_override`) — **fitted** organs, authorized by their fit
  receipts (coherent_shape_refit_v12 / persistence_floor_v11), grain
  category+region+topology, per-cell support_n. Not hand-tuned.
- **Stable-signing** (`stable_signing_support` + `top_ask_price_and_size_persisted`,
  `ask_pulse_exceeded_spread_and_returned`, `strictly_later_same_price_ask_receipt`,
  and the failure-token / variants) — **structural**, authorized by the
  stable-same-price V2 spec and the module's own principle: *"a stable same-price
  ask is not self-authenticating… no count, elapsed-time, or fitted threshold is
  added."* No tuned number to orphan.
- **Micro-position** (`own_micro_position_observed`), **anchor-freshness**
  (`current_ask_at_observed_low`, `fresh_own_book_receipt`, `fresh_own_receipt`),
  **inverse-sibling** (`inverse_sibling_resolved`,
  `resolved_inverse_sibling_has_ask_transition`) — **structural** boolean
  recognitions (later-receipt / running-low / sibling-transition), no tuned
  constant; authorized by their module seams (micro_position_v2, pair_wiring_v3,
  the qualifying-floor law).
- **10 feature-inputs** (`ask_dwell_seconds`, `top_ask_size`, `top5_ask_depth`,
  `spread`, `quote_rate`, `ask_change_rate`, `same_price_receipt_count`,
  `episode_distinct_bbo_states`, `episode_distinct_size_values`,
  `seconds_since_prior_receipt`) — live-tape observables consumed by the gates
  above; not thresholds themselves.

## Reading

The registry is small and mostly clean: of 41 names, the pricer's decision surface
is **fitted or structural**, with exactly **two** hand-set constants — and only one
of them, the **10-second dwell**, has no ruling behind it. That is the single
ORPHAN, and because it gates every leg's floor, it is the one number to either
ratify or replace before the build queue leans on this trace. The premise
correction stands beside it: the trace's authority lives in the replay pricer, not
in `live_v4.py`.

## Caveat (v1 scope)

The ORPHAN determination covers the operative tuned constants in the V23 re-arm
module (`DWELL_SECONDS`, `QUANTITY`). A line-by-line audit of all seven pricer
modules for any further hidden constant is the v1 follow-up; nothing in the
module headers (which explicitly disclaim added thresholds) suggests more, but the
registry should be re-run against a full constant sweep to close it.

## Artifacts

`DECISION_REGISTRY_V23.csv` (41 rows: site, name, role, trace occurrences, meaning,
inputs, threshold, authorizing ruling / ORPHAN) and
`DECISION_REGISTRY_V23_SUMMARY.json`.
