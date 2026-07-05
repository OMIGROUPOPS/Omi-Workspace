# LIVE VALIDATION — rolling status

- cycle 4 @ **2026-07-05 11:34:28 AM ET** | build `f84f6a1` | session boot 07-05 10:39 ET | log `live_v3_20260705.jsonl` | 10368 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 4 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 10:48:45 | **grace_breach** | KXITFMATCH-26JUL05SALCON-CON | fill 13c 5.2min past latch (grace 300s) |
| 11:10:44 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05TENBER | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 11:15:35 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL05KOBLEW | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 11:28:58 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05PEROPI | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_combined_over_goal.md**

## FILLS — 31 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10:39 | ITFWMATCH-26JUL05TRAABB-ABB | ITF_W | ? | 64 | 64 | +0 (window_cell) | -31.5 | pre | pair | 97 | EARNED |
| 10:39 | ATPCHALLENGERMATCH-26JUL05RAMNEU-R | ATP_CHALL | ? | 36 | 2 | +34 (window_cell) | — | pre | single |  | MIXED |
| 10:39 | ATPCHALLENGERMATCH-26JUL05WEHIFI-I | ATP_CHALL | ? | 11 | 8 | +3 (adopted_est) | 5.5 | pre | single |  | GIFT_CLASS |
| 10:39 | WTACHALLENGERMATCH-26JUL05DITLEW-D | WTA_CHALL | ? | 31 | 28 | +3 (adopted_est) | 25.5 | pre | single |  | GIFT_CLASS |
| 10:39 | ATPCHALLENGERMATCH-26JUL05KUZMAT-M | ATP_CHALL | ? | 5 | 2 | +3 (adopted_est) | -2.5 | pre | single |  | MIXED |
| 10:40 | ITFWMATCH-26JUL05AITDAE-AIT | ITF_W | underdog | 8 | 4 | +4 (place_cell) | -9.0 | pre | pair | 89 | EARNED |
| 10:41 | ATPCHALLENGERMATCH-26JUL05VALREJ-V | ATP_CHALL | leader | 62 | 71 | -9 (place_cell) | 11.5 | pre | single |  | GIFT_CLASS |
| 10:41 | ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | ATP_CHALL | underdog | 23 | 19 | +4 (place_cell) | — | pre | single |  | MIXED |
| 10:41 | ITFMATCH-26JUL05GELBRE-GEL | ITF_M | ? | 44 | 40 | +4 (window_cell) | — | pre | pair | 92 | MIXED |
| 10:42 | WTAMATCH-26JUL05BENGAU-GAU | WTA_MAIN | ? | 50 | 50 | +0 (adopted_est) | — | pre | single |  | PENDING |
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

