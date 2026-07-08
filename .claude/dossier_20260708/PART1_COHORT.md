# PART 1 — FREEZE-BOOT LINEAGE COHORT (fills 2026-07-07 23:12 ET → 2026-07-08 11:45 ET)

Generated 2026-07-08 ~12:3x ET. Ground truth = Kalshi portfolio fills dump (`/root/naked_sweep_20260708/fills_recent.json`, buy/yes maker bids), cross-checked vs `logs/live_v3_20260707.jsonl` + `live_v3_20260708.jsonl`. Bot timeline: freeze boot 23:12 ET Jul 7 → disk-full CRASH 02:52:22 ET Jul 8 → dead → resurrected 11:30:16 ET Jul 8. **n = 293 filled legs.**

## Conventions used (same classifier/rubric as sweep_20260707, adapted for tonight's evidence holes)
- **Honest clock**: NO observed_start exists anywhere tonight; only volume_burst latches (and none 02:52→11:30 because the bot was dead). Windows therefore use, in priority: live latch (`match_live_detected`) > **tape-onset** (first ≥20 prints in 15 min on the full Kalshi API trade tape — a reconstructed latch) > kalshi schedule clock (sanity-guarded: dropped if start ≥ settle time or >8h before it). Flags: `W1?` = before all anchors; `W2~` = after tape-onset (onset-derived, latch-grade evidence); `W2` = after a live latch; `grace/corridor?` = between anchors; `window-uncertain` = no usable anchor.
- **Own cheapest fillable W1 point**: lowest **sell-flow print** (taker_side=no — proof a resting bid at that px filled) on the Kalshi API tape, pre-start (pre-anchor), since conception of our order where known. `sf`=sell-flow print, `pr`=any print, `ask`=min ask from local ticks. Local tick/trade recorders also died 02:52→11:30 ET, so API trade prints are the primary tape.
- **DIVOT/REPRICE/NO_UNDERCUT/AMBIG**: post_fill_move.py classifier verbatim where local tick tape covers the fill; a **trades-only proxy (starred, e.g. REPRICE\*)** where the fill sits in the 02:52→11:30 tape hole (no order-book undercut evidence: DIVOT\*=prints dip below fill then recover ≥fill within 30m; REPRICE\*=prints ≤fill−3 and last-30m print < fill; NO_UNDERCUT\*=no print below fill within 60m).
- **Grade (per-leg, this cohort)**: S = gap≤4 **and** cashed pregame/corridor; A = gap≤4 and cashed in W2, or cashed pregame with gap≤8; B = cashed profitably otherwise **or** settled winner (rode to settlement — B3-wing); C = open, exit resting, band within 5c or band printed post-fill; D = open with band far/untouched, or exited at a loss; F = settled loser (naked leg rode to 0). `?` suffix = window-uncertain clock. NOTE: with the bot dead 8.6h most of this cohort could never be exited — grades B/F here are overwhelmingly the *pair-rode-to-settlement* shape, not managed outcomes.
- **MECHANICAL**: naked(crash-orphan) = fill 02:52→11:30 ET on an orphaned resting bid; naked(wave2-adopt) = the 5 named second-wave adoptions after 11:30 (DAMARN-ARN/DAM, PDARIB-RIB, MAXABA-MAX, ISHCRO-CRO); frac-qty = fractional share qty. Exchange prices used everywhere (bot-ledger exit prices disagreed on adopted exits, e.g. LUENAT-LUE ledger 65 vs exchange 85 taker-sweep).

## Cohort table (one row per filled leg; sorted by category, then fill time)

