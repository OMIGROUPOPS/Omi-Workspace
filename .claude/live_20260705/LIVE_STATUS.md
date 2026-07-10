# LIVE VALIDATION — rolling status

- cycle 16 @ **2026-07-10 07:38:33 PM ET** | build `b39bf3a2` | session boot 07-10 17:25 ET | log `live_v3_20260710.jsonl` | 3365 session events | monitor READ-ONLY

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
- classes now: {'FLOW_ABOVE': 1} | repriceable now: true 1 / false 0 | **cumulative bid_grade lines: 7903 (repriceable true 1070 / false 6833)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10DELJAS-JAS | 24 | 30m | 19/28-30/1487 | 28-28 | 4 | **FLOW_ABOVE** | 26 | REPRICEABLE→26 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL10DELJAS | 71 | 28 | **99** | 97 | +2 |

## FLOW-STATE — 2 tracked game(s) ({'WAKING': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10DELJAS | ITF_M | 2.267 | — | **WAKING** |
| ITFMATCH-26JUL10POLMIY | ITF_M | 121.967 | — | **WAKING** |

## PATTERNS (sub-B) — 2
- half_arm_aging: KXITFMATCH-26JUL10POLMIY-POL {"fill": 32, "age_min": 98, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL10DELJAS-DEL {"fill": 71, "age_min": 31, "mode": "SET_BELOW_FLOW(prints 4c above)", "emitted_et": "2026-07-10 07:38:33 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
