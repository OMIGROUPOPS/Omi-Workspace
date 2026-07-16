# LIVE VALIDATION — rolling status

- cycle 76 @ **2026-07-16 02:58:16 PM ET** | build `155a1d6b` | session boot 07-16 12:56 ET | log `live_v3_20260716.jsonl` | 10195 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 105 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL16DRAMIL-MIL aim=29 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- placed:path_aim UL16BECANT-ANT aim=78 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- placed:path_aim UL16SAINIS-SAI aim=46 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- placed:path_aim UL16SAINIS-NIS aim=33 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 13 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 12:59:20 | **bell_missing** | KXITFMATCH-26JUL16BERPAL | min_past_start 28.8 |
| 12:59:20 | **bell_missing** | KXITFMATCH-26JUL16WILALM | min_past_start 28.8 |
| 13:01:47 | **w2_fill** | KXITFWMATCH-26JUL16CHAGUZ-CHA | W2 FILL (buy after start): 33c x5 booking=v4_fingerprint_readopt gun=tape_flow |
| 13:07:11 | **bell_missing** | KXATPCHALLENGERMATCH-26JUL15YIBYUN | min_past_start 1386.3 |
| 13:27:27 | **w2_fill** | KXATPCHALLENGERMATCH-26JUL16FUESEY-SEY | W2 FILL (buy after start): 80c x5 booking=reconcile_adoption gun=percat_fitted |
| 13:36:18 | **w2_fill** | KXITFWMATCH-26JUL16MATREA-REA | W2 FILL (buy after start): 54c x5 booking=v4_fingerprint_readopt gun=percat_fitted |
| 13:40:54 | **bell_missing** | KXWTACHALLENGERMATCH-26JUL16KOVRIE | min_past_start 10.1 |
| 13:47:21 | **w2_fill** | KXWTACHALLENGERMATCH-26JUL16KOVRIE-RIE | W2 FILL (buy after start): 74c x5 booking=reconcile_adoption gun=fallback_bell |
| 13:47:43 | **flatten_leash** | KXWTACHALLENGERMATCH-26JUL16KOVRIE-RIE | flatten DEFERRED: ev -2.44 above margin floor -3.0 |
| 13:49:24 | **flatten_leash** | KXITFWMATCH-26JUL16MATREA-REA | flatten DEFERRED: ev -2.44 above margin floor -3.0 |
| 13:58:21 | **flatten_leash** | KXWTACHALLENGERMATCH-26JUL16KOVRIE-RIE | flatten DEFERRED: ev -2.44 above margin floor -3.0 |
| 14:23:53 | **w2_fill** | KXITFWMATCH-26JUL16KOIKUR-KOI | W2 FILL (buy after start): 54c x5 booking=v4_fingerprint_readopt gun=percat_fitted |
| 14:26:11 | **flatten_leash** | KXITFWMATCH-26JUL16KOIKUR-KOI | flatten DEFERRED: ev -1.2 above margin floor -3.0 |

