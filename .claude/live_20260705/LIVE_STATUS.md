# LIVE VALIDATION — rolling status

- cycle 23 @ **2026-07-12 08:03:28 PM ET** | build `0dd6ac1f` | session boot 07-12 17:18 ET | log `live_v3_20260712.jsonl` | 10844 session events | monitor READ-ONLY

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

## RESTING BIDS — 2 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 2} | repriceable now: true 1 / false 1 | **cumulative bid_grade lines: 8718 (repriceable true 1277 / false 7441)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 164m | 1/59-59/16 | 57-59 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFWMATCH-26JUL12SUNYUN-YUN | 5 | 28m | 1/50-50/14 | 5-50 | 45 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 3 tracked game(s) ({'WAKING': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL12PANOUN | ITF_W | 0.267 | — | **WAKING** |
| ITFWMATCH-26JUL12SUNYUN | ITF_W | 0.033 | 45 | **WAKING** |

## PATTERNS (sub-B) — 2
- half_arm_aging: KXITFWMATCH-26JUL12PANOUN-OUN {"fill": 55, "age_min": 71, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXITFWMATCH-26JUL12SUNYUN-YUN {"kind": "resting_bid", "ref": 5.0, "market_mid": 47.5, "divergence": -42.5}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
