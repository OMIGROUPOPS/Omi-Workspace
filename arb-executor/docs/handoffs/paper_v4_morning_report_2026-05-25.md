# live_v4 paper — morning PnL report (2026-05-25, ~10:00 ET)

RG Day 2; live_v4 paper running since 02:52 ET. **Read-only**, built from the structured JSONL log + `paper_state.json` + latest heartbeat. v4 positions isolated by v4-signature events (the old live_v3 FV-anchor shared the JSONL 02:52-04:59 and is excluded). **PnL is pre-fee in the bot's `realized_pnl_cents` (P0 #5: fee flagged not modeled); fees reported separately. WS churn (~43/h, CC patch pending) caused 5,314 stale-book skips degrading execution — caveat on all numbers.** All $ at 10ct sizing.

## 3. AGGREGATE PAPER PNL (authoritative, latest heartbeat 10:00 ET)
- **Realized PnL today: -5860 cents = $-58.60** (pre-fee)
- **Unrealized MtM (best_bid): -1510 cents = $-15.10**
- **Total fees (1c/ct on taker entries): 900 cents = $9.00**
- **NET (realized + MtM - fees): $-82.70**
- **Capital deployed today: $546.20** (105 v4 positions: 75 closed, 30 open)
- Heartbeat: 36 active positions, 44 resting orders. (Per-position realized sum cross-check: $-45.40 vs heartbeat $-58.60.)

## 4. PER-CATEGORY ROI vs corpus

| category | positions | realized $ | cap $ | observed ROI | corpus floor | v4 target |
|---|---|---|---|---|---|---|
| ATP_MAIN | 26 (14 closed) | -10.00 | 128.90 | -7.76% | +7.9% | +8.95% |
| WTA_MAIN | 16 (9 closed) | -21.20 | 85.60 | -24.77% | +9.84% | +10.89% |
| ATP_CHALL | 63 (52 closed) | -14.20 | 331.70 | -4.28% | +7.57% | +8.62% |
| WTA_CHALL | 0 (0 closed) | 0.00 | 0.00 | 0.00% | +14.52% | +15.57% |

**Today's blended (closed): $-45.40 on $546.20 cap = -8.31% vs corpus floor +8.70% / v4 target +9.75%.** Partial day, many open, pre-fee, WS-degraded.

## 5. ENTRY MODE DISTRIBUTION
- marketable_taker: 0 | resting(maker/filled): 15 | miss_fallback (t20m): 90 (total 105)
- **Observed fill rate (marketable+resting)/total = 14%** vs corpus v4 ~58%.
Per category:
  - ATP_MAIN: mkt=0 rest=12 miss=14
  - WTA_MAIN: mkt=0 rest=3 miss=13
  - ATP_CHALL: mkt=0 rest=0 miss=63
  - WTA_CHALL: mkt=0 rest=0 miss=0

## 6. EXIT OUTCOMES
- exit_filled: 45 (avg time-to-exit 95.0 min)
- settled (exit-cell, no exit fill -> settlement): 24
- **hold_settled (live hold cells that fired): 6**
  - `KXATPCHALLENGERMATCH-26MAY25CREYEV-CRE` cell 77 (r75_84) entry 77 settle 100 -> realized $2.30
  - `KXATPCHALLENGERMATCH-26MAY25RODJAN-ROD` cell 53 (r45_54) entry 53 settle 0 -> realized $-5.30
  - `KXATPCHALLENGERMATCH-26MAY25DALHON-HON` cell 76 (r75_84) entry 76 settle 0 -> realized $-7.60
  - `KXATPCHALLENGERMATCH-26MAY25DONVUJ-DON` cell 77 (r75_84) entry 77 settle 0 -> realized $-7.70
  - `KXATPMATCH-26MAY25DESAM-SAM` cell 9 (r05_14) entry 9 settle 0 -> realized $-0.90
  - `KXATPCHALLENGERMATCH-26MAY25XILDAL-DAL` cell 76 (r75_84) entry 76 settle 100 -> realized $2.40

