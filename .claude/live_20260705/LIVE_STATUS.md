# LIVE VALIDATION — rolling status

- cycle 27 @ **2026-07-09 08:01:55 PM ET** | build `f421175` | session boot 07-09 18:36 ET | log `live_v3_20260709.jsonl` | 2714 session events | monitor READ-ONLY
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
- classes now: {'FLOW_AT_LEVEL': 1, 'NO_FLOW': 2} | repriceable now: true 0 / false 3 | **cumulative bid_grade lines: 7180 (repriceable true 890 / false 6290)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM-DEL | 85 | 85m | 24/85-88/599 | 85-88 | 0 | **FLOW_AT_LEVEL** | 86 |  |
| ITFMATCH-26JUL09IMANAK-IMA | 53 | 4m | 0 | 53-54 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MOCJAS-MOC | 23 | 0m | 0 | 25-27 | — | **NO_FLOW** | 23 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL09DRAARS | 78 | 11 | **89** | 97 | -8 |
| ITFMATCH-26JUL09DELYAM | 11 | 88 | **99** | 97 | +2 |
| ITFMATCH-26JUL09MOCJAS | 74 | 27 | **101** | 97 | +4 |

## FLOW-STATE — 4 tracked game(s) ({'OPEN': 2, 'WAKING': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM | ITF_M | 0.767 | 1 | **OPEN** |
| ITFMATCH-26JUL09MOCJAS | ITF_M | 1.967 | 2 | **OPEN** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 25.033 | — | **WAKING** |
| ITFMATCH-26JUL09IMANAK | ITF_M | 0.1 | 1 | **WAKING** |

## PATTERNS (sub-B) — 2
- half_arm_aging: KXITFMATCH-26JUL09DELYAM-YAM {"fill": 11, "age_min": 85, "mode": "QUEUE(flow at/below our level, unfilled)"}
- half_arm_aging: KXITFMATCH-26JUL09DRAARS-DRA {"fill": 78, "age_min": 34, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
