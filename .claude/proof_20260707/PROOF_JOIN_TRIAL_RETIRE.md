# OUTCOME PROOF (C46, two-lane) — C-RETIRE-JOIN-TRIAL (config-only flip)

**Candidate SHA: `501a23ae`** (`join_trial_mode: true → false`, config-only; no code, no tables).

## Prior art (C45)
Join-the-bid 5¢ trial staged 06-17 (pre-registered abort spec LOCKED @8cc9ff1, `docs/policy/join_trial_abort_spec.md`); **trial DIED 2026-06-18** (night-1 −$10.12; join-induced naked legs — partner starved behind the MM wall; abort structurally blind to starvation). LIVING_VAULT RETIRED grave + CONFORMANCE §4 archaic-ARMED finding. Precedents for config-only gated flips: PLEX_FLIP (per_match_clock, Ratification #20), RISER_DISARM (pre-registered rule).

## LANE 1 — MECHANISM (deterministic, code-scoped)
`join_trial_mode` gates exactly two sites (grep-complete): **live_v4.py:5139** (`_join_trial_resolve` early-return — the trial-abort bookkeeping) and **:7031** (`pos.join_is_trial = self.join_trial_mode` — the stamp). Neither is on the placement, walk, exit, completion, or reconcile paths; no price, size, timing, or cancel decision reads the flag. Replayed against today's tape: **528 `"trial": true` stamps, 0 abort fires** — the flip removes false stamps and de-arms a path that never fired. Construction delta: ZERO on every Lane-1 metric (grades, ≤97 rate, Δaim, pair completion) by code-path construction.

## LANE 2 — SETTLEMENT P&L
Not applicable (no order-path delta); flagged pro forma per C46.

**Verdict: flip is bookkeeping-only de-arming of a dead trial; deploys through the full gate with the C47 boot audit as the live check and C50's bootstrap recording.**
