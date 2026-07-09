# LIVE VALIDATION — rolling status

- cycle 5 @ **2026-07-09 04:16:05 PM ET** | build `f63f1a2` | session boot 07-09 15:50 ET | log `live_v3_20260709.jsonl` | 5641 session events | monitor READ-ONLY
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
- classes now: {'FLOW_ABOVE': 4, 'NO_FLOW': 1} | repriceable now: true 1 / false 4 | **cumulative bid_grade lines: 7158 (repriceable true 881 / false 6277)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB-A | 50 | 25m | 13/53-53/2038 | 52-53 | 3 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ-K | 20 | 25m | 15/23-23/1702 | 20-23 | 3 | **FLOW_ABOVE** | 20 | flow above but bound 20c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL09JOHBLA-B | 69 | 25m | 1/81-81/24 | 80-81 | 12 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 25m | 0 | 80-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THORIC-THO | 17 | 25m | 2/21-21/13 | 17-21 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTACHALLENGERMATCH-26JUL09STEROG | 17 | 86 | **103** | 97 | +6 |
| ITFMATCH-26JUL09GORARD | 72 | 40 | **112** | 97 | +15 |

## FLOW-STATE — 8 tracked game(s) ({'OPEN': 1, 'WAKING': 7}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB | ATP_CHALL | 0.5 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ | ATP_CHALL | 0.533 | 3 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09JOHBLA | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09MEJROD | ATP_CHALL | 39.967 | — | **WAKING** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09GORARD | ITF_M | 11.0 | — | **WAKING** |
| ITFMATCH-26JUL09THORIC | ITF_M | 0.133 | 4 | **WAKING** |
| WTACHALLENGERMATCH-26JUL09STEROG | WTA_CHALL | 8.9 | — | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
