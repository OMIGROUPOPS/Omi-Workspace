# THE 81 DECISION-CHAIN LEDGER — per game, no aggregates

Analysis seat only. Read-only over frozen receipts. Built 2026-08-11.

| basis | commit |
|---|---|
| STANDABILITY_V2 (the 81 freeze) | `fe4747cd915830dc16f41c6bbec5e0ca1c14d99c` |
| v1 anatomy (the 62 + top10) | `3dd57fbad16b5eb068d5e1a3de9bd9a4a31e8aff` |
| V47 operative baseline | `fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34` |
| V49 evidenced-level standing (BLOCKED) | `1c8700fad871061890cbf41ea9f236002c06dc2e` |

## THE FINDING FIRST — the 81 are frozen as aggregates, not as identities

The tasking premise "the 81 window-law games are listed in STANDABILITY_V2" is **false**. `fe4747cd` freezes the 81 **only as aggregates** (81 games / 1,162c / 34-10-30-7 by category). It emits identities for exactly **20** legs (the WINDOW_LAWFUL_EVIDENCE re-cut). V49's own conversion receipt states it verbatim: *"THE_FE4747CD_RECEIPT_FREEZES_THE_81_GAME_TARGET_AS_AGGREGATES_BUT_DOES_NOT_EMIT_ALL_81_IDENTITIES; V49_DOES_NOT_FABRICATE_AN_INTERSECTION."*

What IS pinned, and how:

- **19 window-law additions — pinned exactly by conservation.** The 20 WINDOW_LAWFUL_EVIDENCE games minus `26JUL13KABPER` (its PER leg is WINDOW_BARE_PREDICTION, so the game does not join). Category deltas v1->v2 (+10 ATP_CHALL / +0 ATP_MAIN / +7 WTA_CHALL / +2 WTA_MAIN) match this set **exactly**, including the KABPER exclusion.
- **10 of the v1-62 — pinned by `top_recoverable`** in THE_183_ANATOMY (`3dd57fba`).
- **52 of the v1-62 — NOT reconstructible from committed receipts.** The v1 instant-law needs ask-at-print per missing leg; that exists only in the private fit-local tape (SOURCE_HASH_MANIFEST `private_prints`, hash-only, 1.77 GB). Two independent receipted proxies were tried and both fail the frozen aggregates: (a) V47 seller-hit-at-P criterion -> 76 games, wrong category mix, 338c vs 1,162c; (b) the committed 896-leg regret tables cover only 83/328 gap legs with matching lows (earlier window basis). The 52 rows below are therefore **conserved slots, named as unreceipted** — not fabricated identities.

Machine-check anchors reproduced from receipts before any row was written: V47 completed **396** (= frozen receipt), V49 completed **393** (= frozen receipt), traded-floor under-par universe **711** (= THE_315_GAP_MAP), gap **315** (= 711-396).

## The 81 rows

P = evidenced/target level per the freezing receipt; lock = 100 - (machine-window lowest true trade per leg), 1c8700fa window basis. Identity status: **W** = window-law addition (pinned), **T** = v1 top_recoverable (pinned), **U** = unreceipted slot.

| # | game | cat | id | missing leg(s): P | window | V47 | V49 | V49 non-convert reason (named) | lock c |
|--:|---|---|:-:|---|--:|---|---|---|--:|
| 1 | 26JUL12AZKLEO | ATP_CHALL | W | AZK: 49; LEO: 47 | 23723s | NONE (AZK,LEO uncalled) | NONE (AZK,LEO uncalled) | bid-1 offset at P; bid-1 offset at P | 4 |
| 2 | 26JUL12FANBIG | ATP_CHALL | W | FAN: 35 | 17563s | ONE_LEG 64c (FAN uncalled) | ONE_LEG 64c (FAN uncalled) | at/above P; tick-cause unreceipted | 3 |
| 3 | 26JUL13DONWES | ATP_CHALL | W | WES: 73 | 12023s | ONE_LEG 26c (WES uncalled) | COMPLETED 99c | CONVERTED | 2 |
| 4 | 26JUL13PERTOB | ATP_CHALL | W | TOB: 45 | 12247s | ONE_LEG 52c (TOB uncalled) | ONE_LEG 52c (TOB uncalled) | bid-1 offset at P | 4 |
| 5 | 26JUL14GENPET | ATP_CHALL | W | PET: 37 | 3739s | ONE_LEG 61c (PET uncalled) | ONE_LEG 61c (PET uncalled) | rest clamped 4c under P | 4 |
| 6 | 26JUL19DJOMAT | ATP_CHALL | W | MAT: 84 | 21998s | ONE_LEG 11c (MAT uncalled) | ONE_LEG 13c (MAT uncalled) | bid-1 offset at P | 12 |
| 7 | 26JUL19SINMAT | ATP_CHALL | W | SIN: 31 | 13860s | ONE_LEG 68c (SIN uncalled) | ONE_LEG 68c (SIN uncalled) | bid-1 offset at P | 7 |
| 8 | 26JUL20CHABOU | ATP_CHALL | W | BOU: 39 | 21658s | ONE_LEG 60c (BOU uncalled) | ONE_LEG 40c (CHA uncalled) | bid-1 offset at P; sibling flip | 1 |
| 9 | 26JUL20STAMAT | ATP_CHALL | W | MAT: 61 | 13419s | ONE_LEG 38c (MAT uncalled) | ONE_LEG 38c (MAT uncalled) | bid-1 offset at P | 2 |
| 10 | 26JUL20VALGOM | ATP_CHALL | W | VAL: 14 | 16142s | ONE_LEG 81c (VAL uncalled) | ONE_LEG 81c (VAL uncalled) | evidence ceiling 4c above P | 5 |
| 11 | 26JUL12MALTUR | WTA_CHALL | W | MAL: 53 | 1106s | ONE_LEG 46c (MAL uncalled) | COMPLETED 99c | CONVERTED | 5 |
| 12 | 26JUL13KOTURG | WTA_CHALL | W | KOT: 32 | 17212s | ONE_LEG 67c (KOT uncalled) | ONE_LEG 67c (KOT uncalled) | evidence ceiling 3c above P | 4 |
| 13 | 26JUL13SELYAN | WTA_CHALL | W | YAN: 39 | 16110s | ONE_LEG 59c (YAN uncalled) | ONE_LEG 42c (SEL uncalled) | rest clamped 2c under P; sibling flip | 2 |
| 14 | 26JUL16BASRUS | WTA_CHALL | W | RUS: 32 | 7336s | ONE_LEG 66c (RUS uncalled) | ONE_LEG 66c (RUS uncalled) | bid-1 offset at P | 2 |
| 15 | 26JUL17JONNOH | WTA_CHALL | W | NOH: 38 | 8574s | ONE_LEG 61c (NOH uncalled) | ONE_LEG 62c (NOH uncalled) | rest clamped 2c under P | 1 |
| 16 | 26JUL20KABCHI | WTA_CHALL | W | CHI: 77 | 8648s | ONE_LEG 20c (CHI uncalled) | COMPLETED 98c | CONVERTED | 3 |
| 17 | 26JUL20TOTRUG | WTA_CHALL | W | RUG: 55 | 3105s | ONE_LEG 44c (RUG uncalled) | COMPLETED 99c | CONVERTED | 1 |
| 18 | 26JUL12HERKAZ | WTA_MAIN | W | HER: 46 | 7740s | ONE_LEG 46c (HER uncalled) | ONE_LEG 46c (HER uncalled) | bid-1 offset at P | 8 |
| 19 | 26JUL20LYSVAL | WTA_MAIN | W | LYS: 30 | 787s | ONE_LEG 67c (LYS uncalled) | ONE_LEG 67c (LYS uncalled) | rest clamped 2c under P | 4 |
| 20 | 26JUL18BASBOE | WTA_CHALL | T | BAS: 94 | -- | ONE_LEG 5c (BAS uncalled) | ONE_LEG 5c (BAS uncalled) | -- | 2 |
| 21 | 26JUL13JONSPI | WTA_CHALL | T | JON: 91 | -- | ONE_LEG 8c (JON uncalled) | ONE_LEG 8c (JON uncalled) | -- | 42 |
| 22 | 26JUL13KNUKUR | WTA_CHALL | T | KNU: 84 | -- | ONE_LEG 9c (KNU uncalled) | ONE_LEG 9c (KNU uncalled) | -- | 6 |
| 23 | 26JUL16KHOPRO | WTA_CHALL | T | PRO: 84 | -- | ONE_LEG 15c (PRO uncalled) | ONE_LEG 15c (PRO uncalled) | -- | 0 |
| 24 | 26JUL14ZHUYUN | ATP_CHALL | T | YUN: 78 | -- | ONE_LEG 9c (YUN uncalled) | ONE_LEG 14c (YUN uncalled) | -- | 3 |
| 25 | 26JUL14MAKSEY | ATP_CHALL | T | SEY: 77 | -- | ONE_LEG 19c (SEY uncalled) | ONE_LEG 20c (SEY uncalled) | -- | 1 |
| 26 | 26JUL19RUSKAZ | WTA_MAIN | T | RUS: 75 | -- | ONE_LEG 24c (RUS uncalled) | ONE_LEG 24c (RUS uncalled) | -- | 2 |
| 27 | 26JUL12FEICHE | WTA_CHALL | T | CHE: 25; FEI: 74 | -- | NONE (CHE,FEI uncalled) | NONE (CHE,FEI uncalled) | -- | 1 |
| 28 | 26JUL13BOUZHA | ATP_CHALL | T | ZHA: 73 | -- | ONE_LEG 24c (ZHA uncalled) | ONE_LEG 24c (ZHA uncalled) | -- | 2 |
| 29 | 26JUL13OKATAR | WTA_CHALL | T | OKA: 18; TAR: 71 | -- | NONE (OKA,TAR uncalled) | ONE_LEG 85c (OKA uncalled) | -- | -2 |
| 30 | *SLOT_ATP_CHALL_01* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 31 | *SLOT_ATP_CHALL_02* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 32 | *SLOT_ATP_CHALL_03* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 33 | *SLOT_ATP_CHALL_04* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 34 | *SLOT_ATP_CHALL_05* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 35 | *SLOT_ATP_CHALL_06* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 36 | *SLOT_ATP_CHALL_07* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 37 | *SLOT_ATP_CHALL_08* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 38 | *SLOT_ATP_CHALL_09* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 39 | *SLOT_ATP_CHALL_10* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 40 | *SLOT_ATP_CHALL_11* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 41 | *SLOT_ATP_CHALL_12* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 42 | *SLOT_ATP_CHALL_13* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 43 | *SLOT_ATP_CHALL_14* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 44 | *SLOT_ATP_CHALL_15* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 45 | *SLOT_ATP_CHALL_16* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 46 | *SLOT_ATP_CHALL_17* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 47 | *SLOT_ATP_CHALL_18* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 48 | *SLOT_ATP_CHALL_19* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 49 | *SLOT_ATP_CHALL_20* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 50 | *SLOT_ATP_CHALL_21* | ATP_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 51 | *SLOT_ATP_MAIN_01* | ATP_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 52 | *SLOT_ATP_MAIN_02* | ATP_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 53 | *SLOT_ATP_MAIN_03* | ATP_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 54 | *SLOT_ATP_MAIN_04* | ATP_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 55 | *SLOT_ATP_MAIN_05* | ATP_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 56 | *SLOT_ATP_MAIN_06* | ATP_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 57 | *SLOT_ATP_MAIN_07* | ATP_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 58 | *SLOT_ATP_MAIN_08* | ATP_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 59 | *SLOT_ATP_MAIN_09* | ATP_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 60 | *SLOT_ATP_MAIN_10* | ATP_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 61 | *SLOT_WTA_CHALL_01* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 62 | *SLOT_WTA_CHALL_02* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 63 | *SLOT_WTA_CHALL_03* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 64 | *SLOT_WTA_CHALL_04* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 65 | *SLOT_WTA_CHALL_05* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 66 | *SLOT_WTA_CHALL_06* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 67 | *SLOT_WTA_CHALL_07* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 68 | *SLOT_WTA_CHALL_08* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 69 | *SLOT_WTA_CHALL_09* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 70 | *SLOT_WTA_CHALL_10* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 71 | *SLOT_WTA_CHALL_11* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 72 | *SLOT_WTA_CHALL_12* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 73 | *SLOT_WTA_CHALL_13* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 74 | *SLOT_WTA_CHALL_14* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 75 | *SLOT_WTA_CHALL_15* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 76 | *SLOT_WTA_CHALL_16* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 77 | *SLOT_WTA_CHALL_17* | WTA_CHALL | U | identity unreceipted | -- | -- | -- | -- | -- |
| 78 | *SLOT_WTA_MAIN_01* | WTA_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 79 | *SLOT_WTA_MAIN_02* | WTA_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 80 | *SLOT_WTA_MAIN_03* | WTA_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |
| 81 | *SLOT_WTA_MAIN_04* | WTA_MAIN | U | identity unreceipted | -- | -- | -- | -- | -- |

