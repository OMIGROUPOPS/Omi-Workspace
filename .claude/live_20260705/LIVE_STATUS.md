# LIVE VALIDATION — rolling status

- cycle 10 @ **2026-07-05 12:35:00 PM ET** | build `0f4e800` | session boot 07-05 10:39 ET | log `live_v3_20260705.jsonl` | 22003 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 6 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 10:48:45 | **grace_breach** | KXITFMATCH-26JUL05SALCON-CON | fill 13c 5.2min past latch (grace 300s) |
| 11:10:44 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05TENBER | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 11:15:35 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL05KOBLEW | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 11:28:58 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05PEROPI | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 12:05:34 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05HUANOC | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 12:07:26 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05KAMVAN | pair combined 100c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 54 graded (session)
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
| 10:41 | ITFMATCH-26JUL05GELBRE-GEL | ITF_M | ? | 44 | 40 | +4 (window_cell) | 18.0 | pre | pair | 92 | GIFT_CLASS |
| 10:42 | WTAMATCH-26JUL05BENGAU-GAU | WTA_MAIN | ? | 50 | 50 | +0 (adopted_est) | 0.5 | pre | single |  | MIXED |
| 10:48 | ITFMATCH-26JUL05SALCON-CON | ITF_M | ? | 13 | 29 | -16 (window_cell) | -10.0 | 5.2 | single |  | EARNED |
| 10:53 | ITFMATCH-26JUL05GELBRE-BRE | ITF_M | ? | 48 | 56 | -8 (window_cell) | -25.0 | pre | pair | 92 | EARNED |
| 10:53 | ATPCHALLENGERMATCH-26JUL05PEROPI-O | ATP_CHALL | ? | 25 | 22 | +3 (window_cell) | -8.0 | pre | pair | 98 | EARNED |
| 10:55 | ATPCHALLENGERMATCH-26JUL05INGFEL-F | ATP_CHALL | ? | 72 | 72 | +0 (adopted_est) | — | pre | single |  | PENDING |
| 11:02 | ITFWMATCH-26JUL05TRAABB-TRA | ITF_W | ? | 33 | 29 | +4 (window_cell) | 29.0 | pre | pair | 97 | GIFT_CLASS |
| 11:07 | ATPCHALLENGERMATCH-26JUL05HUEMAR-M | ATP_CHALL | ? | 31 | 28 | +3 (window_cell) | — | pre | single |  | MIXED |
| 11:07 | ATPCHALLENGERMATCH-26JUL05TENBER-T | ATP_CHALL | ? | 42 | 39 | +3 (window_cell) | — | pre | pair | 99 | MIXED |
| 11:08 | WTACHALLENGERMATCH-26JUL05KOBLEW-L | WTA_CHALL | ? | 10 | 8 | +2 (window_cell) | — | pre | pair | 99 | MIXED |
| 11:10 | ATPCHALLENGERMATCH-26JUL05TENBER-B | ATP_CHALL | ? | 57 | 60 | -3 (window_cell) | — | pre | pair | 99 | MIXED |
| 11:12 | ITFWMATCH-26JUL05AITDAE-DAE | ITF_W | ? | 81 | 94 | -13 (window_cell) | 2.5 | pre | pair | 89 | MIXED |
| 11:12 | ATPCHALLENGERMATCH-26JUL05SUNBAR-B | ATP_CHALL | ? | 57 | 59 | -2 (window_cell) | -31.0 | pre | pair | 97 | EARNED |
| 11:12 | ATPCHALLENGERMATCH-26JUL05PRICOU-C | ATP_CHALL | ? | 50 | 53 | -3 (window_cell) | — | pre | pair | 97 | MIXED |
| 11:15 | ATPCHALLENGERMATCH-26JUL05SUNBAR-S | ATP_CHALL | ? | 40 | 41 | -1 (window_cell) | 30.0 | pre | pair | 97 | EARNED |
| 11:15 | ATPCHALLENGERMATCH-26JUL05RYBTUN-T | ATP_CHALL | ? | 73 | 75 | -2 (window_cell) | 61.0 | pre | single |  | GIFT_CLASS |
| 11:15 | WTACHALLENGERMATCH-26JUL05KOBLEW-K | WTA_CHALL | ? | 89 | 91 | -2 (window_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 11:16 | ATPCHALLENGERMATCH-26JUL05HUANOC-H | ATP_CHALL | ? | 29 | 29 | +0 (window_cell) | 12.0 | pre | pair | 98 | EARNED |
| 11:16 | ATPCHALLENGERMATCH-26JUL05PRICOU-P | ATP_CHALL | ? | 47 | 54 | -7 (window_cell) | — | pre | pair | 97 | EARNED |
| 11:21 | ITFWMATCH-26JUL05TUBSOB-SOB | ITF_W | ? | 24 | 30 | -6 (window_cell) | 9.0 | pre | single |  | EARNED |
| 11:28 | ATPCHALLENGERMATCH-26JUL05PEROPI-P | ATP_CHALL | ? | 73 | 75 | -2 (window_cell) | 9.0 | pre | pair | 98 | GIFT_CLASS |
| 11:32 | ATPCHALLENGERMATCH-26JUL05PDACAS-C | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 11:33 | ITFMATCH-26JUL05BONBRA-BRA | ITF_M | ? | 13 | 10 | +3 (window_cell) | — | pre | single |  | MIXED |
| 11:37 | ATPCHALLENGERMATCH-26JUL05HIGZHU-H | ATP_CHALL | ? | 38 | 38 | +0 (window_cell) | -8.5 | pre | pair | 96 | EARNED |
| 11:43 | ATPCHALLENGERMATCH-26JUL05HIGZHU-Z | ATP_CHALL | ? | 58 | 61 | -3 (window_cell) | 9.5 | pre | pair | 96 | GIFT_CLASS |
| 11:45 | ATPCHALLENGERMATCH-26JUL05POTANG-P | ATP_CHALL | ? | 50 | 50 | +0 (fill_est) | -15.0 | pre | single |  | EARNED |
| 11:45 | ATPCHALLENGERMATCH-26JUL05KAMVAN-K | ATP_CHALL | ? | 13 | 10 | +3 (adopted_est) | 2.0 | pre | pair | 100 | MIXED |
| 11:47 | ITFMATCH-26JUL05SABMIS-SAB | ITF_M | underdog | 81 | 14 | +67 (place_cell) | 15.0 | pre | single |  | GIFT_CLASS |
| 11:48 | ATPCHALLENGERMATCH-26JUL05BINPOL-B | ATP_CHALL | ? | 59 | 61 | -2 (window_cell) | -31.0 | pre | pair | 97 | EARNED |
| 11:54 | ATPCHALLENGERMATCH-26JUL05GOIAND-G | ATP_CHALL | underdog | 31 | 26 | +5 (place_cell) | — | pre | single |  | MIXED |
| 11:56 | ATPCHALLENGERMATCH-26JUL05GANZIN-G | ATP_CHALL | underdog | 29 | 25 | +4 (place_cell) | — | pre | single |  | MIXED |
| 12:01 | ITFMATCH-26JUL05XUXCHE-CHE | ITF_M | underdog | 2 | 1 | +1 (place_cell) | — | pre | single |  | MIXED |
| 12:01 | ITFMATCH-26JUL05FARBRO-FAR | ITF_M | ? | 64 | 64 | +0 (place_cell) | 17.0 | pre | pair | 96 | GIFT_CLASS |
| 12:03 | ITFMATCH-26JUL05THUGRE-THU | ITF_M | leader | 98 | 98 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 12:05 | ATPCHALLENGERMATCH-26JUL05HUANOC-N | ATP_CHALL | ? | 69 | 71 | -2 (window_cell) | — | pre | pair | 98 | GIFT_CLASS |
| 12:07 | ATPCHALLENGERMATCH-26JUL05KAMVAN-V | ATP_CHALL | ? | 87 | 87 | +0 (adopted_est) | — | pre | pair | 100 | PENDING |
| 12:08 | ATPMATCH-26JUL05SINMOC-SIN | ATP_MAIN | ? | 96 | 96 | +0 (adopted_est) | — | pre | single |  | PENDING |
| 12:12 | ITFMATCH-26JUL05FARBRO-BRO | ITF_M | ? | 32 | 30 | +2 (window_cell) | -18.0 | pre | pair | 96 | EARNED |
| 12:13 | ITFWMATCH-26JUL05KULVAN-KUL | ITF_W | ? | 55 | 60 | -5 (window_cell) | — | pre | pair | 94 | MIXED |
| 12:13 | ATPCHALLENGERMATCH-26JUL05PDACAS-P | ATP_CHALL | leader | 58 | 61 | -3 (place_cell) | — | pre | pair | 97 | MIXED |
| 12:16 | ATPCHALLENGERMATCH-26JUL05IVAGAN-G | ATP_CHALL | ? | 22 | 23 | -1 (window_cell) | — | pre | single |  | EARNED |
| 12:17 | ATPCHALLENGERMATCH-26JUL05MARJUN-J | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | single |  | MIXED |
| 12:17 | ATPCHALLENGERMATCH-26JUL05BINPOL-P | ATP_CHALL | ? | 38 | 38 | +0 (window_cell) | 20.0 | pre | pair | 97 | EARNED |
| 12:21 | ATPCHALLENGERMATCH-26JUL05MARHAI-H | ATP_CHALL | ? | 96 | 94 | +2 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 12:21 | ATPCHALLENGERMATCH-26JUL05MORMAR-M | ATP_CHALL | leader | 59 | 59 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 12:24 | ITFWMATCH-26JUL05KULVAN-VAN | ITF_W | ? | 39 | 43 | -4 (window_cell) | — | pre | pair | 94 | EARNED |

## RESTING BIDS — 35 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 20, 'NO_FLOW': 9, 'FLOW_AT_LEVEL': 6} | repriceable now: true 5 / false 30 | **cumulative bid_grade lines: 721 (repriceable true 68 / false 653)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BANMAR-B | 65 | 114m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BANMAR-M | 33 | 114m | 7/33-37/340 | 33-37 | 0 | **FLOW_AT_LEVEL** | 33 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 91 | 97m | 39/97-99/5892 | 99-99 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-E | 65 | 114m | 1/67-67/10 | 65-66 | 2 | **FLOW_ABOVE** | 67 | REPRICEABLE→67 |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-J | 33 | 114m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GANZIN-Z | 68 | 38m | 1/74-74/2 | 71-73 | 6 | **FLOW_ABOVE** | 68 | flow above but bound 68c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05GOIAND-A | 66 | 41m | 3/69-71/1203 | 68-69 | 3 | **FLOW_ABOVE** | 66 | flow above but bound 66c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05HUANOC-H | 28 | 6m | 73/42-64/9479 | 62-60 | 14 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05IMAMIL-I | 41 | 44m | 0 | 41-43 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IMAMIL-M | 58 | 44m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05KOZMAY-K | 46 | 44m | 1/47-47/150 | 46-47 | 1 | **FLOW_ABOVE** | 44 | flow above but bound 44c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05KOZMAY-M | 53 | 44m | 3/53-53/205 | 53-54 | 0 | **FLOW_AT_LEVEL** | 54 |  |
| ATPCHALLENGERMATCH-26JUL05MARJUN-M | 58 | 17m | 1/62-62/10 | 59-62 | 4 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MONHUR-H | 4 | 14m | 2/5-5/74 | 4-5 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MONHUR-M | 95 | 14m | 1/96-96/1 | 95-96 | 1 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MORMAR-M | 38 | 13m | 0 | 43-46 | — | **NO_FLOW** | 38 |  |
| ATPCHALLENGERMATCH-26JUL05NUNCLA-C | 57 | 14m | 1/60-60/10 | 57-60 | 3 | **FLOW_ABOVE** | 60 | REPRICEABLE→60 |
| ATPCHALLENGERMATCH-26JUL05NUNCLA-N | 39 | 14m | 0 | 40-43 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PAPMBI-M | 65 | 14m | 1/68-68/10 | 65-68 | 3 | **FLOW_ABOVE** | 68 | REPRICEABLE→68 |
| ATPCHALLENGERMATCH-26JUL05PAPMBI-P | 33 | 14m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05POPCAS-C | 6 | 84m | 0 | 6-7 | — | **NO_FLOW** | 4 |  |
| ATPCHALLENGERMATCH-26JUL05POPCAS-P | 93 | 83m | 9/94-96/714 | 93-95 | 1 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05PRICOU-P | 47 | 64m | 96/1-59/22582 | 1-1 | -46 | **FLOW_AT_LEVEL** | 47 |  |
| ATPCHALLENGERMATCH-26JUL05RAMNEU-N | 61 | 115m | 17/98-99/2359 | 99-98 | 37 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SANROD-R | 82 | 85m | 3/82-85/10 | 82-85 | 0 | **FLOW_AT_LEVEL** | 85 |  |
| ATPCHALLENGERMATCH-26JUL05SANROD-S | 17 | 85m | 2/18-19/56 | 17-19 | 1 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05TENBER-B | 55 | 76m | 176/64-96/24583 | 95-96 | 9 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05GELBRE-GEL | 46 | 101m | 836/7-62/54900 | 16-9 | -39 | **FLOW_AT_LEVEL** | 40 |  |
| ITFMATCH-26JUL05XUXCHE-XUX | 95 | 33m | 183/97-99/12747 | 99-98 | 2 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05KULVAN-KUL | 58 | 2m | 5/60-63/139 | 60-60 | 2 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05KOBLEW-L | 8 | 79m | 445/1-22/57946 | 19-20 | -7 | **FLOW_AT_LEVEL** | 8 |  |
| WTACHALLENGERMATCH-26JUL05SMIJAR-J | 20 | 43m | 1/21-21/18 | 20-21 | 1 | **FLOW_ABOVE** | 18 | flow above but bound 18c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05SMIJAR-S | 81 | 43m | 0 | 81-82 | — | **NO_FLOW** | 81 |  |
| WTACHALLENGERMATCH-26JUL05YAMOVC-O | 28 | 114m | 1/30-30/45 | 28-30 | 2 | **FLOW_ABOVE** | 27 | flow above but bound 27c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05YAMOVC-Y | 70 | 114m | 2/72-72/37 | 70-72 | 2 | **FLOW_ABOVE** | 72 | REPRICEABLE→72 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL05TUBSOB | 24 | 1 | **25** | 97 | -72 |
| ATPCHALLENGERMATCH-26JUL05VALREJ | 62 | 4 | **66** | 97 | -31 |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ | 23 | 70 | **93** | 97 | -4 |
| ATPCHALLENGERMATCH-26JUL05IVAGAN | 22 | 74 | **96** | 97 | -1 |
| ITFMATCH-26JUL05THUGRE | 98 | 1 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL05GOIAND | 31 | 69 | **100** | 97 | +3 |
| ITFMATCH-26JUL05XUXCHE | 2 | 98 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05MARJUN | 39 | 62 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05GANZIN | 29 | 73 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05MORMAR | 59 | 46 | **105** | 97 | +8 |
| ITFMATCH-26JUL05BONBRA | 13 | 93 | **106** | 97 | +9 |
| ITFMATCH-26JUL05SALCON | 13 | 99 | **112** | 97 | +15 |
| ATPCHALLENGERMATCH-26JUL05MARHAI | 96 | 17 | **113** | 97 | +16 |
| ITFMATCH-26JUL05SABMIS | 81 | 44 | **125** | 97 | +28 |
| ATPCHALLENGERMATCH-26JUL05HUEMAR | 31 | 99 | **130** | 97 | +33 |
| ATPCHALLENGERMATCH-26JUL05RAMNEU | 36 | 98 | **134** | 97 | +37 |
| ATPCHALLENGERMATCH-26JUL05RYBTUN | 73 | 80 | **153** | 97 | +56 |

## PATTERNS (sub-B) — 29
- deep_neg_fv: KXITFWMATCH-26JUL05TRAABB-ABB {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05RAMNEU-RAM {"fill": 36, "age_min": 115, "mode": "SET_BELOW_FLOW(prints 37c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05WEHIFI-IFI {"fill": 11, "age_min": 115, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL05DITLEW-DIT {"fill": 31, "age_min": 115, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05KUZMAT-MAT {"fill": 5, "age_min": 115, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXITFWMATCH-26JUL05AITDAE-AIT {"entry_minus_fv_burst": -9.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05VALREJ-VAL {"fill": 62, "age_min": 114, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05CIZCAZ-CIZ {"fill": 23, "age_min": 114, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTAMATCH-26JUL05BENGAU-GAU {"fill": 50, "age_min": 112, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFMATCH-26JUL05SALCON-CON {"entry_minus_fv_burst": -10.0}
- half_arm_aging: KXITFMATCH-26JUL05SALCON-CON {"fill": 13, "age_min": 106, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFMATCH-26JUL05GELBRE-BRE {"entry_minus_fv_burst": -25.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05PEROPI-OPI {"entry_minus_fv_burst": -8.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05INGFEL-FEL {"fill": 72, "age_min": 99, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05HUEMAR-MAR {"fill": 31, "age_min": 87, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05SUNBAR-BAR {"entry_minus_fv_burst": -31.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05RYBTUN-TUN {"fill": 73, "age_min": 79, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL05TUBSOB-SOB {"fill": 24, "age_min": 74, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL05BONBRA-BRA {"fill": 13, "age_min": 62, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05HIGZHU-HIG {"entry_minus_fv_burst": -8.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05POTANG-POT {"entry_minus_fv_burst": -15.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05POTANG-POT {"fill": 50, "age_min": 50, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL05SABMIS-SAB {"fill": 81, "age_min": 48, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05BINPOL-BIN {"entry_minus_fv_burst": -31.0, "emitted_et": "2026-07-05 12:35:00 PM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05GOIAND-GOI {"fill": 31, "age_min": 41, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05GANZIN-GAN {"fill": 29, "age_min": 38, "mode": "SET_BELOW_FLOW(prints 6c above)", "emitted_et": "2026-07-05 12:35:00 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL05XUXCHE-CHE {"fill": 2, "age_min": 33, "mode": "SET_BELOW_FLOW(prints 2c above)", "emitted_et": "2026-07-05 12:35:00 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL05THUGRE-THU {"fill": 98, "age_min": 31, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-05 12:35:00 PM ET"}
- deep_neg_fv: KXITFMATCH-26JUL05FARBRO-BRO {"entry_minus_fv_burst": -18.0, "emitted_et": "2026-07-05 12:35:00 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
