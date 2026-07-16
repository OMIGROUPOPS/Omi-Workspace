# LIVE VALIDATION — rolling status

- cycle 70 @ **2026-07-16 01:57:08 PM ET** | build `9e44b8f8` | session boot 07-16 12:56 ET | log `live_v3_20260716.jsonl` | 6624 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 44 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:w1_preference UL16TAUTON-TON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16TAUTON-TON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16TAUTON-TON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16TAUTON-TON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 10 violation(s)
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

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_w2_fill.md, FORENSIC_flatten_leash.md**

## FILLS — 5 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12:58 | ATPCHALLENGERMATCH-26JUL16DELDAL-D | ATP_CHALL | ? | 57 | 54 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 13:01 | ITFWMATCH-26JUL16CHAGUZ-CHA | ITF_W | ? | 33 | 29 | +4 (fill_est) | — | pre | single |  | PENDING |
| 13:27 | ATPCHALLENGERMATCH-26JUL16FUESEY-S | ATP_CHALL | ? | 80 | 83 | -3 (window_cell) | — | pre | single |  | MIXED |
| 13:36 | ITFWMATCH-26JUL16MATREA-REA | ITF_W | ? | 54 | 52 | +2 (fill_est) | — | pre | single |  | PENDING |
| 13:47 | WTACHALLENGERMATCH-26JUL16KOVRIE-R | WTA_CHALL | ? | 74 | 76 | -2 (window_cell) | -1.5 | pre | single |  | MIXED |

## RESTING BIDS — 32 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 23, 'NO_FLOW': 8, 'FLOW_AT_LEVEL': 1} | repriceable now: true 3 / false 29 | **cumulative bid_grade lines: 11960 (repriceable true 1580 / false 10380)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL16GRESAN-G | 56 | 59m | 9/60-61/173 | 60-61 | 4 | **FLOW_ABOVE** | 57 | REPRICEABLE→57 |
| ATPCHALLENGERMATCH-26JUL16GRESAN-S | 35 | 59m | 7/40-41/428 | 39-40 | 5 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL16PALALM-A | 67 | 59m | 1/72-72/1 | 71-72 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL16PALALM-P | 24 | 59m | 5/29-30/11 | 28-30 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL16MOLDAV-DAV | 52 | 59m | 63/57-58/6097 | 57-58 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL16MOLDAV-MOL | 39 | 56m | 16/42-43/4941 | 42-43 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFMATCH-26JUL16BECANT-BEC | 5 | 56m | 3/11-11/117 | 9-11 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16BERPAL-BER | 39 | 59m | 0 | 50-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16BERPAL-PAL | 22 | 59m | 0 | 47-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16BYNLON-BYN | 37 | 59m | 32/57-58/751 | 52-57 | 20 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16BYNLON-LON | 31 | 59m | 3/46-47/22 | 42-46 | 15 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FAHCOL-COL | 8 | 59m | 2/16-16/17 | 14-17 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FAHCOL-FAH | 68 | 59m | 2/85-86/16 | 82-86 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FISGAI-FIS | 13 | 59m | 2/33-33/25 | 32-36 | 20 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FISGAI-GAI | 21 | 59m | 1/68-68/1 | 64-69 | 47 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16LEGBON-LEG | 51 | 59m | 53/67-85/1618 | 77-83 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16NEFCOX-COX | 22 | 59m | 0 | 33-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16NEFCOX-NEF | 45 | 59m | 1/66-66/15 | 62-67 | 21 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16SERBAS-BAS | 67 | 59m | 4/84-85/72 | 83-84 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16SERBAS-SER | 10 | 59m | 4/19-19/32 | 15-19 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16WILALM-ALM | 17 | 59m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16WILALM-WIL | 44 | 59m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL16CHAGUZ-GUZ | 42 | 59m | 179/56-93/14831 | 90-80 | 14 | **FLOW_ABOVE** | 64 |  |
| ITFWMATCH-26JUL16COLMAR-COL | 16 | 59m | 5/28-28/26 | 26-29 | 12 | **FLOW_ABOVE** | 25 | flow above but bound 25c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL16COLMAR-MAR | 57 | 59m | 7/75-75/184 | 71-75 | 18 | **FLOW_ABOVE** | 73 | flow above but bound 73c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL16KOIKUR-KOI | 54 | 59m | 2/70-71/69 | 69-71 | 16 | **FLOW_ABOVE** | 68 | flow above but bound 68c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL16KOIKUR-KUR | 20 | 59m | 1/33-33/2 | 30-33 | 13 | **FLOW_ABOVE** | 29 | flow above but bound 29c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL16SAINIS-NIS | 28 | 59m | 0 | 40-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL16SAINIS-SAI | 46 | 59m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL16KOSBRO-B | 37 | 59m | 0 | 40-41 | — | **NO_FLOW** | 38 |  |
| WTACHALLENGERMATCH-26JUL16KOSBRO-K | 56 | 59m | 3/60-60/124 | 59-60 | 4 | **FLOW_ABOVE** | 57 | REPRICEABLE→57 |
| WTAMATCH-26JUL16TAUTON-TAU | 94 | 46m | 7/94-95/1165 | 94-95 | 0 | **FLOW_AT_LEVEL** | 94 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL16FUESEY | 80 | 7 | **87** | 97 | -10 |
| WTACHALLENGERMATCH-26JUL16KOVRIE | 74 | 24 | **98** | 97 | +1 |
| ITFWMATCH-26JUL16CHAGUZ | 33 | 80 | **113** | 97 | +16 |

