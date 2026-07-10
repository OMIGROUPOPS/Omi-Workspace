# LIVE VALIDATION — rolling status

- cycle 36 @ **2026-07-09 09:33:33 PM ET** | build `64cce57` | session boot 07-09 21:21 ET | log `live_v3_20260709.jsonl` | 725 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:26 | ITFMATCH-26JUL09IMANAK-IMA | ITF_M | leader | 54 | 51 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 3 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 3} | repriceable now: true 2 / false 1 | **cumulative bid_grade lines: 7190 (repriceable true 892 / false 6298)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM-YAM | 11 | 12m | 103/15-17/5568 | 16-16 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL09IMANAK-NAK | 43 | 7m | 6/48-48/222 | 45-48 | 5 | **FLOW_ABOVE** | 43 | flow above but bound 43c < flow -- chasing breaks goal |
| ITFMATCH-26JUL09MOCJAS-MOC | 22 | 12m | 47/26-27/1747 | 26-27 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK | 54 | 48 | **102** | 97 | +5 |

## FLOW-STATE — 3 tracked game(s) ({'WAKING': 1, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK | ITF_M | 1.467 | 2 | **OPEN** |
| ITFMATCH-26JUL09MOCJAS | ITF_M | 3.167 | 1 | **OPEN** |
| ITFMATCH-26JUL09DELYAM | ITF_M | 5.333 | — | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
