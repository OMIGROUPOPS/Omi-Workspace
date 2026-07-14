# LIVE VALIDATION — rolling status

- cycle 142 @ **2026-07-13 09:26:26 PM ET** | build `f16e317e` | session boot 07-13 18:33 ET | log `live_v3_20260713.jsonl` | 14926 session events | monitor READ-ONLY

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

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_taker_capped.md**

## FILLS — 5 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:46 | ITFWMATCH-26JUL13SHIMIC-MIC | ITF_W | underdog | 16 | 11 | +5 (place_cell) | — | pre | single |  | PENDING |
| 19:59 | ITFMATCH-26JUL13SIKSCH-SCH | ITF_M | underdog | 27 | 26 | +1 (place_cell) | — | pre | pair | 95 | PENDING |
| 20:22 | ITFMATCH-26JUL13SIKSCH-SIK | ITF_M | leader | 68 | 71 | -3 (place_cell) | — | pre | pair | 95 | PENDING |
| 21:17 | ITFWMATCH-26JUL13RUSCAD-CAD | ITF_W | underdog | 17 | 12 | +5 (place_cell) | — | pre | pair | 94 | PENDING |
| 21:25 | ITFWMATCH-26JUL13RUSCAD-RUS | ITF_W | leader | 77 | 69 | +8 (place_cell) | — | pre | pair | 94 | PENDING |

## RESTING BIDS — 19 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 1, 'FLOW_ABOVE': 13, 'NO_FLOW': 5} | repriceable now: true 9 / false 10 | **cumulative bid_grade lines: 9635 (repriceable true 1420 / false 8215)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI-DEM | 63 | 25m | 2/72-73/13 | 64-73 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-TRI | 21 | 45m | 10/27-34/260 | 21-33 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13JONELL-ELL | 77 | 73m | 10/78-79/748 | 77-79 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFMATCH-26JUL13VANBAX-BAX | 31 | 47m | 2/36-36/57 | 31-36 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13VANBAX-VAN | 63 | 29m | 4/70-70/26 | 63-70 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13BECMIL-BEC | 44 | 86m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13LIXTIA-LIX | 56 | 26m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SNICAI-CAI | 8 | 116m | 4/10-10/126 | 8-10 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL13SNICAI-SNI | 90 | 92m | 0 | 90-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SUBKAW-KAW | 15 | 171m | 2/16-18/83 | 15-16 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→16 |
| ITFWMATCH-26JUL13SUBKAW-SUB | 83 | 137m | 3/85-85/2 | 83-85 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFWMATCH-26JUL13UEMWAN-UEM | 40 | 171m | 3/40-45/436 | 40-45 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-WAN | 55 | 171m | 4/59-60/189 | 55-60 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFWMATCH-26JUL13WEBARA-ARA | 22 | 153m | 0 | 22-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-WEB | 74 | 165m | 2/78-78/0 | 74-78 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL13ZHARUO-RUO | 19 | 171m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-ZHA | 79 | 171m | 3/81-81/121 | 79-81 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→81 |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 171m | 1/45-45/15 | 44-45 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 171m | 11/90-90/346 | 89-90 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 15 tracked game(s) ({'WAKING': 14, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 5.667 | 2 | **OPEN** |
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.4 | 9 | **WAKING** |
| ITFMATCH-26JUL13JONELL | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 49.267 | — | **WAKING** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 0.2 | 5 | **WAKING** |
| ITFWMATCH-26JUL13BECMIL | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13LIXTIA | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.8 | — | **WAKING** |
| ITFWMATCH-26JUL13SNICAI | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL13SUBKAW | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL13UEMWAN | ITF_W | 0.067 | 5 | **WAKING** |
| ITFWMATCH-26JUL13WEBARA | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL13ZHARUO | ITF_W | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 4
- half_arm_aging: KXITFWMATCH-26JUL13SHIMIC-MIC {"fill": 16, "age_min": 100, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL13SHIHAR-HAR {"kind": "position_basis", "ref": 60.0, "market_mid": 28.5, "divergence": 31.5}
- reality_divergence: KXITFMATCH-26JUL13IBRCAM-IBR {"kind": "position_basis", "ref": 40.0, "market_mid": 13.5, "divergence": 26.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL13SHIHAR-HAR {"kind": "position_basis", "ref": 60.0, "market_mid": 24.0, "divergence": 36.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