| leg (ticker) | cat | fill ET | window | fill px | own W1 low (px @ t, src) | gap | class | posture@post | walks | exit state now (+band dist) | grade | MECH |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 26JUL08DEMGIU-GIU | ATP_CHALL | 07/08 02:18 | W1? | 66 | 66 @ 07/08 02:18 (sf) | +0 | NO_UNDERCUT | join | 0 | EXIT_FILLED @85 (W2, maker) +19.0c/sh | A? | — |
| 26JUL08SCHDJE-SCH | ATP_CHALL | 07/08 02:57 | W1? | 32 | 32 @ 07/08 02:57 (sf) | +0 | NO_UNDERCUT* | join | 0 | SETTLED no -32.0c/sh | F | naked(crash-orphan) |
| 26JUL08DEDSVR-SVR | ATP_CHALL | 07/08 04:56 | W2~ | 65 | 64 @ 07/07 18:34 (pr) | +1 | REPRICE* | join | 0 | SETTLED no -65.0c/sh | F | naked(crash-orphan) |
| 26JUL08ZHODE-ZHO | ATP_CHALL | 07/08 05:00 | W1? | 81 | 81 @ 07/08 05:00 (sf) | +0 | NO_TAPE* | join | 1 | SETTLED yes +19.0c/sh | B | naked(crash-orphan) |
| 26JUL08DEDSVR-DED | ATP_CHALL | 07/08 05:09 | W2~ | 35 | 35 @ 07/08 03:47 (sf) | +0 | DIVOT* | join | 0 | SETTLED yes +65.0c/sh | B | naked(crash-orphan) |
| 26JUL08DEMGIU-DEM | ATP_CHALL | 07/08 05:39 | W2~ | 31 | 34 @ 07/08 01:57 (pr) | -3 | REPRICE* | join | 16 | SETTLED no -31.0c/sh | F | naked(crash-orphan) |
| 26JUL08CHIBAR-BAR | ATP_CHALL | 07/08 06:10 | W1? | 14 | 14 @ 07/08 02:41 (sf) | +0 | REPRICE* | join | 0 | SETTLED no -14.0c/sh | F | naked(crash-orphan) |
| 26JUL08ZHODE-DE | ATP_CHALL | 07/08 06:11 | W2~ | 18 | 20 @ 07/08 02:22 (pr) | -2 | DIVOT* | join | 0 | SETTLED no -18.0c/sh | F | naked(crash-orphan) |
| 26JUL08RIBDOD-DOD | ATP_CHALL | 07/08 06:40 | W2~ | 55 | 56 @ 07/08 02:42 (pr) | -1 | DIVOT* | join | 0 | SETTLED yes +45.0c/sh | B | naked(crash-orphan) |
| 26JUL08SCHDJE-DJE | ATP_CHALL | 07/08 06:42 | W1? | 66 | 66 @ 07/08 06:42 (sf) | +0 | REPRICE* | join | 0 | SETTLED yes +34.0c/sh | B | naked(crash-orphan) |
| 26JUL08RIBDOD-RIB | ATP_CHALL | 07/08 06:46 | W2~ | 44 | 45 @ 07/08 02:42 (pr) | -1 | DIVOT* | join | 0 | SETTLED no -44.0c/sh | F | naked(crash-orphan) |
| 26JUL08STALOG-STA | ATP_CHALL | 07/08 06:49 | W1? | 52 | 38 @ 07/08 07:07 (sf) | +14 | REPRICE* | join | 0 | SETTLED no -52.0c/sh | F | naked(crash-orphan) |
| 26JUL08SIMMID-SIM | ATP_CHALL | 07/08 06:55 | W2~ | 30 | 31 @ 07/08 03:44 (pr) | -1 | REPRICE* | join | 0 | SETTLED no -30.0c/sh | F | naked(crash-orphan) |
| 26JUL08SIMMID-MID | ATP_CHALL | 07/08 06:56 | W2~ | 68 | 68 @ 07/08 05:30 (sf) | +0 | DIVOT* | join | 0 | SETTLED yes +32.0c/sh | B | naked(crash-orphan) |
| 26JUL08STALOG-LOG | ATP_CHALL | 07/08 07:46 | W2~ | 46 | 48 @ 07/08 02:42 (pr) | -2 | DIVOT* | join | 0 | SETTLED yes +54.0c/sh | B | naked(crash-orphan) |
| 26JUL07TOMSHI-TOM | ATP_CHALL | 07/08 11:18 | W2~ | 63 | 58 @ 07/07 04:15 (ask) | +5 | AMBIG | join | 0 | OPEN, exit resting @82; band dist +18 (last 64) | D | naked(crash-orphan) |
| 26JUL08DAMARN-ARN | ATP_CHALL | 07/08 11:31 | W2~ | 62 | 58 @ 07/08 06:44 (pr) | +4 | AMBIG | join | 0 | OPEN, exit resting @80; band dist +18 (last 62) | D | naked(wave2-adopt) |
| 26JUL08PDARIB-RIB | ATP_CHALL | 07/08 11:32 | W2~ | 20 | 32 @ 07/08 02:51 (sf) | -12 | REPRICE | join | 0 | EXIT_FILLED @26 (W2, maker) +6.0c/sh | A | naked(wave2-adopt) |
| 26JUL08DAMARN-DAM | ATP_CHALL | 07/08 11:35 | W2~ | 37 | 40 @ 07/08 10:42 (sf) | -3 | AMBIG | join | 0 | OPEN, exit resting @45; band dist +6 (last 39) | C | naked(wave2-adopt) |
| 26JUL08MELAND-MEL | ATP_CHALL | 07/08 11:41 | window-uncertain | 65 | 66 @ 07/08 11:08 (sf) | -1 | AMBIG | join | 0 | OPEN, exit resting @84; band dist +19 (last 65) | D | — |
| 26JUL08VANSEL-VAN | WTA_CHALL | 07/08 04:44 | window-uncertain | 38 | 39 @ 07/08 04:44 (sf) | -1 | NO_TAPE* | join | 0 | OPEN, exit resting @45; band dist +5 (last 40) | C | naked(crash-orphan) |
| 26JUL08ARABAD-BAD | WTA_CHALL | 07/08 04:46 | W1? | 76 | 74 @ 07/08 05:10 (sf) | +2 | AMBIG* | join | 0 | SETTLED yes +24.0c/sh | B | naked(crash-orphan) |
| 26JUL08RADPUT-PUT | WTA_CHALL | 07/08 04:56 | W2~ | 66 | 67 @ 07/08 04:16 (pr) | -1 | REPRICE* | join | 0 | SETTLED yes +34.0c/sh | B | naked(crash-orphan) |
| 26JUL08RADPUT-RAD | WTA_CHALL | 07/08 05:06 | W2~ | 33 | 34 @ 07/08 01:52 (sf) | -1 | DIVOT* | join | 0 | SETTLED no -33.0c/sh | F | naked(crash-orphan) |
| 26JUL08BULROM-ROM | WTA_CHALL | 07/08 05:07 | W1? | 78 | 71 @ 07/08 05:10 (sf) | +7 | REPRICE* | join | 0 | SETTLED yes +22.0c/sh | B | naked(crash-orphan) |
| 26JUL08KRAHEN-KRA | WTA_CHALL | 07/08 05:08 | W2~ | 73 | 74 @ 07/08 04:00 (sf) | -1 | NO_UNDERCUT* | join | 0 | SETTLED yes +27.0c/sh | B | naked(crash-orphan) |
| 26JUL08MASCUR-CUR | WTA_CHALL | 07/08 05:09 | W2~ | 26 | 28 @ 07/08 01:58 (pr) | -2 | DIVOT* | join | 0 | SETTLED yes +74.0c/sh | B | naked(crash-orphan) |
| 26JUL08KRAHEN-HEN | WTA_CHALL | 07/08 05:11 | W2~ | 24 | 25 @ 07/08 01:28 (pr) | -1 | REPRICE* | join | 0 | SETTLED no -24.0c/sh | F | naked(crash-orphan) |
| 26JUL08MASCUR-MAS | WTA_CHALL | 07/08 05:15 | W2~ | 71 | 72 @ 07/08 04:00 (sf) | -1 | REPRICE* | join | 0 | SETTLED no -71.0c/sh | F | naked(crash-orphan) |
| 26JUL08BULROM-BUL | WTA_CHALL | 07/08 05:16 | W2~ | 20 | 21 @ 07/08 01:28 (pr) | -1 | REPRICE* | join | 0 | SETTLED no -20.0c/sh | F | naked(crash-orphan) |
| 26JUL08JONJEA-JON | WTA_CHALL | 07/08 06:16 | window-uncertain | 50 | 51 @ 07/08 04:38 (pr) | -1 | NO_TAPE* | below_chain | 0 | OPEN, exit resting @61; band dist +12 (last 49) | D | naked(crash-orphan) |
| 26JUL08LEPKOR-LEP | WTA_CHALL | 07/08 06:16 | W1? | 28 | 28 @ 07/08 06:16 (sf) | +0 | NO_UNDERCUT* | join | 0 | SETTLED yes +72.0c/sh | B | naked(crash-orphan) |
| 26JUL08WALLAB-LAB | WTA_CHALL | 07/08 06:47 | W2~ | 7 | 8 @ 07/08 03:23 (pr) | -1 | REPRICE* | join | 0 | SETTLED no -7.0c/sh | F | naked(crash-orphan) |
| 26JUL08WALLAB-WAL | WTA_CHALL | 07/08 06:48 | W2~ | 91 | 92 @ 07/08 05:10 (sf) | -1 | NO_UNDERCUT* | join | 0 | SETTLED yes +9.0c/sh | B | naked(crash-orphan) |
| 26JUL08TUBWER-WER | WTA_CHALL | 07/08 06:50 | W2~ | 43 | 44 @ 07/08 03:12 (pr) | -1 | DIVOT* | join | 0 | SETTLED no -43.0c/sh | F | naked(crash-orphan) |
| 26JUL08ARABAD-ARA | WTA_CHALL | 07/08 06:53 | W2~ | 23 | 24 @ 07/08 04:46 (pr) | -1 | REPRICE* | join | 0 | SETTLED no -23.0c/sh | F | naked(crash-orphan) |
| 26JUL08TUBWER-TUB | WTA_CHALL | 07/08 06:53 | W2~ | 55 | 56 @ 07/08 06:35 (pr) | -1 | DIVOT* | join | 0 | SETTLED yes +45.0c/sh | B | naked(crash-orphan) |
| 26JUL08LEPKOR-KOR | WTA_CHALL | 07/08 07:35 | W2~ | 71 | 71 @ 07/08 05:10 (sf) | +0 | REPRICE* | below_chain | 0 | SETTLED no -71.0c/sh | F | naked(crash-orphan) |
| 26JUL08JONJEA-JEA | WTA_CHALL | 07/08 09:30 | window-uncertain | 47 | 49 @ 07/08 07:00 (sf) | -2 | NO_TAPE* | below_chain | 0 | OPEN, exit resting @56; band dist +2 (last 54) | C | naked(crash-orphan) |
| 26JUL06ISHCRO-CRO | WTA_CHALL | 07/08 11:32 | W2~ | 59 | 61 @ 07/07 01:24 (sf) | -2 | AMBIG | ? | 19 | EXIT_FILLED @72 (W2, maker) +13.0c/sh | A | naked(wave2-adopt) |
| 26JUL06COLSMI-COL | WTA_CHALL | 07/08 11:41 | W1? | 38 | 31 @ 07/08 11:57 (sf) | +7 | AMBIG | below_chain | 16 | EXIT_FILLED @45 (W1?, maker) +7.0c/sh | A? | — |
| 26JUL07SEBBRA-BRA | WTA_CHALL | 07/08 11:42 | W2~ | 49 | 50 @ 07/08 06:17 (sf) | -1 | REPRICE | join | 126 | EXIT_FILLED @59 (W2, maker) +10.0c/sh | A | — |
| 26JUL07LOMTOM-TOM | ITF_M | 07/07 23:13 | W2~ | 62 | 67 @ 07/07 20:52 (pr) | -5 | NO_UNDERCUT | join | 0 | EXIT_FILLED @80 (W2, maker) +18.0c/sh | A | — |
| 26JUL07OKIMAT-OKI | ITF_M | 07/07 23:13 | W2~ | 53 | 54 @ 07/07 19:27 (pr) | -1 | REPRICE | join | 1 | SETTLED no -53.0c/sh | F | — |
| 26JUL07NASLEE-LEE | ITF_M | 07/07 23:24 | W2~ | 25 | 28 @ 07/07 20:27 (pr) | -3 | NO_UNDERCUT | below_chain | 75 | EXIT_FILLED @39.5 (W2, taker-swept) +14.5c/sh | A | — |
| 26JUL07NAKSHI-NAK | ITF_M | 07/07 23:31 | W1? | 40 | 33 @ 07/08 01:19 (sf) | +7 | REPRICE | join | 1 | EXIT_FILLED @48 (W2, maker) +8.0c/sh | B | — |
| 26JUL07NAKSHI-SHI | ITF_M | 07/07 23:34 | W2~ | 57 | 60 @ 07/07 21:47 (pr) | -3 | AMBIG | join | 0 | EXIT_FILLED @73 (W2, maker) +16.0c/sh | A | — |
| 26JUL07YAMNAK-YAM | ITF_M | 07/07 23:37 | W2~ | 90 | 92 @ 07/07 22:51 (pr) | -2 | REPRICE | join | 3 | EXIT_FILLED @98 (W2, maker) +8.0c/sh | A | — |
| 26JUL07BORZEN-ZEN | ITF_M | 07/07 23:42 | W2~ | 42 | 43 @ 07/07 22:22 (pr) | -1 | AMBIG | join | 0 | EXIT_FILLED @51 (W2, maker) +9.0c/sh | A | — |
| 26JUL07YAMNAK-NAK | ITF_M | 07/07 23:57 | W2~ | 7 | 5 @ 07/07 22:57 (sf) | +2 | NO_UNDERCUT | join | 3 | EXIT_FILLED @11 (W2, maker) +4.0c/sh | A | frac-qty |
| 26JUL07BORZEN-BOR | ITF_M | 07/07 23:57 | W2~ | 53 | 69 @ 07/07 12:28 (ask) | -16 | NO_UNDERCUT | join | 0 | EXIT_FILLED @67 (W2, maker) +14.0c/sh | A | — |
| 26JUL08HARBEA-BEA | ITF_M | 07/08 00:03 | W1? | 91 | 91 @ 07/08 00:03 (sf) | +0 | AMBIG | improve1 | 9 | EXIT_FILLED @98 (W2, maker) +7.0c/sh | A? | — |
| 26JUL07YAMTAN-TAN | ITF_M | 07/08 00:19 | W1? | 82 | 71 @ 07/08 01:33 (sf) | +11 | AMBIG | join | 1 | EXIT_FILLED @98 (W2, maker) +16.0c/sh | B | — |
| 26JUL07YAMTAN-YAM | ITF_M | 07/08 00:25 | W1? | 15 | 14 @ 07/08 00:25 (sf) | +1 | DIVOT | join | 0 | EXIT_FILLED @20 (W2, maker) +5.0c/sh | A? | — |
| 26JUL08KUNMEN-MEN | ITF_M | 07/08 00:42 | W2~ | 65 | 50 @ 07/07 23:08 (pr) | +15 | REPRICE | mid_spread | 7 | EXIT_FILLED @84 (W2, maker) +19.0c/sh | B | — |
| 26JUL08SAKVAN-SAK | ITF_M | 07/08 00:43 | W1? | 27 | 24 @ 07/08 04:42 (sf) | +3 | DIVOT | join | 1 | SETTLED no -27.0c/sh | F | — |
| 26JUL08STERAD-RAD | ITF_M | 07/08 00:44 | W1? | 34 | 27 @ 07/08 04:17 (sf) | +7 | AMBIG | join | 0 | EXIT_FILLED @42 (W2, maker) +8.0c/sh | B | — |
| 26JUL08ZHAISH-ZHA | ITF_M | 07/08 00:46 | W1? | 86 | 75 @ 07/08 02:30 (sf) | +11 | NO_UNDERCUT | join | 0 | SETTLED no -86.0c/sh | F | — |
| 26JUL08LIUSHI-LIU | ITF_M | 07/08 00:54 | W1? | 75 | 66 @ 07/08 01:05 (sf) | +9 | REPRICE | below_chain | 9 | EXIT_FILLED @94 (W2, maker) +19.0c/sh | B | — |
| 26JUL08SERROS-ROS | ITF_M | 07/08 00:55 | W1? | 54 | 48 @ 07/08 00:55 (sf) | +6 | AMBIG | join | 1 | EXIT_FILLED @69 (W2, maker) +15.0c/sh | B | — |
| 26JUL07MOXSAR-SAR | ITF_M | 07/08 01:05 | W2~ | 27 | 31 @ 07/07 21:51 (pr) | -4 | REPRICE | join | 11 | EXIT_FILLED @34 (W2, maker) +7.0c/sh | A | — |
| 26JUL07BOUMOC-MOC | ITF_M | 07/08 01:20 | W2 | 24 | 24 @ 07/07 22:44 (ask) | +0 | NO_UNDERCUT | ? | 4 | EXIT_FILLED @38.2 (W1?, taker-swept) +14.2c/sh | S | — |
| 26JUL07TROKIM-TRO | ITF_M | 07/08 01:34 | W2~ | 35 | 38 @ 07/08 01:12 (pr) | -3 | DIVOT | join | 0 | EXIT_FILLED @43 (W2, maker) +8.0c/sh | A | — |
| 26JUL07TROKIM-KIM | ITF_M | 07/08 01:51 | W2~ | 62 | 64 @ 07/07 20:52 (pr) | -2 | REPRICE | join | 1 | SETTLED no -62.0c/sh | F | — |
| 26JUL08STEGSC-GSC | ITF_M | 07/08 01:52 | W1? | 85 | 75 @ 07/08 04:46 (sf) | +10 | AMBIG | join | 0 | EXIT_FILLED @98 (W2, maker) +13.0c/sh | B | — |
| 26JUL08KUNMEN-KUN | ITF_M | 07/08 02:08 | W2~ | 31 | 36 @ 07/08 00:02 (pr) | -5 | NO_UNDERCUT | join | 3 | SETTLED no -31.0c/sh | F | — |
| 26JUL08BALKAS-KAS | ITF_M | 07/08 02:16 | window-uncertain | 18 | 21 @ 07/07 20:33 (ask) | -3 | DIVOT | join | 1 | SETTLED no -18.0c/sh | F | — |
| 26JUL08SHIVUJ-SHI | ITF_M | 07/08 02:41 | window-uncertain | 61 | 61 @ 07/08 02:41 (sf) | +0 | AMBIG | join | 1 | SETTLED scalar | F | — |
| 26JUL08KIMROH-KIM | ITF_M | 07/08 03:03 | W2~ | 64 | 66 @ 07/08 01:19 (sf) | -2 | REPRICE* | join | 0 | SETTLED no -64.0c/sh | F | naked(crash-orphan) |
| 26JUL08ARSOPA-ARS | ITF_M | 07/08 03:10 | W1? | 76 | 76 @ 07/08 03:10 (sf) | +0 | DIVOT* | join | 0 | SETTLED yes +24.0c/sh | B | naked(crash-orphan) |
| 26JUL08PAPPET-PET | ITF_M | 07/08 03:14 | W2~ | 30 | 30 @ 07/07 20:48 (ask) | +0 | REPRICE* | join | 0 | SETTLED no -30.0c/sh | F | naked(crash-orphan) |
| 26JUL08BORBRE-BRE | ITF_M | 07/08 03:15 | W2~ | 25 | 28 @ 07/08 02:17 (pr) | -3 | REPRICE* | join | 0 | SETTLED no -25.0c/sh | F | naked(crash-orphan) |
| 26JUL08BREBRU-BRE | ITF_M | 07/08 03:18 | W1? | 70 | 70 @ 07/08 03:18 (sf) | +0 | DIVOT* | join | 0 | SETTLED yes +30.0c/sh | B | naked(crash-orphan) |
| 26JUL08EICAND-AND | ITF_M | 07/08 03:18 | W2~ | 70 | 74 @ 07/08 01:02 (pr) | -4 | DIVOT* | join | 0 | SETTLED yes +30.0c/sh | B | naked(crash-orphan) |
| 26JUL08BREBRU-BRU | ITF_M | 07/08 03:19 | W2~ | 25 | 30 @ 07/07 23:34 (pr) | -5 | DIVOT* | join | 0 | SETTLED no -25.0c/sh | F | naked(crash-orphan) |
| 26JUL08EICAND-EIC | ITF_M | 07/08 03:22 | W2~ | 26 | 30 @ 07/08 02:31 (pr) | -4 | REPRICE* | join | 0 | SETTLED no -26.0c/sh | F | naked(crash-orphan) |
| 26JUL08ARSOPA-OPA | ITF_M | 07/08 03:25 | W2~ | 19 | 23 @ 07/08 02:55 (pr) | -4 | DIVOT* | join | 0 | SETTLED no -19.0c/sh | F | naked(crash-orphan) |
| 26JUL08BORBRE-BOR | ITF_M | 07/08 03:31 | W2~ | 71 | 74 @ 07/08 03:11 (pr) | -3 | DIVOT* | join | 0 | SETTLED yes +29.0c/sh | B | naked(crash-orphan) |
| 26JUL08KIMROH-ROH | ITF_M | 07/08 03:34 | W2~ | 31 | 34 @ 07/07 23:56 (pr) | -3 | REPRICE* | join | 0 | SETTLED yes +69.0c/sh | B | naked(crash-orphan) |
| 26JUL08PELDUH-PEL | ITF_M | 07/08 03:36 | W1? | 74 | 74 @ 07/08 03:36 (sf) | +0 | DIVOT* | join | 1 | SETTLED no -74.0c/sh | F | naked(crash-orphan) |
| 26JUL08GHAGEN-GEN | ITF_M | 07/08 03:42 | W2~ | 34 | 37 @ 07/08 03:00 (pr) | -3 | REPRICE* | join | 1 | SETTLED no -34.0c/sh | F | naked(crash-orphan) |
| 26JUL08THIAND-AND | ITF_M | 07/08 03:45 | window-uncertain | 38 | 40 @ 07/08 03:02 (pr) | -2 | AMBIG* | join | 0 | SETTLED no -38.0c/sh | F | naked(crash-orphan) |
| 26JUL08LAPGAR-GAR | ITF_M | 07/08 03:45 | W2~ | 59 | 63 @ 07/08 03:06 (pr) | -4 | NO_UNDERCUT* | join | 0 | SETTLED yes +41.0c/sh | B | naked(crash-orphan) |
| 26JUL08PIEPRA-PRA | ITF_M | 07/08 03:45 | W2~ | 14 | 16 @ 07/08 03:02 (pr) | -2 | REPRICE* | join | 0 | SETTLED no -14.0c/sh | F | naked(crash-orphan) |
| 26JUL08LAPGAR-LAP | ITF_M | 07/08 03:47 | W1? | 36 | 16 @ 07/08 04:05 (sf) | +20 | REPRICE* | join | 0 | SETTLED no -36.0c/sh | F | naked(crash-orphan) |
| 26JUL08HARBEA-HAR | ITF_M | 07/08 03:49 | W2~ | 5 | 8 @ 07/08 02:40 (sf) | -3 | REPRICE* | below_chain | 79 | SETTLED no -5.0c/sh | F | naked(crash-orphan) |
| 26JUL08PELDUH-DUH | ITF_M | 07/08 03:52 | W1? | 21 | 16 @ 07/08 03:53 (sf) | +5 | REPRICE* | improve1 | 1 | SETTLED yes +79.0c/sh | B | naked(crash-orphan) |
| 26JUL08SAKVAN-VAN | ITF_M | 07/08 04:00 | window-uncertain | 71 | 22 @ 07/07 15:13 (ask) | +49 | NO_TAPE* | join | 0 | SETTLED yes +29.0c/sh | B | naked(crash-orphan) |
| 26JUL08LAZADD-LAZ | ITF_M | 07/08 04:10 | W1? | 16 | 16 @ 07/08 04:10 (sf) | +0 | DIVOT* | join | 4 | SETTLED no -16.0c/sh | F | naked(crash-orphan) |
| 26JUL08BERKUM-BER | ITF_M | 07/08 04:11 | W1? | 63 | 63 @ 07/08 04:11 (sf) | +0 | DIVOT* | join | 0 | SETTLED yes +37.0c/sh | B | naked(crash-orphan) |
| 26JUL08CARERE-ERE | ITF_M | 07/08 04:11 | window-uncertain | 90 | 90 @ 07/08 03:34 (sf) | +0 | NO_UNDERCUT* | join | 2 | SETTLED yes +10.0c/sh | B | naked(crash-orphan) |
| 26JUL08BALKAS-BAL | ITF_M | 07/08 04:11 | window-uncertain | 79 | 83 @ 07/08 03:08 (pr) | -4 | NO_UNDERCUT* | improve1 | 2 | SETTLED yes +21.0c/sh | B | naked(crash-orphan) |
| 26JUL08SERROS-SER | ITF_M | 07/08 04:15 | W2~ | 42 | 47 @ 07/08 00:54 (pr) | -5 | DIVOT* | below_chain | 59 | SETTLED no -42.0c/sh | F | naked(crash-orphan) |
| 26JUL08BRAWYG-BRA | ITF_M | 07/08 04:18 | window-uncertain | 85 | 88 @ 07/08 03:08 (pr) | -3 | DIVOT* | join | 0 | SETTLED yes +15.0c/sh | B | naked(crash-orphan) |
| 26JUL08STEGSC-STE | ITF_M | 07/08 04:19 | W2~ | 12 | 16 @ 07/08 02:29 (pr) | -4 | DIVOT* | below_chain | 30 | SETTLED no -12.0c/sh | F | naked(crash-orphan) |
| 26JUL08BERKUM-KUM | ITF_M | 07/08 04:20 | W2~ | 34 | 37 @ 07/08 00:08 (pr) | -3 | REPRICE* | join | 0 | SETTLED no -34.0c/sh | F | naked(crash-orphan) |
| 26JUL08MURGUN-GUN | ITF_M | 07/08 04:23 | W1? | 91 | 91 @ 07/08 02:30 (sf) | +0 | DIVOT* | join | 0 | SETTLED no -91.0c/sh | F | naked(crash-orphan) |
| 26JUL08BRAWYG-WYG | ITF_M | 07/08 04:25 | W2~ | 12 | 15 @ 07/08 03:05 (pr) | -3 | REPRICE* | join | 1 | SETTLED no -12.0c/sh | F | naked(crash-orphan) |
| 26JUL08GHAGEN-GHA | ITF_M | 07/08 04:25 | W2~ | 64 | 65 @ 07/08 03:27 (pr) | -1 | REPRICE* | join | 3 | SETTLED yes +36.0c/sh | B | naked(crash-orphan) |
| 26JUL08LAZADD-ADD | ITF_M | 07/08 04:32 | W2~ | 82 | 85 @ 07/08 03:07 (pr) | -3 | DIVOT* | join | 0 | SETTLED yes +18.0c/sh | B | naked(crash-orphan) |
| 26JUL08KIRVAN-KIR | ITF_M | 07/08 04:40 | W1? | 86 | 83 @ 07/08 05:54 (sf) | +3 | NO_UNDERCUT* | join | 0 | SETTLED yes +14.0c/sh | B | naked(crash-orphan) |
| 26JUL08CARERE-CAR | ITF_M | 07/08 04:43 | W2~ | 6 | 8 @ 07/08 02:29 (pr) | -2 | DIVOT* | join | 0 | SETTLED no -6.0c/sh | F | naked(crash-orphan) |
| 26JUL08MABDUR-DUR | ITF_M | 07/08 04:46 | window-uncertain | 92 | 95 @ 07/07 16:55 (ask) | -3 | DIVOT* | join | 0 | SETTLED yes +8.0c/sh | B | naked(crash-orphan) |
| 26JUL08JONSNO-JON | ITF_M | 07/08 04:47 | W2~ | 92 | 95 @ 07/08 04:38 (pr) | -3 | DIVOT* | join | 0 | SETTLED yes +8.0c/sh | B | naked(crash-orphan) |
| 26JUL08DOUDAR-DOU | ITF_M | 07/08 04:49 | W1? | 82 | 56 @ 07/08 05:00 (sf) | +26 | REPRICE* | join | 0 | SETTLED yes +18.0c/sh | B | naked(crash-orphan) |
| 26JUL08MABDUR-MAB | ITF_M | 07/08 04:56 | W2~ | 6 | 7 @ 07/08 02:31 (pr) | -1 | DIVOT* | join | 0 | SETTLED no -6.0c/sh | F | naked(crash-orphan) |
| 26JUL08KAMDEC-DEC | ITF_M | 07/08 05:03 | W1? | 90 | 86 @ 07/08 05:32 (sf) | +4 | REPRICE* | join | 0 | SETTLED yes +10.0c/sh | B | naked(crash-orphan) |
| 26JUL08BAXLEN-BAX | ITF_M | 07/08 05:05 | W1? | 94 | 90 @ 07/08 05:05 (sf) | +4 | NO_TAPE* | join | 1 | SETTLED yes +6.0c/sh | B | naked(crash-orphan) |
| 26JUL08MINFAB-MIN | ITF_M | 07/08 05:05 | window-uncertain | 48 | 52 @ 07/08 04:56 (sf) | -4 | REPRICE* | join | 1 | SETTLED no -48.0c/sh | F | naked(crash-orphan) |
| 26JUL08DEDPOE-DED | ITF_M | 07/08 05:06 | W2~ | 47 | 49 @ 07/08 01:23 (pr) | -2 | REPRICE* | improve1 | 1 | SETTLED no -47.0c/sh | F | naked(crash-orphan) |
| 26JUL08HOPFIX-FIX | ITF_M | 07/08 05:07 | W2~ | 39 | 40 @ 07/08 00:34 (pr) | -1 | DIVOT* | join | 0 | SETTLED yes +61.0c/sh | B | naked(crash-orphan) |
| 26JUL08XILSTR-XIL | ITF_M | 07/08 05:08 | W2~ | 90 | 93 @ 07/07 17:29 (ask) | -3 | NO_UNDERCUT* | join | 0 | SETTLED yes +10.0c/sh | B | naked(crash-orphan) |
| 26JUL08KIRVAN-VAN | ITF_M | 07/08 05:08 | W1? | 11 | 11 @ 07/08 00:49 (sf) | +0 | DIVOT* | join | 0 | SETTLED no -11.0c/sh | F | naked(crash-orphan) |
| 26JUL08DEDPOE-POE | ITF_M | 07/08 05:08 | W2~ | 51 | 54 @ 07/08 04:32 (pr) | -3 | DIVOT* | join | 0 | SETTLED yes +49.0c/sh | B | naked(crash-orphan) |
| 26JUL08SHAMAT-MAT | ITF_M | 07/08 05:09 | W1? | 66 | 57 @ 07/08 05:15 (sf) | +9 | REPRICE* | improve1 | 1 | SETTLED yes +34.0c/sh | B | naked(crash-orphan) |
| 26JUL08XILSTR-STR | ITF_M | 07/08 05:10 | W2~ | 7 | 10 @ 07/08 02:31 (pr) | -3 | REPRICE* | join | 0 | SETTLED no -7.0c/sh | F | naked(crash-orphan) |
| 26JUL08HOPFIX-HOP | ITF_M | 07/08 05:15 | W2~ | 58 | 59 @ 07/07 19:14 (pr) | -1 | REPRICE* | join | 0 | SETTLED no -58.0c/sh | F | naked(crash-orphan) |
| 26JUL08KAMDEC-KAM | ITF_M | 07/08 05:23 | W2~ | 7 | 8 @ 07/08 01:21 (pr) | -1 | DIVOT* | join | 0 | SETTLED no -7.0c/sh | F | naked(crash-orphan) |
| 26JUL08SHAMAT-SHA | ITF_M | 07/08 05:24 | W2~ | 31 | 35 @ 07/08 03:09 (pr) | -4 | DIVOT* | join | 0 | SETTLED no -31.0c/sh | F | naked(crash-orphan) |
| 26JUL08TYAGAR-GAR | ITF_M | 07/08 05:28 | W1? | 36 | 16 @ 07/08 05:49 (sf) | +20 | REPRICE* | join | 0 | SETTLED no -36.0c/sh | F | naked(crash-orphan) |
| 26JUL08OETSCH-OET | ITF_M | 07/08 05:32 | W1? | 55 | 55 @ 07/08 05:32 (sf) | +0 | NO_TAPE* | join | 0 | SETTLED yes +45.0c/sh | B | naked(crash-orphan) |
| 26JUL08CHLBOJ-CHL | ITF_M | 07/08 05:43 | W2~ | 31 | 34 @ 07/08 03:08 (pr) | -3 | DIVOT* | join | 1 | SETTLED yes +69.0c/sh | B | naked(crash-orphan) |
| 26JUL08MURGUN-MUR | ITF_M | 07/08 05:45 | W2~ | 6 | 7 @ 07/08 02:47 (pr) | -1 | DIVOT* | join | 1 | SETTLED yes +94.0c/sh | B | naked(crash-orphan) |
| 26JUL08BONWEI-WEI | ITF_M | 07/08 05:47 | window-uncertain | 88 | 91 @ 07/08 01:57 (ask) | -3 | NO_UNDERCUT* | join | 1 | SETTLED yes +12.0c/sh | B | naked(crash-orphan) |
| 26JUL08BONWEI-BON | ITF_M | 07/08 05:52 | W2~ | 9 | 11 @ 07/08 04:45 (pr) | -2 | REPRICE* | join | 1 | SETTLED no -9.0c/sh | F | naked(crash-orphan) |
| 26JUL08LAGHOM-LAG | ITF_M | 07/08 05:53 | W1? | 55 | 52 @ 07/08 05:58 (sf) | +3 | REPRICE* | join | 1 | SETTLED yes +45.0c/sh | B | naked(crash-orphan) |
| 26JUL08ROBHOS-ROB | ITF_M | 07/08 05:58 | W1? | 73 | 73 @ 07/08 05:58 (sf) | +0 | NO_TAPE* | join | 1 | SETTLED yes +27.0c/sh | B | naked(crash-orphan) |
| 26JUL08KASVAC-VAC | ITF_M | 07/08 05:58 | W1? | 37 | 4 @ 07/08 06:45 (sf) | +33 | REPRICE* | join | 0 | SETTLED yes +63.0c/sh | B | naked(crash-orphan) |
| 26JUL08LAGHOM-HOM | ITF_M | 07/08 06:03 | W2~ | 42 | 46 @ 07/08 05:09 (pr) | -4 | DIVOT* | join | 0 | SETTLED no -42.0c/sh | F | naked(crash-orphan) |
| 26JUL08PERVAN-VAN | ITF_M | 07/08 06:06 | W1? | 42 | 40 @ 07/08 06:06 (sf) | +2 | DIVOT* | improve1 | 1 | SETTLED yes +58.0c/sh | B | naked(crash-orphan) |
| 26JUL08PERVAN-PER | ITF_M | 07/08 06:09 | W1? | 54 | 41 @ 07/08 06:19 (sf) | +13 | REPRICE* | join | 0 | SETTLED no -54.0c/sh | F | naked(crash-orphan) |
| 26JUL08NAWALA-NAW | ITF_M | 07/08 06:09 | W2~ | 71 | 75 @ 07/07 18:48 (ask) | -4 | REPRICE* | join | 1 | SETTLED no -71.0c/sh | F | naked(crash-orphan) |
| 26JUL08CHLBOJ-BOJ | ITF_M | 07/08 06:10 | W1? | 65 | 62 @ 07/08 06:14 (sf) | +3 | REPRICE* | below_chain | 0 | SETTLED no -65.0c/sh | F | naked(crash-orphan) |
| 26JUL08PAASTA-STA | ITF_M | 07/08 06:11 | W1? | 12 | 12 @ 07/08 06:11 (sf) | +0 | REPRICE* | join | 1 | SETTLED no -12.0c/sh | F | naked(crash-orphan) |
| 26JUL08RIVBER-BER | ITF_M | 07/08 06:19 | W1? | 86 | 60 @ 07/08 06:42 (sf) | +26 | REPRICE* | join | 0 | SETTLED no -86.0c/sh | F | naked(crash-orphan) |
| 26JUL08DOUDAR-DAR | ITF_M | 07/08 06:20 | W2~ | 14 | 18 @ 07/08 03:07 (pr) | -4 | REPRICE* | join | 0 | SETTLED no -14.0c/sh | F | naked(crash-orphan) |
| 26JUL08RECCAS-REC | ITF_M | 07/08 06:22 | W1? | 55 | 55 @ 07/08 06:22 (sf) | +0 | NO_UNDERCUT* | join | 0 | SETTLED yes +45.0c/sh | B | naked(crash-orphan) |
| 26JUL08BLOBRA-BRA | ITF_M | 07/08 06:23 | W1? | 74 | 74 @ 07/08 06:23 (sf) | +0 | DIVOT* | join | 0 | SETTLED yes +26.0c/sh | B | naked(crash-orphan) |
| 26JUL08RECCAS-CAS | ITF_M | 07/08 06:24 | W1? | 42 | 16 @ 07/08 07:01 (sf) | +26 | REPRICE* | join | 0 | SETTLED no -42.0c/sh | F | naked(crash-orphan) |
| 26JUL08PAASTA-PAA | ITF_M | 07/08 06:27 | W1? | 85 | 85 @ 07/08 06:27 (sf) | +0 | REPRICE* | join | 0 | SETTLED yes +15.0c/sh | B | naked(crash-orphan) |
| 26JUL08ROCTSI-ROC | ITF_M | 07/08 06:32 | W1? | 23 | 3 @ 07/08 07:26 (sf) | +20 | REPRICE* | join | 0 | SETTLED no -23.0c/sh | F | naked(crash-orphan) |
| 26JUL08ROBSAH-SAH | ITF_M | 07/08 06:32 | W1? | 73 | 73 @ 07/08 06:32 (sf) | +0 | REPRICE* | join | 4 | SETTLED no -73.0c/sh | F | naked(crash-orphan) |
| 26JUL08BLOBRA-BLO | ITF_M | 07/08 06:34 | window-uncertain | 21 | 25 @ 07/08 06:27 (pr) | -4 | REPRICE* | join | 1 | SETTLED no -21.0c/sh | F | naked(crash-orphan) |
| 26JUL08JERCIO-CIO | ITF_M | 07/08 06:36 | window-uncertain | 11 | 12 @ 07/08 06:36 (pr) | -1 | REPRICE* | join | 0 | SETTLED no -11.0c/sh | F | naked(crash-orphan) |
| 26JUL08CLAVIS-CLA | ITF_M | 07/08 06:41 | W1? | 93 | 91 @ 07/08 06:46 (sf) | +2 | DIVOT* | join | 0 | SETTLED yes +7.0c/sh | B | naked(crash-orphan) |
| 26JUL08SINMUE-SIN | ITF_M | 07/08 06:43 | W1? | 79 | 77 @ 07/08 07:12 (sf) | +2 | REPRICE* | join | 0 | SETTLED yes +21.0c/sh | B | naked(crash-orphan) |
| 26JUL08SPIBER-BER | ITF_M | 07/08 06:44 | W1? | 53 | 51 @ 07/08 06:45 (sf) | +2 | DIVOT* | join | 1 | SETTLED no -53.0c/sh | F | naked(crash-orphan) |
| 26JUL08BAGSTE-STE | ITF_M | 07/08 06:46 | W1? | 73 | 73 @ 07/08 06:46 (sf) | +0 | NO_UNDERCUT* | join | 1 | SETTLED yes +27.0c/sh | B | naked(crash-orphan) |
| 26JUL08SPIBER-SPI | ITF_M | 07/08 06:46 | W1? | 43 | 31 @ 07/08 06:53 (sf) | +12 | REPRICE* | join | 0 | SETTLED yes +57.0c/sh | B | naked(crash-orphan) |
| 26JUL08SINMUE-MUE | ITF_M | 07/08 06:50 | W2~ | 17 | 22 @ 07/08 06:42 (sf) | -5 | DIVOT* | join | 0 | SETTLED no -17.0c/sh | F | naked(crash-orphan) |
| 26JUL08MALCRA-MAL | ITF_M | 07/08 06:54 | W2~ | 26 | 30 @ 07/08 03:12 (pr) | -4 | REPRICE* | join | 0 | SETTLED no -26.0c/sh | F | naked(crash-orphan) |
| 26JUL08MIRGOL-MIR | ITF_M | 07/08 06:55 | W1? | 90 | 81 @ 07/08 07:30 (sf) | +9 | AMBIG* | join | 0 | SETTLED yes +10.0c/sh | B | naked(crash-orphan) |
| 26JUL08POUBEC-BEC | ITF_M | 07/08 06:55 | W1? | 20 | 16 @ 07/08 07:40 (sf) | +4 | REPRICE* | join | 0 | SETTLED yes +80.0c/sh | B | naked(crash-orphan) |
| 26JUL08BARDON-DON | ITF_M | 07/08 06:56 | W1? | 94 | 92 @ 07/08 07:40 (sf) | +2 | DIVOT* | join | 0 | SETTLED yes +6.0c/sh | B | naked(crash-orphan) |
| 26JUL08ZAPBEN-BEN | ITF_M | 07/08 07:03 | W1? | 21 | 17 @ 07/08 07:11 (sf) | +4 | DIVOT* | join | 0 | SETTLED no -21.0c/sh | F | naked(crash-orphan) |
| 26JUL08PIAPIE-PIA | ITF_M | 07/08 07:12 | W1? | 38 | 38 @ 07/08 07:12 (sf) | +0 | DIVOT* | join | 3 | SETTLED no -38.0c/sh | F | naked(crash-orphan) |
| 26JUL08BAGSTE-BAG | ITF_M | 07/08 07:12 | W1? | 25 | 3 @ 07/08 07:51 (sf) | +22 | REPRICE* | join | 0 | SETTLED no -25.0c/sh | F | naked(crash-orphan) |
| 26JUL08ZAPBEN-ZAP | ITF_M | 07/08 07:18 | W1? | 76 | 57 @ 07/08 07:40 (sf) | +19 | DIVOT* | join | 0 | SETTLED yes +24.0c/sh | B | naked(crash-orphan) |
| 26JUL08KASVAC-KAS | ITF_M | 07/08 07:21 | W2~ | 58 | 71 @ 07/08 06:02 (sf) | -13 | REPRICE* | join | 0 | SETTLED no -58.0c/sh | F | naked(crash-orphan) |
| 26JUL08CATMCD-CAT | ITF_M | 07/08 07:30 | W1? | 92 | 85 @ 07/08 08:02 (sf) | +7 | DIVOT* | join | 1 | SETTLED yes +8.0c/sh | B | naked(crash-orphan) |
| 26JUL08POUBEC-POU | ITF_M | 07/08 07:30 | W1? | 75 | 75 @ 07/08 07:30 (sf) | +0 | REPRICE* | join | 0 | SETTLED no -75.0c/sh | F | naked(crash-orphan) |
| 26JUL08ROBHOS-HOS | ITF_M | 07/08 07:39 | W2~ | 24 | 27 @ 07/08 03:58 (pr) | -3 | REPRICE* | join | 0 | SETTLED no -24.0c/sh | F | naked(crash-orphan) |
| 26JUL08OETSCH-SCH | ITF_M | 07/08 08:06 | W1? | 44 | 44 @ 07/08 08:06 (sf) | +0 | DIVOT* | join | 3 | SETTLED no -44.0c/sh | F | naked(crash-orphan) |
| 26JUL08CATMCD-MCD | ITF_M | 07/08 08:49 | W2~ | 6 | 8 @ 07/08 03:13 (pr) | -2 | REPRICE* | join | 0 | SETTLED no -6.0c/sh | F | naked(crash-orphan) |
| 26JUL08MIRGOL-GOL | ITF_M | 07/08 09:50 | W2~ | 6 | 7 @ 07/08 03:48 (pr) | -1 | REPRICE* | join | 0 | SETTLED no -6.0c/sh | F | naked(crash-orphan) |
| 26JUL08ALFMON-MON | ITF_M | 07/08 11:37 | W2~ | 15 | ? | ? | REPRICE | join | 0 | OPEN, exit resting @20; band dist +19 (last 1) | D | — |
| 26JUL07CHOCAO-CAO | ITF_W | 07/07 23:16 | W1? | 49 | 16 @ 07/08 02:15 (ask) | +33 | REPRICE | join | 0 | EXIT_FILLED @59 (W1?, maker) +10.0c/sh | A? | — |
| 26JUL08TUPPAN-PAN | ITF_W | 07/07 23:19 | W1? | 14 | 4 @ 07/07 23:24 (sf) | +10 | REPRICE | mid_spread | 7 | EXIT_FILLED @18 (W2, maker) +4.0c/sh | B | — |
| 26JUL07WEISUN-WEI | ITF_W | 07/07 23:39 | W2~ | 79 | 82 @ 07/07 20:54 (pr) | -3 | REPRICE | join | 0 | SETTLED no -79.0c/sh | F | — |
| 26JUL07WEISUN-SUN | ITF_W | 07/07 23:40 | W2~ | 18 | 20 @ 07/07 20:41 (pr) | -2 | DIVOT | join | 0 | EXIT_FILLED @23 (W2, maker) +5.0c/sh | A | — |
| 26JUL07GURKAL-KAL | ITF_W | 07/07 23:45 | W1? | 65 | 61 @ 07/07 23:45 (sf) | +4 | AMBIG | improve1 | 1 | EXIT_FILLED @81 (W2, maker) +16.0c/sh | A? | — |
| 26JUL07LIURUO-RUO | ITF_W | 07/07 23:53 | W1? | 23 | 23 @ 07/07 23:53 (sf) | +0 | NO_UNDERCUT | join | 0 | EXIT_FILLED @28 (W2, maker) +5.0c/sh | A? | — |
| 26JUL08HARMAI-HAR | ITF_W | 07/07 23:55 | W1? | 4 | 2 @ 07/08 02:28 (ask) | +2 | REPRICE | join | 3 | EXIT_FILLED @7 (W1?, maker) +3.0c/sh | S? | — |
| 26JUL07GURKAL-GUR | ITF_W | 07/08 00:07 | W1? | 32 | 29 @ 07/08 00:10 (sf) | +3 | REPRICE | join | 0 | EXIT_FILLED @39 (W2, maker) +7.0c/sh | A? | — |
| 26JUL07CHOCAO-CHO | ITF_W | 07/08 00:07 | W1? | 50 | 7 @ 07/08 01:38 (ask) | +43 | REPRICE | join | 1 | EXIT_FILLED @61 (W1?, maker) +11.0c/sh | A? | — |
| 26JUL08NAKZHA-ZHA | ITF_W | 07/08 00:25 | W1? | 15 | 15 @ 07/08 00:25 (sf) | +0 | AMBIG | join | 12 | EXIT_FILLED @19 (W2, maker) +4.0c/sh | A? | — |
| 26JUL08LIUMAL-MAL | ITF_W | 07/08 00:26 | W1? | 72 | 68 @ 07/08 03:00 (sf) | +4 | REPRICE | join | 1 | EXIT_FILLED @90 (W2, maker) +18.0c/sh | A? | — |
| 26JUL07LIURUO-LIU | ITF_W | 07/08 00:27 | W1? | 75 | 74 @ 07/08 01:22 (sf) | +1 | AMBIG | join | 0 | SETTLED no -75.0c/sh | F | — |
| 26JUL08NONYUA-YUA | ITF_W | 07/08 00:50 | W1? | 83 | 72 @ 07/08 01:15 (ask) | +11 | REPRICE | join | 0 | SETTLED no -83.0c/sh | F | — |
| 26JUL08MAMBEL-BEL | ITF_W | 07/08 00:53 | W1? | 12 | 13 @ 07/08 01:30 (ask) | -1 | NO_UNDERCUT | join | 0 | EXIT_FILLED @15 (W1?, maker) +3.0c/sh | S? | — |
| 26JUL08IUSSAG-SAG | ITF_W | 07/08 01:02 | W1? | 31 | 29 @ 07/08 01:31 (sf) | +2 | DIVOT | improve1 | 1 | EXIT_FILLED @37 (W1?, maker) +6.0c/sh | S? | — |
| 26JUL08WANOHX-WAN | ITF_W | 07/08 01:11 | W1? | 79 | 67 @ 07/08 04:11 (sf) | +12 | DIVOT | join | 0 | EXIT_FILLED @98 (W2, maker) +19.0c/sh | B | — |
| 26JUL08TUPPAN-TUP | ITF_W | 07/08 01:12 | W2~ | 83 | 66 @ 07/07 22:43 (sf) | +17 | NO_UNDERCUT | mid_spread | 209 | EXIT_FILLED @98 (W2, maker) +15.0c/sh | B | — |
| 26JUL08IUSSAG-IUS | ITF_W | 07/08 01:15 | W1? | 66 | 58 @ 07/08 01:15 (sf) | +8 | REPRICE | join | 0 | EXIT_FILLED @83 (W2, maker) +17.0c/sh | B | — |
| 26JUL08NONYUA-NON | ITF_W | 07/08 01:19 | W1? | 14 | 14 @ 07/08 01:20 (ask) | +0 | NO_UNDERCUT | join | 0 | EXIT_FILLED @18 (W1?, maker) +4.0c/sh | S? | — |
| 26JUL08SHEWAN-WAN | ITF_W | 07/08 01:30 | W1? | 59 | 40 @ 07/08 03:56 (sf) | +19 | AMBIG | join | 0 | SETTLED no -59.0c/sh | F | — |
| 26JUL08NUPBAR-BAR | ITF_W | 07/08 01:31 | W1? | 75 | 51 @ 07/08 05:05 (sf) | +24 | AMBIG | join | 1 | EXIT_FILLED @94 (W2, maker) +19.0c/sh | B | — |
| 26JUL08LIXYAM-LIX | ITF_W | 07/08 01:33 | W1? | 8 | 8 @ 07/07 23:09 (sf) | +0 | DIVOT | join | 0 | EXIT_FILLED @11 (W1?, maker) +3.0c/sh | S? | — |
| 26JUL08DESNIT-DES | ITF_W | 07/08 01:33 | W1? | 87 | 76 @ 07/08 01:55 (sf) | +11 | REPRICE | join | 0 | EXIT_FILLED @98 (W2, maker) +11.0c/sh | B | — |
| 26JUL08LASKOR-LAS | ITF_W | 07/08 01:35 | W1? | 66 | 66 @ 07/08 01:35 (sf) | +0 | AMBIG | join | 0 | SETTLED no -66.0c/sh | F | — |
| 26JUL08AHLKHO-AHL | ITF_W | 07/08 01:35 | W1? | 80 | 73 @ 07/08 03:56 (sf) | +7 | AMBIG | join | 0 | EXIT_FILLED @98 (W2, maker) +18.0c/sh | B | — |
| 26JUL08MAMBEL-MAM | ITF_W | 07/08 01:40 | W1? | 84 | 71 @ 07/08 01:43 (ask) | +13 | REPRICE | join | 0 | EXIT_FILLED @98 (W2, maker) +14.0c/sh | B | — |
| 26JUL08PUSBUR-BUR | ITF_W | 07/08 01:43 | W1? | 88 | 88 @ 07/08 01:43 (sf) | +0 | AMBIG | join | 0 | EXIT_FILLED @98 (W2, maker) +10.0c/sh | A? | — |
| 26JUL08SEDSTA-SED | ITF_W | 07/08 01:52 | W2~ | 46 | 46 @ 07/07 20:07 (pr) | +0 | REPRICE | below_chain | 38 | EXIT_FILLED @55 (W2, maker) +9.0c/sh | A | — |
| 26JUL08LIXYAM-YAM | ITF_W | 07/08 01:54 | W1? | 89 | 87 @ 07/08 03:00 (sf) | +2 | AMBIG | below_chain | 1 | EXIT_FILLED @98 (W2, maker) +9.0c/sh | A? | — |
| 26JUL08RYSTRA-TRA | ITF_W | 07/08 01:58 | W2~ | 9 | 8 @ 07/07 18:59 (pr) | +1 | AMBIG | join | 3 | SETTLED no -9.0c/sh | F | — |
| 26JUL08LOVBRE-BRE | ITF_W | 07/08 02:04 | W1? | 33 | 33 @ 07/08 02:04 (sf) | +0 | REPRICE | join | 1 | EXIT_FILLED @40 (W2, maker) +7.0c/sh | A? | — |
| 26JUL08HAYGIO-GIO | ITF_W | 07/08 02:08 | W2~ | 32 | 34 @ 07/07 23:57 (pr) | -2 | AMBIG | join | 2 | EXIT_FILLED @39 (W2, maker) +7.0c/sh | A | — |
| 26JUL08CEUMCK-MCK | ITF_W | 07/08 02:10 | W2~ | 22 | 26 @ 07/08 01:27 (pr) | -4 | REPRICE | join | 2 | EXIT_FILLED @28 (W2, maker) +6.0c/sh | A | — |
| 26JUL08CEUMCK-CEU | ITF_W | 07/08 02:11 | W2~ | 74 | 75 @ 07/08 02:07 (ask) | -1 | AMBIG | join | 0 | EXIT_FILLED @92 (W2, maker) +18.0c/sh | A | — |
| 26JUL08RICSTR-STR | ITF_W | 07/08 02:13 | W2~ | 69 | 74 @ 07/08 01:37 (pr) | -5 | REPRICE | join | 1 | EXIT_FILLED @87 (W2, maker) +18.0c/sh | A | — |
| 26JUL08HAYGIO-HAY | ITF_W | 07/08 02:13 | W2~ | 65 | 69 @ 07/07 23:35 (pr) | -4 | REPRICE | join | 0 | EXIT_FILLED @81 (W2, maker) +16.0c/sh | A | — |
| 26JUL08BALGOL-BAL | ITF_W | 07/08 02:16 | W2~ | 38 | 41 @ 07/08 00:04 (pr) | -3 | AMBIG | join | 0 | EXIT_FILLED @45 (W2, maker) +7.0c/sh | A | — |
| 26JUL08BALGOL-GOL | ITF_W | 07/08 02:18 | W2~ | 60 | 61 @ 07/07 23:34 (pr) | -1 | REPRICE | join | 1 | EXIT_FILLED @74 (W2, maker) +14.0c/sh | A | — |
| 26JUL08PUSBUR-PUS | ITF_W | 07/08 02:22 | W2~ | 7 | 7 @ 07/08 00:33 (sf) | +0 | REPRICE | join | 0 | SETTLED no -7.0c/sh | F | — |
| 26JUL08SHEWAN-SHE | ITF_W | 07/08 02:23 | W1? | 38 | 38 @ 07/08 02:23 (sf) | +0 | NO_UNDERCUT | join | 0 | EXIT_FILLED @45 (W1?, maker) +7.0c/sh | S? | — |
| 26JUL08WUXSNI-WUX | ITF_W | 07/08 02:29 | W2~ | 48 | 49 @ 07/08 01:44 (sf) | -1 | REPRICE | join | 0 | EXIT_FILLED @58 (W2, maker) +10.0c/sh | A | — |
| 26JUL08WANOHX-OHX | ITF_W | 07/08 02:31 | W1? | 18 | 18 @ 07/08 02:31 (sf) | +0 | NO_UNDERCUT | join | 0 | EXIT_FILLED @23 (W2, maker) +5.0c/sh | A? | — |
| 26JUL08WUXSNI-SNI | ITF_W | 07/08 02:36 | W2~ | 49 | 50 @ 07/08 01:19 (sf) | -1 | AMBIG | join | 1 | EXIT_FILLED @59 (W2, maker) +10.0c/sh | A | — |
| 26JUL08CHOKOS-KOS | ITF_W | 07/08 02:37 | W1? | 32 | 32 @ 07/08 02:37 (sf) | +0 | NO_UNDERCUT | improve1 | 2 | EXIT_FILLED @39 (W1?, maker) +7.0c/sh | S? | — |
| 26JUL08LOVBRE-LOV | ITF_W | 07/08 02:48 | W2~ | 63 | 65 @ 07/08 01:02 (pr) | -2 | NO_UNDERCUT | join | 0 | EXIT_FILLED @78 (W2, maker) +15.0c/sh | A | — |
| 26JUL08HARMAI-MAI | ITF_W | 07/08 02:53 | W2~ | 93 | 96 @ 07/08 01:24 (sf) | -3 | REPRICE* | ? | 2 | SETTLED yes +7.0c/sh | B | naked(crash-orphan) |
| 26JUL08BOSBOY-BOS | ITF_W | 07/08 03:08 | W1? | 94 | 93 @ 07/08 05:00 (sf) | +1 | NO_UNDERCUT* | join | 0 | SETTLED yes +6.0c/sh | B | naked(crash-orphan) |
| 26JUL08BOJVIR-BOJ | ITF_W | 07/08 03:09 | W2~ | 65 | 68 @ 07/07 23:36 (pr) | -3 | NO_UNDERCUT* | join | 0 | SETTLED yes +35.0c/sh | B | naked(crash-orphan) |
| 26JUL08BOJVIR-VIR | ITF_W | 07/08 03:10 | W1? | 32 | 11 @ 07/08 03:25 (sf) | +21 | REPRICE* | join | 0 | SETTLED no -32.0c/sh | F | naked(crash-orphan) |
| 26JUL08SUPFAV-FAV | ITF_W | 07/08 03:11 | W2~ | 18 | 21 @ 07/08 00:52 (pr) | -3 | DIVOT* | join | 0 | SETTLED no -18.0c/sh | F | naked(crash-orphan) |
| 26JUL08KOVPOL-POL | ITF_W | 07/08 03:13 | W2~ | 18 | 22 @ 07/08 03:00 (pr) | -4 | REPRICE* | join | 0 | SETTLED no -18.0c/sh | F | naked(crash-orphan) |
| 26JUL08LASKOR-KOR | ITF_W | 07/08 03:14 | W2~ | 30 | 42 @ 07/08 03:01 (sf) | -12 | DIVOT* | improve1 | 1 | SETTLED yes +70.0c/sh | B | naked(crash-orphan) |
| 26JUL08RICSTR-RIC | ITF_W | 07/08 03:15 | W1? | 26 | 30 @ 07/07 23:42 (ask) | -4 | NO_UNDERCUT* | join | 0 | SETTLED no -26.0c/sh | F | naked(crash-orphan) |
| 26JUL08DESNIT-NIT | ITF_W | 07/08 03:18 | W1? | 12 | 8 @ 07/07 14:07 (ask) | +4 | NO_TAPE* | join | 0 | SETTLED no -12.0c/sh | F | naked(crash-orphan) |
| 26JUL08NUPBAR-NUP | ITF_W | 07/08 03:19 | W1? | 22 | 18 @ 07/08 04:46 (sf) | +4 | NO_UNDERCUT* | join | 1 | SETTLED yes +78.0c/sh | B | naked(crash-orphan) |
| 26JUL08ROSPAR-ROS | ITF_W | 07/08 03:27 | W2~ | 48 | 47 @ 07/08 02:07 (sf) | +1 | REPRICE* | join | 1 | SETTLED yes +52.0c/sh | B | naked(crash-orphan) |
| 26JUL08MANKAV-MAN | ITF_W | 07/08 03:27 | W1? | 94 | 94 @ 07/08 01:22 (sf) | +0 | AMBIG* | join | 2 | SETTLED yes +6.0c/sh | B | naked(crash-orphan) |
| 26JUL08KAZSAC-KAZ | ITF_W | 07/08 03:28 | W1? | 62 | 60 @ 07/08 05:29 (sf) | +2 | NO_UNDERCUT* | join | 0 | SETTLED yes +38.0c/sh | B | naked(crash-orphan) |
| 26JUL08MATBEL-MAT | ITF_W | 07/08 03:30 | W1? | 74 | 74 @ 07/08 03:30 (sf) | +0 | NO_UNDERCUT* | join | 0 | SETTLED yes +26.0c/sh | B | naked(crash-orphan) |
| 26JUL08MIXKRU-KRU | ITF_W | 07/08 03:30 | W1? | 60 | 60 @ 07/08 03:30 (sf) | +0 | DIVOT* | join | 0 | SETTLED yes +40.0c/sh | B | naked(crash-orphan) |
| 26JUL08VANWON-WON | ITF_W | 07/08 03:38 | W2~ | 54 | 56 @ 07/08 03:05 (pr) | -2 | REPRICE* | join | 4 | SETTLED no -54.0c/sh | F | naked(crash-orphan) |
| 26JUL08SUPFAV-SUP | ITF_W | 07/08 03:39 | W2~ | 78 | 84 @ 07/08 03:20 (sf) | -6 | REPRICE* | join | 0 | SETTLED yes +22.0c/sh | B | naked(crash-orphan) |
| 26JUL08MIXKRU-MIX | ITF_W | 07/08 03:41 | W2~ | 39 | 34 @ 07/07 23:34 (pr) | +5 | REPRICE* | improve1 | 5 | SETTLED no -39.0c/sh | F | naked(crash-orphan) |
| 26JUL08CIRBRE-CIR | ITF_W | 07/08 03:43 | W1? | 85 | 66 @ 07/08 04:02 (sf) | +19 | REPRICE* | join | 0 | SETTLED yes +15.0c/sh | B | naked(crash-orphan) |
| 26JUL08AHLKHO-KHO | ITF_W | 07/08 03:48 | W2~ | 16 | 16 @ 07/08 00:25 (sf) | +0 | REPRICE* | join | 0 | SETTLED no -16.0c/sh | F | naked(crash-orphan) |
| 26JUL08VOSLEY-LEY | ITF_W | 07/08 04:00 | W1? | 94 | 92 @ 07/08 06:30 (sf) | +2 | NO_UNDERCUT* | join | 1 | SETTLED yes +6.0c/sh | B | naked(crash-orphan) |
| 26JUL08YODKEN-YOD | ITF_W | 07/08 04:23 | W1? | 78 | 81 @ 07/08 01:35 (ask) | -3 | NO_TAPE* | join | 0 | SETTLED yes +22.0c/sh | B | naked(crash-orphan) |
| 26JUL08KAZSAC-SAC | ITF_W | 07/08 04:24 | W1? | 27 | 23 @ 07/08 05:46 (sf) | +4 | NO_UNDERCUT* | join | 0 | SETTLED no -27.0c/sh | F | naked(crash-orphan) |
| 26JUL08MATBEL-BEL | ITF_W | 07/08 04:30 | W2~ | 21 | 21 @ 07/08 00:01 (sf) | +0 | REPRICE* | join | 0 | SETTLED no -21.0c/sh | F | naked(crash-orphan) |
| 26JUL08MILMIS-MIS | ITF_W | 07/08 04:37 | W1? | 92 | 84 @ 07/08 11:30 (ask) | +8 | NO_TAPE* | join | 0 | OPEN, exit resting @98; band dist +14 (last 84) | D | naked(crash-orphan) |
| 26JUL08SOLRAS-RAS | ITF_W | 07/08 04:38 | W1? | 41 | 8 @ 07/08 05:41 (sf) | +33 | REPRICE* | join | 0 | SETTLED no -41.0c/sh | F | naked(crash-orphan) |
| 26JUL08MILEZZ-EZZ | ITF_W | 07/08 04:39 | W1? | 56 | 53 @ 07/08 04:40 (sf) | +3 | DIVOT* | join | 0 | SETTLED yes +44.0c/sh | B | naked(crash-orphan) |
| 26JUL08DEPGAR-GAR | ITF_W | 07/08 04:39 | W1? | 45 | 27 @ 07/08 04:39 (sf) | +18 | REPRICE* | join | 1 | SETTLED no -45.0c/sh | F | naked(crash-orphan) |
| 26JUL08DENSIM-DEN | ITF_W | 07/08 04:40 | W1? | 82 | 66 @ 07/08 04:58 (sf) | +16 | REPRICE* | join | 2 | SETTLED yes +18.0c/sh | B | naked(crash-orphan) |
| 26JUL08NEWCOU-NEW | ITF_W | 07/08 04:41 | W1? | 60 | 48 @ 07/08 05:03 (sf) | +12 | REPRICE* | join | 0 | SETTLED no -60.0c/sh | F | naked(crash-orphan) |
| 26JUL08KNUSHI-KNU | ITF_W | 07/08 04:42 | W1? | 40 | 35 @ 07/08 04:45 (sf) | +5 | REPRICE* | join | 0 | SETTLED no -40.0c/sh | F | naked(crash-orphan) |
| 26JUL08WIEORT-WIE | ITF_W | 07/08 04:43 | W1? | 74 | 53 @ 07/08 05:03 (sf) | +21 | DIVOT* | join | 0 | SETTLED yes +26.0c/sh | B | naked(crash-orphan) |
| 26JUL08DILSAV-SAV | ITF_W | 07/08 04:44 | W1? | 39 | 39 @ 07/08 04:44 (sf) | +0 | REPRICE* | join | 0 | SETTLED no -39.0c/sh | F | naked(crash-orphan) |
| 26JUL08DEPGAR-DEP | ITF_W | 07/08 04:46 | W2~ | 54 | 57 @ 07/08 04:39 (pr) | -3 | DIVOT* | join | 2 | SETTLED yes +46.0c/sh | B | naked(crash-orphan) |
| 26JUL08ILIPOP-ILI | ITF_W | 07/08 04:56 | window-uncertain | 24 | 27 @ 07/08 02:33 (ask) | -3 | REPRICE* | join | 1 | SETTLED no -24.0c/sh | F | naked(crash-orphan) |
| 26JUL08TRETSY-TSY | ITF_W | 07/08 05:01 | W1? | 26 | 15 @ 07/08 07:45 (sf) | +11 | NO_TAPE* | join | 0 | SETTLED no -26.0c/sh | F | naked(crash-orphan) |
| 26JUL08PRIVON-VON | ITF_W | 07/08 05:08 | W1? | 61 | 61 @ 07/08 05:08 (sf) | +0 | REPRICE* | join | 2 | SETTLED yes +39.0c/sh | B | naked(crash-orphan) |
| 26JUL08TRICEN-CEN | ITF_W | 07/08 05:09 | window-uncertain | 91 | 91 @ 07/08 04:45 (sf) | +0 | NO_UNDERCUT* | join | 3 | SETTLED yes +9.0c/sh | B | naked(crash-orphan) |
| 26JUL08TRICEN-TRI | ITF_W | 07/08 05:10 | W1? | 8 | 2 @ 07/08 05:37 (sf) | +6 | REPRICE* | improve1 | 2 | SETTLED no -8.0c/sh | F | naked(crash-orphan) |
| 26JUL08VANWON-VAN | ITF_W | 07/08 05:13 | W2~ | 44 | 47 @ 07/08 00:07 (pr) | -3 | REPRICE* | join | 0 | SETTLED yes +56.0c/sh | B | naked(crash-orphan) |
| 26JUL08PAPCAP-CAP | ITF_W | 07/08 05:13 | W1? | 51 | 48 @ 07/08 05:16 (sf) | +3 | DIVOT* | join | 0 | SETTLED yes +49.0c/sh | B | naked(crash-orphan) |
| 26JUL08CHOKOS-CHO | ITF_W | 07/08 05:14 | W1? | 65 | 50 @ 07/08 05:14 (sf) | +15 | DIVOT* | join | 0 | SETTLED yes +35.0c/sh | B | naked(crash-orphan) |
| 26JUL08PAWLAZ-LAZ | ITF_W | 07/08 05:14 | W2~ | 21 | 25 @ 07/08 03:57 (pr) | -4 | REPRICE* | join | 1 | SETTLED no -21.0c/sh | F | naked(crash-orphan) |
| 26JUL08PAPCAP-PAP | ITF_W | 07/08 05:22 | W2~ | 47 | 50 @ 07/08 05:12 (sf) | -3 | REPRICE* | improve1 | 1 | SETTLED no -47.0c/sh | F | naked(crash-orphan) |
| 26JUL08MILMIS-MIL | ITF_W | 07/08 05:32 | W2~ | 6 | 8 @ 07/07 17:01 (ask) | -2 | REPRICE* | join | 1 | EXIT_FILLED @13 (W2, taker-swept) +7.0c/sh | A | naked(crash-orphan) |
| 26JUL08WIEORT-ORT | ITF_W | 07/08 05:37 | W2~ | 21 | 38 @ 07/08 05:03 (sf) | -17 | REPRICE* | join | 0 | SETTLED no -21.0c/sh | F | naked(crash-orphan) |
| 26JUL08DENSIM-SIM | ITF_W | 07/08 05:38 | W2~ | 13 | 13 @ 07/08 00:37 (sf) | +0 | REPRICE* | join | 0 | SETTLED no -13.0c/sh | F | naked(crash-orphan) |
| 26JUL08PAVAGR-PAV | ITF_W | 07/08 05:39 | W2~ | 94 | 95 @ 07/08 03:17 (pr) | -1 | DIVOT* | join | 4 | SETTLED yes +6.0c/sh | B | naked(crash-orphan) |
| 26JUL08YESGAN-GAN | ITF_W | 07/08 05:55 | W1? | 45 | 44 @ 07/08 06:51 (sf) | +1 | DIVOT* | join | 0 | SETTLED yes +55.0c/sh | B | naked(crash-orphan) |
| 26JUL08LIUMAL-LIU | ITF_W | 07/08 05:56 | W2~ | 26 | 29 @ 07/08 00:26 (pr) | -3 | REPRICE* | join | 0 | SETTLED no -26.0c/sh | F | naked(crash-orphan) |
| 26JUL08ZHILEE-ZHI | ITF_W | 07/08 06:03 | W2~ | 12 | 15 @ 07/08 05:17 (pr) | -3 | DIVOT* | join | 0 | SETTLED no -12.0c/sh | F | naked(crash-orphan) |
| 26JUL08SOBBEN-BEN | ITF_W | 07/08 06:03 | W1? | 25 | 11 @ 07/08 06:47 (sf) | +14 | REPRICE* | join | 0 | SETTLED no -25.0c/sh | F | naked(crash-orphan) |
| 26JUL08ZHILEE-LEE | ITF_W | 07/08 06:08 | W1? | 84 | 82 @ 07/08 06:19 (sf) | +2 | REPRICE* | join | 0 | SETTLED yes +16.0c/sh | B | naked(crash-orphan) |
| 26JUL08PRIKAR-PRI | ITF_W | 07/08 06:08 | W2~ | 52 | 52 @ 07/08 04:04 (sf) | +0 | DIVOT* | join | 0 | SETTLED no -52.0c/sh | F | naked(crash-orphan) |
| 26JUL08KOVSTO-KOV | ITF_W | 07/08 06:09 | W2~ | 61 | 64 @ 07/08 06:02 (pr) | -3 | DIVOT* | join | 0 | SETTLED yes +39.0c/sh | B | naked(crash-orphan) |
| 26JUL08STEVAN-VAN | ITF_W | 07/08 06:10 | W1? | 35 | 16 @ 07/08 06:40 (sf) | +19 | REPRICE* | improve1 | 1 | SETTLED no -35.0c/sh | F | naked(crash-orphan) |
| 26JUL08STEVAN-STE | ITF_W | 07/08 06:12 | W1? | 63 | 63 @ 07/08 06:12 (sf) | +0 | NO_UNDERCUT* | join | 1 | SETTLED yes +37.0c/sh | B | naked(crash-orphan) |
| 26JUL08REVHRU-HRU | ITF_W | 07/08 06:13 | W1? | 94 | 94 @ 07/08 06:13 (sf) | +0 | DIVOT* | join | 6 | SETTLED yes +6.0c/sh | B | naked(crash-orphan) |
| 26JUL08ERCLEM-ERC | ITF_W | 07/08 06:15 | W2~ | 34 | 36 @ 07/08 00:09 (pr) | -2 | DIVOT* | join | 0 | SETTLED yes +66.0c/sh | B | naked(crash-orphan) |
| 26JUL08ABOFOU-ABO | ITF_W | 07/08 06:18 | window-uncertain | 28 | 29 @ 07/08 06:18 (pr) | -1 | REPRICE* | join | 1 | SETTLED no -28.0c/sh | F | naked(crash-orphan) |
| 26JUL08VOLKUZ-KUZ | ITF_W | 07/08 06:20 | W1? | 46 | 26 @ 07/08 06:34 (sf) | +20 | REPRICE* | join | 0 | SETTLED no -46.0c/sh | F | naked(crash-orphan) |
| 26JUL08KOVSTO-STO | ITF_W | 07/08 06:21 | W2~ | 37 | 39 @ 07/08 00:37 (pr) | -2 | DIVOT* | join | 0 | SETTLED no -37.0c/sh | F | naked(crash-orphan) |
| 26JUL08ERCLEM-LEM | ITF_W | 07/08 06:24 | W2~ | 63 | 65 @ 07/07 17:02 (ask) | -2 | REPRICE* | join | 0 | SETTLED no -63.0c/sh | F | naked(crash-orphan) |
| 26JUL08ABOFOU-FOU | ITF_W | 07/08 06:24 | W1? | 68 | 68 @ 07/08 06:24 (sf) | +0 | NO_UNDERCUT* | join | 0 | SETTLED yes +32.0c/sh | B | naked(crash-orphan) |
| 26JUL08PRIVON-PRI | ITF_W | 07/08 06:25 | W2~ | 37 | 44 @ 07/08 05:19 (sf) | -7 | REPRICE* | join | 1 | SETTLED no -37.0c/sh | F | naked(crash-orphan) |
| 26JUL08CIRBRE-BRE | ITF_W | 07/08 06:25 | W2~ | 11 | 13 @ 07/08 03:14 (pr) | -2 | REPRICE* | join | 1 | SETTLED no -11.0c/sh | F | naked(crash-orphan) |
| 26JUL08JORNOE-JOR | ITF_W | 07/08 06:29 | W2~ | 88 | 92 @ 07/07 17:50 (ask) | -4 | REPRICE* | join | 0 | SETTLED no -88.0c/sh | F | naked(crash-orphan) |
| 26JUL08PRIKAR-KAR | ITF_W | 07/08 06:30 | W2~ | 44 | 48 @ 07/08 05:01 (pr) | -4 | REPRICE* | join | 1 | SETTLED yes +56.0c/sh | B | naked(crash-orphan) |
| 26JUL08YODKEN-KEN | ITF_W | 07/08 06:44 | W1? | 18 | 6 @ 07/08 06:57 (sf) | +12 | REPRICE* | join | 1 | SETTLED no -18.0c/sh | F | naked(crash-orphan) |
| 26JUL08LUENAT-LUE | ITF_W | 07/08 06:45 | W1? | 53 | 53 @ 07/08 06:45 (sf) | +0 | DIVOT* | join | 1 | EXIT_FILLED @85 (W2, taker-swept) +32.0c/sh | A? | naked(crash-orphan) |
| 26JUL08PROBAR-PRO | ITF_W | 07/08 06:55 | W1? | 14 | 3 @ 07/08 07:48 (sf) | +11 | REPRICE* | join | 0 | SETTLED no -14.0c/sh | F | naked(crash-orphan) |
| 26JUL08LUENAT-NAT | ITF_W | 07/08 06:59 | window-uncertain | 41 | 47 @ 07/08 06:57 (sf) | -6 | REPRICE* | join | 0 | OPEN, exit resting @49; band dist +38 (last 11) | C | naked(crash-orphan) |
| 26JUL08SIEKUH-SIE | ITF_W | 07/08 07:00 | W1? | 71 | 61 @ 07/08 08:24 (sf) | +10 | NO_TAPE* | join | 0 | SETTLED no -71.0c/sh | F | naked(crash-orphan) |
| 26JUL08LUKAVD-LUK | ITF_W | 07/08 07:03 | W1? | 38 | 38 @ 07/08 07:03 (sf) | +0 | REPRICE* | improve1 | 1 | SETTLED no -38.0c/sh | F | naked(crash-orphan) |
| 26JUL08LUKAVD-AVD | ITF_W | 07/08 07:12 | W1? | 62 | 57 @ 07/08 07:16 (sf) | +5 | DIVOT* | join | 1 | SETTLED yes +38.0c/sh | B | naked(crash-orphan) |
| 26JUL08TRETSY-TRE | ITF_W | 07/08 07:15 | W1? | 71 | 66 @ 07/08 07:31 (sf) | +5 | DIVOT* | join | 0 | SETTLED yes +29.0c/sh | B | naked(crash-orphan) |
| 26JUL08PAHSCH-PAH | ITF_W | 07/08 08:06 | W1? | 59 | 34 @ 07/08 08:26 (sf) | +25 | REPRICE* | join | 1 | SETTLED yes +41.0c/sh | B | naked(crash-orphan) |
| 26JUL08PAHSCH-SCH | ITF_W | 07/08 08:08 | W2~ | 39 | 43 @ 07/08 05:41 (pr) | -4 | DIVOT* | join | 0 | SETTLED no -39.0c/sh | F | naked(crash-orphan) |
| 26JUL08SIEKUH-KUH | ITF_W | 07/08 08:15 | W2~ | 24 | 27 @ 07/08 06:45 (pr) | -3 | DIVOT* | join | 0 | SETTLED yes +76.0c/sh | B | naked(crash-orphan) |
| 26JUL08PROBAR-BAR | ITF_W | 07/08 08:24 | W2~ | 82 | 89 @ 07/08 07:30 (sf) | -7 | DIVOT* | join | 0 | SETTLED yes +18.0c/sh | B | naked(crash-orphan) |
| 26JUL08MAXABA-MAX | ITF_W | 07/08 11:36 | W1? | 67 | 43 @ 07/08 11:53 (sf) | +24 | REPRICE | join | 0 | OPEN, exit resting @84; band dist +32 (last 52) | D | naked(wave2-adopt) |
| 26JUL08MAXABA-ABA | ITF_W | 07/08 11:39 | W1? | 29 | 29 @ 07/08 11:39 (sf) | +0 | NO_UNDERCUT | below_chain | 1 | EXIT_FILLED @35 (W1?, maker) +6.0c/sh | S? | — |

