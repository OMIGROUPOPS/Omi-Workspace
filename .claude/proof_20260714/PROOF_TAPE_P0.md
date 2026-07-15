# PROOF — C-READ-THE-TAPE v2 Part 0 (halt triage; the boot race, dead)

**Candidate SHA: 8e1ac67d.** Defect class, gate-exempt from config freezes; full gate.
**Adjudication, by timestamp: BOOT RACE.** At the 20:14 shutdown→20:16 boot, `_drain_replay` re-placed drained bids while the live-detection stamps were still landing (DEMSAC: clock_liar stamp 20:16:17, bid re-placed 20:16:18; `fire_src: null` on all 7 audit rows = the state's stamps hadn't a named writer visible to the auditor). The chokepoint had nothing to refuse against at the placement instant. **Zero of the 7 filled. All 7 swept by hand (200s across the board; post-sweep resting buys on the 7: 0). The 20:40 boot audit armed the conception halt and HELD it for ~10 minutes until the reaudit passed at 8:50:44 PM — the halt worked, exactly as built.**
**The fix (this SHA):** (1) ordering law — `_drain_replay` refuses to run until `_gun_rebuild_done` AND `_live_scan_done` (one full gun-source pass) are set; a not-ready replay defers, NAMED (`drain_replay_deferred`), and retries at halt-clear/cadence as before. (2) The belt: a manifest entry whose event has ANY gun state or `_events_live` membership is `refused_gun_fired`, named with the source. (3) The auditor prints the raw fire entry whenever source is null — the next sourceless stamp names its own writer.
**Lane 2:** subtraction and ordering only; no aims, postures, or prices change; the replay's refusals are the same refusals the chokepoint would issue a second later.

## Deploy gate
[1/2] lint PASS · [2/3] smoke (gate-run) · [3/3] this file, OUTCOME_PROOF_SHA=8e1ac67d · [4/4] C50 rides the C-READ-THE-TAPE close-out · [5/5] constraints surface.
