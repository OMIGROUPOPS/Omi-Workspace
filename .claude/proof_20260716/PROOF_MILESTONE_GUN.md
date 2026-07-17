# OUTCOME PROOF — C-MILESTONE-GUN v1 (gun source 9: milestone_official)
Proven SHA: **602b04c5** (live_v4.py + deploy_v5_live.json + knob citations)
Operator word: **decision ⑯ = YES** (dispatch 07-16, verbatim: "MILESTONE GUN, ARMED (operator word given: ⑯ = YES)").
Prior art (C45): decision ⑯ evidence chain — C-CORRIDOR-TRUTH part 6 investigation (status vocabulary + Sportradar second-precision start_date) → C-MILESTONE-SHADOW (*/15 shadow, three-clock table, first medians ms−fp +7.8 min) → C-OFFICIAL-BELL regrade (16 fills convicted that the estimate clocks missed).

## Lane 1 — per-game would-have-fired replay (today's shadow tape vs our actual guns)
158 tracked events observed STARTED by the milestone feed (status live/P) across 07-15/16:
- **30 events: milestone start EARLIER than our first gun fire — source 9 sweeps resting bids sooner.** Top rows (event · milestone start · our gun · delta): CHACHA2 4:13 AM vs 5:37 AM (+84.0 min) · PASSTR 4:40 vs 5:06 (+26.0) · KOIKUR 2:16 PM vs 2:39 PM (+23.8) · PLUWAG 5:55 vs 6:10 (+14.2) · GRESAN 3:35 PM vs 3:45 PM (+10.0) · ZHAZHA2 (+9.3) · ZHASHI (+7.3) · JACROW (+6.8) · BYNLON (+6.0). (CARPAL's +1315 min excluded from the headline — cross-day join artifact in the shadow row, filed for the nightly table's day-keying.)
- **117 events: milestone later than our gun — first-fire-wins keeps the existing source; ZERO behavior delta** (the new source only logs gun_source_confirm through the existing machinery).
- **0 events: milestone-started with NO gun of ours** on this window (the bell_missing family this source closes going forward).
Convicted-fill tie-back: today's official-bell regrade convicted 16 fills that landed post-official-start under estimate clocks — the exact fills a milestone-fired sweep cancels before they can happen (e.g. KOIKE filled 2:39 PM window vs official start 2:16 PM: the +23.8 min sweep gap IS the conviction window).

## Lane 2 — behavior isolation
- The entire source is gated on `milestone_gun_enabled` (config; DECREED knob, cited). Flag off = the block never executes = byte-identical behavior.
- Boot safety: 6h age window (same bound as tape_flow/price_divergence — stale events never mass-fire) + future-start distrust (a "started" status whose start_date sits >300s in the future is skipped).
- Fire path is THE NORMAL PATH: `_gun_stamp(et, "milestone_official", …)` → `_events_live` → existing match-live sweep; evidence-grade 60s grace (the tape_flow class) at both grace sites. The official bell (`start_date`, second precision) is recorded in the gun_fired detail at fire time.
- 429 budget: one public GET per UN-GUNNED tracked event per 90s (`milestone_gun_poll_sec`), transient errors log once/hour and retry next cadence; the */15 shadow cron continues unchanged so the nightly three-clock table proves the arming honest.

## Gate
lint + smoke via deploy/deploy_gate.sh (this file is OUTCOME_PROOF; OUTCOME_PROOF_SHA=602b04c5).