## Per-category summary

**ATP_CHALL** — n=20 legs | median gap +0 | windows: W2~ 13, W1? 6, window-uncertain 1
- class mix: REPRICE* 6, DIVOT* 6, AMBIG 4, NO_UNDERCUT 1, NO_UNDERCUT* 1, NO_TAPE* 1, REPRICE 1
- grade mix: A 1, A? 1, B 6, C 1, D 3, F 8
- outcomes: 2 exited, 6 settled-winner, 8 settled-loser, 4 still open | naked-class 18/20

**WTA_CHALL** — n=22 legs | median gap -1 | windows: W2~ 15, W1? 4, window-uncertain 3
- class mix: REPRICE* 8, DIVOT* 4, NO_TAPE* 3, NO_UNDERCUT* 3, AMBIG 2, AMBIG* 1, REPRICE 1
- grade mix: A 2, A? 1, B 8, C 2, D 1, F 8
- outcomes: 3 exited, 8 settled-winner, 8 settled-loser, 3 still open | naked-class 20/22

**ITF_M** — n=124 legs | median gap +0 | windows: W2~ 56, W1? 55, window-uncertain 12, W2 1
- class mix: REPRICE* 46, DIVOT* 37, REPRICE 8, AMBIG 8, NO_UNDERCUT* 8, NO_UNDERCUT 7, DIVOT 4, NO_TAPE* 4, AMBIG* 2
- grade mix: S 1, A 9, A? 2, B 51, D 1, F 60
- outcomes: 19 exited, 44 settled-winner, 59 settled-loser, 1 still open | naked-class 97/124