Slot rows 30-81: each is a member of the v1-62 lawfully-recoverable set (`3dd57fba`) whose identity was never emitted; category budget ATP_CHALL 21, ATP_MAIN 10, WTA_CHALL 17, WTA_MAIN 4 (= frozen 34/10/30/7 minus the 29 pinned). Naming them requires either the private fit-local tape or a re-emission by the seat that computed `3dd57fba`/`fe4747cd`.

## Conservation

- Rows: **19 (W) + 10 (T) + 52 (U) = 81 exactly.**
- Category: pinned W 10/0/7/2 + pinned T 3/0/6/1 + slots 21/10/17/4 = **34/10/30/7** (= fe4747cd freeze).
- The 46 re-cut legs conserve 20 LAWFUL + 6 BARE + 20 NO_WINDOW = 46 (fe4747cd).
- V49 vs V47 on the 20 detailed rows: 6 credited, 2 at-or-better, **4 pair conversions** (DONWES, MALTUR, KABCHI, TOTRUG) = 1c8700fa conversion receipt, reproduced row-for-row here.
- **Basis drift flagged, not hidden** — 13 pinned legs where the freezing receipt's P differs from the 1c8700fa machine-window lowest true trade (fit-local tape span vs machine W1 span). One flips under-par: OKATAR machine-window lock is **-2c** (under-par only on the fit-local basis).
  - 26JUL14GENPET PET: receipt P 37 vs machine-window low 35
  - 26JUL20STAMAT MAT: receipt P 61 vs machine-window low 60
  - 26JUL12MALTUR MAL: receipt P 53 vs machine-window low 49
  - 26JUL20LYSVAL LYS: receipt P 30 vs machine-window low 29
  - 26JUL18BASBOE BAS: receipt P 94 vs machine-window low 95
  - 26JUL13JONSPI JON: receipt P 91 vs machine-window low 51
  - 26JUL13KNUKUR KNU: receipt P 84 vs machine-window low 85
  - 26JUL16KHOPRO PRO: receipt P 84 vs machine-window low 85
  - 26JUL14ZHUYUN YUN: receipt P 78 vs machine-window low 90
  - 26JUL14MAKSEY SEY: receipt P 77 vs machine-window low 80
  - 26JUL19RUSKAZ RUS: receipt P 75 vs machine-window low 74
  - 26JUL13BOUZHA ZHA: receipt P 73 vs machine-window low 74
  - 26JUL13OKATAR TAR: receipt P 71 vs machine-window low 84

## Per-game decision chains — the 29 pinned games

### 1. 26JUL12AZKLEO [ATP_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **NONE (AZK,LEO uncalled)** -> V49: **NONE (AZK,LEO uncalled)**; machine-window lock 4c.

**AZK** — P=49 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: NOT_RECUT
1. rest in window: V47 48 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL12AZKLEO-AZK.csv.gz#row-165`); persistent join 52 (receipt `KXATPCHALLENGERMATCH-26JUL12AZKLEO-AZK.csv.gz#row-2173`); V49 48 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL12AZKLEO-AZK.csv.gz#row-165`)
2. evidence for P: V49 min evidenced standing level 45 at 1783840181 (receipt `KXATPCHALLENGERMATCH-26JUL12AZKLEO-AZK.csv.gz#row-8`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 4, 'PRIOR_TRUE_TRADE_AT_OR_BELOW_P': 3})
3. completing print: 49c at 1783847145 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling LEO at that moment: rest 50 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

**LEO** — P=47 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 46 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL12AZKLEO-LEO.csv.gz#row-3541`); persistent join 46 (receipt `KXATPCHALLENGERMATCH-26JUL12AZKLEO-LEO.csv.gz#row-3646`); V49 46 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL12AZKLEO-LEO.csv.gz#row-3541`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 46 at 1783840599 (receipt `KXATPCHALLENGERMATCH-26JUL12AZKLEO-LEO.csv.gz#row-27`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 14})
3. completing print: 47c at 1783887762 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling AZK at that moment: rest 52 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

