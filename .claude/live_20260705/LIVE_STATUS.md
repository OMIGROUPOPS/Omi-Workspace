# LIVE VALIDATION — rolling status

- cycle 84 @ **2026-07-06 01:04:45 AM ET** | build `957798c` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 14569 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 01:01:56 | **combined_over_goal** | KXITFWMATCH-26JUL06TODSAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 19 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:51 | ITFWMATCH-26JUL06PASCOP-PAS | ITF_W | underdog | 12 | 8 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:51 | ITFWMATCH-26JUL06LUCGAD-GAD | ITF_W | underdog | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:52 | ITFWMATCH-26JUL06PASCOP-COP | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:59 | ITFWMATCH-26JUL06BRESAF-BRE | ITF_W | leader | 63 | 61 | +2 (place_cell) | — | pre | single |  | PENDING |
| 00:04 | ITFWMATCH-26JUL06SIMCIR-CIR | ITF_W | underdog | 16 | 12 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:04 | ITFWMATCH-26JUL06SACLAZ-LAZ | ITF_W | underdog | 19 | 11 | +8 (place_cell) | — | pre | single |  | PENDING |
| 00:05 | ITFWMATCH-26JUL06HOSFEH-FEH | ITF_W | underdog | 61 | 63 | -2 (place_cell) | — | pre | single |  | PENDING |
| 00:06 | ITFWMATCH-26JUL06VAJRAM-VAJ | ITF_W | leader | 82 | 74 | +8 (place_cell) | — | pre | single |  | PENDING |
| 00:10 | ITFWMATCH-26JUL06LUCGAD-LUC | ITF_W | leader | 60 | 60 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:17 | ITFMATCH-26JUL06GENAZO-AZO | ITF_M | underdog | 16 | 9 | +7 (place_cell) | — | pre | single |  | PENDING |
| 00:22 | ITFMATCH-26JUL06VULCOU-COU | ITF_M | ? | 16 | 10 | +6 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:33 | ITFWMATCH-26JUL06WONIBR-IBR | ITF_W | leader | 65 | 52 | +13 (place_cell) | — | pre | single |  | PENDING |
| 00:33 | ITFWMATCH-26JUL06SIMCIR-SIM | ITF_W | leader | 81 | 81 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:34 | ITFWMATCH-26JUL06KARBAS-BAS | ITF_W | underdog | 26 | 26 | +0 (place_cell) | — | pre | single |  | PENDING |
| 00:47 | ITFWMATCH-26JUL06TODSAG-TOD | ITF_W | leader | 68 | 62 | +6 (place_cell) | — | pre | pair | 98 | PENDING |
| 00:55 | ITFWMATCH-26JUL06ZRNLUE-LUE | ITF_W | underdog | 69 | 6 | +63 (place_cell) | — | pre | single |  | PENDING |
| 01:00 | ITFMATCH-26JUL06VULCOU-VUL | ITF_M | leader | 81 | 80 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06BEASCO-SCO | ITF_M | underdog | 33 | 21 | +12 (place_cell) | — | pre | single |  | PENDING |
| 01:01 | ITFWMATCH-26JUL06TODSAG-SAG | ITF_W | ? | 30 | 25 | +5 (place_cell) | — | pre | pair | 98 | PENDING |