**ITF_W** — n=127 legs | median gap +0 | windows: W1? 74, W2~ 49, window-uncertain 4
- class mix: REPRICE* 41, DIVOT* 22, REPRICE 20, AMBIG 14, NO_UNDERCUT* 11, NO_UNDERCUT 9, NO_TAPE* 5, DIVOT 4, AMBIG* 1
- grade mix: S? 8, A 13, A? 12, B 45, C 1, D 2, F 46
- outcomes: 41 exited, 37 settled-winner, 46 settled-loser, 3 still open | naked-class 81/127

**ALL** — n=293 | median gap +0 | grade mix: S 1, S? 8, A 25, A? 16, B 110, C 4, D 7, F 122 | class mix: REPRICE* 101, DIVOT* 69, REPRICE 30, AMBIG 28, NO_UNDERCUT* 23, NO_UNDERCUT 17, NO_TAPE* 13, DIVOT 8, AMBIG* 4

## Could not determine (named missing sources — not guessed)
- **Honest match starts**: no observed_start/ESPN-status events exist in either jsonl; only volume_burst latches, and none for anything that went live 02:52→11:30 ET (bot dead). Every W1/W2 call above rests on tape-onset or the kalshi schedule clock — hence the `?`/`~` flags; 20 legs had no usable anchor at all (window-uncertain). Missing source: an independent start-time feed (ESPN scoreboard) for Jul 8 03:00–11:30 ET.
- **Order-book context in the tape hole**: local premarket_ticks/trades recorders died with the disk at 02:52 ET and resumed 11:30 ET. All starred classes (210 of 293) are trades-only proxies; true DIVOT-vs-REPRICE (ask-hold test) is UNKNOWABLE for those fills. NO_TAPE* (13 legs) = too few post-fill prints even on the API tape.
- **Posture for 3 legs** (`?`): no aim_shadow line before fill and ENTRY_ROLL had `?` (bids conceived before instrumentation).
- **Queue/walk history before 07-07 01:06 ET**: the 07 jsonl starts there; walk counts for bids conceived earlier are undercounted from conception (counted from log start).
- **Fills dump is a rolling 3000-fill window** captured ~11:45 ET and refreshed during analysis (~12:30 ET data present); exits after ~12:30 ET are not in this file. SHIVUJ-SHI settled `scalar` (retirement-style settlement) — cash consequence not derivable from result field alone.
- **Bot-ledger vs exchange conflicts**: exit_filled log events on adopted positions carry fabricated exit prices (autopsy class); exchange fills used throughout, so per-leg c/sh here can disagree with the bot ledger.

