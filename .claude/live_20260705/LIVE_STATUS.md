# LIVE VALIDATION — rolling status

- cycle 41 @ **2026-07-09 10:24:38 PM ET** | build `1d91e96` | session boot 07-09 22:09 ET | log `live_v3_20260709.jsonl` | 1079 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 22:19 | ITFMATCH-26JUL09DELYAM-YAM | ITF_M | ? | 11 | 7 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 8 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 4, 'NO_FLOW': 4} | repriceable now: true 4 / false 4 | **cumulative bid_grade lines: 7206 (repriceable true 899 / false 6307)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFWMATCH-26JUL10DYUSAG-DYU | 17 | 15m | 1/20-20/85 | 17-20 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL10DYUSAG-SAG | 80 | 15m | 2/82-82/11 | 80-82 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ITFWMATCH-26JUL10SHOKRO-KRO | 51 | 15m | 0 | 51-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10SHOKRO-SHO | 44 | 15m | 1/46-46/6 | 44-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL10TUPMAK-MAK | 47 | 15m | 0 | 47-51 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10TUPMAK-TUP | 51 | 15m | 0 | 51-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10YODJAN-JAN | 64 | 15m | 1/66-66/4 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFWMATCH-26JUL10YODJAN-YOD | 34 | 15m | 0 | 34-35 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 5 tracked game(s) ({'WAKING': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM | ITF_M | 55.233 | — | **WAKING** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL10SHOKRO | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL10TUPMAK | ITF_W | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 0.033 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
