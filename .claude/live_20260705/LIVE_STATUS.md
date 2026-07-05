# LIVE VALIDATION — rolling status

- cycle 7 @ **2026-07-05 12:04:43 PM ET** | build `d839748` | session boot 07-05 10:39 ET | log `live_v3_20260705.jsonl` | 17090 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 4 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 10:48:45 | **grace_breach** | KXITFMATCH-26JUL05SALCON-CON | fill 13c 5.2min past latch (grace 300s) |
| 11:10:44 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05TENBER | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 11:15:35 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL05KOBLEW | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 11:28:58 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05PEROPI | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 42 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10:39 | ITFWMATCH-26JUL05TRAABB-ABB | ITF_W | ? | 64 | 64 | +0 (window_cell) | -31.5 | pre | pair | 97 | EARNED |
| 10:39 | ATPCHALLENGERMATCH-26JUL05RAMNEU-R | ATP_CHALL | ? | 36 | 2 | +34 (window_cell) | — | pre | single |  | MIXED |
| 10:39 | ATPCHALLENGERMATCH-26JUL05WEHIFI-I | ATP_CHALL | ? | 11 | 8 | +3 (adopted_est) | 5.5 | pre | single |  | GIFT_CLASS |
| 10:39 | WTACHALLENGERMATCH-26JUL05DITLEW-D | WTA_CHALL | ? | 31 | 28 | +3 (adopted_est) | 25.5 | pre | single |  | GIFT_CLASS |
| 10:39 | ATPCHALLENGERMATCH-26JUL05KUZMAT-M | ATP_CHALL | ? | 5 | 2 | +3 (adopted_est) | -2.5 | pre | single |  | MIXED |
| 10:40 | ITFWMATCH-26JUL05AITDAE-AIT | ITF_W | underdog | 8 | 4 | +4 (place_cell) | -9.0 | pre | pair | 89 | EARNED |
| 10:41 | ATPCHALLENGERMATCH-26JUL05VALREJ-V | ATP_CHALL | leader | 62 | 71 | -9 (place_cell) | 11.5 | pre | single |  | GIFT_CLASS |
| 10:41 | ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | ATP_CHALL | underdog | 23 | 19 | +4 (place_cell) | 8.0 | pre | single |  | GIFT_CLASS |
| 10:41 | ITFMATCH-26JUL05GELBRE-GEL | ITF_M | ? | 44 | 40 | +4 (window_cell) | — | pre | pair | 92 | MIXED |
| 10:42 | WTAMATCH-26JUL05BENGAU-GAU | WTA_MAIN | ? | 50 | 50 | +0 (adopted_est) | 0.5 | pre | single |  | MIXED |
| 10:48 | ITFMATCH-26JUL05SALCON-CON | ITF_M | ? | 13 | 29 | -16 (window_cell) | -10.0 | 5.2 | single |  | EARNED |
| 10:53 | ITFMATCH-26JUL05GELBRE-BRE | ITF_M | ? | 48 | 56 | -8 (window_cell) | — | pre | pair | 92 | EARNED |
| 10:53 | ATPCHALLENGERMATCH-26JUL05PEROPI-O | ATP_CHALL | ? | 25 | 22 | +3 (window_cell) | -8.0 | pre | pair | 98 | EARNED |
| 10:55 | ATPCHALLENGERMATCH-26JUL05INGFEL-F | ATP_CHALL | ? | 72 | 72 | +0 (adopted_est) | — | pre | single |  | PENDING |
| 11:02 | ITFWMATCH-26JUL05TRAABB-TRA | ITF_W | ? | 33 | 29 | +4 (window_cell) | 29.0 | pre | pair | 97 | GIFT_CLASS |
| 11:07 | ATPCHALLENGERMATCH-26JUL05HUEMAR-M | ATP_CHALL | ? | 31 | 28 | +3 (window_cell) | — | pre | single |  | MIXED |
| 11:07 | ATPCHALLENGERMATCH-26JUL05TENBER-T | ATP_CHALL | ? | 42 | 39 | +3 (window_cell) | — | pre | pair | 99 | MIXED |
| 11:08 | WTACHALLENGERMATCH-26JUL05KOBLEW-L | WTA_CHALL | ? | 10 | 8 | +2 (window_cell) | — | pre | pair | 99 | MIXED |
| 11:10 | ATPCHALLENGERMATCH-26JUL05TENBER-B | ATP_CHALL | ? | 57 | 60 | -3 (window_cell) | — | pre | pair | 99 | MIXED |
| 11:12 | ITFWMATCH-26JUL05AITDAE-DAE | ITF_W | ? | 81 | 94 | -13 (window_cell) | 2.5 | pre | pair | 89 | MIXED |
| 11:12 | ATPCHALLENGERMATCH-26JUL05SUNBAR-B | ATP_CHALL | ? | 57 | 59 | -2 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 11:12 | ATPCHALLENGERMATCH-26JUL05PRICOU-C | ATP_CHALL | ? | 50 | 53 | -3 (window_cell) | — | pre | pair | 97 | MIXED |
| 11:15 | ATPCHALLENGERMATCH-26JUL05SUNBAR-S | ATP_CHALL | ? | 40 | 41 | -1 (window_cell) | — | pre | pair | 97 | EARNED |
| 11:15 | ATPCHALLENGERMATCH-26JUL05RYBTUN-T | ATP_CHALL | ? | 73 | 75 | -2 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 11:15 | WTACHALLENGERMATCH-26JUL05KOBLEW-K | WTA_CHALL | ? | 89 | 91 | -2 (window_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 11:16 | ATPCHALLENGERMATCH-26JUL05HUANOC-H | ATP_CHALL | ? | 29 | 29 | +0 (window_cell) | 12.0 | pre | single |  | EARNED |
| 11:16 | ATPCHALLENGERMATCH-26JUL05PRICOU-P | ATP_CHALL | ? | 47 | 54 | -7 (window_cell) | — | pre | pair | 97 | EARNED |
| 11:21 | ITFWMATCH-26JUL05TUBSOB-SOB | ITF_W | ? | 24 | 30 | -6 (window_cell) | 9.0 | pre | single |  | EARNED |
| 11:28 | ATPCHALLENGERMATCH-26JUL05PEROPI-P | ATP_CHALL | ? | 73 | 75 | -2 (window_cell) | 9.0 | pre | pair | 98 | GIFT_CLASS |
| 11:32 | ATPCHALLENGERMATCH-26JUL05PDACAS-C | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | single |  | MIXED |
| 11:33 | ITFMATCH-26JUL05BONBRA-BRA | ITF_M | ? | 13 | 10 | +3 (window_cell) | — | pre | single |  | MIXED |
| 11:37 | ATPCHALLENGERMATCH-26JUL05HIGZHU-H | ATP_CHALL | ? | 38 | 38 | +0 (window_cell) | -8.5 | pre | pair | 96 | EARNED |
| 11:43 | ATPCHALLENGERMATCH-26JUL05HIGZHU-Z | ATP_CHALL | ? | 58 | 61 | -3 (window_cell) | 9.5 | pre | pair | 96 | GIFT_CLASS |
| 11:45 | ATPCHALLENGERMATCH-26JUL05POTANG-P | ATP_CHALL | ? | 50 | 50 | +0 (fill_est) | — | pre | single |  | PENDING |
| 11:45 | ATPCHALLENGERMATCH-26JUL05KAMVAN-K | ATP_CHALL | ? | 13 | 10 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 11:47 | ITFMATCH-26JUL05SABMIS-SAB | ITF_M | underdog | 81 | 14 | +67 (place_cell) | 15.0 | pre | single |  | GIFT_CLASS |
| 11:48 | ATPCHALLENGERMATCH-26JUL05BINPOL-B | ATP_CHALL | ? | 59 | 61 | -2 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 11:54 | ATPCHALLENGERMATCH-26JUL05GOIAND-G | ATP_CHALL | underdog | 31 | 26 | +5 (place_cell) | — | pre | single |  | MIXED |
| 11:56 | ATPCHALLENGERMATCH-26JUL05GANZIN-G | ATP_CHALL | underdog | 29 | 25 | +4 (place_cell) | — | pre | single |  | MIXED |
| 12:01 | ITFMATCH-26JUL05XUXCHE-CHE | ITF_M | underdog | 2 | 1 | +1 (place_cell) | — | pre | single |  | MIXED |
| 12:01 | ITFMATCH-26JUL05FARBRO-FAR | ITF_M | ? | 64 | 64 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 12:03 | ITFMATCH-26JUL05THUGRE-THU | ITF_M | leader | 98 | 98 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 32 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 13, 'NO_FLOW': 15, 'FLOW_AT_LEVEL': 4} | repriceable now: true 3 / false 29 | **cumulative bid_grade lines: 699 (repriceable true 64 / false 635)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BANMAR-B | 65 | 84m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BANMAR-M | 33 | 84m | 7/33-37/340 | 33-37 | 0 | **FLOW_AT_LEVEL** | 33 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 91 | 67m | 39/97-99/5892 | 99-99 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-E | 65 | 84m | 1/67-67/10 | 65-68 | 2 | **FLOW_ABOVE** | 67 | REPRICEABLE→67 |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-J | 33 | 84m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GANZIN-Z | 68 | 8m | 0 | 70-72 | — | **NO_FLOW** | 68 |  |
| ATPCHALLENGERMATCH-26JUL05GOIAND-A | 66 | 10m | 2/70-71/203 | 68-70 | 4 | **FLOW_ABOVE** | 66 | flow above but bound 66c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05IMAMIL-I | 41 | 14m | 0 | 41-43 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IMAMIL-M | 58 | 14m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05KOZMAY-K | 46 | 14m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05KOZMAY-M | 53 | 13m | 0 | 53-54 | — | **NO_FLOW** | 54 |  |
| ATPCHALLENGERMATCH-26JUL05MARJUN-J | 39 | 14m | 0 | 39-41 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05MARJUN-M | 59 | 14m | 0 | 59-62 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05MORMAR-M | 39 | 32m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05MORMAR-M | 59 | 49m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PDACAS-P | 58 | 32m | 3/62-63/20 | 61-63 | 4 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05POPCAS-C | 6 | 54m | 0 | 6-8 | — | **NO_FLOW** | 4 |  |
| ATPCHALLENGERMATCH-26JUL05POPCAS-P | 93 | 52m | 6/94-95/132 | 93-95 | 1 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05PRICOU-P | 47 | 33m | 59/4-59/3259 | 4-4 | -43 | **FLOW_AT_LEVEL** | 47 |  |
| ATPCHALLENGERMATCH-26JUL05RAMNEU-N | 61 | 85m | 17/98-99/2359 | 99-98 | 37 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SANROD-R | 82 | 54m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SANROD-S | 17 | 54m | 0 | 17-18 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SUNBAR-B | 57 | 35m | 73/59-88/9344 | 83-84 | 2 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05TENBER-B | 55 | 45m | 75/64-91/9474 | 91-87 | 9 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05FARBRO-BRO | 33 | 3m | 69/39-48/6724 | 46-39 | 6 | **FLOW_ABOVE** | 30 | flow above but bound 30c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05GELBRE-GEL | 46 | 71m | 374/25-62/28260 | 51-50 | -21 | **FLOW_AT_LEVEL** | 40 |  |
| ITFMATCH-26JUL05XUXCHE-XUX | 95 | 3m | 39/98-99/2197 | 98-98 | 3 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05KOBLEW-L | 8 | 49m | 212/1-22/20582 | 4-5 | -7 | **FLOW_AT_LEVEL** | 8 |  |
| WTACHALLENGERMATCH-26JUL05SMIJAR-J | 20 | 13m | 1/21-21/18 | 20-21 | 1 | **FLOW_ABOVE** | 18 | flow above but bound 18c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05SMIJAR-S | 81 | 12m | 0 | 81-82 | — | **NO_FLOW** | 81 |  |
| WTACHALLENGERMATCH-26JUL05YAMOVC-O | 28 | 84m | 1/30-30/45 | 28-30 | 2 | **FLOW_ABOVE** | 27 | flow above but bound 27c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05YAMOVC-Y | 70 | 84m | 1/72-72/35 | 70-72 | 2 | **FLOW_ABOVE** | 72 | REPRICEABLE→72 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL05TUBSOB | 24 | 5 | **29** | 97 | -68 |
| ATPCHALLENGERMATCH-26JUL05VALREJ | 62 | 4 | **66** | 97 | -31 |
| ATPCHALLENGERMATCH-26JUL05HUANOC | 29 | 70 | **99** | 97 | +2 |
| ITFMATCH-26JUL05XUXCHE | 2 | 98 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05GOIAND | 31 | 70 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05GANZIN | 29 | 72 | **101** | 97 | +4 |
| ITFMATCH-26JUL05THUGRE | 98 | 3 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05PDACAS | 39 | 63 | **102** | 97 | +5 |
| ITFMATCH-26JUL05FARBRO | 64 | 39 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ | 23 | 83 | **106** | 97 | +9 |
| ITFMATCH-26JUL05BONBRA | 13 | 94 | **107** | 97 | +10 |
| ITFMATCH-26JUL05SALCON | 13 | 99 | **112** | 97 | +15 |
| ATPCHALLENGERMATCH-26JUL05BINPOL | 59 | 55 | **114** | 97 | +17 |
| ITFMATCH-26JUL05SABMIS | 81 | 34 | **115** | 97 | +18 |
| ATPCHALLENGERMATCH-26JUL05HUEMAR | 31 | 96 | **127** | 97 | +30 |
| ATPCHALLENGERMATCH-26JUL05RAMNEU | 36 | 98 | **134** | 97 | +37 |
| ATPCHALLENGERMATCH-26JUL05RYBTUN | 73 | 66 | **139** | 97 | +42 |