## FLOW-STATE — 22 tracked game(s) ({'QUIET': 1, 'WAKING': 18, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL16GRESAN | ATP_CHALL | 0.5 | 1 | **OPEN** |
| ATPMATCH-26JUL16MOLDAV | ATP_MAIN | 1.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL16COLMAR | ITF_W | 0.333 | 3 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL16DELDAL | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL16FUESEY | ATP_CHALL | 2.567 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL16PALALM | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL16BECANT | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL16BERPAL | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL16BYNLON | ITF_M | 0.967 | 4 | **WAKING** |
| ITFMATCH-26JUL16FAHCOL | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL16FISGAI | ITF_M | 0.067 | 4 | **WAKING** |
| ITFMATCH-26JUL16LEGBON | ITF_M | 1.467 | 6 | **WAKING** |
| ITFMATCH-26JUL16NEFCOX | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL16SERBAS | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL16WILALM | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL16CHAGUZ | ITF_W | 6.233 | — | **WAKING** |
| ITFWMATCH-26JUL16KOIKUR | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL16MATREA | ITF_W | 4.767 | — | **WAKING** |
| ITFWMATCH-26JUL16SAINIS | ITF_W | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL16KOSBRO | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL16KOVRIE | WTA_CHALL | 1.167 | — | **WAKING** |
| WTAMATCH-26JUL16TAUTON | WTA_MAIN | 0.2 | 1 | **WAKING** |

## PATTERNS (sub-B) — 10
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL16DELDAL-DEL {"fill": 57, "age_min": 59, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL16CHAGUZ-CHA {"fill": 33, "age_min": 55, "mode": "SET_BELOW_FLOW(prints 14c above)"}
- reality_divergence: KXITFMATCH-26JUL16BERPAL-PAL {"kind": "resting_bid", "ref": 22.0, "market_mid": 48.5, "divergence": -26.5}
- reality_divergence: KXITFMATCH-26JUL16FISGAI-GAI {"kind": "resting_bid", "ref": 21.0, "market_mid": 66.0, "divergence": -45.0}
- reality_divergence: KXITFMATCH-26JUL16LEGBON-LEG {"kind": "resting_bid", "ref": 51.0, "market_mid": 76.5, "divergence": -25.5}
- reality_divergence: KXITFWMATCH-26JUL16CHAGUZ-GUZ {"kind": "resting_bid", "ref": 42.0, "market_mid": 77.0, "divergence": -35.0}
- reality_divergence: KXITFMATCH-26JUL16BERPAL-PAL {"kind": "resting_bid", "ref": 22.0, "market_mid": 48.0, "divergence": -26.0}
- reality_divergence: KXITFMATCH-26JUL16FISGAI-GAI {"kind": "resting_bid", "ref": 21.0, "market_mid": 66.5, "divergence": -45.5}
- reality_divergence: KXITFMATCH-26JUL16LEGBON-LEG {"kind": "resting_bid", "ref": 51.0, "market_mid": 77.5, "divergence": -26.5}
- reality_divergence: KXITFWMATCH-26JUL16CHAGUZ-GUZ {"kind": "resting_bid", "ref": 42.0, "market_mid": 79.5, "divergence": -37.5, "emitted_et": "2026-07-16 01:57:07 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
