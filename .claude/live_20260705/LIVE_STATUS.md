# LIVE VALIDATION — rolling status

- cycle 144 @ **2026-07-09 03:16:10 PM ET** | build `f92c3c6` | session boot 07-09 14:54 ET | log `live_v3_20260709.jsonl` | 3489 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 6 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:54 | WTACHALLENGERMATCH-26JUL09STEROG-R | WTA_CHALL | ? | 15 | 53 | -38 (window_cell) | — | pre | single |  | EARNED |
| 14:54 | ATPCHALLENGERMATCH-26JUL09MEJROD-R | ATP_CHALL | ? | 19 | 16 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:54 | ITFMATCH-26JUL09GORARD-GOR | ITF_M | ? | 72 | 69 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:55 | ITFWMATCH-26JUL09DAALUX-DAA | ITF_W | leader | 63 | 62 | +1 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 14:55 | ITFWMATCH-26JUL09DAALUX-LUX | ITF_W | underdog | 34 | 32 | +2 (place_cell) | — | pre | pair | 97 | EARNED |
| 15:07 | ITFWMATCH-26JUL09EBEFEI-EBE | ITF_W | ? | 16 | 26 | -10 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 11 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 9, 'NO_FLOW': 2} | repriceable now: true 1 / false 10 | **cumulative bid_grade lines: 7146 (repriceable true 879 / false 6267)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB-A | 50 | 22m | 12/53-53/6580 | 52-53 | 3 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ-F | 77 | 21m | 0 | 77-78 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ-K | 21 | 9m | 1/24-24/37 | 21-24 | 3 | **FLOW_ABOVE** | 21 | flow above but bound 21c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09JOHBLA-B | 69 | 22m | 1/80-80/6 | 79-80 | 11 | **FLOW_ABOVE** | 77 | flow above but bound 77c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09MANGAL-G | 18 | 22m | 149/22-27/17973 | 22-22 | 4 | **FLOW_ABOVE** | 19 | REPRICEABLE→19 |
| ITFMATCH-26JUL09BRUJOH-JOH | 61 | 22m | 5/70-72/70 | 68-70 | 9 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 22m | 1/83-83/17 | 80-83 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL09THORIC-RIC | 80 | 21m | 0 | 80-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09GJISHC-SHC | 79 | 22m | 12/89-96/1269 | 95-96 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL09NAHKHA-KHA | 44 | 22m | 151/69-86/15241 | 81-69 | 25 | **FLOW_ABOVE** | 71 |  |
| ITFWMATCH-26JUL09QUAMAL-MAL | 27 | 22m | 332/61-88/25529 | 83-66 | 34 | **FLOW_ABOVE** | 69 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL09EBEFEI | 16 | 68 | **84** | 97 | -13 |
| WTACHALLENGERMATCH-26JUL09STEROG | 15 | 71 | **86** | 97 | -11 |

## FLOW-STATE — 15 tracked game(s) ({'OPEN': 6, 'WAKING': 9}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB | ATP_CHALL | 0.5 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ | ATP_CHALL | 0.333 | 1 | **OPEN** |
| ITFMATCH-26JUL09BRUJOH | ITF_M | 0.3 | 2 | **OPEN** |
| ITFMATCH-26JUL09GORARD | ITF_M | 0.2 | 2 | **OPEN** |
| ITFWMATCH-26JUL09GJISHC | ITF_W | 0.4 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL09STEROG | WTA_CHALL | 1.4 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL09JOHBLA | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09MANGAL | ATP_CHALL | 5.033 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09MEJROD | ATP_CHALL | 25.0 | — | **WAKING** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL09THORIC | ITF_M | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09DAALUX | ITF_W | 29.5 | — | **WAKING** |
| ITFWMATCH-26JUL09EBEFEI | ITF_W | 6.033 | — | **WAKING** |
| ITFWMATCH-26JUL09NAHKHA | ITF_W | 5.467 | — | **WAKING** |
| ITFWMATCH-26JUL09QUAMAL | ITF_W | 16.9 | — | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
