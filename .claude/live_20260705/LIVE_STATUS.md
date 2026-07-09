# LIVE VALIDATION — rolling status

- cycle 3 @ **2026-07-09 03:55:33 PM ET** | build `3c811cf` | session boot 07-09 15:50 ET | log `live_v3_20260709.jsonl` | 931 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:50 | WTACHALLENGERMATCH-26JUL09STEROG-R | WTA_CHALL | ? | 17 | 14 | +3 (window_cell) | — | pre | single |  | MIXED |
| 15:50 | ATPCHALLENGERMATCH-26JUL09MEJROD-R | ATP_CHALL | ? | 19 | 16 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 15:50 | ITFMATCH-26JUL09GORARD-GOR | ITF_M | ? | 72 | 69 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 5 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 5} | repriceable now: true 0 / false 5 | **cumulative bid_grade lines: 7154 (repriceable true 880 / false 6274)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB-A | 50 | 5m | 0 | 52-53 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ-K | 20 | 5m | 0 | 20-23 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09JOHBLA-B | 69 | 5m | 0 | 80-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 5m | 0 | 80-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THORIC-THO | 17 | 4m | 0 | 17-21 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTACHALLENGERMATCH-26JUL09STEROG | 17 | 87 | **104** | 97 | +7 |

## FLOW-STATE — 8 tracked game(s) ({'WAKING': 6, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09GORARD | ITF_M | 3.033 | 2 | **OPEN** |
| WTACHALLENGERMATCH-26JUL09STEROG | WTA_CHALL | 2.967 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL09CASAMB | ATP_CHALL | 0.233 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09FEAKOZ | ATP_CHALL | 0.1 | 3 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09JOHBLA | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09MEJROD | ATP_CHALL | 41.6 | — | **WAKING** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09THORIC | ITF_M | 0.2 | 4 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
