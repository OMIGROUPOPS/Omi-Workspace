# OUTCOME PROOF (C46, two-lane) — THE OS BUILD (consumption layer, shadow-first; Plex T1–T4)

**Candidate SHA: `1a187f77`**.

## Prior art (C45)
- **GAME_LIFECYCLE.md** (this build IS steps 2–5 as code) · **CLIMBSIDE_SPEC.md** (T3-ratified posture: T−90 resting, fitted level, NO upward revision by construction, stand-down onset+15) · **Plex T1–T4 (this date)** — T1 import boundary same-PR, T4 hold-gate dual readings binding-before-logging · **recut_cells_volume** (the aim surface, thin-tape flagged) · **FILL_REDO regimes** (mains join-only cliff; ITF depth ladder) · **STEP1 P1b** (floor staged: placement-light, hold-hard) · **combined-price / granularity / category laws** (levels macro, triggers micro, all per-cat).

## LANE 1 — MECHANISM
- **The OS cannot trade, twice over, by construction:** (1) `oslayer/` is order-path-PURE, asserted at EVERY gate by the new `os-import-boundary` AST check in lint_gate.py (no live_v4/network imports, no `place_order`/`cancel_order`/`api_post`/payload references — hard-fail); the assertion ran in this deploy's own gate and printed `os-import-boundary OK`. (2) `os_active` is ABSENT from config (code default False) — the dormant arm flag, gated on: coverage ruling (three-weight table) · in-flight dedup lock shipped · gun certification · four-bar gate · operator word.
- **Shadow operation is logging-only:** `_os_shadow()` wraps in try/except-pass, dedups (tk|site)/300s, and fires at the existing decision sites (placement/repost/walk via the aim-shadow hook; hold reviews in validate_resting_buys). The bot's decision paths are untouched — the hook adds a log line beside them.
- **T4 binding honored before logging starts:** the hold-gate ships IN this build with the two separate readings (quiet-flag vs floor-pace) on every hold_review line — never merged; the floor reading is a prints-proxy in-process with the true-contracts recompute at the nightly rollup (stated in code); the threshold number is Plex's.
- **#12 (decision-input conformance) satisfied by construction:** every os_shadow line carries the full assembled vector (cell, edge, close-ref, three observables, ex-self chain, prints_30m, anchored tts, onset state, qualification stage, anchor_source, liar flag).
- Byte-identity: `os_shadow_enabled=false` → the hook returns immediately; all decision paths identical either way.

## LANE 2 — SETTLEMENT P&L
$0 claimed. Logging-only; no order path exists to claim through.

## Regression watches
`os_shadow` line rate + sites mix · gate output `os-import-boundary OK` on every future deploy · hold_review dual-flag divergence (the Plex threshold dataset) · nightly OS SHADOW line in NIGHTLY_PASS · `os_active` stays absent until the five arm conditions.