6. V49 verdict: AZK: BID_MINUS_ONE_OFFSET_AT_P -- V49 own-bid evidence min 45 (receipt KXATPCHALLENGERMATCH-26JUL12AZKLEO-AZK.csv.gz#row-8); the persistence join rest stood at 48=P-1 when the print arrived (receipt KXATPCHALLENGERMATCH-26JUL12AZKLEO-AZK.csv.gz#row-165); the print passed 1c above the rest | LEO: BID_MINUS_ONE_OFFSET_AT_P -- fe4747cd bid_reached_P=true, V49 evidence min 46; the bid-1 tracking rest stood at 46=P-1 when the print arrived (receipt KXATPCHALLENGERMATCH-26JUL12AZKLEO-LEO.csv.gz#row-3541); the print passed 1c above the rest; ask==P at the print tick (fe4747cd), so a post-only bid at P at that tick would cross (sanity-bound collision at P)

### 2. 26JUL12FANBIG [ATP_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 64c (FAN uncalled)** -> V49: **ONE_LEG 64c (FAN uncalled)**; machine-window lock 3c.

**BIG** — P=62 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 64 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL12FANBIG-BIG.csv.gz#row-1225`); persistent join 64 (receipt `KXATPCHALLENGERMATCH-26JUL12FANBIG-BIG.csv.gz#row-1225`); V49 64 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL12FANBIG-BIG.csv.gz#row-1225`)
2. evidence for P: V49 min evidenced standing level 5 at 1783833048 (receipt `KXATPCHALLENGERMATCH-26JUL12FANBIG-BIG.csv.gz#row-15`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 3})
3. completing print: 62c at 1783839118.727 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling FAN at that moment: rest 35 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@64 (MARKET_REACH_PRINT_CROSS); V49 credited@64 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**FAN** — P=35 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 35 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL12FANBIG-FAN.csv.gz#row-1279`); persistent join 32 (receipt `KXATPCHALLENGERMATCH-26JUL12FANBIG-FAN.csv.gz#row-2058`); V49 35 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL12FANBIG-FAN.csv.gz#row-1279`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 4 at 1783827794 (receipt `KXATPCHALLENGERMATCH-26JUL12FANBIG-FAN.csv.gz#row-4`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 4})
3. completing print: 35c at 1783854017.132 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling BIG at that moment: rest 64 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@64
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

6. V49 verdict: FAN: REST_AT_OR_ABOVE_P_YET_UNCREDITED -- rest stood at 35>=P=35 from 1783839079 (receipt KXATPCHALLENGERMATCH-26JUL12FANBIG-FAN.csv.gz#row-1279); the completing print's tick-time is NOT receipted in committed artifacts (tape private, hash-only), so the at-tick non-credit cause is not derivable from receipts; 1c8700fa conversion receipt confirms uncredited

### 3. 26JUL13DONWES [ATP_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 26c (WES uncalled)** -> V49: **COMPLETED 99c**; machine-window lock 2c.

**DON** — P=25 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 26 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL13DONWES-DON.csv.gz#row-767`); persistent join 26 (receipt `KXATPCHALLENGERMATCH-26JUL13DONWES-DON.csv.gz#row-767`); V49 27 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL13DONWES-DON.csv.gz#row-658`)
2. evidence for P: V49 min evidenced standing level 22 at 1783895499 (receipt `KXATPCHALLENGERMATCH-26JUL13DONWES-DON.csv.gz#row-10`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 10})
3. completing print: 25c at 1783936618.668 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling WES at that moment: rest 72 (bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY)), direction read FALLING, not yet filled
5. outcome: V47 credited@26 (MARKET_REACH_PRINT_CROSS); V49 credited@25 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**WES** — P=73 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 72 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL13DONWES-WES.csv.gz#row-478`); persistent join 72 (receipt `KXATPCHALLENGERMATCH-26JUL13DONWES-WES.csv.gz#row-2526`); V49 72 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL13DONWES-WES.csv.gz#row-483`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 74 at 1783922799 (receipt `KXATPCHALLENGERMATCH-26JUL13DONWES-WES.csv.gz#row-363`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 2})
3. completing print: 73c at 1783931511 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling DON at that moment: rest 27 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 uncalled (no fill); V49 credited@74 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

6. V49 verdict: CONVERTED

### 4. 26JUL13PERTOB [ATP_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 52c (TOB uncalled)** -> V49: **ONE_LEG 52c (TOB uncalled)**; machine-window lock 4c.

**PER** — P=51 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 52 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL13PERTOB-PER.csv.gz#row-1172`); persistent join 52 (receipt `KXATPCHALLENGERMATCH-26JUL13PERTOB-PER.csv.gz#row-1172`); V49 52 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL13PERTOB-PER.csv.gz#row-1172`)
2. evidence for P: V49 min evidenced standing level 45 at 1783923505 (receipt `KXATPCHALLENGERMATCH-26JUL13PERTOB-PER.csv.gz#row-32`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 3})
3. completing print: 51c at 1783950315.382 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling TOB at that moment: rest 46 (bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY)), direction read SETTLED, not yet filled
5. outcome: V47 credited@52 (MARKET_REACH_TRADED_AT_LEVEL); V49 credited@52 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**TOB** — P=45 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 44 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL13PERTOB-TOB.csv.gz#row-4612`); persistent join 43 (receipt `KXATPCHALLENGERMATCH-26JUL13PERTOB-TOB.csv.gz#row-8011`); V49 44 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL13PERTOB-TOB.csv.gz#row-4619`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 45 at 1783923509 (receipt `KXATPCHALLENGERMATCH-26JUL13PERTOB-TOB.csv.gz#row-29`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 9})
3. completing print: 45c at 1783960083 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling PER at that moment: rest 53 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@52
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

6. V49 verdict: TOB: BID_MINUS_ONE_OFFSET_AT_P -- fe4747cd bid_reached_P=true, V49 evidence min 45; the bid-1 tracking rest stood at 44=P-1 when the print arrived (receipt KXATPCHALLENGERMATCH-26JUL13PERTOB-TOB.csv.gz#row-4619); the print passed 1c above the rest; ask==P at the print tick (fe4747cd), so a post-only bid at P at that tick would cross (sanity-bound collision at P)

### 5. 26JUL14GENPET [ATP_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 61c (PET uncalled)** -> V49: **ONE_LEG 61c (PET uncalled)**; machine-window lock 4c.

**GEN** — P=61 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 61 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL14GENPET-GEN.csv.gz#row-142`); persistent join 61 (receipt `KXATPCHALLENGERMATCH-26JUL14GENPET-GEN.csv.gz#row-44`); V49 61 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL14GENPET-GEN.csv.gz#row-44`)
2. evidence for P: not receipted
3. completing print: 61c at 1784001443.109 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling PET at that moment: rest 37 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@61 (MARKET_REACH_PRINT_CROSS); V49 credited@61 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**PET** — P=37 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 33 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL14GENPET-PET.csv.gz#row-5013`); persistent join 35 (receipt `KXATPCHALLENGERMATCH-26JUL14GENPET-PET.csv.gz#row-5889`); V49 33 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL14GENPET-PET.csv.gz#row-5045`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 36 at 1783980251 (receipt `KXATPCHALLENGERMATCH-26JUL14GENPET-PET.csv.gz#row-39`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 2, 'PRIOR_TRUE_TRADE_AT_OR_BELOW_P': 64})
3. completing print: 37c at 1784027437 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling GEN at that moment: rest 61 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@61
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

6. V49 verdict: PET: REST_CLAMPED_4C_UNDER_P -- rest at 33 under bid-1 tracking at the print (receipt KXATPCHALLENGERMATCH-26JUL14GENPET-PET.csv.gz#row-5045); V49 evidence min 36; ask==P at print tick (sanity collision at P)

### 6. 26JUL19DJOMAT [ATP_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 11c (MAT uncalled)** -> V49: **ONE_LEG 13c (MAT uncalled)**; machine-window lock 12c.

**DJO** — P=4 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 11 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL19DJOMAT-DJO.csv.gz#row-387`); persistent join 11 (receipt `KXATPCHALLENGERMATCH-26JUL19DJOMAT-DJO.csv.gz#row-416`); V49 13 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL19DJOMAT-DJO.csv.gz#row-512`)
2. evidence for P: V49 min evidenced standing level 5 at 1784428572 (receipt `KXATPCHALLENGERMATCH-26JUL19DJOMAT-DJO.csv.gz#row-23`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 14})
3. completing print: 4c at 1784435942.898 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling MAT at that moment: rest 86 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@11 (MARKET_REACH_PRINT_CROSS); V49 credited@13 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**MAT** — P=84 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 83 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL19DJOMAT-MAT.csv.gz#row-1547`); persistent join 82 (receipt `KXATPCHALLENGERMATCH-26JUL19DJOMAT-MAT.csv.gz#row-1861`); V49 83 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL19DJOMAT-MAT.csv.gz#row-1547`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 5 at 1784428572 (receipt `KXATPCHALLENGERMATCH-26JUL19DJOMAT-MAT.csv.gz#row-22`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 5})
3. completing print: 84c at 1784462326 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling DJO at that moment: rest 11 (bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY)), direction read FALLING, FILLED@11
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

