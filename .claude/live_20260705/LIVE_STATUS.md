# LIVE VALIDATION — rolling status

- cycle 69 @ **2026-07-16 01:46:56 PM ET** | build `24a3a372` | session boot 07-16 12:56 ET | log `live_v3_20260716.jsonl` | 5655 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 34 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:w1_preference UL16TAUTON-TON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16TAUTON-TON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16TAUTON-TON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16TAUTON-TON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 7 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 12:59:20 | **bell_missing** | KXITFMATCH-26JUL16BERPAL | min_past_start 28.8 |
| 12:59:20 | **bell_missing** | KXITFMATCH-26JUL16WILALM | min_past_start 28.8 |
| 13:01:47 | **w2_fill** | KXITFWMATCH-26JUL16CHAGUZ-CHA | W2 FILL (buy after start): 33c x5 booking=v4_fingerprint_readopt gun=tape_flow |
| 13:07:11 | **bell_missing** | KXATPCHALLENGERMATCH-26JUL15YIBYUN | min_past_start 1386.3 |
| 13:27:27 | **w2_fill** | KXATPCHALLENGERMATCH-26JUL16FUESEY-SEY | W2 FILL (buy after start): 80c x5 booking=reconcile_adoption gun=percat_fitted |
| 13:36:18 | **w2_fill** | KXITFWMATCH-26JUL16MATREA-REA | W2 FILL (buy after start): 54c x5 booking=v4_fingerprint_readopt gun=percat_fitted |
| 13:40:54 | **bell_missing** | KXWTACHALLENGERMATCH-26JUL16KOVRIE | min_past_start 10.1 |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_bell_missing.md**

## FILLS — 4 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12:58 | ATPCHALLENGERMATCH-26JUL16DELDAL-D | ATP_CHALL | ? | 57 | 54 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 13:01 | ITFWMATCH-26JUL16CHAGUZ-CHA | ITF_W | ? | 33 | 29 | +4 (fill_est) | — | pre | single |  | PENDING |
| 13:27 | ATPCHALLENGERMATCH-26JUL16FUESEY-S | ATP_CHALL | ? | 80 | 83 | -3 (window_cell) | — | pre | single |  | MIXED |
| 13:36 | ITFWMATCH-26JUL16MATREA-REA | ITF_W | ? | 54 | 52 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 37 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 27, 'NO_FLOW': 10} | repriceable now: true 4 / false 33 | **cumulative bid_grade lines: 11959 (repriceable true 1580 / false 10379)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL16GLISEK-G | 57 | 49m | 6/64-64/115 | 63-64 | 7 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL16GLISEK-S | 33 | 49m | 1/38-38/0 | 36-38 | 5 | **FLOW_ABOVE** | 35 | flow above but bound 35c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL16GRESAN-G | 56 | 49m | 7/60-61/55 | 59-61 | 4 | **FLOW_ABOVE** | 57 | REPRICEABLE→57 |
| ATPCHALLENGERMATCH-26JUL16GRESAN-S | 35 | 49m | 4/40-41/188 | 39-40 | 5 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL16PALALM-A | 67 | 49m | 0 | 71-72 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL16PALALM-P | 24 | 49m | 5/29-30/11 | 28-30 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL16MOLDAV-DAV | 52 | 49m | 51/57-58/5551 | 57-58 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL16MOLDAV-MOL | 39 | 46m | 14/42-43/4909 | 42-43 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ITFMATCH-26JUL16BECANT-BEC | 5 | 46m | 3/11-11/117 | 9-11 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16BERPAL-BER | 39 | 49m | 0 | 50-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16BERPAL-PAL | 22 | 49m | 0 | 47-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16BYNLON-BYN | 37 | 49m | 19/57-57/410 | 51-57 | 20 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16BYNLON-LON | 31 | 49m | 1/47-47/10 | 42-47 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FAHCOL-COL | 8 | 49m | 2/16-16/17 | 14-17 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FAHCOL-FAH | 68 | 49m | 2/85-86/16 | 82-86 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FISGAI-FIS | 13 | 49m | 2/33-33/25 | 32-36 | 20 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16FISGAI-GAI | 21 | 49m | 1/68-68/1 | 64-69 | 47 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16LEGBON-BON | 17 | 49m | 70/23-35/4406 | 27-29 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16LEGBON-LEG | 51 | 49m | 31/67-79/644 | 71-73 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16NEFCOX-COX | 22 | 49m | 0 | 33-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16NEFCOX-NEF | 45 | 49m | 1/66-66/15 | 62-67 | 21 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16SERBAS-BAS | 67 | 49m | 4/84-85/72 | 83-84 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16SERBAS-SER | 10 | 49m | 2/19-19/23 | 15-19 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL16WILALM-ALM | 17 | 49m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL16WILALM-WIL | 44 | 49m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL16CHAGUZ-GUZ | 42 | 49m | 131/56-90/9782 | 85-87 | 14 | **FLOW_ABOVE** | 64 |  |
| ITFWMATCH-26JUL16COLMAR-COL | 16 | 49m | 5/28-28/26 | 24-29 | 12 | **FLOW_ABOVE** | 25 | flow above but bound 25c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL16COLMAR-MAR | 57 | 49m | 2/75-75/7 | 71-75 | 18 | **FLOW_ABOVE** | 73 | flow above but bound 73c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL16KOIKUR-KOI | 54 | 49m | 0 | 69-70 | — | **NO_FLOW** | 68 |  |
| ITFWMATCH-26JUL16KOIKUR-KUR | 20 | 49m | 1/33-33/2 | 30-33 | 13 | **FLOW_ABOVE** | 29 | flow above but bound 29c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL16SAINIS-NIS | 28 | 49m | 0 | 40-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL16SAINIS-SAI | 46 | 49m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL16KOSBRO-B | 37 | 49m | 0 | 40-41 | — | **NO_FLOW** | 38 |  |
| WTACHALLENGERMATCH-26JUL16KOSBRO-K | 56 | 49m | 2/60-60/92 | 59-60 | 4 | **FLOW_ABOVE** | 57 | REPRICEABLE→57 |
| WTACHALLENGERMATCH-26JUL16KOVRIE-K | 19 | 49m | 15/21-26/2909 | 24-25 | 2 | **FLOW_ABOVE** | 19 | flow above but bound 19c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL16KOVRIE-R | 74 | 49m | 10/78-79/419 | 75-76 | 4 | **FLOW_ABOVE** | 76 | REPRICEABLE→76 |
| WTAMATCH-26JUL16TAUTON-TAU | 94 | 36m | 3/95-95/24 | 94-95 | 1 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL16FUESEY | 80 | 13 | **93** | 97 | -4 |
| ITFWMATCH-26JUL16CHAGUZ | 33 | 87 | **120** | 97 | +23 |

