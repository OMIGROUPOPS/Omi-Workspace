# LIVE VALIDATION — rolling status

- cycle 31 @ **2026-07-09 08:42:38 PM ET** | build `e93d1c0` | session boot 07-09 18:36 ET | log `live_v3_20260709.jsonl` | 4152 session events | monitor READ-ONLY
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
- classes now: {'FLOW_ABOVE': 3} | repriceable now: true 2 / false 1 | **cumulative bid_grade lines: 7184 (repriceable true 892 / false 6292)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM-DEL | 86 | 4m | 2/87-88/10 | 87-88 | 1 | **FLOW_ABOVE** | 86 | flow above but bound 86c < flow -- chasing breaks goal |
| ITFMATCH-26JUL09IMANAK-IMA | 53 | 45m | 38/54-57/3513 | 54-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL09MOCJAS-MOC | 22 | 8m | 12/25-27/763 | 25-26 | 3 | **FLOW_ABOVE** | 23 | REPRICEABLE→23 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL09DRAARS | 78 | 2 | **80** | 97 | -17 |
| ITFMATCH-26JUL09DELYAM | 11 | 88 | **99** | 97 | +2 |
| ITFMATCH-26JUL09MOCJAS | 74 | 26 | **100** | 97 | +3 |

## FLOW-STATE — 4 tracked game(s) ({'OPEN': 2, 'WAKING': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM | ITF_M | 2.0 | 1 | **OPEN** |
| ITFMATCH-26JUL09MOCJAS | ITF_M | 3.267 | 1 | **OPEN** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 52.567 | — | **WAKING** |
| ITFMATCH-26JUL09IMANAK | ITF_M | 0.733 | — | **WAKING** |

## PATTERNS (sub-B) — 3
- half_arm_aging: KXITFMATCH-26JUL09DELYAM-YAM {"fill": 11, "age_min": 125, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFMATCH-26JUL09DRAARS-DRA {"fill": 78, "age_min": 75, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL09MOCJAS-JAS {"fill": 74, "age_min": 57, "mode": "SET_BELOW_FLOW(prints 3c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
