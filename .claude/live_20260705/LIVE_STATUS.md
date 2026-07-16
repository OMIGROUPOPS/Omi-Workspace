# LIVE VALIDATION — rolling status

- cycle 68 @ **2026-07-16 01:36:45 PM ET** | build `1fe7620e` | session boot 07-16 12:56 ET | log `live_v3_20260716.jsonl` | 4605 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:w1_preference UL16TAUTON-TON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16TAUTON-TON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16TAUTON-TON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16TAUTON-TON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 6 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 12:59:20 | **bell_missing** | KXITFMATCH-26JUL16BERPAL | min_past_start 28.8 |
| 12:59:20 | **bell_missing** | KXITFMATCH-26JUL16WILALM | min_past_start 28.8 |
| 13:01:47 | **w2_fill** | KXITFWMATCH-26JUL16CHAGUZ-CHA | W2 FILL (buy after start): 33c x5 booking=v4_fingerprint_readopt gun=tape_flow |
| 13:07:11 | **bell_missing** | KXATPCHALLENGERMATCH-26JUL15YIBYUN | min_past_start 1386.3 |
| 13:27:27 | **w2_fill** | KXATPCHALLENGERMATCH-26JUL16FUESEY-SEY | W2 FILL (buy after start): 80c x5 booking=reconcile_adoption gun=percat_fitted |
| 13:36:18 | **w2_fill** | KXITFWMATCH-26JUL16MATREA-REA | W2 FILL (buy after start): 54c x5 booking=v4_fingerprint_readopt gun=percat_fitted |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_w2_fill.md**

## FILLS — 4 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12:58 | ATPCHALLENGERMATCH-26JUL16DELDAL-D | ATP_CHALL | ? | 57 | 54 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 13:01 | ITFWMATCH-26JUL16CHAGUZ-CHA | ITF_W | ? | 33 | 29 | +4 (fill_est) | — | pre | single |  | PENDING |
| 13:27 | ATPCHALLENGERMATCH-26JUL16FUESEY-S | ATP_CHALL | ? | 80 | 83 | -3 (window_cell) | — | pre | single |  | MIXED |
| 13:36 | ITFWMATCH-26JUL16MATREA-REA | ITF_W | ? | 54 | 52 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 37 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 25, 'NO_FLOW': 12} | repriceable now: true 4 / false 33 | **cumulative bid_grade lines: 11959 (repriceable true 1580 / false 10379)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL16GLISEK-G | 57 | 39m | 5/64-64/108 | 63-64 | 7 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL16GLISEK-S | 33 | 39m | 0 | 36-38 | — | **NO_FLOW** | 35 |  |
| ATPCHALLENGERMATCH-26JUL16GRESAN-G | 56 | 39m | 3/60-61/25 | 60-61 | 4 | **FLOW_ABOVE** | 57 | REPRICEABLE→57 |
| ATPCHALLENGERMATCH-26JUL16GRESAN-S | 35 | 39m | 1/40-40/8 | 39-40 | 5 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL16PALALM-A | 67 | 39m | 0 | 71-72 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL16PALALM-P | 24 | 39m | 5/29-30/11 | 28-30 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL16MOLDAV-DAV | 52 | 39m | 48/57-58/5248 | 57-58 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL16MOLDAV-MOL | 39 | 36m | 14/42-43/4909 | 42-43 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFMATCH-26JUL16BECANT-BEC | 5 | 36m | 1/11-11/34 | 9-11 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16BERPAL-BER | 39 | 39m | 0 | 50-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16BERPAL-PAL | 22 | 39m | 0 | 47-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16BYNLON-BYN | 37 | 39m | 8/57-57/282 | 54-57 | 20 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16BYNLON-LON | 31 | 39m | 1/47-47/10 | 43-47 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FAHCOL-COL | 8 | 39m | 2/16-16/17 | 14-17 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FAHCOL-FAH | 68 | 39m | 2/85-86/16 | 82-86 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FISGAI-FIS | 13 | 39m | 2/33-33/25 | 32-36 | 20 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FISGAI-GAI | 21 | 39m | 1/68-68/1 | 64-69 | 47 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16LEGBON-BON | 17 | 39m | 37/23-26/2561 | 24-25 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16LEGBON-LEG | 51 | 39m | 15/76-79/134 | 74-75 | 25 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16NEFCOX-COX | 22 | 39m | 0 | 33-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16NEFCOX-NEF | 45 | 39m | 1/66-66/15 | 62-67 | 21 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16SERBAS-BAS | 67 | 39m | 3/84-85/71 | 83-84 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16SERBAS-SER | 10 | 39m | 1/19-19/19 | 15-19 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16WILALM-ALM | 17 | 39m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16WILALM-WIL | 44 | 39m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL16CHAGUZ-GUZ | 42 | 39m | 109/56-90/9465 | 84-84 | 14 | **FLOW_ABOVE** | 64 |  |
| ITFWMATCH-26JUL16COLMAR-COL | 16 | 39m | 3/28-28/10 | 27-28 | 12 | **FLOW_ABOVE** | 25 | flow above but bound 25c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL16COLMAR-MAR | 57 | 39m | 0 | 71-75 | — | **NO_FLOW** | 73 |  |
| ITFWMATCH-26JUL16KOIKUR-KOI | 54 | 39m | 0 | 69-70 | — | **NO_FLOW** | 68 |  |
| ITFWMATCH-26JUL16KOIKUR-KUR | 20 | 39m | 1/33-33/2 | 29-33 | 13 | **FLOW_ABOVE** | 29 | flow above but bound 29c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL16SAINIS-NIS | 28 | 39m | 0 | 40-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL16SAINIS-SAI | 46 | 39m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL16KOSBRO-B | 37 | 39m | 0 | 40-41 | — | **NO_FLOW** | 38 |  |
| WTACHALLENGERMATCH-26JUL16KOSBRO-K | 56 | 39m | 2/60-60/92 | 59-60 | 4 | **FLOW_ABOVE** | 57 | REPRICEABLE→57 |
| WTACHALLENGERMATCH-26JUL16KOVRIE-K | 19 | 39m | 4/21-22/2099 | 21-22 | 2 | **FLOW_ABOVE** | 19 | flow above but bound 19c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL16KOVRIE-R | 74 | 39m | 5/78-79/399 | 78-79 | 4 | **FLOW_ABOVE** | 76 | REPRICEABLE→76 |
| WTAMATCH-26JUL16TAUTON-TAU | 94 | 26m | 1/95-95/18 | 94-95 | 1 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL16FUESEY | 80 | 6 | **86** | 97 | -11 |
| ITFWMATCH-26JUL16CHAGUZ | 33 | 84 | **117** | 97 | +20 |