## 7. TOP / BOTTOM 5 REALIZED
**Top 5 winners:**
- `KXATPCHALLENGERMATCH-26MAY25DALHON-DAL` ATP_CHALL cell 27 exit_at_X entry 27 exit 86 -> **$5.90**
- `KXATPCHALLENGERMATCH-26MAY25BERRAP-BER` ATP_CHALL cell 45 exit_at_X entry 45 exit 98 -> **$5.30**
- `KXATPCHALLENGERMATCH-26MAY25STRKRU-KRU` ATP_CHALL cell 47 exit_at_X entry 47 exit 98 -> **$5.10**
- `KXATPCHALLENGERMATCH-26MAY25SARKRA-SAR` ATP_CHALL cell 34 exit_at_X entry 34 exit 83 -> **$4.90**
- `KXATPCHALLENGERMATCH-26MAY25FELARN-FEL` ATP_CHALL cell 41 exit_at_X entry 41 exit 76 -> **$3.50**
**Bottom 5 losers:**
- `KXATPMATCH-26MAY24CARLEH-LEH` ATP_MAIN cell 82 exit_at_X entry 82 exit 0 -> **$-8.20**
- `KXATPCHALLENGERMATCH-26MAY25DONVUJ-DON` ATP_CHALL cell 77 hold entry 77 exit 0 -> **$-7.70**
- `KXWTAMATCH-26MAY24CHWZHE-ZHE` WTA_MAIN cell 76 exit_at_X entry 76 exit 0 -> **$-7.60**
- `KXATPCHALLENGERMATCH-26MAY25DALHON-HON` ATP_CHALL cell 76 hold entry 76 exit 0 -> **$-7.60**
- `KXATPCHALLENGERMATCH-26MAY25SARKRA-KRA` ATP_CHALL cell 71 exit_at_X entry 71 exit 0 -> **$-7.10**

## 1. REALIZED (closed positions today)

