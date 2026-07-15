# C-KOAY-EXHIBIT v1 — the Koay/Yazdani two-leg autopsy (REACH-RECAL exhibit #1)

**2026-07-15, operator live catch.** Read executed ~12:50–1:20 AM ET off the VPS jsonl + the exchange REST tape; the match was STILL IN PLAY at write time (running numbers stamped where they can still move). Event `KXITFMATCH-26JUL14KOAYAZ` (ITF_M): KOA = Koay (underdog), YAZ = Yazdani (leader). Single-cat exhibit — nothing here generalizes past ITF_M without its own evidence (CATEGORY LAW).

## PRIOR ART (C45: grep + cite + delta)

- **REACH VERDICT 07-14** (vault): PRESENCE — aims right, bids GONE (premature latches). This exhibit is that class at case scale, with the reach-law consultation record attached for the first time.
- **C-TAKER-REACH v1 + C-CONVICTED-INSTRUMENTS refit** (`.claude/takerreach/LAW.json`, `integration_bound: evidence_gun`, refit 07-14 `869de031`): the fill judge this read runs on.
- **WINDOW LAW 07-14** (vault): queued the "reach-count recalibration read" — THIS document executes it, KOAYYAZ the named case.
- **W1 LIBRARY 07-14**: MIS-ANCHORED (−0k onset lags the gun on ITF; fitted deep tiers are in-play on the gun axis) — corroborated here to the cent.
- **−0k survivor class 07-11** (`.claude/triage_20260711/ZEROK_REPORT.md`): live n_eff undercount, WS-seen vs full tape — this exhibit proves that class at the reach consultation site.
- **Match-start signal + FERCER 06-19** (vault graves): premature cancels kill resting bids — the KOA leg is the shape on the new machinery (and here the cancel was RIGHT; see Part 2 R2).
- **ADJUDICATION_20260714 §REACH E-vs-A**: lawful E[fills] 44.77 vs actual 0 across 61 legs — the slate-scale divergence this case decomposes.

**Delta:** first per-case decomposition of the reach law's error on a live named pair. The divergence axis is IDENTIFIED — the flow-bucket **input** at placement, not the page depth, not the rate table — and the pair-law stamp's fill-instant blind spot is named as census intake.

## PART 0 — SAFETY (exchange truth, read-only probe `/root/koay_probe.py`)

- **YAZ: NOT naked.** Position 5.00 shares @ 59¢ basis ($2.95 exposure, $0 fees — maker fill). Exit resting on the exchange: sell 5.00 @ 76¢ (basis 59 + band 17), order `3a0e50d4`, created 12:27:35 AM — **the same second as the fill booking** (§0A same-second law held). Confirmed resting at probe time.
- **KOA: no position, no resting order.** The 29¢ bid (order `e3f69f53`) was cancelled **12:33:27 AM by match_live_cancel** (grace armed 12:28:26, 300s; W2 stamp; gun evidence-grade percat_fitted).
- **pair_law_violation: did NOT fire — and correctly per the coded law.** The stamp evaluates at the FILL INSTANT (`live_v4.py:2045`; `selector_drop_enforce: true` confirmed in `config/deploy_v5_live.json`): at 12:27:35 the sibling's deep cast composed — KOA mid ≈36.5 − page depth_p75 21 → deep aim ≈16; 59+16 ≈ 75 ≤ 97 → reachable → no stamp.
- **NAMED BLIND SPOT (census intake for the queued pair-law violation census):** one-sidedness MADE LATER by a lawful cancel is invisible to the stamp — nothing re-evaluates when the 12:33 cancel strands the 12:27 fill. The census must count **cancel-stranded one-sided pairs** beside stamp-flagged ones or it undercounts the class.

## PART 1 — THE TWO-LEG DOSSIER HISTORY (ET 12-hour; sources: `logs/live_v3_20260715.jsonl`, exchange REST trades)

### Koay (KOA, underdog; discovery 44¢)

