# LIVE VALIDATION — rolling status

- cycle 143 @ **2026-07-09 03:05:51 PM ET** | build `c9b010b` | session boot 07-09 14:54 ET | log `live_v3_20260709.jsonl` | 2389 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 5 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:54 | WTACHALLENGERMATCH-26JUL09STEROG-R | WTA_CHALL | ? | 15 | 53 | -38 (window_cell) | — | pre | single |  | EARNED |
| 14:54 | ATPCHALLENGERMATCH-26JUL09MEJROD-R | ATP_CHALL | ? | 19 | 16 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:54 | ITFMATCH-26JUL09GORARD-GOR | ITF_M | ? | 72 | 69 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:55 | ITFWMATCH-26JUL09DAALUX-DAA | ITF_W | leader | 63 | 62 | +1 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 14:55 | ITFWMATCH-26JUL09DAALUX-LUX | ITF_W | underdog | 34 | 32 | +2 (place_cell) | — | pre | pair | 97 | EARNED |

## RESTING BIDS — 12 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 7, 'NO_FLOW': 5} | repriceable now: true 1 / false 11 | **cumulative bid_grade lines: 7143 (repriceable true 879 / false 6264)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB-A | 50 | 11m | 5/53-53/3746 | 52-53 | 3 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ-F | 77 | 11m | 0 | 77-78 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ-K | 20 | 7m | 0 | 20-23 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09JOHBLA-B | 69 | 11m | 0 | 79-80 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09MANGAL-G | 18 | 11m | 37/22-24/4436 | 23-22 | 4 | **FLOW_ABOVE** | 19 | REPRICEABLE→19 |
| ITFMATCH-26JUL09BRUJOH-JOH | 61 | 11m | 3/72-72/37 | 68-71 | 11 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 11m | 0 | 80-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THORIC-RIC | 80 | 11m | 0 | 80-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09EBEFEI-EBE | 16 | 11m | 55/21-37/6089 | 25-22 | 5 | **FLOW_ABOVE** | 26 |  |
| ITFWMATCH-26JUL09GJISHC-SHC | 79 | 11m | 3/91-96/27 | 95-96 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL09NAHKHA-KHA | 44 | 11m | 58/69-77/7543 | 74-69 | 25 | **FLOW_ABOVE** | 71 |  |
| ITFWMATCH-26JUL09QUAMAL-MAL | 27 | 11m | 81/61-73/6635 | 71-66 | 34 | **FLOW_ABOVE** | 69 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTACHALLENGERMATCH-26JUL09STEROG | 15 | 71 | **86** | 97 | -11 |

## FLOW-STATE — 15 tracked game(s) ({'OPEN': 4, 'WAKING': 11}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB | ATP_CHALL | 0.3 | 1 | **OPEN** |
| ITFMATCH-26JUL09BRUJOH | ITF_M | 0.333 | 3 | **OPEN** |
| ITFMATCH-26JUL09GORARD | ITF_M | 0.2 | 2 | **OPEN** |
| WTACHALLENGERMATCH-26JUL09STEROG | WTA_CHALL | 1.533 | 2 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09JOHBLA | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09MANGAL | ATP_CHALL | 1.567 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09MEJROD | ATP_CHALL | 25.4 | — | **WAKING** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09THORIC | ITF_M | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09DAALUX | ITF_W | 22.6 | — | **WAKING** |
| ITFWMATCH-26JUL09EBEFEI | ITF_W | 2.767 | — | **WAKING** |
| ITFWMATCH-26JUL09GJISHC | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL09NAHKHA | ITF_W | 6.233 | — | **WAKING** |
| ITFWMATCH-26JUL09QUAMAL | ITF_W | 11.433 | — | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
