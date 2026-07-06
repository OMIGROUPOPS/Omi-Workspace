# LIVE VALIDATION — rolling status

- cycle 81 @ **2026-07-06 12:34:23 AM ET** | build `97c93f3` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 5701 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 13 graded (session)
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

## RESTING BIDS — 27 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 12, 'NO_FLOW': 15} | repriceable now: true 5 / false 22 | **cumulative bid_grade lines: 903 (repriceable true 97 / false 806)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 34m | 8/9-9/526 | 6-9 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 9m | 0 | 40-43 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 24 | 34m | 2/26-26/54 | 24-26 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFMATCH-26JUL06BEASCO-SCO | 32 | 17m | 2/36-36/7 | 32-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL06ELDHAU-ELD | 59 | 1m | 0 | 59-69 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 28 | 1m | 0 | 29-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-GEN | 81 | 39m | 5/85-85/101 | 81-85 | 4 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06SALNGW-NGW | 39 | 37m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALNGW-SAL | 54 | 27m | 0 | 54-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VULCOU-VUL | 81 | 12m | 0 | 82-85 | — | **NO_FLOW** | 81 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 35m | 14/40-43/253 | 41-42 | 6 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06DZJMCK-DZJ | 62 | 3m | 0 | 62-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 12 | 0m | 0 | 68-77 | — | **NO_FLOW** | 36 |  |
| ITFWMATCH-26JUL06KARBAS-BAS | 26 | 3m | 0 | 26-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARBAS-KAR | 69 | 3m | 0 | 69-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 11m | 56/44-57/1133 | 48-41 | 7 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06LUKNOE-LUK | 67 | 1m | 0 | 68-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUKNOE-NOE | 25 | 3m | 0 | 25-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 9 | 5m | 24/15-16/3728 | 14-12 | 6 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 34m | 25/79-85/198 | 81-83 | 1 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06TODSAG-SAG | 31 | 39m | 1/35-35/8 | 31-35 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ITFWMATCH-26JUL06TODSAG-TOD | 67 | 23m | 4/70-72/35 | 67-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 28m | 10/20-22/208 | 16-20 | 5 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06VAJRAM-RAM | 14 | 22m | 9/20-22/199 | 16-20 | 6 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06WONIBR-WON | 11 | 1m | 0 | 16-90 | — | **NO_FLOW** | 32 |  |
| ITFWMATCH-26JUL06ZRNLUE-LUE | 68 | 4m | 0 | 68-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 20 | 5m | 0 | 20-37 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL06GENAZO | 16 | 85 | **101** | 97 | +4 |
| ITFMATCH-26JUL06VULCOU | 16 | 85 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06SACLAZ | 19 | 83 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06VAJRAM | 82 | 20 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06BRESAF | 63 | 42 | **105** | 97 | +8 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 77 | **138** | 97 | +41 |
| ITFWMATCH-26JUL06WONIBR | 65 | 90 | **155** | 97 | +58 |

## PATTERNS (sub-B) — 2
- half_arm_aging: KXITFWMATCH-26JUL06BRESAF-BRE {"fill": 63, "age_min": 35, "mode": "SET_BELOW_FLOW(prints 6c above)", "emitted_et": "2026-07-06 12:34:23 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL06SACLAZ-LAZ {"fill": 19, "age_min": 30, "mode": "SET_BELOW_FLOW(prints 1c above)", "emitted_et": "2026-07-06 12:34:23 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