- **12:26:35** `trendpath_live_aim`: page `ITF_M|underdog|26_50` (n=76, bottom p25/50/75 = 7/13/21) → **path aim 31** (44 − p50 13). Selector TRADE-AT-PATH (best_pct 33.5, tier p75). Pair PAIR-COMPOSED, combined_at_path **69**.
- **reach_law surface at placement:** flow_bucket `quiet`, depth_X 13, rate 0.0/hr, **p_fill 0.000**, bound `evidence_gun`. flow_state surface: prints_30m **1**.
- **12:26:36** placed 31×5 shares (T-20260715-0052) → **12:26:37** `v4_move_repost` to **29×5** (current_price 34, regime r25_34, reference join_bid). One re-aim, downward, pre-fill. **No further re-aim ever fired.**
- **After YAZ filled (12:27:35):** `completion_no_attempt`, reason `leg1_window_open_unset` (governed_by pair97_bound) — **no completion re-aim ran; the 29¢ was the pre-fill path aim left standing** until the cancel. The operator's read is confirmed.
- **Sibling's own economics (RULING_PAIR_ECONOMICS, completion_shadow / M15):** 12:29:27 cross EV **−5.67¢** (basis 46, p_exit_fill 0.733, band 9) → FAIL; 12:38:56 cross EV **−4.53¢** (basis 39) → FAIL. **The sibling's economics never passed, before or after the fill.**
- **Taker completion at the cancel:** `complete_cross_skip` 12:33:27 — sib_fill 59 + ask 39 = basis 98 (cap 100, leg in [5,95]) but **ask_sz 1 < qty 5 → partial-ask skip** (`_try_complete_cross`, the coded law).
- **12:33:27** `order_cancelled` label match_live_cancel (W2, gun evidence-grade).
- **The tape beside it:** KOA's first print EVER = 12:25:22 (37¢). The dog's dip printed **36–37¢ at 12:25:22–12:25:46 — 50 seconds BEFORE the bid existed** (placed 12:26:36). During the bid's whole residency (12:26:37→12:33:27) the lowest print was **41¢ (12:27:20)** — 12¢ above the 29 bid. This is the B3 half-timing shape verbatim: the fader's dip passes before the bid is even standing.

### Yazdani (YAZ, leader; discovery 75¢)

