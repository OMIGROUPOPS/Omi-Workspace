# LIVE VALIDATION — rolling status

- cycle 48 @ **2026-07-05 05:08:23 AM ET** | build `bf7774a` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 15580 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 05:08:08 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05SCHDE | pair combined 99c > goal 97c |

## FILLS — 16 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:32 | ITFWMATCH-26JUL04MAXSTE-MAX | ITF_W | underdog | 14 | 10 | +4 (place_cell) | — | pre | single |  | MIXED |
| 21:34 | ITFWMATCH-26JUL04BROKOI-KOI | ITF_W | underdog | 21 | 18 | +3 (place_cell) | — | pre | single |  | MIXED |
| 21:40 | ATPCHALLENGERMATCH-26JUL04LEGWIN-L | ATP_CHALL | ? | 80 | 83 | -3 (window_cell) | -34.0 | pre | single |  | EARNED |
| 03:09 | ATPCHALLENGERMATCH-26JUL05MARZAN-Z | ATP_CHALL | underdog | 6 | 11 | -5 (place_cell) | — | pre | single |  | EARNED |
| 04:03 | ATPCHALLENGERMATCH-26JUL05PIELAR-P | ATP_CHALL | leader | 91 | 91 | +0 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 04:04 | ATPCHALLENGERMATCH-26JUL05VILKOV-K | ATP_CHALL | underdog | 47 | 44 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 04:09 | ATPCHALLENGERMATCH-26JUL05CRIRUB-R | ATP_CHALL | leader | 72 | 73 | -1 (place_cell) | — | pre | single |  | MIXED |
| 04:10 | ATPCHALLENGERMATCH-26JUL05PRIROT-P | ATP_CHALL | leader | 70 | 70 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 04:10 | ATPCHALLENGERMATCH-26JUL05SEIMOL-M | ATP_CHALL | leader | 84 | 84 | +0 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 04:11 | ATPCHALLENGERMATCH-26JUL05VILKOV-V | ATP_CHALL | ? | 50 | 53 | -3 (window_cell) | — | pre | pair | 97 | MIXED |
| 04:11 | ATPCHALLENGERMATCH-26JUL05SEIMOL-S | ATP_CHALL | underdog | 11 | 11 | +0 (place_cell) | — | pre | pair | 95 | EARNED |
| 04:44 | ATPCHALLENGERMATCH-26JUL05PIELAR-L | ATP_CHALL | underdog | 5 | 5 | +0 (place_cell) | — | pre | pair | 96 | EARNED |
| 04:48 | WTACHALLENGERMATCH-26JUL05KUDBOU-B | WTA_CHALL | underdog | 5 | 2 | +3 (place_cell) | — | pre | single |  | MIXED |
| 05:06 | WTACHALLENGERMATCH-26JUL05HERVAI-H | WTA_CHALL | leader | 81 | 83 | -2 (place_cell) | — | pre | single |  | MIXED |
| 05:07 | ATPCHALLENGERMATCH-26JUL05SCHDE-DE | ATP_CHALL | leader | 75 | 75 | +0 (place_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 05:08 | ATPCHALLENGERMATCH-26JUL05SCHDE-SC | ATP_CHALL | underdog | 24 | 20 | +4 (place_cell) | — | pre | pair | 99 | MIXED |

## RESTING BIDS — 53 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 20, 'NO_FLOW': 33} | repriceable now: true 7 / false 46 | **cumulative bid_grade lines: 123 (repriceable true 14 / false 109)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BERBOC-B | 22 | 76m | 8/25-26/136 | 22-25 | 3 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05BERBOC-B | 75 | 127m | 7/78-80/450 | 75-79 | 3 | **FLOW_ABOVE** | 79 | REPRICEABLE→78 |
| ATPCHALLENGERMATCH-26JUL05BONSCH-S | 15 | 19m | 0 | 15-90 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BRAAGA-B | 14 | 128m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CAMBID-B | 15 | 68m | 0 | 16-18 | — | **NO_FLOW** | 14 |  |
| ATPCHALLENGERMATCH-26JUL05CAMBID-C | 82 | 49m | 0 | 82-84 | — | **NO_FLOW** | 84 |  |
| ATPCHALLENGERMATCH-26JUL05CANDEL-C | 14 | 8m | 0 | 14-86 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CANDEL-D | 15 | 19m | 0 | 15-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 6 | 65m | 0 | 6-7 | — | **NO_FLOW** | 5 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 93 | 40m | 0 | 93-95 | — | **NO_FLOW** | 94 |  |
| ATPCHALLENGERMATCH-26JUL05CRIRUB-C | 25 | 6m | 10/37-45/1654 | 64-29 | 12 | **FLOW_ABOVE** | 24 | flow above but bound 24c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05DALARI-A | 6 | 127m | 0 | 6-7 | — | **NO_FLOW** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 93 | 126m | 1/94-94/74 | 93-94 | 1 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05DIACEC-D | 65 | 8m | 3/67-67/580 | 66-67 | 2 | **FLOW_ABOVE** | 67 | REPRICEABLE→67 |
| ATPCHALLENGERMATCH-26JUL05GUEROC-G | 14 | 128m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IEMBER-B | 95 | 127m | 1/96-96/1 | 95-96 | 1 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05IEMBER-I | 4 | 127m | 3/5-6/320 | 4-5 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05INGFEL-F | 75 | 127m | 1/77-77/1 | 75-76 | 2 | **FLOW_ABOVE** | 77 | REPRICEABLE→77 |
| ATPCHALLENGERMATCH-26JUL05INGFEL-I | 24 | 66m | 0 | 24-25 | — | **NO_FLOW** | 21 |  |
| ATPCHALLENGERMATCH-26JUL05MARDUR-D | 63 | 40m | 0 | 63-64 | — | **NO_FLOW** | 64 |  |
| ATPCHALLENGERMATCH-26JUL05MARDUR-M | 34 | 47m | 0 | 34-36 | — | **NO_FLOW** | 33 |  |
| ATPCHALLENGERMATCH-26JUL05MARZAN-M | 91 | 118m | 1/95-95/1 | 94-95 | 4 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MELWAL-M | 33 | 8m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05MELWAL-W | 63 | 8m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05NAGDOD-D | 14 | 128m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05NEUNED-N | 14 | 128m | 0 | 14-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PAPPAR-P | 82 | 8m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PAPPAR-P | 15 | 8m | 0 | 15-18 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PELALC-A | 18 | 77m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PELALC-P | 18 | 79m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PIELAR-L | 4 | 17m | 189/6-21/25190 | 19-5 | 2 | **FLOW_ABOVE** | 6 | REPRICEABLE→6 |
| ATPCHALLENGERMATCH-26JUL05POTANG-A | 47 | 86m | 0 | 47-48 | — | **NO_FLOW** | 51 |  |
| ATPCHALLENGERMATCH-26JUL05PRIROT-R | 27 | 58m | 0 | 32-32 | — | **NO_FLOW** | 27 |  |
| ATPCHALLENGERMATCH-26JUL05RATRAH-R | 58 | 48m | 0 | 58-59 | — | **NO_FLOW** | 61 |  |
| ATPCHALLENGERMATCH-26JUL05RATRAH-R | 38 | 45m | 0 | 39-40 | — | **NO_FLOW** | 36 |  |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 15 | 24m | 0 | 15-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SAIDIE-D | 18 | 66m | 0 | 18-78 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SAIDIE-S | 21 | 48m | 0 | 21-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-O | 80 | 127m | 1/81-81/1 | 80-82 | 1 | **FLOW_ABOVE** | 81 | REPRICEABLE→81 |
| ATPCHALLENGERMATCH-26JUL05SCIORA-S | 19 | 116m | 1/20-20/4 | 19-21 | 1 | **FLOW_ABOVE** | 17 | flow above but bound 17c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ-M | 4 | 58m | 25/5-6/1939 | 4-5 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SMIPIR-P | 71 | 8m | 6/72-72/108 | 72-72 | 1 | **FLOW_ABOVE** | 72 | REPRICEABLE→72 |
| ATPCHALLENGERMATCH-26JUL05SMIPIR-S | 28 | 2m | 8/29-30/272 | 29-29 | 1 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SQUGUI-G | 14 | 93m | 0 | 14-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SQUGUI-S | 15 | 19m | 0 | 15-54 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL05HURSTR-STR | 26 | 8m | 2/27-27/55 | 27-27 | 1 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05SINMOC-MOC | 3 | 8m | 4/4-4/1070 | 3-4 | 1 | **FLOW_ABOVE** | 3 | flow above but bound 3c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04BROKOI-BRO | 76 | 453m | 1350/80-99/350336 | 99-78 | 4 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 455m | 545/86-99/126759 | 99-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05HERVAI-V | 16 | 2m | 2/22-23/68 | 24-19 | 6 | **FLOW_ABOVE** | 16 | flow above but bound 16c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05KUDBOU-K | 92 | 20m | 0 | 92-95 | — | **NO_FLOW** | 92 |  |
| WTACHALLENGERMATCH-26JUL05MONGIM-G | 26 | 68m | 0 | 26-35 | — | **NO_FLOW** | 26 |  |
| WTACHALLENGERMATCH-26JUL05MONGIM-M | 71 | 68m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN | 80 | 1 | **81** | 97 | -16 |
| ITFWMATCH-26JUL04BROKOI | 21 | 78 | **99** | 97 | +2 |
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL05KUDBOU | 5 | 95 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL05HERVAI | 81 | 19 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05MARZAN | 6 | 95 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05CRIRUB | 72 | 29 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05PRIROT | 70 | 32 | **102** | 97 | +5 |

## PATTERNS (sub-B) — 7
- half_arm_aging: KXITFWMATCH-26JUL04MAXSTE-MAX {"fill": 14, "age_min": 455, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL04BROKOI-KOI {"fill": 21, "age_min": 453, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"entry_minus_fv_burst": -34.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"fill": 80, "age_min": 448, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARZAN-ZAN {"fill": 6, "age_min": 119, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05CRIRUB-RUB {"fill": 72, "age_min": 59, "mode": "SET_BELOW_FLOW(prints 12c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05PRIROT-PRI {"fill": 70, "age_min": 58, "mode": "STARVATION(no prints since post)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
