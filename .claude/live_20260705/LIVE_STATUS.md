# LIVE VALIDATION — rolling status

- cycle 134 @ **2026-07-15 03:15:32 PM ET** | build `aa094a54` | session boot 07-15 14:35 ET | log `live_v3_20260715.jsonl` | 4333 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 15 violation(s)
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
| 15:04:20 | **flatten_leash** | KXITFMATCH-26JUL15PECJAN-PEC | flatten DEFERRED: ev -1.75 above margin floor -3.0 |
| 15:05:24 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL15YIBYUN-YUN | flatten DEFERRED: ev -2.56 above margin floor -3.0 |
| 15:09:16 | **flatten_leash** | KXATPMATCH-26JUL15TABMID-MID | flatten DEFERRED: ev -2.43 above margin floor -3.0 |
| 15:10:00 | **bell_missing** | KXITFMATCH-26JUL15NOCMEC | min_past_start 10.0 |
| 15:10:00 | **bell_missing** | KXITFMATCH-26JUL15WILFAL | min_past_start 10.0 |
| 15:10:00 | **bell_missing** | KXITFMATCH-26JUL15BERKLI | min_past_start 10.0 |
| 15:10:00 | **bell_missing** | KXITFMATCH-26JUL15RODPOW | min_past_start 10.0 |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_bell_missing.md, FORENSIC_flatten_leash.md**

## FILLS — 5 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:37 | ITFMATCH-26JUL15LONMIL-MIL | ITF_M | ? | 50 | 47 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:37 | ITFMATCH-26JUL15LERHUR-LER | ITF_M | ? | 19 | 15 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:51 | ITFMATCH-26JUL15PECJAN-PEC | ITF_M | ? | 16 | 18 | -2 (window_cell) | — | pre | single |  | EARNED |
| 14:53 | ATPCHALLENGERMATCH-26JUL15YIBYUN-Y | ATP_CHALL | ? | 42 | 39 | +3 (fill_est) | — | pre | single |  | PENDING |
| 15:09 | ITFMATCH-26JUL15MESBAR-MES | ITF_M | ? | 11 | 16 | -5 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 31 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 15, 'NO_FLOW': 16} | repriceable now: true 5 / false 26 | **cumulative bid_grade lines: 11366 (repriceable true 1548 / false 9818)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL14VUKARS-A | 18 | 38m | 0 | 20-22 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15IVACRA-C | 59 | 38m | 6/66-66/179 | 65-66 | 7 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL15IVACRA-I | 32 | 38m | 10/34-37/573 | 34-37 | 2 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL15LAJKRU-K | 28 | 38m | 1/33-33/14 | 32-33 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15LAJKRU-L | 64 | 38m | 2/69-69/13 | 68-69 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15NAGTOR-N | 56 | 38m | 0 | 60-61 | — | **NO_FLOW** | 58 |  |
| ATPCHALLENGERMATCH-26JUL15NAGTOR-T | 36 | 38m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15YIBYUN-Y | 53 | 38m | 0 | 57-58 | — | **NO_FLOW** | 55 |  |
| ATPMATCH-26JUL15BASTIR-TIR | 65 | 38m | 1/69-69/7 | 68-69 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ATPMATCH-26JUL15RUBPEL-PEL | 27 | 38m | 1/29-29/21 | 28-29 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ATPMATCH-26JUL15RUBPEL-RUB | 71 | 38m | 4/73-73/1332 | 72-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL15BERKLI-BER | 55 | 38m | 0 | 56-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BERKLI-KLI | 17 | 14m | 0 | 21-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15NOCMEC-MEC | 31 | 14m | 0 | 58-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15NOCMEC-NOC | 23 | 38m | 5/38-43/227 | 38-41 | 15 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15RODPOW-POW | 48 | 38m | 6/55-68/333 | 52-53 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15RODPOW-ROD | 16 | 38m | 9/37-50/99 | 47-48 | 21 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15STHALM-ALM | 43 | 38m | 0 | 59-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15STHALM-STH | 22 | 38m | 0 | 35-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WILFAL-FAL | 11 | 38m | 0 | 15-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WILFAL-WIL | 55 | 11m | 0 | 55-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15FULMOY-FUL | 44 | 38m | 3/62-63/123 | 59-63 | 18 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL15FULMOY-MOY | 28 | 38m | 0 | 37-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15KONPED-KON | 5 | 38m | 0 | 9-24 | — | **NO_FLOW** | 9 |  |
| ITFWMATCH-26JUL15MATSHC-MAT | 17 | 38m | 1/35-35/3 | 28-35 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15MATSHC-SHC | 55 | 38m | 1/70-70/6 | 67-70 | 15 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15PONSAN-SAN | 82 | 38m | 0 | 94-98 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15RAILEW-LEW | 29 | 38m | 0 | 42-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15RAILEW-RAI | 44 | 38m | 0 | 45-55 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15KREMON-MON | 8 | 38m | 1/10-10/9 | 9-10 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| WTAMATCH-26JUL15SHEQUE-QUE | 32 | 38m | 2/36-36/60 | 38-39 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL15MESBAR | 11 | 85 | **96** | 97 | -1 |
| ATPCHALLENGERMATCH-26JUL15YIBYUN | 42 | 58 | **100** | 97 | +3 |
| ITFMATCH-26JUL15PECJAN | 16 | 88 | **104** | 97 | +7 |