| ticker | cat | cell | regime | strategy | entry_mode | entry | ct | outcome | exit/settle | fee¢ | realized$ | close ET |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KXATPCHALLENGERMATCH-26MAY25KIEDUT-DUT | ATP_CHALL | 92 | r85_94 | exit_at_X | miss_fallback | 92 | 10 | exit_filled | 93 | 10 | 0.10 | 03:30:20 AM |
| KXATPCHALLENGERMATCH-26MAY25BERRAP-RAP | ATP_CHALL | 56 | r55_64 | exit_at_X | miss_fallback | 56 | 10 | exit_filled | 68 | 10 | 1.20 | 04:07:01 AM |
| KXATPCHALLENGERMATCH-26MAY25CREYEV-CRE | ATP_CHALL | 77 | r75_84 | hold | miss_fallback | 77 | 10 | hold_settled | 100 | 10 | 2.30 | 04:26:46 AM |
| KXATPCHALLENGERMATCH-26MAY25FOMCAZ-FOM | ATP_CHALL | 80 | r75_84 | exit_at_X | miss_fallback | 80 | 10 | exit_filled | 96 | 10 | 1.60 | 04:28:36 AM |
| KXATPCHALLENGERMATCH-26MAY25SHIBRO-SHI | ATP_CHALL | 81 | r75_84 | exit_at_X | miss_fallback | 81 | 10 | exit_filled | 86 | 10 | 0.50 | 04:28:44 AM |
| KXATPCHALLENGERMATCH-26MAY25CREYEV-YEV | ATP_CHALL | 26 | r25_34 | exit_at_X | miss_fallback | 26 | 10 | settled | 0 | 10 | -2.60 | 04:45:47 AM |
| KXATPCHALLENGERMATCH-26MAY25DONVUJ-VUJ | ATP_CHALL | 25 | r25_34 | exit_at_X | miss_fallback | 25 | 10 | exit_filled | 49 | 10 | 2.40 | 04:52:34 AM |
| KXATPCHALLENGERMATCH-26MAY25RODJAN-JAN | ATP_CHALL | 49 | r45_54 | exit_at_X | miss_fallback | 49 | 10 | exit_filled | 67 | 10 | 1.80 | 04:55:46 AM |
| KXATPMATCH-26MAY24RINROD-RIN | ATP_MAIN | 75 | r75_84 | exit_at_X | miss_fallback | 75 | 10 | exit_filled | 76 | 10 | 0.10 | 05:00:27 AM |
| KXWTAMATCH-26MAY24KASSON-SON | WTA_MAIN | 31 | r25_34 | exit_at_X | resting_maker | 31 | 10 | exit_filled | 48 | 0 | 1.70 | 05:22:32 AM |
| KXATPMATCH-26MAY24CARLEH-CAR | ATP_MAIN | 16 | r15_24 | exit_at_X | resting_maker | 16 | 10 | exit_filled | 20 | 0 | 0.40 | 05:26:41 AM |
| KXATPMATCH-26MAY25DESAM-DE | ATP_MAIN | 91 | r85_94 | exit_at_X | resting_maker | 91 | 10 | exit_filled | 95 | 0 | 0.40 | 05:33:32 AM |
| KXATPCHALLENGERMATCH-26MAY25MARAND-MAR | ATP_CHALL | 82 | r75_84 | exit_at_X | miss_fallback | 82 | 10 | exit_filled | 87 | 10 | 0.50 | 05:43:27 AM |
| KXATPCHALLENGERMATCH-26MAY25SAKPAP-SAK | ATP_CHALL | 59 | r55_64 | exit_at_X | miss_fallback | 59 | 10 | exit_filled | 77 | 10 | 1.80 | 05:48:16 AM |
| KXATPCHALLENGERMATCH-26MAY25SAKPAP-PAP | ATP_CHALL | 44 | r35_44 | exit_at_X | miss_fallback | 44 | 10 | settled | 0 | 10 | -4.40 | 06:00:27 AM |
| KXATPCHALLENGERMATCH-26MAY25MARAND-AND | ATP_CHALL | 21 | r15_24 | exit_at_X | miss_fallback | 21 | 10 | settled | 0 | 10 | -2.10 | 06:11:25 AM |
| KXATPCHALLENGERMATCH-26MAY25BRULOK-BRU | ATP_CHALL | 59 | r55_64 | exit_at_X | miss_fallback | 59 | 10 | exit_filled | 77 | 10 | 1.80 | 06:11:50 AM |
| KXATPCHALLENGERMATCH-26MAY25BERRAP-BER | ATP_CHALL | 45 | r45_54 | exit_at_X | miss_fallback | 45 | 10 | exit_filled | 98 | 10 | 5.30 | 06:14:58 AM |
| KXATPCHALLENGERMATCH-26MAY25DALHON-DAL | ATP_CHALL | 27 | r25_34 | exit_at_X | miss_fallback | 27 | 10 | exit_filled | 86 | 10 | 5.90 | 06:18:12 AM |
| KXATPCHALLENGERMATCH-26MAY25FELARN-FEL | ATP_CHALL | 41 | r35_44 | exit_at_X | miss_fallback | 41 | 10 | exit_filled | 76 | 10 | 3.50 | 06:23:43 AM |
| KXATPCHALLENGERMATCH-26MAY25BENMAK-BEN | ATP_CHALL | 49 | r45_54 | exit_at_X | miss_fallback | 49 | 10 | exit_filled | 67 | 10 | 1.80 | 06:24:47 AM |
| KXATPCHALLENGERMATCH-26MAY25DALHON-HON | ATP_CHALL | 76 | r75_84 | hold | miss_fallback | 76 | 10 | hold_settled | 0 | 10 | -7.60 | 06:24:48 AM |
| KXATPCHALLENGERMATCH-26MAY25LAMLAT-LAT | ATP_CHALL | 93 | r85_94 | exit_at_X | miss_fallback | 93 | 10 | exit_filled | 94 | 10 | 0.10 | 06:25:20 AM |
| KXATPCHALLENGERMATCH-26MAY25SHIBRO-BRO | ATP_CHALL | 22 | r15_24 | exit_at_X | miss_fallback | 22 | 10 | exit_filled | 43 | 10 | 2.10 | 06:27:27 AM |
| KXATPMATCH-26MAY25DESAM-SAM | ATP_MAIN | 9 | r05_14 | hold | miss_fallback | 9 | 10 | hold_settled | 0 | 10 | -0.90 | 06:31:46 AM |
| KXATPMATCH-26MAY24SHEMIC-MIC | ATP_MAIN | 64 | r55_64 | exit_at_X | miss_fallback | 64 | 10 | exit_filled | 98 | 10 | 3.40 | 06:32:56 AM |
| KXATPMATCH-26MAY24SHEMIC-SHE | ATP_MAIN | 37 | r35_44 | exit_at_X | resting_maker | 37 | 10 | settled | 0 | 0 | -3.70 | 06:33:04 AM |
| KXWTAMATCH-26MAY24CHWZHE-ZHE | WTA_MAIN | 76 | r75_84 | exit_at_X | miss_fallback | 76 | 10 | settled | 0 | 10 | -7.60 | 06:34:31 AM |
| KXWTAMATCH-26MAY24GRASRA-GRA | WTA_MAIN | 37 | r35_44 | exit_at_X | miss_fallback | 37 | 10 | exit_filled | 38 | 10 | 0.10 | 06:37:20 AM |
| KXATPMATCH-26MAY25WAWDEJ-WAW | ATP_MAIN | 39 | r35_44 | exit_at_X | resting_maker | 39 | 10 | exit_filled | 40 | 0 | 0.10 | 06:37:46 AM |
| KXATPCHALLENGERMATCH-26MAY25RODJAN-ROD | ATP_CHALL | 53 | r45_54 | hold | miss_fallback | 53 | 10 | hold_settled | 0 | 10 | -5.30 | 06:44:49 AM |
| KXATPCHALLENGERMATCH-26MAY25DONVUJ-DON | ATP_CHALL | 77 | r75_84 | hold | miss_fallback | 77 | 10 | hold_settled | 0 | 10 | -7.70 | 06:51:26 AM |
| KXATPCHALLENGERMATCH-26MAY25BRULOK-LOK | ATP_CHALL | 44 | r35_44 | exit_at_X | miss_fallback | 44 | 10 | settled | 0 | 10 | -4.40 | 06:58:14 AM |
| KXATPCHALLENGERMATCH-26MAY25FAJWIE-FAJ | ATP_CHALL | 54 | r45_54 | exit_at_X | miss_fallback | 54 | 10 | exit_filled | 55 | 10 | 0.10 | 07:04:16 AM |
| KXATPMATCH-26MAY24CARLEH-LEH | ATP_MAIN | 82 | r75_84 | exit_at_X | miss_fallback | 82 | 10 | settled | 0 | 10 | -8.20 | 07:08:06 AM |
| KXATPCHALLENGERMATCH-26MAY25TOPGIU-GIU | ATP_CHALL | 50 | r45_54 | exit_at_X | miss_fallback | 50 | 10 | exit_filled | 65 | 10 | 1.50 | 07:10:28 AM |
| KXATPMATCH-26MAY25BAUNAK-NAK | ATP_MAIN | 76 | r75_84 | exit_at_X | miss_fallback | 76 | 10 | exit_filled | 77 | 10 | 0.10 | 07:14:50 AM |
| KXWTAMATCH-26MAY24BANBUC-BUC | WTA_MAIN | 71 | r65_74 | exit_at_X | miss_fallback | 71 | 10 | settled | 0 | 10 | -7.10 | 07:19:40 AM |
| KXATPCHALLENGERMATCH-26MAY25GOMSAK-SAK | ATP_CHALL | 60 | r55_64 | exit_at_X | miss_fallback | 60 | 10 | exit_filled | 63 | 10 | 0.30 | 07:25:39 AM |
| KXWTAMATCH-26MAY24MARMER-MER | WTA_MAIN | 93 | r85_94 | exit_at_X | miss_fallback | 93 | 10 | exit_filled | 94 | 10 | 0.10 | 07:25:55 AM |
| KXATPCHALLENGERMATCH-26MAY25DURKIM-KIM | ATP_CHALL | 35 | r35_44 | exit_at_X | miss_fallback | 35 | 10 | exit_filled | 43 | 10 | 0.80 | 07:26:11 AM |
| KXATPCHALLENGERMATCH-26MAY25YMEPUR-PUR | ATP_CHALL | 16 | r15_24 | exit_at_X | miss_fallback | 16 | 10 | exit_filled | 30 | 10 | 1.40 | 07:26:46 AM |
| KXATPCHALLENGERMATCH-26MAY25NESPIE-PIE | ATP_CHALL | 50 | r45_54 | exit_at_X | miss_fallback | 50 | 10 | exit_filled | 65 | 10 | 1.50 | 07:27:36 AM |
| KXATPCHALLENGERMATCH-26MAY25STRKRU-STR | ATP_CHALL | 55 | r55_64 | exit_at_X | miss_fallback | 55 | 10 | exit_filled | 67 | 10 | 1.20 | 07:31:17 AM |
| KXATPCHALLENGERMATCH-26MAY25WEIKOE-KOE | ATP_CHALL | 57 | r55_64 | exit_at_X | miss_fallback | 57 | 10 | exit_filled | 69 | 10 | 1.20 | 07:32:37 AM |
| KXATPMATCH-26MAY25WAWDEJ-DEJ | ATP_MAIN | 58 | r55_64 | exit_at_X | resting_maker | 58 | 10 | exit_filled | 77 | 0 | 1.90 | 07:36:16 AM |
| KXATPMATCH-26MAY24KOVJOD-KOV | ATP_MAIN | 11 | r05_14 | exit_at_X | resting_maker | 11 | 10 | settled | 0 | 0 | -1.10 | 07:36:24 AM |
| KXATPCHALLENGERMATCH-26MAY25BECLON-BEC | ATP_CHALL | 87 | r85_94 | exit_at_X | miss_fallback | 87 | 10 | exit_filled | 98 | 10 | 1.10 | 07:52:08 AM |
| KXWTAMATCH-26MAY24GRASRA-SRA | WTA_MAIN | 64 | r55_64 | exit_at_X | miss_fallback | 64 | 10 | settled | 0 | 10 | -6.40 | 07:58:41 AM |
| KXATPCHALLENGERMATCH-26MAY25SARKRA-SAR | ATP_CHALL | 34 | r25_34 | exit_at_X | miss_fallback | 34 | 10 | exit_filled | 83 | 10 | 4.90 | 07:59:59 AM |
| KXATPCHALLENGERMATCH-26MAY25FAJWIE-WIE | ATP_CHALL | 47 | r45_54 | exit_at_X | miss_fallback | 47 | 10 | settled | 0 | 10 | -4.70 | 08:02:49 AM |
| KXATPCHALLENGERMATCH-26MAY25YMEPUR-YME | ATP_CHALL | 86 | r85_94 | exit_at_X | miss_fallback | 86 | 10 | exit_filled | 90 | 10 | 0.40 | 08:10:34 AM |
| KXATPCHALLENGERMATCH-26MAY25XILDAL-XIL | ATP_CHALL | 26 | r25_34 | exit_at_X | miss_fallback | 26 | 10 | settled | 0 | 10 | -2.60 | 08:14:13 AM |
| KXATPCHALLENGERMATCH-26MAY25XILDAL-DAL | ATP_CHALL | 76 | r75_84 | hold | miss_fallback | 76 | 10 | hold_settled | 100 | 10 | 2.40 | 08:14:13 AM |
| KXATPCHALLENGERMATCH-26MAY25BOYDAM-BOY | ATP_CHALL | 65 | r65_74 | exit_at_X | miss_fallback | 65 | 10 | exit_filled | 66 | 10 | 0.10 | 08:20:33 AM |
| KXATPCHALLENGERMATCH-26MAY25DURKIM-DUR | ATP_CHALL | 66 | r65_74 | exit_at_X | miss_fallback | 66 | 10 | settled | 0 | 10 | -6.60 | 08:23:41 AM |
| KXWTAMATCH-26MAY24MARMER-MAR | WTA_MAIN | 9 | r05_14 | exit_at_X | miss_fallback | 9 | 10 | settled | 0 | 10 | -0.90 | 08:28:14 AM |
| KXATPCHALLENGERMATCH-26MAY25SARKRA-KRA | ATP_CHALL | 71 | r65_74 | exit_at_X | miss_fallback | 71 | 10 | settled | 0 | 10 | -7.10 | 08:30:38 AM |
| KXATPCHALLENGERMATCH-26MAY25WEIKOE-WEI | ATP_CHALL | 47 | r45_54 | exit_at_X | miss_fallback | 47 | 10 | settled | 0 | 10 | -4.70 | 08:38:41 AM |
| KXWTAMATCH-26MAY24JOIPOT-POT | WTA_MAIN | 87 | r85_94 | exit_at_X | miss_fallback | 87 | 10 | exit_filled | 90 | 10 | 0.30 | 08:44:56 AM |
| KXATPCHALLENGERMATCH-26MAY25GOMSAK-GOM | ATP_CHALL | 41 | r35_44 | exit_at_X | miss_fallback | 41 | 10 | settled | 0 | 10 | -4.10 | 08:45:27 AM |
| KXATPCHALLENGERMATCH-26MAY25DANPRI-DAN | ATP_CHALL | 61 | r55_64 | exit_at_X | miss_fallback | 61 | 10 | exit_filled | 64 | 10 | 0.30 | 08:55:34 AM |
| KXATPCHALLENGERMATCH-26MAY25COMSEL-COM | ATP_CHALL | 71 | r65_74 | exit_at_X | miss_fallback | 71 | 10 | exit_filled | 98 | 10 | 2.70 | 08:59:47 AM |
| KXATPCHALLENGERMATCH-26MAY25COMSEL-SEL | ATP_CHALL | 30 | r25_34 | exit_at_X | miss_fallback | 30 | 10 | settled | 0 | 10 | -3.00 | 09:00:01 AM |
| KXATPMATCH-26MAY25BAUNAK-BAU | ATP_MAIN | 25 | r25_34 | exit_at_X | miss_fallback | 25 | 10 | settled | 0 | 10 | -2.50 | 09:05:13 AM |
| KXATPCHALLENGERMATCH-26MAY25JUSMAR-JUS | ATP_CHALL | 35 | r35_44 | exit_at_X | miss_fallback | 35 | 10 | exit_filled | 43 | 10 | 0.80 | 09:10:24 AM |
| KXATPCHALLENGERMATCH-26MAY25STRKRU-KRU | ATP_CHALL | 47 | r45_54 | exit_at_X | miss_fallback | 47 | 10 | exit_filled | 98 | 10 | 5.10 | 09:16:29 AM |
| KXWTAMATCH-26MAY24JOIPOT-JOI | WTA_MAIN | 14 | r05_14 | exit_at_X | miss_fallback | 14 | 10 | settled | 0 | 10 | -1.40 | 09:18:08 AM |
| KXATPCHALLENGERMATCH-26MAY25BECLON-LON | ATP_CHALL | 17 | r15_24 | exit_at_X | miss_fallback | 17 | 10 | settled | 0 | 10 | -1.70 | 09:26:32 AM |
| KXATPMATCH-26MAY24NAVBRO-NAV | ATP_MAIN | 85 | r85_94 | exit_at_X | resting_maker | 85 | 10 | exit_filled | 98 | 0 | 1.30 | 09:36:47 AM |
| KXATPCHALLENGERMATCH-26MAY25DANPRI-PRI | ATP_CHALL | 41 | r35_44 | exit_at_X | miss_fallback | 41 | 10 | settled | 0 | 10 | -4.10 | 09:36:53 AM |
| KXATPMATCH-26MAY24NAVBRO-BRO | ATP_MAIN | 13 | r05_14 | exit_at_X | resting_maker | 13 | 10 | settled | 0 | 0 | -1.30 | 09:40:29 AM |
| KXATPCHALLENGERMATCH-26MAY25MAYHUR-MAY | ATP_CHALL | 78 | r75_84 | exit_at_X | miss_fallback | 78 | 10 | exit_filled | 97 | 10 | 1.90 | 09:54:25 AM |
| KXATPCHALLENGERMATCH-26MAY25GRENAR-NAR | ATP_CHALL | 82 | r75_84 | exit_at_X | miss_fallback | 82 | 10 | exit_filled | 87 | 10 | 0.50 | 09:56:32 AM |
| KXATPCHALLENGERMATCH-26MAY25MAYHUR-HUR | ATP_CHALL | 24 | r15_24 | exit_at_X | miss_fallback | 24 | 10 | settled | 0 | 10 | -2.40 | 09:56:33 AM |

