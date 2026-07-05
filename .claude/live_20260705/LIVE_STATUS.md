# LIVE VALIDATION — rolling status

- cycle 45 @ **2026-07-05 04:38:04 AM ET** | build `5a1f81c` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 13737 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 11 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:32 | ITFWMATCH-26JUL04MAXSTE-MAX | ITF_W | underdog | 14 | 10 | +4 (place_cell) | — | pre | single |  | MIXED |
| 21:34 | ITFWMATCH-26JUL04BROKOI-KOI | ITF_W | underdog | 21 | 18 | +3 (place_cell) | — | pre | single |  | MIXED |
| 21:40 | ATPCHALLENGERMATCH-26JUL04LEGWIN-L | ATP_CHALL | ? | 80 | 83 | -3 (window_cell) | -34.0 | pre | single |  | EARNED |
| 03:09 | ATPCHALLENGERMATCH-26JUL05MARZAN-Z | ATP_CHALL | underdog | 6 | 11 | -5 (place_cell) | — | pre | single |  | EARNED |
| 04:03 | ATPCHALLENGERMATCH-26JUL05PIELAR-P | ATP_CHALL | leader | 91 | 91 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 04:04 | ATPCHALLENGERMATCH-26JUL05VILKOV-K | ATP_CHALL | underdog | 47 | 44 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 04:09 | ATPCHALLENGERMATCH-26JUL05CRIRUB-R | ATP_CHALL | leader | 72 | 73 | -1 (place_cell) | — | pre | single |  | MIXED |
| 04:10 | ATPCHALLENGERMATCH-26JUL05PRIROT-P | ATP_CHALL | leader | 70 | 70 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 04:10 | ATPCHALLENGERMATCH-26JUL05SEIMOL-M | ATP_CHALL | leader | 84 | 84 | +0 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 04:11 | ATPCHALLENGERMATCH-26JUL05VILKOV-V | ATP_CHALL | ? | 50 | 53 | -3 (window_cell) | — | pre | pair | 97 | MIXED |
| 04:11 | ATPCHALLENGERMATCH-26JUL05SEIMOL-S | ATP_CHALL | underdog | 11 | 11 | +0 (place_cell) | — | pre | pair | 95 | EARNED |

