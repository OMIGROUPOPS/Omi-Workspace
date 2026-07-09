# LIVE VALIDATION — rolling status

- cycle 145 @ **2026-07-09 03:26:29 PM ET** | build `81b3b1d` | session boot 07-09 14:54 ET | log `live_v3_20260709.jsonl` | 5646 session events | monitor READ-ONLY
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
- classes now: {'FLOW_ABOVE': 11} | repriceable now: true 2 / false 9 | **cumulative bid_grade lines: 7148 (repriceable true 880 / false 6268)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB-A | 50 | 32m | 20/52-53/6707 | 52-53 | 2 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ-F | 77 | 32m | 1/78-78/11 | 77-78 | 1 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ-K | 21 | 19m | 1/24-24/37 | 21-23 | 3 | **FLOW_ABOVE** | 21 | flow above but bound 21c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09JOHBLA-B | 69 | 32m | 3/80-81/432 | 80-80 | 11 | **FLOW_ABOVE** | 77 | flow above but bound 77c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09MANGAL-G | 18 | 32m | 383/22-51/89226 | 50-22 | 4 | **FLOW_ABOVE** | 19 | REPRICEABLE→19 |
| ITFMATCH-26JUL09BRUJOH-JOH | 61 | 32m | 15/70-73/989 | 70-70 | 9 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 32m | 2/83-83/28 | 80-83 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL09THORIC-RIC | 80 | 32m | 1/83-83/11 | 80-83 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→83 |
| ITFWMATCH-26JUL09GJISHC-SHC | 79 | 32m | 51/89-99/5259 | 94-91 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL09NAHKHA-KHA | 44 | 32m | 271/54-86/23027 | 81-55 | 10 | **FLOW_ABOVE** | 71 |  |
| ITFWMATCH-26JUL09QUAMAL-MAL | 27 | 32m | 739/61-96/72652 | 94-66 | 34 | **FLOW_ABOVE** | 69 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL09EBEFEI | 16 | 68 | **84** | 97 | -13 |
| WTACHALLENGERMATCH-26JUL09STEROG | 15 | 71 | **86** | 97 | -11 |

## FLOW-STATE — 15 tracked game(s) ({'OPEN': 3, 'WAKING': 12}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB | ATP_CHALL | 0.6 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ | ATP_CHALL | 0.333 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL09STEROG | WTA_CHALL | 0.833 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL09JOHBLA | ATP_CHALL | 0.1 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09MANGAL | ATP_CHALL | 12.767 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09MEJROD | ATP_CHALL | 30.033 | — | **WAKING** |
| ITFMATCH-26JUL09BRUJOH | ITF_M | 0.433 | — | **WAKING** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.067 | 3 | **WAKING** |
| ITFMATCH-26JUL09GORARD | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL09THORIC | ITF_M | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL09DAALUX | ITF_W | 41.3 | — | **WAKING** |
| ITFWMATCH-26JUL09EBEFEI | ITF_W | 9.9 | — | **WAKING** |
| ITFWMATCH-26JUL09GJISHC | ITF_W | 1.633 | — | **WAKING** |
| ITFWMATCH-26JUL09NAHKHA | ITF_W | 8.067 | — | **WAKING** |
| ITFWMATCH-26JUL09QUAMAL | ITF_W | 24.233 | — | **WAKING** |

## PATTERNS (sub-B) — 3
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL09STEROG-ROG {"fill": 15, "age_min": 32, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-09 03:26:29 PM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL09MEJROD-ROD {"fill": 19, "age_min": 32, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL09GORARD-GOR {"fill": 72, "age_min": 32, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-09 03:26:29 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
