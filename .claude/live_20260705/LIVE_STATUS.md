# LIVE VALIDATION — rolling status

- cycle 42 @ **2026-07-09 10:34:49 PM ET** | build `e3f8d64` | session boot 07-09 22:09 ET | log `live_v3_20260709.jsonl` | 1620 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 22:19 | ITFMATCH-26JUL09DELYAM-YAM | ITF_M | ? | 11 | 7 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 9 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 3} | repriceable now: true 5 / false 4 | **cumulative bid_grade lines: 7208 (repriceable true 900 / false 6308)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK-NAK | 42 | 3m | 10/47-48/1049 | 45-47 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL10DYUSAG-DYU | 17 | 25m | 2/20-20/87 | 17-20 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL10DYUSAG-SAG | 80 | 25m | 2/82-82/11 | 80-82 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL10SHOKRO-KRO | 51 | 25m | 0 | 51-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SHOKRO-SHO | 44 | 25m | 3/46-46/434 | 44-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL10TUPMAK-MAK | 47 | 25m | 2/51-51/8 | 47-51 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| ITFWMATCH-26JUL10TUPMAK-TUP | 51 | 25m | 0 | 51-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10YODJAN-JAN | 64 | 25m | 5/66-66/47 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFWMATCH-26JUL10YODJAN-YOD | 34 | 25m | 0 | 34-35 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 6 tracked game(s) ({'WAKING': 5, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK | ITF_M | 3.633 | 2 | **OPEN** |
| ITFMATCH-26JUL09DELYAM | ITF_M | 59.533 | — | **WAKING** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 0.133 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 0.167 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
