# LIVE VALIDATION — rolling status

- cycle 132 @ **2026-07-15 02:52:12 PM ET** | build `55042eff` | session boot 07-15 14:35 ET | log `live_v3_20260715.jsonl` | 2287 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PERDIG-DIG aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PERDIG-DIG aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 6 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 14:38:27 | **bell_missing** | KXATPCHALLENGERMATCH-26JUL15YIBYUN | min_past_start 38.5 |
| 14:38:27 | **bell_missing** | KXITFMATCH-26JUL15PECJAN | min_past_start 13.5 |
| 14:38:27 | **bell_missing** | KXITFWMATCH-26JUL15RAILEW | min_past_start 13.5 |
| 14:38:27 | **bell_missing** | KXITFWMATCH-26JUL15CROGRU | min_past_start 13.5 |
| 14:41:14 | **bell_missing** | KXITFMATCH-26JUL15FITLYN | min_past_start 11.2 |
| 14:41:14 | **bell_missing** | KXITFWMATCH-26JUL15MATSHC | min_past_start 11.2 |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_bell_missing.md**

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:37 | ITFMATCH-26JUL15LONMIL-MIL | ITF_M | ? | 50 | 47 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:37 | ITFMATCH-26JUL15LERHUR-LER | ITF_M | ? | 19 | 15 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 14:51 | ITFMATCH-26JUL15PECJAN-PEC | ITF_M | ? | 16 | 18 | -2 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 39 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 9, 'NO_FLOW': 30} | repriceable now: true 1 / false 38 | **cumulative bid_grade lines: 11358 (repriceable true 1548 / false 9810)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL14VUKARS-A | 18 | 14m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15IVACRA-C | 59 | 15m | 1/66-66/11 | 64-66 | 7 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL15IVACRA-I | 32 | 15m | 1/36-36/13 | 34-36 | 4 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL15LAJKRU-K | 28 | 15m | 1/33-33/14 | 32-33 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15LAJKRU-L | 64 | 15m | 0 | 68-69 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15NAGTOR-N | 56 | 15m | 0 | 60-61 | — | **NO_FLOW** | 58 |  |
| ATPCHALLENGERMATCH-26JUL15NAGTOR-T | 36 | 15m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15YIBYUN-Y | 53 | 15m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15YIBYUN-Y | 42 | 15m | 0 | 42-44 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15BASTIR-TIR | 65 | 15m | 1/69-69/7 | 68-69 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ATPMATCH-26JUL15PRIMOL-PRI | 65 | 15m | 8/73-73/433 | 72-73 | 8 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15RUBPEL-PEL | 27 | 15m | 0 | 29-30 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15RUBPEL-RUB | 71 | 15m | 0 | 72-73 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BERKLI-BER | 55 | 15m | 0 | 72-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BERKLI-KLI | 17 | 15m | 0 | 22-27 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15FITLYN-FIT | 6 | 3m | 0 | 46-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15FITLYN-LYN | 29 | 15m | 0 | 37-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MESBAR-BAR | 66 | 15m | 5/78-84/668 | 79-82 | 12 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFMATCH-26JUL15MESBAR-MES | 11 | 15m | 1/20-20/4 | 19-20 | 9 | **FLOW_ABOVE** | 16 | flow above but bound 16c < flow -- chasing breaks goal |
| ITFMATCH-26JUL15NOCMEC-MEC | 41 | 15m | 0 | 57-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15NOCMEC-NOC | 23 | 15m | 4/42-43/223 | 38-42 | 19 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15PALVAN-VAN | 11 | 15m | 0 | 16-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15RODPOW-POW | 48 | 15m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15RODPOW-ROD | 16 | 15m | 0 | 34-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15STHALM-ALM | 43 | 14m | 0 | 59-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15STHALM-STH | 22 | 14m | 0 | 35-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WILFAL-FAL | 11 | 15m | 0 | 17-19 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WILFAL-WIL | 66 | 15m | 0 | 78-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CROGRU-CRO | 78 | 15m | 0 | 88-94 | — | **NO_FLOW** | 86 |  |
| ITFWMATCH-26JUL15FULMOY-FUL | 44 | 15m | 0 | 57-62 | — | **NO_FLOW** | 60 |  |
| ITFWMATCH-26JUL15FULMOY-MOY | 28 | 15m | 0 | 37-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15KONPED-KON | 5 | 15m | 0 | 7-13 | — | **NO_FLOW** | 9 |  |
| ITFWMATCH-26JUL15MATSHC-MAT | 17 | 15m | 1/35-35/3 | 28-35 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15MATSHC-SHC | 55 | 15m | 0 | 67-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15PONSAN-SAN | 82 | 15m | 0 | 94-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15RAILEW-LEW | 29 | 15m | 0 | 43-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15RAILEW-RAI | 44 | 15m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15KREMON-MON | 8 | 15m | 0 | 9-10 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15SHEQUE-QUE | 32 | 15m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL15PECJAN | 16 | 84 | **100** | 97 | +3 |

## FLOW-STATE — 27 tracked game(s) ({'WAKING': 21, 'QUIET': 3, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL15LONMIL | ITF_M | 8.067 | 1 | **OPEN** |
| ITFMATCH-26JUL15MESBAR | ITF_M | 0.2 | 1 | **OPEN** |
| ITFMATCH-26JUL15PECJAN | ITF_M | 0.6 | 1 | **OPEN** |
| ITFMATCH-26JUL15FITLYN | ITF_M | 0.0 | 6 | **QUIET** |
| ITFMATCH-26JUL15PALVAN | ITF_M | 0.0 | 37 | **QUIET** |
| ITFWMATCH-26JUL15KONPED | ITF_W | 0.0 | 6 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL14VUKARS | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15IVACRA | ATP_CHALL | 0.067 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15LAJKRU | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15NAGTOR | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15YIBYUN | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.033 | 1 | **WAKING** |
| ATPMATCH-26JUL15PRIMOL | ATP_MAIN | 0.3 | 1 | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15BERKLI | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15LERHUR | ITF_M | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL15NOCMEC | ITF_M | 0.133 | 4 | **WAKING** |
| ITFMATCH-26JUL15RODPOW | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15STHALM | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15WILFAL | ITF_M | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15CROGRU | ITF_W | 0.033 | 6 | **WAKING** |
| ITFWMATCH-26JUL15FULMOY | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15MATSHC | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL15PONSAN | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL15RAILEW | ITF_W | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL15KREMON | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 3
- reality_divergence: KXATPCHALLENGERMATCH-26JUL15NOGSUR-SUR {"kind": "position_basis", "ref": 54.0, "market_mid": 13.5, "divergence": 40.5, "emitted_et": "2026-07-15 02:52:06 PM ET"}
- reality_divergence: KXITFMATCH-26JUL15FITLYN-FIT {"kind": "resting_bid", "ref": 23.0, "market_mid": 56.5, "divergence": -33.5, "emitted_et": "2026-07-15 02:52:06 PM ET"}
- reality_divergence: KXITFMATCH-26JUL15PALVAN-VAN {"kind": "resting_bid", "ref": 11.0, "market_mid": 42.5, "divergence": -31.5, "emitted_et": "2026-07-15 02:52:06 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
