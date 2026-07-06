# LIVE VALIDATION — rolling status

- cycle 79 @ **2026-07-06 12:14:13 AM ET** | build `8bddae5` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 3187 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 9 graded (session)
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

## RESTING BIDS — 22 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 12, 'NO_FLOW': 10} | repriceable now: true 6 / false 16 | **cumulative bid_grade lines: 878 (repriceable true 93 / false 785)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 14m | 2/9-9/57 | 6-9 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 24 | 14m | 1/26-26/0 | 24-26 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFMATCH-26JUL06BEASCO-SCO | 31 | 1m | 0 | 31-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 19m | 1/20-20/4 | 16-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL06GENAZO-GEN | 81 | 18m | 0 | 81-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALNGW-NGW | 39 | 17m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALNGW-SAL | 54 | 7m | 0 | 54-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VULCOU-COU | 16 | 19m | 2/20-20/22 | 16-17 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL06VULCOU-VUL | 83 | 23m | 1/87-87/1 | 83-87 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→87 |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 15m | 9/40-42/104 | 41-40 | 6 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06HOSFEH-HOS | 36 | 6m | 0 | 36-60 | — | **NO_FLOW** | 36 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 36 | 3m | 0 | 40-41 | — | **NO_FLOW** | 37 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 7 | 11m | 47/10-13/6842 | 10-12 | 3 | **FLOW_ABOVE** | 12 | REPRICEABLE→10 |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 14m | 21/82-85/140 | 81-83 | 4 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-SIM | 81 | 10m | 15/82-84/275 | 84-87 | 1 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-SIM | 81 | 10m | 15/82-84/275 | 84-87 | 1 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06TODSAG-SAG | 31 | 19m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TODSAG-TOD | 67 | 3m | 0 | 67-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 8m | 2/20-20/12 | 16-20 | 5 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06VAJRAM-RAM | 14 | 2m | 1/20-20/3 | 16-20 | 6 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ZRNLUE-LUE | 64 | 1m | 0 | 65-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 17 | 1m | 0 | 18-35 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06SACLAZ | 19 | 83 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06VAJRAM | 82 | 20 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06BRESAF | 63 | 40 | **103** | 97 | +6 |
| ITFWMATCH-26JUL06SIMCIR | 16 | 87 | **103** | 97 | +6 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 60 | **121** | 97 | +24 |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
