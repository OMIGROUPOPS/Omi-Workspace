# LIVE VALIDATION — rolling status

- cycle 12 @ **2026-07-09 05:28:12 PM ET** | build `6f148f4` | session boot 07-09 15:50 ET | log `live_v3_20260709.jsonl` | 9922 session events | monitor READ-ONLY
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
- classes now: {'FLOW_ABOVE': 2} | repriceable now: true 0 / false 2 | **cumulative bid_grade lines: 7159 (repriceable true 881 / false 6278)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09JOHBLA-B | 69 | 97m | 26/80-83/3394 | 83-81 | 11 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFMATCH-26JUL09DRAARS-DRA | 78 | 97m | 2/83-83/2 | 80-83 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09CASAMB | 50 | 36 | **86** | 97 | -11 |
| WTACHALLENGERMATCH-26JUL09STEROG | 17 | 97 | **114** | 97 | +17 |
| ITFMATCH-26JUL09GORARD | 72 | 59 | **131** | 97 | +34 |

## FLOW-STATE — 6 tracked game(s) ({'WAKING': 5, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09MEJROD | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL09CASAMB | ATP_CHALL | 29.167 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09JOHBLA | ATP_CHALL | 0.767 | — | **WAKING** |
| ITFMATCH-26JUL09DRAARS | ITF_M | 0.067 | 3 | **WAKING** |
| ITFMATCH-26JUL09GORARD | ITF_M | 71.4 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL09STEROG | WTA_CHALL | 6.433 | — | **WAKING** |

## PATTERNS (sub-B) — 4
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL09STEROG-ROG {"fill": 17, "age_min": 97, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL09MEJROD-ROD {"fill": 19, "age_min": 97, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL09GORARD-GOR {"fill": 72, "age_min": 97, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL09CASAMB-AMB {"fill": 50, "age_min": 49, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