## PATTERNS (sub-B) — 20
- deep_neg_fv: KXITFWMATCH-26JUL05TRAABB-ABB {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05RAMNEU-RAM {"fill": 36, "age_min": 85, "mode": "SET_BELOW_FLOW(prints 37c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05WEHIFI-IFI {"fill": 11, "age_min": 85, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL05DITLEW-DIT {"fill": 31, "age_min": 85, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05KUZMAT-MAT {"fill": 5, "age_min": 85, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXITFWMATCH-26JUL05AITDAE-AIT {"entry_minus_fv_burst": -9.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05VALREJ-VAL {"fill": 62, "age_min": 84, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05CIZCAZ-CIZ {"fill": 23, "age_min": 84, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTAMATCH-26JUL05BENGAU-GAU {"fill": 50, "age_min": 82, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFMATCH-26JUL05SALCON-CON {"entry_minus_fv_burst": -10.0}
- half_arm_aging: KXITFMATCH-26JUL05SALCON-CON {"fill": 13, "age_min": 76, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05PEROPI-OPI {"entry_minus_fv_burst": -8.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05INGFEL-FEL {"fill": 72, "age_min": 69, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05HUEMAR-MAR {"fill": 31, "age_min": 57, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05RYBTUN-TUN {"fill": 73, "age_min": 49, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05HUANOC-HUA {"fill": 29, "age_min": 48, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL05TUBSOB-SOB {"fill": 24, "age_min": 44, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05PDACAS-CAS {"fill": 39, "age_min": 32, "mode": "SET_BELOW_FLOW(prints 4c above)", "emitted_et": "2026-07-05 12:04:43 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL05BONBRA-BRA {"fill": 13, "age_min": 31, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-05 12:04:43 PM ET"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05HIGZHU-HIG {"entry_minus_fv_burst": -8.5, "emitted_et": "2026-07-05 12:04:43 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
