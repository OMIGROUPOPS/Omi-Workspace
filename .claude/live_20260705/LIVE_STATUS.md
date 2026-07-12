# LIVE VALIDATION — rolling status

- cycle 2 @ **2026-07-12 04:31:44 PM ET** | build `6db605e9` | session boot 07-12 16:20 ET | log `live_v3_20260712.jsonl` | 2443 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 16:21:08 | **self_fill_bell** | KXATPCHALLENGERMATCH-26JUL12RAIZHU-ZHU | own buys rose 6c (48->54) in 1800s -> match-live presumption, entry buys FROZEN |
| 16:23:27 | **chase_cap** | KXATPCHALLENGERMATCH-26JUL12YIBMAL-MAL | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 17) |

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:22 | ATPCHALLENGERMATCH-26JUL12CALRAD-R | ATP_CHALL | ? | 40 | 38 | +2 (window_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 6 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 2, 'NO_FLOW': 3, 'FLOW_AT_LEVEL': 1} | repriceable now: true 0 / false 6 | **cumulative bid_grade lines: 8701 (repriceable true 1276 / false 7425)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL12CALRAD-C | 57 | 8m | 6/60-62/168 | 59-61 | 3 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL12MIYKUZ-K | 32 | 11m | 0 | 35-37 | — | **NO_FLOW** | 34 |  |
| ATPCHALLENGERMATCH-26JUL12RAIZHU-Z | 54 | 11m | 1/61-61/138 | 59-61 | 7 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL12YIBMAL-Y | 82 | 8m | 5/82-83/62 | 82-83 | 0 | **FLOW_AT_LEVEL** | 80 |  |
| ATPCHALLENGERMATCH-26JUL12YOUDLI-D | 36 | 11m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 11m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL12CALRAD | 40 | 61 | **101** | 97 | +4 |

## FLOW-STATE — 6 tracked game(s) ({'OPEN': 1, 'WAKING': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL12CALRAD | ATP_CHALL | 0.367 | 2 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL12MIYKUZ | ATP_CHALL | 0.033 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12RAIZHU | ATP_CHALL | 0.033 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12YIBMAL | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12YOUDLI | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 2 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