## RESTING BIDS — 26 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 10, 'NO_FLOW': 12, 'FLOW_AT_LEVEL': 4} | repriceable now: true 4 / false 22 | **cumulative bid_grade lines: 682 (repriceable true 63 / false 619)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BANMAR-B | 65 | 54m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BANMAR-M | 33 | 54m | 7/33-37/340 | 33-37 | 0 | **FLOW_AT_LEVEL** | 33 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 91 | 37m | 37/97-99/5852 | 99-99 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-E | 65 | 54m | 1/67-67/10 | 65-67 | 2 | **FLOW_ABOVE** | 67 | REPRICEABLE→67 |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-J | 33 | 54m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GANZIN-G | 28 | 54m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GANZIN-Z | 70 | 54m | 1/72-72/10 | 71-72 | 2 | **FLOW_ABOVE** | 72 | REPRICEABLE→72 |
| ATPCHALLENGERMATCH-26JUL05GOIAND-A | 68 | 22m | 3/69-69/105 | 68-69 | 1 | **FLOW_ABOVE** | 73 | REPRICEABLE→69 |
| ATPCHALLENGERMATCH-26JUL05GOIAND-G | 31 | 18m | 0 | 31-32 | — | **NO_FLOW** | 28 |  |
| ATPCHALLENGERMATCH-26JUL05MORMAR-M | 39 | 2m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05MORMAR-M | 59 | 19m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PDACAS-P | 58 | 1m | 0 | 61-62 | — | **NO_FLOW** | 58 |  |
| ATPCHALLENGERMATCH-26JUL05POPCAS-C | 6 | 24m | 0 | 6-7 | — | **NO_FLOW** | 4 |  |
| ATPCHALLENGERMATCH-26JUL05POPCAS-P | 93 | 22m | 6/94-95/132 | 93-95 | 1 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05POTANG-P | 50 | 55m | 6/55-56/186 | 55-56 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PRICOU-P | 47 | 3m | 9/39-59/621 | 35-43 | -8 | **FLOW_AT_LEVEL** | 47 |  |
| ATPCHALLENGERMATCH-26JUL05RAMNEU-N | 61 | 55m | 17/98-99/2359 | 99-98 | 37 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SANROD-R | 82 | 24m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SANROD-S | 17 | 24m | 0 | 17-18 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SUNBAR-B | 57 | 5m | 20/76-83/3872 | 81-62 | 19 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05TENBER-B | 55 | 15m | 23/71-80/3875 | 76-71 | 16 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05GELBRE-GEL | 46 | 41m | 131/27-62/10005 | 30-27 | -19 | **FLOW_AT_LEVEL** | 40 |  |
| ITFMATCH-26JUL05SABMIS-SAB | 21 | 1m | 0 | 21-90 | — | **NO_FLOW** | 81 |  |
| WTACHALLENGERMATCH-26JUL05KOBLEW-L | 8 | 19m | 101/3-22/8975 | 12-3 | -5 | **FLOW_AT_LEVEL** | 8 |  |
| WTACHALLENGERMATCH-26JUL05YAMOVC-O | 28 | 54m | 1/30-30/45 | 28-30 | 2 | **FLOW_ABOVE** | 27 | flow above but bound 27c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05YAMOVC-Y | 70 | 54m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05VALREJ | 62 | 4 | **66** | 97 | -31 |
| ITFWMATCH-26JUL05TUBSOB | 24 | 66 | **90** | 97 | -7 |
| ATPCHALLENGERMATCH-26JUL05PDACAS | 39 | 62 | **101** | 97 | +4 |
| ITFMATCH-26JUL05BONBRA | 13 | 91 | **104** | 97 | +7 |
| ATPCHALLENGERMATCH-26JUL05HUEMAR | 31 | 74 | **105** | 97 | +8 |
| ATPCHALLENGERMATCH-26JUL05RYBTUN | 73 | 33 | **106** | 97 | +9 |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ | 23 | 85 | **108** | 97 | +11 |
| ATPCHALLENGERMATCH-26JUL05HUANOC | 29 | 82 | **111** | 97 | +14 |
| ITFMATCH-26JUL05SALCON | 13 | 99 | **112** | 97 | +15 |
| ATPCHALLENGERMATCH-26JUL05RAMNEU | 36 | 98 | **134** | 97 | +37 |

## PATTERNS (sub-B) — 13
- deep_neg_fv: KXITFWMATCH-26JUL05TRAABB-ABB {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05RAMNEU-RAM {"fill": 36, "age_min": 55, "mode": "SET_BELOW_FLOW(prints 37c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05WEHIFI-IFI {"fill": 11, "age_min": 55, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL05DITLEW-DIT {"fill": 31, "age_min": 55, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05KUZMAT-MAT {"fill": 5, "age_min": 55, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXITFWMATCH-26JUL05AITDAE-AIT {"entry_minus_fv_burst": -9.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05VALREJ-VAL {"fill": 62, "age_min": 53, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05CIZCAZ-CIZ {"fill": 23, "age_min": 53, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTAMATCH-26JUL05BENGAU-GAU {"fill": 50, "age_min": 52, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFMATCH-26JUL05SALCON-CON {"entry_minus_fv_burst": -10.0}
- half_arm_aging: KXITFMATCH-26JUL05SALCON-CON {"fill": 13, "age_min": 46, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05PEROPI-OPI {"entry_minus_fv_burst": -8.0, "emitted_et": "2026-07-05 11:34:28 AM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05INGFEL-FEL {"fill": 72, "age_min": 39, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
