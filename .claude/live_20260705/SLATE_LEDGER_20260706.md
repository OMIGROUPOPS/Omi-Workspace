# SLATE LEDGER — THE BOOK (window: flip boot 2026-07-05 23:50:39 ET → 2026-07-07 00:18:15 ET)

**This document supersedes the 15:52 roll and is the reconcile. Every future grading is a CUT of this ledger.** Exchange truth only (REST fills/settlements/positions/orders + live book); bot positions only; **39 manual tickers excluded**; canonical $ rule = SETTLEMENT-REALIZED per ticker (revenue + sells − buys − fees; an exited-but-unsettled leg is OPEN with partial cash noted, never counted settled).

## 0 · GRADE × DISPOSITION — the money-machine cross-tab (settled events; leg-level, $ = leg settlement-realized)

| grade | CASHED_W1 | CASHED_CORRIDOR | CASHED_W2 | RODE | legs | leg-$ total |
|---|---|---|---|---|---|---|
| **B2** | 0 (+0.00) | 23 (+9.18) | 175 (+116.23) | 0 (+0.00) | 198 | +125.41 |
| **B3** | 1 (+0.80) | 6 (+8.63) | 34 (+23.13) | 43 (-132.47) | 84 | -99.91 |
| **C** | 0 (+0.00) | 2 (+1.25) | 12 (+6.08) | 6 (-10.28) | 20 | -2.95 |
| **D** | 1 (+0.30) | 5 (+2.30) | 20 (+12.20) | 1 (-0.45) | 27 | +14.35 |
| **F** | 0 (+0.00) | 1 (-1.40) | 1 (-0.40) | 26 (-50.15) | 28 | -51.95 |

(A-legs that rode: 0 — A requires exits REACHED in W1, not necessarily filled; the table shows whether construction cashed.)

## 0b · A–F MATRIX × cat × epoch — headline row: W1-cash rate + BOUHAR above the dollars

**HEADLINE: W1-cash 2/357 legs (0%) · BOUHAR pairs 0 · settled $-15.05**

| epoch | cat | A | B1 | B2 | B3 | C | D | F | W1-cash | BOUHAR | $ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E3a | ATP_MAIN | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0/5 | 0 | -5.82 |
| E3a | WTA_MAIN | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 0/8 | 0 | -8.16 |
| E3a | ATP_CHALL | 0 | 0 | 23 | 12 | 2 | 5 | 9 | 1/88 | 0 | +2.31 |
| E3a | WTA_CHALL | 0 | 0 | 9 | 4 | 3 | 2 | 0 | 0/34 | 0 | +2.60 |
| E3a | ITF_M | 0 | 0 | 22 | 9 | 3 | 6 | 7 | 0/81 | 0 | -7.47 |
| E3a | ITF_W | 0 | 0 | 39 | 13 | 2 | 7 | 12 | 0/128 | 0 | +1.29 |
| E3b | ATP_CHALL | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0/2 | 0 | +1.20 |
| E3b | ITF_M | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0/1 | 0 | +0.40 |
| E3b | ITF_W | 0 | 0 | 0 | 1 | 0 | 2 | 0 | 0/4 | 0 | -3.20 |
| E4 | ITF_M | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1/1 | 0 | +0.30 |
| E4 | ITF_W | 0 | 0 | 2 | 0 | 0 | 1 | 0 | 0/5 | 0 | +1.50 |

## 0c · THE DECOMPOSITION — settled $ split: exit-cashed vs RODE-TO-SETTLEMENT (the structural-bleed number)

**RODE bucket: 76 legs, $-193.35 ← the structural-bleed number. Exit-cashed: 281 legs, $+178.30.**

| epoch | cat | cashed legs ($) | rode legs ($) | touched-not-filled W1/COR/W2 |
|---|---|---|---|---|
| E3a | ATP_MAIN | 4 (+1.65) | 1 (-7.47) | 0/0/0 |
| E3a | WTA_MAIN | 6 (+0.47) | 2 (-8.63) | 0/0/0 |
| E3a | ATP_CHALL | 68 (+49.91) | 20 (-47.60) | 1/0/4 |
| E3a | WTA_CHALL | 27 (+19.40) | 7 (-16.80) | 1/2/2 |
| E3a | ITF_M | 62 (+35.88) | 19 (-43.35) | 0/0/4 |
| E3a | ITF_W | 102 (+66.59) | 26 (-65.30) | 0/0/9 |
| E3b | ATP_CHALL | 2 (+1.20) | 0 (+0.00) | 0/0/0 |
| E3b | ITF_M | 1 (+0.40) | 0 (+0.00) | 0/0/0 |
| E3b | ITF_W | 3 (+1.00) | 1 (-4.20) | 0/0/0 |
| E4 | ITF_M | 1 (+0.30) | 0 (+0.00) | 0/0/0 |
| E4 | ITF_W | 5 (+1.50) | 0 (+0.00) | 0/0/0 |

### exit-fill window mix (cashed legs, honest clock; corridor end = onset > latch > honest+cat-median)

W1 2 · CORRIDOR 37 · W2 242

## 1 · THE ONE LEDGER LINE (cumulative since flip boot)

| settled $ | open exposure at basis | open mark-to-book | book right now (settled + mark − basis... stated) |
|---|---|---|---|
| **-15.05** | 60.11 (98 events) | 55.20 | **-15.05 settled, -4.91 unrealized on the open book** |

### per epoch (conception-stamped; NO blending)

| epoch | settled $ (n) | open basis (n) | open mark | luck flag |
|---|---|---|---|---|
| E3a | -15.25 (196) | 14.40 (12) | 14.10 | n≥30 |
| E3b | -1.60 (5) | 0.00 (1) | 0.00 | LUCK-POLLUTED (n<30) |
| E4 | +1.80 (4) | 45.71 (85) | 41.10 | LUCK-POLLUTED (n<30) |

### per cat within epoch (settled $; n<30 flagged)

| epoch | ATP_MAIN | WTA_MAIN | ATP_CHALL | WTA_CHALL | ITF_M | ITF_W |
|---|---|---|---|---|---|---|
| E3a | -5.82 (n=3‼) | -8.16 (n=4‼) | +2.31 (n=51) | +2.60 (n=18‼) | -7.47 (n=47) | +1.29 (n=73) |
| E3b | — | — | +1.20 (n=1‼) | — | +0.40 (n=1‼) | -3.20 (n=3‼) |
| E4 | — | — | — | — | +0.30 (n=1‼) | +1.50 (n=3‼) |
(‼ = LUCK-POLLUTED, n<30 per C46.)

## 3 · CONTINUITY PROOF (the reconcile, built in)