6. V49 verdict: MAT: BID_MINUS_ONE_OFFSET_AT_P -- fe4747cd bid_reached_P=true, V49 evidence min 5; the persistence join rest stood at 83=P-1 when the print arrived (receipt KXATPCHALLENGERMATCH-26JUL19DJOMAT-MAT.csv.gz#row-1547); the print passed 1c above the rest; ask==P at the print tick (fe4747cd), so a post-only bid at P at that tick would cross (sanity-bound collision at P)

### 7. 26JUL19SINMAT [ATP_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 68c (SIN uncalled)** -> V49: **ONE_LEG 68c (SIN uncalled)**; machine-window lock 7c.

**MAT** — P=62 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 68 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL19SINMAT-MAT.csv.gz#row-1542`); persistent join 68 (receipt `KXATPCHALLENGERMATCH-26JUL19SINMAT-MAT.csv.gz#row-1505`); V49 68 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL19SINMAT-MAT.csv.gz#row-1542`)
2. evidence for P: V49 min evidenced standing level 4 at 1784410845 (receipt `KXATPCHALLENGERMATCH-26JUL19SINMAT-MAT.csv.gz#row-9`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 4, 'PRIOR_TRUE_TRADE_AT_OR_BELOW_P': 1})
3. completing print: 62c at 1784449048.803 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling SIN at that moment: rest 30 (bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY)), direction read FALLING, not yet filled
5. outcome: V47 credited@68 (MARKET_REACH_TRADED_AT_LEVEL); V49 credited@68 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**SIN** — P=31 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 30 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL19SINMAT-SIN.csv.gz#row-1016`); persistent join 29 (receipt `KXATPCHALLENGERMATCH-26JUL19SINMAT-SIN.csv.gz#row-1180`); V49 30 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL19SINMAT-SIN.csv.gz#row-1080`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 5 at 1784435129 (receipt `KXATPCHALLENGERMATCH-26JUL19SINMAT-SIN.csv.gz#row-118`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 1, 'PRIOR_TRUE_TRADE_AT_OR_BELOW_P': 1})
3. completing print: 31c at 1784448291 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling MAT at that moment: rest 65 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

6. V49 verdict: SIN: BID_MINUS_ONE_OFFSET_AT_P -- fe4747cd bid_reached_P=true, V49 evidence min 5; the bid-1 tracking rest stood at 30=P-1 when the print arrived (receipt KXATPCHALLENGERMATCH-26JUL19SINMAT-SIN.csv.gz#row-1080); the print passed 1c above the rest; ask==P at the print tick (fe4747cd), so a post-only bid at P at that tick would cross (sanity-bound collision at P)

### 8. 26JUL20CHABOU [ATP_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 60c (BOU uncalled)** -> V49: **ONE_LEG 40c (CHA uncalled)**; machine-window lock 1c.

**BOU** — P=39 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 38 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL20CHABOU-BOU.csv.gz#row-5751`); persistent join 38 (receipt `KXATPCHALLENGERMATCH-26JUL20CHABOU-BOU.csv.gz#row-5800`); V49 38 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL20CHABOU-BOU.csv.gz#row-8073`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 38 at 1784531063 (receipt `KXATPCHALLENGERMATCH-26JUL20CHABOU-BOU.csv.gz#row-140`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 3})
3. completing print: 39c at 1784571091 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling CHA at that moment: rest 60 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 uncalled (no fill); V49 credited@40 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**CHA** — P=60 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 60 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL20CHABOU-CHA.csv.gz#row-7597`); persistent join 60 (receipt `KXATPCHALLENGERMATCH-26JUL20CHABOU-CHA.csv.gz#row-7597`); V49 60 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL20CHABOU-CHA.csv.gz#row-7597`)
2. evidence for P: V49 min evidenced standing level 57 at 1784531063 (receipt `KXATPCHALLENGERMATCH-26JUL20CHABOU-CHA.csv.gz#row-224`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 10})
3. completing print: 60c at 1784571501.321 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling BOU at that moment: rest 38 (bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY)), direction read FALLING, not yet filled
5. outcome: V47 credited@60 (MARKET_REACH_PRINT_CROSS); V49 uncalled (no fill)

6. V49 verdict: CHA: BID_MINUS_ONE_OFFSET_AT_P -- V49 own-bid evidence min 57 (receipt KXATPCHALLENGERMATCH-26JUL20CHABOU-CHA.csv.gz#row-224); the persistence join rest stood at 59=P-1 when the print arrived (receipt KXATPCHALLENGERMATCH-26JUL20CHABOU-CHA.csv.gz#row-489); the print passed 1c above the rest | SIBLING_FLIP: V47 filled CHA but left BOU; V49 instead filled BOU and left CHA -- the evidence gate moved which side stood; the pair completed under neither machine

### 9. 26JUL20STAMAT [ATP_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 38c (MAT uncalled)** -> V49: **ONE_LEG 38c (MAT uncalled)**; machine-window lock 2c.

**MAT** — P=61 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 60 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL20STAMAT-MAT.csv.gz#row-436`); persistent join 60 (receipt `KXATPCHALLENGERMATCH-26JUL20STAMAT-MAT.csv.gz#row-436`); V49 60 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL20STAMAT-MAT.csv.gz#row-462`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 59 at 1784503269 (receipt `KXATPCHALLENGERMATCH-26JUL20STAMAT-MAT.csv.gz#row-268`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 1, 'PRIOR_TRUE_TRADE_AT_OR_BELOW_P': 16})
3. completing print: 61c at 1784515548 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling STA at that moment: rest 38 (bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY)), direction read FALLING, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

**STA** — P=38 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 38 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL20STAMAT-STA.csv.gz#row-531`); persistent join 38 (receipt `KXATPCHALLENGERMATCH-26JUL20STAMAT-STA.csv.gz#row-593`); V49 38 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL20STAMAT-STA.csv.gz#row-703`)
2. evidence for P: V49 min evidenced standing level 38 at 1784496044 (receipt `KXATPCHALLENGERMATCH-26JUL20STAMAT-STA.csv.gz#row-172`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 3})
3. completing print: 38c at 1784528769.419 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling MAT at that moment: rest 60 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@38 (MARKET_REACH_PRINT_CROSS); V49 credited@38 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

6. V49 verdict: MAT: BID_MINUS_ONE_OFFSET_AT_P -- fe4747cd bid_reached_P=true, V49 evidence min 59; the bid-1 tracking rest stood at 60=P-1 when the print arrived (receipt KXATPCHALLENGERMATCH-26JUL20STAMAT-MAT.csv.gz#row-462); the print passed 1c above the rest; ask==P at the print tick (fe4747cd), so a post-only bid at P at that tick would cross (sanity-bound collision at P)

### 10. 26JUL20VALGOM [ATP_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 81c (VAL uncalled)** -> V49: **ONE_LEG 81c (VAL uncalled)**; machine-window lock 5c.

**GOM** — P=81 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 81 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL20VALGOM-GOM.csv.gz#row-57`); persistent join 81 (receipt `KXATPCHALLENGERMATCH-26JUL20VALGOM-GOM.csv.gz#row-57`); V49 81 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL20VALGOM-GOM.csv.gz#row-57`)
2. evidence for P: not receipted
3. completing print: 81c at 1784500416.52 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling VAL at that moment: rest 18 (bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY)), direction read FALLING, not yet filled
5. outcome: V47 credited@81 (MARKET_REACH_PRINT_CROSS); V49 credited@81 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**VAL** — P=14 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 13 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL20VALGOM-VAL.csv.gz#row-901`); persistent join 14 (receipt `KXATPCHALLENGERMATCH-26JUL20VALGOM-VAL.csv.gz#row-1088`); V49 13 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL20VALGOM-VAL.csv.gz#row-903`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 18 at 1784500363 (receipt `KXATPCHALLENGERMATCH-26JUL20VALGOM-VAL.csv.gz#row-60`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 1})
3. completing print: 14c at 1784540452 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling GOM at that moment: rest 81 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@81
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

6. V49 verdict: VAL: EVIDENCE_CEILING_4C_ABOVE_P -- V49's gate never certified P=14: min evidenced standing level 18 (receipt KXATPCHALLENGERMATCH-26JUL20VALGOM-VAL.csv.gz#row-60); no prior true trade <=P receipt; rest at print stood 13 under bid-1 tracking (receipt KXATPCHALLENGERMATCH-26JUL20VALGOM-VAL.csv.gz#row-903); ask==P at the print tick (fe4747cd), so placing at P at that tick would cross -- the stand had to happen earlier in the window and never did

### 11. 26JUL12MALTUR [WTA_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 46c (MAL uncalled)** -> V49: **COMPLETED 99c**; machine-window lock 5c.

