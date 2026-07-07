# LIVE VALIDATION — rolling status

- cycle 124 @ **2026-07-07 12:34:43 PM ET** | build `a53a0c8` | session boot 07-07 10:21 ET | log `live_v3_20260707.jsonl` | 75843 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 10:38:44 | **grace_breach** | KXATPMATCH-26JUL07AUGDJO-DJO | fill 61c 5.7min past latch (grace 300s) |
| 10:38:44 | **combined_over_goal** | KXATPMATCH-26JUL07AUGDJO | pair combined 100c > goal 97c [complete_cross_insurance: cap102 by design (d?)] |
| 11:31:21 | **grace_breach** | KXWTAMATCH-26JUL07OSAMUC-OSA | fill 53c 62.6min past latch (grace 300s) |

## FILLS — 96 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10:21 | WTACHALLENGERMATCH-26JUL07ZANJAC-Z | WTA_CHALL | ? | 28 | 25 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | WTACHALLENGERMATCH-26JUL07ZANJAC-J | WTA_CHALL | ? | 69 | 66 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | ITFMATCH-26JUL07MOUMON-MOU | ITF_M | ? | 34 | 10 | +24 (window_cell) | — | pre | pair | 98 | MIXED |
| 10:21 | ATPCHALLENGERMATCH-26JUL07HAMWAL-H | ATP_CHALL | ? | 13 | 11 | +2 (window_cell) | — | pre | pair | 99 | MIXED |
| 10:21 | ITFWMATCH-26JUL07BUEXAV-XAV | ITF_W | ? | 68 | 73 | -5 (window_cell) | — | pre | single |  | MIXED |
| 10:21 | ATPCHALLENGERMATCH-26JUL07GASCHE-C | ATP_CHALL | ? | 24 | 21 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 10:21 | ITFWMATCH-26JUL07SIMROU-SIM | ITF_W | ? | 33 | 66 | -33 (window_cell) | -61.5 | pre | single |  | EARNED |
| 10:21 | ITFWMATCH-26JUL07KHRYOU-KHR | ITF_W | ? | 44 | 40 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | ITFWMATCH-26JUL07KHRYOU-YOU | ITF_W | ? | 53 | 51 | +2 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | ATPCHALLENGERMATCH-26JUL07WALVAL-W | ATP_CHALL | ? | 32 | 2 | +30 (window_cell) | — | pre | single |  | MIXED |
| 10:21 | ITFWMATCH-26JUL07GUESAN-SAN | ITF_W | ? | 8 | 4 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 10:21 | ITFMATCH-26JUL07URSPOU-POU | ITF_M | ? | 50 | 33 | +17 (window_cell) | -4.5 | pre | pair | 97 | EARNED |
| 10:21 | ITFWMATCH-26JUL07MALKOM-KOM | ITF_W | ? | 10 | 6 | +4 (adopted_est) | -9.0 | pre | single |  | EARNED |
| 10:21 | ITFWMATCH-26JUL07VRARUG-RUG | ITF_W | ? | 61 | 43 | +18 (window_cell) | 30.5 | pre | single |  | GIFT_CLASS |
| 10:23 | ATPCHALLENGERMATCH-26JUL07ZAHSEA-S | ATP_CHALL | ? | 82 | 79 | +3 (fill_est) | -2.5 | pre | single |  | MIXED |
| 10:23 | ITFWMATCH-26JUL07MELDIG-MEL | ITF_W | underdog | 4 | 2 | +2 (place_cell) | — | pre | pair | 95 | EARNED |
| 10:23 | ATPCHALLENGERMATCH-26JUL07GUEDON-D | ATP_CHALL | ? | 29 | 29 | +0 (window_cell) | — | pre | single |  | EARNED |
| 10:25 | WTACHALLENGERMATCH-26JUL07GALRIN-G | WTA_CHALL | ? | 63 | 60 | +3 (fill_est) | -7.5 | 0.8 | single |  | EARNED |
| 10:25 | ITFMATCH-26JUL07GAGMED-MED | ITF_M | ? | 10 | 6 | +4 (fill_est) | -5.5 | 1.1 | single |  | EARNED |
| 10:25 | ITFMATCH-26JUL07TSIHER-TSI | ITF_M | ? | 50 | 17 | +33 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 10:27 | ITFWMATCH-26JUL07MELROD-MEL | ITF_W | ? | 74 | 78 | -4 (window_cell) | — | pre | single |  | MIXED |
| 10:27 | ATPCHALLENGERMATCH-26JUL07BROWEH-W | ATP_CHALL | ? | 35 | 35 | +0 (window_cell) | -16.5 | pre | pair | 99 | EARNED |
| 10:28 | ITFMATCH-26JUL07URSPOU-URS | ITF_M | ? | 47 | 60 | -13 (window_cell) | 1.5 | pre | pair | 97 | EARNED |
| 10:29 | ITFWMATCH-26JUL07BROGAR-GAR | ITF_W | ? | 5 | 1 | +4 (window_cell) | — | pre | single |  | MIXED |
| 10:29 | ATPCHALLENGERMATCH-26JUL07RODAND-R | ATP_CHALL | ? | 39 | 36 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 10:31 | ITFWMATCH-26JUL07ARCOLI-OLI | ITF_W | ? | 72 | 92 | -20 (window_cell) | — | pre | pair | 93 | MIXED |
| 10:31 | ITFWMATCH-26JUL07MELDIG-DIG | ITF_W | ? | 91 | 75 | +16 (window_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 10:33 | ATPCHALLENGERMATCH-26JUL07POLHEI-H | ATP_CHALL | ? | 92 | 91 | +1 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 10:34 | ATPMATCH-26JUL07AUGDJO-AUG | ATP_MAIN | underdog | 39 | 37 | +2 (place_cell) | -0.5 | 1.7 | pair | 100 | MIXED |
| 10:37 | WTACHALLENGERMATCH-26JUL07SCOSTO-S | WTA_CHALL | leader | 82 | 79 | +3 (place_cell) | — | pre | single |  | PENDING |
| 10:38 | ATPMATCH-26JUL07AUGDJO-DJO | ATP_MAIN | leader | 61 | 60 | +1 (place_cell) | -0.5 | 5.7 | pair | 100 | MIXED |
| 10:40 | ITFMATCH-26JUL07MOUMON-MON | ITF_M | ? | 64 | 82 | -18 (window_cell) | — | pre | pair | 98 | MIXED |
| 10:40 | WTACHALLENGERMATCH-26JUL07ZAALEP-Z | WTA_CHALL | ? | 58 | 55 | +3 (window_cell) | — | pre | pair | 100 | GIFT_CLASS |
| 10:41 | ITFMATCH-26JUL07GREKAS-GRE | ITF_M | ? | 91 | 85 | +6 (window_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 10:44 | ITFMATCH-26JUL07GREKAS-KAS | ITF_M | ? | 8 | 6 | +2 (window_cell) | — | pre | pair | 99 | MIXED |
| 10:49 | ATPCHALLENGERMATCH-26JUL07BASGAU-B | ATP_CHALL | ? | 41 | 41 | +0 (window_cell) | 24.5 | pre | single |  | EARNED |
| 10:49 | ATPCHALLENGERMATCH-26JUL06MALMAT-M | ATP_CHALL | ? | 49 | 46 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 11:00 | ITFMATCH-26JUL07PUTVAS-PUT | ITF_M | ? | 5 | 1 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:00 | ITFMATCH-26JUL07MARBAS-BAS | ITF_M | ? | 46 | 42 | +4 (window_cell) | — | pre | single |  | MIXED |
| 11:00 | ITFWMATCH-26JUL07SCHCAN-SCH | ITF_W | ? | 12 | 8 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:00 | WTACHALLENGERMATCH-26JUL07SEBBRA-S | WTA_CHALL | ? | 48 | 45 | +3 (window_cell) | — | pre | single |  | MIXED |
| 11:02 | ITFMATCH-26JUL07SEGMIT-MIT | ITF_M | ? | 25 | 21 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:03 | ITFWMATCH-26JUL07ARCOLI-ARC | ITF_W | ? | 21 | 1 | +20 (window_cell) | — | pre | pair | 93 | MIXED |
| 11:03 | ITFMATCH-26JUL07ROLLAR-ROL | ITF_M | ? | 92 | 89 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 11:06 | ATPCHALLENGERMATCH-26JUL07PLAMAR-P | ATP_CHALL | ? | 34 | 36 | -2 (window_cell) | -32.0 | pre | single |  | EARNED |
| 11:08 | ITFMATCH-26JUL07DUSSHE-SHE | ITF_M | ? | 28 | 24 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:11 | ITFWMATCH-26JUL07EVAGOW-EVA | ITF_W | ? | 79 | 77 | +2 (adopted_est) | — | pre | pair | 93 | PENDING |
| 11:11 | ATPCHALLENGERMATCH-26JUL07CLAHER-H | ATP_CHALL | ? | 53 | 52 | +1 (window_cell) | — | pre | pair | 98 | GIFT_CLASS |
| 11:14 | ITFWMATCH-26JUL07EVAGOW-GOW | ITF_W | ? | 14 | 10 | +4 (adopted_est) | — | pre | pair | 93 | PENDING |
| 11:20 | ATPCHALLENGERMATCH-26JUL07BROWEH-B | ATP_CHALL | ? | 64 | 64 | +0 (window_cell) | 13.5 | pre | pair | 99 | GIFT_CLASS |
| 11:20 | ITFMATCH-26JUL07TISNAP-TIS | ITF_M | ? | 74 | 71 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 11:20 | ATPCHALLENGERMATCH-26JUL07CLAHER-C | ATP_CHALL | ? | 45 | 43 | +2 (window_cell) | — | pre | pair | 98 | MIXED |
| 11:20 | ATPCHALLENGERMATCH-26JUL07MARCRE-M | ATP_CHALL | ? | 29 | 29 | +0 (window_cell) | — | pre | single |  | EARNED |
| 11:24 | ATPCHALLENGERMATCH-26JUL07DROERH-E | ATP_CHALL | ? | 24 | 22 | +2 (window_cell) | 8.5 | pre | pair | 98 | GIFT_CLASS |
| 11:24 | WTACHALLENGERMATCH-26JUL07FITPIG-F | WTA_CHALL | ? | 31 | 29 | +2 (window_cell) | — | pre | pair | 98 | MIXED |
| 11:24 | ATPCHALLENGERMATCH-26JUL07MONSUM-M | ATP_CHALL | ? | 89 | 87 | +2 (window_cell) | -6.0 | pre | pair | 99 | EARNED |
| 11:24 | ATPCHALLENGERMATCH-26JUL07MONSUM-S | ATP_CHALL | ? | 10 | 8 | +2 (window_cell) | 3.0 | pre | pair | 99 | GIFT_CLASS |
| 11:25 | ITFWMATCH-26JUL07JOHKAJ-KAJ | ITF_W | ? | 48 | 44 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:28 | ATPCHALLENGERMATCH-26JUL07AZKBON-A | ATP_CHALL | ? | 33 | 32 | +1 (window_cell) | -1.0 | pre | pair | 98 | MIXED |
| 11:30 | ITFWMATCH-26JUL07SOTTEO-SOT | ITF_W | leader | 93 | 92 | +1 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 11:31 | ATPCHALLENGERMATCH-26JUL07OSOSOT-O | ATP_CHALL | ? | 20 | 21 | -1 (window_cell) | — | pre | single |  | EARNED |
| 11:31 | ATPCHALLENGERMATCH-26JUL07HERAMB-H | ATP_CHALL | ? | 7 | 7 | +0 (window_cell) | — | pre | single |  | EARNED |
| 11:31 | WTAMATCH-26JUL07OSAMUC-OSA | WTA_MAIN | ? | 53 | 53 | +0 (adopted_est) | — | 62.6 | single |  | PENDING |
| 11:33 | ITFMATCH-26JUL07BOUMOC-MOC | ITF_M | ? | 30 | 26 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:33 | ITFWMATCH-26JUL07MCNREE-REE | ITF_W | ? | 54 | 33 | +21 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 11:34 | ATPCHALLENGERMATCH-26JUL07AZKBON-B | ATP_CHALL | ? | 65 | 64 | +1 (window_cell) | 0.5 | pre | pair | 98 | GIFT_CLASS |
| 11:34 | WTACHALLENGERMATCH-26JUL07VICBRA-V | WTA_CHALL | underdog | 27 | 24 | +3 (place_cell) | — | pre | single |  | PENDING |
| 11:38 | WTACHALLENGERMATCH-26JUL07MARBUR-B | WTA_CHALL | ? | 31 | 29 | +2 (window_cell) | — | pre | pair | 99 | MIXED |
| 11:40 | ATPCHALLENGERMATCH-26JUL07MOESAN-M | ATP_CHALL | ? | 71 | 71 | +0 (window_cell) | 15.0 | pre | single |  | GIFT_CLASS |
| 11:40 | WTACHALLENGERMATCH-26JUL07MARBUR-M | WTA_CHALL | ? | 68 | 66 | +2 (window_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 11:40 | ITFWMATCH-26JUL07MULSIN-SIN | ITF_W | ? | 25 | 21 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:40 | ITFWMATCH-26JUL07SCHZID-ZID | ITF_W | ? | 70 | 68 | +2 (adopted_est) | — | pre | pair | 97 | PENDING |
| 11:46 | ITFMATCH-26JUL07BARCOT-COT | ITF_M | ? | 41 | 37 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 11:46 | ITFMATCH-26JUL07ROLLAR-LAR | ITF_M | ? | 5 | 1 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 11:48 | ATPCHALLENGERMATCH-26JUL07HERHAR-H | ATP_CHALL | ? | 80 | 77 | +3 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 11:48 | ITFWMATCH-26JUL07JAUMAT-JAU | ITF_W | ? | 46 | 58 | -12 (window_cell) | — | pre | single |  | EARNED |
| 11:50 | ITFWMATCH-26JUL07SCHZID-SCH | ITF_W | ? | 27 | 23 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 11:50 | ITFWMATCH-26JUL07MAROLU-OLU | ITF_W | ? | 30 | 26 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:52 | ITFWMATCH-26JUL07GIADIA-GIA | ITF_W | ? | 34 | 39 | -5 (window_cell) | — | pre | single |  | EARNED |
| 11:56 | ITFWMATCH-26JUL07SOTTEO-TEO | ITF_W | underdog | 2 | 5 | -3 (place_cell) | — | pre | pair | 95 | EARNED |
| 11:59 | ITFMATCH-26JUL07SCHJON-SCH | ITF_M | ? | 4 | 1 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 12:00 | ITFMATCH-26JUL07SELWAS-SEL | ITF_M | ? | 59 | 64 | -5 (window_cell) | — | pre | single |  | MIXED |
| 12:02 | ITFMATCH-26JUL07LERBRO-BRO | ITF_M | ? | 16 | 12 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:04 | WTACHALLENGERMATCH-26JUL07SHYKIN-S | WTA_CHALL | leader | 57 | 54 | +3 (place_cell) | — | pre | single |  | PENDING |
| 12:06 | ITFMATCH-26JUL07BARCOT-BAR | ITF_M | ? | 56 | 53 | +3 (fill_est) | — | pre | pair | 97 | PENDING |
| 12:15 | ATPCHALLENGERMATCH-26JUL07ONCCAM-C | ATP_CHALL | ? | 20 | 19 | +1 (window_cell) | — | pre | pair | 98 | MIXED |
| 12:18 | ATPCHALLENGERMATCH-26JUL07ONCCAM-O | ATP_CHALL | ? | 78 | 77 | +1 (window_cell) | — | pre | pair | 98 | GIFT_CLASS |
| 12:19 | ATPCHALLENGERMATCH-26JUL07HAMWAL-W | ATP_CHALL | ? | 86 | 84 | +2 (window_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 12:19 | ITFWMATCH-26JUL07PASLEE-PAS | ITF_W | ? | 54 | 52 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 12:19 | ITFWMATCH-26JUL07MOROLM-MOR | ITF_W | ? | 31 | 27 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:22 | ITFMATCH-26JUL07ESTBAS-BAS | ITF_M | underdog | 7 | 3 | +4 (place_cell) | — | pre | single |  | PENDING |
| 12:25 | ITFWMATCH-26JUL07ABASLA-SLA | ITF_W | ? | 51 | 79 | -28 (window_cell) | — | pre | single |  | MIXED |
| 12:25 | WTACHALLENGERMATCH-26JUL07ZAALEP-L | WTA_CHALL | ? | 42 | 40 | +2 (window_cell) | — | pre | pair | 100 | MIXED |
| 12:26 | WTACHALLENGERMATCH-26JUL07FITPIG-P | WTA_CHALL | ? | 67 | 67 | +0 (window_cell) | — | pre | pair | 98 | MIXED |
| 12:28 | ITFWMATCH-26JUL07CHAPER-CHA | ITF_W | ? | 51 | 49 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 12:33 | ATPCHALLENGERMATCH-26JUL07DROERH-D | ATP_CHALL | ? | 74 | 73 | +1 (window_cell) | — | pre | pair | 98 | GIFT_CLASS |

## RESTING BIDS — 46 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 16, 'FLOW_AT_LEVEL': 11, 'NO_FLOW': 19} | repriceable now: true 7 / false 39 | **cumulative bid_grade lines: 4862 (repriceable true 420 / false 4442)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07AZKBON-A | 32 | 58m | 134/19-70/21975 | 68-70 | -13 | **FLOW_AT_LEVEL** | 32 |  |
| ATPCHALLENGERMATCH-26JUL07BASGAU-G | 54 | 97m | 424/55-93/76897 | 73-74 | 1 | **FLOW_ABOVE** | 54 | flow above but bound 54c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07BROWEH-W | 33 | 68m | 114/1-50/10548 | 1-2 | -32 | **FLOW_AT_LEVEL** | 33 |  |
| ATPCHALLENGERMATCH-26JUL07CLAHER-C | 44 | 56m | 148/40-79/7392 | 76-77 | -4 | **FLOW_AT_LEVEL** | 43 |  |
| ATPCHALLENGERMATCH-26JUL07HERAMB-H | 1 | 55m | 253/1-28/34745 | 1-2 | 0 | **FLOW_AT_LEVEL** | 7 |  |
| ATPCHALLENGERMATCH-26JUL07KRUPIE-K | 60 | 107m | 452/56-98/61154 | 90-91 | -4 | **FLOW_AT_LEVEL** | 67 |  |
| ATPCHALLENGERMATCH-26JUL07MARBER-B | 58 | 127m | 961/21-99/118990 | 97-99 | -37 | **FLOW_AT_LEVEL** | 61 |  |
| ATPCHALLENGERMATCH-26JUL07MCCSAK-M | 27 | 54m | 0 | 27-28 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07MCCSAK-S | 71 | 54m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07MONSUM-S | 8 | 66m | 239/1-16/45870 | 1-2 | -7 | **FLOW_AT_LEVEL** | 8 |  |
| ATPCHALLENGERMATCH-26JUL07ONCCAM-C | 19 | 17m | 23/28-43/1828 | 35-40 | 9 | **FLOW_ABOVE** | 19 | flow above but bound 19c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07OSOSOT-O | 20 | 13m | 49/22-37/3381 | 32-31 | 2 | **FLOW_ABOVE** | 21 | REPRICEABLE→21 |
| ATPCHALLENGERMATCH-26JUL07PLAMAR-P | 34 | 84m | 153/32-99/10073 | 97-98 | -2 | **FLOW_AT_LEVEL** | 36 |  |
| ATPCHALLENGERMATCH-26JUL07POLHEI-P | 4 | 118m | 781/1-13/197045 | 1-2 | -3 | **FLOW_AT_LEVEL** | 4 |  |
| ATPCHALLENGERMATCH-26JUL07POPPDA-P | 57 | 107m | 2/58-58/126 | 57-58 | 1 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07POPPDA-P | 39 | 84m | 5/43-45/226 | 41-45 | 4 | **FLOW_ABOVE** | 42 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL07TOMSHI-T | 63 | 64m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07ARSWIL-ARS | 46 | 125m | 0 | 46-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07ARSWIL-WIL | 52 | 124m | 0 | 52-54 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07COLSHI-COL | 19 | 34m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07COLSHI-SHI | 79 | 17m | 0 | 79-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07ESTBAS-EST | 90 | 10m | 0 | 91-95 | — | **NO_FLOW** | 90 |  |
| ITFMATCH-26JUL07KLEHOH-HOH | 86 | 94m | 0 | 86-90 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07KLEHOH-KLE | 10 | 94m | 0 | 10-13 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07LERBRO-LER | 81 | 31m | 18/94-97/241 | 94-95 | 13 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07MOUMON-MOU | 31 | 95m | 163/4-38/6009 | 4-6 | -27 | **FLOW_AT_LEVEL** | 10 |  |
| ITFMATCH-26JUL07ROLLAR-ROL | 92 | 23m | 3/93-94/49 | 96-97 | 1 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07SELWAS-WAS | 33 | 32m | 87/58-70/6676 | 66-68 | 25 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07STRGUR-GUR | 9 | 124m | 3/10-10/47 | 9-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL07STRGUR-STR | 91 | 123m | 0 | 91-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07GIADIA-DIA | 41 | 42m | 33/46-70/2496 | 50-52 | 5 | **FLOW_ABOVE** | 58 |  |
| ITFWMATCH-26JUL07MAHCHA-CHA | 54 | 94m | 0 | 54-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07MAHCHA-MAH | 42 | 94m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07MANNAH-NAH | 45 | 94m | 0 | 45-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07MELROD-ROD | 7 | 127m | 232/10-35/15238 | 15-17 | 3 | **FLOW_ABOVE** | 20 | REPRICEABLE→10 |
| ITFWMATCH-26JUL07WANMIR-MIR | 61 | 67m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07WANMIR-WAN | 35 | 94m | 0 | 35-40 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL07KOBMAN-K | 26 | 64m | 1/27-27/35 | 26-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| WTACHALLENGERMATCH-26JUL07KOBMAN-M | 73 | 64m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL07MARBUR-M | 66 | 32m | 124/61-89/18437 | 67-68 | -5 | **FLOW_AT_LEVEL** | 66 |  |
| WTACHALLENGERMATCH-26JUL07SAWDOL-D | 37 | 63m | 6/38-38/103 | 38-40 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| WTACHALLENGERMATCH-26JUL07SAWDOL-S | 61 | 63m | 2/62-62/55 | 61-62 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→62 |
| WTACHALLENGERMATCH-26JUL07SCOSTO-S | 15 | 117m | 2/18-18/6 | 17-18 | 3 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL07SEBBRA-B | 49 | 94m | 1/52-52/185 | 51-52 | 3 | **FLOW_ABOVE** | 49 | flow above but bound 49c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL07SHYKIN-K | 40 | 30m | 0 | 42-43 | — | **NO_FLOW** | 40 |  |
| WTACHALLENGERMATCH-26JUL07VICBRA-B | 70 | 60m | 0 | 72-75 | — | **NO_FLOW** | 70 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL07SIMROU | 33 | 1 | **34** | 97 | -63 |
| ATPCHALLENGERMATCH-26JUL07PLAMAR | 34 | 3 | **37** | 97 | -60 |
| ITFWMATCH-26JUL07BUEXAV | 68 | 2 | **70** | 97 | -27 |
| ITFMATCH-26JUL07TSIHER | 50 | 26 | **76** | 97 | -21 |
| ITFWMATCH-26JUL07GIADIA | 34 | 52 | **86** | 97 | -11 |
| ATPCHALLENGERMATCH-26JUL07OSOSOT | 20 | 68 | **88** | 97 | -9 |
| ITFWMATCH-26JUL07MELROD | 74 | 17 | **91** | 97 | -6 |
| ATPCHALLENGERMATCH-26JUL07POLHEI | 92 | 2 | **94** | 97 | -3 |
| ITFWMATCH-26JUL07JAUMAT | 46 | 53 | **99** | 97 | +2 |
| WTACHALLENGERMATCH-26JUL07SCOSTO | 82 | 18 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL07SEBBRA | 48 | 52 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL07SHYKIN | 57 | 43 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL07HERHAR | 80 | 21 | **101** | 97 | +4 |
| WTACHALLENGERMATCH-26JUL07VICBRA | 27 | 75 | **102** | 97 | +5 |
| ITFMATCH-26JUL07ESTBAS | 7 | 95 | **102** | 97 | +5 |
| ITFWMATCH-26JUL07BROGAR | 5 | 99 | **104** | 97 | +7 |
| ATPCHALLENGERMATCH-26JUL07HERAMB | 7 | 99 | **106** | 97 | +9 |
| ITFMATCH-26JUL07LERBRO | 16 | 95 | **111** | 97 | +14 |
| ITFWMATCH-26JUL07ABASLA | 51 | 60 | **111** | 97 | +14 |
| ATPCHALLENGERMATCH-26JUL07BASGAU | 41 | 74 | **115** | 97 | +18 |
| ATPCHALLENGERMATCH-26JUL07GUEDON | 29 | 98 | **127** | 97 | +30 |
| ITFMATCH-26JUL07SELWAS | 59 | 68 | **127** | 97 | +30 |
| ITFMATCH-26JUL07MARBAS | 46 | 82 | **128** | 97 | +31 |
| ATPCHALLENGERMATCH-26JUL07MARCRE | 29 | 99 | **128** | 97 | +31 |
| ATPCHALLENGERMATCH-26JUL07WALVAL | 32 | 98 | **130** | 97 | +33 |
| ITFWMATCH-26JUL07MCNREE | 54 | 84 | **138** | 97 | +41 |
| ATPCHALLENGERMATCH-26JUL07MOESAN | 71 | 75 | **146** | 97 | +49 |
| ITFWMATCH-26JUL07VRARUG | 61 | 94 | **155** | 97 | +58 |

## PATTERNS (sub-B) — 62
- half_arm_aging: KXITFWMATCH-26JUL07BUEXAV-XAV {"fill": 68, "age_min": 133, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07GASCHE-CHE {"fill": 24, "age_min": 133, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXITFWMATCH-26JUL07SIMROU-SIM {"entry_minus_fv_burst": -61.5}
- half_arm_aging: KXITFWMATCH-26JUL07SIMROU-SIM {"fill": 33, "age_min": 133, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07WALVAL-WAL {"fill": 32, "age_min": 133, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07GUESAN-SAN {"fill": 8, "age_min": 133, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXITFWMATCH-26JUL07MALKOM-KOM {"entry_minus_fv_burst": -9.0}
- half_arm_aging: KXITFWMATCH-26JUL07MALKOM-KOM {"fill": 10, "age_min": 133, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07VRARUG-RUG {"fill": 61, "age_min": 133, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFWMATCH-26JUL07MCNREE-REE {"price": 54, "conception_ts": 1783440007.2574482, "detail": "buy 54c predates the conception stamp by 98min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07ZAHSEA-SEA {"fill": 82, "age_min": 131, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07GUEDON-DON {"fill": 29, "age_min": 131, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07GALRIN-GAL {"fill": 63, "age_min": 129, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07GAGMED-MED {"fill": 10, "age_min": 129, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07TSIHER-TSI {"fill": 50, "age_min": 129, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07MELROD-MEL {"fill": 74, "age_min": 127, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07BROWEH-WEH {"entry_minus_fv_burst": -16.5}
- half_arm_aging: KXITFWMATCH-26JUL07BROGAR-GAR {"fill": 5, "age_min": 125, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07RODAND-ROD {"fill": 39, "age_min": 125, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07POLHEI-HEI {"fill": 92, "age_min": 121, "mode": "QUEUE(flow at/below our level, unfilled)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07SCOSTO-STO {"fill": 82, "age_min": 117, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07MOUMON {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07GREKAS {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07BASGAU-BAS {"fill": 41, "age_min": 106, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06MALMAT-MAT {"fill": 49, "age_min": 105, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07PUTVAS-PUT {"fill": 5, "age_min": 94, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07MARBAS-BAS {"fill": 46, "age_min": 94, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07SCHCAN-SCH {"fill": 12, "age_min": 94, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07SEBBRA-SEB {"fill": 48, "age_min": 94, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFMATCH-26JUL07SEGMIT-MIT {"fill": 25, "age_min": 93, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07PLAMAR-PLA {"entry_minus_fv_burst": -32.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07PLAMAR-PLA {"fill": 34, "age_min": 88, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07DUSSHE-SHE {"fill": 28, "age_min": 86, "mode": "PAIRING(sib never rested)"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07BROWEH {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXITFMATCH-26JUL07TISNAP-TIS {"fill": 74, "age_min": 74, "mode": "PAIRING(sib never rested)"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07CLAHER {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07MARCRE-MAR {"fill": 29, "age_min": 74, "mode": "PAIRING(sib never rested)"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07MONSUM {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXITFWMATCH-26JUL07JOHKAJ-KAJ {"fill": 48, "age_min": 69, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07OSOSOT-OSO {"fill": 20, "age_min": 63, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07HERAMB-HER {"fill": 7, "age_min": 63, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTAMATCH-26JUL07OSAMUC-OSA {"fill": 53, "age_min": 63, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07BOUMOC-MOC {"fill": 30, "age_min": 62, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07MCNREE-REE {"fill": 54, "age_min": 62, "mode": "PAIRING(sib never rested)"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07AZKBON {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07VICBRA-VIC {"fill": 27, "age_min": 60, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07MOESAN-MOE {"fill": 71, "age_min": 54, "mode": "PAIRING(sib never rested)"}
- combined_over_goal_UNVERIFIED_BASIS: KXWTACHALLENGERMATCH-26JUL07MARBUR {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXITFWMATCH-26JUL07MULSIN-SIN {"fill": 25, "age_min": 54, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07HERHAR-HAR {"fill": 80, "age_min": 46, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07JAUMAT-JAU {"fill": 46, "age_min": 46, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07MAROLU-OLU {"fill": 30, "age_min": 44, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL07GIADIA-GIA {"fill": 34, "age_min": 42, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFMATCH-26JUL07SCHJON-SCH {"fill": 4, "age_min": 36, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07SELWAS-SEL {"fill": 59, "age_min": 34, "mode": "SET_BELOW_FLOW(prints 25c above)", "emitted_et": "2026-07-07 12:34:43 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL07LERBRO-BRO {"fill": 16, "age_min": 32, "mode": "SET_BELOW_FLOW(prints 13c above)", "emitted_et": "2026-07-07 12:34:43 PM ET"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07SHYKIN-SHY {"fill": 57, "age_min": 31, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-07 12:34:43 PM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07ONCCAM {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07HAMWAL {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- combined_over_goal_UNVERIFIED_BASIS: KXWTACHALLENGERMATCH-26JUL07ZAALEP {"combined": 100, "detail": "pair combined 100c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-07 12:34:43 PM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXWTACHALLENGERMATCH-26JUL07FITPIG {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-07 12:34:43 PM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07DROERH {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-07 12:34:43 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
