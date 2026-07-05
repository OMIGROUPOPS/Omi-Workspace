# LIVE VALIDATION — rolling status

- cycle 39 @ **2026-07-05 03:37:32 AM ET** | build `5f46ff0` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 11321 session events | monitor READ-ONLY
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

## RESTING BIDS — 34 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 27, 'FLOW_AT_LEVEL': 1} | repriceable now: true 2 / false 32 | **cumulative bid_grade lines: 45 (repriceable true 3 / false 42)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BERBOC-B | 20 | 37m | 0 | 20-25 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BERBOC-B | 75 | 37m | 1/79-79/10 | 75-79 | 4 | **FLOW_ABOVE** | 79 | REPRICEABLE→79 |
| ATPCHALLENGERMATCH-26JUL05BONSCH-S | 14 | 37m | 0 | 14-86 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BRAAGA-B | 14 | 37m | 0 | 14-87 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CANDEL-D | 14 | 37m | 0 | 14-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 5 | 37m | 0 | 5-8 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 92 | 37m | 0 | 92-95 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CRIRUB-C | 25 | 35m | 0 | 25-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CRIRUB-R | 73 | 37m | 3/76-76/24 | 74-75 | 3 | **FLOW_ABOVE** | 76 | REPRICEABLE→76 |
| ATPCHALLENGERMATCH-26JUL05DALARI-A | 6 | 37m | 0 | 6-7 | — | **NO_FLOW** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 93 | 35m | 0 | 93-94 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GUEROC-G | 14 | 37m | 0 | 14-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IEMBER-B | 95 | 37m | 0 | 95-96 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IEMBER-I | 4 | 37m | 0 | 4-5 | — | **NO_FLOW** | 2 |  |
| ATPCHALLENGERMATCH-26JUL05INGFEL-F | 75 | 37m | 0 | 75-76 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05INGFEL-I | 23 | 35m | 0 | 23-24 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05MARZAN-M | 91 | 27m | 0 | 94-95 | — | **NO_FLOW** | 91 |  |
| ATPCHALLENGERMATCH-26JUL05NAGDOD-D | 14 | 37m | 0 | 14-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05NEUNED-N | 14 | 37m | 0 | 14-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PELALC-P | 14 | 0m | 0 | 14-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PIELAR-L | 7 | 37m | 22/9-10/1798 | 8-8 | 2 | **FLOW_ABOVE** | 6 | flow above but bound 6c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PIELAR-P | 91 | 37m | 0 | 91-93 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PRIROT-P | 70 | 22m | 4/70-71/56 | 70-71 | 0 | **FLOW_AT_LEVEL** | 71 |  |
| ATPCHALLENGERMATCH-26JUL05PRIROT-R | 31 | 10m | 0 | 31-32 | — | **NO_FLOW** | 30 |  |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 14 | 37m | 0 | 14-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SAIDIE-D | 15 | 2m | 0 | 15-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SAIDIE-S | 15 | 0m | 0 | 16-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-O | 80 | 37m | 0 | 80-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-S | 19 | 25m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SEIMOL-M | 84 | 37m | 0 | 84-85 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SEIMOL-S | 14 | 37m | 24/16-17/3057 | 15-15 | 2 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SQUGUI-G | 14 | 2m | 0 | 14-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL04BROKOI-BRO | 76 | 363m | 1350/80-99/350336 | 99-78 | 4 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 365m | 545/86-99/126759 | 99-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN | 80 | 1 | **81** | 97 | -16 |
| ITFWMATCH-26JUL04BROKOI | 21 | 78 | **99** | 97 | +2 |
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05MARZAN | 6 | 95 | **101** | 97 | +4 |

## PATTERNS (sub-B) — 4
- half_arm_aging: KXITFWMATCH-26JUL04MAXSTE-MAX {"fill": 14, "age_min": 365, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL04BROKOI-KOI {"fill": 21, "age_min": 363, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"entry_minus_fv_burst": -34.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"fill": 80, "age_min": 357, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
