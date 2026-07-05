# SHADOW GRADUATION SCOREBOARD — pm_clock_shadow + gun_scale_shadow (Plex conditions, tracked nightly)

**Armed:** `c2a59a62` (shadow flags only, Plex source ruling `PLEX_PART1_SOURCE_RULING.md`). Window: ≥1 full
US-daytime slate covering ALL categories (2 if light). Rollback rule: ANY flagged symptom → both shadows off
(config flip through the gate), source review re-opens.

## Graduation criteria (Plex, verbatim thresholds)
| # | bar | how graded |
|---|---|---|
| G1 | **pm_clock_shadow coverage ≥95%** of placement-pipeline events | events emitting pm_clock_shadow ÷ events reaching the routing pipeline with a resolved start (grep `pm_clock_shadow` vs routed-event census per slate) |
| G2 | **no HONEST-mode delta outside ±30min** without a documented category reason | pm_clock_shadow `delta_min` distribution per cat; any \|delta\|>30min in mode_if_armed=honest gets a per-event writeup or fails |
| G3 | **sched_fresh ≥90%** | share of pm_clock_shadow rows with sched_fresh=true |
| G4 | **MAIN legacy-would-fire-but-shadow-suppresses observed** | gun_scale_shadow on _MAIN: cases where recent≥LIVE_TRADE_BURST (legacy bar) but < scaled_bar (logged suppression implicit in fire timing), and/or shadow fires later than the legacy latch_ts |
| G5 | MAIN widen X (8h, ruled-with-caveat) | collect honest-vs-placeholder deltas on mains to retune X — shadow-informed, Plex re-review required for any shrinkage below max_observed + one cron cycle |

## On pass
Consumer flip = `per_match_clock: true` ONLY (config-only diff), its own C46 two-lane doc, **back to Plex for
re-gate**. Scale-gun consumer stays separate and keeps collecting — never bundled.

## Nightly log (append per slate)
| date | slates covered | G1 | G2 | G3 | G4 | verdict |
|---|---|---|---|---|---|---|
| (pending first slate) | | | | | | |
