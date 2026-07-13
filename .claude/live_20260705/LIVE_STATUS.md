# LIVE VALIDATION — rolling status

- cycle 131 @ **2026-07-13 07:31:46 PM ET** | build `8a769f41` | session boot 07-13 18:33 ET | log `live_v3_20260713.jsonl` | 5458 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 18:40:37 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 2140.6 |
| 18:43:04 | **self_fill_bell** | KXITFMATCH-26JUL13SIKSCH-SIK | own buys rose 15c (53->68) in 1800s -> match-live presumption, entry buys FROZEN |
| 19:28:59 | **self_fill_bell** | KXITFWMATCH-26JUL13SHIMIC-SHI | own buys rose 4c (78->82) in 1800s -> match-live presumption, entry buys FROZEN |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_self_fill_bell.md**

## FILLS — 0 graded (session)
none yet this session

## RESTING BIDS — 27 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 16, 'FLOW_ABOVE': 11} | repriceable now: true 8 / false 19 | **cumulative bid_grade lines: 9603 (repriceable true 1412 / false 8191)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI-DEM | 52 | 39m | 0 | 52-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-TRI | 16 | 39m | 0 | 16-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13FERMOC-FER | 48 | 57m | 2/50-50/99 | 48-50 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFMATCH-26JUL13JONELL-ELL | 76 | 57m | 2/78-78/10 | 76-78 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFMATCH-26JUL13JONELL-JON | 22 | 57m | 0 | 22-23 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SCH | 27 | 55m | 2/29-30/9 | 28-29 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ITFMATCH-26JUL13SIKSCH-SIK | 68 | 49m | 1/74-74/13 | 69-73 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13VANBAX-BAX | 20 | 57m | 0 | 23-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NONWAN-NON | 16 | 45m | 0 | 16-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NONWAN-WAN | 82 | 54m | 2/83-83/10 | 82-83 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→83 |
| ITFWMATCH-26JUL13RUSCAD-CAD | 17 | 54m | 0 | 18-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-RUS | 77 | 54m | 2/82-82/12 | 77-82 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-MIC | 16 | 52m | 2/21-21/33 | 16-17 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-SHI | 82 | 3m | 0 | 83-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SNICAI-CAI | 8 | 2m | 0 | 8-10 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SUBKAW-KAW | 15 | 56m | 1/18-18/78 | 15-17 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| ITFWMATCH-26JUL13SUBKAW-SUB | 83 | 22m | 2/85-85/1 | 83-85 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFWMATCH-26JUL13UEMWAN-UEM | 40 | 57m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-WAN | 55 | 57m | 0 | 55-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-STE | 32 | 45m | 0 | 32-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-WAR | 56 | 54m | 0 | 56-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-ARA | 22 | 39m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-WEB | 74 | 50m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-RUO | 19 | 57m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-ZHA | 79 | 57m | 1/81-81/0 | 79-81 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→81 |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 57m | 0 | 44-45 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 57m | 4/90-90/109 | 89-90 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 16 tracked game(s) ({'QUIET': 3, 'WAKING': 13}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.0 | 32 | **QUIET** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 0.0 | 26 | **QUIET** |
| ITFWMATCH-26JUL13WARSTE | ITF_W | 0.0 | 12 | **QUIET** |
| ITFMATCH-26JUL13FERMOC | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL13JONELL | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL13NONWAN | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 0.033 | 5 | **WAKING** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL13SNICAI | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL13SUBKAW | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL13UEMWAN | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13WEBARA | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL13ZHARUO | ITF_W | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.1 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
