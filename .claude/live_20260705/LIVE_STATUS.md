# LIVE VALIDATION — rolling status

- cycle 41 @ **2026-07-05 03:57:40 AM ET** | build `894728e` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 11839 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 4 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:32 | ITFWMATCH-26JUL04MAXSTE-MAX | ITF_W | underdog | 14 | 10 | +4 (place_cell) | — | pre | single |  | MIXED |
| 21:34 | ITFWMATCH-26JUL04BROKOI-KOI | ITF_W | underdog | 21 | 18 | +3 (place_cell) | — | pre | single |  | MIXED |
| 21:40 | ATPCHALLENGERMATCH-26JUL04LEGWIN-L | ATP_CHALL | ? | 80 | 83 | -3 (window_cell) | -34.0 | pre | single |  | EARNED |
| 03:09 | ATPCHALLENGERMATCH-26JUL05MARZAN-Z | ATP_CHALL | underdog | 6 | 11 | -5 (place_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 37 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 18, 'NO_FLOW': 16, 'FLOW_AT_LEVEL': 3} | repriceable now: true 7 / false 30 | **cumulative bid_grade lines: 70 (repriceable true 8 / false 62)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BERBOC-B | 22 | 6m | 0 | 22-25 | — | **NO_FLOW** | 22 |  |
| ATPCHALLENGERMATCH-26JUL05BERBOC-B | 75 | 57m | 1/79-79/10 | 75-79 | 4 | **FLOW_ABOVE** | 79 | REPRICEABLE→79 |
| ATPCHALLENGERMATCH-26JUL05BONSCH-S | 14 | 57m | 0 | 14-86 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BRAAGA-B | 14 | 57m | 0 | 14-86 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CANDEL-D | 14 | 58m | 0 | 14-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 5 | 57m | 1/8-8/9 | 5-8 | 3 | **FLOW_ABOVE** | 5 | flow above but bound 5c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 92 | 57m | 1/95-95/1 | 92-95 | 3 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05CRIRUB-C | 25 | 55m | 1/27-27/3 | 25-27 | 2 | **FLOW_ABOVE** | 24 | flow above but bound 24c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05CRIRUB-R | 73 | 57m | 8/76-76/155 | 75-75 | 3 | **FLOW_ABOVE** | 76 | REPRICEABLE→76 |
| ATPCHALLENGERMATCH-26JUL05DALARI-A | 6 | 57m | 0 | 6-7 | — | **NO_FLOW** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 93 | 55m | 0 | 93-94 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GUEROC-G | 14 | 57m | 0 | 14-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IEMBER-B | 95 | 57m | 1/96-96/1 | 95-96 | 1 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05IEMBER-I | 4 | 57m | 1/5-5/14 | 4-5 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05INGFEL-F | 75 | 57m | 1/77-77/1 | 75-76 | 2 | **FLOW_ABOVE** | 77 | REPRICEABLE→77 |
| ATPCHALLENGERMATCH-26JUL05INGFEL-I | 23 | 55m | 1/24-24/3 | 23-24 | 1 | **FLOW_ABOVE** | 21 | flow above but bound 21c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MARZAN-M | 91 | 47m | 1/95-95/1 | 94-95 | 4 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05NAGDOD-D | 14 | 57m | 0 | 14-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05NEUNED-N | 14 | 58m | 0 | 14-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PELALC-A | 18 | 6m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PELALC-P | 18 | 8m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PIELAR-L | 7 | 57m | 33/9-10/2246 | 8-8 | 2 | **FLOW_ABOVE** | 6 | flow above but bound 6c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PIELAR-P | 91 | 57m | 3/91-93/32 | 91-93 | 0 | **FLOW_AT_LEVEL** | 91 |  |
| ATPCHALLENGERMATCH-26JUL05POTANG-A | 47 | 15m | 0 | 47-49 | — | **NO_FLOW** | 51 |  |
| ATPCHALLENGERMATCH-26JUL05PRIROT-P | 70 | 42m | 6/70-71/59 | 70-71 | 0 | **FLOW_AT_LEVEL** | 71 |  |
| ATPCHALLENGERMATCH-26JUL05PRIROT-R | 31 | 30m | 2/31-33/247 | 31-32 | 0 | **FLOW_AT_LEVEL** | 30 |  |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 14 | 57m | 0 | 14-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SAIDIE-D | 17 | 8m | 0 | 17-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SAIDIE-S | 18 | 14m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-O | 80 | 57m | 1/81-81/1 | 80-81 | 1 | **FLOW_ABOVE** | 81 | REPRICEABLE→81 |
| ATPCHALLENGERMATCH-26JUL05SCIORA-S | 19 | 45m | 1/20-20/4 | 19-20 | 1 | **FLOW_ABOVE** | 17 | flow above but bound 17c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SEIMOL-M | 84 | 57m | 1/85-85/1 | 84-85 | 1 | **FLOW_ABOVE** | 85 | REPRICEABLE→85 |
| ATPCHALLENGERMATCH-26JUL05SEIMOL-S | 14 | 57m | 36/16-17/4187 | 15-15 | 2 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SQUGUI-G | 14 | 23m | 0 | 14-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05VILKOV-K | 47 | 12m | 3/48-48/133 | 47-49 | 1 | **FLOW_ABOVE** | 50 | REPRICEABLE→48 |
| ITFWMATCH-26JUL04BROKOI-BRO | 76 | 383m | 1350/80-99/350336 | 99-78 | 4 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 385m | 545/86-99/126759 | 99-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN | 80 | 1 | **81** | 97 | -16 |
| ITFWMATCH-26JUL04BROKOI | 21 | 78 | **99** | 97 | +2 |
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05MARZAN | 6 | 95 | **101** | 97 | +4 |

## PATTERNS (sub-B) — 5
- half_arm_aging: KXITFWMATCH-26JUL04MAXSTE-MAX {"fill": 14, "age_min": 385, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL04BROKOI-KOI {"fill": 21, "age_min": 383, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"entry_minus_fv_burst": -34.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"fill": 80, "age_min": 377, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARZAN-ZAN {"fill": 6, "age_min": 48, "mode": "SET_BELOW_FLOW(prints 4c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
