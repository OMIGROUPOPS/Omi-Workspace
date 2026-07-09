# LIVE VALIDATION — rolling status

- cycle 15 @ **2026-07-09 05:58:55 PM ET** | build `3cac9df` | session boot 07-09 17:53 ET | log `live_v3_20260709.jsonl` | 338 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:58 | ITFMATCH-26JUL09THORIC-RIC | ITF_M | leader | 80 | 76 | +4 (place_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 2 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 2} | repriceable now: true 0 / false 2 | **cumulative bid_grade lines: 7161 (repriceable true 881 / false 6280)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 5m | 0 | 80-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THORIC-THO | 16 | 1m | 0 | 18-21 | — | **NO_FLOW** | 17 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL09THORIC | 80 | 21 | **101** | 97 | +4 |

## FLOW-STATE — 2 tracked game(s) ({'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.233 | 3 | **OPEN** |
| ITFMATCH-26JUL09THORIC | ITF_M | 1.933 | 2 | **OPEN** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
