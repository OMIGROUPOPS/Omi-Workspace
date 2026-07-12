# LIVE VALIDATION — rolling status

- cycle 5 @ **2026-07-12 05:02:01 PM ET** | build `3012148a` | session boot 07-12 16:20 ET | log `live_v3_20260712.jsonl` | 5995 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 16:21:08 | **self_fill_bell** | KXATPCHALLENGERMATCH-26JUL12RAIZHU-ZHU | own buys rose 6c (48->54) in 1800s -> match-live presumption, entry buys FROZEN |
| 16:23:27 | **chase_cap** | KXATPCHALLENGERMATCH-26JUL12YIBMAL-MAL | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 17) |

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:22 | ATPCHALLENGERMATCH-26JUL12CALRAD-R | ATP_CHALL | ? | 40 | 38 | +2 (window_cell) | — | pre | single |  | MIXED |
| 16:46 | ATPCHALLENGERMATCH-26JUL12YIBMAL-Y | ATP_CHALL | leader | 82 | 80 | +2 (place_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 5 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 3, 'NO_FLOW': 2} | repriceable now: true 0 / false 5 | **cumulative bid_grade lines: 8706 (repriceable true 1276 / false 7430)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL12MIYKUZ-K | 31 | 2m | 0 | 34-35 | — | **NO_FLOW** | 34 |  |
| ATPCHALLENGERMATCH-26JUL12RAIZHU-Z | 54 | 41m | 13/61-63/495 | 61-61 | 7 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL12YIBMAL-M | 15 | 15m | 1/17-17/27 | 16-17 | 2 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL12YOUDLI-D | 36 | 41m | 2/43-43/195 | 41-43 | 7 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 41m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL12CALRAD | 40 | 39 | **79** | 97 | -18 |
| ATPCHALLENGERMATCH-26JUL12YIBMAL | 82 | 17 | **99** | 97 | +2 |

## FLOW-STATE — 6 tracked game(s) ({'WAKING': 5, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL12YIBMAL | ATP_CHALL | 0.4 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL12CALRAD | ATP_CHALL | 4.233 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12MIYKUZ | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12RAIZHU | ATP_CHALL | 0.4 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12YOUDLI | ATP_CHALL | 0.067 | 2 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 2 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL12CALRAD-RAD {"fill": 40, "age_min": 40, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-12 05:02:01 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