**MAL** — P=53 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 45 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL12MALTUR-MAL.csv.gz#row-41856`); persistent join 47 (receipt `KXWTACHALLENGERMATCH-26JUL12MALTUR-MAL.csv.gz#row-42649`); V49 45 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL12MALTUR-MAL.csv.gz#row-41856`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 51 at 1783829010 (receipt `KXWTACHALLENGERMATCH-26JUL12MALTUR-MAL.csv.gz#row-220`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 3})
3. completing print: 53c at 1783876484.256 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling TUR at that moment: rest 46 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@46
5. outcome: V47 uncalled (no fill); V49 credited@53 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**TUR** — P=46 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 46 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL12MALTUR-TUR.csv.gz#row-155`); persistent join 46 (receipt `KXWTACHALLENGERMATCH-26JUL12MALTUR-TUR.csv.gz#row-155`); V49 40 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL12MALTUR-TUR.csv.gz#row-156`)
2. evidence for P: V49 min evidenced standing level 40 at 1783827339 (receipt `KXWTACHALLENGERMATCH-26JUL12MALTUR-TUR.csv.gz#row-109`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 3, 'PRIOR_TRUE_TRADE_AT_OR_BELOW_P': 1})
3. completing print: 46c at 1783827770.435 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling MAL at that moment: rest 51 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@46 (MARKET_REACH_PRINT_CROSS); V49 credited@46 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

6. V49 verdict: CONVERTED

### 12. 26JUL13KOTURG [WTA_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 67c (KOT uncalled)** -> V49: **ONE_LEG 67c (KOT uncalled)**; machine-window lock 4c.

**KOT** — P=32 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 31 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL13KOTURG-KOT.csv.gz#row-1961`); persistent join 31 (receipt `KXWTACHALLENGERMATCH-26JUL13KOTURG-KOT.csv.gz#row-17320`); V49 31 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL13KOTURG-KOT.csv.gz#row-4239`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 35 at 1783918357 (receipt `KXWTACHALLENGERMATCH-26JUL13KOTURG-KOT.csv.gz#row-34`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 9})
3. completing print: 32c at 1783959598 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling URG at that moment: rest 67 (bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY)), direction read SETTLED, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

**URG** — P=64 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 67 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL13KOTURG-URG.csv.gz#row-924`); persistent join 67 (receipt `KXWTACHALLENGERMATCH-26JUL13KOTURG-URG.csv.gz#row-285`); V49 67 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL13KOTURG-URG.csv.gz#row-924`)
2. evidence for P: V49 min evidenced standing level 67 at 1783944935 (receipt `KXWTACHALLENGERMATCH-26JUL13KOTURG-URG.csv.gz#row-924`; sources {'PRIOR_TRUE_TRADE_AT_OR_BELOW_P': 1, 'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 1})
3. completing print: 64c at 1783966995.001 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling KOT at that moment: rest 32 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@67 (MARKET_REACH_TRADED_AT_LEVEL); V49 credited@67 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

6. V49 verdict: KOT: EVIDENCE_CEILING_3C_ABOVE_P -- V49's gate never certified P=32: min evidenced standing level 35 (receipt KXWTACHALLENGERMATCH-26JUL13KOTURG-KOT.csv.gz#row-34); no prior true trade <=P receipt; rest at print stood 31 under bid-1 tracking (receipt KXWTACHALLENGERMATCH-26JUL13KOTURG-KOT.csv.gz#row-4239); ask==P at the print tick (fe4747cd), so placing at P at that tick would cross -- the stand had to happen earlier in the window and never did

### 13. 26JUL13SELYAN [WTA_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 59c (YAN uncalled)** -> V49: **ONE_LEG 42c (SEL uncalled)**; machine-window lock 2c.

**SEL** — P=59 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 59 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL13SELYAN-SEL.csv.gz#row-2568`); persistent join 59 (receipt `KXWTACHALLENGERMATCH-26JUL13SELYAN-SEL.csv.gz#row-2568`); V49 57 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL13SELYAN-SEL.csv.gz#row-994`)
2. evidence for P: V49 min evidenced standing level 52 at 1783914323 (receipt `KXWTACHALLENGERMATCH-26JUL13SELYAN-SEL.csv.gz#row-31`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 5})
3. completing print: 59c at 1783948951.283 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling YAN at that moment: rest 39 (bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY)), direction read FALLING, not yet filled
5. outcome: V47 credited@59 (MARKET_REACH_PRINT_CROSS); V49 uncalled (no fill)

**YAN** — P=39 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 38 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL13SELYAN-YAN.csv.gz#row-2528`); persistent join 37 (receipt `KXWTACHALLENGERMATCH-26JUL13SELYAN-YAN.csv.gz#row-3481`); V49 42 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL13SELYAN-YAN.csv.gz#row-301`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd)
3. completing print: 39c at 1783953549 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling SEL at that moment: rest 59 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@59
5. outcome: V47 uncalled (no fill); V49 credited@42 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

6. V49 verdict: SEL: REST_CLAMPED_2C_UNDER_P -- rest at 57 under bid-1 tracking at the print (receipt KXWTACHALLENGERMATCH-26JUL13SELYAN-SEL.csv.gz#row-994); V49 evidence min 52 | SIBLING_FLIP: V47 filled SEL but left YAN; V49 instead filled YAN and left SEL -- the evidence gate moved which side stood; the pair completed under neither machine

### 14. 26JUL16BASRUS [WTA_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 66c (RUS uncalled)** -> V49: **ONE_LEG 66c (RUS uncalled)**; machine-window lock 2c.

**BAS** — P=66 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 66 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL16BASRUS-BAS.csv.gz#row-100`); persistent join 66 (receipt `KXWTACHALLENGERMATCH-26JUL16BASRUS-BAS.csv.gz#row-100`); V49 66 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL16BASRUS-BAS.csv.gz#row-100`)
2. evidence for P: not receipted
3. completing print: 66c at 1784162687.132 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling RUS at that moment: rest 30 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@66 (MARKET_REACH_TRADED_AT_LEVEL); V49 credited@66 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**RUS** — P=32 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 31 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL16BASRUS-RUS.csv.gz#row-123`); persistent join 31 (receipt `KXWTACHALLENGERMATCH-26JUL16BASRUS-RUS.csv.gz#row-867`); V49 31 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL16BASRUS-RUS.csv.gz#row-145`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 31 at 1784163045 (receipt `KXWTACHALLENGERMATCH-26JUL16BASRUS-RUS.csv.gz#row-145`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 2})
3. completing print: 32c at 1784168790 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling BAS at that moment: rest 68 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@66
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

6. V49 verdict: RUS: BID_MINUS_ONE_OFFSET_AT_P -- fe4747cd bid_reached_P=true, V49 evidence min 31; the bid-1 tracking rest stood at 31=P-1 when the print arrived (receipt KXWTACHALLENGERMATCH-26JUL16BASRUS-RUS.csv.gz#row-145); the print passed 1c above the rest; ask==P at the print tick (fe4747cd), so a post-only bid at P at that tick would cross (sanity-bound collision at P)

### 15. 26JUL17JONNOH [WTA_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 61c (NOH uncalled)** -> V49: **ONE_LEG 62c (NOH uncalled)**; machine-window lock 1c.

**JON** — P=61 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 61 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL17JONNOH-JON.csv.gz#row-174`); persistent join 61 (receipt `KXWTACHALLENGERMATCH-26JUL17JONNOH-JON.csv.gz#row-202`); V49 62 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL17JONNOH-JON.csv.gz#row-298`)
2. evidence for P: V49 min evidenced standing level 62 at 1784255082 (receipt `KXWTACHALLENGERMATCH-26JUL17JONNOH-JON.csv.gz#row-46`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 2})
3. completing print: 61c at 1784265037.947 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling NOH at that moment: rest 37 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@61 (MARKET_REACH_PRINT_CROSS); V49 credited@62 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**NOH** — P=38 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 36 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL17JONNOH-NOH.csv.gz#row-86`); persistent join 37 (receipt `KXWTACHALLENGERMATCH-26JUL17JONNOH-NOH.csv.gz#row-988`); V49 36 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL17JONNOH-NOH.csv.gz#row-86`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 34 at 1784254835 (receipt `KXWTACHALLENGERMATCH-26JUL17JONNOH-NOH.csv.gz#row-24`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 3})
3. completing print: 38c at 1784255635 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling JON at that moment: rest 63 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

6. V49 verdict: NOH: REST_CLAMPED_2C_UNDER_P -- rest at 36 under persistence join at the print (receipt KXWTACHALLENGERMATCH-26JUL17JONNOH-NOH.csv.gz#row-86); V49 evidence min 34; ask==P at print tick (sanity collision at P)

### 16. 26JUL20KABCHI [WTA_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 20c (CHI uncalled)** -> V49: **COMPLETED 98c**; machine-window lock 3c.

**CHI** — P=77 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 76 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL20KABCHI-CHI.csv.gz#row-1192`); persistent join 76 (receipt `KXWTACHALLENGERMATCH-26JUL20KABCHI-CHI.csv.gz#row-1535`); V49 76 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL20KABCHI-CHI.csv.gz#row-1198`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 77 at 1784518012 (receipt `KXWTACHALLENGERMATCH-26JUL20KABCHI-CHI.csv.gz#row-57`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 1})
3. completing print: 77c at 1784550440 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling KAB at that moment: rest 20 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@20
5. outcome: V47 uncalled (no fill); V49 credited@78 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**KAB** — P=20 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 20 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL20KABCHI-KAB.csv.gz#row-119`); persistent join 20 (receipt `KXWTACHALLENGERMATCH-26JUL20KABCHI-KAB.csv.gz#row-54`); V49 20 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL20KABCHI-KAB.csv.gz#row-73`)
2. evidence for P: V49 min evidenced standing level 20 at 1784518381 (receipt `KXWTACHALLENGERMATCH-26JUL20KABCHI-KAB.csv.gz#row-73`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 1})
3. completing print: 20c at 1784520304.116 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling CHI at that moment: rest 78 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@20 (MARKET_REACH_PRINT_CROSS); V49 credited@20 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

6. V49 verdict: CONVERTED

### 17. 26JUL20TOTRUG [WTA_CHALL] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 44c (RUG uncalled)** -> V49: **COMPLETED 99c**; machine-window lock 1c.

**RUG** — P=55 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 54 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL20TOTRUG-RUG.csv.gz#row-492`); persistent join 54 (receipt `KXWTACHALLENGERMATCH-26JUL20TOTRUG-RUG.csv.gz#row-2511`); V49 54 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL20TOTRUG-RUG.csv.gz#row-842`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 52 at 1784523992 (receipt `KXWTACHALLENGERMATCH-26JUL20TOTRUG-RUG.csv.gz#row-24`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 6})
3. completing print: 55c at 1784552480 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling TOT at that moment: rest 44 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 uncalled (no fill); V49 credited@55 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**TOT** — P=44 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 44 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL20TOTRUG-TOT.csv.gz#row-1070`); persistent join 44 (receipt `KXWTACHALLENGERMATCH-26JUL20TOTRUG-TOT.csv.gz#row-1045`); V49 44 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL20TOTRUG-TOT.csv.gz#row-1056`)
2. evidence for P: V49 min evidenced standing level 38 at 1784523666 (receipt `KXWTACHALLENGERMATCH-26JUL20TOTRUG-TOT.csv.gz#row-24`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 25, 'PRIOR_TRUE_TRADE_AT_OR_BELOW_P': 1})
3. completing print: 44c at 1784562358.234 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling RUG at that moment: rest 54 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@44 (MARKET_REACH_PRINT_CROSS); V49 credited@44 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

