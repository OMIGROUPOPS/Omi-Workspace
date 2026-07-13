# LIVE VALIDATION — rolling status

- cycle 11 @ **2026-07-12 10:41:45 PM ET** | build `44c6ac8b` | session boot 07-12 20:59 ET | log `live_v3_20260712.jsonl` | 8815 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 21:03:06 | **chase_cap** | KXITFWMATCH-26JUL12SUNYUN-SUN | chase ladder refused: pursuit_buys 3 >= cap 2 (proposed 53) |
| 21:03:06 | **chase_cap** | KXITFWMATCH-26JUL12SUNYUN-YUN | chase ladder refused: pursuit_buys 3 >= cap 2 (proposed 8) |
| 21:06:16 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 846.3 |

## FILLS — 0 graded (session)
none yet this session

## RESTING BIDS — 2 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 1, 'FLOW_ABOVE': 1} | repriceable now: true 1 / false 1 | **cumulative bid_grade lines: 8725 (repriceable true 1278 / false 7447)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 101m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12SONSCH-SON | 65 | 101m | 147/68-70/21308 | 68-68 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 2 tracked game(s) ({'WAKING': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL12SONSCH | ATP_MAIN | 1.833 | — | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
