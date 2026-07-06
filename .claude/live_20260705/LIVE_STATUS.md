# LIVE VALIDATION — rolling status

- cycle 82 @ **2026-07-06 12:44:31 AM ET** | build `e3f5c17` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 7156 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 14 graded (session)
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

## RESTING BIDS — 28 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 14, 'NO_FLOW': 14} | repriceable now: true 6 / false 22 | **cumulative bid_grade lines: 917 (repriceable true 100 / false 817)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 44m | 8/9-9/526 | 6-9 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ATPCHALLENGERMATCH-26JUL06KRACRI-K | 92 | 3m | 0 | 92-94 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 19m | 0 | 40-43 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 24 | 44m | 2/26-26/54 | 24-26 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFMATCH-26JUL06BEASCO-SCO | 33 | 1m | 2/37-40/120 | 33-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFMATCH-26JUL06ELDHAU-ELD | 59 | 11m | 0 | 59-69 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 30 | 7m | 0 | 30-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-GEN | 81 | 49m | 7/85-85/226 | 81-85 | 4 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06SALNGW-NGW | 39 | 48m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALNGW-SAL | 54 | 37m | 0 | 54-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VULCOU-VUL | 81 | 22m | 10/85-93/121 | 82-85 | 4 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 45m | 25/40-45/430 | 41-43 | 6 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06DZJMCK-DZJ | 65 | 5m | 0 | 65-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 10 | 0m | 0 | 84-77 | — | **NO_FLOW** | 36 |  |
| ITFWMATCH-26JUL06KARBAS-KAR | 71 | 9m | 3/75-76/31 | 71-72 | 4 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 21m | 114/43-57/5717 | 45-41 | 6 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06LUKNOE-LUK | 68 | 9m | 0 | 68-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUKNOE-NOE | 25 | 13m | 0 | 25-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 1m | 8/13-16/85 | 11-12 | 5 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 44m | 40/79-86/343 | 82-83 | 1 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 10m | 28/16-23/487 | 18-19 | 2 | **FLOW_ABOVE** | 16 | REPRICEABLE→16 |
| ITFWMATCH-26JUL06TODSAG-SAG | 31 | 50m | 1/35-35/8 | 31-34 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ITFWMATCH-26JUL06TODSAG-TOD | 68 | 7m | 4/72-75/39 | 68-69 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→72 |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 38m | 25/20-29/753 | 28-20 | 5 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 1m | 0 | 28-20 | — | **NO_FLOW** | 15 |  |
| ITFWMATCH-26JUL06WONIBR-WON | 2 | 0m | 0 | 54-57 | — | **NO_FLOW** | 32 |  |
| ITFWMATCH-26JUL06ZRNLUE-LUE | 69 | 5m | 0 | 69-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 20 | 15m | 0 | 20-36 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06KARBAS | 26 | 72 | **98** | 97 | +1 |
| ITFMATCH-26JUL06GENAZO | 16 | 85 | **101** | 97 | +4 |
| ITFMATCH-26JUL06VULCOU | 16 | 85 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06SACLAZ | 19 | 83 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06VAJRAM | 82 | 20 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06BRESAF | 63 | 43 | **106** | 97 | +9 |
| ITFWMATCH-26JUL06WONIBR | 65 | 57 | **122** | 97 | +25 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 77 | **138** | 97 | +41 |

## PATTERNS (sub-B) — 4
- half_arm_aging: KXITFWMATCH-26JUL06BRESAF-BRE {"fill": 63, "age_min": 45, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06SACLAZ-LAZ {"fill": 19, "age_min": 40, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 39, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-06 12:44:31 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL06VAJRAM-VAJ {"fill": 82, "age_min": 38, "mode": "SET_BELOW_FLOW(prints 5c above)", "emitted_et": "2026-07-06 12:44:31 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
