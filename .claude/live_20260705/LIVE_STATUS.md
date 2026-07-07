# LIVE VALIDATION — rolling status

- cycle 120 @ **2026-07-07 11:51:43 AM ET** | build `e1d8479` | session boot 07-07 10:21 ET | log `live_v3_20260707.jsonl` | 55149 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 10:38:44 | **grace_breach** | KXATPMATCH-26JUL07AUGDJO-DJO | fill 61c 5.7min past latch (grace 300s) |
| 10:38:44 | **combined_over_goal** | KXATPMATCH-26JUL07AUGDJO | pair combined 100c > goal 97c [complete_cross_insurance: cap102 by design (d?)] |
| 11:31:21 | **grace_breach** | KXWTAMATCH-26JUL07OSAMUC-OSA | fill 53c 62.6min past latch (grace 300s) |

## FILLS — 78 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10:21 | WTACHALLENGERMATCH-26JUL07ZANJAC-Z | WTA_CHALL | ? | 28 | 25 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | WTACHALLENGERMATCH-26JUL07ZANJAC-J | WTA_CHALL | ? | 69 | 66 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | ITFMATCH-26JUL07MOUMON-MOU | ITF_M | ? | 34 | 10 | +24 (window_cell) | — | pre | pair | 98 | MIXED |
| 10:21 | ATPCHALLENGERMATCH-26JUL07HAMWAL-H | ATP_CHALL | ? | 13 | 11 | +2 (window_cell) | — | pre | single |  | MIXED |
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
| 10:25 | ITFMATCH-26JUL07TSIHER-TSI | ITF_M | ? | 50 | 47 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 10:27 | ITFWMATCH-26JUL07MELROD-MEL | ITF_W | ? | 74 | 72 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 10:27 | ATPCHALLENGERMATCH-26JUL07BROWEH-W | ATP_CHALL | ? | 35 | 35 | +0 (window_cell) | -16.5 | pre | pair | 99 | EARNED |
| 10:28 | ITFMATCH-26JUL07URSPOU-URS | ITF_M | ? | 47 | 60 | -13 (window_cell) | 1.5 | pre | pair | 97 | EARNED |
| 10:29 | ITFWMATCH-26JUL07BROGAR-GAR | ITF_W | ? | 5 | 1 | +4 (window_cell) | — | pre | single |  | MIXED |
| 10:29 | ATPCHALLENGERMATCH-26JUL07RODAND-R | ATP_CHALL | ? | 39 | 36 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 10:31 | ITFWMATCH-26JUL07ARCOLI-OLI | ITF_W | ? | 72 | 70 | +2 (adopted_est) | — | pre | pair | 93 | PENDING |
| 10:31 | ITFWMATCH-26JUL07MELDIG-DIG | ITF_W | ? | 91 | 75 | +16 (window_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 10:33 | ATPCHALLENGERMATCH-26JUL07POLHEI-H | ATP_CHALL | ? | 92 | 91 | +1 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 10:34 | ATPMATCH-26JUL07AUGDJO-AUG | ATP_MAIN | underdog | 39 | 37 | +2 (place_cell) | -0.5 | 1.7 | pair | 100 | MIXED |
| 10:37 | WTACHALLENGERMATCH-26JUL07SCOSTO-S | WTA_CHALL | leader | 82 | 79 | +3 (place_cell) | — | pre | single |  | PENDING |
| 10:38 | ATPMATCH-26JUL07AUGDJO-DJO | ATP_MAIN | leader | 61 | 60 | +1 (place_cell) | -0.5 | 5.7 | pair | 100 | MIXED |
| 10:40 | ITFMATCH-26JUL07MOUMON-MON | ITF_M | ? | 64 | 82 | -18 (window_cell) | — | pre | pair | 98 | MIXED |
| 10:40 | WTACHALLENGERMATCH-26JUL07ZAALEP-Z | WTA_CHALL | ? | 58 | 55 | +3 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 10:41 | ITFMATCH-26JUL07GREKAS-GRE | ITF_M | ? | 91 | 88 | +3 (adopted_est) | — | pre | pair | 99 | PENDING |
| 10:44 | ITFMATCH-26JUL07GREKAS-KAS | ITF_M | ? | 8 | 4 | +4 (adopted_est) | — | pre | pair | 99 | PENDING |
| 10:49 | ATPCHALLENGERMATCH-26JUL07BASGAU-B | ATP_CHALL | ? | 41 | 41 | +0 (window_cell) | 24.5 | pre | single |  | EARNED |
| 10:49 | ATPCHALLENGERMATCH-26JUL06MALMAT-M | ATP_CHALL | ? | 49 | 46 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 11:00 | ITFMATCH-26JUL07PUTVAS-PUT | ITF_M | ? | 5 | 1 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:00 | ITFMATCH-26JUL07MARBAS-BAS | ITF_M | ? | 46 | 42 | +4 (window_cell) | — | pre | single |  | MIXED |
| 11:00 | ITFWMATCH-26JUL07SCHCAN-SCH | ITF_W | ? | 12 | 8 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:00 | WTACHALLENGERMATCH-26JUL07SEBBRA-S | WTA_CHALL | ? | 48 | 45 | +3 (window_cell) | — | pre | single |  | MIXED |
| 11:02 | ITFMATCH-26JUL07SEGMIT-MIT | ITF_M | ? | 25 | 21 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:03 | ITFWMATCH-26JUL07ARCOLI-ARC | ITF_W | ? | 21 | 17 | +4 (adopted_est) | — | pre | pair | 93 | PENDING |
| 11:03 | ITFMATCH-26JUL07ROLLAR-ROL | ITF_M | ? | 92 | 89 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 11:06 | ATPCHALLENGERMATCH-26JUL07PLAMAR-P | ATP_CHALL | ? | 34 | 36 | -2 (window_cell) | — | pre | single |  | EARNED |
| 11:08 | ITFMATCH-26JUL07DUSSHE-SHE | ITF_M | ? | 28 | 24 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:11 | ITFWMATCH-26JUL07EVAGOW-EVA | ITF_W | ? | 79 | 77 | +2 (adopted_est) | — | pre | pair | 93 | PENDING |
| 11:11 | ATPCHALLENGERMATCH-26JUL07CLAHER-H | ATP_CHALL | ? | 53 | 52 | +1 (window_cell) | — | pre | pair | 98 | GIFT_CLASS |
| 11:14 | ITFWMATCH-26JUL07EVAGOW-GOW | ITF_W | ? | 14 | 10 | +4 (adopted_est) | — | pre | pair | 93 | PENDING |
| 11:20 | ATPCHALLENGERMATCH-26JUL07BROWEH-B | ATP_CHALL | ? | 64 | 64 | +0 (window_cell) | 13.5 | pre | pair | 99 | GIFT_CLASS |
| 11:20 | ITFMATCH-26JUL07TISNAP-TIS | ITF_M | ? | 74 | 71 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 11:20 | ATPCHALLENGERMATCH-26JUL07CLAHER-C | ATP_CHALL | ? | 45 | 43 | +2 (window_cell) | — | pre | pair | 98 | MIXED |
| 11:20 | ATPCHALLENGERMATCH-26JUL07MARCRE-M | ATP_CHALL | ? | 29 | 29 | +0 (window_cell) | — | pre | single |  | EARNED |
| 11:24 | ATPCHALLENGERMATCH-26JUL07DROERH-E | ATP_CHALL | ? | 24 | 21 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 11:24 | WTACHALLENGERMATCH-26JUL07FITPIG-F | WTA_CHALL | ? | 31 | 29 | +2 (window_cell) | — | pre | single |  | MIXED |
| 11:24 | ATPCHALLENGERMATCH-26JUL07MONSUM-M | ATP_CHALL | ? | 89 | 87 | +2 (window_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 11:24 | ATPCHALLENGERMATCH-26JUL07MONSUM-S | ATP_CHALL | ? | 10 | 8 | +2 (window_cell) | — | pre | pair | 99 | MIXED |
| 11:25 | ITFWMATCH-26JUL07JOHKAJ-KAJ | ITF_W | ? | 48 | 44 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:28 | ATPCHALLENGERMATCH-26JUL07AZKBON-A | ATP_CHALL | ? | 33 | 32 | +1 (window_cell) | -1.0 | pre | pair | 98 | MIXED |
| 11:30 | ITFWMATCH-26JUL07SOTTEO-SOT | ITF_W | leader | 93 | 92 | +1 (place_cell) | — | pre | single |  | PENDING |
| 11:31 | ATPCHALLENGERMATCH-26JUL07OSOSOT-O | ATP_CHALL | ? | 20 | 21 | -1 (window_cell) | — | pre | single |  | EARNED |
| 11:31 | ATPCHALLENGERMATCH-26JUL07HERAMB-H | ATP_CHALL | ? | 7 | 7 | +0 (window_cell) | — | pre | single |  | EARNED |
| 11:31 | WTAMATCH-26JUL07OSAMUC-OSA | WTA_MAIN | ? | 53 | 53 | +0 (adopted_est) | — | 62.6 | single |  | PENDING |
| 11:33 | ITFMATCH-26JUL07BOUMOC-MOC | ITF_M | ? | 30 | 26 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:33 | ITFWMATCH-26JUL07MCNREE-REE | ITF_W | ? | 54 | 52 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 11:34 | ATPCHALLENGERMATCH-26JUL07AZKBON-B | ATP_CHALL | ? | 65 | 64 | +1 (window_cell) | 0.5 | pre | pair | 98 | GIFT_CLASS |
| 11:34 | WTACHALLENGERMATCH-26JUL07VICBRA-V | WTA_CHALL | underdog | 27 | 24 | +3 (place_cell) | — | pre | single |  | PENDING |
| 11:38 | WTACHALLENGERMATCH-26JUL07MARBUR-B | WTA_CHALL | ? | 31 | 29 | +2 (window_cell) | — | pre | pair | 99 | MIXED |
| 11:40 | ATPCHALLENGERMATCH-26JUL07MOESAN-M | ATP_CHALL | ? | 71 | 71 | +0 (window_cell) | 15.0 | pre | single |  | GIFT_CLASS |
| 11:40 | WTACHALLENGERMATCH-26JUL07MARBUR-M | WTA_CHALL | ? | 68 | 66 | +2 (window_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 11:40 | ITFWMATCH-26JUL07MULSIN-SIN | ITF_W | ? | 25 | 21 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:40 | ITFWMATCH-26JUL07SCHZID-ZID | ITF_W | ? | 70 | 68 | +2 (adopted_est) | — | pre | pair | 97 | PENDING |
| 11:46 | ITFMATCH-26JUL07BARCOT-COT | ITF_M | ? | 41 | 37 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:46 | ITFMATCH-26JUL07ROLLAR-LAR | ITF_M | ? | 5 | 1 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 11:48 | ATPCHALLENGERMATCH-26JUL07HERHAR-H | ATP_CHALL | ? | 80 | 77 | +3 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 11:48 | ITFWMATCH-26JUL07JAUMAT-JAU | ITF_W | ? | 46 | 42 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 11:50 | ITFWMATCH-26JUL07SCHZID-SCH | ITF_W | ? | 27 | 23 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 11:50 | ITFWMATCH-26JUL07MAROLU-OLU | ITF_W | ? | 30 | 26 | +4 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 44 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 15, 'FLOW_AT_LEVEL': 7, 'NO_FLOW': 22} | repriceable now: true 7 / false 37 | **cumulative bid_grade lines: 4839 (repriceable true 419 / false 4420)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07AZKBON-A | 32 | 15m | 26/31-35/14665 | 31-32 | -1 | **FLOW_AT_LEVEL** | 32 |  |
| ATPCHALLENGERMATCH-26JUL07BASGAU-G | 54 | 54m | 176/70-93/25023 | 81-82 | 16 | **FLOW_ABOVE** | 54 | flow above but bound 54c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07BROWEH-W | 33 | 25m | 53/12-50/4927 | 11-16 | -21 | **FLOW_AT_LEVEL** | 33 |  |
| ATPCHALLENGERMATCH-26JUL07CLAHER-C | 44 | 13m | 55/40-59/2948 | 55-56 | -4 | **FLOW_AT_LEVEL** | 43 |  |
| ATPCHALLENGERMATCH-26JUL07HERAMB-H | 1 | 12m | 88/9-28/3773 | 19-20 | 8 | **FLOW_ABOVE** | 7 | flow above but bound 7c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07KRUPIE-K | 60 | 64m | 200/64-98/30678 | 63-64 | 4 | **FLOW_ABOVE** | 67 | REPRICEABLE→64 |
| ATPCHALLENGERMATCH-26JUL07MARBER-B | 58 | 84m | 658/21-87/61080 | 84-85 | -37 | **FLOW_AT_LEVEL** | 61 |  |
| ATPCHALLENGERMATCH-26JUL07MCCSAK-M | 27 | 11m | 0 | 27-28 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07MCCSAK-S | 71 | 11m | 0 | 72-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07MONSUM-S | 8 | 23m | 121/4-16/14597 | 3-4 | -4 | **FLOW_AT_LEVEL** | 8 |  |
| ATPCHALLENGERMATCH-26JUL07PLAMAR-P | 34 | 41m | 27/35-47/1131 | 35-36 | 1 | **FLOW_ABOVE** | 36 | REPRICEABLE→35 |
| ATPCHALLENGERMATCH-26JUL07POLHEI-P | 4 | 75m | 641/1-12/165047 | 8-9 | -3 | **FLOW_AT_LEVEL** | 4 |  |
| ATPCHALLENGERMATCH-26JUL07POPPDA-P | 57 | 64m | 2/58-58/126 | 57-58 | 1 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07POPPDA-P | 39 | 41m | 5/43-45/226 | 42-46 | 4 | **FLOW_ABOVE** | 42 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL07TOMSHI-S | 36 | 21m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07TOMSHI-T | 63 | 21m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07ARSWIL-ARS | 46 | 82m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07ARSWIL-WIL | 52 | 81m | 0 | 52-54 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07BARCOT-BAR | 56 | 5m | 2/61-62/62 | 66-71 | 5 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07ESTBAS-BAS | 7 | 21m | 0 | 7-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07ESTBAS-EST | 91 | 21m | 0 | 91-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07GREKAS-KAS | 6 | 65m | 10/13-22/153 | 10-18 | 7 | **FLOW_ABOVE** | 6 | flow above but bound 6c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07KLEHOH-HOH | 86 | 51m | 0 | 86-90 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07KLEHOH-KLE | 10 | 51m | 0 | 10-13 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07MOUMON-MOU | 31 | 52m | 108/10-38/4277 | 12-13 | -21 | **FLOW_AT_LEVEL** | 10 |  |
| ITFMATCH-26JUL07STRGUR-GUR | 9 | 81m | 3/10-10/47 | 9-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL07STRGUR-STR | 91 | 80m | 0 | 91-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07ARCOLI-OLI | 76 | 41m | 35/89-96/1033 | 96-97 | 13 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL07MAHCHA-CHA | 54 | 51m | 0 | 54-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07MAHCHA-MAH | 42 | 51m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07MANNAH-NAH | 45 | 51m | 0 | 45-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07MELROD-ROD | 7 | 84m | 87/13-35/6541 | 11-13 | 6 | **FLOW_ABOVE** | 23 |  |
| ITFWMATCH-26JUL07SOTTEO-TEO | 2 | 0m | 0 | 8-10 | — | **NO_FLOW** | 4 |  |
| ITFWMATCH-26JUL07WANMIR-MIR | 61 | 24m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07WANMIR-WAN | 35 | 51m | 0 | 35-39 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL07KOBMAN-K | 26 | 21m | 1/27-27/35 | 26-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| WTACHALLENGERMATCH-26JUL07KOBMAN-M | 73 | 21m | 0 | 73-74 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL07SAWDOL-D | 37 | 20m | 6/38-38/103 | 37-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| WTACHALLENGERMATCH-26JUL07SAWDOL-S | 61 | 20m | 1/62-62/9 | 61-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→62 |
| WTACHALLENGERMATCH-26JUL07SCOSTO-S | 15 | 74m | 1/18-18/1 | 17-18 | 3 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL07SEBBRA-B | 49 | 51m | 0 | 50-52 | — | **NO_FLOW** | 49 |  |
| WTACHALLENGERMATCH-26JUL07SHYKIN-K | 42 | 21m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL07SHYKIN-S | 57 | 21m | 0 | 57-58 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL07VICBRA-B | 70 | 17m | 0 | 72-75 | — | **NO_FLOW** | 70 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL07SIMROU | 33 | 1 | **34** | 97 | -63 |
| ITFWMATCH-26JUL07BUEXAV | 68 | 2 | **70** | 97 | -27 |
| ITFWMATCH-26JUL07MELROD | 74 | 13 | **87** | 97 | -10 |
| ATPCHALLENGERMATCH-26JUL07HERAMB | 7 | 81 | **88** | 97 | -9 |
| ATPCHALLENGERMATCH-26JUL07PLAMAR | 34 | 65 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL07HAMWAL | 13 | 87 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL07SCOSTO | 82 | 18 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL07SEBBRA | 48 | 52 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL07POLHEI | 92 | 9 | **101** | 97 | +4 |
| WTACHALLENGERMATCH-26JUL07ZAALEP | 58 | 43 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL07DROERH | 24 | 77 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL07HERHAR | 80 | 21 | **101** | 97 | +4 |
| WTACHALLENGERMATCH-26JUL07VICBRA | 27 | 75 | **102** | 97 | +5 |
| ITFWMATCH-26JUL07SOTTEO | 93 | 10 | **103** | 97 | +6 |
| ITFWMATCH-26JUL07BROGAR | 5 | 99 | **104** | 97 | +7 |
| ITFMATCH-26JUL07MARBAS | 46 | 61 | **107** | 97 | +10 |
| ATPCHALLENGERMATCH-26JUL07OSOSOT | 20 | 92 | **112** | 97 | +15 |
| ITFMATCH-26JUL07BARCOT | 41 | 71 | **112** | 97 | +15 |
| WTACHALLENGERMATCH-26JUL07FITPIG | 31 | 83 | **114** | 97 | +17 |
| ATPCHALLENGERMATCH-26JUL07MARCRE | 29 | 93 | **122** | 97 | +25 |
| ATPCHALLENGERMATCH-26JUL07BASGAU | 41 | 82 | **123** | 97 | +26 |
| ATPCHALLENGERMATCH-26JUL07GUEDON | 29 | 98 | **127** | 97 | +30 |
| ATPCHALLENGERMATCH-26JUL07WALVAL | 32 | 98 | **130** | 97 | +33 |
| ATPCHALLENGERMATCH-26JUL07MOESAN | 71 | 69 | **140** | 97 | +43 |
| ITFWMATCH-26JUL07VRARUG | 61 | 94 | **155** | 97 | +58 |

## PATTERNS (sub-B) — 40
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07HAMWAL-HAM {"fill": 13, "age_min": 90, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07BUEXAV-XAV {"fill": 68, "age_min": 90, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07GASCHE-CHE {"fill": 24, "age_min": 90, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXITFWMATCH-26JUL07SIMROU-SIM {"entry_minus_fv_burst": -61.5}
- half_arm_aging: KXITFWMATCH-26JUL07SIMROU-SIM {"fill": 33, "age_min": 90, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07WALVAL-WAL {"fill": 32, "age_min": 90, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07GUESAN-SAN {"fill": 8, "age_min": 90, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXITFWMATCH-26JUL07MALKOM-KOM {"entry_minus_fv_burst": -9.0}
- half_arm_aging: KXITFWMATCH-26JUL07MALKOM-KOM {"fill": 10, "age_min": 90, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07VRARUG-RUG {"fill": 61, "age_min": 90, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07ZAHSEA-SEA {"fill": 82, "age_min": 88, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07GUEDON-DON {"fill": 29, "age_min": 88, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07GALRIN-GAL {"fill": 63, "age_min": 86, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07GAGMED-MED {"fill": 10, "age_min": 86, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07TSIHER-TSI {"fill": 50, "age_min": 86, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07MELROD-MEL {"fill": 74, "age_min": 84, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07BROWEH-WEH {"entry_minus_fv_burst": -16.5}
- half_arm_aging: KXITFWMATCH-26JUL07BROGAR-GAR {"fill": 5, "age_min": 82, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07RODAND-ROD {"fill": 39, "age_min": 82, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07POLHEI-HEI {"fill": 92, "age_min": 78, "mode": "QUEUE(flow at/below our level, unfilled)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07SCOSTO-STO {"fill": 82, "age_min": 74, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07MOUMON {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07ZAALEP-ZAA {"fill": 58, "age_min": 72, "mode": "PAIRING(sib never rested)"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07GREKAS {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07BASGAU-BAS {"fill": 41, "age_min": 63, "mode": "SET_BELOW_FLOW(prints 16c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06MALMAT-MAT {"fill": 49, "age_min": 62, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07PUTVAS-PUT {"fill": 5, "age_min": 51, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07MARBAS-BAS {"fill": 46, "age_min": 51, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07SCHCAN-SCH {"fill": 12, "age_min": 51, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07SEBBRA-SEB {"fill": 48, "age_min": 51, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFMATCH-26JUL07SEGMIT-MIT {"fill": 25, "age_min": 50, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07PLAMAR-PLA {"fill": 34, "age_min": 45, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07DUSSHE-SHE {"fill": 28, "age_min": 43, "mode": "PAIRING(sib never rested)"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07BROWEH {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXITFMATCH-26JUL07TISNAP-TIS {"fill": 74, "age_min": 31, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-07 11:51:43 AM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07CLAHER {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07MARCRE-MAR {"fill": 29, "age_min": 31, "mode": "PAIRING(sib never rested)"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07MONSUM {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07AZKBON {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- combined_over_goal_UNVERIFIED_BASIS: KXWTACHALLENGERMATCH-26JUL07MARBUR {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