## FLOW-STATE — 23 tracked game(s) ({'QUIET': 1, 'OPEN': 7, 'WAKING': 15}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL16FUESEY | ATP_CHALL | 1.933 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL16GRESAN | ATP_CHALL | 0.367 | 1 | **OPEN** |
| ATPMATCH-26JUL16MOLDAV | ATP_MAIN | 1.033 | 1 | **OPEN** |
| ITFMATCH-26JUL16LEGBON | ITF_M | 3.133 | 2 | **OPEN** |
| ITFWMATCH-26JUL16CHAGUZ | ITF_W | 5.2 | 2 | **OPEN** |
| ITFWMATCH-26JUL16MATREA | ITF_W | 2.2 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL16KOVRIE | WTA_CHALL | 0.7 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL16DELDAL | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL16GLISEK | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL16PALALM | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL16BECANT | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL16BERPAL | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL16BYNLON | ITF_M | 0.5 | 5 | **WAKING** |
| ITFMATCH-26JUL16FAHCOL | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL16FISGAI | ITF_M | 0.067 | 4 | **WAKING** |
| ITFMATCH-26JUL16NEFCOX | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL16SERBAS | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL16WILALM | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL16COLMAR | ITF_W | 0.233 | 4 | **WAKING** |
| ITFWMATCH-26JUL16KOIKUR | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL16SAINIS | ITF_W | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL16KOSBRO | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL16TAUTON | WTA_MAIN | 0.067 | 1 | **WAKING** |

## PATTERNS (sub-B) — 9
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL16DELDAL-DEL {"fill": 57, "age_min": 49, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL16CHAGUZ-CHA {"fill": 33, "age_min": 45, "mode": "SET_BELOW_FLOW(prints 14c above)"}
- reality_divergence: KXITFMATCH-26JUL16BERPAL-PAL {"kind": "resting_bid", "ref": 22.0, "market_mid": 48.5, "divergence": -26.5}
- reality_divergence: KXITFMATCH-26JUL16FISGAI-GAI {"kind": "resting_bid", "ref": 21.0, "market_mid": 66.0, "divergence": -45.0}
- reality_divergence: KXITFMATCH-26JUL16LEGBON-LEG {"kind": "resting_bid", "ref": 51.0, "market_mid": 76.5, "divergence": -25.5}
- reality_divergence: KXITFWMATCH-26JUL16CHAGUZ-GUZ {"kind": "resting_bid", "ref": 42.0, "market_mid": 77.0, "divergence": -35.0}
- reality_divergence: KXITFMATCH-26JUL16BERPAL-PAL {"kind": "resting_bid", "ref": 22.0, "market_mid": 48.0, "divergence": -26.0}
- reality_divergence: KXITFMATCH-26JUL16FISGAI-GAI {"kind": "resting_bid", "ref": 21.0, "market_mid": 66.5, "divergence": -45.5}
- reality_divergence: KXITFMATCH-26JUL16LEGBON-LEG {"kind": "resting_bid", "ref": 51.0, "market_mid": 77.5, "divergence": -26.5}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
