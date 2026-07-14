# LIVE VALIDATION — rolling status

- cycle 136 @ **2026-07-13 08:23:45 PM ET** | build `a9dc5706` | session boot 07-13 18:33 ET | log `live_v3_20260713.jsonl` | 10272 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 6 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 18:40:37 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 2140.6 |
| 18:43:04 | **self_fill_bell** | KXITFMATCH-26JUL13SIKSCH-SIK | own buys rose 15c (53->68) in 1800s -> match-live presumption, entry buys FROZEN |
| 19:28:59 | **self_fill_bell** | KXITFWMATCH-26JUL13SHIMIC-SHI | own buys rose 4c (78->82) in 1800s -> match-live presumption, entry buys FROZEN |
| 19:46:40 | **taker_capped** | KXITFWMATCH-26JUL13SHIMIC-MIC | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 19:56:43 | **taker_capped** | KXITFWMATCH-26JUL13SHIMIC-MIC | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 20:09:32 | **taker_capped** | KXITFMATCH-26JUL13SIKSCH-SCH | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:46 | ITFWMATCH-26JUL13SHIMIC-MIC | ITF_W | underdog | 16 | 11 | +5 (place_cell) | — | pre | single |  | PENDING |
| 19:59 | ITFMATCH-26JUL13SIKSCH-SCH | ITF_M | underdog | 27 | 26 | +1 (place_cell) | — | pre | pair | 95 | PENDING |
| 20:22 | ITFMATCH-26JUL13SIKSCH-SIK | ITF_M | leader | 68 | 71 | -3 (place_cell) | — | pre | pair | 95 | PENDING |

## RESTING BIDS — 22 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 11, 'FLOW_ABOVE': 11} | repriceable now: true 8 / false 14 | **cumulative bid_grade lines: 9616 (repriceable true 1417 / false 8199)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI-DEM | 52 | 91m | 0 | 52-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-TRI | 16 | 91m | 0 | 16-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13JONELL-ELL | 77 | 10m | 0 | 77-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13JONELL-JON | 22 | 109m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFMATCH-26JUL13VANBAX-BAX | 20 | 109m | 0 | 20-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BECMIL-BEC | 44 | 23m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-CAD | 17 | 106m | 3/22-24/20 | 18-22 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-RUS | 77 | 106m | 3/82-82/18 | 79-82 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13SNICAI-CAI | 8 | 54m | 1/10-10/28 | 8-10 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL13SNICAI-SNI | 90 | 29m | 0 | 90-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SUBKAW-KAW | 15 | 108m | 1/18-18/78 | 15-16 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| ITFWMATCH-26JUL13SUBKAW-SUB | 83 | 74m | 2/85-85/1 | 83-85 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFWMATCH-26JUL13UEMWAN-UEM | 40 | 109m | 1/45-45/2 | 40-45 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-WAN | 55 | 109m | 1/59-59/32 | 55-59 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFWMATCH-26JUL13WARSTE-STE | 36 | 3m | 0 | 37-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-WAR | 57 | 11m | 3/61-64/22 | 57-61 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ITFWMATCH-26JUL13WEBARA-ARA | 22 | 91m | 0 | 22-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-WEB | 74 | 102m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-RUO | 19 | 109m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-ZHA | 79 | 109m | 1/81-81/0 | 79-81 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→81 |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 109m | 0 | 44-45 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 109m | 10/90-90/345 | 89-90 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 15 tracked game(s) ({'QUIET': 2, 'WAKING': 13}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.0 | 32 | **QUIET** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 0.0 | 29 | **QUIET** |
| ITFMATCH-26JUL13JONELL | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 12.4 | — | **WAKING** |
| ITFWMATCH-26JUL13BECMIL | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.267 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SNICAI | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL13SUBKAW | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL13UEMWAN | ITF_W | 0.067 | 4 | **WAKING** |
| ITFWMATCH-26JUL13WARSTE | ITF_W | 0.2 | 4 | **WAKING** |
| ITFWMATCH-26JUL13WEBARA | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13ZHARUO | ITF_W | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.1 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXITFWMATCH-26JUL13SHIMIC-MIC {"fill": 16, "age_min": 37, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-13 08:23:45 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
