# LIVE VALIDATION — rolling status

- cycle 144 @ **2026-07-13 09:46:52 PM ET** | build `2db7c7e2` | session boot 07-13 18:33 ET | log `live_v3_20260713.jsonl` | 17325 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 10 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 18:40:37 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 2140.6 |
| 18:43:04 | **self_fill_bell** | KXITFMATCH-26JUL13SIKSCH-SIK | own buys rose 15c (53->68) in 1800s -> match-live presumption, entry buys FROZEN |
| 19:28:59 | **self_fill_bell** | KXITFWMATCH-26JUL13SHIMIC-SHI | own buys rose 4c (78->82) in 1800s -> match-live presumption, entry buys FROZEN |
| 19:46:40 | **taker_capped** | KXITFWMATCH-26JUL13SHIMIC-MIC | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 19:56:43 | **taker_capped** | KXITFWMATCH-26JUL13SHIMIC-MIC | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 20:09:32 | **taker_capped** | KXITFMATCH-26JUL13SIKSCH-SCH | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 21:01:43 | **self_fill_bell** | KXITFMATCH-26JUL13DEMTRI-DEM | own buys rose 8c (55->63) in 1800s -> match-live presumption, entry buys FROZEN |
| 21:09:15 | **taker_capped** | KXITFWMATCH-26JUL13SHIMIC-MIC | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 21:17:33 | **taker_capped** | KXITFWMATCH-26JUL13RUSCAD-CAD | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 21:18:18 | **bell_missing** | KXITFMATCH-26JUL13VANBAX | min_past_start 10.3 |

## FILLS — 6 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:46 | ITFWMATCH-26JUL13SHIMIC-MIC | ITF_W | underdog | 16 | 11 | +5 (place_cell) | — | pre | single |  | PENDING |
| 19:59 | ITFMATCH-26JUL13SIKSCH-SCH | ITF_M | underdog | 27 | 26 | +1 (place_cell) | — | pre | pair | 95 | PENDING |
| 20:22 | ITFMATCH-26JUL13SIKSCH-SIK | ITF_M | leader | 68 | 71 | -3 (place_cell) | — | pre | pair | 95 | PENDING |
| 21:17 | ITFWMATCH-26JUL13RUSCAD-CAD | ITF_W | underdog | 17 | 12 | +5 (place_cell) | — | pre | pair | 94 | PENDING |
| 21:25 | ITFWMATCH-26JUL13RUSCAD-RUS | ITF_W | leader | 77 | 69 | +8 (place_cell) | — | pre | pair | 94 | PENDING |
| 21:29 | ITFMATCH-26JUL13VANBAX-BAX | ITF_M | ? | 31 | 27 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 18 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 1, 'FLOW_ABOVE': 13, 'NO_FLOW': 4} | repriceable now: true 11 / false 7 | **cumulative bid_grade lines: 9642 (repriceable true 1424 / false 8218)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI-DEM | 63 | 45m | 6/68-79/53 | 73-72 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-TRI | 21 | 65m | 14/27-40/271 | 21-29 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13JONELL-ELL | 77 | 93m | 10/78-79/748 | 77-79 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL13BECMIL-BEC | 44 | 106m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LIXTIA-LIX | 56 | 46m | 1/57-57/10 | 56-57 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFWMATCH-26JUL13SNICAI-CAI | 9 | 20m | 2/10-10/11 | 9-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL13SNICAI-SNI | 90 | 112m | 0 | 90-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SUBKAW-KAW | 15 | 191m | 2/16-18/83 | 15-16 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→16 |
| ITFWMATCH-26JUL13SUBKAW-SUB | 83 | 157m | 5/85-85/29 | 83-85 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFWMATCH-26JUL13UEMWAN-UEM | 40 | 192m | 3/40-45/436 | 40-43 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-WAN | 55 | 2m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-ARA | 22 | 174m | 2/25-26/55 | 22-25 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→25 |
| ITFWMATCH-26JUL13WEBARA-WEB | 74 | 185m | 2/78-78/0 | 74-78 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL13ZHARUO-RUO | 19 | 192m | 1/20-20/4 | 19-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFWMATCH-26JUL13ZHARUO-ZHA | 79 | 192m | 4/81-81/127 | 79-81 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→81 |
| ITFWMATCH-26JUL14SUSSAM-SUS | 8 | 2m | 0 | 8-94 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 192m | 6/45-45/602 | 44-45 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 192m | 11/90-90/346 | 89-90 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 16 tracked game(s) ({'WAKING': 15, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL14SUSSAM | ITF_W | 0.0 | 86 | **QUIET** |
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.433 | 8 | **WAKING** |
| ITFMATCH-26JUL13JONELL | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 91.7 | — | **WAKING** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL13BECMIL | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13LIXTIA | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 25.967 | — | **WAKING** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.533 | — | **WAKING** |
| ITFWMATCH-26JUL13SNICAI | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL13SUBKAW | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL13UEMWAN | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL13WEBARA | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL13ZHARUO | ITF_W | 0.1 | 1 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.2 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 5
- half_arm_aging: KXITFWMATCH-26JUL13SHIMIC-MIC {"fill": 16, "age_min": 120, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL13SHIHAR-HAR {"kind": "position_basis", "ref": 60.0, "market_mid": 28.5, "divergence": 31.5}
- reality_divergence: KXITFMATCH-26JUL13IBRCAM-IBR {"kind": "position_basis", "ref": 40.0, "market_mid": 13.5, "divergence": 26.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL13SHIHAR-HAR {"kind": "position_basis", "ref": 60.0, "market_mid": 24.0, "divergence": 36.0}
- reality_divergence: KXITFWMATCH-26JUL14SUSSAM-SUS {"kind": "resting_bid", "ref": 7.0, "market_mid": 51.0, "divergence": -44.0, "emitted_et": "2026-07-13 09:46:52 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
