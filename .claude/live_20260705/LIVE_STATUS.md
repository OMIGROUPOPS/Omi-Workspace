# LIVE VALIDATION — rolling status

- cycle 132 @ **2026-07-13 07:42:06 PM ET** | build `93fefda6` | session boot 07-13 18:33 ET | log `live_v3_20260713.jsonl` | 5703 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 18:40:37 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 2140.6 |
| 18:43:04 | **self_fill_bell** | KXITFMATCH-26JUL13SIKSCH-SIK | own buys rose 15c (53->68) in 1800s -> match-live presumption, entry buys FROZEN |
| 19:28:59 | **self_fill_bell** | KXITFWMATCH-26JUL13SHIMIC-SHI | own buys rose 4c (78->82) in 1800s -> match-live presumption, entry buys FROZEN |

## FILLS — 0 graded (session)
none yet this session

## RESTING BIDS — 26 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 13, 'FLOW_ABOVE': 13} | repriceable now: true 9 / false 17 | **cumulative bid_grade lines: 9606 (repriceable true 1414 / false 8192)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI-DEM | 52 | 50m | 0 | 52-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-TRI | 16 | 50m | 0 | 16-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13JONELL-ELL | 76 | 67m | 2/78-78/10 | 76-78 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFMATCH-26JUL13JONELL-JON | 22 | 67m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFMATCH-26JUL13SIKSCH-SCH | 27 | 65m | 9/29-31/117 | 28-29 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ITFMATCH-26JUL13SIKSCH-SIK | 68 | 59m | 1/74-74/13 | 68-73 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13VANBAX-BAX | 20 | 67m | 0 | 23-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NONWAN-NON | 16 | 55m | 0 | 16-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NONWAN-WAN | 82 | 65m | 2/83-83/10 | 82-83 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→83 |
| ITFWMATCH-26JUL13RUSCAD-CAD | 17 | 64m | 2/23-24/12 | 18-24 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-RUS | 77 | 65m | 2/82-82/12 | 77-82 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-MIC | 16 | 63m | 2/21-21/33 | 16-17 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-SHI | 82 | 13m | 0 | 83-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SNICAI-CAI | 8 | 12m | 1/10-10/28 | 8-10 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL13SUBKAW-KAW | 15 | 67m | 1/18-18/78 | 15-17 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| ITFWMATCH-26JUL13SUBKAW-SUB | 83 | 33m | 2/85-85/1 | 83-85 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFWMATCH-26JUL13UEMWAN-UEM | 40 | 67m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-WAN | 55 | 67m | 0 | 55-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-STE | 32 | 55m | 0 | 32-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-WAR | 56 | 65m | 0 | 56-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-ARA | 22 | 49m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-WEB | 74 | 61m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-RUO | 19 | 67m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-ZHA | 79 | 67m | 1/81-81/0 | 79-81 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→81 |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 67m | 0 | 44-45 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 67m | 6/90-90/217 | 89-90 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 15 tracked game(s) ({'QUIET': 3, 'WAKING': 11, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL13SIKSCH | ITF_M | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.0 | 32 | **QUIET** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 0.0 | 26 | **QUIET** |
| ITFWMATCH-26JUL13WARSTE | ITF_W | 0.0 | 11 | **QUIET** |
| ITFMATCH-26JUL13JONELL | ITF_M | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL13NONWAN | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 0.1 | 5 | **WAKING** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL13SNICAI | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL13SUBKAW | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL13UEMWAN | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13WEBARA | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL13ZHARUO | ITF_W | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.067 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