## Side question (a) — [5,95) maker band-clamp: did it fire, did it hold?
- **Fired: YES.** `band_refused` fired **51 times** post-boot (all in the 07-07 file, prices 1–4 and 95–96; e.g. VAJKAR-VAJ@1, KUBSHK-KUB@95, MORBLA-BLA@96). Zero `v4_fallback_maker_clamp` / `fallback_bound_clamped` events post-boot. `bid_outside_5_95` appears only inside `post_boot_audit` payloads: 6 flag-lines at the 23:12 boot audit (pre-existing out-of-band bids, since cancelled), **0 in the 11:30 resurrection boot audit** — the book came back clean.
- **Held: NOT AIRTIGHT.** Of 639 post-boot buy `order_placed` events scanned, **29 landed outside [5,95)** (repeated ADAIMA-ADA reposts at 1–4, CAVPLO/HARMAI/BOSBOY/MANKAV/KUBSHK/TUPPAN legs at 2–4, and VAJKAR-KAR/MANKAV-MAN/KUBSHK-KUB at 95, VAJKAR-KAR at 96) — a second placement path (walk/repost) bypasses the chokepoint clamp. One of them FILLED: **HARMAI-HAR bought 5sh @4** at 23:55 ET (later exited @7, so it made money — but it is a live clamp violation). No out-of-band buy is resting as of the 11:45 dump.

