# LIVE VALIDATION — rolling status

- cycle 83 @ **2026-07-06 12:54:37 AM ET** | build `170e138` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 8932 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 15 graded (session)
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
| 00:22 | ITFMATCH-26JUL06VULCOU-COU | ITF_M | ? | 16 | 10 | +6 (place_cell) | — | pre | single |  | PENDING |
| 00:33 | ITFWMATCH-26JUL06WONIBR-IBR | ITF_W | leader | 65 | 52 | +13 (place_cell) | — | pre | single |  | PENDING |
| 00:33 | ITFWMATCH-26JUL06SIMCIR-SIM | ITF_W | leader | 81 | 81 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:34 | ITFWMATCH-26JUL06KARBAS-BAS | ITF_W | underdog | 26 | 26 | +0 (place_cell) | — | pre | single |  | PENDING |
| 00:47 | ITFWMATCH-26JUL06TODSAG-TOD | ITF_W | leader | 68 | 62 | +6 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 30 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 15, 'NO_FLOW': 13, 'FLOW_AT_LEVEL': 2} | repriceable now: true 6 / false 24 | **cumulative bid_grade lines: 926 (repriceable true 101 / false 825)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 54m | 10/9-9/541 | 6-9 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ATPCHALLENGERMATCH-26JUL06KRACRI-K | 92 | 13m | 0 | 92-94 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 30m | 2/43-43/33 | 40-43 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 24 | 54m | 2/26-26/54 | 24-26 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ATPCHALLENGERMATCH-26JUL06VILBOC-V | 75 | 2m | 0 | 75-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BEASCO-BEA | 65 | 1m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BEASCO-SCO | 33 | 11m | 2/37-40/120 | 33-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFMATCH-26JUL06ELDHAU-ELD | 59 | 21m | 0 | 59-69 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 30 | 17m | 0 | 30-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-GEN | 81 | 59m | 7/85-85/226 | 81-84 | 4 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06SALNGW-NGW | 39 | 58m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALNGW-SAL | 54 | 48m | 0 | 54-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VULCOU-VUL | 81 | 33m | 10/85-93/121 | 82-85 | 4 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 55m | 31/40-45/503 | 41-43 | 6 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06DZJMCK-DZJ | 65 | 16m | 0 | 65-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 10 | 11m | 0 | 84-77 | — | **NO_FLOW** | 36 |  |
| ITFWMATCH-26JUL06KARBAS-KAR | 71 | 19m | 3/75-76/31 | 71-72 | 4 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 31m | 157/41-57/7705 | 44-41 | 4 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06LUKNOE-LUK | 68 | 19m | 0 | 68-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUKNOE-NOE | 25 | 23m | 0 | 25-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 11m | 110/11-17/3850 | 11-12 | 3 | **FLOW_ABOVE** | 12 | REPRICEABLE→11 |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 54m | 42/79-86/347 | 80-82 | 1 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 20m | 51/16-23/2225 | 17-19 | 2 | **FLOW_ABOVE** | 16 | REPRICEABLE→16 |
| ITFWMATCH-26JUL06TODSAG-SAG | 29 | 7m | 1/29-29/0 | 29-33 | 0 | **FLOW_AT_LEVEL** | 29 |  |
| ITFWMATCH-26JUL06TODSAG-SAG | 27 | 1m | 0 | 29-33 | — | **NO_FLOW** | 29 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 48m | 30/20-31/803 | 25-20 | 5 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 3m | 5/28-31/50 | 25-20 | 13 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06WONIBR-WON | 2 | 3m | 0 | 56-57 | — | **NO_FLOW** | 32 |  |
| ITFWMATCH-26JUL06ZRNLUE-LUE | 69 | 16m | 2/69-80/1 | 69-80 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 20 | 25m | 1/36-36/1 | 20-33 | 16 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06KARBAS | 26 | 72 | **98** | 97 | +1 |
| ITFMATCH-26JUL06GENAZO | 16 | 84 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06SACLAZ | 19 | 82 | **101** | 97 | +4 |
| ITFMATCH-26JUL06VULCOU | 16 | 85 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06TODSAG | 68 | 33 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06VAJRAM | 82 | 20 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06BRESAF | 63 | 43 | **106** | 97 | +9 |
| ITFWMATCH-26JUL06WONIBR | 65 | 57 | **122** | 97 | +25 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 77 | **138** | 97 | +41 |

## PATTERNS (sub-B) — 6
- half_arm_aging: KXITFWMATCH-26JUL06BRESAF-BRE {"fill": 63, "age_min": 55, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06SACLAZ-LAZ {"fill": 19, "age_min": 50, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 49, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06VAJRAM-VAJ {"fill": 82, "age_min": 48, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFMATCH-26JUL06GENAZO-AZO {"fill": 16, "age_min": 37, "mode": "SET_BELOW_FLOW(prints 4c above)", "emitted_et": "2026-07-06 12:54:37 AM ET"}
- half_arm_aging: KXITFMATCH-26JUL06VULCOU-COU {"fill": 16, "age_min": 33, "mode": "SET_BELOW_FLOW(prints 4c above)", "emitted_et": "2026-07-06 12:54:37 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
