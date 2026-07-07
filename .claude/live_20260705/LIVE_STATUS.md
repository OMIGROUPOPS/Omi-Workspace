# LIVE VALIDATION — rolling status

- cycle 118 @ **2026-07-07 11:30:14 AM ET** | build `0a37cd3` | session boot 07-07 10:21 ET | log `live_v3_20260707.jsonl` | 44248 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 10:38:44 | **grace_breach** | KXATPMATCH-26JUL07AUGDJO-DJO | fill 61c 5.7min past latch (grace 300s) |
| 10:38:44 | **combined_over_goal** | KXATPMATCH-26JUL07AUGDJO | pair combined 100c > goal 97c [complete_cross_insurance: cap102 by design (d?)] |

## FILLS — 59 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10:21 | WTACHALLENGERMATCH-26JUL07ZANJAC-Z | WTA_CHALL | ? | 28 | 25 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | WTACHALLENGERMATCH-26JUL07ZANJAC-J | WTA_CHALL | ? | 69 | 66 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | ITFMATCH-26JUL07MOUMON-MOU | ITF_M | ? | 34 | 30 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
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
| 10:40 | ITFMATCH-26JUL07MOUMON-MON | ITF_M | ? | 64 | 61 | +3 (adopted_est) | — | pre | pair | 98 | PENDING |
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
| 11:03 | ITFMATCH-26JUL07ROLLAR-ROL | ITF_M | ? | 92 | 89 | +3 (adopted_est) | — | pre | single |  | PENDING |
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
| 11:28 | ATPCHALLENGERMATCH-26JUL07AZKBON-A | ATP_CHALL | ? | 33 | 32 | +1 (window_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 30 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 12, 'NO_FLOW': 14, 'FLOW_AT_LEVEL': 4} | repriceable now: true 2 / false 28 | **cumulative bid_grade lines: 4811 (repriceable true 415 / false 4396)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07BASGAU-G | 54 | 33m | 93/70-85/18270 | 80-81 | 16 | **FLOW_ABOVE** | 54 | flow above but bound 54c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07BROWEH-W | 33 | 3m | 9/49-50/1008 | 45-46 | 16 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07KRUPIE-K | 60 | 43m | 118/84-98/23186 | 90-91 | 24 | **FLOW_ABOVE** | 67 | flow above but bound 67c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07MARBER-B | 58 | 63m | 470/21-72/51312 | 43-48 | -37 | **FLOW_AT_LEVEL** | 61 |  |
| ATPCHALLENGERMATCH-26JUL07MONSUM-S | 8 | 2m | 10/14-16/1024 | 16-17 | 6 | **FLOW_ABOVE** | 8 | flow above but bound 8c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07PLAMAR-P | 34 | 20m | 10/35-47/479 | 36-38 | 1 | **FLOW_ABOVE** | 36 | REPRICEABLE→35 |
| ATPCHALLENGERMATCH-26JUL07POLHEI-P | 4 | 53m | 340/1-12/88945 | 7-8 | -3 | **FLOW_AT_LEVEL** | 4 |  |
| ATPCHALLENGERMATCH-26JUL07POPPDA-P | 57 | 43m | 0 | 57-58 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07POPPDA-P | 39 | 20m | 5/43-45/226 | 40-45 | 4 | **FLOW_ABOVE** | 42 | REPRICEABLE→42 |
| ITFMATCH-26JUL07ARSWIL-ARS | 46 | 60m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07ARSWIL-WIL | 52 | 59m | 0 | 52-54 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07GREKAS-KAS | 6 | 44m | 4/13-22/38 | 9-14 | 7 | **FLOW_ABOVE** | 6 | flow above but bound 6c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07IAMGAL-GAL | 57 | 68m | 175/66-96/10588 | 96-97 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL07KLEHOH-HOH | 86 | 30m | 0 | 86-90 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07KLEHOH-KLE | 10 | 30m | 0 | 10-13 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07MOUMON-MOU | 31 | 30m | 53/16-38/1389 | 14-16 | -15 | **FLOW_AT_LEVEL** | 33 |  |
| ITFMATCH-26JUL07STRGUR-GUR | 9 | 59m | 0 | 9-10 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07STRGUR-STR | 91 | 58m | 0 | 91-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07ARCOLI-OLI | 76 | 20m | 22/89-96/691 | 84-85 | 13 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL07JAUMAT-JAU | 47 | 68m | 175/61-91/22424 | 67-72 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07MAHCHA-CHA | 54 | 30m | 0 | 54-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07MAHCHA-MAH | 42 | 30m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07MANNAH-NAH | 45 | 30m | 0 | 45-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07MCNREE-REE | 54 | 68m | 119/61-97/18785 | 67-71 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07MELROD-ROD | 7 | 63m | 0 | 13-51 | — | **NO_FLOW** | 23 |  |
| ITFWMATCH-26JUL07SOTTEO-SOT | 93 | 2m | 1/93-93/5 | 88-90 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL07WANMIR-MIR | 61 | 2m | 0 | 61-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07WANMIR-WAN | 35 | 30m | 0 | 35-38 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL07SCOSTO-S | 15 | 52m | 1/18-18/1 | 17-18 | 3 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL07SEBBRA-B | 49 | 30m | 0 | 51-52 | — | **NO_FLOW** | 49 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL07SIMROU | 33 | 1 | **34** | 97 | -63 |
| ITFWMATCH-26JUL07BUEXAV | 68 | 2 | **70** | 97 | -27 |
| ATPCHALLENGERMATCH-26JUL07GUEDON | 29 | 66 | **95** | 97 | -2 |
| ATPCHALLENGERMATCH-26JUL07PLAMAR | 34 | 63 | **97** | 97 | +0 |
| ATPCHALLENGERMATCH-26JUL07HAMWAL | 13 | 87 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL07POLHEI | 92 | 8 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL07SCOSTO | 82 | 18 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL07SEBBRA | 48 | 52 | **100** | 97 | +3 |
| ITFWMATCH-26JUL07BROGAR | 5 | 96 | **101** | 97 | +4 |
| WTACHALLENGERMATCH-26JUL07ZAALEP | 58 | 43 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL07DROERH | 24 | 77 | **101** | 97 | +4 |
| WTACHALLENGERMATCH-26JUL07FITPIG | 31 | 71 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL07AZKBON | 33 | 71 | **104** | 97 | +7 |
| ITFMATCH-26JUL07MARBAS | 46 | 61 | **107** | 97 | +10 |
| ATPCHALLENGERMATCH-26JUL07MARCRE | 29 | 90 | **119** | 97 | +22 |
| ATPCHALLENGERMATCH-26JUL07BASGAU | 41 | 81 | **122** | 97 | +25 |
| ITFWMATCH-26JUL07MELROD | 74 | 51 | **125** | 97 | +28 |
| ATPCHALLENGERMATCH-26JUL07WALVAL | 32 | 98 | **130** | 97 | +33 |
| ITFWMATCH-26JUL07VRARUG | 61 | 94 | **155** | 97 | +58 |

