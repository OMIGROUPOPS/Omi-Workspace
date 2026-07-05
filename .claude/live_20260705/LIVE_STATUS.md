# LIVE VALIDATION — rolling status

- cycle 36 @ **2026-07-05 03:07:15 AM ET** | build `23383cb` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 9795 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:32 | ITFWMATCH-26JUL04MAXSTE-MAX | ITF_W | underdog | 14 | 10 | +4 (place_cell) | — | pre | single |  | MIXED |
| 21:34 | ITFWMATCH-26JUL04BROKOI-KOI | ITF_W | underdog | 21 | 18 | +3 (place_cell) | — | pre | single |  | MIXED |
| 21:40 | ATPCHALLENGERMATCH-26JUL04LEGWIN-L | ATP_CHALL | ? | 80 | 83 | -3 (window_cell) | -34.0 | pre | single |  | EARNED |

## RESTING BIDS — 28 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 4, 'NO_FLOW': 24} | repriceable now: true 0 / false 28 | **cumulative bid_grade lines: 34 (repriceable true 0 / false 34)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BERBOC-B | 20 | 6m | 0 | 20-25 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BERBOC-B | 75 | 6m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BONSCH-S | 14 | 7m | 0 | 14-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BRAAGA-B | 14 | 7m | 0 | 14-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CANDEL-D | 14 | 7m | 0 | 14-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 5 | 6m | 0 | 5-8 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 92 | 6m | 0 | 92-95 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CRIRUB-C | 25 | 5m | 0 | 25-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05CRIRUB-R | 73 | 6m | 0 | 74-75 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-A | 6 | 6m | 0 | 6-7 | — | **NO_FLOW** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 93 | 5m | 0 | 93-94 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GUEROC-G | 14 | 7m | 0 | 14-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IEMBER-B | 95 | 6m | 0 | 95-96 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IEMBER-I | 4 | 6m | 0 | 4-5 | — | **NO_FLOW** | 2 |  |
| ATPCHALLENGERMATCH-26JUL05INGFEL-F | 75 | 6m | 0 | 75-76 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05INGFEL-I | 23 | 5m | 0 | 23-24 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05MARZAN-Z | 6 | 6m | 0 | 6-7 | — | **NO_FLOW** | 11 |  |
| ATPCHALLENGERMATCH-26JUL05NAGDOD-D | 14 | 7m | 0 | 14-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05NEUNED-N | 14 | 7m | 0 | 14-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PIELAR-L | 7 | 6m | 18/9-10/1485 | 8-8 | 2 | **FLOW_ABOVE** | 6 | flow above but bound 6c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PIELAR-P | 91 | 6m | 0 | 91-93 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 14 | 7m | 0 | 14-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-O | 80 | 6m | 0 | 80-82 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-S | 18 | 3m | 0 | 18-20 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SEIMOL-M | 84 | 7m | 0 | 84-85 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SEIMOL-S | 14 | 7m | 4/16-16/294 | 14-15 | 2 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04BROKOI-BRO | 76 | 332m | 1350/80-99/350336 | 99-78 | 4 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 334m | 545/86-99/126759 | 99-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN | 80 | 1 | **81** | 97 | -16 |
| ITFWMATCH-26JUL04BROKOI | 21 | 78 | **99** | 97 | +2 |
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |

## PATTERNS (sub-B) — 4
- half_arm_aging: KXITFWMATCH-26JUL04MAXSTE-MAX {"fill": 14, "age_min": 334, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL04BROKOI-KOI {"fill": 21, "age_min": 332, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"entry_minus_fv_burst": -34.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"fill": 80, "age_min": 327, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
