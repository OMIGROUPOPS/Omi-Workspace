# LIVE VALIDATION — rolling status

- cycle 146 @ **2026-07-13 10:07:26 PM ET** | build `3108b0f9` | session boot 07-13 18:33 ET | log `live_v3_20260713.jsonl` | 21847 session events | monitor READ-ONLY

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
| 19:59 | ITFMATCH-26JUL13SIKSCH-SCH | ITF_M | underdog | 27 | 26 | +1 (place_cell) | — | pre | pair | 95 | MIXED |
| 20:22 | ITFMATCH-26JUL13SIKSCH-SIK | ITF_M | leader | 68 | 71 | -3 (place_cell) | — | pre | pair | 95 | MIXED |
| 21:17 | ITFWMATCH-26JUL13RUSCAD-CAD | ITF_W | underdog | 17 | 12 | +5 (place_cell) | — | pre | pair | 94 | PENDING |
| 21:25 | ITFWMATCH-26JUL13RUSCAD-RUS | ITF_W | leader | 77 | 69 | +8 (place_cell) | — | pre | pair | 94 | PENDING |
| 21:29 | ITFMATCH-26JUL13VANBAX-BAX | ITF_M | ? | 31 | 27 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 21 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 2, 'FLOW_ABOVE': 14, 'NO_FLOW': 5} | repriceable now: true 14 / false 7 | **cumulative bid_grade lines: 9650 (repriceable true 1427 / false 8223)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI-DEM | 63 | 66m | 15/65-80/172 | 77-72 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFMATCH-26JUL13DEMTRI-TRI | 21 | 86m | 24/21-40/405 | 16-23 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL13JONELL-ELL | 77 | 114m | 10/78-79/748 | 77-79 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL13BECMIL-BEC | 44 | 127m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LIXTIA-LIX | 56 | 67m | 1/57-57/10 | 56-57 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| ITFWMATCH-26JUL13SNICAI-CAI | 9 | 40m | 4/10-10/20 | 9-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL13SNICAI-SNI | 90 | 133m | 1/91-91/0 | 90-91 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| ITFWMATCH-26JUL13SUBKAW-KAW | 15 | 212m | 7/16-18/217 | 15-16 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→16 |
| ITFWMATCH-26JUL13SUBKAW-SUB | 83 | 178m | 6/85-85/31 | 83-85 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFWMATCH-26JUL13UEMWAN-UEM | 40 | 212m | 3/40-45/436 | 40-44 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-WAN | 56 | 20m | 2/60-60/24 | 56-60 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL13WEBARA-ARA | 22 | 194m | 4/25-26/76 | 22-26 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→25 |
| ITFWMATCH-26JUL13WEBARA-WEB | 74 | 206m | 3/78-78/0 | 74-78 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL13ZHARUO-ZHA | 79 | 212m | 6/81-81/135 | 80-81 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→81 |
| ITFWMATCH-26JUL14DESKOR-DES | 66 | 7m | 0 | 66-71 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14DESKOR-KOR | 28 | 7m | 0 | 28-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14JANPAT-JAN | 91 | 7m | 0 | 91-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL14JANPAT-PAT | 5 | 7m | 1/9-9/20 | 5-9 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL14SUSSAM-SUS | 8 | 23m | 0 | 8-94 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 212m | 6/45-45/602 | 44-45 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 212m | 11/90-90/346 | 89-90 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 18 tracked game(s) ({'WAKING': 16, 'OPEN': 1, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL13SUBKAW | ITF_W | 0.233 | 1 | **OPEN** |
| ITFWMATCH-26JUL14SUSSAM | ITF_W | 0.0 | 86 | **QUIET** |
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.767 | 7 | **WAKING** |
| ITFMATCH-26JUL13JONELL | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 148.567 | — | **WAKING** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 2.033 | — | **WAKING** |
| ITFWMATCH-26JUL13BECMIL | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13LIXTIA | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 45.8 | — | **WAKING** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.733 | — | **WAKING** |
| ITFWMATCH-26JUL13SNICAI | ITF_W | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL13UEMWAN | ITF_W | 0.067 | 4 | **WAKING** |
| ITFWMATCH-26JUL13WEBARA | ITF_W | 0.167 | 4 | **WAKING** |
| ITFWMATCH-26JUL13ZHARUO | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL14DESKOR | ITF_W | 0.033 | 5 | **WAKING** |
| ITFWMATCH-26JUL14JANPAT | ITF_W | 0.167 | 2 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.1 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 9
- pre_conception_buy: KXITFMATCH-26JUL13SIKSCH-SCH {"price": 27, "conception_ts": 1783994400.4005694, "detail": "buy 27c predates the conception stamp by 205min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-13 10:07:26 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL13SIKSCH-SCH {"price": 18, "conception_ts": 1783994400.4005694, "detail": "buy 18c predates the conception stamp by 203min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-13 10:07:26 PM ET"}
- pre_conception_buy: KXITFMATCH-26JUL13SIKSCH-SCH {"price": 27, "conception_ts": 1783994400.4005694, "detail": "buy 27c predates the conception stamp by 203min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-13 10:07:26 PM ET"}
- half_arm_aging: KXITFWMATCH-26JUL13SHIMIC-MIC {"fill": 16, "age_min": 141, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL13SHIHAR-HAR {"kind": "position_basis", "ref": 60.0, "market_mid": 28.5, "divergence": 31.5}
- reality_divergence: KXITFMATCH-26JUL13IBRCAM-IBR {"kind": "position_basis", "ref": 40.0, "market_mid": 13.5, "divergence": 26.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL13SHIHAR-HAR {"kind": "position_basis", "ref": 60.0, "market_mid": 24.0, "divergence": 36.0}
- half_arm_aging: KXITFMATCH-26JUL13VANBAX-BAX {"fill": 31, "age_min": 38, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-13 10:07:26 PM ET"}
- reality_divergence: KXITFWMATCH-26JUL14SUSSAM-SUS {"kind": "resting_bid", "ref": 7.0, "market_mid": 51.0, "divergence": -44.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
