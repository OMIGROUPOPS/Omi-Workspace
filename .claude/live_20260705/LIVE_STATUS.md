# LIVE VALIDATION — rolling status

- cycle 42 @ **2026-07-05 04:07:45 AM ET** | build `55feae3` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 12625 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 6 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:32 | ITFWMATCH-26JUL04MAXSTE-MAX | ITF_W | underdog | 14 | 10 | +4 (place_cell) | — | pre | single |  | MIXED |
| 21:34 | ITFWMATCH-26JUL04BROKOI-KOI | ITF_W | underdog | 21 | 18 | +3 (place_cell) | — | pre | single |  | MIXED |
| 21:40 | ATPCHALLENGERMATCH-26JUL04LEGWIN-L | ATP_CHALL | ? | 80 | 83 | -3 (window_cell) | -34.0 | pre | single |  | EARNED |
| 03:09 | ATPCHALLENGERMATCH-26JUL05MARZAN-Z | ATP_CHALL | underdog | 6 | 11 | -5 (place_cell) | — | pre | single |  | EARNED |
| 04:03 | ATPCHALLENGERMATCH-26JUL05PIELAR-P | ATP_CHALL | leader | 91 | 91 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 04:04 | ATPCHALLENGERMATCH-26JUL05VILKOV-K | ATP_CHALL | underdog | 47 | 44 | +3 (place_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 45 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 15, 'NO_FLOW': 28, 'FLOW_AT_LEVEL': 2} | repriceable now: true 7 / false 38 | **cumulative bid_grade lines: 84 (repriceable true 9 / false 75)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BERBOC-B | 22 | 16m | 0 | 22-26 | — | **NO_FLOW** | 22 |  |
| ATPCHALLENGERMATCH-26JUL05BERBOC-B | 75 | 67m | 2/79-79/11 | 75-79 | 4 | **FLOW_ABOVE** | 79 | REPRICEABLE→79 |
| ATPCHALLENGERMATCH-26JUL05BONSCH-S | 14 | 68m | 0 | 14-90 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BRAAGA-B | 14 | 67m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CAMBID-B | 15 | 7m | 0 | 16-17 | — | **NO_FLOW** | 14 |  |
| ATPCHALLENGERMATCH-26JUL05CANDEL-D | 14 | 68m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 6 | 5m | 0 | 6-7 | — | **NO_FLOW** | 5 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 92 | 67m | 1/95-95/1 | 92-95 | 3 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05CRIRUB-C | 25 | 65m | 14/27-34/224 | 25-30 | 2 | **FLOW_ABOVE** | 24 | flow above but bound 24c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05CRIRUB-R | 73 | 67m | 9/76-77/156 | 75-75 | 3 | **FLOW_ABOVE** | 76 | REPRICEABLE→76 |
| ATPCHALLENGERMATCH-26JUL05DALARI-A | 6 | 67m | 0 | 6-7 | — | **NO_FLOW** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 93 | 65m | 0 | 93-94 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GUEROC-G | 14 | 68m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IEMBER-B | 95 | 67m | 1/96-96/1 | 95-96 | 1 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05IEMBER-I | 4 | 67m | 1/5-5/14 | 4-5 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05INGFEL-F | 75 | 67m | 1/77-77/1 | 75-76 | 2 | **FLOW_ABOVE** | 77 | REPRICEABLE→77 |
| ATPCHALLENGERMATCH-26JUL05INGFEL-I | 24 | 6m | 0 | 24-25 | — | **NO_FLOW** | 21 |  |
| ATPCHALLENGERMATCH-26JUL05MARZAN-M | 91 | 57m | 1/95-95/1 | 94-95 | 4 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05NAGDOD-D | 14 | 68m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05NEUNED-N | 14 | 68m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PELALC-A | 18 | 16m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PELALC-P | 18 | 18m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PIELAR-L | 5 | 4m | 57/9-19/1931 | 7-8 | 4 | **FLOW_ABOVE** | 6 | REPRICEABLE→6 |
| ATPCHALLENGERMATCH-26JUL05POTANG-A | 47 | 25m | 0 | 47-49 | — | **NO_FLOW** | 51 |  |
| ATPCHALLENGERMATCH-26JUL05PRIROT-P | 70 | 52m | 6/70-71/59 | 70-71 | 0 | **FLOW_AT_LEVEL** | 71 |  |
| ATPCHALLENGERMATCH-26JUL05PRIROT-R | 31 | 40m | 2/31-33/247 | 32-32 | 0 | **FLOW_AT_LEVEL** | 30 |  |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 14 | 67m | 0 | 14-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SAIDIE-D | 18 | 6m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SAIDIE-S | 18 | 24m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 21 | 7m | 0 | 21-23 | — | **NO_FLOW** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-O | 80 | 67m | 1/81-81/1 | 80-81 | 1 | **FLOW_ABOVE** | 81 | REPRICEABLE→81 |
| ATPCHALLENGERMATCH-26JUL05SCIORA-S | 19 | 55m | 1/20-20/4 | 19-22 | 1 | **FLOW_ABOVE** | 17 | flow above but bound 17c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SEIMOL-M | 84 | 67m | 2/85-85/2 | 84-85 | 1 | **FLOW_ABOVE** | 85 | REPRICEABLE→85 |
| ATPCHALLENGERMATCH-26JUL05SEIMOL-S | 14 | 67m | 36/16-17/4187 | 14-15 | 2 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SQUGUI-G | 14 | 33m | 0 | 14-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SQUGUI-S | 14 | 6m | 0 | 14-54 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05VILKOV-V | 50 | 2m | 0 | 53-53 | — | **NO_FLOW** | 50 |  |
| ITFWMATCH-26JUL04BROKOI-BRO | 76 | 393m | 1350/80-99/350336 | 99-78 | 4 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 395m | 545/86-99/126759 | 99-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05HERVAI-H | 81 | 7m | 0 | 83-84 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05HERVAI-V | 16 | 6m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05KUDBOU-B | 5 | 7m | 0 | 5-6 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05KUDBOU-K | 93 | 7m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05MONGIM-G | 26 | 7m | 0 | 26-29 | — | **NO_FLOW** | 26 |  |
| WTACHALLENGERMATCH-26JUL05MONGIM-M | 71 | 7m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN | 80 | 1 | **81** | 97 | -16 |
| ITFWMATCH-26JUL04BROKOI | 21 | 78 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL05PIELAR | 91 | 8 | **99** | 97 | +2 |
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05VILKOV | 47 | 53 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05MARZAN | 6 | 95 | **101** | 97 | +4 |

## PATTERNS (sub-B) — 5
- half_arm_aging: KXITFWMATCH-26JUL04MAXSTE-MAX {"fill": 14, "age_min": 395, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL04BROKOI-KOI {"fill": 21, "age_min": 393, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"entry_minus_fv_burst": -34.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"fill": 80, "age_min": 388, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARZAN-ZAN {"fill": 6, "age_min": 58, "mode": "SET_BELOW_FLOW(prints 4c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
