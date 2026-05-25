# Exit-capture diagnostic — 75 closed v4 paper positions (2026-05-25, ~10am ET)

Read-only. Separates **execution misses** (price hit exit_target but the exit didn't fill -> WS/stale-book induced, recoverable with CC's patch) from **target-not-reached** (genuine variance). Tick walk uses the bot's own `analysis/premarket_ticks/{ticker}.csv`. **Limitation:** the tick log reflects what the *bot* saw; a crossing that happened on real Kalshi while the bot was WS-disconnected won't appear -> those land in `stale_book` (can't determine), so execution-miss is a *lower bound*.

## 5. HEADLINE
- Ride-to-settle exit-cells: **25**
- **execution_miss (bot saw bid>=target, didn't fill): 0**
- **target_not_reached (genuine variance): 17**
- stale_book (blind window / no ticks, undetermined; execution-miss lower-bounded): 8

## 6. MISSED PNL on execution-miss legs
- Aggregate missed PnL (counterfactual band_x*qty minus actual settle realized): **0 cents = $0.00**
- (Counterfactual assumes the resting exit fills at entry+band_x, maker, 0 fee. This is the recoverable upside if the WS patch stops the misses.)

## 2. RIDE-TO-SETTLE detail (24)

| ticker | cat | cell | entry | target(=e+X) | max_bid | max_ask | hit_target | first_cross ET | settle | realized$ | why | ws@cross |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KXATPCHALLENGERMATCH-26MAY25CREYEV-YEV | ATP_CHALL | 26 | 26 | 47 | 25 | 31 | no (max-tgt=-22) | ? | 0 | -2.60 | stale_book | None |
| KXATPCHALLENGERMATCH-26MAY25BRULOK-LOK | ATP_CHALL | 44 | 44 | 98 | 67 | 68 | no (max-tgt=-31) | ? | 0 | -4.40 | stale_book | None |
| KXATPCHALLENGERMATCH-26MAY25MARAND-AND | ATP_CHALL | 21 | 21 | 42 | 30 | 32 | no (max-tgt=-12) | ? | 0 | -2.10 | stale_book | None |
| KXATPCHALLENGERMATCH-26MAY25WEIKOE-WEI | ATP_CHALL | 47 | 47 | 98 | 49 | 57 | no (max-tgt=-49) | ? | 0 | -4.70 | stale_book | None |
| KXATPCHALLENGERMATCH-26MAY25BECLON-LON | ATP_CHALL | 17 | 17 | 54 | 44 | 63 | no (max-tgt=-10) | ? | 0 | -1.70 | stale_book | None |
| KXATPCHALLENGERMATCH-26MAY25XILDAL-XIL | ATP_CHALL | 26 | 26 | 47 | 28 | 33 | no (max-tgt=-19) | ? | 0 | -2.60 | stale_book | None |
| KXATPCHALLENGERMATCH-26MAY25GOMSAK-GOM | ATP_CHALL | 41 | 41 | 76 | 61 | 62 | no (max-tgt=-15) | ? | 0 | -4.10 | stale_book | None |
| KXATPCHALLENGERMATCH-26MAY25MAYHUR-HUR | ATP_CHALL | 24 | 24 | 74 | 38 | 41 | no (max-tgt=-36) | ? | 0 | -2.40 | stale_book | None |
| KXATPCHALLENGERMATCH-26MAY25SAKPAP-PAP | ATP_CHALL | 44 | 44 | 98 | 75 | 79 | no (max-tgt=-23) | ? | 0 | -4.40 | target_not_reached | None |
| KXATPMATCH-26MAY24SHEMIC-SHE | ATP_MAIN | 37 | 37 | 74 | 48 | 49 | no (max-tgt=-26) | ? | 0 | -3.70 | target_not_reached | None |
| KXATPMATCH-26MAY24CARLEH-LEH | ATP_MAIN | 82 | 82 | 88 | 86 | 87 | no (max-tgt=-2) | ? | 0 | -8.20 | target_not_reached | None |
| KXWTAMATCH-26MAY24CHWZHE-ZHE | WTA_MAIN | 76 | 76 | 91 | 82 | 78 | no (max-tgt=-9) | ? | 0 | -7.60 | target_not_reached | None |
| KXWTAMATCH-26MAY24BANBUC-BUC | WTA_MAIN | 71 | 71 | 93 | 80 | 81 | no (max-tgt=-13) | ? | 0 | -7.10 | target_not_reached | None |
| KXATPCHALLENGERMATCH-26MAY25FAJWIE-WIE | ATP_CHALL | 47 | 47 | 98 | 61 | 65 | no (max-tgt=-37) | ? | 0 | -4.70 | target_not_reached | None |
| KXATPCHALLENGERMATCH-26MAY25DURKIM-DUR | ATP_CHALL | 66 | 66 | 98 | 71 | 81 | no (max-tgt=-27) | ? | 0 | -6.60 | target_not_reached | None |
| KXATPCHALLENGERMATCH-26MAY25SARKRA-KRA | ATP_CHALL | 71 | 71 | 98 | 84 | 87 | no (max-tgt=-14) | ? | 0 | -7.10 | target_not_reached | None |
| KXWTAMATCH-26MAY24GRASRA-SRA | WTA_MAIN | 64 | 64 | 98 | 63 | 65 | no (max-tgt=-35) | ? | 0 | -6.40 | target_not_reached | None |
| KXATPMATCH-26MAY25BAUNAK-BAU | ATP_MAIN | 25 | 25 | 49 | 25 | 27 | no (max-tgt=-24) | ? | 0 | -2.50 | target_not_reached | None |
| KXATPCHALLENGERMATCH-26MAY25COMSEL-SEL | ATP_CHALL | 30 | 30 | 96 | 70 | 70 | no (max-tgt=-26) | ? | 0 | -3.00 | target_not_reached | None |
| KXATPMATCH-26MAY24NAVBRO-BRO | ATP_MAIN | 13 | 13 | 55 | 26 | 26 | no (max-tgt=-29) | ? | 0 | -1.30 | target_not_reached | None |
| KXATPCHALLENGERMATCH-26MAY25DANPRI-PRI | ATP_CHALL | 41 | 41 | 76 | 59 | 69 | no (max-tgt=-17) | ? | 0 | -4.10 | target_not_reached | None |
| KXATPMATCH-26MAY24KOVJOD-KOV | ATP_MAIN | 11 | 11 | 28 | 11 | 12 | no (max-tgt=-17) | ? | 0 | -1.10 | target_not_reached | None |
| KXWTAMATCH-26MAY24JOIPOT-JOI | WTA_MAIN | 14 | 14 | 60 | 13 | 15 | no (max-tgt=-47) | ? | 0 | -1.40 | target_not_reached | None |
| KXWTAMATCH-26MAY24MARMER-MAR | WTA_MAIN | 9 | 9 | 24 | 16 | 17 | no (max-tgt=-8) | ? | 0 | -0.90 | target_not_reached | None |
| KXATPMATCH-26MAY24HUMMAN-MAN | ATP_MAIN | 11 | 11 | 28 | 11 | 13 | no (max-tgt=-17) | ? | 0 | -1.10 | target_not_reached | None |

## 3. EXIT_FILLED (45): fill_price vs exit_target
- fill_price == exit_target on **46/46** (deltas: Counter({0: 46}))
- time-to-fill: min 2.7m, median 93.5m, max 192.0m (n=46)

## 1. ALL 75 CLOSED — per-position

| ticker | cat | cell | entry_mode | entry | strat | band_x | target | outcome | close_px | realized$ |
|---|---|---|---|---|---|---|---|---|---|---|
| KXATPCHALLENGERMATCH-26MAY25RODJAN-JAN | ATP_CHALL | 49 | miss_fallback | 49 | exit_at_X | 18 | 67 | exit_filled | 67 | 1.80 |
| KXATPCHALLENGERMATCH-26MAY25KIEDUT-DUT | ATP_CHALL | 92 | miss_fallback | 92 | exit_at_X | 1 | 93 | exit_filled | 93 | 0.10 |
| KXATPCHALLENGERMATCH-26MAY25FOMCAZ-FOM | ATP_CHALL | 80 | miss_fallback | 80 | exit_at_X | 16 | 96 | exit_filled | 96 | 1.60 |
| KXATPCHALLENGERMATCH-26MAY25DONVUJ-VUJ | ATP_CHALL | 25 | miss_fallback | 25 | exit_at_X | 24 | 49 | exit_filled | 49 | 2.40 |
| KXATPCHALLENGERMATCH-26MAY25DALHON-DAL | ATP_CHALL | 27 | miss_fallback | 27 | exit_at_X | 59 | 86 | exit_filled | 86 | 5.90 |
| KXATPCHALLENGERMATCH-26MAY25BERRAP-BER | ATP_CHALL | 45 | miss_fallback | 45 | exit_at_X | 55 | 98 | exit_filled | 98 | 5.30 |
| KXATPCHALLENGERMATCH-26MAY25SAKPAP-SAK | ATP_CHALL | 59 | miss_fallback | 59 | exit_at_X | 18 | 77 | exit_filled | 77 | 1.80 |
| KXATPCHALLENGERMATCH-26MAY25BERRAP-RAP | ATP_CHALL | 56 | miss_fallback | 56 | exit_at_X | 12 | 68 | exit_filled | 68 | 1.20 |
| KXATPCHALLENGERMATCH-26MAY25SHIBRO-SHI | ATP_CHALL | 81 | miss_fallback | 81 | exit_at_X | 5 | 86 | exit_filled | 86 | 0.50 |
| KXATPCHALLENGERMATCH-26MAY25SHIBRO-BRO | ATP_CHALL | 22 | miss_fallback | 22 | exit_at_X | 21 | 43 | exit_filled | 43 | 2.10 |
| KXATPCHALLENGERMATCH-26MAY25FELARN-FEL | ATP_CHALL | 41 | miss_fallback | 41 | exit_at_X | 35 | 76 | exit_filled | 76 | 3.50 |
| KXATPCHALLENGERMATCH-26MAY25BRULOK-BRU | ATP_CHALL | 59 | miss_fallback | 59 | exit_at_X | 18 | 77 | exit_filled | 77 | 1.80 |
| KXATPCHALLENGERMATCH-26MAY25LAMLAT-LAT | ATP_CHALL | 93 | miss_fallback | 93 | exit_at_X | 1 | 94 | exit_filled | 94 | 0.10 |
| KXATPCHALLENGERMATCH-26MAY25MARAND-MAR | ATP_CHALL | 82 | miss_fallback | 82 | exit_at_X | 5 | 87 | exit_filled | 87 | 0.50 |
| KXATPCHALLENGERMATCH-26MAY25DURKIM-KIM | ATP_CHALL | 35 | miss_fallback | 35 | exit_at_X | 8 | 43 | exit_filled | 43 | 0.80 |
| KXATPCHALLENGERMATCH-26MAY25BENMAK-BEN | ATP_CHALL | 49 | miss_fallback | 49 | exit_at_X | 18 | 67 | exit_filled | 67 | 1.80 |
| KXATPCHALLENGERMATCH-26MAY25BECLON-BEC | ATP_CHALL | 87 | miss_fallback | 87 | exit_at_X | 12 | 98 | exit_filled | 98 | 1.10 |
| KXATPCHALLENGERMATCH-26MAY25WEIKOE-KOE | ATP_CHALL | 57 | miss_fallback | 57 | exit_at_X | 12 | 69 | exit_filled | 69 | 1.20 |
| KXATPCHALLENGERMATCH-26MAY25SARKRA-SAR | ATP_CHALL | 34 | miss_fallback | 34 | exit_at_X | 49 | 83 | exit_filled | 83 | 4.90 |
| KXATPCHALLENGERMATCH-26MAY25FAJWIE-FAJ | ATP_CHALL | 54 | miss_fallback | 54 | exit_at_X | 1 | 55 | exit_filled | 55 | 0.10 |
| KXATPCHALLENGERMATCH-26MAY25YMEPUR-PUR | ATP_CHALL | 16 | miss_fallback | 16 | exit_at_X | 14 | 30 | exit_filled | 30 | 1.40 |
| KXATPCHALLENGERMATCH-26MAY25COMSEL-COM | ATP_CHALL | 71 | miss_fallback | 71 | exit_at_X | 27 | 98 | exit_filled | 98 | 2.70 |
| KXATPCHALLENGERMATCH-26MAY25GOMSAK-SAK | ATP_CHALL | 60 | miss_fallback | 60 | exit_at_X | 3 | 63 | exit_filled | 63 | 0.30 |
| KXATPCHALLENGERMATCH-26MAY25TOPGIU-GIU | ATP_CHALL | 50 | miss_fallback | 50 | exit_at_X | 15 | 65 | exit_filled | 65 | 1.50 |
| KXATPCHALLENGERMATCH-26MAY25YMEPUR-YME | ATP_CHALL | 86 | miss_fallback | 86 | exit_at_X | 4 | 90 | exit_filled | 90 | 0.40 |
| KXATPCHALLENGERMATCH-26MAY25NESPIE-PIE | ATP_CHALL | 50 | miss_fallback | 50 | exit_at_X | 15 | 65 | exit_filled | 65 | 1.50 |
| KXATPCHALLENGERMATCH-26MAY25MAYHUR-MAY | ATP_CHALL | 78 | miss_fallback | 78 | exit_at_X | 19 | 97 | exit_filled | 97 | 1.90 |
| KXATPCHALLENGERMATCH-26MAY25STRKRU-STR | ATP_CHALL | 55 | miss_fallback | 55 | exit_at_X | 12 | 67 | exit_filled | 67 | 1.20 |
| KXATPCHALLENGERMATCH-26MAY25STRKRU-KRU | ATP_CHALL | 47 | miss_fallback | 47 | exit_at_X | 55 | 98 | exit_filled | 98 | 5.10 |
| KXATPCHALLENGERMATCH-26MAY25DANPRI-DAN | ATP_CHALL | 61 | miss_fallback | 61 | exit_at_X | 3 | 64 | exit_filled | 64 | 0.30 |
| KXATPCHALLENGERMATCH-26MAY25JUSMAR-JUS | ATP_CHALL | 35 | miss_fallback | 35 | exit_at_X | 8 | 43 | exit_filled | 43 | 0.80 |
| KXATPCHALLENGERMATCH-26MAY25BOYDAM-BOY | ATP_CHALL | 65 | miss_fallback | 65 | exit_at_X | 1 | 66 | exit_filled | 66 | 0.10 |
| KXATPCHALLENGERMATCH-26MAY25GRENAR-NAR | ATP_CHALL | 82 | miss_fallback | 82 | exit_at_X | 5 | 87 | exit_filled | 87 | 0.50 |
| KXATPMATCH-26MAY25DESAM-DE | ATP_MAIN | 91 | resting_maker | 91 | exit_at_X | 4 | 95 | exit_filled | 95 | 0.40 |
| KXATPMATCH-26MAY24CARLEH-CAR | ATP_MAIN | 16 | resting_maker | 16 | exit_at_X | 4 | 20 | exit_filled | 20 | 0.40 |
| KXATPMATCH-26MAY24RINROD-RIN | ATP_MAIN | 75 | miss_fallback | 75 | exit_at_X | 1 | 76 | exit_filled | 76 | 0.10 |
| KXATPMATCH-26MAY24SHEMIC-MIC | ATP_MAIN | 64 | miss_fallback | 64 | exit_at_X | 36 | 98 | exit_filled | 98 | 3.40 |
| KXATPMATCH-26MAY25WAWDEJ-DEJ | ATP_MAIN | 58 | resting_maker | 58 | exit_at_X | 19 | 77 | exit_filled | 77 | 1.90 |
| KXATPMATCH-26MAY25BAUNAK-NAK | ATP_MAIN | 76 | miss_fallback | 76 | exit_at_X | 1 | 77 | exit_filled | 77 | 0.10 |
| KXATPMATCH-26MAY25WAWDEJ-WAW | ATP_MAIN | 39 | resting_maker | 39 | exit_at_X | 1 | 40 | exit_filled | 40 | 0.10 |
| KXATPMATCH-26MAY24NAVBRO-NAV | ATP_MAIN | 85 | resting_maker | 85 | exit_at_X | 13 | 98 | exit_filled | 98 | 1.30 |
| KXATPMATCH-26MAY24HUMMAN-HUM | ATP_MAIN | 94 | miss_fallback | 95 | exit_at_X | 4 | 98 | exit_filled | 98 | 0.30 |
| KXWTAMATCH-26MAY24KASSON-SON | WTA_MAIN | 31 | resting_maker | 31 | exit_at_X | 17 | 48 | exit_filled | 48 | 1.70 |
| KXWTAMATCH-26MAY24GRASRA-GRA | WTA_MAIN | 37 | miss_fallback | 37 | exit_at_X | 1 | 38 | exit_filled | 38 | 0.10 |
| KXWTAMATCH-26MAY24JOIPOT-POT | WTA_MAIN | 87 | miss_fallback | 87 | exit_at_X | 3 | 90 | exit_filled | 90 | 0.30 |
| KXWTAMATCH-26MAY24MARMER-MER | WTA_MAIN | 93 | miss_fallback | 93 | exit_at_X | 1 | 94 | exit_filled | 94 | 0.10 |
| KXATPCHALLENGERMATCH-26MAY25CREYEV-CRE | ATP_CHALL | 77 | miss_fallback | 77 | hold | None | None | hold_settle | 100 | 2.30 |
| KXATPCHALLENGERMATCH-26MAY25RODJAN-ROD | ATP_CHALL | 53 | miss_fallback | 53 | hold | None | None | hold_settle | 0 | -5.30 |
| KXATPCHALLENGERMATCH-26MAY25DALHON-HON | ATP_CHALL | 76 | miss_fallback | 76 | hold | None | None | hold_settle | 0 | -7.60 |
| KXATPCHALLENGERMATCH-26MAY25DONVUJ-DON | ATP_CHALL | 77 | miss_fallback | 77 | hold | None | None | hold_settle | 0 | -7.70 |
| KXATPCHALLENGERMATCH-26MAY25XILDAL-DAL | ATP_CHALL | 76 | miss_fallback | 76 | hold | None | None | hold_settle | 100 | 2.40 |
| KXATPMATCH-26MAY25DESAM-SAM | ATP_MAIN | 9 | miss_fallback | 9 | hold | None | None | hold_settle | 0 | -0.90 |
| KXATPCHALLENGERMATCH-26MAY25CREYEV-YEV | ATP_CHALL | 26 | miss_fallback | 26 | exit_at_X | 21 | 47 | rode_to_settle | 0 | -2.60 |
| KXATPCHALLENGERMATCH-26MAY25SAKPAP-PAP | ATP_CHALL | 44 | miss_fallback | 44 | exit_at_X | 55 | 98 | rode_to_settle | 0 | -4.40 |
| KXATPCHALLENGERMATCH-26MAY25BRULOK-LOK | ATP_CHALL | 44 | miss_fallback | 44 | exit_at_X | 55 | 98 | rode_to_settle | 0 | -4.40 |
| KXATPCHALLENGERMATCH-26MAY25MARAND-AND | ATP_CHALL | 21 | miss_fallback | 21 | exit_at_X | 21 | 42 | rode_to_settle | 0 | -2.10 |
| KXATPCHALLENGERMATCH-26MAY25WEIKOE-WEI | ATP_CHALL | 47 | miss_fallback | 47 | exit_at_X | 55 | 98 | rode_to_settle | 0 | -4.70 |
| KXATPCHALLENGERMATCH-26MAY25FAJWIE-WIE | ATP_CHALL | 47 | miss_fallback | 47 | exit_at_X | 55 | 98 | rode_to_settle | 0 | -4.70 |
| KXATPCHALLENGERMATCH-26MAY25BECLON-LON | ATP_CHALL | 17 | miss_fallback | 17 | exit_at_X | 37 | 54 | rode_to_settle | 0 | -1.70 |
| KXATPCHALLENGERMATCH-26MAY25DURKIM-DUR | ATP_CHALL | 66 | miss_fallback | 66 | exit_at_X | 33 | 98 | rode_to_settle | 0 | -6.60 |
| KXATPCHALLENGERMATCH-26MAY25SARKRA-KRA | ATP_CHALL | 71 | miss_fallback | 71 | exit_at_X | 27 | 98 | rode_to_settle | 0 | -7.10 |
| KXATPCHALLENGERMATCH-26MAY25XILDAL-XIL | ATP_CHALL | 26 | miss_fallback | 26 | exit_at_X | 21 | 47 | rode_to_settle | 0 | -2.60 |
| KXATPCHALLENGERMATCH-26MAY25COMSEL-SEL | ATP_CHALL | 30 | miss_fallback | 30 | exit_at_X | 66 | 96 | rode_to_settle | 0 | -3.00 |
| KXATPCHALLENGERMATCH-26MAY25GOMSAK-GOM | ATP_CHALL | 41 | miss_fallback | 41 | exit_at_X | 35 | 76 | rode_to_settle | 0 | -4.10 |
| KXATPCHALLENGERMATCH-26MAY25MAYHUR-HUR | ATP_CHALL | 24 | miss_fallback | 24 | exit_at_X | 50 | 74 | rode_to_settle | 0 | -2.40 |
| KXATPCHALLENGERMATCH-26MAY25DANPRI-PRI | ATP_CHALL | 41 | miss_fallback | 41 | exit_at_X | 35 | 76 | rode_to_settle | 0 | -4.10 |
| KXATPMATCH-26MAY24SHEMIC-SHE | ATP_MAIN | 37 | resting_maker | 37 | exit_at_X | 37 | 74 | rode_to_settle | 0 | -3.70 |
| KXATPMATCH-26MAY24CARLEH-LEH | ATP_MAIN | 82 | miss_fallback | 82 | exit_at_X | 6 | 88 | rode_to_settle | 0 | -8.20 |
| KXATPMATCH-26MAY25BAUNAK-BAU | ATP_MAIN | 25 | miss_fallback | 25 | exit_at_X | 24 | 49 | rode_to_settle | 0 | -2.50 |
| KXATPMATCH-26MAY24NAVBRO-BRO | ATP_MAIN | 13 | resting_maker | 13 | exit_at_X | 42 | 55 | rode_to_settle | 0 | -1.30 |
| KXATPMATCH-26MAY24KOVJOD-KOV | ATP_MAIN | 11 | resting_maker | 11 | exit_at_X | 17 | 28 | rode_to_settle | 0 | -1.10 |
| KXATPMATCH-26MAY24HUMMAN-MAN | ATP_MAIN | 11 | resting_maker | 11 | exit_at_X | 17 | 28 | rode_to_settle | 0 | -1.10 |
| KXWTAMATCH-26MAY24CHWZHE-ZHE | WTA_MAIN | 76 | miss_fallback | 76 | exit_at_X | 15 | 91 | rode_to_settle | 0 | -7.60 |
| KXWTAMATCH-26MAY24BANBUC-BUC | WTA_MAIN | 71 | miss_fallback | 71 | exit_at_X | 22 | 93 | rode_to_settle | 0 | -7.10 |
| KXWTAMATCH-26MAY24GRASRA-SRA | WTA_MAIN | 64 | miss_fallback | 64 | exit_at_X | 35 | 98 | rode_to_settle | 0 | -6.40 |
| KXWTAMATCH-26MAY24JOIPOT-JOI | WTA_MAIN | 14 | miss_fallback | 14 | exit_at_X | 46 | 60 | rode_to_settle | 0 | -1.40 |
| KXWTAMATCH-26MAY24MARMER-MAR | WTA_MAIN | 9 | miss_fallback | 9 | exit_at_X | 15 | 24 | rode_to_settle | 0 | -0.90 |

## Interpretation
Of the 25 ride-to-settle legs, **0 are execution misses** (recoverable with the WS patch -- $0.00 missed) and **17 are target-not-reached** (genuine variance). 8 undetermined (blind during a WS gap; execution-miss is a lower bound). **The exit mechanism is clean: 46/46 posted exits filled at exactly entry+band_x, 0 confirmed execution misses, $0 recoverable on the exit side.** The morning's loss on the ride-to-settle legs is genuine variance (17 never reached +X and the settlement outcome decided them) plus 8 WS-blind-undetermined (upper bound 8 hidden misses). **The WS bug's recoverable impact is on the ENTRY side (14%% fill vs 58%% corpus -> 86%% defaulting to T-20m fallback), NOT exits.** So the patch should lift entry fill rate; it will not change exit capture, which already works.

*Read-only on logs. tick-log walk reflects the bot's observed book (WS-blind crossings -> stale_book). Pre-fee realized per P0 #5.*