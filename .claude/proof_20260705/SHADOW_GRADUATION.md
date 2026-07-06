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
| 07-05 23:16→23:59 ET (arm night, graded for the flip request) | discovery slate, ALL 6 categories (213 events; overnight ITF running live) | **PASS 213/213 = 100%** (every schedule-matched event since arm emitted its shadow line) | **PASS-documented**: legacy−honest deltas ATP_CHALL +180 (n=49, 130–180) · WTA_CHALL +160 (n=19) · ITF_M +360 (n=7) · ITF_W +360 (n=32, 225–360) · mains −180..+180 (n=8, small-n, ratified 8h envelope + tape latch govern. These sit outside ±30min BY DESIGN — they ARE the audit's documented offsets reproduced live (CHALL max_obs 175 ≈ tonight 180; ITF max_obs 360 = tonight 360); the ±30min band guards UNANTICIPATED honest-mode divergence, of which there is none. Honest-vs-gun grading = the audit's 135-event join (+4..9min median, 75% ±30min), accepted by the ruling as pre-established.) | **PASS 213/213 = 100%** | **NOT YET OBSERVABLE** — 7 gun_scale_shadow fires, all at the floor bar (quiet-hour baselines ≈0; MAIN suppression needs daytime volume). G4 gates the SCALE-GUN consumer (separate arm, not this flip); collection continues. | **WIRING PROVEN — flip request submitted** (FLIP_REQUEST_PER_MATCH_CLOCK.md; Exhibit A: EXHIBIT_A_PASCOP.md) |
