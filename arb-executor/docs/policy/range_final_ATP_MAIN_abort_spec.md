# C-STAIRCASE SHIP-2 — abort-spec (ratified)

The ATP_MAIN staircase walk halts NEW entries if the live deploy fails to reproduce the validated
depth/fill regime. AND-gated; resting legs continue (placement-side skip only); mirrors the
`join_trial_aborted` flag pattern.

## Constants (module-level, live_v4.py)
| constant | value | meaning |
|---|---|---|
| `STAIRCASE_MIN_RESOLVED` | **10** | evaluate only after ≥10 staircase legs reach fill-or-cancel |
| `STAIRCASE_ABORT_FILLRATE` | **0.623** | BAR 1: fill_rate **below** this … |
| `STAIRCASE_ABORT_DEPTH` | **1.44** | BAR 2: mean(realized depth) **below** this … |

**ABORT iff (over the first `STAIRCASE_MIN_RESOLVED` resolved legs):**
`mean(realized depth) < STAIRCASE_ABORT_DEPTH  AND  fill_rate < STAIRCASE_ABORT_FILLRATE`.
Realized depth = `staircase_anchor − fill_price` per filled leg.

## BAR 2 derivation (source-pinned)
- source: `docs/policy/range_final_ATP_MAIN_abort_fills.csv`
- **source content sha256 = `4e4c15534c6cb6a2f38802760b584c101bbf1f1b245e2631d7db075cc678a92e`** (`4e4c1553…`)
- n = **3595** fills
- **mean(offset) = 1.9388**
- **STAIRCASE_ABORT_DEPTH = mean(offset) − 0.5c margin = 1.9388 − 0.5 = 1.44** (ratified)

> **Reconciliation note (margin):** an earlier read used a **1c** margin → 0.9388. The ratified value
> **1.44 uses a 0.5c margin**. Wired as ratified (1.44); flagged here so the margin choice is explicit
> and auditable against the source mean.

## Telemetry
- `staircase_walk` — one per resolved leg (outcome, resolved, fills, anchor, fill_price, depth, ref, cell).
- `staircase_trial_abort` — fired once when both bars trip (resolved, fill_rate, mean_depth, bars, action).
- placement skip logs `skipped {reason: "staircase_aborted"}` once aborted.

## Tests
`tests/test_staircase_abort.py` — AND-gate unit test: <MIN no-abort; both bars → abort; each single
bar → no-abort; non-staircase ignored; telemetry present; abort fires only at ≥MIN.
