# LIVE VALIDATION — rolling status

- cycle 14 @ **2026-07-10 07:18:07 PM ET** | build `48e47fd3` | session boot 07-10 17:25 ET | log `live_v3_20260710.jsonl` | 3092 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 18:00 | ITFMATCH-26JUL10POLMIY-POL | ITF_M | underdog | 32 | 31 | +1 (place_cell) | — | pre | single |  | PENDING |
| 19:07 | ITFMATCH-26JUL10DELJAS-DEL | ITF_M | leader | 71 | 69 | +2 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 1 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 1} | repriceable now: true 0 / false 1 | **cumulative bid_grade lines: 7903 (repriceable true 1070 / false 6833)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10DELJAS-JAS | 24 | 10m | 8/30-30/1023 | 28-28 | 6 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL10DELJAS | 71 | 28 | **99** | 97 | +2 |

## FLOW-STATE — 2 tracked game(s) ({'WAKING': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10DELJAS | ITF_M | 3.033 | — | **WAKING** |
| ITFMATCH-26JUL10POLMIY | ITF_M | 116.8 | — | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXITFMATCH-26JUL10POLMIY-POL {"fill": 32, "age_min": 77, "mode": "PAIRING(sib never rested)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