6. V49 verdict: CONVERTED

### 18. 26JUL12HERKAZ [WTA_MAIN] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 46c (HER uncalled)** -> V49: **ONE_LEG 46c (HER uncalled)**; machine-window lock 8c.

**HER** — P=46 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 45 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTAMATCH-26JUL12HERKAZ-HER.csv.gz#row-1039`); persistent join 53 (receipt `KXWTAMATCH-26JUL12HERKAZ-HER.csv.gz#row-2192`); V49 45 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTAMATCH-26JUL12HERKAZ-HER.csv.gz#row-1039`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 8 at 1783785096 (receipt `KXWTAMATCH-26JUL12HERKAZ-HER.csv.gz#row-8`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 28})
3. completing print: 46c at 1783830206.519 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling KAZ at that moment: rest 46 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

**KAZ** — P=46 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 46 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTAMATCH-26JUL12HERKAZ-KAZ.csv.gz#row-1925`); persistent join 46 (receipt `KXWTAMATCH-26JUL12HERKAZ-KAZ.csv.gz#row-1925`); V49 46 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTAMATCH-26JUL12HERKAZ-KAZ.csv.gz#row-1990`)
2. evidence for P: V49 min evidenced standing level 8 at 1783785096 (receipt `KXWTAMATCH-26JUL12HERKAZ-KAZ.csv.gz#row-8`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 12})
3. completing print: 46c at 1783833104.571 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling HER at that moment: rest 45 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@46 (MARKET_REACH_PRINT_CROSS); V49 credited@46 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

6. V49 verdict: HER: BID_MINUS_ONE_OFFSET_AT_P -- fe4747cd bid_reached_P=true, V49 evidence min 8; the persistence join rest stood at 45=P-1 when the print arrived (receipt KXWTAMATCH-26JUL12HERKAZ-HER.csv.gz#row-1039); the print passed 1c above the rest; ask==P at the print tick (fe4747cd), so a post-only bid at P at that tick would cross (sanity-bound collision at P)

### 19. 26JUL20LYSVAL [WTA_MAIN] — WINDOW LAW ADDITION (fe4747cd)

V47: **ONE_LEG 67c (LYS uncalled)** -> V49: **ONE_LEG 67c (LYS uncalled)**; machine-window lock 4c.

**LYS** — P=30 (fe4747cd v2 detail); standability: WINDOW_LAWFUL_EVIDENCE
1. rest in window: V47 28 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTAMATCH-26JUL20LYSVAL-LYS.csv.gz#row-124`); persistent join 29 (receipt `KXWTAMATCH-26JUL20LYSVAL-LYS.csv.gz#row-15431`); V49 28 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTAMATCH-26JUL20LYSVAL-LYS.csv.gz#row-124`)
2. evidence for P: prior trade<=P: False; bid reached P: True (fe4747cd); V49 min evidenced standing level 9 at 1784448898 (receipt `KXWTAMATCH-26JUL20LYSVAL-LYS.csv.gz#row-39`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 5, 'PRIOR_TRUE_TRADE_AT_OR_BELOW_P': 3})
3. completing print: 30c at 1784454465 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling VAL at that moment: rest 70 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@67
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

**VAL** — P=67 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 67 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTAMATCH-26JUL20LYSVAL-VAL.csv.gz#row-68`); persistent join 67 (receipt `KXWTAMATCH-26JUL20LYSVAL-VAL.csv.gz#row-68`); V49 67 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTAMATCH-26JUL20LYSVAL-VAL.csv.gz#row-68`)
2. evidence for P: V49 min evidenced standing level 66 at 1784449420 (receipt `KXWTAMATCH-26JUL20LYSVAL-VAL.csv.gz#row-66`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 1})
3. completing print: 67c at 1784449831.786 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling LYS at that moment: rest 26 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@67 (MARKET_REACH_TRADED_AT_LEVEL); V49 credited@67 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

6. V49 verdict: LYS: REST_CLAMPED_2C_UNDER_P -- rest at 28 under persistence join at the print (receipt KXWTAMATCH-26JUL20LYSVAL-LYS.csv.gz#row-124); V49 evidence min 9; ask==P at print tick (sanity collision at P)

### 20. 26JUL18BASBOE [WTA_CHALL] — V1 TOP RECOVERABLE (3dd57fba)

V47: **ONE_LEG 5c (BAS uncalled)** -> V49: **ONE_LEG 5c (BAS uncalled)**; machine-window lock 2c.

**BAS** — P=94 (3dd57fba top_recoverable); standability: LAWFULLY_STANDABLE_INSTANT ask_at_print=95>P=94 (3dd57fba)
1. rest in window: V47 94 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL18BASBOE-BAS.csv.gz#row-198`); persistent join 96 (receipt `KXWTACHALLENGERMATCH-26JUL18BASBOE-BAS.csv.gz#row-366`); V49 94 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL18BASBOE-BAS.csv.gz#row-198`)
2. evidence for P: V49 min evidenced standing level 4 at 1784353078 (receipt `KXWTACHALLENGERMATCH-26JUL18BASBOE-BAS.csv.gz#row-7`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 3})
3. completing print: 94c at 1784354550.326 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling BOE at that moment: rest 5 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@5
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

**BOE** — P=3 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 5 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL18BASBOE-BOE.csv.gz#row-16`); persistent join 5 (receipt `KXWTACHALLENGERMATCH-26JUL18BASBOE-BOE.csv.gz#row-7`); V49 5 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL18BASBOE-BOE.csv.gz#row-16`)
2. evidence for P: V49 min evidenced standing level 4 at 1784353448 (receipt `KXWTACHALLENGERMATCH-26JUL18BASBOE-BOE.csv.gz#row-8`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 1})
3. completing print: 3c at 1784353551.969 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling BAS at that moment: rest 90 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@5 (MARKET_REACH_PRINT_CROSS); V49 credited@5 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

