# PART 1 + PART 3 STAGED — gate evidence for Plex's source-level review

> **Provenance note (for the record, per the Plex source ruling):** this evidence doc landed at `53b68438`,
> AFTER the staged code commit `ce38ca8c` it describes — Plex correctly noted it was absent at ce38ca8c.
> Not a blocker (ruled); recorded here. Source ruling: `PLEX_PART1_SOURCE_RULING.md` (verbatim) —
> **ce38ca8c source RATIFIED**; widening dict ratified as staged (MAIN 8h with caveat, flagged for
> shadow-informed retune; X shrinkage below max_observed + one_cron_cycle requires Plex re-review);
> shadow flags arm first, both together; consumer flip is a separate Plex-re-gated config-only diff.
**2026-07-05 · staged commit `ce38ca8c` on blend/kalshi-occ-fallback · NOT armed · bot untouched (PID 3669831 up throughout)**

## What is staged
- **Part 1 (C-PM-CLOCK):** pure helpers `_pm_clock_resolve` / `_pm_window_closed`; flags `per_match_clock_shadow` (observe-only, both clocks logged once per event as `pm_clock_shadow`) and `per_match_clock` (entry-window `time_to_start` in `_route_event` resolves HONEST per-match TE/ESPN start with legacy edges, or FALLBACK placeholder + `PM_CLOCK_WIDEN_SEC` CHALL 4h / ITF 7h / MAIN 8h). Honest resolution via the existing matcher at discovery cadence, cache-only (`_pm_resolve_honest`); `_apply_schedule_data` stamps `fetched_epoch` for the 45-min staleness rule. Spec: `PART1_SPEC.md` (a8314dd7).
- **Part 3 (C-SCALE-GUN shadow):** `_scale_gun_shadow_tick` behind `scale_gun_shadow` — scale-aware burst bar (trailing baseline prints/min × 3, floor `LIVE_TRADE_BURST`), pure reads of `_trade_times`/`_trade_prices`, log-once `gun_scale_shadow`, **no consumer switched**.

## Proof stack (all on the staged SHA)
| bar | result |
|---|---|
| AST sweep (`.claude/ast_pm_clock.py`) | **PASS** — changed = exactly `{__init__, _apply_schedule_data, discover_markets, _route_event}`; added = exactly the 4 helpers; zero removals |
| Tape supremacy / forbidden zone | `_is_match_live`, `_sustained_flow_live/_windows`, `_fv_burst_ready`, `_coarse_window_closed`, `_maybe_set_window_open`, `_completion_target`, `_reconcile_event_start`, matcher — **byte-identical**; grep-proof: zero pm/scale tokens inside liveness bodies; `latch_tape_override` semantics preserved |
| Purity | helpers module-level, no await / state-write / IO per tick; honest resolution only at discovery cadence |
| Staged tests (`tests/test_pm_clock.py`, AST-extract real bodies) | **24/24 PASS** (locally AND inside the VPS smoke env) |
| Byte-identical-OFF | OFF-path expressions reduce to legacy (`tts − 0 > K`, `max(TAIL,0)`, `_pm_mode None` ⇒ original `_coarse_window_closed` call verbatim); honest mode ≡ legacy `_coarse_window_closed(coarse=False)` across the edge sweep |
| Existing suites (staged file) | kalshi_occ, kalshi_occ_observe, schedule_trust, t51_match_live, e113, bound_ruling, latch_walkcap, option_c, participate_clean, fv_burst — **all green**. `test_sustained_flow` + `test_live_detect_floor` fail **identically at HEAD** (pre-existing environmental: module-import / stale fixture), verified via stash-baseline |
| Lint gate (`deploy/lint_gate.py`) | **PASS** (local + VPS staging clone) |
| Smoke replay (gate law, isolated) | **PASS** — full LiveV3, real deploy config (staged flags verified ABSENT = OFF), paper-forced, recorded slate replay in `/root/smoke_env` rebuilt from a **staging clone at ce38ca8c** (live repo read-only): 137 v4 placements, 277 orders, 256 staircase holds, 56,313 dog-leg book states routed, zero ERROR_EVENTS |

## Arming plan (pending Plex ratification — nothing moves without it)
1. `per_match_clock_shadow: true` + `scale_gun_shadow: true` first (observe-only night; grade `pm_clock_shadow` deltas + `gun_scale_shadow` agreement vs the honest clock).
2. Only after shadow validates: `per_match_clock: true` through `deploy/deploy_live_v4.sh` (the ONLY restart path), one change at a time.
3. Widen table X is pre-registered as adjustable at this gate (one dict).

## Open items
- **PLEX_REANCHOR_RULING.md body still owed** — the relay dropped it twice (literal placeholder arrived both times); the reserved slot (0a17ce03) stands, operative constraints captured in operator's words.
- Shadow-population note: `pm_clock_shadow`/`gun_scale_shadow` fire from the routing observe block, so events already PROCESSED before flag-arm won't emit; fresh slate coverage is complete.
