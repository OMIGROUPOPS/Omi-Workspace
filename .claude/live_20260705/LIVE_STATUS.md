# LIVE VALIDATION — rolling status

- cycle 25 @ **2026-07-09 07:41:33 PM ET** | build `feb069f` | session boot 07-09 18:36 ET | log `live_v3_20260709.jsonl` | 2434 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 18:37 | ITFMATCH-26JUL09DELYAM-YAM | ITF_M | ? | 11 | 7 | +4 (fill_est) | — | pre | single |  | PENDING |
| 19:27 | ITFMATCH-26JUL09DRAARS-DRA | ITF_M | ? | 78 | 75 | +3 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 4 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 2, 'FLOW_ABOVE': 1, 'NO_FLOW': 1} | repriceable now: true 1 / false 3 | **cumulative bid_grade lines: 7176 (repriceable true 889 / false 6287)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM-DEL | 85 | 65m | 18/85-88/447 | 85-88 | 0 | **FLOW_AT_LEVEL** | 86 |  |
| ITFMATCH-26JUL09IMANAK-IMA | 52 | 11m | 0 | 52-54 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MOCJAS-JAS | 73 | 31m | 16/77-77/538 | 73-75 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| ITFMATCH-26JUL09MOCJAS-MOC | 25 | 65m | 34/25-28/658 | 25-27 | 0 | **FLOW_AT_LEVEL** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM | 11 | 88 | **99** | 97 | +2 |

## FLOW-STATE — 4 tracked game(s) ({'OPEN': 2, 'WAKING': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09DELYAM | ITF_M | 1.233 | 1 | **OPEN** |
| ITFMATCH-26JUL09MOCJAS | ITF_M | 0.867 | 2 | **OPEN** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 20.667 | — | **WAKING** |
| ITFMATCH-26JUL09IMANAK | ITF_M | 0.0 | 2 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXITFMATCH-26JUL09DELYAM-YAM {"fill": 11, "age_min": 64, "mode": "QUEUE(flow at/below our level, unfilled)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
