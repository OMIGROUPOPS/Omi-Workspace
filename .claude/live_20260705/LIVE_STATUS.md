# LIVE VALIDATION — rolling status

- cycle 139 @ **2026-07-13 08:54:49 PM ET** | build `14a4c198` | session boot 07-13 18:33 ET | log `live_v3_20260713.jsonl` | 12622 session events | monitor READ-ONLY

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

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:46 | ITFWMATCH-26JUL13SHIMIC-MIC | ITF_W | underdog | 16 | 11 | +5 (place_cell) | — | pre | single |  | PENDING |
| 19:59 | ITFMATCH-26JUL13SIKSCH-SCH | ITF_M | underdog | 27 | 26 | +1 (place_cell) | — | pre | pair | 95 | PENDING |
| 20:22 | ITFMATCH-26JUL13SIKSCH-SIK | ITF_M | leader | 68 | 71 | -3 (place_cell) | — | pre | pair | 95 | PENDING |

## RESTING BIDS — 21 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 11, 'FLOW_AT_LEVEL': 1, 'NO_FLOW': 9} | repriceable now: true 9 / false 12 | **cumulative bid_grade lines: 9627 (repriceable true 1419 / false 8208)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI-DEM | 63 | 1m | 0 | 70-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13DEMTRI-TRI | 21 | 13m | 0 | 21-27 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13JONELL-ELL | 77 | 41m | 8/78-79/624 | 77-79 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFMATCH-26JUL13JONELL-JON | 22 | 140m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ITFMATCH-26JUL13VANBAX-BAX | 31 | 16m | 0 | 31-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13VANBAX-VAN | 59 | 7m | 0 | 59-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13BECMIL-BEC | 44 | 54m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-CAD | 17 | 137m | 3/22-24/20 | 18-22 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13RUSCAD-RUS | 77 | 137m | 4/82-83/18 | 79-83 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13SNICAI-CAI | 8 | 85m | 2/10-10/33 | 8-10 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL13SNICAI-SNI | 90 | 60m | 0 | 90-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SUBKAW-KAW | 15 | 139m | 1/18-18/78 | 15-16 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| ITFWMATCH-26JUL13SUBKAW-SUB | 83 | 105m | 3/85-85/2 | 83-85 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFWMATCH-26JUL13UEMWAN-UEM | 40 | 140m | 3/40-45/436 | 40-45 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL13UEMWAN-WAN | 55 | 140m | 2/59-59/32 | 55-59 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFWMATCH-26JUL13WEBARA-ARA | 22 | 122m | 0 | 22-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WEBARA-WEB | 74 | 133m | 1/78-78/0 | 74-78 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL13ZHARUO-RUO | 19 | 140m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ZHARUO-ZHA | 79 | 140m | 2/81-81/0 | 79-81 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→81 |
| WTAMATCH-26JUL13BLISAS-BLI | 41 | 140m | 0 | 44-45 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 140m | 11/90-90/346 | 89-90 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 14 tracked game(s) ({'WAKING': 12, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL13JONELL | ITF_M | 0.267 | 1 | **OPEN** |
| ITFWMATCH-26JUL13SHIMIC | ITF_W | 0.267 | 3 | **OPEN** |
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.133 | 6 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 51.2 | — | **WAKING** |
| ITFMATCH-26JUL13VANBAX | ITF_M | 0.1 | 9 | **WAKING** |
| ITFWMATCH-26JUL13BECMIL | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL13RUSCAD | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SNICAI | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL13SUBKAW | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL13UEMWAN | ITF_W | 0.1 | 4 | **WAKING** |
| ITFWMATCH-26JUL13WEBARA | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL13ZHARUO | ITF_W | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.033 | 1 | **WAKING** |

## PATTERNS (sub-B) — 3
- half_arm_aging: KXITFWMATCH-26JUL13SHIMIC-MIC {"fill": 16, "age_min": 68, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL13SHIHAR-HAR {"kind": "position_basis", "ref": 60.0, "market_mid": 28.5, "divergence": 31.5}
- reality_divergence: KXITFMATCH-26JUL13IBRCAM-IBR {"kind": "position_basis", "ref": 40.0, "market_mid": 13.5, "divergence": 26.5}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
