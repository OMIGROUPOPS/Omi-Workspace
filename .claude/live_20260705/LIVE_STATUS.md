# LIVE VALIDATION — rolling status

- cycle 9 @ **2026-07-09 04:57:29 PM ET** | build `583569f` | session boot 07-09 15:50 ET | log `live_v3_20260709.jsonl` | 8379 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 4 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:50 | WTACHALLENGERMATCH-26JUL09STEROG-R | WTA_CHALL | ? | 17 | 14 | +3 (window_cell) | — | pre | single |  | MIXED |
| 15:50 | ATPCHALLENGERMATCH-26JUL09MEJROD-R | ATP_CHALL | ? | 19 | 16 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 15:50 | ITFMATCH-26JUL09GORARD-GOR | ITF_M | ? | 72 | 50 | +22 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 16:39 | ATPCHALLENGERMATCH-26JUL09CASAMB-A | ATP_CHALL | ? | 50 | 50 | +0 (window_cell) | -1.5 | pre | single |  | MIXED |

## RESTING BIDS — 2 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 1, 'NO_FLOW': 1} | repriceable now: true 0 / false 2 | **cumulative bid_grade lines: 7158 (repriceable true 881 / false 6277)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09JOHBLA-B | 69 | 67m | 3/81-81/75 | 80-81 | 12 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 67m | 0 | 80-83 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTACHALLENGERMATCH-26JUL09STEROG | 17 | 95 | **112** | 97 | +15 |
| ATPCHALLENGERMATCH-26JUL09CASAMB | 50 | 62 | **112** | 97 | +15 |
| ITFMATCH-26JUL09GORARD | 72 | 72 | **144** | 97 | +47 |

## FLOW-STATE — 6 tracked game(s) ({'WAKING': 4, 'QUIET': 1, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| WTACHALLENGERMATCH-26JUL09STEROG | WTA_CHALL | 8.8 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL09MEJROD | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL09CASAMB | ATP_CHALL | 5.867 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09JOHBLA | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09GORARD | ITF_M | 30.4 | — | **WAKING** |

## PATTERNS (sub-B) — 3
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL09STEROG-ROG {"fill": 17, "age_min": 67, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL09MEJROD-ROD {"fill": 19, "age_min": 67, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL09GORARD-GOR {"fill": 72, "age_min": 67, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
