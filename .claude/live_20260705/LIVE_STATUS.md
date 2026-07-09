# LIVE VALIDATION — rolling status

- cycle 4 @ **2026-07-09 04:05:48 PM ET** | build `668c6f6` | session boot 07-09 15:50 ET | log `live_v3_20260709.jsonl` | 4588 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:50 | WTACHALLENGERMATCH-26JUL09STEROG-R | WTA_CHALL | ? | 17 | 14 | +3 (window_cell) | — | pre | single |  | MIXED |
| 15:50 | ATPCHALLENGERMATCH-26JUL09MEJROD-R | ATP_CHALL | ? | 19 | 16 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 15:50 | ITFMATCH-26JUL09GORARD-GOR | ITF_M | ? | 72 | 50 | +22 (window_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 5 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 3, 'FLOW_ABOVE': 2} | repriceable now: true 0 / false 5 | **cumulative bid_grade lines: 7156 (repriceable true 880 / false 6276)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB-A | 50 | 15m | 3/53-53/1027 | 52-53 | 3 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ-K | 20 | 15m | 3/23-23/199 | 20-23 | 3 | **FLOW_ABOVE** | 20 | flow above but bound 20c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09JOHBLA-B | 69 | 15m | 0 | 80-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 15m | 0 | 80-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THORIC-THO | 17 | 15m | 0 | 17-21 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTACHALLENGERMATCH-26JUL09STEROG | 17 | 87 | **104** | 97 | +7 |
| ITFMATCH-26JUL09GORARD | 72 | 40 | **112** | 97 | +15 |

## FLOW-STATE — 8 tracked game(s) ({'WAKING': 8}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB | ATP_CHALL | 0.267 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ | ATP_CHALL | 0.2 | 3 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09JOHBLA | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09MEJROD | ATP_CHALL | 43.4 | — | **WAKING** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09GORARD | ITF_M | 5.567 | — | **WAKING** |
| ITFMATCH-26JUL09THORIC | ITF_M | 0.067 | 4 | **WAKING** |
| WTACHALLENGERMATCH-26JUL09STEROG | WTA_CHALL | 3.633 | — | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
