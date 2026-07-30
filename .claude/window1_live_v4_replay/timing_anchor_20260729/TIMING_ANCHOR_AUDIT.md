# Window-1 timing-anchor audit

## Ruling

**The prior five-game timing table is invalid.** Atlas `bottom_t_med_min` is a lead time to a per-leg, volume-derived “−0k onset.” It was treated as minutes after the policy-window left edge. Those are different clocks.

The four tour categories have no bell-anchored timing column: all five-game Atlas pages have `timing_gun = null`, and all selected-category cohort cells have `gun_axis = null`. The depth pass is therefore held exactly as directed; the timing surface did not survive.

There is a second target mismatch: Atlas fits the lowest price **before −0k onset**, while the evaluator reports the lowest price through the guarded bell. In this sample, only 5/10 full-window lows are even before a reconstructable −0k onset; 3 are after it and 2 legs have no −0k onset under the builder law.

Signed error below is predicted wall-clock low minus actual wall-clock low: positive means the prediction was late; negative means it was early.

## Five games on T-minus scheduled start

| Event | Leg | Atlas stored lead (really T−0k) | Actual low vs schedule | If misread as T−schedule: error |
|---|---:|---:|---:|---:|
| KXATPCHALLENGERMATCH-26JUL19HURBIG | BIG | T−318.0 | T−406.2 | +88.2m |
| KXATPCHALLENGERMATCH-26JUL19HURBIG | HUR | T−139.0 | T−79.3 | −59.7m |
| KXATPCHALLENGERMATCH-26JUL19NIKVRB | NIK | T−139.0 | T−51.2 | −87.8m |
| KXATPCHALLENGERMATCH-26JUL19NIKVRB | VRB | T−318.0 | T−316.1 | −1.9m |
| KXATPMATCH-26JUL12LAJVAN | LAJ | T−639.0 | T+637.9 | −1276.9m |
| KXATPMATCH-26JUL12LAJVAN | VAN | T−567.0 | T−454.6 | −112.4m |
| KXWTACHALLENGERMATCH-26JUL16BRAVED | BRA | T−78.0 | T+4.7 | −82.7m |
| KXWTACHALLENGERMATCH-26JUL16BRAVED | VED | T−114.0 | T+37.9 | −151.9m |
| KXWTAMATCH-26JUL20KORJIM | JIM | T−547.0 | T+1082.3 | −1629.3m |
| KXWTAMATCH-26JUL20KORJIM | KOR | T−685.0 | T−472.0 | −213.0m |

The Atlas value is printed in the requested T-minus layout so the coordinate mismatch is visible; it is **not** a valid scheduled-start prediction.

## Three candidate anchors

| Event | Leg | schedule-anchor error | exact-bell-anchor error | left-edge error (old table) | native −0k error |
|---|---:|---:|---:|---:|---:|
| KXATPCHALLENGERMATCH-26JUL19HURBIG | BIG | +88.2 | +178.2 | +244.2 | +15.2 |
| KXATPCHALLENGERMATCH-26JUL19HURBIG | HUR | −59.7 | +30.3 | −261.7 | −89.7 |
| KXATPCHALLENGERMATCH-26JUL19NIKVRB | NIK | −87.8 | −82.8 | −289.8 | −165.8 |
| KXATPCHALLENGERMATCH-26JUL19NIKVRB | VRB | −1.9 | +3.1 | +154.1 | −81.9 |
| KXATPMATCH-26JUL12LAJVAN | LAJ | −1276.9 | +43.1 | −478.9 | −16.9 |
| KXATPMATCH-26JUL12LAJVAN | VAN | −112.4 | +1207.6 | +541.6 | +455.6 |
| KXWTACHALLENGERMATCH-26JUL16BRAVED | BRA | −82.7 | −32.7 | −406.7 | −91.7 |
| KXWTACHALLENGERMATCH-26JUL16BRAVED | VED | −151.9 | −101.9 | −403.9 | −189.9 |
| KXWTAMATCH-26JUL20KORJIM | JIM | −1629.3 | −49.3 | −1015.3 | n/a |
| KXWTAMATCH-26JUL20KORJIM | KOR | −213.0 | +1367.0 | +677.0 | n/a |

Median absolute error by anchor hypothesis: schedule 100.3m; exact bell 66.0m; left edge 405.3m; native −0k 81.9m on the 5 target-comparable legs.

Changing the anchor collapses much of the old 405-minute headline, but no candidate anchor makes the surface valid. Its literal training target is −0k onset, and live_v4 compares it to a start clock.

## Lineage

