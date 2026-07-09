# LIVE VALIDATION — rolling status

- cycle 14 @ **2026-07-09 05:48:44 PM ET** | build `e365c82` | session boot 07-09 15:50 ET | log `live_v3_20260709.jsonl` | 10546 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 5 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:50 | WTACHALLENGERMATCH-26JUL09STEROG-R | WTA_CHALL | ? | 17 | 14 | +3 (window_cell) | — | pre | single |  | MIXED |
| 15:50 | ATPCHALLENGERMATCH-26JUL09MEJROD-R | ATP_CHALL | ? | 19 | 16 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 15:50 | ITFMATCH-26JUL09GORARD-GOR | ITF_M | ? | 72 | 50 | +22 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 16:39 | ATPCHALLENGERMATCH-26JUL09CASAMB-A | ATP_CHALL | ? | 50 | 50 | +0 (window_cell) | -1.5 | pre | single |  | MIXED |
| 17:41 | ATPCHALLENGERMATCH-26JUL09JOHBLA-B | ATP_CHALL | ? | 69 | 78 | -9 (window_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 1 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 1} | repriceable now: true 0 / false 1 | **cumulative bid_grade lines: 7159 (repriceable true 881 / false 6278)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 118m | 8/83-84/176 | 80-83 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB | 50 | 36 | **86** | 97 | -11 |
| ATPCHALLENGERMATCH-26JUL09JOHBLA | 69 | 17 | **86** | 97 | -11 |
| WTACHALLENGERMATCH-26JUL09STEROG | 17 | 97 | **114** | 97 | +17 |
| ITFMATCH-26JUL09GORARD | 72 | 59 | **131** | 97 | +34 |

## FLOW-STATE — 6 tracked game(s) ({'WAKING': 3, 'QUIET': 2, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.233 | 3 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL09MEJROD | ATP_CHALL | 0.0 | — | **QUIET** |
| WTACHALLENGERMATCH-26JUL09STEROG | WTA_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL09CASAMB | ATP_CHALL | 62.267 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09JOHBLA | ATP_CHALL | 12.067 | — | **WAKING** |
| ITFMATCH-26JUL09GORARD | ITF_M | 62.467 | — | **WAKING** |

## PATTERNS (sub-B) — 4
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL09STEROG-ROG {"fill": 17, "age_min": 118, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL09MEJROD-ROD {"fill": 19, "age_min": 118, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL09GORARD-GOR {"fill": 72, "age_min": 118, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL09CASAMB-AMB {"fill": 50, "age_min": 69, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
