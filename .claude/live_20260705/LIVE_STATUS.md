# LIVE VALIDATION — rolling status

- cycle 38 @ **2026-07-09 09:53:58 PM ET** | build `f2ff4b6` | session boot 07-09 21:21 ET | log `live_v3_20260709.jsonl` | 1606 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:26 | ITFMATCH-26JUL09IMANAK-IMA | ITF_M | leader | 54 | 51 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 2 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 2} | repriceable now: true 1 / false 1 | **cumulative bid_grade lines: 7191 (repriceable true 893 / false 6298)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM-YAM | 11 | 32m | 265/15-17/24755 | 16-16 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL09IMANAK-NAK | 43 | 27m | 52/45-48/2085 | 45-47 | 2 | **FLOW_ABOVE** | 43 | flow above but bound 43c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK | 54 | 47 | **101** | 97 | +4 |

## FLOW-STATE — 2 tracked game(s) ({'WAKING': 1, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK | ITF_M | 3.0 | 2 | **OPEN** |
| ITFMATCH-26JUL09DELYAM | ITF_M | 8.233 | — | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