| Surface/change | Commit date | Relation to honest-clock migration |
|---|---:|---|
| Atlas timing | 2026-07-13T20:18:47-04:00 (`7338fef7`) | C-TREND-PATH v1: the W1 drift atlas (fifth aim design, SHADOW) -- atlas builder (G9 candles tour walk-forward + live-era ITF branded; path quantiles per slice + bottom depth/timing per cat x side x price-cell); trendpath_shadow at discovery places BOTH legs at path prices with the combined-at-path pair check (operator ruling: window-1 value is the thesis; no mid-game completion; flatten-kept only post-bell). |
| Cohort timing | 2026-07-14T20:18:35-04:00 (`ebdb03c9`) | C-W1-LIBRARY v1 Part 2 (intake #3): THE W1-COHORT LIBRARY -- builder cohort pass (cat x price band x fitted vol-terciles -> dip_freq/depth p25-50-75/dip timing/never-wake; axis honesty: timing on the -0k clock MIS-ANCHORED per X-CAL, tts axis na for tour, both named in meta) -> LIBRARY_V1.json refits nightly; dossier surface #14 w1_cohort (SHADOW, GAP-honest, hot-reload); nightly cohort calibration line (predicted dip_freq vs realized) + census rows for w1_cohort/window_phase. |
| Evidence-gun recut | 2026-07-14T22:11:14-04:00 (`c070a158`) | C-TAPE-GATE v1 (two operator words): (1) THE FLATTEN TAPE GATE ARMED, ship-condition MET (founding table: 25 below-basis skips, 23 BAND-CASHED, gate delta +$15.50 REAL -- the honest number vs the +$20.06 wider-cohort headline, stated) -- one input inside the unchanged leash: trailing-15min median >= basis -> SKIP, named flatten_tape_skipped with median+basis on the stamp, one-shot NOT consumed (the tape may turn); nightly self-grading (SKIP/KEEP + skip-cohort realized forward outcomes -- re-earned or revoked). (2) THE TIMING RECUT: builder joins evidence guns from the day-logs; every atlas page gains timing_gun (dual-stamp quantiles + lawful_share); library cells gain gun_axis; LAWFUL_HARVEST_MAP.txt per category; the w1_cohort caveat lifts ONLY where the gun column exists. Depth quantiles untouched; no aim values change. |
| Historical honest-clock restamp | 2026-07-17T18:17:44-04:00 (`dea47904`) | C50: DISPATCH 2 PHASE A — RE-STAMP HISTORY TO HONEST CLOCKS. Corrected event table 12,509 events (state/corpus_events_v2.jsonl: sched_honest=/milestones Sportradar corpus-wide; official=flip-cache 205; onset_est clamped>=sched 4,412; sched-only named 7,892) + THE INDICTMENT (last-consumed old stamps wrong median 155-180 min, 89-97% >30min; session-clock the dominant class, WTA_CHALL 71%; reschedule class split ~24h as Kalshi's own moves; ITF named-unmeasurable-from-snapshots) + riders (W1 LOW full-span with its time "12c @T-14h" on closed cards, lo_ts in the window cut; nightly PRE-HORIZON METER: lows before T-8h + median cents outside the horizon) + ACCEPTANCE WALK BROBAL (old stamp +180min = the whole match fed to the era's fits as premarket; honest W1 lows 24c@T-4.8h / 76c@T-4.4h, corridor 5.6min). v1's own defects caught before publishing (MIN-commence bias, pre-sched onsets, ITF universe hole). Phases B-F queued in order; deferred items named. Engine untouched. |

Atlas and cohort timing were fitted before the July 17 historical clock migration. Later artifact refreshes did not change the builder target from −0k onset.

## Exact bell versus stored schedule (234 games)

| Category | n | median bell slip | p10 | p90 | min | max | earlier / later |
|---|---:|---:|---:|---:|---:|---:|---:|
| ATP_CHALL | 108 | −135.0m | −175.0m | +300.0m | −180.0m | +3205.0m | 84 / 23 |
| ATP_MAIN | 37 | +30.0m | −175.0m | +3050.0m | −180.0m | +3170.0m | 16 / 20 |
| WTA_CHALL | 40 | −132.5m | −180.0m | 0.0m | −280.0m | +135.0m | 36 / 3 |
| WTA_MAIN | 49 | +45.0m | −175.0m | +1380.0m | −180.0m | +1580.0m | 23 / 26 |

Overall: median −90.0m, p10 −175.0m, p90 +1350.0m, range −280.0m to +3205.0m.

The evaluator’s earlier −91-minute median was the **guarded cutoff**, not the bell. Exact rows use a 60-second negative guard, so the actual-bell median is one minute later.

Selected exact-start sources:

- `milestone_shadow_official_start`: 4
- `official_provider_match_start`: 230

## What Kalshi and the local corpus actually store

The current Kalshi Market object exposes `occurrence_datetime`, `open_time`, `close_time`, `expected_expiration_time`, `latest_expiration_time`, deprecated `expiration_time`, `updated_time`, and `settlement_ts`. These do not all mean match start: `close_time` is trading close and `expected_expiration_time` is expected resolution.

For this 804-game corpus, `joined/events.jsonl` retained only one `scheduled_start_exchange_ts`, its `schedule_observed_exchange_ts`, and source `exchange_catalog_occurrence_datetime_current_snapshot`. It did not retain a complete revision history, market close time, or settlement time. `window1_close_cents` is the last lawful true print—not a Kalshi lifecycle close.

`milestone_shadow.remote.jsonl` has point-in-time `sched_ep` values for a subset of events, so some schedule revisions can be seen forensically. It is not complete enough to serve as the 804-game updated-schedule feed.

The 234 exact games use `exact_start_utc` selected from the sources listed above. Their evaluator boundary is that exact bell minus the row’s guard (60 seconds for this class).

## Reading a bell fit live

Let `δ = actual bell − current schedule`. A low fitted at `L` minutes before the actual bell maps to schedule time as:

`T-minus schedule = L − δ`

Because δ is broad and category-dependent, the OS needs the current schedule plus schedule updates and a conditional slip distribution. With only the original snapshot, the translation is probabilistic. There is no honest deterministic bridge.

## Work intentionally not done

No depth calibration, aim frontier, dial change, package, audit, holdout read, or live action was performed. The requested precondition failed: the existing timing surface is not fitted on the actual bell.