## RESTING BIDS — 46 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 14, 'NO_FLOW': 32} | repriceable now: true 5 / false 41 | **cumulative bid_grade lines: 101 (repriceable true 11 / false 90)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BERBOC-B | 22 | 46m | 1/25-25/13 | 22-25 | 3 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05BERBOC-B | 75 | 97m | 2/79-79/11 | 75-78 | 4 | **FLOW_ABOVE** | 79 | REPRICEABLE→79 |
| ATPCHALLENGERMATCH-26JUL05BONSCH-S | 14 | 98m | 0 | 14-90 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BRAAGA-B | 14 | 98m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CAMBID-B | 15 | 38m | 0 | 16-17 | — | **NO_FLOW** | 14 |  |
| ATPCHALLENGERMATCH-26JUL05CAMBID-C | 82 | 19m | 0 | 82-84 | — | **NO_FLOW** | 84 |  |
| ATPCHALLENGERMATCH-26JUL05CANDEL-D | 14 | 98m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 6 | 35m | 0 | 6-7 | — | **NO_FLOW** | 5 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 93 | 10m | 0 | 93-95 | — | **NO_FLOW** | 94 |  |
| ATPCHALLENGERMATCH-26JUL05CRIRUB-C | 24 | 1m | 3/50-56/47 | 56-29 | 26 | **FLOW_ABOVE** | 24 | flow above but bound 24c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05DALARI-A | 6 | 97m | 0 | 6-7 | — | **NO_FLOW** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 93 | 95m | 1/94-94/74 | 93-94 | 1 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05GUEROC-G | 14 | 98m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IEMBER-B | 95 | 97m | 1/96-96/1 | 95-96 | 1 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05IEMBER-I | 4 | 97m | 2/5-6/264 | 4-5 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05INGFEL-F | 75 | 97m | 1/77-77/1 | 75-76 | 2 | **FLOW_ABOVE** | 77 | REPRICEABLE→77 |
| ATPCHALLENGERMATCH-26JUL05INGFEL-I | 24 | 36m | 0 | 24-25 | — | **NO_FLOW** | 21 |  |
| ATPCHALLENGERMATCH-26JUL05MARDUR-D | 63 | 10m | 0 | 63-64 | — | **NO_FLOW** | 64 |  |
| ATPCHALLENGERMATCH-26JUL05MARDUR-M | 34 | 16m | 0 | 34-36 | — | **NO_FLOW** | 33 |  |
| ATPCHALLENGERMATCH-26JUL05MARZAN-M | 91 | 88m | 1/95-95/1 | 94-95 | 4 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05NAGDOD-D | 14 | 98m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05NEUNED-N | 14 | 98m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PELALC-A | 18 | 46m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PELALC-P | 18 | 48m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PIELAR-L | 5 | 25m | 201/7-21/40927 | 19-6 | 2 | **FLOW_ABOVE** | 6 | REPRICEABLE→6 |
| ATPCHALLENGERMATCH-26JUL05POTANG-A | 47 | 56m | 0 | 47-49 | — | **NO_FLOW** | 51 |  |
| ATPCHALLENGERMATCH-26JUL05PRIROT-R | 27 | 28m | 0 | 32-32 | — | **NO_FLOW** | 27 |  |
| ATPCHALLENGERMATCH-26JUL05RATRAH-R | 58 | 17m | 0 | 58-60 | — | **NO_FLOW** | 61 |  |
| ATPCHALLENGERMATCH-26JUL05RATRAH-R | 38 | 14m | 0 | 38-39 | — | **NO_FLOW** | 36 |  |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 14 | 97m | 0 | 14-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SAIDIE-D | 18 | 36m | 0 | 18-78 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SAIDIE-S | 21 | 17m | 0 | 21-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 21 | 38m | 0 | 21-23 | — | **NO_FLOW** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-O | 80 | 97m | 1/81-81/1 | 80-82 | 1 | **FLOW_ABOVE** | 81 | REPRICEABLE→81 |
| ATPCHALLENGERMATCH-26JUL05SCIORA-S | 19 | 85m | 1/20-20/4 | 19-21 | 1 | **FLOW_ABOVE** | 17 | flow above but bound 17c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ-M | 4 | 27m | 11/5-5/842 | 4-5 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SQUGUI-G | 14 | 63m | 0 | 14-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SQUGUI-S | 14 | 36m | 0 | 14-54 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL04BROKOI-BRO | 76 | 423m | 1350/80-99/350336 | 99-78 | 4 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 425m | 545/86-99/126759 | 99-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05HERVAI-H | 81 | 38m | 0 | 83-84 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05HERVAI-V | 16 | 36m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05KUDBOU-B | 5 | 38m | 0 | 5-6 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05KUDBOU-K | 93 | 38m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05MONGIM-G | 26 | 38m | 0 | 26-29 | — | **NO_FLOW** | 26 |  |
| WTACHALLENGERMATCH-26JUL05MONGIM-M | 71 | 38m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN | 80 | 1 | **81** | 97 | -16 |
| ATPCHALLENGERMATCH-26JUL05PIELAR | 91 | 6 | **97** | 97 | +0 |
| ITFWMATCH-26JUL04BROKOI | 21 | 78 | **99** | 97 | +2 |
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05MARZAN | 6 | 95 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05CRIRUB | 72 | 29 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05PRIROT | 70 | 32 | **102** | 97 | +5 |

## PATTERNS (sub-B) — 6
- half_arm_aging: KXITFWMATCH-26JUL04MAXSTE-MAX {"fill": 14, "age_min": 425, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL04BROKOI-KOI {"fill": 21, "age_min": 423, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"entry_minus_fv_burst": -34.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"fill": 80, "age_min": 418, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARZAN-ZAN {"fill": 6, "age_min": 89, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05PIELAR-PIE {"fill": 91, "age_min": 34, "mode": "SET_BELOW_FLOW(prints 2c above)", "emitted_et": "2026-07-05 04:38:04 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
