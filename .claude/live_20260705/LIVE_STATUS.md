# LIVE VALIDATION — rolling status

- cycle 133 @ **2026-07-15 03:03:40 PM ET** | build `ebca40fa` | session boot 07-15 14:35 ET | log `live_v3_20260715.jsonl` | 3287 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- placed:path_aim UL15PERDIG-DIG aim=6 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 8 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 14:38:27 | **bell_missing** | KXATPCHALLENGERMATCH-26JUL15YIBYUN | min_past_start 38.5 |
| 14:38:27 | **bell_missing** | KXITFMATCH-26JUL15PECJAN | min_past_start 13.5 |
| 14:38:27 | **bell_missing** | KXITFWMATCH-26JUL15RAILEW | min_past_start 13.5 |
| 14:38:27 | **bell_missing** | KXITFWMATCH-26JUL15CROGRU | min_past_start 13.5 |
| 14:41:14 | **bell_missing** | KXITFMATCH-26JUL15FITLYN | min_past_start 11.2 |
| 14:41:14 | **bell_missing** | KXITFWMATCH-26JUL15MATSHC | min_past_start 11.2 |
| 14:52:54 | **taker_capped** | KXITFMATCH-26JUL15PECJAN-PEC | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 14:54:37 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL15YIBYUN-YUN | flatten DEFERRED: ev -2.56 above margin floor -3.0 |

## FILLS — 4 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:37 | ITFMATCH-26JUL15LONMIL-MIL | ITF_M | ? | 50 | 47 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:37 | ITFMATCH-26JUL15LERHUR-LER | ITF_M | ? | 19 | 15 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:51 | ITFMATCH-26JUL15PECJAN-PEC | ITF_M | ? | 16 | 18 | -2 (window_cell) | — | pre | single |  | EARNED |
| 14:53 | ATPCHALLENGERMATCH-26JUL15YIBYUN-Y | ATP_CHALL | ? | 42 | 39 | +3 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 35 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 11, 'NO_FLOW': 24} | repriceable now: true 2 / false 33 | **cumulative bid_grade lines: 11362 (repriceable true 1548 / false 9814)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL14VUKARS-A | 18 | 26m | 0 | 20-22 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15IVACRA-C | 59 | 26m | 5/66-66/171 | 65-66 | 7 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL15IVACRA-I | 32 | 26m | 1/36-36/13 | 34-36 | 4 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL15LAJKRU-K | 28 | 26m | 1/33-33/14 | 32-33 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15LAJKRU-L | 64 | 26m | 0 | 68-69 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15NAGTOR-N | 56 | 26m | 0 | 60-61 | — | **NO_FLOW** | 58 |  |
| ATPCHALLENGERMATCH-26JUL15NAGTOR-T | 36 | 26m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15YIBYUN-Y | 53 | 26m | 0 | 56-57 | — | **NO_FLOW** | 55 |  |
| ATPMATCH-26JUL15BASTIR-TIR | 65 | 26m | 1/69-69/7 | 68-69 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ATPMATCH-26JUL15PRIMOL-PRI | 65 | 26m | 17/73-74/2619 | 72-73 | 8 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15RUBPEL-PEL | 27 | 26m | 0 | 29-30 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15RUBPEL-RUB | 71 | 26m | 0 | 72-73 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BERKLI-BER | 55 | 26m | 0 | 56-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BERKLI-KLI | 17 | 2m | 0 | 21-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MESBAR-BAR | 66 | 26m | 10/78-84/1272 | 80-84 | 12 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFMATCH-26JUL15MESBAR-MES | 11 | 26m | 3/18-20/13 | 16-19 | 7 | **FLOW_ABOVE** | 16 | flow above but bound 16c < flow -- chasing breaks goal |
| ITFMATCH-26JUL15NOCMEC-MEC | 31 | 2m | 0 | 33-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15NOCMEC-NOC | 23 | 26m | 5/38-43/227 | 38-42 | 15 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15PALVAN-VAN | 11 | 26m | 0 | 17-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15RODPOW-POW | 48 | 26m | 0 | 61-69 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15RODPOW-ROD | 16 | 26m | 0 | 34-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15STHALM-ALM | 43 | 26m | 0 | 59-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15STHALM-STH | 22 | 26m | 0 | 35-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WILFAL-FAL | 11 | 26m | 0 | 16-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WILFAL-WIL | 66 | 2m | 0 | 67-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15FULMOY-FUL | 44 | 26m | 0 | 57-62 | — | **NO_FLOW** | 60 |  |
| ITFWMATCH-26JUL15FULMOY-MOY | 28 | 26m | 0 | 37-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15KONPED-KON | 5 | 26m | 0 | 7-17 | — | **NO_FLOW** | 9 |  |
| ITFWMATCH-26JUL15MATSHC-MAT | 17 | 26m | 1/35-35/3 | 28-35 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15MATSHC-SHC | 55 | 26m | 1/70-70/6 | 67-70 | 15 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15PONSAN-SAN | 82 | 26m | 0 | 94-98 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15RAILEW-LEW | 29 | 26m | 0 | 42-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15RAILEW-RAI | 44 | 26m | 0 | 45-55 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15KREMON-MON | 8 | 26m | 1/10-10/9 | 9-10 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| WTAMATCH-26JUL15SHEQUE-QUE | 32 | 26m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15YIBYUN | 42 | 57 | **99** | 97 | +2 |
| ITFMATCH-26JUL15PECJAN | 16 | 88 | **104** | 97 | +7 |

## FLOW-STATE — 25 tracked game(s) ({'WAKING': 17, 'OPEN': 4, 'QUIET': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL15PRIMOL | ATP_MAIN | 0.567 | 1 | **OPEN** |
| ITFMATCH-26JUL15LONMIL | ITF_M | 5.1 | 1 | **OPEN** |
| ITFMATCH-26JUL15MESBAR | ITF_M | 0.433 | 3 | **OPEN** |
| ITFMATCH-26JUL15PECJAN | ITF_M | 2.433 | 1 | **OPEN** |
| ITFMATCH-26JUL15BERKLI | ITF_M | 0.0 | 7 | **QUIET** |
| ITFMATCH-26JUL15PALVAN | ITF_M | 0.0 | 36 | **QUIET** |
| ITFWMATCH-26JUL15KONPED | ITF_W | 0.0 | 10 | **QUIET** |
| ITFWMATCH-26JUL15RAILEW | ITF_W | 0.0 | 8 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL14VUKARS | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15IVACRA | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15LAJKRU | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15NAGTOR | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15YIBYUN | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.033 | 1 | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15LERHUR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15NOCMEC | ITF_M | 0.167 | 4 | **WAKING** |
| ITFMATCH-26JUL15RODPOW | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15STHALM | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15WILFAL | ITF_M | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL15FULMOY | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15MATSHC | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL15PONSAN | ITF_W | 0.0 | 4 | **WAKING** |
| WTAMATCH-26JUL15KREMON | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 3
- reality_divergence: KXATPCHALLENGERMATCH-26JUL15NOGSUR-SUR {"kind": "position_basis", "ref": 54.0, "market_mid": 13.5, "divergence": 40.5}
- reality_divergence: KXITFMATCH-26JUL15FITLYN-FIT {"kind": "resting_bid", "ref": 23.0, "market_mid": 56.5, "divergence": -33.5}
- reality_divergence: KXITFMATCH-26JUL15PALVAN-VAN {"kind": "resting_bid", "ref": 11.0, "market_mid": 42.5, "divergence": -31.5}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
