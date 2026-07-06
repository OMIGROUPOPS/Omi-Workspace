# LIVE VALIDATION — rolling status

- cycle 80 @ **2026-07-06 12:24:18 AM ET** | build `c0976ff` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 4140 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 11 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:51 | ITFWMATCH-26JUL06PASCOP-PAS | ITF_W | underdog | 12 | 8 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:51 | ITFWMATCH-26JUL06LUCGAD-GAD | ITF_W | underdog | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:52 | ITFWMATCH-26JUL06PASCOP-COP | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:59 | ITFWMATCH-26JUL06BRESAF-BRE | ITF_W | leader | 63 | 61 | +2 (place_cell) | — | pre | single |  | PENDING |
| 00:04 | ITFWMATCH-26JUL06SIMCIR-CIR | ITF_W | underdog | 16 | 12 | +4 (place_cell) | — | pre | single |  | PENDING |
| 00:04 | ITFWMATCH-26JUL06SACLAZ-LAZ | ITF_W | underdog | 19 | 11 | +8 (place_cell) | — | pre | single |  | PENDING |
| 00:05 | ITFWMATCH-26JUL06HOSFEH-FEH | ITF_W | underdog | 61 | 63 | -2 (place_cell) | — | pre | single |  | PENDING |
| 00:06 | ITFWMATCH-26JUL06VAJRAM-VAJ | ITF_W | leader | 82 | 74 | +8 (place_cell) | — | pre | single |  | PENDING |
| 00:10 | ITFWMATCH-26JUL06LUCGAD-LUC | ITF_W | leader | 60 | 60 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:17 | ITFMATCH-26JUL06GENAZO-AZO | ITF_M | underdog | 16 | 9 | +7 (place_cell) | — | pre | single |  | PENDING |
| 00:22 | ITFMATCH-26JUL06VULCOU-COU | ITF_M | ? | 16 | 10 | +6 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 21 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 14, 'NO_FLOW': 7} | repriceable now: true 5 / false 16 | **cumulative bid_grade lines: 889 (repriceable true 96 / false 793)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 24m | 3/9-9/161 | 6-9 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 24 | 24m | 1/26-26/0 | 24-26 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFMATCH-26JUL06BEASCO-SCO | 32 | 7m | 0 | 32-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-GEN | 81 | 28m | 5/85-85/101 | 81-85 | 4 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06SALNGW-NGW | 39 | 27m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALNGW-SAL | 54 | 17m | 0 | 54-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VULCOU-VUL | 81 | 2m | 0 | 82-87 | — | **NO_FLOW** | 81 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 25m | 9/40-42/104 | 41-40 | 6 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06DZJMCK-DZJ | 5 | 1m | 0 | 56-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 36 | 16m | 1/41-41/6 | 40-57 | 5 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 1m | 11/44-51/295 | 45-41 | 7 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 2m | 8/11-16/559 | 11-12 | 3 | **FLOW_ABOVE** | 12 | REPRICEABLE→11 |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 24m | 25/79-85/198 | 79-83 | 1 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-SIM | 81 | 20m | 43/82-90/637 | 84-84 | 1 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-SIM | 81 | 20m | 43/82-90/637 | 84-84 | 1 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06TODSAG-SAG | 31 | 29m | 1/35-35/8 | 31-35 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ITFWMATCH-26JUL06TODSAG-TOD | 67 | 13m | 3/70-71/34 | 67-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 18m | 4/20-20/25 | 16-20 | 5 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06VAJRAM-RAM | 14 | 12m | 3/20-20/16 | 16-20 | 6 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ZRNLUE-LUE | 67 | 1m | 0 | 67-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 19 | 1m | 0 | 19-37 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06SIMCIR | 16 | 84 | **100** | 97 | +3 |
| ITFMATCH-26JUL06GENAZO | 16 | 85 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06SACLAZ | 19 | 83 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06VAJRAM | 82 | 20 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06BRESAF | 63 | 40 | **103** | 97 | +6 |
| ITFMATCH-26JUL06VULCOU | 16 | 87 | **103** | 97 | +6 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 57 | **118** | 97 | +21 |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
