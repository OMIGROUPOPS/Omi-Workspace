# LIVE VALIDATION — rolling status

- cycle 130 @ **2026-07-13 07:21:36 PM ET** | build `d418945c` | session boot 07-13 18:33 ET | log `live_v3_20260713.jsonl` | 5051 session events | monitor READ-ONLY

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

## RESTING BIDS — 26 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 18, 'FLOW_ABOVE': 8} | repriceable now: true 5 / false 21 | **cumulative bid_grade lines: 9598 (repriceable true 1409 / false 8189)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI-DEM | 52 | 29m | 0 | 52-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-TRI | 16 | 29m | 0 | 16-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13FERMOC-FER | 48 | 47m | 0 | 48-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13JONELL-ELL | 76 | 46m | 1/78-78/10 | 76-78 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFMATCH-26JUL13JONELL-JON | 22 | 47m | 0 | 22-23 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SCH | 27 | 45m | 2/29-30/9 | 28-29 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ITFMATCH-26JUL13SIKSCH-SIK | 68 | 39m | 1/74-74/13 | 69-73 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13VANBAX-BAX | 20 | 47m | 0 | 23-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NONWAN-NON | 16 | 35m | 0 | 16-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NONWAN-WAN | 82 | 44m | 1/83-83/10 | 82-83 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→83 |
| ITFWMATCH-26JUL13RUSCAD-CAD | 17 | 44m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-RUS | 77 | 44m | 1/82-82/12 | 77-82 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-MIC | 16 | 42m | 2/21-21/33 | 16-20 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-SHI | 80 | 1m | 0 | 80-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SUBKAW-KAW | 15 | 46m | 1/18-18/78 | 15-17 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| ITFWMATCH-26JUL13SUBKAW-SUB | 83 | 12m | 0 | 83-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-UEM | 40 | 47m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-WAN | 55 | 47m | 0 | 55-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-STE | 32 | 35m | 0 | 32-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-WAR | 56 | 44m | 0 | 56-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-ARA | 22 | 29m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-WEB | 74 | 40m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-RUO | 19 | 47m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-ZHA | 79 | 47m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 46m | 0 | 44-45 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 47m | 4/90-90/109 | 89-90 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 15 tracked game(s) ({'QUIET': 3, 'WAKING': 12}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.0 | 32 | **QUIET** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 0.0 | 26 | **QUIET** |
| ITFWMATCH-26JUL13WARSTE | ITF_W | 0.0 | 11 | **QUIET** |
| ITFMATCH-26JUL13FERMOC | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL13JONELL | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL13NONWAN | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 0.033 | 5 | **WAKING** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.067 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SUBKAW | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL13UEMWAN | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13WEBARA | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL13ZHARUO | ITF_W | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.1 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