## PATTERNS (sub-B) — 29
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07HAMWAL-HAM {"fill": 13, "age_min": 69, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07BUEXAV-XAV {"fill": 68, "age_min": 69, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07GASCHE-CHE {"fill": 24, "age_min": 69, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXITFWMATCH-26JUL07SIMROU-SIM {"entry_minus_fv_burst": -61.5}
- half_arm_aging: KXITFWMATCH-26JUL07SIMROU-SIM {"fill": 33, "age_min": 69, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07WALVAL-WAL {"fill": 32, "age_min": 68, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07GUESAN-SAN {"fill": 8, "age_min": 68, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXITFWMATCH-26JUL07MALKOM-KOM {"entry_minus_fv_burst": -9.0}
- half_arm_aging: KXITFWMATCH-26JUL07MALKOM-KOM {"fill": 10, "age_min": 68, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07VRARUG-RUG {"fill": 61, "age_min": 68, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07ZAHSEA-SEA {"fill": 82, "age_min": 66, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07GUEDON-DON {"fill": 29, "age_min": 66, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07GALRIN-GAL {"fill": 63, "age_min": 65, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07GAGMED-MED {"fill": 10, "age_min": 65, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07TSIHER-TSI {"fill": 50, "age_min": 65, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07MELROD-MEL {"fill": 74, "age_min": 63, "mode": "STARVATION(no prints since post)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07BROWEH-WEH {"entry_minus_fv_burst": -16.5, "emitted_et": "2026-07-07 11:30:14 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL07BROGAR-GAR {"fill": 5, "age_min": 60, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07RODAND-ROD {"fill": 39, "age_min": 60, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07POLHEI-HEI {"fill": 92, "age_min": 56, "mode": "QUEUE(flow at/below our level, unfilled)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07SCOSTO-STO {"fill": 82, "age_min": 52, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07MOUMON {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07ZAALEP-ZAA {"fill": 58, "age_min": 50, "mode": "PAIRING(sib never rested)"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07GREKAS {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07BASGAU-BAS {"fill": 41, "age_min": 41, "mode": "SET_BELOW_FLOW(prints 16c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06MALMAT-MAT {"fill": 49, "age_min": 41, "mode": "PAIRING(sib never rested)"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07BROWEH {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-07 11:30:14 AM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07CLAHER {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-07 11:30:14 AM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXATPCHALLENGERMATCH-26JUL07MONSUM {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-07 11:30:14 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