## FILLS — 6 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12:58 | ATPCHALLENGERMATCH-26JUL16DELDAL-D | ATP_CHALL | ? | 57 | 54 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 13:01 | ITFWMATCH-26JUL16CHAGUZ-CHA | ITF_W | ? | 33 | 4 | +29 (window_cell) | — | pre | single |  | MIXED |
| 13:27 | ATPCHALLENGERMATCH-26JUL16FUESEY-S | ATP_CHALL | ? | 80 | 83 | -3 (window_cell) | — | pre | single |  | MIXED |
| 13:36 | ITFWMATCH-26JUL16MATREA-REA | ITF_W | ? | 54 | 52 | +2 (fill_est) | — | pre | single |  | PENDING |
| 13:47 | WTACHALLENGERMATCH-26JUL16KOVRIE-R | WTA_CHALL | ? | 74 | 76 | -2 (window_cell) | -1.5 | pre | single |  | MIXED |
| 14:23 | ITFWMATCH-26JUL16KOIKUR-KOI | ITF_W | ? | 54 | 68 | -14 (window_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 27 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 25, 'NO_FLOW': 2} | repriceable now: true 2 / false 25 | **cumulative bid_grade lines: 11969 (repriceable true 1580 / false 10389)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL16GRESAN-G | 56 | 120m | 26/60-61/4725 | 60-62 | 4 | **FLOW_ABOVE** | 57 | REPRICEABLE→57 |
| ATPCHALLENGERMATCH-26JUL16GRESAN-S | 35 | 120m | 8/40-41/430 | 38-40 | 5 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL16PALALM-A | 67 | 120m | 5/72-73/26 | 71-74 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL16PALALM-P | 24 | 120m | 8/29-30/57 | 27-30 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL16MOLDAV-DAV | 52 | 120m | 216/57-59/28721 | 57-58 | 5 | **FLOW_ABOVE** | 58 |  |
| ATPMATCH-26JUL16MOLDAV-MOL | 39 | 117m | 95/42-44/23972 | 42-43 | 3 | **FLOW_ABOVE** | 41 | REPRICEABLE→41 |
| ITFMATCH-26JUL16BECANT-ANT | 78 | 28m | 0 | 91-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16BECANT-BEC | 5 | 117m | 6/11-11/146 | 9-11 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16BERPAL-BER | 39 | 120m | 2/55-55/22 | 52-55 | 16 | **FLOW_ABOVE** | 52 | flow above but bound 52c < flow -- chasing breaks goal |
| ITFMATCH-26JUL16BERPAL-PAL | 22 | 120m | 1/49-49/39 | 47-50 | 27 | **FLOW_ABOVE** | 45 | flow above but bound 45c < flow -- chasing breaks goal |
| ITFMATCH-26JUL16BYNLON-BYN | 37 | 120m | 40/57-60/861 | 55-59 | 20 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ITFMATCH-26JUL16BYNLON-LON | 31 | 120m | 3/46-47/22 | 41-43 | 15 | **FLOW_ABOVE** | 42 | flow above but bound 42c < flow -- chasing breaks goal |
| ITFMATCH-26JUL16FAHCOL-COL | 8 | 120m | 2/16-16/17 | 14-17 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FAHCOL-FAH | 68 | 120m | 4/85-86/78 | 82-86 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FISGAI-FIS | 13 | 120m | 4/33-36/32 | 32-36 | 20 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FISGAI-GAI | 21 | 120m | 7/68-68/229 | 66-68 | 47 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16LEGBON-LEG | 51 | 120m | 72/67-86/1826 | 80-85 | 16 | **FLOW_ABOVE** | 82 |  |
| ITFMATCH-26JUL16NEFCOX-COX | 16 | 52m | 2/37-38/14 | 34-38 | 21 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16NEFCOX-NEF | 45 | 120m | 3/66-66/21 | 62-66 | 21 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16SERBAS-BAS | 67 | 120m | 12/84-85/226 | 83-84 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16SERBAS-SER | 10 | 120m | 10/15-19/502 | 15-19 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16WILALM-ALM | 17 | 120m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16WILALM-WIL | 44 | 120m | 1/68-68/10 | 66-68 | 24 | **FLOW_ABOVE** | 65 | flow above but bound 65c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL16COLMAR-COL | 16 | 120m | 31/28-32/1340 | 25-28 | 12 | **FLOW_ABOVE** | 25 | flow above but bound 25c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL16COLMAR-MAR | 57 | 120m | 20/74-77/367 | 70-75 | 17 | **FLOW_ABOVE** | 73 | flow above but bound 73c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL16SEMBRA-BRA | 75 | 57m | 2/88-88/26 | 87-88 | 13 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL16SEMBRA-SEM | 6 | 57m | 3/16-16/48 | 12-16 | 10 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL16KOIKUR | 54 | 6 | **60** | 97 | -37 |
| ATPCHALLENGERMATCH-26JUL16FUESEY | 80 | 15 | **95** | 97 | -2 |
| WTACHALLENGERMATCH-26JUL16KOVRIE | 74 | 40 | **114** | 97 | +17 |
| ITFWMATCH-26JUL16CHAGUZ | 33 | 98 | **131** | 97 | +34 |

