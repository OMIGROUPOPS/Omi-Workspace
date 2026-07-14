# LIVE VALIDATION — rolling status

- cycle 135 @ **2026-07-13 08:13:34 PM ET** | build `383bbf58` | session boot 07-13 18:33 ET | log `live_v3_20260713.jsonl` | 8712 session events | monitor READ-ONLY

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

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_taker_capped.md**

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:46 | ITFWMATCH-26JUL13SHIMIC-MIC | ITF_W | underdog | 16 | 11 | +5 (place_cell) | — | pre | single |  | PENDING |
| 19:59 | ITFMATCH-26JUL13SIKSCH-SCH | ITF_M | underdog | 27 | 26 | +1 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 25 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 14, 'FLOW_ABOVE': 11} | repriceable now: true 9 / false 16 | **cumulative bid_grade lines: 9612 (repriceable true 1415 / false 8197)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI-DEM | 52 | 81m | 0 | 52-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-TRI | 16 | 81m | 0 | 16-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13JONELL-ELL | 77 | 0m | 0 | 77-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13JONELL-JON | 22 | 99m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFMATCH-26JUL13SIKSCH-SIK | 68 | 90m | 76/71-81/1414 | 76-71 | 3 | **FLOW_ABOVE** | 70 | REPRICEABLE→70 |
| ITFMATCH-26JUL13VANBAX-BAX | 20 | 99m | 0 | 20-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BECMIL-BEC | 44 | 13m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NONWAN-NON | 16 | 87m | 11/17-18/2512 | 16-17 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→17 |
| ITFWMATCH-26JUL13NONWAN-WAN | 82 | 96m | 5/83-84/122 | 82-85 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→83 |
| ITFWMATCH-26JUL13RUSCAD-CAD | 17 | 96m | 2/23-24/12 | 18-22 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-RUS | 77 | 96m | 2/82-82/12 | 78-82 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13SNICAI-CAI | 8 | 44m | 1/10-10/28 | 8-10 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL13SNICAI-SNI | 90 | 19m | 0 | 90-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SUBKAW-KAW | 15 | 98m | 1/18-18/78 | 15-16 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| ITFWMATCH-26JUL13SUBKAW-SUB | 83 | 64m | 2/85-85/1 | 83-85 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFWMATCH-26JUL13UEMWAN-UEM | 40 | 99m | 0 | 40-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-WAN | 55 | 99m | 0 | 55-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-STE | 33 | 1m | 0 | 34-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-WAR | 57 | 1m | 0 | 57-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-ARA | 22 | 80m | 0 | 22-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-WEB | 74 | 92m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-RUO | 19 | 99m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-ZHA | 79 | 99m | 1/81-81/0 | 79-81 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→81 |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 98m | 0 | 44-45 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 99m | 10/90-90/345 | 89-90 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL13SIKSCH | 27 | 71 | **98** | 97 | +1 |

## FLOW-STATE — 16 tracked game(s) ({'QUIET': 2, 'WAKING': 13, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL13NONWAN | ITF_W | 0.467 | 1 | **OPEN** |
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.0 | 32 | **QUIET** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 0.0 | 29 | **QUIET** |
| ITFMATCH-26JUL13JONELL | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 5.167 | — | **WAKING** |
| ITFWMATCH-26JUL13BECMIL | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.1 | 3 | **WAKING** |
| ITFWMATCH-26JUL13SNICAI | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL13SUBKAW | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL13UEMWAN | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13WARSTE | ITF_W | 0.1 | 7 | **WAKING** |
| ITFWMATCH-26JUL13WEBARA | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13ZHARUO | ITF_W | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.1 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
