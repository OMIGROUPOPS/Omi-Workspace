# LIVE VALIDATION — rolling status

- cycle 50 @ **2026-07-05 05:28:35 AM ET** | build `cc9f991` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 16904 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 05:08:08 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05SCHDE | pair combined 99c > goal 97c |

## FILLS — 25 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:32 | ITFWMATCH-26JUL04MAXSTE-MAX | ITF_W | underdog | 14 | 10 | +4 (place_cell) | — | pre | single |  | MIXED |
| 21:34 | ITFWMATCH-26JUL04BROKOI-KOI | ITF_W | underdog | 21 | 18 | +3 (place_cell) | — | pre | single |  | MIXED |
| 21:40 | ATPCHALLENGERMATCH-26JUL04LEGWIN-L | ATP_CHALL | ? | 80 | 83 | -3 (window_cell) | -34.0 | pre | single |  | EARNED |
| 03:09 | ATPCHALLENGERMATCH-26JUL05MARZAN-Z | ATP_CHALL | underdog | 6 | 11 | -5 (place_cell) | — | pre | single |  | EARNED |
| 04:03 | ATPCHALLENGERMATCH-26JUL05PIELAR-P | ATP_CHALL | leader | 91 | 91 | +0 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 04:04 | ATPCHALLENGERMATCH-26JUL05VILKOV-K | ATP_CHALL | underdog | 47 | 44 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 04:09 | ATPCHALLENGERMATCH-26JUL05CRIRUB-R | ATP_CHALL | leader | 72 | 73 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:10 | ATPCHALLENGERMATCH-26JUL05PRIROT-P | ATP_CHALL | leader | 70 | 70 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 04:10 | ATPCHALLENGERMATCH-26JUL05SEIMOL-M | ATP_CHALL | leader | 84 | 84 | +0 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 04:11 | ATPCHALLENGERMATCH-26JUL05VILKOV-V | ATP_CHALL | ? | 50 | 53 | -3 (window_cell) | — | pre | pair | 97 | MIXED |
| 04:11 | ATPCHALLENGERMATCH-26JUL05SEIMOL-S | ATP_CHALL | underdog | 11 | 11 | +0 (place_cell) | — | pre | pair | 95 | EARNED |
| 04:44 | ATPCHALLENGERMATCH-26JUL05PIELAR-L | ATP_CHALL | underdog | 5 | 5 | +0 (place_cell) | — | pre | pair | 96 | EARNED |
| 04:48 | WTACHALLENGERMATCH-26JUL05KUDBOU-B | WTA_CHALL | underdog | 5 | 2 | +3 (place_cell) | — | pre | single |  | MIXED |
| 05:06 | WTACHALLENGERMATCH-26JUL05HERVAI-H | WTA_CHALL | leader | 81 | 83 | -2 (place_cell) | — | pre | single |  | MIXED |
| 05:07 | ATPCHALLENGERMATCH-26JUL05SCHDE-DE | ATP_CHALL | leader | 75 | 75 | +0 (place_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 05:08 | ATPCHALLENGERMATCH-26JUL05SCHDE-SC | ATP_CHALL | underdog | 24 | 20 | +4 (place_cell) | — | pre | pair | 99 | MIXED |
| 05:09 | ATPCHALLENGERMATCH-26JUL05SMIPIR-P | ATP_CHALL | leader | 71 | 72 | -1 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 05:10 | ATPCHALLENGERMATCH-26JUL05BERBOC-B | ATP_CHALL | underdog | 22 | 17 | +5 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:10 | WTACHALLENGERMATCH-26JUL05MONGIM-G | WTA_CHALL | underdog | 26 | 26 | +0 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:17 | ATPCHALLENGERMATCH-26JUL05BERBOC-B | ATP_CHALL | leader | 75 | 75 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:21 | WTACHALLENGERMATCH-26JUL05MONGIM-M | WTA_CHALL | leader | 71 | 71 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:21 | ATPCHALLENGERMATCH-26JUL05DIACEC-D | ATP_CHALL | leader | 65 | 66 | -1 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 05:21 | ATPCHALLENGERMATCH-26JUL05CRIRUB-C | ATP_CHALL | underdog | 25 | 22 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:22 | ATPCHALLENGERMATCH-26JUL05RATRAH-R | ATP_CHALL | leader | 58 | 58 | +0 (place_cell) | — | pre | single |  | MIXED |
| 05:25 | ATPCHALLENGERMATCH-26JUL05DIACEC-C | ATP_CHALL | ? | 31 | 33 | -2 (window_cell) | — | pre | pair | 96 | EARNED |

## RESTING BIDS — 66 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 18, 'NO_FLOW': 42, 'FLOW_AT_LEVEL': 6} | repriceable now: true 5 / false 61 | **cumulative bid_grade lines: 160 (repriceable true 17 / false 143)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BONSCH-S | 15 | 39m | 0 | 15-87 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BRAAGA-B | 14 | 148m | 0 | 14-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CAMBID-B | 15 | 88m | 1/21-21/5 | 16-18 | 6 | **FLOW_ABOVE** | 14 | flow above but bound 14c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05CAMBID-C | 82 | 69m | 0 | 82-84 | — | **NO_FLOW** | 84 |  |
| ATPCHALLENGERMATCH-26JUL05CANDEL-C | 14 | 28m | 0 | 14-87 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CANDEL-D | 15 | 39m | 0 | 15-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 6 | 86m | 1/6-6/0 | 6-7 | 0 | **FLOW_AT_LEVEL** | 5 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 93 | 61m | 0 | 93-95 | — | **NO_FLOW** | 94 |  |
| ATPCHALLENGERMATCH-26JUL05CHESPE-C | 58 | 8m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CHESPE-S | 39 | 8m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CRIRUB-C | 24 | 2m | 25/34-38/972 | 64-26 | 10 | **FLOW_ABOVE** | 24 | flow above but bound 24c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05DALARI-A | 6 | 148m | 0 | 6-7 | — | **NO_FLOW** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 93 | 146m | 1/94-94/74 | 93-94 | 1 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05GOMMAJ-G | 80 | 8m | 0 | 80-82 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GOMMAJ-M | 17 | 8m | 0 | 17-20 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GUEROC-G | 14 | 148m | 0 | 14-91 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IEMBER-B | 95 | 148m | 1/96-96/1 | 95-96 | 1 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05IEMBER-I | 4 | 148m | 4/4-6/320 | 4-5 | 0 | **FLOW_AT_LEVEL** | 2 |  |
| ATPCHALLENGERMATCH-26JUL05INGFEL-F | 75 | 148m | 1/77-77/1 | 75-76 | 2 | **FLOW_ABOVE** | 77 | REPRICEABLE→77 |
| ATPCHALLENGERMATCH-26JUL05INGFEL-I | 24 | 87m | 0 | 24-25 | — | **NO_FLOW** | 21 |  |
| ATPCHALLENGERMATCH-26JUL05MARDUR-D | 63 | 60m | 9/65-66/199 | 63-64 | 2 | **FLOW_ABOVE** | 64 | REPRICEABLE→64 |
| ATPCHALLENGERMATCH-26JUL05MARDUR-M | 34 | 67m | 0 | 34-37 | — | **NO_FLOW** | 33 |  |
| ATPCHALLENGERMATCH-26JUL05MARZAN-M | 91 | 138m | 1/95-95/1 | 94-95 | 4 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MELWAL-M | 33 | 28m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05MELWAL-W | 63 | 28m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05NAGDOD-D | 14 | 148m | 0 | 14-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05NEUNED-N | 14 | 149m | 0 | 14-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05NIJBER-B | 23 | 18m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05NIJBER-N | 74 | 18m | 0 | 74-77 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PAPPAR-P | 82 | 28m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PAPPAR-P | 15 | 28m | 0 | 15-18 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PELALC-A | 18 | 97m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PELALC-P | 18 | 99m | 0 | 18-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PIELAR-L | 4 | 37m | 387/3-21/52259 | 19-4 | -1 | **FLOW_AT_LEVEL** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05POTANG-A | 47 | 106m | 1/48-48/131 | 47-48 | 1 | **FLOW_ABOVE** | 51 | REPRICEABLE→48 |
| ATPCHALLENGERMATCH-26JUL05PRIROT-R | 27 | 78m | 0 | 32-32 | — | **NO_FLOW** | 27 |  |
| ATPCHALLENGERMATCH-26JUL05RATRAH-R | 39 | 4m | 4/52-57/116 | 60-40 | 13 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 20 | 13m | 0 | 33-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 15 | 44m | 0 | 15-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SAIDIE-D | 18 | 86m | 0 | 18-78 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SAIDIE-S | 21 | 68m | 0 | 21-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 20 | 11m | 17/11-26/787 | 11-13 | -9 | **FLOW_AT_LEVEL** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 17 | 7m | 8/11-17/625 | 11-13 | -6 | **FLOW_AT_LEVEL** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-O | 80 | 148m | 5/81-82/67 | 80-82 | 1 | **FLOW_ABOVE** | 81 | REPRICEABLE→81 |
| ATPCHALLENGERMATCH-26JUL05SCIORA-S | 19 | 136m | 1/20-20/4 | 19-21 | 1 | **FLOW_ABOVE** | 17 | flow above but bound 17c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ-M | 4 | 78m | 26/5-6/1972 | 4-5 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SMIPIR-S | 26 | 6m | 35/32-55/2069 | 45-27 | 6 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SQUGUI-G | 14 | 113m | 0 | 14-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SQUGUI-S | 15 | 39m | 0 | 15-54 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05STALOC-L | 4 | 18m | 0 | 5-6 | — | **NO_FLOW** | 3 |  |
| ATPCHALLENGERMATCH-26JUL05STALOC-S | 94 | 18m | 0 | 94-95 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05TIXLEC-L | 77 | 18m | 0 | 77-78 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05TIXLEC-T | 19 | 18m | 0 | 19-23 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL05HURSTR-STR | 26 | 28m | 9/26-27/618 | 27-27 | 0 | **FLOW_AT_LEVEL** | 26 |  |
| ATPMATCH-26JUL05SINMOC-MOC | 3 | 28m | 10/4-4/2011 | 3-4 | 1 | **FLOW_ABOVE** | 3 | flow above but bound 3c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04BROKOI-BRO | 76 | 474m | 1350/80-99/350336 | 99-78 | 4 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 476m | 545/86-99/126759 | 99-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05BARPOP-B | 33 | 18m | 0 | 33-37 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05BARPOP-P | 63 | 18m | 0 | 63-66 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05HERVAI-V | 16 | 2m | 12/20-23/13483 | 20-19 | 4 | **FLOW_ABOVE** | 16 | flow above but bound 16c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05KUDBOU-K | 92 | 40m | 30/94-96/14797 | 95-94 | 2 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05MONGIM-G | 25 | 2m | 0 | 27-28 | — | **NO_FLOW** | 26 |  |
| WTACHALLENGERMATCH-26JUL05MORKOT-K | 92 | 18m | 0 | 92-93 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05MORKOT-M | 6 | 18m | 0 | 6-8 | — | **NO_FLOW** | 5 |  |
| WTACHALLENGERMATCH-26JUL05MORNGU-M | 6 | 18m | 0 | 6-9 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05MORNGU-N | 91 | 18m | 0 | 91-92 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN | 80 | 1 | **81** | 97 | -16 |
| ATPCHALLENGERMATCH-26JUL05SMIPIR | 71 | 27 | **98** | 97 | +1 |
| ATPCHALLENGERMATCH-26JUL05RATRAH | 58 | 40 | **98** | 97 | +1 |
| ITFWMATCH-26JUL04BROKOI | 21 | 78 | **99** | 97 | +2 |
| WTACHALLENGERMATCH-26JUL05KUDBOU | 5 | 94 | **99** | 97 | +2 |
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL05HERVAI | 81 | 19 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05MARZAN | 6 | 95 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05PRIROT | 70 | 32 | **102** | 97 | +5 |

## PATTERNS (sub-B) — 7
- half_arm_aging: KXITFWMATCH-26JUL04MAXSTE-MAX {"fill": 14, "age_min": 476, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL04BROKOI-KOI {"fill": 21, "age_min": 474, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"entry_minus_fv_burst": -34.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"fill": 80, "age_min": 468, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARZAN-ZAN {"fill": 6, "age_min": 139, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05PRIROT-PRI {"fill": 70, "age_min": 78, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL05KUDBOU-BOU {"fill": 5, "age_min": 40, "mode": "SET_BELOW_FLOW(prints 2c above)", "emitted_et": "2026-07-05 05:28:35 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
