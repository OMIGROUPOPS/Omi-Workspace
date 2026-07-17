# PHASE A — CORPUS RE-STAMP CENSUS v2 (the indictment, scrutinized)

- universe 12509 events · sched resolved 12028 · official actuals matched 205 · onset fallbacks 4412 · sched-only 7892

## |LAST-consumed old stamp − honest sched| by category (min) — the error the fits actually ate
(old stamp = the last commence_time the era's machinery read; Kalshi's own later corrections are NOT billed as fit error — the reschedule class is split out below)
- ATP_CHALL: n=3038 · median 155 · p75 180 · p95 1335 · >30min 93% · >2h 65% · classes {'reschedule': 242, 'session_clock': 1133, 'near': 201, 'residual': 1462}
- ATP_MAIN: n=1097 · median 180 · p75 1260 · p95 2570 · >30min 92% · >2h 67% · classes {'residual': 399, 'near': 91, 'reschedule': 301, 'session_clock': 306}
- WTA_CHALL: n=721 · median 180 · p75 180 · p95 1465 · >30min 97% · >2h 84% · classes {'reschedule': 47, 'session_clock': 510, 'residual': 142, 'near': 22}
- WTA_MAIN: n=1104 · median 180 · p75 960 · p95 1765 · >30min 89% · >2h 62% · classes {'near': 120, 'reschedule': 276, 'residual': 424, 'session_clock': 284}
- ITF_M / ITF_W: old-stamp error UNMEASURABLE FROM SNAPSHOTS (the snapshot collector never carried ITF commence_time); the engine logs' clock_liar lines are the ITF lying-clock record — named, not guessed.

## Kalshi self-corrections (|first − last commence| > 10 min) — the reschedule tail
- ATP_CHALL: n=81 · median 1440 · p75 1620 · p95 2940 (minutes moved)
- ATP_MAIN: n=25 · median 1500 · p75 3000 · p95 4500 (minutes moved)
- WTA_CHALL: n=41 · median 1440 · p75 1620 · p95 2940 (minutes moved)
- WTA_MAIN: n=30 · median 2880 · p75 3000 · p95 3060 (minutes moved)

## sched → right-edge corridor (the tail where the entries live)
- OFFICIAL-ACTUAL corridors (evidence-grade): n=196 · median 0 · p75 0 · p95 0
- ONSET-EST corridors (estimate-grade, poll-cadence resolution, clamped >= sched): n=4412 · median 36 · p75 62 · p95 135

## ACCEPTANCE WALK — KXATPCHALLENGERMATCH-26JUL10BROBAL under honest clocks

- honest sched (milestone/Sportradar): **12:00 PM ET** · evidence onset:
  **12:05 PM** (clamped ≥ sched, estimate-grade) · the OLD stamp the fits
  consumed: **3:00 PM — 180 minutes late** (session-clock class).
- Under the old clock, the ENTIRE MATCH was labeled premarket: from onset
  to the old stamp, BRO printed 25→99¢ and BAL 76→1¢ — ten polls of
  in-play collapse/climb ingested by every era fit as "W1 drift data."
  That is the indictment made flesh: the atlas's premarket paths ate live
  knife moves.
- Under the honest clocks the same tape reads true: **BRO honest-W1 low
  24¢ @T−4.8h (07:12 AM) · BAL 76¢ @T−4.4h (07:38 AM)** — the rider's
  render ("low¢ @T−Xh") exactly; corridor sched→onset = 5.6 min.

## Stamp-hierarchy honesty notes (named, not guessed)

- "official_actual" = the live status-flip cache (205 events, recent era);
  its start_dates are milestone-grade at flip time — only 24 corpus-wide
  stamps are non-round-minute (true second precision). Corridors on this
  class median ~0 min: matches start near their Sportradar slot.
- Past-event /milestones are SCHEDULE-grade (status None, round minutes)
  — they are the honest per-match SCHED clock, not an actual-start record.
- ITF old-stamp error is UNMEASURABLE from snapshots (collector never
  carried ITF commence); the engine logs' clock_liar lines are the ITF
  record. ITF events still enter the corrected table with milestone scheds
  (universe 12,509 includes ITF via tick CSVs + official cache).
- Onset fallback = ≥2 consecutive positive volume deltas at/after sched,
  poll-cadence resolution, clamped ≥ sched (a match cannot start before
  its schedule — P0v3 law applied to history).