## FLOW-STATE — 20 tracked game(s) ({'QUIET': 1, 'WAKING': 15, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL16GRESAN | ATP_CHALL | 0.367 | 2 | **OPEN** |
| ATPMATCH-26JUL16MOLDAV | ATP_MAIN | 4.933 | 1 | **OPEN** |
| ITFMATCH-26JUL16SERBAS | ITF_M | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL16COLMAR | ITF_W | 0.833 | 3 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL16DELDAL | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL16FUESEY | ATP_CHALL | 6.6 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL16PALALM | ATP_CHALL | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL16BECANT | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL16BERPAL | ITF_M | 0.1 | 3 | **WAKING** |
| ITFMATCH-26JUL16BYNLON | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL16FAHCOL | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL16FISGAI | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL16LEGBON | ITF_M | 0.167 | 5 | **WAKING** |
| ITFMATCH-26JUL16NEFCOX | ITF_M | 0.1 | 4 | **WAKING** |
| ITFMATCH-26JUL16WILALM | ITF_M | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL16CHAGUZ | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL16KOIKUR | ITF_W | 4.233 | — | **WAKING** |
| ITFWMATCH-26JUL16MATREA | ITF_W | 17.4 | — | **WAKING** |
| ITFWMATCH-26JUL16SEMBRA | ITF_W | 0.1 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL16KOVRIE | WTA_CHALL | 19.667 | — | **WAKING** |

## PATTERNS (sub-B) — 22
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL16DELDAL-DEL {"fill": 57, "age_min": 120, "mode": "PAIRING(sib never rested)"}
- pre_conception_buy: KXITFWMATCH-26JUL16JACREE-JAC {"price": 21, "conception_ts": 1784224817.910219, "detail": "buy 21c predates the conception stamp by 62min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL16CHAGUZ-CHA {"price": 33, "conception_ts": 1784224822.7887716, "detail": "buy 33c predates the conception stamp by 62min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL16CHAGUZ-CHA {"fill": 33, "age_min": 116, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXITFMATCH-26JUL16BERPAL-PAL {"kind": "resting_bid", "ref": 22.0, "market_mid": 48.5, "divergence": -26.5}
- reality_divergence: KXITFMATCH-26JUL16FISGAI-GAI {"kind": "resting_bid", "ref": 21.0, "market_mid": 66.0, "divergence": -45.0}
- reality_divergence: KXITFMATCH-26JUL16LEGBON-LEG {"kind": "resting_bid", "ref": 51.0, "market_mid": 76.5, "divergence": -25.5}
- reality_divergence: KXITFWMATCH-26JUL16CHAGUZ-GUZ {"kind": "resting_bid", "ref": 42.0, "market_mid": 77.0, "divergence": -35.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL16FUESEY-SEY {"fill": 80, "age_min": 91, "mode": "PAIRING(sib never rested)"}
- reality_divergence: KXITFMATCH-26JUL16BERPAL-PAL {"kind": "resting_bid", "ref": 22.0, "market_mid": 48.0, "divergence": -26.0}
- reality_divergence: KXITFMATCH-26JUL16FISGAI-GAI {"kind": "resting_bid", "ref": 21.0, "market_mid": 66.5, "divergence": -45.5}
- reality_divergence: KXITFMATCH-26JUL16LEGBON-LEG {"kind": "resting_bid", "ref": 51.0, "market_mid": 77.5, "divergence": -26.5}
- half_arm_aging: KXITFWMATCH-26JUL16MATREA-REA {"fill": 54, "age_min": 82, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL16KOVRIE-RIE {"fill": 74, "age_min": 71, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXITFWMATCH-26JUL16CHAGUZ-GUZ {"kind": "resting_bid", "ref": 42.0, "market_mid": 79.5, "divergence": -37.5}
- reality_divergence: KXITFMATCH-26JUL16BERPAL-PAL {"kind": "resting_bid", "ref": 22.0, "market_mid": 48.0, "divergence": -26.0}
- reality_divergence: KXITFMATCH-26JUL16FISGAI-GAI {"kind": "resting_bid", "ref": 21.0, "market_mid": 66.0, "divergence": -45.0}
- reality_divergence: KXITFMATCH-26JUL16LEGBON-LEG {"kind": "resting_bid", "ref": 51.0, "market_mid": 81.0, "divergence": -30.0}
- half_arm_aging: KXITFWMATCH-26JUL16KOIKUR-KOI {"fill": 54, "age_min": 34, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-16 02:58:16 PM ET"}
- reality_divergence: KXITFMATCH-26JUL16BERPAL-PAL {"kind": "resting_bid", "ref": 22.0, "market_mid": 48.0, "divergence": -26.0}
- reality_divergence: KXITFMATCH-26JUL16FISGAI-GAI {"kind": "resting_bid", "ref": 21.0, "market_mid": 67.0, "divergence": -46.0}
- reality_divergence: KXITFMATCH-26JUL16LEGBON-LEG {"kind": "resting_bid", "ref": 51.0, "market_mid": 82.5, "divergence": -31.5}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
