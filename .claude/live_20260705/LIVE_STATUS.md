# LIVE VALIDATION — rolling status

- cycle 122 @ **2026-07-13 05:59:59 PM ET** | build `97237edb` | session boot 07-13 15:32 ET | log `live_v3_20260713.jsonl` | 7583 session events | monitor READ-ONLY

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

## RESTING BIDS — 24 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 12, 'NO_FLOW': 12} | repriceable now: true 9 / false 15 | **cumulative bid_grade lines: 9528 (repriceable true 1402 / false 8126)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 147m | 5/59-60/26 | 59-60 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFMATCH-26JUL13DEMTRI-DEM | 51 | 8m | 0 | 51-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-TRI | 15 | 4m | 0 | 15-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13IBRCAM-IBR | 40 | 107m | 12/45-45/187 | 40-45 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SCH | 26 | 8m | 0 | 26-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SIK | 52 | 13m | 0 | 52-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13VANBAX-BAX | 23 | 7m | 0 | 23-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GILNAY-GIL | 63 | 45m | 2/69-69/8 | 63-67 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13GILNAY-NAY | 32 | 60m | 5/36-40/67 | 32-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFWMATCH-26JUL13OHADOD-DOD | 25 | 75m | 5/29-29/87 | 25-29 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ITFWMATCH-26JUL13OHADOD-OHA | 70 | 92m | 4/75-76/15 | 70-75 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-CAD | 16 | 24m | 3/20-20/32 | 16-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL13RUSCAD-RUS | 78 | 0m | 0 | 79-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SATSCH-SAT | 62 | 0m | 0 | 63-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SATSCH-SCH | 10 | 0m | 0 | 10-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-MIC | 20 | 14m | 0 | 20-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SHIMIC-SHI | 55 | 6m | 0 | 55-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WARSTE-STE | 31 | 1m | 0 | 31-57 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 147m | 14/51-54/2427 | 53-54 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 147m | 2/60-60/32 | 59-60 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 147m | 1/41-41/6 | 40-41 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 18m | 0 | 44-45 | — | **NO_FLOW** | 42 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 147m | 9/89-90/345 | 89-90 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 147m | 1/20-20/1 | 18-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| WTAMATCH-26JUL13BLISAS | 55 | 45 | **100** | 97 | +3 |

## FLOW-STATE — 17 tracked game(s) ({'WAKING': 12, 'QUIET': 4, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL13STEKOT | ITF_M | 0.667 | 2 | **OPEN** |
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.0 | 33 | **QUIET** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 0.0 | 26 | **QUIET** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.0 | 25 | **QUIET** |
| ITFWMATCH-26JUL13WARSTE | ITF_W | 0.0 | 26 | **QUIET** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL13IBRCAM | ITF_M | 0.1 | 5 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 0.033 | 22 | **WAKING** |
| ITFWMATCH-26JUL13GILNAY | ITF_W | 0.067 | 4 | **WAKING** |
| ITFWMATCH-26JUL13OHADOD | ITF_W | 0.167 | 4 | **WAKING** |
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 0.1 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SATSCH | ITF_W | 0.067 | 25 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.1 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXITFMATCH-26JUL13STEKOT-KOT {"fill": 20, "age_min": 109, "mode": "NO_BID(sib rested earlier, none now)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
