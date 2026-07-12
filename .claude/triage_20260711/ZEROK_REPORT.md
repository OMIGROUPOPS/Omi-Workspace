# −0k — TRUTH-JOIN DRIBBLE-ONSET closing build + the three appended roots

Written 2026-07-12 afternoon ET. Code `476b4326` (gun_scorecard flow-step + conviction_replay join/tick fixes, validated on the 07-11 tape post-pull). Raw evidence: `ZEROK_FORENSIC.json` beside this file. **The clean regrade night runs tonight** — the 6:10 am scorecard and 12:20 am adjudication both ride the fixed instruments — **and the gun-cutover gate reopens on those numbers.**

## THE FLOW-STEP FIX (TRUTH-JOIN DRIBBLE-ONSET kill bar, part 1)

`tape_onset` now requires, at the onset minute: ≥5-of-15 active minutes AND trailing-15 prints ≥ max(8, 3× the search window's FIRST-HOUR baseline per-15-min) AND a 30-minute forward sustain at the same absolute bar. The baseline is the window's first hour (anchor−2h, definitionally premarket), NOT the prior hour — gradual dribble makes every ramp stage a "step" over the stage before it. The forward sustain kills one-window premarket burst clumps (KUBRYS) while thin ~0.5 print/min ITF matches still join.

**Fail-before / pass-after on the 07-11 tape:** the old rule reproduces all 16 SUSPECT deltas exactly (+75.4…+115.4). The new rule: **10/16 become clean joins within ±12 min of the tape-proven fires** (HUEBUT −3.6, MONHER +6.4, DOUROB +0.6, SHIROB −2.7, TYAMON −1.7, ERCHRU −0.7, HOSCIR −1.7, KUBRYS −4.0, SHEYAM +2.4, SMILEY −7.7). The remaining 6 are heavy-premarket ambiguity (premarket hour hotter than the match's first hour) and **every one now QUARANTINES instead of averaging**: MICHEM +53.5 / NAKMAT +17.3 / POLMIY +58.4 / MAKSHO +55.3 by the predates rule; SAGYOD −68.7 by the NEW symmetric `onset_lags_fresh_fire` bound (>20 min lag on a FRESH fire — before this bound it would have AVERAGED IN at −68.7); TABJEB +13.4 grades under the 15-min bar. Regression guard: 11/12 previously-good rows unchanged; MILARS shifts to −35.6 and is safely quarantined by the same new bound (one row off the meter, in the refusing direction). Deliberately NOT tuned further — separating premarket-hotter-than-match tapes on tape alone would be overfitting July 11; the quarantine is the honest answer there.

## (a) THE PERCAT FITTED TRIGGER vs JULY 11's BELL_MISSING ROSTER — cutover evidence, cited per event

(The dispatch said eleven; the 07-11 tape carries **12** `bell_missing` events — all ruled.) Per event, first crossing of the fitted vol30 OPEN threshold (ITF ≥6/30m, CHALL ≥16/30m, MAINS OFF) in [start−2h, start+1h]:

| event | cat thr | honest start | fitted would-fire | verdict |
|---|---|---|---|---|
| SOTCLA | CHALL 16 | 10:59 am | YES +14 min | caught, 4 min after the bell's own miss flag |
| BAXLOK | ITF 6 | 12:00 pm | YES +13 min | caught |
| JOHKLA | ITF 6 | 12:59 pm | YES +12 min | caught |
| SNIMAZ | ITF 6 | 4:59 am | YES −87 min | fires on premarket dribble — UNGATED threshold is not enough |
| FULSOU | ITF 6 | 10:59 am | YES −22 min | premarket-early |
| STATOM | ITF 6 | 4:00 am | YES −63 min | premarket-early |
| MINVOL | CHALL 16 | 12:00 pm | YES −79 min | premarket-early |
| BERBEN / RICHAR / SAMLOP | ITF 6 | 4-5 pm (kalshi_schedule) | NO — vol30 never ≥6 | no real tape near the (lying) schedule anchor; nothing to catch |
| MORSZI / YASGLU | WTA_MAIN | 12:50 / 10:29 am | MAINS-OFF by design | stays uncovered — the mains hole is a design decision on record |

**The honest count: 7 of 12 would-fire — but only 3 timely (+12…+14 min); 4 fire 22–87 min EARLY on the same premarket dribble the truth-join just got cured of.** Cutover evidence cuts both ways: the fitted threshold catches what the bell missed on live tape, but as a NAKED vol30 crossing it needs the bell's start/rise gating (gauge-plus-start composition), or it recreates FERCER-class premature fires. That composition question is on the cutover decision's table, with these 12 rows as its evidence.

## (b) THE 4 LIVE-vs-REPLAY DIVERGENCES — rooted, and two instrument defects fixed on the way

The one-paragraph root: **none of the four was conviction math disagreeing with itself — all four were the COMPARISON instrument.** (1) The replay re-minted trade IDs by fill-order enumeration while live mints at placement; fills arrive out of placement order, so the violation labels cited the wrong trades (live T-0039 = TALPAP-PAP; the replay's row #39 = BOSKAR-KAR — 4/4 labels misnamed). (2) The checker compared the live shadow line (emitted at the decision site, up to the 300 s/site dedup BEFORE the fill — FRAMAR-FRA's was 5 min 56 s early) against the replay posterior AT the fill tick; in-play tape moves conf past the 0.10 tolerance inside that gap — tick alignment, not nondeterminism. Both fixed at `476b4326`: the replay now joins the tape's own `trade_id` stamp, and the checker recomputes the replay posterior at the shadow's own tick. **Rerun on the same 07-11 tape: divergences 4 → 1, labels correct.** The one survivor (T-0045, 0.39 live vs 0.52 replay at the same instant) is REAL and has a named root: live `n_eff` counts only the prints the bot's websocket saw since boot (2.0 there) while the replay reads the full trades CSV plus 0.25-weight mids — the live instrument is under-informed, not wrong. Review item filed: seed composer state from REST tape at boot (the C-TAPE-SEED pattern applied to the composer), own dispatch.

## (c) THE TWO ORGANIC COMBINED-OVER-GOAL BREACHES — the 97 constant's two enforcement holes, class-filed

**WALBAD (WTA_CHALL, 99 = 28+71, 2 shares):** both legs rested from 4:00/4:05 am at targets summing 99 — allowed by design (the cap "binds the SECOND leg's target after the first fills; never a participation filter"). WAL filled at 28 ~8:08:26; the machinery FIRED CORRECTLY — `reaim_sibling_lower` cancelled BAD's 71 bid within a second — but the tape shows `cancel_fill_race`: 2 shares crossed at 71 before the cancel landed. The constant lost a race, not an argument. Also on the tape: the sell on the filled leg was placed BEFORE the sibling cancel — reversing that order shaves the race window.

**MIRMAL (ITF_W, 99 = 87+12):** leg MAL carried an 11–12¢ basis from pre-conception morning buys (~8:00 am, before the 2:00 pm conception stamp). MIR's 87 bid rested and FILLED at 12:52:23 pm as if it were leg1 with a free 10¢ sibling budget — one second later the machinery re-aimed **the already-filled leg** (MAL 12→10, `leg1_basis 87`). Root: **pre-conception fills are invisible to the pair-basis accounting** (the 07-06 autopsy's conception-void hole, now expressed in the combined-cap organ) — MIR should have been capped at ≤ 97−12 = 85 the moment MAL had basis.

Class-filed: **COMBINED-CAP BLIND SPOTS** (CLASS_LEDGER) — instance 1 the race second, instance 2 the conception-void ledger. Remedies named for the operator (resting-sum clamp vs doctrine, cancel-before-exit ordering, pre-conception basis into pair accounting); no build in this dispatch.

## THE DISK, because it interrupted the work

Mid-forensic the volume hit **100% (0 bytes)** — disk-full incident #4. The bot rode it out (C-LOG-ENOSPC held; zero errors). Emergency actions, all inside the standing verified-twin rule: archive-sync's own step-(e) prune machinery run at 2-day retention (**12,667 checksum-verified files deleted, 1.9G**), 186 stale tick CSVs gzipped (ticks 5.3G→2.3G). Disk now 97% — still tight. **The named eater: `data/durable/ws_depth_recorder` (7.2G, ~1.5G/day, files back to Jun 23) has NEVER been in archive_sync's scope** — board item filed to extend the sync + prune to it; tennis.db (16G) remains the standing hog.

## CONSTRAINTS
§0A untouched · one dispatch (analysis instruments only; no bot code, no config, no knob) · both fixed instruments ride tonight's crons — the clean regrade night — and the cutover gate reopens on admissible numbers + the operator's word.
