# LIVE VALIDATION — rolling status

- cycle 127 @ **2026-07-13 06:51:11 PM ET** | build `e66420e3` | session boot 07-13 18:33 ET | log `live_v3_20260713.jsonl` | 2720 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 18:40:37 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 2140.6 |
| 18:43:04 | **self_fill_bell** | KXITFMATCH-26JUL13SIKSCH-SIK | own buys rose 15c (53->68) in 1800s -> match-live presumption, entry buys FROZEN |

## FILLS — 0 graded (session)
none yet this session

## RESTING BIDS — 27 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 24, 'FLOW_ABOVE': 3} | repriceable now: true 2 / false 25 | **cumulative bid_grade lines: 9582 (repriceable true 1405 / false 8177)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 16m | 1/60-60/118 | 59-60 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-DEM | 51 | 14m | 0 | 51-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-TRI | 15 | 8m | 0 | 15-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13FERMOC-FER | 48 | 16m | 0 | 48-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13JONELL-ELL | 76 | 16m | 1/78-78/10 | 76-78 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFMATCH-26JUL13JONELL-JON | 22 | 16m | 0 | 22-23 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SCH | 27 | 14m | 1/29-29/6 | 28-29 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ITFMATCH-26JUL13SIKSCH-SIK | 68 | 8m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13VANBAX-BAX | 20 | 16m | 0 | 21-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NONWAN-NON | 16 | 4m | 0 | 16-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NONWAN-WAN | 82 | 14m | 0 | 82-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-CAD | 17 | 13m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-RUS | 77 | 14m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-MIC | 16 | 12m | 0 | 16-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-SHI | 76 | 2m | 0 | 77-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SUBKAW-KAW | 15 | 16m | 0 | 15-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SUBKAW-SUB | 82 | 12m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-UEM | 40 | 16m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-WAN | 55 | 16m | 0 | 55-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-STE | 32 | 4m | 0 | 32-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-WAR | 56 | 14m | 0 | 56-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-ARA | 21 | 16m | 0 | 21-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-WEB | 74 | 10m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-RUO | 19 | 16m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-ZHA | 79 | 16m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 16m | 0 | 44-45 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 16m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 16 tracked game(s) ({'WAKING': 12, 'QUIET': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.0 | 33 | **QUIET** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 0.0 | 28 | **QUIET** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.0 | 7 | **QUIET** |
| ITFWMATCH-26JUL13WARSTE | ITF_W | 0.0 | 11 | **QUIET** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL13FERMOC | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL13JONELL | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL13NONWAN | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 0.233 | 5 | **WAKING** |
| ITFWMATCH-26JUL13SUBKAW | ITF_W | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL13UEMWAN | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13WEBARA | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13ZHARUO | ITF_W | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
