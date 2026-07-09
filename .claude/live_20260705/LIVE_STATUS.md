# LIVE VALIDATION — rolling status

- cycle 17 @ **2026-07-09 06:19:23 PM ET** | build `49ea9d2` | session boot 07-09 17:53 ET | log `live_v3_20260709.jsonl` | 1874 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:58 | ITFMATCH-26JUL09THORIC-RIC | ITF_M | leader | 80 | 76 | +4 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 18:08 | ITFMATCH-26JUL09THORIC-THO | ITF_M | underdog | 16 | 14 | +2 (place_cell) | — | pre | pair | 96 | EARNED |

## RESTING BIDS — 5 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 5} | repriceable now: true 4 / false 1 | **cumulative bid_grade lines: 7166 (repriceable true 885 / false 6281)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM-DEL | 85 | 19m | 1/88-88/1 | 85-88 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→88 |
| ITFMATCH-26JUL09DELYAM-YAM | 11 | 19m | 23/15-16/1150 | 12-12 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 25m | 2/83-83/11 | 80-83 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL09MOCJAS-JAS | 72 | 19m | 9/75-77/223 | 72-75 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| ITFMATCH-26JUL09MOCJAS-MOC | 25 | 19m | 16/27-28/494 | 25-27 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 4 tracked game(s) ({'OPEN': 2, 'WAKING': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM | ITF_M | 1.1 | 3 | **OPEN** |
| ITFMATCH-26JUL09MOCJAS | ITF_M | 0.833 | 2 | **OPEN** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.1 | 3 | **WAKING** |
| ITFMATCH-26JUL09THORIC | ITF_M | 2.833 | 4 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
