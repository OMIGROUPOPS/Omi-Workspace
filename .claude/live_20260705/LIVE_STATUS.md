# LIVE VALIDATION — rolling status

- cycle 125 @ **2026-07-13 06:30:45 PM ET** | build `4f6e7338` | session boot 07-13 15:32 ET | log `live_v3_20260713.jsonl` | 11465 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 14 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:38:15 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 1958.3 |
| 15:43:02 | **taker_capped** | KXITFWMATCH-26JUL13OLIKAI-KAI | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 15:43:03 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 15:53:02 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:03:03 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:11:18 | **taker_capped** | KXITFMATCH-26JUL13STEKOT-KOT | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:13:06 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:13:11 | **self_fill_bell** | KXITFMATCH-26JUL13IBRCAM-IBR | own buys rose 5c (35->40) in 1800s -> match-live presumption, entry buys FROZEN |
| 16:21:19 | **taker_capped** | KXITFMATCH-26JUL13STEKOT-KOT | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:23:11 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:31:22 | **taker_capped** | KXITFMATCH-26JUL13STEKOT-KOT | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 17:01:27 | **taker_capped** | KXITFMATCH-26JUL13STEKOT-KOT | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 17:11:32 | **taker_capped** | KXITFMATCH-26JUL13STEKOT-KOT | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 18:30:09 | **self_fill_bell** | KXITFWMATCH-26JUL13SATSCH-SAT | own buys rose 8c (62->70) in 1800s -> match-live presumption, entry buys FROZEN |

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:11 | ITFMATCH-26JUL13STEKOT-KOT | ITF_M | underdog | 20 | 20 | +0 (place_cell) | — | pre | single |  | PENDING |
| 17:41 | WTAMATCH-26JUL13BLISAS-SAS | WTA_MAIN | ? | 55 | 55 | +0 (fill_est) | — | pre | single |  | PENDING |
| 18:16 | ITFMATCH-26JUL13IBRCAM-IBR | ITF_M | underdog | 40 | 32 | +8 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 36 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 14, 'NO_FLOW': 22} | repriceable now: true 10 / false 26 | **cumulative bid_grade lines: 9554 (repriceable true 1403 / false 8151)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 178m | 5/59-60/26 | 59-60 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFMATCH-26JUL13DEMTRI-DEM | 51 | 38m | 0 | 51-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-TRI | 15 | 5m | 0 | 15-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13FERMOC-FER | 48 | 0m | 0 | 48-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13JONELL-ELL | 76 | 0m | 0 | 77-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13JONELL-JON | 21 | 0m | 0 | 21-23 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SCH | 26 | 38m | 0 | 26-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SIK | 53 | 19m | 1/74-74/1 | 53-74 | 21 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13VANBAX-BAX | 23 | 38m | 0 | 23-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GILNAY-GIL | 63 | 75m | 2/69-69/8 | 63-67 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13GILNAY-NAY | 32 | 91m | 5/36-40/67 | 32-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFWMATCH-26JUL13NONWAN-NON | 15 | 30m | 0 | 15-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NONWAN-WAN | 83 | 23m | 0 | 83-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13OHADOD-DOD | 25 | 106m | 9/29-30/133 | 25-29 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ITFWMATCH-26JUL13OHADOD-OHA | 70 | 122m | 8/75-76/158 | 70-75 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-CAD | 16 | 55m | 3/20-20/32 | 16-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL13RUSCAD-RUS | 79 | 27m | 0 | 79-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SATSCH-SAT | 70 | 1m | 0 | 71-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SATSCH-SCH | 13 | 24m | 5/18-34/90 | 14-27 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-MIC | 20 | 45m | 0 | 20-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-SHI | 71 | 2m | 0 | 72-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SUBKAW-KAW | 14 | 0m | 0 | 14-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SUBKAW-SUB | 83 | 0m | 0 | 83-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-UEM | 40 | 0m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-WAN | 55 | 0m | 0 | 55-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-STE | 31 | 31m | 0 | 31-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-ARA | 21 | 0m | 0 | 21-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-WEB | 74 | 0m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-RUO | 19 | 30m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-ZHA | 79 | 30m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 178m | 16/51-54/2497 | 53-54 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 178m | 3/60-60/34 | 59-60 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 178m | 11/41-41/1239 | 40-41 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 49m | 1/45-45/5 | 44-45 | 4 | **FLOW_ABOVE** | 42 | REPRICEABLE→42 |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 178m | 11/89-90/349 | 89-90 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 178m | 1/20-20/1 | 18-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTAMATCH-26JUL13BLISAS | 55 | 45 | **100** | 97 | +3 |

## FLOW-STATE — 24 tracked game(s) ({'WAKING': 20, 'QUIET': 3, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL13STEKOT | ITF_M | 0.5 | 1 | **OPEN** |
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.0 | 33 | **QUIET** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 0.0 | 26 | **QUIET** |
| ITFWMATCH-26JUL13WARSTE | ITF_W | 0.0 | 18 | **QUIET** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13FERMOC | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL13IBRCAM | ITF_M | 0.1 | 4 | **WAKING** |
| ITFMATCH-26JUL13JONELL | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 0.033 | 21 | **WAKING** |
| ITFWMATCH-26JUL13GILNAY | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13NONWAN | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL13OHADOD | ITF_W | 0.267 | 4 | **WAKING** |
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SATSCH | ITF_W | 0.233 | 13 | **WAKING** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13SUBKAW | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL13UEMWAN | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13WEBARA | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13ZHARUO | ITF_W | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.3 | 1 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 2
- half_arm_aging: KXITFMATCH-26JUL13STEKOT-KOT {"fill": 20, "age_min": 140, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTAMATCH-26JUL13BLISAS-SAS {"fill": 55, "age_min": 49, "mode": "SET_BELOW_FLOW(prints 4c above)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
