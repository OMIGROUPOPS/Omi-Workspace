# EXHIBIT A — PASCOP (Pastoric vs Coppez, W35 Buzau ITF_W, KXITFWMATCH-26JUL06PASCOP)
**One live event, captured in real time on 2026-07-05 ~23:20 ET, showing exactly the gap the flip closes.**

| clock | value | consequence |
|---|---|---|
| Card/legacy start (`kalshi_schedule_primary`, held all day, 4 schedule_match logs) | **Jul 6 08:00 EDT** | legacy T-240 entry window opens **04:00 EDT** |
| Honest start (TE, `direct_6char` join, sched_fresh, `pm_clock_shadow` 23:18:22) | **Jul 6 02:00 EDT** | honest T-240 window opened **22:00 EDT tonight** |
| Clock error | **+360 min exactly** | **the legacy window opens TWO HOURS AFTER the true start** |

**The money is visibly happening while the consumer path is blind:**
- Tape (Kalshi REST, verified at capture): the COP leg's **last 200 prints range 66→90 (a 24¢ swing band), latest 87** — a live, actively-repricing premarket running right now inside the honest window. (Operator's live read: ~$19k volume with 80/20 swings — consistent with the tape range; my markets-endpoint field read returned nulls on the volume keys, so the print evidence is what this exhibit certifies.)
- `gun_scale_shadow` fired on PASCOP at 23:19 — **burst 12 prints/60s at legacy tts +521 min** — the premarket-volume class that trips the fixed gun hours early on the lying clock.
- **Zero bids resting or planned**: the bot's legacy window is 4.5h away from opening, and when it opens (04:00) the match will have been OVER or in its final sets (started 02:00). This is the ITF-no-premarket finding as a single live frame: the premarket exists — we schedule ourselves out of it.
- **Spec warts handled correctly, live:** schedule.json mislabels this Buzau ITF as `WTA_MAIN` (the frozen ESPN/TE category wart) — the shadow line carries the bot's own category `ITF_W`, exactly as PART1_SPEC mandates (never consume the schedule's category field).

**Under the flip (`per_match_clock: true`):** HONEST mode, legacy edges on the 02:00 clock — window open
since 22:00, both legs' bids resting through this exact 66–90 premarket, T-15 lock at 01:45, tape latch
untouched as the real-start governor. Under fallback (had the join missed): today's exact behavior + the
ratified 7h ITF widening — never worse than status quo.
