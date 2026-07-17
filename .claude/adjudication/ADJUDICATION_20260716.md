# ADJUDICATION 20260716 (nightly conviction replay; gate 3a passed)


**YIELD-ON-WAGERED: +7.8% (net $+1.95 on $25 staked) vs the 8% bar** (backfill: 07-10 +1.6% · 07-11 +0.8% · 07-12 +0.1% · 07-13 −3.8%)
**REALIZED-BY-SUBTRACTION: 0 DROP-AS-PAIR refusals (0 graded, dollars-not-lost $+0.00) | seesaw: 6 refused / 0 lifted | one-sided VIOLATIONS: 0 | PACKET COUNTDOWN: n=411/300 (auto re-run 2026-07-16 10:40 PM ET; PACKET FIRED)**
**INCUMBENT-COST: $+1.95 across 12 incumbent-entered legs (attribution: trendpath_live_aim stamp)**
**BELOW-BAR NIGHT — named: settled legs $-3.15 vs exited legs $+5.10; worst categories ITF_M $-1.15, ITF_W $-0.05; diagnosis, not explanation: ride-to-zero settlements dominate — the payoff-asymmetry class**
| id | ticker | cat | fill ET | paid | cyc | grade | posterior | legacy | pnl¢ |
|---|---|---|---|---|---|---|---|---|---|
| T-20260716-0214 | ITFWMATCH-26JUL16CHAGUZ-CHA | ITF_W | 01:01:47 PM | 33 | 1 | AGREE | 0.40 |  | 35.0 |
| T-20260716-0240 | ATPCHALLENGERMATCH-26JUL16FU | ATP_CHALL | 01:27:27 PM | 80 | 1 | AGREE | 0.82 |  | 90.0 |
| T-20260716-0237 | ITFWMATCH-26JUL16MATREA-REA | ITF_W | 01:36:18 PM | 54 | 1 | WOULD-REFUSE | 0.52 |  | 60.0 |
| T-20260716-0180 | WTACHALLENGERMATCH-26JUL16KO | WTA_CHALL | 01:47:21 PM | 74 | 1 | AGREE | 0.76 |  | 90.0 |
| T-20260716-0169 | ITFWMATCH-26JUL16KOIKUR-KOI | ITF_W | 02:23:53 PM | 54 | 1 | AGREE | 0.53 |  | 60.0 |
| T-20260716-0253 | ITFMATCH-26JUL16SERBAS-SER | ITF_M | 03:26:50 PM | 10 | 1 | AGREE | 0.09 |  | 20.0 |
| T-20260716-0245 | ATPCHALLENGERMATCH-26JUL16GR | ATP_CHALL | 03:51:12 PM | 35 | 1 | AGREE | 0.40 |  | 40.0 |
| T-20260716-0179 | ITFWMATCH-26JUL16COLMAR-COL | ITF_W | 03:51:14 PM | 16 | 1 | AGREE | 0.14 |  | -80.0 |
| T-20260716-0179 | ITFWMATCH-26JUL16COLMAR-COL | ITF_W | 03:55:04 PM | 16 | 1 | WOULD-REFUSE | 0.11 |  | -80.0 |
| T-20260716-0233 | ITFMATCH-26JUL16BYNLON-LON | ITF_M | 04:18:46 PM | 31 | 1 | AGREE | 0.34 |  | -155.0 |
| T-20260716-0256 | ATPCHALLENGERMATCH-26JUL16PA | ATP_CHALL | 05:05:33 PM | 66 | 1 | AGREE | 0.65 |  | 95.0 |
| T-20260716-0247 | ITFMATCH-26JUL16NEFCOX-COX | ITF_M | 06:07:35 PM | 16 | 1 | AGREE | 0.29 |  | 20.0 |
| T-20260716-0275 | ITFMATCH-26JUL16USMMAS-USM | ITF_M | 10:15:44 PM | 20 | 1 | AGREE | 0.29 |  | open |