- **12:25:44** `trendpath_live_aim`: page `ITF_M|leader|51_75` (n=91, bottom p25/50/75 = 5/16/31) → **path aim 59** (75 − p50 16). Selector verdict **DROP** (best_pct 4.0 vs the 8% bar) on the leader side alone — but the PAIR composed at 69 ≤ 97, so under the C-PAIR-LAW amendment (DROP-AS-PAIR only where no orientation composes) the pair proceeds. Working as ratified.
- **reach_law surface at placement:** flow_bucket `quiet`, depth_X 16, rate 0.0/hr, **p_fill 0.000**, bound `evidence_gun`. flow_state: prints_30m **1**, harvest 0.0/hr.
- **12:25:45** placed 59×5 shares (T-20260715-0051, W1, resting maker, post-only). `would_skip_walled_post` observe-line rode along (1,455 shares of book depth at 59; the dip swept through the wall exactly as the 06-19 starvation finding says it must).
- **12:26:36** `path_mode_hold`: held 59 against a proposed 60 — the cutover law (the bid rests at its path aim).
- **12:27:00 the tape swept 59:** four prints, 55 shares, taker=no (sellers into the bid) — our 5 shares filled in that sweep; booked 12:27:35, **W1, gun not yet fired. Fill price = posted price = the page p50 aim, to the cent.**
- **12:27:35** exit posted same second (sell 5 @ 76). **12:27:37 THE GUN** (percat_fitted, 11 prints/30m ≥ threshold 6; te_honest null — the TE feed had no sighting; kalshi scheduled start 5:00 AM = **the clock lying by ~4.5 hours**, `clock_liar` stamped 12:27:38).
- **Window phase at fill: W1 — by 37 seconds.**
- **Grade:** leg-level, the entry did its job — path-aim fill at the fitted p50, all dossier surfaces consulted, exit same-second, W1. Pair-level, the ENTRY UNIT failed — one-sided; the pair scoreboard never got its second leg (see Part 0 blind spot).
- **The tape after (the operator's 38-low question):** the corridor NEVER EXISTED on this pair — the gun fired 273 minutes before the lying schedule, so the phase stepped **W1→W2 directly at 12:27:37** (corridor = scheduled→gun is empty when the gun precedes the schedule). W2 chop: 46 @ 12:30:22 (the ~12:30 dip printed 46, not 38); heavy 43/42 12:38:55–12:39:34; **first bottom 41 @ 12:39:45–12:39:56 (~230 shares, taker=no); running low 40 @ 12:51:19 AM** (in-play, still moving at write time). **No 38 print exists on either leg through 1:18 AM** — if the chart shows 38 it is a quote flash or a mid, not a print; the three-observables law grades on prints. So: the low is **W2 by the coded WINDOW LAW**, not corridor — the "on the bell" intuition is right that it came with the gun, but the phase vocabulary says W2 (in-play), and the depth it reached (34–35¢ below discovery) is the page's BEYOND-p75 tier printing in-play — MIS-ANCHORED corroborated.

## PART 2 — THE REACH RECALIBRATION READ (queued at WINDOW LAW; executed here, KOAYYAZ the named case)

What the law was ASKED and what it ANSWERED, against what the tape DID:

| leg | bid (depth) | bucket as consulted | p_fill consulted | honest bucket (exchange tape) | p_fill on honest bucket, gun-bound residency | realized |
|---|---|---|---|---|---|---|
| YAZ | 59¢ (16 deep) | quiet (prints_30m=1) | **0.000** | **warm** (30m count = 3; see AMENDMENT) | **0.010** (ITF_M\|warm rate 0.0105/hr) | **FILLED in 75s** |
| KOA | 29¢ (13 deep) | quiet (prints_30m=1) | **0.000** | open (~15 prints/30m at consult) | **0.346** (rate 25.5/hr × 1.0 min) | no fill (residency low 41¢) |

**AMENDMENT (same night, caught by the outcome replay's own instrument):** the first draft of this table put YAZ's honest bucket at "open / 0.449" — WRONG. At the consultation instant (12:25:44) the trailing-30m REST count was **3** (12:02:41 ×2 + 12:25:18) → **warm**, p_fill 0.010; the burst was 26 seconds old and a 30-minute trailing window dilutes it to near-nothing. The KOA read (open, ~15 prints) stands. **The correction adds a SECOND named limitation, distinct from the input-staleness finding: the 30-minute bucket is a LAGGING instrument at onset** — even with a perfectly honest input, a bid placed seconds into a burst reads warm-at-best. R1 cures the input (KOA-type, and the slate's quiet→open flips); it does NOT cure bucket onset-lag (YAZ-type). A short-window burst term is reach-law REFIT territory — its own dispatch, evidence accruing from tonight's `gauge_src` stamps.

(Full-residency KOA — ignoring the gun bound, 6.83 min — would price 0.945: the bound matters. Rates: `LAW.json ITF_M|open`, arrivals 145.35/hr; `ITF_M|quiet` is literally 0.0 at depth ≥10 — the quiet table cannot price an onset.)

**Where the rate error lives, decomposed:**

1. **THE FLOW-BUCKET INPUT — the error's home.** At the KOA consultation (12:26:36) the gauge read prints_30m=1 → quiet → rate 0.0. The exchange tape had **~15 KOA prints in the prior 71 seconds** (first print ever 12:25:22; the onset burst was already dense). YAZ's read (1) was also under (truth 3). The bot's own gun counter confirms the lag: 11 prints seen by 12:27:37, ~2 minutes after the exchange tape shows the burst. This is the **−0k survivor class (WS-seen vs full-tape n_eff undercount) biting the reach consultation** — the law consulted a stale input at the only moment that mattered, answered 0.000, and the leader filled 75 seconds later.
2. **NOT the page depth.** The leader page's p50 (16 deep) printed at the fill to the cent. The deep tiers (p75 31 and beyond) printed only post-gun — exactly MIS-ANCHORED. The atlas was right where it claims to be right (W1) on this pair.
3. **NOT the rate table.** On the honest bucket the fitted rates price both legs sanely (one 0.45 that filled, one 0.35 that didn't — unremarkable at n=2). Slate-level, the nightly REACH E-vs-A (44.77 expected vs 0 realized lawful fills, 61 legs) remains the law's honesty problem in the OTHER direction — the live consult under-reads (stale bucket → refuses credit), the replay over-credits (expects fills the book never gives our bids). Both directions now have named cases; the recalibration accrues n on both.
4. **The structural corollary (named, not new):** on ITF the discovery moment IS the onset — the evidence gun follows in ~1–2 minutes — so ANY discovery-time bid has ~1–2 lawful minutes, and an honest reach law will price near-zero even with honest buckets. Lawful p_fill mass requires **presence BEFORE the burst** (the W1 thesis). The KOA dip printing 50 seconds before the bid existed is this case's own proof.

**REMEDY, PRICED (nothing ships without the word):**

- **R1 — REST-seed the flow gauge at consultation (the error's home).** Same pattern as C-TAPE-SEED for last-trade age (REST trade reads already proven at boot): refresh the prints_30m counter from exchange-truth trades at dossier/reach consultation time, or a rolling per-conceived-event REST poll (~60s). Flips this exhibit's consulted p_fill 0.000 → 0.35–0.45; no decision-path change beyond the honest input. Cost: one public REST call per consultation (or per event-minute).
- **R2 — the standing REACH-VERDICT proposals (re-place on unlatch; ESPN-status gate)** are NOT advanced by this case: KOA's cancel at 12:33 was CORRECT (the match was genuinely in play; the tape never returned below 41 in W2 through 1:18 AM). Named to keep the file honest.
- **NO aim change proposed.** The page aims graded well here.

## RECORD NOTES (dispatch Part 3, executed)

- **The 12:20 nightly print is now ON the pushed record**: the VPS had committed `ADJUDICATION_20260714.md` (+ FULL_SLATE_REVIEW + RESULTS) at `468536ef` but never pushed (non-fast-forward vs the monitor's race); rebased and pushed — origin advanced `80ce3751 → 738ced4c`, which also carries the packet artifacts (`RULING_PACKET.md` + `PACKET_STATUS.json`, fired 07-14 10:40 AM, `go_state: CUTOVER-DONE`, refreshed 12:40 AM with all three doors PASS at n=495/495/370) and the census AUTO-GAPS BOARD append.
- **The "40-mains-legs" HAS a disk record — not struck:** `ADJUDICATION_20260714.md` §EARLY-CHALL COHORT: "**DEFECT: 40 mains legs pre-T-4h**" (placements across `KXATPMATCH-26JUL14RINTAB-RIN`, `KXATPMATCH-26JUL14NEUPRA-NEU`, `KXATPMATCH-26JUL14NEUPRA-PRA`, `KXATPMATCH-26JUL15BUBHAL-BUB`). Its adjudication (why mains legs took pre-T-4h placements under an ITF/CHALL-scoped window) remains a QUEUED read — the record question is closed, the defect question is not.
- **te_live / gun-feed tripwire (nightly: 250 min stale):** the process is ALIVE and scraping (log current to 1:17 AM; keepalive cron present); the SOURCE shows 0 live matches in the US-midnight lull. The staleness is source-lull semantics, not a wedge — KOAYAZ was gun-caught by the percat fallback as designed (te_honest null on the clock_liar line is the same fact). No restart performed; the evidence did not support one. Transient `database is locked` blips 1:09–1:11 AM (tennis.db writer wart, known, self-recovered).
- Stray untracked files left untouched on the VPS and named: `analyze_bbo.py` (June-10 Pendulum scratch), `analyze_espn_entries.py`, root garbage-named file — a sweep is its own small hygiene item.