## RESTING BIDS — 39 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 19, 'NO_FLOW': 20} | repriceable now: true 6 / false 33 | **cumulative bid_grade lines: 950 (repriceable true 103 / false 847)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06CAMDE-DE | 39 | 4m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 64m | 11/8-9/547 | 6-8 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ATPCHALLENGERMATCH-26JUL06KRACRI-K | 92 | 23m | 2/94-94/52 | 92-94 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH-R | 40 | 4m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 40m | 2/43-43/33 | 40-43 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 4m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 24 | 65m | 2/26-26/54 | 24-25 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ATPCHALLENGERMATCH-26JUL06VILBOC-V | 75 | 13m | 1/77-77/6 | 75-77 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| ITFMATCH-26JUL06BEASCO-BEA | 62 | 0m | 0 | 64-66 | — | **NO_FLOW** | 64 |  |
| ITFMATCH-26JUL06ELDHAU-ELD | 59 | 31m | 1/69-69/1 | 59-69 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 30 | 27m | 0 | 30-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-GEN | 81 | 69m | 8/84-85/227 | 81-84 | 3 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06SALNGW-NGW | 39 | 68m | 3/45-45/76 | 39-45 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALNGW-SAL | 54 | 58m | 0 | 54-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 65m | 38/35-45/574 | 41-37 | 1 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06DZJMCK-DZJ | 65 | 26m | 0 | 65-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DZJMCK-MCK | 21 | 2m | 0 | 21-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 36 | 1m | 0 | 84-58 | — | **NO_FLOW** | 36 |  |
| ITFWMATCH-26JUL06IVAKUH-IVA | 61 | 2m | 0 | 61-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06IVAKUH-KUH | 37 | 2m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARBAS-KAR | 71 | 29m | 3/75-76/31 | 71-72 | 4 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 41m | 231/38-57/8768 | 44-41 | 1 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06LUKNOE-LUK | 68 | 29m | 1/74-74/29 | 68-74 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06LUKNOE-NOE | 25 | 33m | 0 | 25-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 21m | 178/11-17/7945 | 13-12 | 3 | **FLOW_ABOVE** | 12 | REPRICEABLE→11 |
| ITFWMATCH-26JUL06RICMIT-MIT | 7 | 3m | 0 | 7-9 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 64m | 47/79-86/383 | 80-82 | 1 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-CIR | 15 | 2m | 1/20-20/26 | 19-19 | 5 | **FLOW_ABOVE** | 16 | flow above but bound 16c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 58m | 35/20-31/850 | 25-20 | 5 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 13m | 10/27-31/97 | 25-20 | 12 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06VLADIL-VLA | 40 | 7m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06WONIBR-WON | 2 | 13m | 2/73-74/20 | 73-57 | 71 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 11 | 10m | 3/50-51/52 | 50-39 | 39 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06BOUKOT-B | 22 | 4m | 0 | 22-23 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BULSTR-B | 71 | 4m | 0 | 71-74 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BULSTR-S | 26 | 4m | 0 | 26-29 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 41 | 4m | 0 | 41-43 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MONPOP-M | 44 | 4m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MONPOP-P | 54 | 2m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06KARBAS | 26 | 72 | **98** | 97 | +1 |
| ITFMATCH-26JUL06BEASCO | 33 | 66 | **99** | 97 | +2 |
| ITFWMATCH-26JUL06BRESAF | 63 | 37 | **100** | 97 | +3 |
| ITFMATCH-26JUL06GENAZO | 16 | 84 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06SACLAZ | 19 | 82 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06VAJRAM | 82 | 20 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06ZRNLUE | 69 | 39 | **108** | 97 | +11 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ITFWMATCH-26JUL06WONIBR | 65 | 57 | **122** | 97 | +25 |

## PATTERNS (sub-B) — 7
- half_arm_aging: KXITFWMATCH-26JUL06BRESAF-BRE {"fill": 63, "age_min": 65, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06SACLAZ-LAZ {"fill": 19, "age_min": 61, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 59, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06VAJRAM-VAJ {"fill": 82, "age_min": 58, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFMATCH-26JUL06GENAZO-AZO {"fill": 16, "age_min": 47, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 32, "mode": "SET_BELOW_FLOW(prints 71c above)", "emitted_et": "2026-07-06 01:04:45 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL06KARBAS-BAS {"fill": 26, "age_min": 30, "mode": "SET_BELOW_FLOW(prints 4c above)", "emitted_et": "2026-07-06 01:04:45 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
