# LIVE VALIDATION — rolling status

- cycle 20 @ **2026-07-12 07:33:15 PM ET** | build `7fe4d1b3` | session boot 07-12 17:18 ET | log `live_v3_20260712.jsonl` | 8283 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 12 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 18:34:49 | **chase_cap** | KXITFWMATCH-26JUL12PANOUN-OUN | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 56) |
| 18:36:52 | **chase_cap** | KXITFWMATCH-26JUL12PANOUN-OUN | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 56) |
| 18:37:17 | **chase_cap** | KXITFWMATCH-26JUL12PANOUN-OUN | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 58) |
| 18:37:18 | **chase_cap** | KXITFWMATCH-26JUL12PANOUN-OUN | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 58) |
| 18:37:20 | **chase_cap** | KXITFWMATCH-26JUL12PANOUN-OUN | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 58) |
| 18:38:53 | **chase_cap** | KXITFWMATCH-26JUL12PANOUN-OUN | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 58) |
| 18:40:53 | **chase_cap** | KXITFWMATCH-26JUL12PANOUN-OUN | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 58) |
| 18:42:53 | **chase_cap** | KXITFWMATCH-26JUL12PANOUN-OUN | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 58) |
| 18:44:54 | **chase_cap** | KXITFWMATCH-26JUL12PANOUN-OUN | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 58) |
| 18:46:55 | **chase_cap** | KXITFWMATCH-26JUL12PANOUN-OUN | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 58) |
| 18:48:55 | **chase_cap** | KXITFWMATCH-26JUL12PANOUN-OUN | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 58) |
| 18:50:55 | **chase_cap** | KXITFWMATCH-26JUL12PANOUN-OUN | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 58) |

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 18:52 | ITFWMATCH-26JUL12PANOUN-OUN | ITF_W | leader | 55 | 53 | +2 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 1 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 1} | repriceable now: true 0 / false 1 | **cumulative bid_grade lines: 8715 (repriceable true 1276 / false 7439)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 133m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 2 tracked game(s) ({'WAKING': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL12PANOUN | ITF_W | 0.667 | — | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXITFWMATCH-26JUL12PANOUN-OUN {"fill": 55, "age_min": 41, "mode": "NO_BID(sib rested earlier, none now)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