## Side question (b) — the 8 LOUD tape-latch-only preflight bids (overnight outcomes)

| LOUD leg | full ticker | outcome |
|---|---|---|
| UL07MOXSAR-SAR | KXITFMATCH-26JUL07MOXSAR-SAR | FILLED 01:05 ET @27 (bot alive) → exit sell FILLED @34 02:38 ET (+7c/sh); market finalized YES. |
| UL08IUSSAG-IUS | KXITFWMATCH-26JUL08IUSSAG-IUS | FILLED 01:15 ET @66 → exit FILLED @83 01:58 ET (+17c/sh); market finalized NO (exited before the collapse). |
| UL08IUSSAG-SAG | KXITFWMATCH-26JUL08IUSSAG-SAG | FILLED 01:02 ET @31 → exit FILLED @37 by 01:21 ET (+6c/sh); market finalized YES. |
| UL08LIXYAM-LIX | KXITFWMATCH-26JUL08LIXYAM-LIX | FILLED 01:33 ET @8 → exit FILLED @11 01:37 ET (+3c/sh); market finalized NO. |
| UL08MIXKRU-MIX | KXITFWMATCH-26JUL08MIXKRU-MIX | FILLED 03:41 ET @39 **during the dead window** (naked crash-orphan) → never exited, market finalized NO = settled LOSER (−39c/sh × 5sh). The one LOUD casualty. |
| UL08WANOHX-OHX | KXITFWMATCH-26JUL08WANOHX-OHX | FILLED 02:31 ET @18 (2.25sh) + 04:01 ET @18 (2.75sh, dead window) → resting exit FILLED @23 04:07 ET (+5c/sh); market finalized NO. |
| UL08WUXSNI-SNI | KXITFWMATCH-26JUL08WUXSNI-SNI | FILLED 02:36 ET @49 → resting exit FILLED @59 02:41 ET (+10c/sh); market finalized YES. |
| UL08WUXSNI-WUX | KXITFWMATCH-26JUL08WUXSNI-WUX | FILLED 02:29 ET @48 → resting exit FILLED @58 05:18 ET dead-window (+10c/sh); market finalized NO (exited before collapse). |

All 8 LOUD bids filled overnight; 7/8 also cashed their exits (several via exit sells that kept resting through the crash and filled unattended); 1/8 (MIXKRU-MIX) filled naked in the dead window and rode to a full loss. Net the LOUD cohort was positive despite the casualty.
