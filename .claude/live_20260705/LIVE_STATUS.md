# LIVE VALIDATION — rolling status

- cycle 13 @ **2026-07-10 07:07:52 PM ET** | build `5d429923` | session boot 07-10 17:25 ET | log `live_v3_20260710.jsonl` | 3011 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 18:00 | ITFMATCH-26JUL10POLMIY-POL | ITF_M | underdog | 32 | 31 | +1 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 2 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 1, 'FLOW_ABOVE': 1} | repriceable now: true 1 / false 1 | **cumulative bid_grade lines: 7902 (repriceable true 1070 / false 6832)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10DELJAS-DEL | 71 | 8m | 11/71-72/667 | 72-72 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL10DELJAS-JAS | 27 | 8m | 11/29-32/351 | 28-28 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 2 tracked game(s) ({'WAKING': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10DELJAS | ITF_M | 2.567 | — | **WAKING** |
| ITFMATCH-26JUL10POLMIY | ITF_M | 97.2 | — | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXITFMATCH-26JUL10POLMIY-POL {"fill": 32, "age_min": 67, "mode": "PAIRING(sib never rested)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
