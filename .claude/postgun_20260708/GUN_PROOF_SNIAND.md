# GUN PROOF — SNIAND, one match mapped (KXITFMATCH-26JUL09SNIAND, Snitari I. vs Andreescu S., ITF_M)

**The +933-minute lying-clock case: both schedule clocks said tomorrow morning; the scoreboard said NOW; the tape said nothing at all.** Fire class: **CATCH-UP** (match already in-play when the fused listener booted 5:25 pm — a state-sync fire, excluded from the ±3-min FRESH bar by the pre-registration). All times ET, 2026-07-08. Raw series: `GUN_PROOF_SNIAND.json`. **This document is the template for every Part-3 proof row.**

## The event timeline

| time (ET) | source | what happened |
|---|---|---|
| (standing) | **legacy kalshi schedule** | start_time **2026-07-09 9:00 am** (`kalshi_schedule_primary`; kalshi_occ delta 0.0 — occurrence agrees) |
| (standing) | **honest schedule read** | `honest_start` **2026-07-09 3:00 am**, status "scheduled" — the honest matcher found a row and it ALSO lies LONG by ~half a day |
| 3:14:43 pm | horizon gate | `conception_horizon_defer` (tts 11.75h) — the T-8h bound counting DOWN to conceiving bids at ~7:00 pm tonight **on a match already in play** (the EKSLUX knife, queued to repeat) |
| ~5:03 pm | match state | match in play by now (scoreboard first sighting; true start unknown — before the feed resumed) |
| **5:03:37 pm** | **te_scoreboard (the trigger)** | `observed_starts` banks Snitari/Andreescu in-play (first sighting; the feed had just been resurrected — down since 07-07 7:20 pm) |
| 5:25:04 pm | deploy | fused-gun build boots (PID 1551401); listener starts |
| 5:25:46 pm | clocks, still lying | `pm_clock_shadow`: legacy Jul-9 9:00 am / honest Jul-9 3:00 am; `conception_horizon_defer` tts 9.57h |
| **5:26:12 pm** | **GUN FIRED** | `gun_fired` source=**te_scoreboard**, match_how=**both_legs** (SNI+AND), tts_legacy **+933.8 min**, tts_honest **+573.8 min**, feed_lag 1355s (row predates the listener → CATCH-UP) |
| 5:26:12 pm → | enforcement | event in `_events_live`; **any buy on either leg now dies at the chokepoint (`gun_buy_refused`)**; external-truth fire is exempt from the tape-quiet unlatch (tts>floor + silent tape would have unlatched a tape gun) |
| **6:02:38 pm** | **independent witness (not consumed by the gun)** | TE /live/ page: "Snitari I. - Andreescu S. **5-1**" — mid-match, 36 min after the fire (fetched + banked in the json) |

## The minute tape, ±45 min around the fire (both legs — identical, one book)

| minute | SNI bid/ask/last | AND bid/ask/last |
|---|---|---|
| 4:41 pm | 6 / 94 / — | 6 / 94 / — |
| 4:53 pm | 6 / 93 / — | 6 / 93 / — |
| 4:59 pm | 6 / 92 / — | 6 / 92 / — |
| 5:17 pm | 6 / 92 / — | 6 / 92 / — |
| 5:25 pm (boot) | 6 / 92 / — | 6 / 92 / — |
| **5:26 pm (FIRE)** | **6 / 92 / —** | **6 / 92 / —** |
| 5:46 pm | 6 / 92 / — | 6 / 92 / — |
| 5:52 pm | 7 / 94 / — | 7 / 94 / — |
| 5:59 pm | 8 / 94 / — | 8 / 94 / — |

**ZERO prints the entire window (last-traded column empty throughout; 86–88¢ spread).** This is the silent lattice from HOURLY_APPENDIX/EARLY_CANVAS, live: the tape latch (≥burst prints/60s, two-stage) is STRUCTURALLY incapable of firing here — not late, *impossible*. The only in-play echo the tape ever gives is a 2¢ bid drift twenty-five minutes after the fire. POST_GUN_FORENSIC's ITF 73–83% latch-silent class, photographed.

## Grace + our orders in the window
- **Our orders: NONE existed and none were attempted** — the horizon gate had (correctly, by accident of its lying anchor) deferred conception all afternoon; post-fire, the `gun_buy_refused` chokepoint makes the block principled instead of accidental. No cancels, no holds, no refusal events fired (nothing tried to buy).
- **Grace: N/A** — grace protects resting bids at the fire; there were none. (Had the horizon deferral expired at ~7:00 pm as scheduled, the old regime CONCEIVES fresh bids into a 5-1 in-play match with both clocks reading premarket — the gun fire 94 minutes earlier is exactly what now prevents it.)

## What this row proves
1. **The gun's fourth clock-independence claim is live:** with legacy AND honest schedules wrong by 574–934 minutes and a print-free tape, only the scoreboard source knew — and it fired within 78s of the listener's first poll (feed row predated boot: CATCH-UP by definition).
2. **The buy chokepoint closed a real, scheduled leak:** the horizon deferral was due to expire ~7:00 pm on this event; conception would have posted bids into a live match. `gun_buy_refused` now stands in front of it for the event's life.
3. **Fire-class labeling is necessary for honest grading:** grading this fire's "lag" vs the 5:03 scoreboard row (23 min) would measure the deploy time, not the gun — hence CATCH-UP fires carry their own column and the ±3-min pass bar applies to FRESH fires only.
