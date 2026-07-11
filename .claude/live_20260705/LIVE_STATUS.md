# LIVE VALIDATION — rolling status

- cycle 19 @ **2026-07-10 08:09:10 PM ET** | build `f30caf6d` | session boot 07-10 17:25 ET | log `live_v3_20260710.jsonl` | 4903 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 18:00 | ITFMATCH-26JUL10POLMIY-POL | ITF_M | underdog | 32 | 31 | +1 (place_cell) | — | pre | single |  | MIXED |
| 19:07 | ITFMATCH-26JUL10DELJAS-DEL | ITF_M | leader | 71 | 69 | +2 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 1 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 1} | repriceable now: true 1 / false 0 | **cumulative bid_grade lines: 7903 (repriceable true 1070 / false 6833)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL10DELJAS-JAS | 24 | 61m | 71/27-30/7147 | 28-28 | 3 | **FLOW_ABOVE** | 26 | REPRICEABLE→26 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL10POLMIY | 32 | 59 | **91** | 97 | -6 |
| ITFMATCH-26JUL10DELJAS | 71 | 28 | **99** | 97 | +2 |

## FLOW-STATE — 2 tracked game(s) ({'WAKING': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL10DELJAS | ITF_M | 3.767 | — | **WAKING** |
| ITFMATCH-26JUL10POLMIY | ITF_M | 27.5 | — | **WAKING** |

## PATTERNS (sub-B) — 8
- pre_conception_buy: KXITFMATCH-26JUL10POLMIY-POL {"price": 34, "conception_ts": 1783728028.7072625, "detail": "buy 34c predates the conception stamp by 154min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-10 08:09:10 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL10POLMIY-POL {"price": 34, "conception_ts": 1783728028.7072625, "detail": "buy 34c predates the conception stamp by 148min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-10 08:09:10 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL10POLMIY-POL {"price": 34, "conception_ts": 1783728028.7072625, "detail": "buy 34c predates the conception stamp by 146min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-10 08:09:10 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL10POLMIY-POL {"price": 34, "conception_ts": 1783728028.7072625, "detail": "buy 34c predates the conception stamp by 144min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-10 08:09:10 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL10POLMIY-POL {"price": 34, "conception_ts": 1783728028.7072625, "detail": "buy 34c predates the conception stamp by 143min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-10 08:09:10 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL10POLMIY-POL {"price": 32, "conception_ts": 1783728028.7072625, "detail": "buy 32c predates the conception stamp by 124min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-10 08:09:10 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL10POLMIY-POL {"fill": 32, "age_min": 128, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL10DELJAS-DEL {"fill": 71, "age_min": 61, "mode": "SET_BELOW_FLOW(prints 3c above)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