## FLOW-STATE — 23 tracked game(s) ({'QUIET': 1, 'WAKING': 18, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL16MOLDAV | ATP_MAIN | 1.5 | 1 | **OPEN** |
| ITFMATCH-26JUL16LEGBON | ITF_M | 1.733 | 1 | **OPEN** |
| ITFWMATCH-26JUL16CHAGUZ | ITF_W | 5.367 | 1 | **OPEN** |
| ITFWMATCH-26JUL16MATREA | ITF_W | 0.933 | 2 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL16DELDAL | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL16FUESEY | ATP_CHALL | 1.9 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL16GLISEK | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL16GRESAN | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL16PALALM | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL16BECANT | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL16BERPAL | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL16BYNLON | ITF_M | 0.167 | 3 | **WAKING** |
| ITFMATCH-26JUL16FAHCOL | ITF_M | 0.1 | 3 | **WAKING** |
| ITFMATCH-26JUL16FISGAI | ITF_M | 0.067 | 4 | **WAKING** |
| ITFMATCH-26JUL16NEFCOX | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL16SERBAS | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL16WILALM | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL16COLMAR | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL16KOIKUR | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL16SAINIS | ITF_W | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL16KOSBRO | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL16KOVRIE | WTA_CHALL | 0.2 | 1 | **WAKING** |
| WTAMATCH-26JUL16TAUTON | WTA_MAIN | 0.033 | 1 | **WAKING** |

## PATTERNS (sub-B) — 9
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL16DELDAL-DEL {"fill": 57, "age_min": 39, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-16 01:36:45 PM ET"}
- half_arm_aging: KXITFWMATCH-26JUL16CHAGUZ-CHA {"fill": 33, "age_min": 35, "mode": "SET_BELOW_FLOW(prints 14c above)", "emitted_et": "2026-07-16 01:36:45 PM ET"}
- reality_divergence: KXITFMATCH-26JUL16BERPAL-PAL {"kind": "resting_bid", "ref": 22.0, "market_mid": 48.5, "divergence": -26.5}
- reality_divergence: KXITFMATCH-26JUL16FISGAI-GAI {"kind": "resting_bid", "ref": 21.0, "market_mid": 66.0, "divergence": -45.0}
- reality_divergence: KXITFMATCH-26JUL16LEGBON-LEG {"kind": "resting_bid", "ref": 51.0, "market_mid": 76.5, "divergence": -25.5}
- reality_divergence: KXITFWMATCH-26JUL16CHAGUZ-GUZ {"kind": "resting_bid", "ref": 42.0, "market_mid": 77.0, "divergence": -35.0}
- reality_divergence: KXITFMATCH-26JUL16BERPAL-PAL {"kind": "resting_bid", "ref": 22.0, "market_mid": 48.0, "divergence": -26.0, "emitted_et": "2026-07-16 01:36:45 PM ET"}
- reality_divergence: KXITFMATCH-26JUL16FISGAI-GAI {"kind": "resting_bid", "ref": 21.0, "market_mid": 66.5, "divergence": -45.5, "emitted_et": "2026-07-16 01:36:45 PM ET"}
- reality_divergence: KXITFMATCH-26JUL16LEGBON-LEG {"kind": "resting_bid", "ref": 51.0, "market_mid": 77.5, "divergence": -26.5, "emitted_et": "2026-07-16 01:36:45 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