## 2. STILL-OPEN positions

| ticker | cat | cell | regime | strategy | entry_mode | entry | net_qty | avg_entry |
|---|---|---|---|---|---|---|---|---|
| KXATPCHALLENGERMATCH-26MAY25CASPAN-CAS | ATP_CHALL | 49 | r45_54 | exit_at_X | miss_fallback | 49 | 10 | 49 |
| KXATPCHALLENGERMATCH-26MAY25JUSMAR-MAR | ATP_CHALL | 66 | r65_74 | exit_at_X | miss_fallback | 66 | 10 | 66 |
| KXATPCHALLENGERMATCH-26MAY25CASPAN-PAN | ATP_CHALL | 53 | r45_54 | hold | miss_fallback | 53 | 10 | 53 |
| KXATPCHALLENGERMATCH-26MAY25BOYDAM-DAM | ATP_CHALL | 36 | r35_44 | exit_at_X | miss_fallback | 36 | 10 | 36 |
| KXATPCHALLENGERMATCH-26MAY25GRENAR-GRE | ATP_CHALL | 20 | r15_24 | exit_at_X | miss_fallback | 20 | 10 | 20 |
| KXATPCHALLENGERMATCH-26MAY25ZAHHUS-HUS | ATP_CHALL | 64 | r55_64 | exit_at_X | miss_fallback | 64 | 10 | 64 |
| KXATPCHALLENGERMATCH-26MAY25ZAHHUS-ZAH | ATP_CHALL | 37 | r35_44 | exit_at_X | miss_fallback | 37 | 10 | 37 |
| KXATPCHALLENGERMATCH-26MAY25DEDBRA-DED | ATP_CHALL | 59 | r55_64 | exit_at_X | miss_fallback | 59 | 10 | 59 |
| KXATPCHALLENGERMATCH-26MAY25DEDBRA-BRA | ATP_CHALL | 43 | r35_44 | exit_at_X | miss_fallback | 43 | 10 | 43 |
| KXATPCHALLENGERMATCH-26MAY25POKPAR-POK | ATP_CHALL | 56 | r55_64 | exit_at_X | miss_fallback | 56 | 10 | 56 |
| KXATPCHALLENGERMATCH-26MAY25POKPAR-PAR | ATP_CHALL | 47 | r45_54 | exit_at_X | miss_fallback | 47 | 10 | 47 |
| KXATPMATCH-26MAY25VANKYP-KYP | ATP_MAIN | 49 | r45_54 | exit_at_X | miss_fallback | 49 | 10 | 49 |
| KXATPMATCH-26MAY24KOKATM-KOK | ATP_MAIN | 23 | r15_24 | exit_at_X | miss_fallback | 23 | 10 | 23 |
| KXATPMATCH-26MAY24KOKATM-ATM | ATP_MAIN | 79 | r75_84 | exit_at_X | miss_fallback | 79 | 10 | 79 |
| KXATPMATCH-26MAY24HIJPAU-HIJ | ATP_MAIN | 5 | r05_14 | exit_at_X | resting_maker | 5 | 10 | 5 |
| KXATPMATCH-26MAY24BUSRUB-BUS | ATP_MAIN | 35 | r35_44 | exit_at_X | resting_maker | 35 | 10 | 35 |
| KXATPMATCH-26MAY25NAVUGO-UGO | ATP_MAIN | 50 | r45_54 | hold | miss_fallback | 50 | 10 | 50 |
| KXATPMATCH-26MAY24BUSRUB-RUB | ATP_MAIN | 68 | r65_74 | exit_at_X | miss_fallback | 68 | 10 | 68 |
| KXATPMATCH-26MAY24HIJPAU-PAU | ATP_MAIN | 94 | r85_94 | exit_at_X | miss_fallback | 94 | 10 | 94 |
| KXATPMATCH-26MAY24HUMMAN-MAN | ATP_MAIN | 11 | r05_14 | exit_at_X | resting_maker | 11 | 10 | 11 |
| KXATPMATCH-26MAY25CERVAN-VAN | ATP_MAIN | 14 | r05_14 | exit_at_X | resting_maker | 14 | 10 | 14 |
| KXATPMATCH-26MAY24HUMMAN-HUM | ATP_MAIN | 94 | r85_94 | exit_at_X | miss_fallback | 95 | 10 | 95 |
| KXATPMATCH-26MAY25CERVAN-CER | ATP_MAIN | 85 | r85_94 | exit_at_X | miss_fallback | 85 | 10 | 85 |
| KXWTAMATCH-26MAY24URHBOU-URH | WTA_MAIN | 31 | r25_34 | exit_at_X | miss_fallback | 31 | 10 | 31 |
| KXWTAMATCH-26MAY24URHBOU-BOU | WTA_MAIN | 70 | r65_74 | exit_at_X | miss_fallback | 70 | 10 | 70 |
| KXWTAMATCH-26MAY24RAKANI-ANI | WTA_MAIN | 93 | r85_94 | exit_at_X | resting_maker | 93 | 10 | 93 |
| KXWTAMATCH-26MAY24GIBPUT-PUT | WTA_MAIN | 71 | r65_74 | exit_at_X | resting_maker | 71 | 10 | 71 |
| KXWTAMATCH-26MAY24GUOKES-GUO | WTA_MAIN | 30 | r25_34 | exit_at_X | miss_fallback | 30 | 10 | 30 |
| KXWTAMATCH-26MAY24RAKANI-RAK | WTA_MAIN | 8 | r05_14 | exit_at_X | miss_fallback | 8 | 10 | 8 |
| KXWTAMATCH-26MAY24GUOKES-KES | WTA_MAIN | 71 | r65_74 | exit_at_X | miss_fallback | 71 | 10 | 71 |

(Per-position best_bid MtM requires the live book; **aggregate unrealized MtM = $-15.10** from the bot's `_compute_mark_to_market_cents` in the 10:00 heartbeat is authoritative.)

---
*Read-only. Pre-fee realized per P0 #5. WS-churn caveat applies. Built from JSONL + paper_state.json + heartbeat; v4 positions isolated by v4-signature.*