# COUNTERFACTUAL CHAIN + SCHEDULE-LIE PROOF — 2026-07-09 ~1:10 pm ET (read-only; raw in chain_proof.json)

## PART A — ENTRY→EXIT REACHABILITY CHAIN (asymmetric achievable, conservative prints)
Achievable fill per leg: depth cells (edge_p50>0) worked at `max(own W1 low, W1-close − edge_p50)` — the corpus-median dip bounded by what THIS tape actually printed; JOIN cells (edge=0) at their close level; never better than the tape, never worse than the actual fill. Band re-test from the earliest minute the achievable level printed; existing configured band offsets untouched (0A).

| cat | n | band-reach @ ACTUAL fill | @ ACHIEVABLE fill | Δ | of the never-printed class: converted | touch-after-fill p50/p90 | touched by 1h / 4h |
|---|---|---|---|---|---|---|---|
| ITF_M † | 117 | 73.5% | **82.1%** | **+8.6 pts** | **7/17** | 30m / 145m | 48% / 71% |
| ITF_W † | 107 | 79.4% | **85.0%** | **+5.6 pts** | **5/13** | 35m / 147m | 55% / 77% |
| ATP_CHALL | 35 | 62.9% | 65.7% | +2.9 | 0/2 | 26m / 308m | 46% / 51% |
| WTA_CHALL | 10 | 70.0% | 70.0% | 0 | 0/2 | 36m / 234m | 40% / 70% |

- **VERDICT: 12/34 (35%) of the band-never-printed legs become reachable at achievable entries** — a third of the "exit never came" class is the entry gap, converted by construction, exit surface untouched. The remaining 22 are genuinely unreachable pairs (the band doesn't print even from the doctrine-perfect fill — the pair-selection/timing frontier, not price).
- **The reach-probability value of the entry gap: +6–9 points in ITF** (73.5→82.1 / 79.4→85.0) — the first honest strength read of the existing exit config: at achievable entries the sealed bands reach 82–85% in ITF.
- **The rot curve: band-reach is a fast phenomenon** — median touch 26–36 min after fill, ~half by 1h, plateau by ~4h (71–77% ITF). An entry whose band hasn't printed within the first hour has spent most of its odds — the decay read the dispatch asked for, quantified.

## PART B — THE +121min CLAIM: **KILLED as a generalization; re-diagnosed as a probable feed defect**
145 dual-stamped fires (07-08→09). The category-law decomposition did its job:
- **The bug signature: the ITF lag is ~CONSTANT at every hour of day** — p50 = 120.5–125.2 across hour-slices 03/04/05/06/21/22 (ITF_M) and 01–09 (ITF_W, 100–181). Court queuing would be heterogeneous; **a +2h constant across all times of day in both ITF cats is a timezone/source offset signature in the schedule feed's ITF lane.**
- **124/145 events are clock_liar-flagged** — the liar epidemic itself is largely this same systematic kalshi-vs-te disagreement; sched sources: te_honest 137 / kalshi 8.
- CHALL by contrast: +13 to +63 min, heterogeneous by hour — **plausibly real queuing**, small n.
- Tournament slice: UNAVAILABLE (schedule rows don't join to fire events by name in the current pipeline — named gap); certified-join test: the 33 observed_starts rows joined 0/33 to schedule rows (the global-TE-slate vs Kalshi-slate name mismatch — same gap). Negative tails (−192…−1058) = catch-up fires on already-live matches, anchors stated per row in the raw json.
- **VERDICT: yesterday's "+121 min court queuing" headline does NOT survive its decomposition — the constant offset points at the ITF schedule lane's timezone/source handling, not physics. Queued: ITF schedule-source tz audit with a certified-join fix; no blanket claim stands.**

## PART C — THE 0/500 COVERAGE COUNTER: **BROKEN, not slow — found and fixed**
Trace: collected ✓ (ticks/trades) → belled ✓ (shape_accumulator computes `bell_src` = observed|latchcal_bar at :135–137) → binned ✓ (samples written per (cat,b,t)) → **counted ✗: the write site (:157) never serialized `bell_src` — all 64,644 corpus samples carry `<none>`, so `n_honest ≡ 0` and coverage 0/500 at every weight was STRUCTURAL.** The 4:45 am cron runs fine (today: "folded 213 legs / 0/500 / pushed") — it was counting an empty field forever.
- **Fixed (`739ec32d`, collector-only one-liner, VPS synced): bell_src serializes from the next cron run.**
- **Honest re-forecast:** from tomorrow, latchcal_bar-stamped samples flow at full volume (~200 legs/day) and observed-stamped at the TE-covered pace (~10–15/day, feed now healthy). If n_honest counts observed-only, the 1.0-weight bar stays months out; at the Plex slot's alternate prior-weights (0.5/0.25) coverage moves within days-to-weeks of stamped data. **The bottleneck moves from a broken counter to a RULING: what bell_src qualifies as honest at which prior weight — re-run the derive after 2–3 stamped nights and put the three-weight coverage table in front of the operator.**
