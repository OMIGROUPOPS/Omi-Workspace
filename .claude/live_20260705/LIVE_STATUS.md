# LIVE VALIDATION — rolling status

- cycle 20 @ **2026-07-09 06:50:31 PM ET** | build `a4b4945` | session boot 07-09 18:36 ET | log `live_v3_20260709.jsonl` | 712 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 18:37 | ITFMATCH-26JUL09DELYAM-YAM | ITF_M | ? | 11 | 7 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 4 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 1, 'FLOW_ABOVE': 3} | repriceable now: true 2 / false 2 | **cumulative bid_grade lines: 7170 (repriceable true 887 / false 6283)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM-DEL | 85 | 14m | 4/88-88/47 | 85-88 | 3 | **FLOW_ABOVE** | 86 | REPRICEABLE→86 |
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 14m | 0 | 80-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MOCJAS-JAS | 72 | 14m | 6/77-77/68 | 72-76 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL09MOCJAS-MOC | 25 | 14m | 16/28-28/389 | 25-28 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→28 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM | 11 | 88 | **99** | 97 | +2 |

## FLOW-STATE — 3 tracked game(s) ({'OPEN': 2, 'WAKING': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM | ITF_M | 0.8 | 3 | **OPEN** |
| ITFMATCH-26JUL09MOCJAS | ITF_M | 1.2 | 3 | **OPEN** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.0 | 3 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