- **CUT A (11:13 ET, the morning autopsy's exchange pull):** this ledger reproduces **$-15.29 over 130 events** under the canonical settlement-realized rule. The autopsy headline was **−$9.33 over 142 'settled' games** — 
  **DIVERGENCE, NAMED (not smoothed): the autopsy's 'settled' included exited-but-unsettled legs at exit-realized P&L** (its any_open treated a filled-and-exited leg as closed even when the market hadn't settled), while this ledger counts settlement-realized only. Same fills, same fees, same exclusion of non-MATCH; the counting convention differs and the autopsy convention is hereby RETIRED. (Secondary contributors, same direction: events whose settlements landed 11:13–11:41 while the autopsy rendered, and the autopsy's game set was fills-through-11:13 only.)
- **CUT B (15:47 ET, the 15:52 roll's pull):** this ledger reproduces **$-18.65 over 196 events**. The roll read −$16.05 (E3a, 195 events) + E3b's 2 events — same settlement-realized rule, same code path: 
  match quality stated below the delta list.

### delta events between CUT A and CUT B (66 events settled in the gap)

| event | $ | settled at |
|---|---|---|
| LLENGERMATCH-26JUL06REHKOU | -2.20 | 07-06 11:17 |
| ITFMATCH-26JUL06LAPCIO | -2.05 | 07-06 11:17 |
| LLENGERMATCH-26JUL06DAMHUE | -1.00 | 07-06 11:22 |
| ITFWMATCH-26JUL06BOWMAT | +0.10 | 07-06 11:22 |
| LLENGERMATCH-26JUL06KYMFAU | +2.85 | 07-06 11:27 |
| ITFMATCH-26JUL06BONFAU | +1.65 | 07-06 11:27 |
| ITFMATCH-26JUL06BRABAR | +1.30 | 07-06 11:27 |
| ITFMATCH-26JUL06NAPPIN | -2.50 | 07-06 11:32 |
| LLENGERMATCH-26JUL06BASBAD | -0.35 | 07-06 11:32 |
| ITFMATCH-26JUL06GANVER | +1.15 | 07-06 11:37 |
| ITFWMATCH-26JUL06DRISLA | -1.10 | 07-06 11:37 |
| LLENGERMATCH-26JUL06CHIJAN | +1.20 | 07-06 11:42 |
| ITFMATCH-26JUL06ROURAM | +1.15 | 07-06 11:47 |
| ITFWMATCH-26JUL06SCHELI | -2.05 | 07-06 11:47 |
| ITFWMATCH-26JUL06BUEPOR | -0.25 | 07-06 11:52 |
| ITFWMATCH-26JUL06MARGLU | +1.50 | 07-06 11:52 |
| ITFWMATCH-26JUL06STETRA | +0.90 | 07-06 11:52 |
| ITFWMATCH-26JUL06URREVA | -5.65 | 07-06 11:57 |
| ITFMATCH-26JUL06DEDYUN | +0.25 | 07-06 12:08 |
| ITFWMATCH-26JUL06CENBUL | -0.05 | 07-06 12:08 |
| ITFWMATCH-26JUL06LACSTO | +1.00 | 07-06 12:08 |
| ITFWMATCH-26JUL06TRATEO | +0.95 | 07-06 12:17 |
| LLENGERMATCH-26JUL06POPSAN | +0.20 | 07-06 12:22 |
| ITFMATCH-26JUL06JAIHEN | +1.10 | 07-06 12:22 |
| LLENGERMATCH-26JUL06PAPMID | +1.15 | 07-06 12:27 |
| ITFMATCH-26JUL06VANHOR | +1.95 | 07-06 12:27 |
| LLENGERMATCH-26JUL06MAXGHI | -4.95 | 07-06 12:32 |
| ITFWMATCH-26JUL06HIEGUT | +0.95 | 07-06 12:32 |
| ITFWMATCH-26JUL06REEION | +1.00 | 07-06 12:32 |
| ITFWMATCH-26JUL06RABELI | +1.20 | 07-06 12:37 |
| LLENGERMATCH-26JUL06WERSAL | -2.90 | 07-06 12:42 |
| ITFMATCH-26JUL06BROTHU | +0.80 | 07-06 12:47 |
| ALLENGERMATCH-26JUL06DEHUD | -3.05 | 07-06 12:52 |
| WTAMATCH-26JUL06KEYNOS | -2.38 | 07-06 12:52 |
| LLENGERMATCH-26JUL06FOMDHA | +1.55 | 07-06 13:02 |
| LLENGERMATCH-26JUL06KASCIN | +1.65 | 07-06 13:02 |
| LLENGERMATCH-26JUL06WEIGRA | +0.05 | 07-06 13:12 |
| ITFMATCH-26JUL06DONDEV | +0.95 | 07-06 13:12 |
| LLENGERMATCH-26JUL06CURDOD | -0.30 | 07-06 13:12 |
| LLENGERMATCH-26JUL06HUETEN | +3.21 | 07-06 13:22 |
| ITFMATCH-26JUL06IAMBEN | +0.70 | 07-06 13:22 |
| LLENGERMATCH-26JUL06DENQUE | +0.15 | 07-06 13:22 |
| LLENGERMATCH-26JUL06CLAPAP | -0.40 | 07-06 13:27 |
| ITFMATCH-26JUL06PESTER | +1.05 | 07-06 13:32 |
| ITFMATCH-26JUL06SURMED | +0.35 | 07-06 13:32 |
| ITFWMATCH-26JUL06KULVOG | +2.50 | 07-06 13:37 |
| ITFWMATCH-26JUL06MULCIS | +2.21 | 07-06 13:37 |
| ITFWMATCH-26JUL06BERMEL | -4.00 | 07-06 13:42 |
| ITFWMATCH-26JUL06LIMDEK | +1.40 | 07-06 13:47 |
| ITFWMATCH-26JUL06LABTSY | +0.58 | 07-06 13:57 |
| LLENGERMATCH-26JUL06PALKOL | +0.95 | 07-06 14:02 |
| ITFMATCH-26JUL06XUXBER | -3.25 | 07-06 14:07 |
| ITFMATCH-26JUL06SLODIF | +0.40 | 07-06 14:12 |
| ITFWMATCH-26JUL06POHSTU | +1.90 | 07-06 14:17 |
| ITFWMATCH-26JUL06COHXAV | +0.95 | 07-06 14:27 |
| LLENGERMATCH-26JUL06OLIDAN | -1.40 | 07-06 14:42 |
| ITFMATCH-26JUL06LUEVAN | -7.35 | 07-06 14:42 |
| ITFWMATCH-26JUL06EVARHO | +1.20 | 07-06 14:42 |
| ITFWMATCH-26JUL06MARBED | -0.90 | 07-06 14:42 |
| LLENGERMATCH-26JUL06MAGROD | +0.45 | 07-06 14:52 |
| LLENGERMATCH-26JUL06PERMEL | +0.10 | 07-06 14:57 |
| ATPMATCH-26JUL06FRIBUB | +0.27 | 07-06 15:02 |
| ITFWMATCH-26JUL06SINUSU | -2.40 | 07-06 15:02 |
| ITFWMATCH-26JUL06VARMUN | +0.65 | 07-06 15:17 |
| ATPMATCH-26JUL06DIMFER | +1.10 | 07-06 15:26 |
| LLENGERMATCH-26JUL06SANARN | +0.45 | 07-06 15:42 |
| **Σ delta** | **-3.36** | |
CUT A (-15.29) + Σdelta (-3.36) = -18.65 vs CUT B -18.65 — internal sums must match exactly (they are the same rule); any residual is late fills on cut-A events, listed if nonzero.

## 4 · GRADE ROLLUP (per §0E; per cat per epoch, settled only)

| epoch | cat | A | B | C | D | F | both-fill | ≤97 | W1-cash legs | BOUHAR |
|---|---|---|---|---|---|---|---|---|---|---|
| E3a | ATP_MAIN | 0 | 0+1+1 | 0 | 1 | 0 | 2/3 | 2/2 | 0/5 | 0 |
| E3a | WTA_MAIN | 0 | 0+2+2 | 0 | 0 | 0 | 4/4 | 4/4 | 0/8 | 0 |
| E3a | ATP_CHALL | 0 | 0+23+12 | 2 | 5 | 9 | 37/51 | 35/37 | 1/88 | 0 |
| E3a | WTA_CHALL | 0 | 0+9+4 | 3 | 2 | 0 | 16/18 | 13/16 | 0/34 | 0 |
| E3a | ITF_M | 0 | 0+22+9 | 3 | 6 | 7 | 34/47 | 31/34 | 0/81 | 0 |
| E3a | ITF_W | 0 | 0+39+13 | 2 | 7 | 12 | 55/73 | 52/55 | 0/128 | 0 |
| E3b | ATP_CHALL | 0 | 0+1+0 | 0 | 0 | 0 | 1/1 | 1/1 | 0/2 | 0 |
| E3b | ITF_M | 0 | 0+0+0 | 0 | 1 | 0 | 0/1 | 0/0 | 0/1 | 0 |
| E3b | ITF_W | 0 | 0+0+1 | 0 | 2 | 0 | 1/3 | 1/1 | 0/4 | 0 |
| E4 | ITF_M | 0 | 0+0+0 | 0 | 1 | 0 | 0/1 | 0/0 | 1/1 | 0 |
| E4 | ITF_W | 0 | 0+2+0 | 0 | 1 | 0 | 2/3 | 2/2 | 0/5 | 0 |

## DAY ROLLUP — conception-day attribution (boundary = midnight ET)

Convention (amended 2026-07-07): an event belongs to the ET calendar day of its first conception; positions open at 00:00 carry on the PRIOR day's line and their settlements resolve it. The 00:00-nearest banked account snapshot is the day-close anchor (07-06 close anchored by the 00:18:15 snapshot, 18min late, stated).

| day | events | EXIT-CASHED $ (legs) | RODE $ (legs) | open: basis / mark / realized-so-far | day total | status |
|---|---|---|---|---|---|---|
| 2026-07-05 | 13 | +10.82 (23) | -3.85 (2) | 0.00 / 0.00 / +0.00 | +6.97 | FINAL |
| 2026-07-06 | 263 | +174.26 (271) | -189.50 (74) | 57.01 / 52.15 / +3.27 | -16.83 | OPEN (71 events) |
| 2026-07-07 | 27 | +0.00 (0) | +0.00 (0) | 3.10 / 3.05 / +0.00 | -0.05 | OPEN (27 events) |

Cross-check to §1 (the identity, stated): Σcashed +185.08 + Σrode -193.35 = -8.27; §1 settled = settlement-realized only — the bridge is exit-cash counted IMMEDIATELY here on exited-but-unsettled legs (the convention's point: the band did its job; settlement timing is irrelevant to it). Open basis/mark columns tie to §1's 60.11/55.20 exactly; RODE only ever holds legs that expired unfilled-at-exit.

## THE ROSTER — every engaged event, one row (settled AND open)

| ticker | cat | ep | legs | fills ¢ | comb | vs97 | Δaim | W1 | disp | grade | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LLENGERMATCH-26JUL06BARZIN | ATP_CHALL | E3a | 2 | BAR 51.5+ZIN 45.0 | 96.5 | ≤97 | 3,1 | W2_ONLY,W2_ONLY | OPEN,OPEN | OPEN | OPEN BAR@51.5×10(bid 52)+ZIN@45.0×5(bid 48)  cash -7.40 |
| LLENGERMATCH-26JUL06HOLSCH | ATP_CHALL | E3a | 0 | — | — | — | — | — | — | OPEN | OPEN no-position SCH rest@50 cash +0.00 |
| LLENGERMATCH-26JUL06ILARYB | ATP_CHALL | E3a | 1 | RYB 45.0 | — | — | 2 | W2_ONLY | OPEN | OPEN | OPEN RYB@45.0×5(bid 41) ILA rest@52 ach 104.0 cash -2.25 |
| LLENGERMATCH-26JUL06JUNMOR | ATP_CHALL | E3a | 1 | JUN 51.0 | — | — | 3 | W2_ONLY | OPEN | OPEN | OPEN JUN@51.0×5(bid 46) MOR rest@46 ach 106.0 cash -2.55 |
| LLENGERMATCH-26JUL06MALMAT | ATP_CHALL | E3a | 0 | — | — | — | — | — | — | OPEN | OPEN no-position MAL rest@43; MAT rest@49 cash +0.00 |
| LLENGERMATCH-26JUL06MCDWAL | ATP_CHALL | E3a | 0 | — | — | — | — | — | — | OPEN | OPEN no-position MCD rest@47; WAL rest@50 cash +0.00 |
| LLENGERMATCH-26JUL06VUKBRO | ATP_CHALL | E3b | 0 | — | — | — | — | — | — | OPEN | OPEN no-position BRO rest@49 cash +0.00 |
| LLENGERMATCH-26JUL07DEDTAB | ATP_CHALL | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position DED rest@51; TAB rest@46 cash +0.00 |
| LLENGERMATCH-26JUL07DJEBUE | ATP_CHALL | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position BUE rest@26; DJE rest@74 cash +0.00 |
| LLENGERMATCH-26JUL07GOMDAL | ATP_CHALL | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position DAL rest@71; GOM rest@28 cash +0.00 |
| LLENGERMATCH-26JUL07GOMOFN | ATP_CHALL | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position GOM rest@20; OFN rest@78 cash +0.00 |
| LLENGERMATCH-26JUL07JUSKRA | ATP_CHALL | E4 | 1 | JUS 62.0 | — | — | None | W2_ONLY | OPEN | OPEN | OPEN JUS@62.0×5(bid 61) KRA rest@35 ach 99.0 cash -3.10 |
| ATPMATCH-26JUL06LEHZVE | ATP_MAIN | E3a | 1 | ZVE 73.0 | — | — | -1 | W1_CASHED | X_W1 | OPEN | OPEN no-position  cash +0.93 |
| ITFMATCH-26JUL06BORHAR | ITF_M | E4 | 2 | BOR 55.0+HAR 38.5 | 93.5 | ≤97 | 7,4 | W2_ONLY,W2_ONLY | X_W2,X_W2 | OPEN | OPEN HAR@38.5×5(bid 0)  ach 138.5 cash -0.55 |
| ITFMATCH-26JUL06CHEJIN | ITF_M | E4 | 2 | CHE 53.0+JIN 43.0 | 96.0 | ≤97 | 3,8 | W2_ONLY,W1_REACHA | X_W2,X_CORRIDOR | OPEN | OPEN no-position  cash +1.15 |
| ITFMATCH-26JUL06FUKTAK | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position FUK rest@41; TAK rest@59 cash +0.00 |
| ITFMATCH-26JUL06GARPER | ITF_M | E3a | 0 | — | — | — | — | — | — | OPEN | OPEN no-position  cash +0.00 |
| ITFMATCH-26JUL06HANKUN | ITF_M | E4 | 2 | HAN 36.5+KUN 60.0 | 96.5 | ≤97 | -42,-18 | W1_REACHA,W2_ONLY | X_CORRIDOR,X_W2 | OPEN | OPEN HAN@36.5×5(bid 28)  ach 108.5 cash -0.60 |
| ITFMATCH-26JUL06HAZSHI | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position HAZ rest@32; SHI rest@68 cash +0.00 |
| ITFMATCH-26JUL06MATKOM | ITF_M | E4 | 2 | KOM 7.0+MAT 90.0 | 97.0 | ≤97 | 5,2 | W1_REACHA,W2_ONLY | X_CORRIDOR,OPEN | OPEN | OPEN MAT@90.0×5(bid 91)  ach 99.0 cash -4.30 |
| ITFMATCH-26JUL06NAKIDO | ITF_M | E4 | 1 | IDO 16.0 | — | — | 2 | W1_REACHA | OPEN | OPEN | OPEN IDO@16.0×5(bid 12) NAK rest@81 ach 105.0 cash -0.80 |
| ITFMATCH-26JUL06OCHMUT | ITF_M | E4 | 2 | MUT 23.0+OCH 73.0 | 96.0 | ≤97 | 2,2 | W1_CASHED,W2_ONLY | X_W1,OPEN | OPEN | OPEN MUT@23.0×5(bid 36)+OCH@73.0×5(bid 63)  cash -4.40 |
| ITFMATCH-26JUL06OKITAN | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position OKI rest@67; TAN rest@34 cash +0.00 |
| ITFMATCH-26JUL06PHATOM | ITF_M | E4 | 2 | PHA 21.0+TOM 75.0 | 96.0 | ≤97 | 1,-2 | no-clock,no-clock | X_W2,OPEN | OPEN | OPEN PHA@21.0×5(bid 31)+TOM@75.0×5(bid 66)  cash -4.50 |
| ITFMATCH-26JUL06SAKLIX | ITF_M | E4 | 1 | SAK 68.0 | — | — | None | no-clock | OPEN | OPEN | OPEN SAK@68.0×2(bid 68) LIX rest@29 ach 107.0 cash -1.36 |
| ITFMATCH-26JUL06TAGSUZ | ITF_M | E4 | 2 | SUZ 21.0+TAG 65.0 | 86.0 | ≤97 | 3,16 | W1_CASHED,W1_REACHA | X_W1,OPEN | OPEN | OPEN SUZ@21.0×5(bid 25)+TAG@65.0×5(bid 73)  cash -4.05 |
| ITFMATCH-26JUL06TANKAW | ITF_M | E4 | 2 | KAW 17.0+TAN 80.0 | 97.0 | ≤97 | 12,30 | W1_REACHA,W2_ONLY | OPEN,OPEN | OPEN | OPEN KAW@17.0×5(bid 14)+TAN@80.0×5(bid 78)  cash -4.85 |
| ITFMATCH-26JUL06TANVIS | ITF_M | E4 | 2 | TAN 34.0+VIS 63.0 | 97.0 | ≤97 | -1,0 | W1_CASHED,W2_ONLY | X_W1,OPEN | OPEN | OPEN VIS@63.0×2(bid 64) TAN rest@34 ach 102.0 cash -0.86 |
| ITFMATCH-26JUL06VANBOO | ITF_M | E4 | 1 | BOO 62.0 | — | — | -9 | W2_ONLY | OPEN | OPEN | OPEN BOO@62.0×5(bid 60) VAN rest@35 ach 105.0 cash -3.10 |
| ITFMATCH-26JUL06ZHAISH | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN ISH@None×5(bid 23) ZHA rest@65 ach 81 cash +0.00 |
| ITFMATCH-26JUL07ARSKOL | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position ARS rest@52; KOL rest@14 cash +0.00 |
| ITFMATCH-26JUL07BOJBOR | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position BOJ rest@51; BOR rest@4 cash +0.00 |
| ITFMATCH-26JUL07BOUMOC | ITF_M | E4 | 1 | BOU 67.0 | — | — | None | W2_ONLY | OPEN | OPEN | OPEN BOU@67.0×1(bid 67) MOC rest@30 ach 98.0 cash -0.67 |
| ITFMATCH-26JUL07BRAJAD | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position BRA rest@57; JAD rest@40 cash +0.00 |
| ITFMATCH-26JUL07BRECIO | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position CIO rest@25 cash +0.00 |
| ITFMATCH-26JUL07CHOCHE | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position CHE rest@34; CHO rest@65 cash +0.00 |
| ITFMATCH-26JUL07CHRMON | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position CHR rest@9; MON rest@87 cash +0.00 |
| ITFMATCH-26JUL07FAUVEL | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position FAU rest@53; VEL rest@42 cash +0.00 |
| ITFMATCH-26JUL07FONDUT | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position DUT rest@21 cash +0.00 |
| ITFMATCH-26JUL07HAUMIE | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position MIE rest@27 cash +0.00 |
| ITFMATCH-26JUL07HOMPAB | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position PAB rest@5 cash +0.00 |
| ITFMATCH-26JUL07JIMKUM | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position JIM rest@29; KUM rest@62 cash +0.00 |
| ITFMATCH-26JUL07JOVOPA | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position JOV rest@9; OPA rest@10 cash +0.00 |
| ITFMATCH-26JUL07KOIKAW | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position KAW rest@58; KOI rest@40 cash +0.00 |
| ITFMATCH-26JUL07LAVTOR | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position LAV rest@14; TOR rest@75 cash +0.00 |
| ITFMATCH-26JUL07MIKCLA | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position CLA rest@5 cash +0.00 |
| ITFMATCH-26JUL07OGUJAS | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position JAS rest@72; OGU rest@25 cash +0.00 |
| ITFMATCH-26JUL07PETVTE | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position PET rest@9; VTE rest@9 cash +0.00 |
| ITFMATCH-26JUL07POUOVE | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position OVE rest@87; POU rest@9 cash +0.00 |
| ITFMATCH-26JUL07REYMAL | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position MAL rest@77; REY rest@20 cash +0.00 |
| ITFMATCH-26JUL07ROCMIC | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position MIC rest@21 cash +0.00 |
| ITFMATCH-26JUL07SCHEIN | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position EIN rest@8 cash +0.00 |
| ITFMATCH-26JUL07SCHMUR | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position MUR rest@51; SCH rest@45 cash +0.00 |
| ITFMATCH-26JUL07STOVAN | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position STO rest@27; VAN rest@9 cash +0.00 |
| ITFMATCH-26JUL07STRHAR | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position HAR rest@30 cash +0.00 |
| ITFMATCH-26JUL07VANKOE | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position VAN rest@4 cash +0.00 |
| ITFMATCH-26JUL07WYGMAS | ITF_M | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position MAS rest@43 cash +0.00 |
| ITFWMATCH-26JUL06GAONON | ITF_W | E4 | 2 | GAO 19.6+NON 75.0 | 94.6 | ≤97 | -6,-7 | W1_CASHED,W1_REACHA | X_W1,X_W1 | OPEN | OPEN GAO@19.6×5(bid 7)+NON@75.0×0(bid 92)  cash -0.60 |
| ITFWMATCH-26JUL06KOSOUN | ITF_W | E4 | 2 | KOS 38.5+OUN 56.0 | 94.5 | ≤97 | 8,2 | W2_ONLY,W2_ONLY | X_W2,X_W2 | OPEN | OPEN KOS@38.5×5(bid 60)  ach 79.5 cash -0.85 |
| ITFWMATCH-26JUL06LIXSUN | ITF_W | E4 | 2 | LIX 34.0+SUN 63.0 | 97.0 | ≤97 | -6,2 | no-clock,no-clock | X_W2,X_W2 | OPEN | OPEN no-position  cash +0.80 |
| ITFWMATCH-26JUL06OHWLIU | ITF_W | E4 | 2 | LIU 23.0+OHW 74.0 | 97.0 | ≤97 | 12,4 | W2_ONLY,W2_ONLY | X_W2,OPEN | OPEN | OPEN OHW@74.0×5(bid 0)  ach 174.0 cash -3.45 |
| ITFWMATCH-26JUL06TIAZHO | ITF_W | E4 | 1 | ZHO 50.0 | — | — | -3 | W1_CASHED | X_W1 | OPEN | OPEN no-position TIA rest@47 cash +0.55 |
| ITFWMATCH-26JUL07ARYKRO | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position ARY rest@16; KRO rest@83 cash +0.00 |
| ITFWMATCH-26JUL07BATBEL | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position BAT rest@15; BEL rest@2 cash +0.00 |
| ITFWMATCH-26JUL07BEHBAR | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position BAR rest@24; BEH rest@18 cash +0.00 |
| ITFWMATCH-26JUL07COPBRE | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position BRE rest@66; COP rest@29 cash +0.00 |
| ITFWMATCH-26JUL07GOLALH | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position ALH rest@52; GOL rest@45 cash +0.00 |
| ITFWMATCH-26JUL07HERBAL | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position BAL rest@21; HER rest@79 cash +0.00 |
| ITFWMATCH-26JUL07KAKJAN | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position JAN rest@89; KAK rest@8 cash +0.00 |
| ITFWMATCH-26JUL07KHOSAM | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position SAM rest@8 cash +0.00 |
| ITFWMATCH-26JUL07KHRBEL | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position BEL rest@56; KHR rest@38 cash +0.00 |
| ITFWMATCH-26JUL07KOTOZE | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position KOT rest@4; OZE rest@93 cash +0.00 |
| ITFWMATCH-26JUL07KRYDYU | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position DYU rest@79; KRY rest@18 cash +0.00 |
| ITFWMATCH-26JUL07LANDEN | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position DEN rest@63; LAN rest@36 cash +0.00 |
| ITFWMATCH-26JUL07MANLUK | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position LUK rest@77; MAN rest@15 cash +0.00 |
| ITFWMATCH-26JUL07MCKGUD | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position GUD rest@14; MCK rest@80 cash +0.00 |
| ITFWMATCH-26JUL07MILSAK | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position MIL rest@52; SAK rest@43 cash +0.00 |
| ITFWMATCH-26JUL07PANZHO | ITF_W | E4 | 1 | ZHO 26.0 | — | — | 13 | W1_REACHA | OPEN | OPEN | OPEN ZHO@26.0×5(bid 17) PAN rest@71 ach 105.0 cash -1.30 |
| ITFWMATCH-26JUL07PATMAK | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position MAK rest@92; PAT rest@7 cash +0.00 |
| ITFWMATCH-26JUL07PIEPRI | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position PIE rest@54; PRI rest@38 cash +0.00 |
| ITFWMATCH-26JUL07PLOFON | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position FON rest@28; PLO rest@38 cash +0.00 |
| ITFWMATCH-26JUL07PODSMI | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position POD rest@32; SMI rest@66 cash +0.00 |
| ITFWMATCH-26JUL07PUSMAY | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position MAY rest@7; PUS rest@8 cash +0.00 |
| ITFWMATCH-26JUL07REVHER | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position HER rest@48; REV rest@20 cash +0.00 |
| ITFWMATCH-26JUL07RICMAD | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position MAD rest@35; RIC rest@60 cash +0.00 |
| ITFWMATCH-26JUL07SADSTA | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position SAD rest@22 cash +0.00 |
| ITFWMATCH-26JUL07SCHTRI | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position SCH rest@26; TRI rest@65 cash +0.00 |
| ITFWMATCH-26JUL07SENKEN | ITF_W | E4 | 1 | SEN 19.0 | — | — | 3 | W1_CASHED | X_W1 | OPEN | OPEN no-position KEN rest@78 cash +0.25 |
| ITFWMATCH-26JUL07SHKORL | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position ORL rest@5 cash +0.00 |
| ITFWMATCH-26JUL07SOZNIS | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position NIS rest@53; SOZ rest@42 cash +0.00 |
| ITFWMATCH-26JUL07SUSKOR | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position KOR rest@52; SUS rest@44 cash +0.00 |
| ITFWMATCH-26JUL07TODSTR | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position STR rest@87; TOD rest@10 cash +0.00 |
| ITFWMATCH-26JUL07VANVAN2 | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position VAN rest@91; VAN2 rest@4 cash +0.00 |
| ITFWMATCH-26JUL07YARHAY | ITF_W | E4 | 0 | — | — | — | — | — | — | OPEN | OPEN no-position HAY rest@55; YAR rest@20 cash +0.00 |
| LLENGERMATCH-26JUL06BRESAN | WTA_CHALL | E3a | 0 | — | — | — | — | — | — | OPEN | OPEN no-position BRE rest@86; SAN rest@12 cash +0.00 |
| LLENGERMATCH-26JUL06COLSMI | WTA_CHALL | E3a | 0 | — | — | — | — | — | — | OPEN | OPEN no-position COL rest@35 cash +0.00 |
| LLENGERMATCH-26JUL06ISHCRO | WTA_CHALL | E3a | 1 | ISH 38.0 | — | — | None | W2_ONLY | OPEN | OPEN | OPEN ISH@38.0×5(bid 38) CRO rest@58 ach 100.0 cash -1.90 |
| LLENGERMATCH-26JUL06LINMAR | WTA_CHALL | E3a | 1 | LIN 6.0 | — | — | 3 | W2_ONLY | OPEN | OPEN | OPEN LIN@6.0×5(bid 5) MAR rest@90 ach 102.0 cash -0.30 |
| LENGERMATCH-26JUL06ABOALVA | ATP_CHALL | E3b | 2 | ABO 55.0+ALVA 42.0 | 97.0 | ≤97 | -1,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.20 |
| LLENGERMATCH-26JUL06BARDAL | ATP_CHALL | E3a | 2 | BAR 56.0+DAL 40.0 | 96.0 | ≤97 | 3,2 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED -0.85 |
| LLENGERMATCH-26JUL06BASHOE | ATP_CHALL | E3a | 2 | BAS 46.0+HOE 51.0 | 97.0 | ≤97 | 1,3 | no-clock,no-clock | RODE,X_CORRIDOR | B | SETTLED -3.95 |
| ALLENGERMATCH-26JUL06CAMDE | ATP_CHALL | E3a | 2 | CAM 58.0+DE 39.0 | 97.0 | ≤97 | 2,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +2.00 |
| LLENGERMATCH-26JUL06CHADEM | ATP_CHALL | E3a | 1 | CHA 48.0 | — | — | 3 | no-clock | RODE | F | SETTLED -2.40 |
| LLENGERMATCH-26JUL06CHEYEV | ATP_CHALL | E3a | 2 | CHE 59.5+YEV 37.0 | 96.5 | ≤97 | 1,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +2.05 |
| LLENGERMATCH-26JUL06CHIJAN | ATP_CHALL | E3a | 2 | CHI 75.0+JAN 23.0 | 98.0 | 98-100 | 2,2 | no-clock,no-clock | X_W2,X_W2 | C | SETTLED +1.20 |
| LLENGERMATCH-26JUL06CLAPAP | ATP_CHALL | E3a | 1 | PAP 20.5 | — | — | 3 | no-clock | X_W2 | F | SETTLED -0.40 |
| LLENGERMATCH-26JUL06DALCAR | ATP_CHALL | E3a | 2 | CAR 3.0+DAL 94.0 | 97.0 | ≤97 | 1,1 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.40 |
| LLENGERMATCH-26JUL06DAMHUE | ATP_CHALL | E3a | 1 | HUE 20.0 | — | — | 4 | no-clock | RODE | F | SETTLED -1.00 |
| ALLENGERMATCH-26JUL06DEHUD | ATP_CHALL | E3a | 1 | HUD 61.0 | — | — | 3 | no-clock | RODE | F | SETTLED -3.05 |
| LLENGERMATCH-26JUL06DELWAL | ATP_CHALL | E3a | 2 | DEL 28.0+WAL 69.0 | 97.0 | ≤97 | 4,1 | no-clock,no-clock | X_CORRIDOR,X_CORRIDOR | B | SETTLED +1.30 |
| LLENGERMATCH-26JUL06DONCIZ | ATP_CHALL | E3a | 2 | CIZ 24.0+DON 73.0 | 97.0 | ≤97 | 4,1 | no-clock,no-clock | X_CORRIDOR,X_CORRIDOR | B | SETTLED +2.65 |
| LLENGERMATCH-26JUL06ERHSIN | ATP_CHALL | E3a | 2 | ERH 96.0+SIN 4.0 | 100.0 | 98-100 | 4,2 | no-clock,no-clock | X_W2,RODE | C | SETTLED -0.10 |
| LLENGERMATCH-26JUL06FOMDHA | ATP_CHALL | E3a | 2 | DHA 52.0+FOM 43.5 | 95.5 | ≤97 | 3,1 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.55 |
| LLENGERMATCH-26JUL06GOMLUZ | ATP_CHALL | E3a | 2 | GOM 71.0+LUZ 24.5 | 95.5 | ≤97 | 3,3 | no-clock,no-clock | X_CORRIDOR,X_CORRIDOR | B | SETTLED +0.15 |
| LLENGERMATCH-26JUL06HUAPUR | ATP_CHALL | E3a | 2 | HUA 35.0+PUR 61.5 | 96.5 | ≤97 | 3,1 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +2.15 |
| LLENGERMATCH-26JUL06HUETEN | ATP_CHALL | E3a | 2 | HUE 64.5+TEN 29.3 | 93.8 | ≤97 | 5,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +3.21 |
| LLENGERMATCH-26JUL06IVADIN | ATP_CHALL | E3a | 2 | DIN 20.0+IVA 77.0 | 97.0 | ≤97 | 3,2 | no-clock,no-clock | X_CORRIDOR,X_W2 | B | SETTLED +2.20 |
| LLENGERMATCH-26JUL06KASCIN | ATP_CHALL | E3a | 2 | CIN 54.0+KAS 43.0 | 97.0 | ≤97 | 3,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.65 |
| LLENGERMATCH-26JUL06KRACRI | ATP_CHALL | E3a | 2 | CRI 5.5+KRA 91.0 | 96.5 | ≤97 | 0,2 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.30 |
| LLENGERMATCH-26JUL06KUZSTR | ATP_CHALL | E3a | 2 | KUZ 71.0+STR 26.0 | 97.0 | ≤97 | 1,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +2.25 |
| LLENGERMATCH-26JUL06KYMFAU | ATP_CHALL | E3a | 2 | FAU 28.0+KYM 68.0 | 96.0 | ≤97 | -1,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +2.85 |
| LLENGERMATCH-26JUL06MAGROD | ATP_CHALL | E3a | 1 | MAG 44.0 | — | — | 3 | no-clock | X_CORRIDOR | D | SETTLED +0.45 |
| LLENGERMATCH-26JUL06MARBER | ATP_CHALL | E3a | 2 | BER 58.0+MAR 39.0 | 97.0 | ≤97 | 3,2 | W1_CASHED,W1_REACHA | X_W1,RODE | B | SETTLED -1.15 |
| LLENGERMATCH-26JUL06MARHAM | ATP_CHALL | E3a | 2 | HAM 5.0+MAR 92.0 | 97.0 | ≤97 | 2,0 | no-clock,no-clock | X_W2,RODE | B | SETTLED -4.40 |
| LLENGERMATCH-26JUL06MAXGHI | ATP_CHALL | E3a | 2 | GHI 54.0+MAX 43.0 | 97.0 | ≤97 | 2,3 | no-clock,no-clock | RODE,X_W2 | B | SETTLED -4.95 |
| LLENGERMATCH-26JUL06NIJRAH | ATP_CHALL | E3a | 2 | NIJ 57.0+RAH 40.0 | 97.0 | ≤97 | -1,3 | no-clock,no-clock | X_W2,RODE | B | SETTLED -1.43 |
| LLENGERMATCH-26JUL06OLIDAN | ATP_CHALL | E3a | 1 | OLI 36.0 | — | — | 5 | no-clock | X_CORRIDOR | F | SETTLED -1.40 |
| LLENGERMATCH-26JUL06OPIPET | ATP_CHALL | E3a | 2 | OPI 28.0+PET 69.0 | 97.0 | ≤97 | 5,0 | no-clock,no-clock | RODE,X_W2 | B | SETTLED -0.45 |
| LLENGERMATCH-26JUL06PALKOL | ATP_CHALL | E3a | 1 | KOL 75.0 | — | — | None | no-clock | X_W2 | D | SETTLED +0.95 |
| LLENGERMATCH-26JUL06PAPJAN | ATP_CHALL | E3a | 1 | PAP 53.0 | — | — | 3 | no-clock | X_W2 | D | SETTLED +0.70 |
| LLENGERMATCH-26JUL06PAPMID | ATP_CHALL | E3a | 2 | MID 50.0+PAP 47.0 | 97.0 | ≤97 | 2,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.15 |
| LLENGERMATCH-26JUL06PERMEL | ATP_CHALL | E3a | 2 | MEL 95.0+PER 1.0 | 96.0 | ≤97 | None,-4 | no-clock,no-clock | X_W2,RODE | B | SETTLED +0.10 |
| LLENGERMATCH-26JUL06PIEMOL | ATP_CHALL | E3a | 2 | MOL 52.0+PIE 45.0 | 97.0 | ≤97 | 3,4 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.15 |
| LLENGERMATCH-26JUL06POLHAI | ATP_CHALL | E3a | 2 | HAI 66.0+POL 31.0 | 97.0 | ≤97 | 1,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +3.00 |
| LLENGERMATCH-26JUL06POPSAN | ATP_CHALL | E3a | 1 | SAN 8.0 | — | — | 4 | no-clock | X_W2 | D | SETTLED +0.20 |
| LLENGERMATCH-26JUL06POTFEL | ATP_CHALL | E3a | 2 | FEL 57.0+POT 40.0 | 97.0 | ≤97 | 6,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +3.23 |
| LLENGERMATCH-26JUL06PRIORA | ATP_CHALL | E3a | 2 | ORA 39.5+PRI 56.0 | 95.5 | ≤97 | 2,2 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.50 |
| LLENGERMATCH-26JUL06RAQRIB | ATP_CHALL | E3a | 2 | RAQ 61.0+RIB 36.0 | 97.0 | ≤97 | 0,7 | no-clock,no-clock | X_W2,RODE | B | SETTLED -2.70 |
| LLENGERMATCH-26JUL06REHKOU | ATP_CHALL | E3a | 1 | KOU 44.0 | — | — | 3 | no-clock | RODE | F | SETTLED -2.20 |
| LLENGERMATCH-26JUL06SANARN | ATP_CHALL | E3a | 1 | SAN 44.0 | — | — | 2 | no-clock | X_CORRIDOR | D | SETTLED +0.45 |
| LLENGERMATCH-26JUL06SEGBRA | ATP_CHALL | E3a | 2 | BRA 36.0+SEG 61.0 | 97.0 | ≤97 | 3,3 | no-clock,no-clock | X_CORRIDOR,RODE | B | SETTLED +0.55 |
| LLENGERMATCH-26JUL06SEYMAR | ATP_CHALL | E3a | 1 | MAR 10.0 | — | — | 4 | no-clock | RODE | F | SETTLED -0.50 |
| LLENGERMATCH-26JUL06STALEC | ATP_CHALL | E3a | 2 | LEC 32.5+STA 64.0 | 96.5 | ≤97 | 2,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED -0.30 |
| LLENGERMATCH-26JUL06VALZHU | ATP_CHALL | E3a | 2 | VAL 71.0+ZHU 26.0 | 97.0 | ≤97 | 3,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.30 |
| LLENGERMATCH-26JUL06VILBOC | ATP_CHALL | E3a | 2 | BOC 22.0+VIL 75.0 | 97.0 | ≤97 | 1,3 | no-clock,no-clock | RODE,X_W2 | B | SETTLED -1.25 |
| LLENGERMATCH-26JUL06WALNEU | ATP_CHALL | E3a | 2 | NEU 28.0+WAL 69.0 | 97.0 | ≤97 | 3,2 | no-clock,no-clock | X_CORRIDOR,X_CORRIDOR | B | SETTLED +2.25 |
| LLENGERMATCH-26JUL06WEHVAN | ATP_CHALL | E3a | 1 | VAN 42.0 | — | — | 3 | no-clock | RODE | F | SETTLED -2.10 |
| LLENGERMATCH-26JUL06WEIGRA | ATP_CHALL | E3a | 2 | GRA 81.0+WEI 16.0 | 97.0 | ≤97 | 3,1 | no-clock,no-clock | X_W2,RODE | B | SETTLED +0.05 |
| LLENGERMATCH-26JUL06ZEBAND | ATP_CHALL | E3a | 1 | ZEB 20.0 | — | — | 3 | no-clock | RODE | F | SETTLED -1.00 |
| LLENGERMATCH-26JUL06ZORDEV | ATP_CHALL | E3a | 2 | DEV 42.0+ZOR 55.0 | 97.0 | ≤97 | 3,2 | no-clock,no-clock | X_W2,RODE | B | SETTLED -5.05 |
| ATPMATCH-26JUL06DECOB | ATP_MAIN | E3a | 2 | COB 23.0+DE 74.0 | 97.0 | ≤97 | 1,-3 | no-clock,no-clock | X_CORRIDOR,RODE | B | SETTLED -7.19 |
| ATPMATCH-26JUL06DIMFER | ATP_MAIN | E3a | 2 | DIM 64.0+FER 33.0 | 97.0 | ≤97 | -4,2 | W2_ONLY,W2_ONLY | X_W2,X_W2 | B | SETTLED +1.10 |
| ATPMATCH-26JUL06FRIBUB | ATP_MAIN | E3a | 1 | BUB 33.0 | — | — | 2 | W2_ONLY | X_W2 | D | SETTLED +0.27 |
| ITFMATCH-26JUL06ALEREG | ITF_M | E3a | 1 | ALE 51.0 | — | — | 3 | no-clock | RODE | F | SETTLED -2.55 |
| ITFMATCH-26JUL06ALIMIS | ITF_M | E3a | 2 | ALI 91.0+MIS 4.5 | 95.5 | ≤97 | 8,4 | no-clock,no-clock | X_W2,RODE | B | SETTLED -0.10 |
| ITFMATCH-26JUL06BEASCO | ITF_M | E3a | 2 | BEA 64.0+SCO 33.0 | 97.0 | ≤97 | 1,12 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +2.30 |
| ITFMATCH-26JUL06BONFAU | ITF_M | E3a | 2 | BON 66.0+FAU 28.0 | 94.0 | ≤97 | 3,7 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.65 |
| ITFMATCH-26JUL06BRABAR | ITF_M | E3a | 2 | BAR 62.0+BRA 35.0 | 97.0 | ≤97 | 3,10 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.30 |
| ITFMATCH-26JUL06BROTHU | ITF_M | E3a | 1 | THU 58.0 | — | — | 7 | no-clock | X_CORRIDOR | D | SETTLED +0.80 |
| ITFMATCH-26JUL06CASBAY | ITF_M | E3a | 1 | CAS 45.0 | — | — | 43 | no-clock | RODE | F | SETTLED -2.25 |
| ITFMATCH-26JUL06CUNLIM | ITF_M | E3a | 1 | LIM 20.0 | — | — | 4 | no-clock | X_W2 | D | SETTLED +0.80 |
| ITFMATCH-26JUL06DEDYUN | ITF_M | E3a | 2 | DED 77.0+YUN 20.0 | 97.0 | ≤97 | 7,-3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.25 |
| ITFMATCH-26JUL06DONDEV | ITF_M | E3a | 1 | DON 73.0 | — | — | 7 | no-clock | X_W2 | D | SETTLED +0.95 |
| ITFMATCH-26JUL06DUGHOF | ITF_M | E3a | 2 | DUG 76.0+HOF 21.0 | 97.0 | ≤97 | 25,15 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.25 |
| ITFMATCH-26JUL06DUHCAR | ITF_M | E3a | 2 | CAR 12.0+DUH 88.0 | 100.0 | 98-100 | 7,9 | no-clock,no-clock | RODE,X_W2 | C | SETTLED -0.10 |
| ITFMATCH-26JUL06ELDHAU | ITF_M | E3a | 2 | ELD 65.0+HAU 32.0 | 97.0 | ≤97 | 9,9 | no-clock,no-clock | RODE,X_W2 | B | SETTLED +0.55 |
| ITFMATCH-26JUL06FIXSAL | ITF_M | E3a | 2 | FIX 80.0+SAL 17.0 | 97.0 | ≤97 | -11,-5 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.30 |
| ITFMATCH-26JUL06GANVER | ITF_M | E3a | 2 | GAN 47.0+VER 50.0 | 97.0 | ≤97 | 5,8 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.15 |
| ITFMATCH-26JUL06GARCIO | ITF_M | E3a | 2 | CIO 41.0+GAR 57.0 | 98.0 | 98-100 | 9,2 | no-clock,no-clock | RODE,X_W2 | C | SETTLED -1.40 |
| ITFMATCH-26JUL06GENAZO | ITF_M | E3a | 2 | AZO 16.0+GEN 81.0 | 97.0 | ≤97 | 7,8 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.30 |
| ITFMATCH-26JUL06HERNAG | ITF_M | E3a | 2 | HER 70.0+NAG 15.8 | 85.8 | ≤97 | 21,27 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.39 |
| ITFMATCH-26JUL06HOSGAT | ITF_M | E3a | 2 | GAT 38.0+HOS 57.5 | 95.5 | ≤97 | 4,5 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.95 |
| ITFMATCH-26JUL06IAMBEN | ITF_M | E3a | 1 | BEN 30.5 | — | — | 15 | no-clock | X_W2 | D | SETTLED +0.70 |
| ITFMATCH-26JUL06JAIHEN | ITF_M | E3a | 2 | HEN 51.0+JAI 46.0 | 97.0 | ≤97 | -12,5 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.10 |
| ITFMATCH-26JUL06KASLIL | ITF_M | E3a | 2 | KAS 66.0+LIL 29.5 | 95.5 | ≤97 | 63,30 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED -0.10 |
| ITFMATCH-26JUL06KIMSHI | ITF_M | E4 | 1 | SHI 19.0 | — | — | 2 | W1_CASHED | X_W1 | D | SETTLED +0.30 |
| ITFMATCH-26JUL06LAPCIO | ITF_M | E3a | 1 | CIO 41.0 | — | — | 5 | no-clock | RODE | F | SETTLED -2.05 |
| ITFMATCH-26JUL06LARJIM | ITF_M | E3a | 2 | JIM 57.0+LAR 40.0 | 97.0 | ≤97 | 9,9 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.20 |
| ITFMATCH-26JUL06LAZVAC | ITF_M | E3a | 2 | LAZ 56.0+VAC 39.0 | 95.0 | ≤97 | 8,9 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.15 |
| ITFMATCH-26JUL06LENTHE | ITF_M | E3a | 2 | LEN 32.0+THE 65.0 | 97.0 | ≤97 | -23,9 | no-clock,no-clock | RODE,RODE | B | SETTLED -3.02 |
| ITFMATCH-26JUL06LIBNAK | ITF_M | E3a | 1 | LIB 40.0 | — | — | 6 | no-clock | X_W2 | D | SETTLED +0.40 |
| ITFMATCH-26JUL06LUEVAN | ITF_M | E3a | 2 | LUE 74.0+VAN 22.0 | 96.0 | ≤97 | 3,6 | no-clock,no-clock | RODE,X_W2 | B | SETTLED -7.35 |
| ITFMATCH-26JUL06MEHCOU | ITF_M | E3a | 2 | COU 55.0+MEH 31.5 | 86.5 | ≤97 | 7,13 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +4.25 |
| ITFMATCH-26JUL06NAPPIN | ITF_M | E3a | 2 | NAP 39.0+PIN 58.0 | 97.0 | ≤97 | -9,3 | no-clock,no-clock | X_W2,RODE | B | SETTLED -2.50 |
| ITFMATCH-26JUL06PESTER | ITF_M | E3a | 2 | PES 46.0+TER 51.0 | 97.0 | ≤97 | 21,17 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.05 |
| ITFMATCH-26JUL06ROJBEC | ITF_M | E3a | 1 | ROJ 10.0 | — | — | 3 | no-clock | RODE | F | SETTLED -0.50 |
| ITFMATCH-26JUL06ROURAM | ITF_M | E3a | 2 | RAM 56.0+ROU 37.0 | 93.0 | ≤97 | 6,4 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.15 |
| ITFMATCH-26JUL06SALBRE | ITF_M | E3a | 2 | BRE 7.0+SAL 90.0 | 97.0 | ≤97 | 5,4 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.60 |
| ITFMATCH-26JUL06SALNGW | ITF_M | E3a | 2 | NGW 39.0+SAL 58.0 | 97.0 | ≤97 | 7,10 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.20 |
| ITFMATCH-26JUL06SLODIF | ITF_M | E3b | 1 | DIF 38.0 | — | — | -4 | no-clock | X_CORRIDOR | D | SETTLED +0.40 |
| ITFMATCH-26JUL06STAGUI | ITF_M | E3a | 1 | GUI 37.0 | — | — | 29 | no-clock | RODE | F | SETTLED -1.85 |
| ITFMATCH-26JUL06STEAUN | ITF_M | E3a | 2 | AUN 14.0+STE 83.0 | 97.0 | ≤97 | 4,4 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.30 |
| ITFMATCH-26JUL06SURMED | ITF_M | E3a | 1 | SUR 41.0 | — | — | 23 | no-clock | X_W2 | D | SETTLED +0.35 |
| ITFMATCH-26JUL06TEUHAS | ITF_M | E3a | 2 | HAS 67.0+TEU 30.0 | 97.0 | ≤97 | 6,16 | no-clock,no-clock | X_W2,RODE | B | SETTLED -2.05 |
| ITFMATCH-26JUL06TEXCAR | ITF_M | E3a | 2 | CAR 30.0+TEX 67.0 | 97.0 | ≤97 | -2,-7 | no-clock,no-clock | X_W2,RODE | B | SETTLED -3.00 |
| ITFMATCH-26JUL06TIMJEF | ITF_M | E3a | 2 | JEF 71.5+TIM 20.0 | 91.5 | ≤97 | 5,5 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED -2.54 |
| ITFMATCH-26JUL06TISVER | ITF_M | E3a | 2 | TIS 44.0+VER 53.0 | 97.0 | ≤97 | 41,38 | no-clock,no-clock | X_W2,RODE | B | SETTLED -2.20 |
| ITFMATCH-26JUL06TRUTRA | ITF_M | E3a | 1 | TRA 27.0 | — | — | 7 | no-clock | RODE | F | SETTLED -1.35 |
| ITFMATCH-26JUL06TSIAND | ITF_M | E3a | 2 | AND 24.0+TSI 77.0 | 101.0 | >100 | 20,73 | no-clock,no-clock | X_W2,X_W2 | C | SETTLED +1.30 |
| ITFMATCH-26JUL06VANHOR | ITF_M | E3a | 2 | HOR 32.0+VAN 63.0 | 95.0 | ≤97 | 8,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.95 |
| ITFMATCH-26JUL06VULCOU | ITF_M | E3a | 2 | COU 16.0+VUL 81.0 | 97.0 | ≤97 | 6,1 | no-clock,no-clock | RODE,X_W2 | B | SETTLED +0.05 |
| ITFMATCH-26JUL06XUXBER | ITF_M | E3a | 1 | XUX 65.0 | — | — | -8 | no-clock | RODE | F | SETTLED -3.25 |
| ITFWMATCH-26JUL06ADKFER | ITF_W | E3a | 2 | ADK 77.0+FER 20.0 | 97.0 | ≤97 | 28,8 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.20 |
| ITFWMATCH-26JUL06BERMEL | ITF_W | E3b | 2 | BER 84.0+MEL 13.0 | 97.0 | ≤97 | 9,1 | no-clock,no-clock | RODE,X_W2 | B | SETTLED -4.00 |
| ITFWMATCH-26JUL06BOIBOY | ITF_W | E3a | 1 | BOI 77.0 | — | — | 2 | no-clock | RODE | F | SETTLED -3.85 |
| ITFWMATCH-26JUL06BOSTOP | ITF_W | E3a | 2 | BOS 68.0+TOP 27.5 | 95.5 | ≤97 | 6,0 | no-clock,no-clock | X_W2,RODE | B | SETTLED -1.85 |
| ITFWMATCH-26JUL06BOWMAT | ITF_W | E3a | 2 | BOW 8.0+MAT 88.0 | 96.0 | ≤97 | 6,39 | no-clock,no-clock | RODE,X_W2 | B | SETTLED +0.10 |
| ITFWMATCH-26JUL06BRESAF | ITF_W | E3a | 2 | BRE 63.0+SAF 34.0 | 97.0 | ≤97 | 2,2 | no-clock,no-clock | X_CORRIDOR,X_CORRIDOR | B | SETTLED -0.60 |
| ITFWMATCH-26JUL06BUEPOR | ITF_W | E3a | 1 | POR 5.0 | — | — | 3 | no-clock | RODE | F | SETTLED -0.25 |
| ITFWMATCH-26JUL06BUYALV | ITF_W | E3a | 2 | ALV 23.0+BUY 69.0 | 92.0 | ≤97 | 12,19 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.45 |
| ITFWMATCH-26JUL06CAIOHX | ITF_W | E4 | 2 | CAI 23.0+OHX 74.0 | 97.0 | ≤97 | 0,6 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.00 |
| ITFWMATCH-26JUL06CENBUL | ITF_W | E3a | 2 | BUL 20.0+CEN 77.0 | 97.0 | ≤97 | 5,14 | no-clock,no-clock | RODE,X_W2 | B | SETTLED -0.05 |
| ITFWMATCH-26JUL06CHOLIX | ITF_W | E4 | 1 | LIX 33.0 | — | — | -34 | no-clock | X_W2 | D | SETTLED +0.35 |
| ITFWMATCH-26JUL06CHOPHA | ITF_W | E4 | 2 | CHO 79.0+PHA 16.0 | 95.0 | ≤97 | 2,10 | W2_ONLY,W2_ONLY | X_W2,X_W2 | B | SETTLED +1.15 |
| ITFWMATCH-26JUL06COHXAV | ITF_W | E3a | 2 | COH 51.0+XAV 47.0 | 98.0 | 98-100 | 49,4 | no-clock,no-clock | X_W2,X_W2 | C | SETTLED +0.95 |
| ITFWMATCH-26JUL06DIANIK | ITF_W | E3a | 2 | DIA 44.5+NIK 52.0 | 96.5 | ≤97 | 21,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +5.69 |
| ITFWMATCH-26JUL06DRISLA | ITF_W | E3a | 2 | DRI 36.0+SLA 61.0 | 97.0 | ≤97 | 35,12 | no-clock,no-clock | RODE,X_W2 | B | SETTLED -1.10 |
| ITFWMATCH-26JUL06DZJMCK | ITF_W | E3a | 2 | DZJ 77.0+MCK 22.0 | 99.0 | 98-100 | 36,10 | no-clock,no-clock | X_W2,X_W2 | C | SETTLED +1.25 |
| ITFWMATCH-26JUL06EVARHO | ITF_W | E3a | 2 | EVA 79.0+RHO 18.0 | 97.0 | ≤97 | 30,12 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.20 |
| ITFWMATCH-26JUL06EWAMAN | ITF_W | E3a | 2 | EWA 70.0+MAN 27.0 | 97.0 | ≤97 | 7,13 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.20 |
| ITFWMATCH-26JUL06FAVKLY | ITF_W | E3a | 2 | FAV 15.0+KLY 41.0 | 56.0 | ≤97 | 12,36 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.50 |
| ITFWMATCH-26JUL06GALTSE | ITF_W | E3a | 1 | GAL 77.0 | — | — | 6 | no-clock | RODE | F | SETTLED -3.85 |
| ITFWMATCH-26JUL06GANPUI | ITF_W | E3a | 2 | GAN 83.0+PUI 12.5 | 95.5 | ≤97 | 4,10 | no-clock,no-clock | X_W2,RODE | B | SETTLED -0.50 |
| ITFWMATCH-26JUL06HEDCHI | ITF_W | E3a | 2 | CHI 51.0+HED 44.0 | 95.0 | ≤97 | 31,31 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.95 |
| ITFWMATCH-26JUL06HIEGUT | ITF_W | E3a | 2 | GUT 56.0+HIE 41.0 | 97.0 | ≤97 | 3,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.95 |
| ITFWMATCH-26JUL06HOSFEH | ITF_W | E3a | 1 | FEH 61.0 | — | — | -2 | no-clock | RODE | F | SETTLED -3.05 |
| ITFWMATCH-26JUL06ILIEBE | ITF_W | E3a | 2 | EBE 52.0+ILI 45.0 | 97.0 | ≤97 | 3,8 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.05 |
| ITFWMATCH-26JUL06IVAKUH | ITF_W | E3a | 2 | IVA 60.0+KUH 37.0 | 97.0 | ≤97 | 1,4 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +2.87 |
| ITFWMATCH-26JUL06JOSKUM | ITF_W | E3a | 2 | JOS 67.0+KUM 28.0 | 95.0 | ≤97 | -12,-3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.15 |
| ITFWMATCH-26JUL06JULOLI | ITF_W | E3b | 1 | JUL 16.0 | — | — | 8 | no-clock | X_CORRIDOR | D | SETTLED +0.20 |
| ITFWMATCH-26JUL06KARBAS | ITF_W | E3a | 2 | BAS 26.0+KAR 69.5 | 95.5 | ≤97 | 0,1 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +2.80 |
| ITFWMATCH-26JUL06KARVIS | ITF_W | E3a | 2 | KAR 76.0+VIS 21.0 | 97.0 | ≤97 | 3,13 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.20 |
| ITFWMATCH-26JUL06KOTCHI | ITF_W | E3a | 2 | CHI 45.0+KOT 52.0 | 97.0 | ≤97 | 4,31 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.05 |
| ITFWMATCH-26JUL06KOVDAE | ITF_W | E3a | 2 | DAE 18.0+KOV 76.0 | 94.0 | ≤97 | 4,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.20 |
| ITFWMATCH-26JUL06KULGON | ITF_W | E3a | 1 | GON 22.0 | — | — | 6 | no-clock | RODE | F | SETTLED -1.10 |
| ITFWMATCH-26JUL06KULVOG | ITF_W | E3a | 2 | KUL 56.5+VOG 39.0 | 95.5 | ≤97 | 11,7 | no-clock,no-clock | X_W2,X_CORRIDOR | B | SETTLED +2.50 |
| ITFWMATCH-26JUL06LABTSY | ITF_W | E3a | 1 | TSY 62.0 | — | — | 41 | no-clock | X_W2 | D | SETTLED +0.58 |
| ITFWMATCH-26JUL06LACSTO | ITF_W | E3a | 2 | LAC 59.0+STO 38.0 | 97.0 | ≤97 | -25,25 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.00 |
| ITFWMATCH-26JUL06LIMDEK | ITF_W | E3a | 2 | DEK 23.0+LIM 73.0 | 96.0 | ≤97 | -1,2 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.40 |
| ITFWMATCH-26JUL06LUCGAD | ITF_W | E3a | 2 | GAD 37.0+LUC 60.0 | 97.0 | ≤97 | 4,0 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +4.20 |
| ITFWMATCH-26JUL06LUKNOE | ITF_W | E3a | 2 | LUK 69.0+NOE 26.0 | 95.0 | ≤97 | -3,-1 | no-clock,no-clock | RODE,X_W2 | B | SETTLED -3.15 |
| ITFWMATCH-26JUL06MARBED | ITF_W | E3a | 1 | BED 18.0 | — | — | 14 | no-clock | RODE | F | SETTLED -0.90 |
| ITFWMATCH-26JUL06MARGLU | ITF_W | E3a | 2 | GLU 68.0+MAR 29.0 | 97.0 | ≤97 | 5,5 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.50 |
| ITFWMATCH-26JUL06MCAENC | ITF_W | E3a | 2 | ENC 51.0+MCA 42.0 | 93.0 | ≤97 | 2,12 | no-clock,no-clock | X_W2,RODE | B | SETTLED -2.51 |
| ITFWMATCH-26JUL06MELRAB | ITF_W | E3a | 1 | RAB 12.0 | — | — | 3 | no-clock | RODE | F | SETTLED -0.60 |
| ITFWMATCH-26JUL06MILHER | ITF_W | E3a | 2 | HER 16.0+MIL 79.5 | 95.5 | ≤97 | 13,32 | no-clock,no-clock | X_CORRIDOR,X_CORRIDOR | B | SETTLED +2.15 |
| ITFWMATCH-26JUL06MULCIS | ITF_W | E3a | 2 | CIS 39.0+MUL 58.0 | 97.0 | ≤97 | 9,19 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +2.21 |
| ITFWMATCH-26JUL06OKASAK | ITF_W | E3a | 1 | OKA 41.0 | — | — | 20 | no-clock | RODE | F | SETTLED -2.05 |
| ITFWMATCH-26JUL06OKUPRI | ITF_W | E3a | 2 | OKU 56.0+PRI 41.0 | 97.0 | ≤97 | 7,16 | no-clock,no-clock | RODE,X_CORRIDOR | B | SETTLED +0.55 |
| ITFWMATCH-26JUL06OLUZAM | ITF_W | E3b | 1 | ZAM 54.0 | — | — | 2 | no-clock | X_W2 | D | SETTLED +0.60 |
| ITFWMATCH-26JUL06PACLOV | ITF_W | E3a | 2 | LOV 45.0+PAC 52.0 | 97.0 | ≤97 | 8,7 | no-clock,no-clock | X_CORRIDOR,RODE | B | SETTLED -4.75 |
| ITFWMATCH-26JUL06PASCOP | ITF_W | E3a | 2 | COP 85.0+PAS 10.0 | 95.0 | ≤97 | 2,4 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.40 |
| ITFWMATCH-26JUL06PEEPAH | ITF_W | E3a | 2 | PAH 58.0+PEE 38.5 | 96.5 | ≤97 | 52,34 | no-clock,no-clock | X_CORRIDOR,X_CORRIDOR | B | SETTLED -0.97 |
| ITFWMATCH-26JUL06PIERAD | ITF_W | E3a | 1 | RAD 33.0 | — | — | 15 | no-clock | RODE | F | SETTLED -1.65 |
| ITFWMATCH-26JUL06PODLUK | ITF_W | E3a | 2 | LUK 70.0+POD 25.5 | 95.5 | ≤97 | 17,9 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.00 |
| ITFWMATCH-26JUL06POHSTU | ITF_W | E3a | 1 | STU 68.0 | — | — | 2 | no-clock | X_W2 | D | SETTLED +1.90 |
| ITFWMATCH-26JUL06POPSOL | ITF_W | E3a | 2 | POP 36.0+SOL 61.0 | 97.0 | ≤97 | 15,11 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.75 |
| ITFWMATCH-26JUL06POZMLA | ITF_W | E3a | 2 | MLA 8.0+POZ 89.0 | 97.0 | ≤97 | 7,2 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.60 |
| ITFWMATCH-26JUL06PRINIJ | ITF_W | E3a | 1 | NIJ 30.0 | — | — | 4 | no-clock | RODE | F | SETTLED -1.50 |
| ITFWMATCH-26JUL06RABELI | ITF_W | E3a | 2 | ELI 18.0+RAB 79.0 | 97.0 | ≤97 | 13,75 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.20 |
| ITFWMATCH-26JUL06REEION | ITF_W | E3a | 2 | ION 59.0+REE 38.0 | 97.0 | ≤97 | 10,10 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.00 |
| ITFWMATCH-26JUL06RICMIT | ITF_W | E3a | 1 | MIT 9.0 | — | — | 6 | no-clock | X_W2 | D | SETTLED +0.15 |
| ITFWMATCH-26JUL06SACLAZ | ITF_W | E3a | 2 | LAZ 17.0+SAC 78.0 | 95.0 | ≤97 | 8,5 | no-clock,no-clock | X_CORRIDOR,X_CORRIDOR | B | SETTLED +0.45 |
| ITFWMATCH-26JUL06SCHELI | ITF_W | E3a | 1 | ELI 41.0 | — | — | 40 | no-clock | RODE | F | SETTLED -2.05 |
| ITFWMATCH-26JUL06SILDIG | ITF_W | E3a | 2 | DIG 98.0+SIL 9.0 | 107.0 | >100 | 6,2 | no-clock,no-clock | X_W2,RODE | D | SETTLED -0.45 |
| ITFWMATCH-26JUL06SIMCIR | ITF_W | E3a | 2 | CIR 15.0+SIM 81.0 | 96.0 | ≤97 | 4,0 | no-clock,no-clock | X_CORRIDOR,X_W2 | B | SETTLED +1.20 |
| ITFWMATCH-26JUL06SINUSU | ITF_W | E3a | 2 | SIN 35.0+USU 62.0 | 97.0 | ≤97 | 30,56 | no-clock,no-clock | X_W2,RODE | B | SETTLED -2.40 |
| ITFWMATCH-26JUL06SPIMED | ITF_W | E3a | 2 | MED 8.0+SPI 88.0 | 96.0 | ≤97 | 7,7 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.65 |
| ITFWMATCH-26JUL06STETRA | ITF_W | E3a | 1 | STE 80.0 | — | — | 4 | no-clock | X_W2 | D | SETTLED +0.90 |
| ITFWMATCH-26JUL06TEISCH | ITF_W | E3a | 2 | SCH 4.0+TEI 87.0 | 91.0 | ≤97 | 2,35 | no-clock,no-clock | X_W2,RODE | B | SETTLED -4.20 |
| ITFWMATCH-26JUL06TODSAG | ITF_W | E3a | 2 | SAG 27.5+TOD 68.0 | 95.5 | ≤97 | 5,6 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.75 |
| ITFWMATCH-26JUL06TRATEO | ITF_W | E3a | 1 | TEO 78.0 | — | — | -14 | no-clock | X_W2 | D | SETTLED +0.95 |
| ITFWMATCH-26JUL06TRIVOR | ITF_W | E3a | 2 | TRI 8.0+VOR 89.0 | 97.0 | ≤97 | 7,40 | no-clock,no-clock | X_W2,RODE | B | SETTLED -4.30 |
| ITFWMATCH-26JUL06URREVA | ITF_W | E3a | 2 | EVA 37.0+URR 60.0 | 97.0 | ≤97 | 18,6 | no-clock,no-clock | X_W2,RODE | B | SETTLED -5.65 |
| ITFWMATCH-26JUL06VAJRAM | ITF_W | E3a | 2 | RAM 15.0+VAJ 82.0 | 97.0 | ≤97 | 10,8 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +0.17 |
| ITFWMATCH-26JUL06VARMUN | ITF_W | E3a | 1 | VAR 85.0 | — | — | 5 | no-clock | X_W2 | D | SETTLED +0.65 |
| ITFWMATCH-26JUL06VIRKOV | ITF_W | E3a | 2 | KOV 41.0+VIR 56.0 | 97.0 | ≤97 | 17,2 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.70 |
| ITFWMATCH-26JUL06VLADIL | ITF_W | E3a | 2 | DIL 56.0+VLA 35.5 | 91.5 | ≤97 | 4,7 | no-clock,no-clock | X_CORRIDOR,X_CORRIDOR | B | SETTLED -0.45 |
| ITFWMATCH-26JUL06WAGYOU | ITF_W | E3a | 2 | WAG 34.0+YOU 63.0 | 97.0 | ≤97 | 24,14 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.45 |
| ITFWMATCH-26JUL06WONIBR | ITF_W | E3a | 1 | IBR 65.0 | — | — | 13 | no-clock | RODE | F | SETTLED -3.25 |
| ITFWMATCH-26JUL06ZRNLUE | ITF_W | E3a | 2 | LUE 69.0+ZRN 24.0 | 93.0 | ≤97 | 63,26 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED -1.40 |
| LLENGERMATCH-26JUL06ARANIL | WTA_CHALL | E3a | 2 | ARA 73.0+NIL 24.0 | 97.0 | ≤97 | 3,2 | W2_ONLY,W2_ONLY | X_W2,RODE | B | SETTLED -0.30 |
| LLENGERMATCH-26JUL06BASBAD | WTA_CHALL | E3a | 2 | BAD 74.0+BAS 25.0 | 99.0 | 98-100 | 3,4 | no-clock,no-clock | X_CORRIDOR,RODE | C | SETTLED -0.35 |
| LLENGERMATCH-26JUL06BLIAND | WTA_CHALL | E3a | 2 | AND 33.0+BLI 64.0 | 97.0 | ≤97 | 1,3 | W2_ONLY,W2_ONLY | X_W2,X_W2 | B | SETTLED +1.10 |
| LLENGERMATCH-26JUL06BOUKOT | WTA_CHALL | E3a | 2 | BOU 20.0+KOT 77.0 | 97.0 | ≤97 | 0,3 | W2_ONLY,W2_ONLY | RODE,X_W2 | B | SETTLED -0.05 |
| LLENGERMATCH-26JUL06BULSTR | WTA_CHALL | E3a | 2 | BUL 68.0+STR 29.0 | 97.0 | ≤97 | 0,6 | W2_ONLY,W2_ONLY | X_W2,X_W2 | B | SETTLED +1.20 |
| LLENGERMATCH-26JUL06CURDOD | WTA_CHALL | E3a | 2 | CUR 66.0+DOD 30.0 | 96.0 | ≤97 | 1,4 | W2_ONLY,W2_ONLY | X_W2,X_CORRIDOR | B | SETTLED -0.30 |
| LLENGERMATCH-26JUL06DENQUE | WTA_CHALL | E3a | 1 | DEN 5.0 | — | — | 4 | W2_ONLY | X_W2 | D | SETTLED +0.15 |
| LLENGERMATCH-26JUL06GRAMAS | WTA_CHALL | E3a | 2 | GRA 29.5+MAS 67.0 | 96.5 | ≤97 | 0,3 | W2_ONLY,W2_ONLY | X_W2,X_W2 | B | SETTLED +1.40 |
| LLENGERMATCH-26JUL06HERNGU | WTA_CHALL | E3a | 2 | HER 41.0+NGU 58.0 | 99.0 | 98-100 | 2,4 | no-clock,no-clock | X_W2,RODE | C | SETTLED -2.60 |
| LLENGERMATCH-26JUL06HESPAL | WTA_CHALL | E3a | 2 | HES 33.0+PAL 69.0 | 102.0 | >100 | 7,3 | W2_ONLY,W2_ONLY | X_CORRIDOR,RODE | C | SETTLED -3.10 |
| LLENGERMATCH-26JUL06LEWMAR | WTA_CHALL | E3a | 2 | LEW 54.0+MAR 43.0 | 97.0 | ≤97 | 2,3 | no-clock,no-clock | X_W2,X_W2 | B | SETTLED +1.60 |
| LLENGERMATCH-26JUL06MATPUT | WTA_CHALL | E3a | 2 | MAT 9.0+PUT 88.0 | 97.0 | ≤97 | 3,2 | W2_ONLY,W2_ONLY | X_W2,X_W2 | B | SETTLED +0.65 |
| LLENGERMATCH-26JUL06MONPOP | WTA_CHALL | E3a | 2 | MON 43.0+POP 54.0 | 97.0 | ≤97 | 2,3 | W2_ONLY,W2_ONLY | X_CORRIDOR,X_W2 | B | SETTLED +3.85 |
| LLENGERMATCH-26JUL06NOHBUR | WTA_CHALL | E3a | 2 | BUR 22.0+NOH 75.0 | 97.0 | ≤97 | 2,2 | no-clock,no-clock | X_CORRIDOR,RODE | B | SETTLED -3.45 |
| LLENGERMATCH-26JUL06OLIUCH | WTA_CHALL | E3a | 2 | OLI 58.0+UCH 39.0 | 97.0 | ≤97 | 1,2 | W2_ONLY,W2_ONLY | X_W2,X_W2 | B | SETTLED +4.05 |
| LLENGERMATCH-26JUL06ROMSEM | WTA_CHALL | E3a | 1 | SEM 57.0 | — | — | 4 | no-clock | X_W2 | D | SETTLED +0.65 |
| LLENGERMATCH-26JUL06WALKAW | WTA_CHALL | E3a | 2 | KAW 43.0+WAL 54.0 | 97.0 | ≤97 | 3,2 | W2_ONLY,W2_ONLY | X_W2,X_W2 | B | SETTLED +1.00 |
| LLENGERMATCH-26JUL06WERSAL | WTA_CHALL | E3a | 2 | SAL 65.0+WER 32.0 | 97.0 | ≤97 | 1,4 | W2_ONLY,W2_ONLY | RODE,X_W2 | B | SETTLED -2.90 |
| WTAMATCH-26JUL06BOUMER | WTA_MAIN | E3a | 2 | BOU 46.5+MER 50.0 | 96.5 | ≤97 | 4,-5 | W2_ONLY,W2_ONLY | X_W2,X_W2 | B | SETTLED -1.36 |
| WTAMATCH-26JUL06KEYNOS | WTA_MAIN | E3a | 2 | KEY 54.0+NOS 43.0 | 97.0 | ≤97 | -4,3 | W2_ONLY,W2_ONLY | RODE,X_W2 | B | SETTLED -2.38 |
| WTAMATCH-26JUL06KRUKOS | WTA_MAIN | E3a | 2 | KOS 66.0+KRU 31.0 | 97.0 | ≤97 | -5,1 | W2_ONLY,W2_ONLY | X_W2,X_W2 | B | SETTLED +1.16 |
| WTAMATCH-26JUL06PAOEAL | WTA_MAIN | E3a | 2 | EAL 58.0+PAO 39.0 | 97.0 | ≤97 | -2,2 | W2_ONLY,W2_ONLY | RODE,X_W2 | B | SETTLED -5.58 |

## 6 · KALSHI UI RECONCILE — the book tied to the account, to the penny

Account NOW (REST, 2026-07-06 16:47:50 ET): cash **$871.14** (UI $871.13 ✓), positions mark **$39.00** (UI $39.35 — intra-minute bid-mark drift, named). Window: 07-05 16:30 ET → now (the UI's 24h reference; UI Δ = +$1.00).

| bucket | $ |
|---|---|
| (a) bot flows in-window — settled −19.65 + open-book costs/partials (cash view) | -38.21 |
| (b) pre-boot slate tail (Jul-5 positions settling in-window; 25 settlements) | +7.40 |
| (c) manual/non-MATCH tickers (one line, never blended) | +1.12 |
| (d) open positions value NOW at the ACCOUNT'S OWN mark (portfolio_value; my yes_bid mark reads 38.20 — the 0.80 mark-convention gap is named here, not absorbed) | +39.00 |
| (e) NAMED RESIDUAL: positions value at window START (no historical snapshot exists; = window-start holdings, the Jul-5 tail pre-settlement; cross-check 11:13 snapshot portfolio $96.10 mid-window) | −8.31 |
| **Σ (must equal UI +$1.00)** | **+1.00** |

Decomposition identity: ΔAccount = in-window cash flows + (positions_now − positions_start). All flows exchange-truth; fees inside each bucket. UI 'unrealized −$0.65' is the UI's own avg-cost basis vs its display mark — this book marks at live yes_bid (bot +0.20, manual −1.95 vs cost), convention difference named.

## 7 · GOLD-CLASS CENSUS — the winners' anatomy (findings only; any build goes through prior-art + Plex)

Population: **116 GOLD legs** (filled in W1, cashed in W1/CORRIDOR — the A-legs + the B1 wing) vs **76 RODE legs** (the −$193 wing). Measured distributions side by side (med [p25–p75]); raw legs in slate_ledger json + ui_gold json.

| metric | GOLD | RODE |
|---|---|---|
| fill − own W1 sell-flow dip ¢ | 0.0 [-0.5–0.5] | 0.0 [-1.0–0.0] |
| Δaim ¢ | 6 [3–13] | 4 [2–9] |
| event combined ¢ | 97.0 [95.5–97.0] | 97.0 [97.0–97.0] |
| conception→fill min | 241.5 [152.2–260.9] | 247.4 [151.3–306.4] |
| fill→band-touch min | 16.5 [5.6–47.0] | 1.6 [1.3–1.6] |
| band distance at fill ¢ | 8.0 [7.0–14.0] | 8.0 [6.0–16.0] |
| category mix | {'ATP_CHALL': 22, 'ITF_M': 37, 'ITF_W': 53, 'WTA_CHALL': 4} | {'ATP_CHALL': 20, 'ATP_MAIN': 1, 'ITF_M': 19, 'ITF_W': 27, 'WTA_CHALL': 7, 'WTA_MAIN': 2} |
| price-bucket mix (20¢ bands 0-4) | {0: 16, 1: 43, 2: 34, 3: 20, 4: 3} | {0: 14, 1: 19, 2: 21, 3: 18, 4: 4} |
| sibling disposition mix | {'EXIT_FILLED_CORRIDOR': 41, 'RODE_TO_SETTLEMENT': 22, 'EXIT_FILLED_W2': 38, '—': 8, 'EXIT_FILLED_W1': 7} | {'EXIT_FILLED_CORRIDOR': 21, '—': 26, 'EXIT_FILLED_W2': 25, 'EXIT_FILLED_W1': 2, 'RODE_TO_SETTLEMENT': 2} |
| sibling fill Δt min (sib − leg) | 3.4 [-6.8–22.9] | -4.3 [-82.9–2.4] |

Commonality read (measured, not theory): the columns state what GOLD shares that RODE lacks — the deltas in band-distance, fill-vs-dip, time-to-touch and sibling behavior above are the replication recipe's raw material.

## 8 · CONFIG ECHO + HEAD (self-dating)

```
riser_post_revision = False
walk_cap_honest_anchor = None
aim_zscore_shadow = None
scale_gun_shadow = True
per_match_clock = True
per_match_clock_shadow = True
premarket_walk_cap = True
leg2_reshuffle = True
reaim_on_sibling_arrival = True
repost_sibling_on_boot = True
paired_cap_enforced = False
join_trial_mode = True
57639
ecc287a live-monitor cycle 53: +42 lines
Tue Jul  7 00:19:36 EDT 2026
```
Generated 2026-07-07 00:18:15 ET. This file is THE book — the monitor and every future roll append to or cut from it.
---
# CUT — 2026-07-07 00:18 ET (appended; the book above refreshed in place at the same read)

**Continuity: the 16:28 book REPRODUCES EXACTLY as a timestamp cut — CUT C (16:28) = −19.65 over 197, target −19.65/197.** Chain now: A (named-divergence, convention retired) · B (set-proven) · C (exact).

## THE E4 COHORT (post-disarm + guards + true-basis; conception ≥ 15:25:58)
- **89 engaged · 4 settled (+$1.80 — LUCK-FLAGGED, n≪30) · mechanism columns first:**
- **Combined distribution, 15 completed E4 pairs (exchange VWAP): 86.0, 93.5, 94.5, 94.6, 95.0, 96.0, 96.0, 96.0, 96.5, 97.0, 97.0, 97.0, 97.0, 97.0, 97.0 — every pair ≤97, NINE under 97.** E3a completed AT the wall (med 97.0, 137/148 ≤97); **E4 completes UNDER it (med 96.0)** — the first cohort-level mechanism shift of the fix stack.
- The monitor's three claims CONFIRMED off fills, not log: **TAGSUZ 86.0** (SUZ 21¢×10 + TAG 65¢×5; monitor's 85 = VWAP rounding on the 10-lot) · **CHOPHA 95.0 exact (SETTLED)** · **PHATOM 96.0 exact** (both still open at read).
- Gold/B3/rode rates E4-vs-E3a: **not computable honestly at n=4 settled** — dispositions so far 1× EXIT_FILLED_W1 + 5× W2, zero rode; stated, not celebrated. The overnight settlements will populate this row at the next cut.
- Live E4 book: 85 open events inside the 98-open/180-resting overnight slate.

## ACCOUNT SNAPSHOT — BANKED (the §6 residual-killer)
**2026-07-07 00:18:15 ET: cash $847.74 · positions (account mark) $75.93.** Every future 24h reconcile decomposes against THIS line instead of a named unknown — the window-start residual class is dead from here forward.

One ledger line at this cut: **settled −$15.05 (205) · open basis $60.11 (98 events) · open mark $55.20.**
