# LIVE VALIDATION — rolling status

- cycle 29 @ **2026-07-09 08:22:13 PM ET** | build `84f0ea4` | session boot 07-09 18:36 ET | log `live_v3_20260709.jsonl` | 3651 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 18:37 | ITFMATCH-26JUL09DELYAM-YAM | ITF_M | ? | 11 | 7 | +4 (fill_est) | — | pre | single |  | PENDING |
| 19:27 | ITFMATCH-26JUL09DRAARS-DRA | ITF_M | ? | 78 | 85 | -7 (window_cell) | — | pre | single |  | MIXED |
| 19:45 | ITFMATCH-26JUL09MOCJAS-JAS | ITF_M | leader | 74 | 69 | +5 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 3 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 1, 'FLOW_ABOVE': 2} | repriceable now: true 1 / false 2 | **cumulative bid_grade lines: 7182 (repriceable true 891 / false 6291)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM-DEL | 85 | 106m | 31/85-88/774 | 85-88 | 0 | **FLOW_AT_LEVEL** | 86 |  |
| ITFMATCH-26JUL09IMANAK-IMA | 53 | 25m | 20/54-57/3098 | 54-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL09MOCJAS-MOC | 22 | 17m | 21/28-29/787 | 25-27 | 6 | **FLOW_ABOVE** | 23 | flow above but bound 23c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL09DRAARS | 78 | 5 | **83** | 97 | -14 |
| ITFMATCH-26JUL09DELYAM | 11 | 88 | **99** | 97 | +2 |
| ITFMATCH-26JUL09MOCJAS | 74 | 27 | **101** | 97 | +4 |

## FLOW-STATE — 4 tracked game(s) ({'OPEN': 2, 'WAKING': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM | ITF_M | 1.0 | 1 | **OPEN** |
| ITFMATCH-26JUL09MOCJAS | ITF_M | 1.867 | 2 | **OPEN** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 27.067 | — | **WAKING** |
| ITFMATCH-26JUL09IMANAK | ITF_M | 0.667 | — | **WAKING** |

## PATTERNS (sub-B) — 3
- half_arm_aging: KXITFMATCH-26JUL09DELYAM-YAM {"fill": 11, "age_min": 105, "mode": "QUEUE(flow at/below our level, unfilled)"}
- half_arm_aging: KXITFMATCH-26JUL09DRAARS-DRA {"fill": 78, "age_min": 55, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL09MOCJAS-JAS {"fill": 74, "age_min": 37, "mode": "SET_BELOW_FLOW(prints 6c above)", "emitted_et": "2026-07-09 08:22:13 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
