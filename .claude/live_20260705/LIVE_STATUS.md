# LIVE VALIDATION — rolling status

- cycle 39 @ **2026-07-09 10:04:08 PM ET** | build `cb9486f` | session boot 07-09 21:21 ET | log `live_v3_20260709.jsonl` | 2330 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:26 | ITFMATCH-26JUL09IMANAK-IMA | ITF_M | leader | 54 | 51 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 4 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 2, 'NO_FLOW': 2} | repriceable now: true 1 / false 3 | **cumulative bid_grade lines: 7193 (repriceable true 893 / false 6300)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM-YAM | 11 | 42m | 531/15-24/40391 | 19-16 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL09IMANAK-NAK | 43 | 38m | 64/45-48/2260 | 45-47 | 2 | **FLOW_ABOVE** | 43 | flow above but bound 43c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL10DYUSAG-DYU | 17 | 4m | 0 | 17-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL10YODJAN-JAN | 64 | 4m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK | 54 | 47 | **101** | 97 | +4 |

## FLOW-STATE — 4 tracked game(s) ({'WAKING': 3, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09IMANAK | ITF_M | 2.6 | 2 | **OPEN** |
| ITFMATCH-26JUL09DELYAM | ITF_M | 14.267 | — | **WAKING** |
| ITFWMATCH-26JUL10DYUSAG | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL10YODJAN | ITF_W | 0.133 | 2 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXITFMATCH-26JUL09IMANAK-IMA {"fill": 54, "age_min": 38, "mode": "SET_BELOW_FLOW(prints 2c above)", "emitted_et": "2026-07-09 10:04:08 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
