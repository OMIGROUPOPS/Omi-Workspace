# LIVE VALIDATION — rolling status

- cycle 2 @ **2026-07-05 11:14:21 AM ET** | build `abc51f1` | session boot 07-05 10:39 ET | log `live_v3_20260705.jsonl` | 6187 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 10:48:45 | **grace_breach** | KXITFMATCH-26JUL05SALCON-CON | fill 13c 5.2min past latch (grace 300s) |
| 11:10:44 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05TENBER | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 22 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10:39 | ITFWMATCH-26JUL05TRAABB-ABB | ITF_W | ? | 64 | 64 | +0 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 10:39 | ATPCHALLENGERMATCH-26JUL05RAMNEU-R | ATP_CHALL | ? | 36 | 2 | +34 (window_cell) | — | pre | single |  | MIXED |
| 10:39 | ATPCHALLENGERMATCH-26JUL05WEHIFI-I | ATP_CHALL | ? | 11 | 8 | +3 (adopted_est) | 5.5 | pre | single |  | GIFT_CLASS |
| 10:39 | WTACHALLENGERMATCH-26JUL05DITLEW-D | WTA_CHALL | ? | 31 | 28 | +3 (adopted_est) | 25.5 | pre | single |  | GIFT_CLASS |
| 10:39 | ATPCHALLENGERMATCH-26JUL05KUZMAT-M | ATP_CHALL | ? | 5 | 2 | +3 (adopted_est) | -2.5 | pre | single |  | MIXED |
| 10:40 | ITFWMATCH-26JUL05AITDAE-AIT | ITF_W | underdog | 8 | 4 | +4 (place_cell) | — | pre | pair | 89 | MIXED |
| 10:41 | ATPCHALLENGERMATCH-26JUL05VALREJ-V | ATP_CHALL | leader | 62 | 71 | -9 (place_cell) | 11.5 | pre | single |  | GIFT_CLASS |
| 10:41 | ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | ATP_CHALL | underdog | 23 | 19 | +4 (place_cell) | — | pre | single |  | MIXED |
| 10:41 | ITFMATCH-26JUL05GELBRE-GEL | ITF_M | ? | 44 | 40 | +4 (window_cell) | — | pre | pair | 92 | MIXED |
| 10:42 | WTAMATCH-26JUL05BENGAU-GAU | WTA_MAIN | ? | 50 | 50 | +0 (adopted_est) | — | pre | single |  | PENDING |
| 10:48 | ITFMATCH-26JUL05SALCON-CON | ITF_M | ? | 13 | 29 | -16 (window_cell) | -10.0 | 5.2 | single |  | EARNED |
| 10:53 | ITFMATCH-26JUL05GELBRE-BRE | ITF_M | ? | 48 | 56 | -8 (window_cell) | — | pre | pair | 92 | EARNED |
| 10:53 | ATPCHALLENGERMATCH-26JUL05PEROPI-O | ATP_CHALL | ? | 25 | 22 | +3 (window_cell) | — | pre | single |  | MIXED |
| 10:55 | ATPCHALLENGERMATCH-26JUL05INGFEL-F | ATP_CHALL | ? | 72 | 72 | +0 (adopted_est) | — | pre | single |  | PENDING |
| 11:02 | ITFWMATCH-26JUL05TRAABB-TRA | ITF_W | ? | 33 | 29 | +4 (window_cell) | — | pre | pair | 97 | MIXED |
| 11:07 | ATPCHALLENGERMATCH-26JUL05HUEMAR-M | ATP_CHALL | ? | 31 | 28 | +3 (window_cell) | — | pre | single |  | MIXED |
| 11:07 | ATPCHALLENGERMATCH-26JUL05TENBER-T | ATP_CHALL | ? | 42 | 39 | +3 (window_cell) | — | pre | pair | 99 | MIXED |
| 11:08 | WTACHALLENGERMATCH-26JUL05KOBLEW-L | WTA_CHALL | ? | 10 | 8 | +2 (window_cell) | — | pre | single |  | MIXED |
| 11:10 | ATPCHALLENGERMATCH-26JUL05TENBER-B | ATP_CHALL | ? | 57 | 60 | -3 (window_cell) | — | pre | pair | 99 | MIXED |
| 11:12 | ITFWMATCH-26JUL05AITDAE-DAE | ITF_W | ? | 81 | 94 | -13 (window_cell) | — | pre | pair | 89 | MIXED |
| 11:12 | ATPCHALLENGERMATCH-26JUL05SUNBAR-B | ATP_CHALL | ? | 57 | 59 | -2 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 11:12 | ATPCHALLENGERMATCH-26JUL05PRICOU-C | ATP_CHALL | ? | 50 | 53 | -3 (window_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 24 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 14, 'FLOW_AT_LEVEL': 2} | repriceable now: true 2 / false 22 | **cumulative bid_grade lines: 667 (repriceable true 59 / false 608)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BANMAR-B | 65 | 34m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BANMAR-M | 33 | 34m | 7/33-37/340 | 33-37 | 0 | **FLOW_AT_LEVEL** | 33 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 91 | 17m | 27/97-99/3786 | 98-99 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-E | 65 | 34m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-J | 33 | 34m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GANZIN-G | 28 | 34m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GANZIN-Z | 70 | 34m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GOIAND-A | 68 | 2m | 0 | 68-69 | — | **NO_FLOW** | 73 |  |
| ATPCHALLENGERMATCH-26JUL05GOIAND-G | 29 | 2m | 0 | 29-32 | — | **NO_FLOW** | 28 |  |
| ATPCHALLENGERMATCH-26JUL05MORMAR-M | 4 | 2m | 0 | 4-95 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PDACAS-C | 39 | 13m | 1/40-40/50 | 39-40 | 1 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PDACAS-P | 61 | 13m | 0 | 61-62 | — | **NO_FLOW** | 62 |  |
| ATPCHALLENGERMATCH-26JUL05POPCAS-C | 6 | 4m | 0 | 6-7 | — | **NO_FLOW** | 4 |  |
| ATPCHALLENGERMATCH-26JUL05POPCAS-P | 93 | 2m | 6/94-95/132 | 93-95 | 1 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05POTANG-P | 50 | 34m | 3/55-55/116 | 55-56 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05RAMNEU-N | 61 | 34m | 17/98-99/2359 | 99-98 | 37 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SANROD-R | 82 | 4m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SANROD-S | 17 | 4m | 0 | 17-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL05GELBRE-GEL | 46 | 21m | 61/35-62/4649 | 50-52 | -11 | **FLOW_AT_LEVEL** | 40 |  |
| ITFMATCH-26JUL05SABMIS-SAB | 18 | 11m | 0 | 18-91 | — | **NO_FLOW** | 81 |  |
| ITFWMATCH-26JUL05AITDAE-AIT | 13 | 2m | 41/20-23/3508 | 22-21 | 7 | **FLOW_ABOVE** | 5 | flow above but bound 5c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05TUBSOB-SOB | 25 | 34m | 112/29-81/2919 | 39-40 | 4 | **FLOW_ABOVE** | 30 | REPRICEABLE→29 |
| WTACHALLENGERMATCH-26JUL05YAMOVC-O | 28 | 34m | 1/30-30/45 | 28-30 | 2 | **FLOW_ABOVE** | 27 | flow above but bound 27c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05YAMOVC-Y | 70 | 34m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05VALREJ | 62 | 33 | **95** | 97 | -2 |
| WTACHALLENGERMATCH-26JUL05KOBLEW | 10 | 88 | **98** | 97 | +1 |
| ATPCHALLENGERMATCH-26JUL05SUNBAR | 57 | 42 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL05PRICOU | 50 | 53 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL05PEROPI | 25 | 79 | **104** | 97 | +7 |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ | 23 | 84 | **107** | 97 | +10 |
| ITFMATCH-26JUL05SALCON | 13 | 98 | **111** | 97 | +14 |
| ATPCHALLENGERMATCH-26JUL05HUEMAR | 31 | 80 | **111** | 97 | +14 |
| ATPCHALLENGERMATCH-26JUL05RAMNEU | 36 | 98 | **134** | 97 | +37 |

## PATTERNS (sub-B) — 8
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05RAMNEU-RAM {"fill": 36, "age_min": 35, "mode": "SET_BELOW_FLOW(prints 37c above)", "emitted_et": "2026-07-05 11:14:21 AM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05WEHIFI-IFI {"fill": 11, "age_min": 35, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-05 11:14:21 AM ET"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL05DITLEW-DIT {"fill": 31, "age_min": 35, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-05 11:14:21 AM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05KUZMAT-MAT {"fill": 5, "age_min": 35, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05VALREJ-VAL {"fill": 62, "age_min": 33, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05CIZCAZ-CIZ {"fill": 23, "age_min": 33, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-05 11:14:21 AM ET"}
- half_arm_aging: KXWTAMATCH-26JUL05BENGAU-GAU {"fill": 50, "age_min": 32, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-05 11:14:21 AM ET"}
- deep_neg_fv: KXITFMATCH-26JUL05SALCON-CON {"entry_minus_fv_burst": -10.0}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