### 21. 26JUL13JONSPI [WTA_CHALL] — V1 TOP RECOVERABLE (3dd57fba)

V47: **ONE_LEG 8c (JON uncalled)** -> V49: **ONE_LEG 8c (JON uncalled)**; machine-window lock 42c.

**JON** — P=91 (3dd57fba top_recoverable); standability: LAWFULLY_STANDABLE_INSTANT ask_at_print=92>P=91 (3dd57fba)
1. rest in window: V47 None by None (receipt `None`); persistent join 88 (receipt `KXWTACHALLENGERMATCH-26JUL13JONSPI-JON.csv.gz#row-192`); V49 None by None (receipt `None`)
2. evidence for P: V49 min evidenced standing level 4 at 1783889473 (receipt `KXWTACHALLENGERMATCH-26JUL13JONSPI-JON.csv.gz#row-8`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 1})
3. completing print: 91c at None (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling SPI at that moment: rest None (None), direction read None, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

**SPI** — P=7 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 8 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL13JONSPI-SPI.csv.gz#row-189`); persistent join 8 (receipt `KXWTACHALLENGERMATCH-26JUL13JONSPI-SPI.csv.gz#row-189`); V49 8 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL13JONSPI-SPI.csv.gz#row-189`)
2. evidence for P: V49 min evidenced standing level 4 at 1783889473 (receipt `KXWTACHALLENGERMATCH-26JUL13JONSPI-SPI.csv.gz#row-8`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 17})
3. completing print: 7c at 1783902223.703 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling JON at that moment: rest 50 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@8 (MARKET_REACH_TRADED_AT_LEVEL); V49 credited@8 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

### 22. 26JUL13KNUKUR [WTA_CHALL] — V1 TOP RECOVERABLE (3dd57fba)

V47: **ONE_LEG 9c (KNU uncalled)** -> V49: **ONE_LEG 9c (KNU uncalled)**; machine-window lock 6c.

**KNU** — P=84 (3dd57fba top_recoverable); standability: LAWFULLY_STANDABLE_INSTANT ask_at_print=86>P=84 (3dd57fba)
1. rest in window: V47 87 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL13KNUKUR-KNU.csv.gz#row-1683`); persistent join 89 (receipt `KXWTACHALLENGERMATCH-26JUL13KNUKUR-KNU.csv.gz#row-2237`); V49 87 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL13KNUKUR-KNU.csv.gz#row-1683`)
2. evidence for P: V49 min evidenced standing level 84 at 1783909106 (receipt `KXWTACHALLENGERMATCH-26JUL13KNUKUR-KNU.csv.gz#row-109`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 13, 'PRIOR_TRUE_TRADE_AT_OR_BELOW_P': 1})
3. completing print: 84c at 1783931842 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling KUR at that moment: rest 11 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

**KUR** — P=9 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 9 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL13KNUKUR-KUR.csv.gz#row-132513`); persistent join 9 (receipt `KXWTACHALLENGERMATCH-26JUL13KNUKUR-KUR.csv.gz#row-132518`); V49 9 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL13KNUKUR-KUR.csv.gz#row-132552`)
2. evidence for P: V49 min evidenced standing level 5 at 1783903371 (receipt `KXWTACHALLENGERMATCH-26JUL13KNUKUR-KUR.csv.gz#row-21`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 11})
3. completing print: 9c at 1783942772.625 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling KNU at that moment: rest 87 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@9 (MARKET_REACH_TRADED_AT_LEVEL); V49 credited@9 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

### 23. 26JUL16KHOPRO [WTA_CHALL] — V1 TOP RECOVERABLE (3dd57fba)

V47: **ONE_LEG 15c (PRO uncalled)** -> V49: **ONE_LEG 15c (PRO uncalled)**; machine-window lock 0c.

**KHO** — P=15 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 15 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL16KHOPRO-KHO.csv.gz#row-705`); persistent join 15 (receipt `KXWTACHALLENGERMATCH-26JUL16KHOPRO-KHO.csv.gz#row-737`); V49 15 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL16KHOPRO-KHO.csv.gz#row-900`)
2. evidence for P: V49 min evidenced standing level 15 at 1784161524 (receipt `KXWTACHALLENGERMATCH-26JUL16KHOPRO-KHO.csv.gz#row-45`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 2, 'PRIOR_TRUE_TRADE_AT_OR_BELOW_P': 1})
3. completing print: 15c at 1784203871.573 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling PRO at that moment: rest 84 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@15 (MARKET_REACH_TRADED_AT_LEVEL); V49 credited@15 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**PRO** — P=84 (3dd57fba top_recoverable); standability: LAWFULLY_STANDABLE_INSTANT ask_at_print=86>P=84 (3dd57fba)
1. rest in window: V47 84 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL16KHOPRO-PRO.csv.gz#row-178`); persistent join 86 (receipt `KXWTACHALLENGERMATCH-26JUL16KHOPRO-PRO.csv.gz#row-2132`); V49 84 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL16KHOPRO-PRO.csv.gz#row-178`)
2. evidence for P: not receipted
3. completing print: 84c at 1784166081 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling KHO at that moment: rest 15 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

### 24. 26JUL14ZHUYUN [ATP_CHALL] — V1 TOP RECOVERABLE (3dd57fba)

V47: **ONE_LEG 9c (YUN uncalled)** -> V49: **ONE_LEG 14c (YUN uncalled)**; machine-window lock 3c.

**YUN** — P=78 (3dd57fba top_recoverable); standability: LAWFULLY_STANDABLE_INSTANT ask_at_print=86>P=78 (3dd57fba)
1. rest in window: V47 90 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL14ZHUYUN-YUN.csv.gz#row-407`); persistent join 93 (receipt `KXATPCHALLENGERMATCH-26JUL14ZHUYUN-YUN.csv.gz#row-568`); V49 85 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL14ZHUYUN-YUN.csv.gz#row-95`)
2. evidence for P: V49 min evidenced standing level 5 at 1784007496 (receipt `KXATPCHALLENGERMATCH-26JUL14ZHUYUN-YUN.csv.gz#row-14`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 1})
3. completing print: 78c at 1784031262.625 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling ZHU at that moment: rest 9 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@9
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

**ZHU** — P=7 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 9 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL14ZHUYUN-ZHU.csv.gz#row-598`); persistent join 9 (receipt `KXATPCHALLENGERMATCH-26JUL14ZHUYUN-ZHU.csv.gz#row-598`); V49 14 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL14ZHUYUN-ZHU.csv.gz#row-11`)
2. evidence for P: not receipted
3. completing print: 7c at 1784020275.825 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling YUN at that moment: rest 88 (bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY)), direction read SETTLED, not yet filled
5. outcome: V47 credited@9 (MARKET_REACH_PRINT_CROSS); V49 credited@14 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

### 25. 26JUL14MAKSEY [ATP_CHALL] — V1 TOP RECOVERABLE (3dd57fba)

V47: **ONE_LEG 19c (SEY uncalled)** -> V49: **ONE_LEG 20c (SEY uncalled)**; machine-window lock 1c.

**MAK** — P=19 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 19 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL14MAKSEY-MAK.csv.gz#row-574`); persistent join 20 (receipt `KXATPCHALLENGERMATCH-26JUL14MAKSEY-MAK.csv.gz#row-102`); V49 20 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL14MAKSEY-MAK.csv.gz#row-145`)
2. evidence for P: V49 min evidenced standing level 19 at 1783986565 (receipt `KXATPCHALLENGERMATCH-26JUL14MAKSEY-MAK.csv.gz#row-94`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 3})
3. completing print: 19c at 1784005096.162 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling SEY at that moment: rest 79 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@19 (MARKET_REACH_PRINT_CROSS); V49 credited@20 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**SEY** — P=77 (3dd57fba top_recoverable); standability: LAWFULLY_STANDABLE_INSTANT ask_at_print=79>P=77 (3dd57fba)
1. rest in window: V47 79 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL14MAKSEY-SEY.csv.gz#row-131`); persistent join 80 (receipt `KXATPCHALLENGERMATCH-26JUL14MAKSEY-SEY.csv.gz#row-2142`); V49 79 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL14MAKSEY-SEY.csv.gz#row-131`)
2. evidence for P: V49 min evidenced standing level 77 at 1783986565 (receipt `KXATPCHALLENGERMATCH-26JUL14MAKSEY-SEY.csv.gz#row-109`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 3})
3. completing print: 77c at 1784011093 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling MAK at that moment: rest 19 (bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY)), direction read SETTLED, FILLED@19
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

### 26. 26JUL19RUSKAZ [WTA_MAIN] — V1 TOP RECOVERABLE (3dd57fba)

V47: **ONE_LEG 24c (RUS uncalled)** -> V49: **ONE_LEG 24c (RUS uncalled)**; machine-window lock 2c.

