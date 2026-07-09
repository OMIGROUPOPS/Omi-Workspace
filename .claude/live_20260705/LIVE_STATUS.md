# LIVE VALIDATION — rolling status

- cycle 2 @ **2026-07-09 03:45:23 PM ET** | build `986955c` | session boot 07-09 14:54 ET | log `live_v3_20260709.jsonl` | 9139 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 7 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:54 | WTACHALLENGERMATCH-26JUL09STEROG-R | WTA_CHALL | ? | 15 | 53 | -38 (window_cell) | — | pre | single |  | EARNED |
| 14:54 | ATPCHALLENGERMATCH-26JUL09MEJROD-R | ATP_CHALL | ? | 19 | 16 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:54 | ITFMATCH-26JUL09GORARD-GOR | ITF_M | ? | 72 | 69 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:55 | ITFWMATCH-26JUL09DAALUX-DAA | ITF_W | leader | 63 | 62 | +1 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 14:55 | ITFWMATCH-26JUL09DAALUX-LUX | ITF_W | underdog | 34 | 32 | +2 (place_cell) | — | pre | pair | 97 | EARNED |
| 15:07 | ITFWMATCH-26JUL09EBEFEI-EBE | ITF_W | ? | 16 | 26 | -10 (window_cell) | — | pre | single |  | EARNED |
| 15:35 | ITFWMATCH-26JUL09NAHKHA-KHA | ITF_W | ? | 44 | 71 | -27 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 8 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 7, 'NO_FLOW': 1} | repriceable now: true 1 / false 7 | **cumulative bid_grade lines: 7149 (repriceable true 880 / false 6269)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB-A | 50 | 51m | 25/52-53/7261 | 52-53 | 2 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ-F | 77 | 51m | 3/78-78/22 | 77-78 | 1 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ-K | 21 | 38m | 3/23-24/149 | 21-23 | 2 | **FLOW_ABOVE** | 21 | flow above but bound 21c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09JOHBLA-B | 69 | 51m | 3/80-81/432 | 80-80 | 11 | **FLOW_ABOVE** | 77 | flow above but bound 77c < flow -- chasing breaks goal |
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 51m | 2/83-83/28 | 80-83 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL09THORIC-RIC | 80 | 50m | 2/83-83/11 | 80-83 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→83 |
| ITFMATCH-26JUL09THORIC-THO | 18 | 13m | 0 | 18-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09GJISHC-SHC | 79 | 51m | 103/89-99/8315 | 98-91 | 10 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL09NAHKHA | 44 | 19 | **63** | 97 | -34 |
| ITFWMATCH-26JUL09EBEFEI | 16 | 63 | **79** | 97 | -18 |
| WTACHALLENGERMATCH-26JUL09STEROG | 15 | 71 | **86** | 97 | -11 |

## FLOW-STATE — 12 tracked game(s) ({'OPEN': 2, 'WAKING': 10}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB | ATP_CHALL | 0.433 | 1 | **OPEN** |
| ITFMATCH-26JUL09THORIC | ITF_M | 0.233 | 2 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09JOHBLA | ATP_CHALL | 0.067 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09MEJROD | ATP_CHALL | 39.667 | — | **WAKING** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL09GORARD | ITF_M | 0.833 | — | **WAKING** |
| ITFWMATCH-26JUL09DAALUX | ITF_W | 22.333 | — | **WAKING** |
| ITFWMATCH-26JUL09EBEFEI | ITF_W | 24.867 | — | **WAKING** |
| ITFWMATCH-26JUL09GJISHC | ITF_W | 3.033 | — | **WAKING** |
| ITFWMATCH-26JUL09NAHKHA | ITF_W | 12.467 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL09STEROG | WTA_CHALL | 1.333 | — | **WAKING** |

## PATTERNS (sub-B) — 4
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL09STEROG-ROG {"fill": 15, "age_min": 51, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL09MEJROD-ROD {"fill": 19, "age_min": 51, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL09GORARD-GOR {"fill": 72, "age_min": 51, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL09EBEFEI-EBE {"fill": 16, "age_min": 38, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-09 03:45:23 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