## LIVE-vs-REPLAY AGREEMENT (same-instrument law, live edition) — checked 12, **divergences: 1**
- **VIOLATION** T-20260716-0275: conf gap 0.37 live vs 0.26 replay (at the shadow's tick)

**REFUSE-MARGIN SHADOW (ITF_M, M16): fitted 8c would-have-saved +0¢ | decreed 2c +0¢** (held-out winner 07-11: +1170 vs -85; cutover on the operator's word)

**MIGRATION METER: fitted-conviction AGREE 11/13 (84.6%) | WOULD-REFUSE 2 | NO-OPINION 0 | pair-97 touched 0 (0.0%)**

Per category: ATP_CHALL A3/R0/N0 p97:0 | ITF_M A4/R0/N0 p97:0 | ITF_W A3/R2/N0 p97:0 | WTA_CHALL A1/R0/N0 p97:0

## COMPLETION-SHADOW (per-leg economics beside the live machinery; taker branch GATED behind operator_taker_word)

| cat | verdict | n |
|---|---|---|
| ATP_CHALL | NO-OPINION | 24 |
| ATP_CHALL | hold | 3 |
| ATP_CHALL | taker_complete | 25 |
| ITF_M | NO-OPINION | 74 |
| ITF_M | flatten_kept | 5 |
| ITF_M | hold | 2 |
| ITF_M | taker_complete | 1 |
| ITF_W | NO-OPINION | 7 |
| ITF_W | flatten_kept | 5 |
| ITF_W | hold | 1 |
| WTA_CHALL | NO-OPINION | 12 |
| WTA_CHALL | flatten_kept | 2 |
| WTA_CHALL | hold | 1 |
| WTA_MAIN | NO-OPINION | 7 |

kept-leg EV sums (¢, two-term frame, win-ride residual excluded): ATP_CHALL -48 | ITF_M -17 | ITF_W -13 | WTA_CHALL -2

## COMPLETION LIVE-vs-SHADOW (operator word 07-12; the same-instrument law, completion edition) — actions: 3, divergences: 6
- action taker_complete → refused on KXATPCHALLENGERMATCH-26JUL15YIBYUN
- action taker_complete → refused on KXITFMATCH-26JUL16SERBAS
- action flatten_kept → flattening on KXITFWMATCH-26JUL16COLMAR
- **VIOLATION** shadow said flatten_kept on KXITFWMATCH-26JUL16MATREA but NO action followed
- **VIOLATION** shadow said flatten_kept on KXWTACHALLENGERMATCH-26JUL16KOVRIE but NO action followed
- **VIOLATION** shadow said flatten_kept on KXITFWMATCH-26JUL16KOIKUR but NO action followed
- **VIOLATION** shadow said flatten_kept on KXITFMATCH-26JUL16BYNLON but NO action followed
- **VIOLATION** shadow said flatten_kept on KXITFMATCH-26JUL16NEFCOX but NO action followed
- **VIOLATION** shadow said flatten_kept on KXITFMATCH-26JUL16USMMAS but NO action followed

## LIVE-AIM SHADOW (fourth design, night 20260716) — graded 2 (accruing toward the n>=300 cutover bar)
- ITF_W: n=2 | shadow $+0.00 | live $+0.00

## SELECTOR (C-CONTENTION-LAW: the path decides WHAT we trade) — would-have slate vs actual, vs the 8% bar
- ATP_CHALL: TRADE 4 / DROP 3 / NO-OPINION 0 | would-have $+0.00 on $0 staked (—, 0 graded) | actual slate $+2.25 on $9 (+24.9%)
- ATP_MAIN: TRADE 0 / DROP 1 / NO-OPINION 0 | would-have $+0.00 on $0 staked (—, 0 graded) | actual slate $+0.00 on $0 (—)
- ITF_M: TRADE 29 / DROP 13 / NO-OPINION 0 | would-have $+0.00 on $0 staked (—, 0 graded) | actual slate $-1.15 on $4 (-31.2%)
- ITF_W: TRADE 48 / DROP 0 / NO-OPINION 0 | would-have $+0.00 on $0 staked (—, 0 graded) | actual slate $+0.75 on $9 (+8.7%)
- WTA_CHALL: TRADE 1 / DROP 1 / NO-OPINION 0 | would-have $+0.00 on $0 staked (—, 0 graded) | actual slate $+0.90 on $4 (+24.3%)
- **DROP list** (leg | contention %% | actual): 26JUL16DRAMIL-DRA -5.4% untraded; 26JUL16RICGEA-GEA 0.4% untraded; 26JUL16SMIMAT-SMI 0.4% untraded; 26JUL16MOLDAV-MOL -5.2% untraded; 26JUL16ABDVUX-VUX 6.8% untraded; 26JUL16ALHMOG-MOG 6.8% untraded; 26JUL16ALHYAZ-ALH 6.8% untraded; 26JUL16ALHYAZ-YAZ 6.8% untraded; 26JUL16BEAVII-BEA 6.6% untraded; 26JUL16BECANT-ANT 7.4% untraded; 26JUL16BOBOCO-BOB 6.6% untraded; 26JUL16CHALIM-CHA 6.8% untraded | dropped legs the bot DID trade: $+0.00

## CONSULTATION CENSUS (C-VAULT-WIRED-ENTRY: 296 dossiers across sites {'?': 4, 'refused': 133, 'placed': 159})
- atlas_page           {'CONSULTED': 292}
- contention_selector  {'CONSULTED': 292}
- pair_state           {'CONSULTED': 292}
- reach_law            {'NOT-APPLICABLE': 134, 'CONSULTED': 158}
- range_cell_m15       {'GAP': 292}
- dip_timing           {'CONSULTED': 292}
- flow_state           {'NOT-APPLICABLE': 99, 'CONSULTED': 193}
- refuse_margins       {'CONSULTED': 292}
- operator_adjudications {'CONSULTED': 292}
- fill_regime          {'CONSULTED': 292}
- honest_clock         {'CONSULTED': 292}
- shadow_range_shape   {'SHADOW': 292}
- w1_cohort            {'SHADOW': 292}
- window_phase         {'CONSULTED': 292}
- W1-COHORT CALIBRATION (shadow): predicted dip_freq mean 0.60 vs realized 0.64 across 267 graded legs
- **GAPS -> board items (the intake list): range_cell_m15 (entry-band mapping unfitted (completion-frame bands only) — vault intake item); cash_window (no fitted gun-axis lawful_share for this cohort — cash-window unpriceable, named)**

## WINDOW LEDGER (C-WINDOW-LAW: W1 / CORRIDOR / W2 — no night grades without the split)
- ATP_CHALL: entries[W1:0 C:0 W2:0 U:0] refusals[W1:0 C:0 W2:0 U:0] touches[W1:0 C:0 W2:0 U:0] fills[W1:0 C:0 W2:0 U:0] cash[W1:0 C:0 W2:0 U:0] rode[W1:1 C:0 W2:1 U:1] cancels[W1:0 C:0 W2:0 U:0]
- ITF_M: entries[W1:0 C:0 W2:0 U:0] refusals[W1:0 C:0 W2:0 U:0] touches[W1:0 C:0 W2:0 U:0] fills[W1:0 C:0 W2:0 U:0] cash[W1:0 C:0 W2:0 U:0] rode[W1:0 C:0 W2:1 U:0] cancels[W1:0 C:0 W2:0 U:0]
- ITF_W: entries[W1:0 C:0 W2:0 U:0] refusals[W1:0 C:0 W2:0 U:0] touches[W1:0 C:0 W2:0 U:0] fills[W1:0 C:0 W2:0 U:0] cash[W1:0 C:0 W2:0 U:0] rode[W1:0 C:0 W2:3 U:0] cancels[W1:0 C:0 W2:0 U:0]
- WTA_CHALL: entries[W1:0 C:0 W2:0 U:0] refusals[W1:0 C:0 W2:0 U:0] touches[W1:0 C:0 W2:0 U:0] fills[W1:0 C:0 W2:0 U:0] cash[W1:0 C:0 W2:0 U:0] rode[W1:0 C:0 W2:2 U:0] cancels[W1:0 C:0 W2:0 U:0]
- WTA_MAIN: entries[W1:0 C:0 W2:0 U:0] refusals[W1:0 C:0 W2:0 U:0] touches[W1:0 C:0 W2:0 U:0] fills[W1:0 C:0 W2:0 U:0] cash[W1:0 C:0 W2:0 U:0] rode[W1:0 C:1 W2:0 U:0] cancels[W1:0 C:0 W2:0 U:0]
- GUN-FEED: last new in-play sighting 308 min ago (observed_starts.db) **> 30 min — TRIPWIRE**

## THE THREE-BUCKET ENTRY GRADE (THE DAILY STANDARD Layer 1 — SETTLED / OPEN / POSTED-UNFILLED, window-stamped, per category)
- ATP_CHALL: SETTLED 3 {'F(W2-entry)': 3} (Σ+225c) | OPEN 0 (exits resting per audit) | POSTED-UNFILLED 7 (+ refusals: {'refused:below_leg_floor': 100, 'refused:w1_preference': 25, 'refused:below_discovery_floor': 8})
- ATP_MAIN: SETTLED 0 {} (Σ+0c) | OPEN 0 (exits resting per audit) | POSTED-UNFILLED 1 (+ refusals: …)
- ITF_M: SETTLED 3 {'F(W2-entry)': 3} (Σ-115c) | OPEN 1 (exits resting per audit) | POSTED-UNFILLED 41 (+ refusals: …)
- ITF_W: SETTLED 4 {'F(W2-entry)': 4} (Σ+75c) | OPEN 0 (exits resting per audit) | POSTED-UNFILLED 48 (+ refusals: …)
- WTA_CHALL: SETTLED 1 {'F(W2-entry)': 1} (Σ+90c) | OPEN 0 (exits resting per audit) | POSTED-UNFILLED 2 (+ refusals: …)

## GRACE CENSUS (per-source grace, C-DAILY-STANDARD Part 0 — tape_flow 60s / others 300s)
- source fallback_bell: 11 graced windows @ 300s
- source percat_fitted: 39 graced windows @ 300s
- source tape_flow: 2 graced windows @ 60s

## EXPRESSION COHORT (C-EXPRESS-THE-EDGE — separate from day one, never blended)
- cohort empty (expression not armed / staged)

## THE STANDARD CENSUS (a layer that didn't run = named defect, auto-boarded)
- OT_wiring          RAN — 24 wirings armed / 0 missing
- TS_render          RAN — clean render (70192 bytes)
- L1_three_bucket    RAN — 12 fills / 100 placements graded
- L2_game_reports    RAN — 66 game reports in 20260716
- L3_cash_window     RAN — 292 dossiers carry the cash-window stamp
- P0_grace_census    RAN — 3 sources graced

## TAPE GATE (C-TAPE-GATE: re-earned nightly or revoked) — skips 1 ({'band_cashed': 1, 'won': 0, 'lost': 0, 'open': 0}, realized $+0.60) | below-basis flattens kept 0

## GOVERNOR SPLIT (whose hand moved — actions | exit ¢ attributed | avg band)
- per_leg_policy: 6 actions | +0¢ | band —
- pair97_bound: 238 actions | +0¢ | band —
- maker_exit: 13 actions | +575¢ | band +10.5c (n=11)
- match_live_cancel: 64 actions | +0¢ | band —

## SUNSET LEDGER (post-cutover 07-14, operator word: the incumbent's organs and what replaced them)
- static aim tables -> DELETED from the entry path (cutover 07-14): path aims are THE law; no fitted page = no entry (no_path_page_refused, named)
- join-the-market walking -> DELETED (path_mode_hold): the bid rests at its fitted aim — get paid, not filled
- 97-remainder completion pricing -> remainder-as-TARGET DELETED; the sibling's path aim prices the bid; the C-BOUND remainder CEILING retained (operator adjudication 07-05)
- leg-level entry permission -> PAIR-LAW (orientation-composition + seesaw lift): LIVE 07-15
- static 5-lot sizing -> sizing engine v0 (sizing_live): DARK | awaiting the operator's SEPARATE sizing word (drawdown floor still a named placeholder)
- undirected placement -> orientation layer (orientation_live): DARK | tells' own clock (week: 8% coverage, n=8/300) — layers in when its bar clears

## FULL-SLATE SUMMARY
FULL-SLATE: steps FITTED 46%/DECREED 44%/NAKED 12 | no-fill 22 (starved 15) | xt-violations 70
