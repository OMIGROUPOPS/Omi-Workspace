# LIVE VALIDATION — rolling status

- cycle 123 @ **2026-07-13 06:10:22 PM ET** | build `622fd47c` | session boot 07-13 15:32 ET | log `live_v3_20260713.jsonl` | 9323 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 13 violation(s)
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

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:11 | ITFMATCH-26JUL13STEKOT-KOT | ITF_M | underdog | 20 | 20 | +0 (place_cell) | — | pre | single |  | PENDING |
| 17:41 | WTAMATCH-26JUL13BLISAS-SAS | WTA_MAIN | ? | 55 | 55 | +0 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 28 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 12, 'NO_FLOW': 16} | repriceable now: true 9 / false 19 | **cumulative bid_grade lines: 9536 (repriceable true 1402 / false 8134)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 158m | 5/59-60/26 | 59-60 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFMATCH-26JUL13DEMTRI-DEM | 51 | 18m | 0 | 51-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-TRI | 15 | 14m | 0 | 15-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13IBRCAM-IBR | 40 | 117m | 12/45-45/187 | 40-45 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SCH | 26 | 18m | 0 | 26-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SIK | 52 | 23m | 0 | 52-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13VANBAX-BAX | 23 | 17m | 0 | 23-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GILNAY-GIL | 63 | 55m | 2/69-69/8 | 63-67 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13GILNAY-NAY | 32 | 70m | 5/36-40/67 | 32-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFWMATCH-26JUL13NONWAN-NON | 15 | 10m | 0 | 15-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13NONWAN-WAN | 83 | 2m | 0 | 83-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13OHADOD-DOD | 25 | 86m | 8/29-30/132 | 25-29 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ITFWMATCH-26JUL13OHADOD-OHA | 70 | 102m | 5/75-76/146 | 70-75 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-CAD | 16 | 35m | 3/20-20/32 | 16-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL13RUSCAD-RUS | 79 | 6m | 0 | 79-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SATSCH-SAT | 68 | 0m | 0 | 69-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SATSCH-SCH | 13 | 3m | 0 | 13-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-MIC | 20 | 24m | 0 | 20-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-SHI | 59 | 6m | 0 | 59-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-STE | 31 | 11m | 0 | 31-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-RUO | 19 | 10m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-ZHA | 79 | 10m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 158m | 16/51-54/2497 | 53-54 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 158m | 2/60-60/32 | 59-60 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 158m | 11/41-41/1239 | 40-41 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 29m | 0 | 44-45 | — | **NO_FLOW** | 42 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 158m | 10/89-90/346 | 89-90 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 158m | 1/20-20/1 | 18-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTAMATCH-26JUL13BLISAS | 55 | 45 | **100** | 97 | +3 |

## FLOW-STATE — 19 tracked game(s) ({'WAKING': 14, 'QUIET': 4, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL13STEKOT | ITF_M | 0.633 | 3 | **OPEN** |
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.0 | 33 | **QUIET** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 0.0 | 26 | **QUIET** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.0 | 21 | **QUIET** |
| ITFWMATCH-26JUL13WARSTE | ITF_W | 0.0 | 26 | **QUIET** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL13IBRCAM | ITF_M | 0.1 | 5 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 0.033 | 22 | **WAKING** |
| ITFWMATCH-26JUL13GILNAY | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL13NONWAN | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL13OHADOD | ITF_W | 0.2 | 4 | **WAKING** |
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SATSCH | ITF_W | 0.1 | 6 | **WAKING** |
| ITFWMATCH-26JUL13ZHARUO | ITF_W | 0.0 | 2 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.1 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.367 | 1 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.1 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXITFMATCH-26JUL13STEKOT-KOT {"fill": 20, "age_min": 119, "mode": "NO_BID(sib rested earlier, none now)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