**KAZ** — P=24 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 24 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTAMATCH-26JUL19RUSKAZ-KAZ.csv.gz#row-218`); persistent join 24 (receipt `KXWTAMATCH-26JUL19RUSKAZ-KAZ.csv.gz#row-218`); V49 24 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTAMATCH-26JUL19RUSKAZ-KAZ.csv.gz#row-332`)
2. evidence for P: V49 min evidenced standing level 8 at 1784390687 (receipt `KXWTAMATCH-26JUL19RUSKAZ-KAZ.csv.gz#row-6`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 16})
3. completing print: 24c at 1784414473.652 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling RUS at that moment: rest 72 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@24 (MARKET_REACH_PRINT_CROSS); V49 credited@24 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**RUS** — P=75 (3dd57fba top_recoverable); standability: LAWFULLY_STANDABLE_INSTANT ask_at_print=76>P=75 (3dd57fba)
1. rest in window: V47 74 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTAMATCH-26JUL19RUSKAZ-RUS.csv.gz#row-655`); persistent join 74 (receipt `KXWTAMATCH-26JUL19RUSKAZ-RUS.csv.gz#row-1240`); V49 74 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTAMATCH-26JUL19RUSKAZ-RUS.csv.gz#row-655`)
2. evidence for P: V49 min evidenced standing level 8 at 1784390687 (receipt `KXWTAMATCH-26JUL19RUSKAZ-RUS.csv.gz#row-8`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 22, 'PRIOR_TRUE_TRADE_AT_OR_BELOW_P': 11})
3. completing print: 75c at 1784430467 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling KAZ at that moment: rest 24 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@24
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

### 27. 26JUL12FEICHE [WTA_CHALL] — V1 TOP RECOVERABLE (3dd57fba)

V47: **NONE (CHE,FEI uncalled)** -> V49: **NONE (CHE,FEI uncalled)**; machine-window lock 1c.

**CHE** — P=25 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: NOT_RECUT
1. rest in window: V47 24 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL12FEICHE-CHE.csv.gz#row-6702`); persistent join 24 (receipt `KXWTACHALLENGERMATCH-26JUL12FEICHE-CHE.csv.gz#row-5513`); V49 24 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL12FEICHE-CHE.csv.gz#row-5513`)
2. evidence for P: V49 min evidenced standing level 22 at 1783809761 (receipt `KXWTACHALLENGERMATCH-26JUL12FEICHE-CHE.csv.gz#row-107`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 3})
3. completing print: 25c at 1783840573 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling FEI at that moment: rest 74 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

**FEI** — P=74 (3dd57fba top_recoverable); standability: LAWFULLY_STANDABLE_INSTANT ask_at_print=76>P=74 (3dd57fba)
1. rest in window: V47 None by None (receipt `None`); persistent join 74 (receipt `KXWTACHALLENGERMATCH-26JUL12FEICHE-FEI.csv.gz#row-1247`); V49 None by None (receipt `None`)
2. evidence for P: V49 min evidenced standing level 73 at 1783810076 (receipt `KXWTACHALLENGERMATCH-26JUL12FEICHE-FEI.csv.gz#row-113`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 4})
3. completing print: 74c at None (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling CHE at that moment: rest None (None), direction read None, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

### 28. 26JUL13BOUZHA [ATP_CHALL] — V1 TOP RECOVERABLE (3dd57fba)

V47: **ONE_LEG 24c (ZHA uncalled)** -> V49: **ONE_LEG 24c (ZHA uncalled)**; machine-window lock 2c.

**BOU** — P=24 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: V47_CREDITED
1. rest in window: V47 24 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL13BOUZHA-BOU.csv.gz#row-143`); persistent join 24 (receipt `KXATPCHALLENGERMATCH-26JUL13BOUZHA-BOU.csv.gz#row-143`); V49 24 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXATPCHALLENGERMATCH-26JUL13BOUZHA-BOU.csv.gz#row-143`)
2. evidence for P: not receipted
3. completing print: 24c at 1783923210.657 (fill_timestamp (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling ZHA at that moment: rest 74 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 credited@24 (MARKET_REACH_PRINT_CROSS); V49 credited@24 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

**ZHA** — P=73 (3dd57fba top_recoverable); standability: LAWFULLY_STANDABLE_INSTANT ask_at_print=74>P=73 (3dd57fba)
1. rest in window: V47 73 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL13BOUZHA-ZHA.csv.gz#row-1501`); persistent join 73 (receipt `KXATPCHALLENGERMATCH-26JUL13BOUZHA-ZHA.csv.gz#row-1758`); V49 73 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXATPCHALLENGERMATCH-26JUL13BOUZHA-ZHA.csv.gz#row-1513`)
2. evidence for P: V49 min evidenced standing level 72 at 1783921557 (receipt `KXATPCHALLENGERMATCH-26JUL13BOUZHA-ZHA.csv.gz#row-97`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 8})
3. completing print: 73c at 1783945156 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling BOU at that moment: rest 24 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, FILLED@24
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

### 29. 26JUL13OKATAR [WTA_CHALL] — V1 TOP RECOVERABLE (3dd57fba)

V47: **NONE (OKA,TAR uncalled)** -> V49: **ONE_LEG 85c (OKA uncalled)**; machine-window lock -2c.

**OKA** — P=18 (machine-window lowest true trade (1c8700fa DECISION_TRACE_1608)); standability: NOT_RECUT
1. rest in window: V47 15 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL13OKATAR-OKA.csv.gz#row-238`); persistent join 16 (receipt `KXWTACHALLENGERMATCH-26JUL13OKATAR-OKA.csv.gz#row-190`); V49 15 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL13OKATAR-OKA.csv.gz#row-243`)
2. evidence for P: V49 min evidenced standing level 4 at 1783912853 (receipt `KXWTACHALLENGERMATCH-26JUL13OKATAR-OKA.csv.gz#row-7`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 5})
3. completing print: 18c at 1783931965 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling TAR at that moment: rest 83 (persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1)), direction read RISING, not yet filled
5. outcome: V47 uncalled (no fill); V49 uncalled (no fill)

**TAR** — P=71 (3dd57fba top_recoverable); standability: LAWFULLY_STANDABLE_INSTANT ask_at_print=72>P=71 (3dd57fba)
1. rest in window: V47 84 by bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY) (receipt `KXWTACHALLENGERMATCH-26JUL13OKATAR-TAR.csv.gz#row-957`); persistent join 84 (receipt `KXWTACHALLENGERMATCH-26JUL13OKATAR-TAR.csv.gz#row-988`); V49 85 by persistence join (V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1) (receipt `KXWTACHALLENGERMATCH-26JUL13OKATAR-TAR.csv.gz#row-927`)
2. evidence for P: V49 min evidenced standing level 4 at 1783912855 (receipt `KXWTACHALLENGERMATCH-26JUL13OKATAR-TAR.csv.gz#row-7`; sources {'OWN_BEST_BID_P_CONTINUOUSLY_STANDING': 8})
3. completing print: 71c at 1783933456.542 (latest_new_low_evidence_ts (V47 MARKET_EVENT_LEDGER)); size: NOT_RECEIPTED_IN_COMMITTED_ARTIFACTS
4. sibling OKA at that moment: rest 15 (bid-1 tracking (V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY)), direction read SETTLED, not yet filled
5. outcome: V47 uncalled (no fill); V49 credited@85 (MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST)

## Standing-template packs — the 3 largest V47/V49 divergences

Ranked by naked-cost-removed + lock: **MALTUR** (one-leg 46c naked -> completed 99c; swing 47c), **TOTRUG** (44c naked -> 99c; swing 45c), **DONWES** (26c naked -> 99c; swing 27c). Packs (this directory): `26JUL12MALTUR_DUAL_TIMELINE_V2.csv` + `26JUL12MALTUR_DECISION_MARKS.json`, `26JUL20TOTRUG_DUAL_TIMELINE_V2.csv` + `26JUL20TOTRUG_DECISION_MARKS.json`, `26JUL13DONWES_DUAL_TIMELINE_V2.csv` + `26JUL13DONWES_DECISION_MARKS.json`. Timelines are action-granularity (every PLACE/REPRICE/FILL/withhold of both machines, both legs, with law + receipt per row, V49 evidence-establishment marks, and completing-print proxies); the raw-tape tick timeline cannot be rebuilt here (tape is private, hash-only).

## Conservation footer

81 rows exactly = 19 pinned window-law + 10 pinned v1-top + 52 conserved unreceipted slots; category 34/10/30/7 = frozen fe4747cd; V47 396 / V49 393 / under-par 711 / gap 315 all reproduced from receipts; 4 pair conversions reproduced = 1c8700fa. No identity fabricated.