## FLOW-STATE — 23 tracked game(s) ({'WAKING': 14, 'OPEN': 5, 'QUIET': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15IVACRA | ATP_CHALL | 0.533 | 1 | **OPEN** |
| ITFMATCH-26JUL15LONMIL | ITF_M | 0.433 | 1 | **OPEN** |
| ITFMATCH-26JUL15MESBAR | ITF_M | 1.2 | 1 | **OPEN** |
| ITFMATCH-26JUL15PECJAN | ITF_M | 2.767 | 2 | **OPEN** |
| ITFMATCH-26JUL15RODPOW | ITF_M | 0.5 | 1 | **OPEN** |
| ITFMATCH-26JUL15BERKLI | ITF_M | 0.0 | 23 | **QUIET** |
| ITFMATCH-26JUL15WILFAL | ITF_M | 0.0 | 22 | **QUIET** |
| ITFWMATCH-26JUL15KONPED | ITF_W | 0.0 | 15 | **QUIET** |
| ITFWMATCH-26JUL15RAILEW | ITF_W | 0.0 | 8 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL14VUKARS | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15LAJKRU | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15NAGTOR | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15YIBYUN | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL15LERHUR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15NOCMEC | ITF_M | 0.167 | 3 | **WAKING** |
| ITFMATCH-26JUL15STHALM | ITF_M | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15FULMOY | ITF_W | 0.1 | 3 | **WAKING** |
| ITFWMATCH-26JUL15MATSHC | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL15PONSAN | ITF_W | 0.0 | 4 | **WAKING** |
| WTAMATCH-26JUL15KREMON | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.067 | 1 | **WAKING** |

## PATTERNS (sub-B) — 6
- half_arm_aging: KXITFMATCH-26JUL15LONMIL-MIL {"fill": 50, "age_min": 38, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-15 03:15:19 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL15LERHUR-LER {"fill": 19, "age_min": 38, "mode": "PAIRING(sib never rested)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL15NOGSUR-SUR {"kind": "position_basis", "ref": 54.0, "market_mid": 13.5, "divergence": 40.5}
- reality_divergence: KXITFMATCH-26JUL15FITLYN-FIT {"kind": "resting_bid", "ref": 23.0, "market_mid": 56.5, "divergence": -33.5}
- reality_divergence: KXITFMATCH-26JUL15PALVAN-VAN {"kind": "resting_bid", "ref": 11.0, "market_mid": 42.5, "divergence": -31.5}
- reality_divergence: KXITFMATCH-26JUL15NOCMEC-MEC {"kind": "resting_bid", "ref": 31.0, "market_mid": 61.5, "divergence": -30.5, "emitted_et": "2026-07-15 03:15:19 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
