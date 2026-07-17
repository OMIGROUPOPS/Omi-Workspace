# LIVE VALIDATION — rolling status

- cycle 145 @ **2026-07-17 02:43:05 AM ET** | build `d6dcede5` | session boot 07-17 01:03 ET | log `live_v3_20260717.jsonl` | 10238 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 89 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:w1_preference UL16SHESTR-STR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16SHESTR-SHE aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL17FONDOT-FON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL17FONDOT-FON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 3 item(s)
- **reality_divergence**: KXITFWMATCH-26JUL17BROBRA-BRA {"kind": "resting_bid", "ref": 32.0, "market_mid": 77.0, "divergence": -45.0}
- **reality_divergence**: KXITFWMATCH-26JUL17BROBRA-BRO {"kind": "resting_bid", "ref": 18.0, "market_mid": 53.5, "divergence": -35.5}
- **half_arm_aging**: KXITFWMATCH-26JUL17BROBRA-BRA {"fill": 32, "age_min": 62, "mode": "NO_BID(sib rested earlier, none now)"}
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 4 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 01:42:22 | **flatten_leash** | KXITFWMATCH-26JUL17BROBRA-BRA | flatten DEFERRED: ev -0.8 above margin floor -3.0 |
| 01:53:35 | **flatten_leash** | KXITFWMATCH-26JUL17BROBRA-BRA | flatten DEFERRED: ev -0.8 above margin floor -3.0 |
| 02:06:26 | **flatten_leash** | KXITFWMATCH-26JUL17BROBRA-BRA | flatten DEFERRED: ev -0.8 above margin floor -3.0 |
| 02:28:00 | **w2_fill** | KXITFWMATCH-26JUL17KHRVAN-KHR | W2 FILL (buy after start): 11c x5 booking=reconcile_adoption gun=percat_fitted |

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:41 | ITFWMATCH-26JUL17BROBRA-BRA | ITF_W | ? | 32 | 28 | +4 (fill_est) | — | pre | single |  | PENDING |
| 02:28 | ITFWMATCH-26JUL17KHRVAN-KHR | ITF_W | ? | 11 | 7 | +4 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 72 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 50, 'FLOW_ABOVE': 22} | repriceable now: true 6 / false 66 | **cumulative bid_grade lines: 12091 (repriceable true 1584 / false 10507)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17GALCOP-G | 38 | 99m | 11/42-44/1453 | 43-44 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL17NIJDEN-D | 74 | 11m | 2/78-79/2 | 79-80 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ATPCHALLENGERMATCH-26JUL17NIJDEN-N | 18 | 12m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL17COLVAC-COL | 53 | 72m | 85/56-58/10965 | 56-57 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ATPMATCH-26JUL17COLVAC-VAC | 40 | 13m | 12/43-44/1126 | 43-44 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ATPMATCH-26JUL17VALTRA-TRA | 25 | 99m | 22/28-30/2820 | 28-29 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→28 |
| ATPMATCH-26JUL17VALTRA-VAL | 67 | 99m | 53/71-72/5830 | 71-72 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→71 |
| ITFMATCH-26JUL17BLAGHA-BLA | 54 | 99m | 0 | 67-71 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17BLAGHA-GHA | 16 | 99m | 0 | 28-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17JADDUR-DUR | 35 | 72m | 0 | 47-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17KIMDOI-DOI | 20 | 99m | 0 | 24-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17KIMDOI-KIM | 58 | 99m | 0 | 71-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17KOIFIT-FIT | 50 | 36m | 6/64-67/249 | 68-69 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL17KOIFIT-KOI | 23 | 42m | 5/35-35/417 | 30-32 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL17LANBOS-BOS | 41 | 99m | 2/58-58/82 | 57-58 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL17LANBOS-LAN | 26 | 99m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17MCKTSI-MCK | 70 | 99m | 0 | 83-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17MCKTSI-TSI | 11 | 99m | 2/17-18/26 | 15-16 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL17OMABER-BER | 20 | 72m | 0 | 24-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17OMABER-OMA | 58 | 72m | 0 | 71-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17PALPAP-PAL | 19 | 99m | 1/35-35/2 | 33-35 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL17PALPAP-PAP | 50 | 99m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17SAHMOS-MOS | 34 | 72m | 0 | 46-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17STAORL-ORL | 40 | 99m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17STAORL-STA | 30 | 99m | 0 | 45-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17THORUL-RUL | 24 | 99m | 0 | 37-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17THORUL-THO | 42 | 99m | 2/63-63/0 | 58-63 | 21 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL17TURPAP-PAP | 27 | 99m | 1/43-43/22 | 39-43 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL17TURPAP-TUR | 43 | 99m | 0 | 56-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17VELROB-VEL | 33 | 99m | 0 | 48-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17WIECUE-CUE | 58 | 99m | 0 | 71-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17WIECUE-WIE | 20 | 99m | 0 | 24-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17BAIDOD-BAI | 25 | 72m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17BAIDOD-DOD | 51 | 72m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17DANPAV-DAN | 19 | 42m | 0 | 24-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17DANPAV-PAV | 63 | 42m | 0 | 73-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17DUDKLU-DUD | 45 | 72m | 0 | 55-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17DUDKLU-KLU | 31 | 72m | 0 | 43-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17FITSED-FIT | 61 | 42m | 0 | 71-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17FITSED-SED | 14 | 42m | 0 | 26-28 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17HORROU-HOR | 23 | 99m | 0 | 35-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17HORROU-ROU | 51 | 99m | 10/61-65/680 | 61-64 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17JANSCH-JAN | 26 | 42m | 0 | 38-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17JANSCH-SCH | 49 | 42m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17KARRIC-RIC | 25 | 99m | 0 | 30-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17KUBSHI-KUB | 44 | 42m | 1/56-56/24 | 54-56 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17KUBSHI-SHI | 32 | 42m | 0 | 44-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17KUCSIS-KUC | 14 | 99m | 2/21-21/13 | 19-21 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17KUCSIS-SIS | 69 | 99m | 0 | 79-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17KUHSTR-KUH | 11 | 42m | 0 | 16-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17KUHSTR-STR | 72 | 42m | 0 | 81-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17KUZPAV-KUZ | 50 | 42m | 0 | 60-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17KUZPAV-PAV | 24 | 42m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17MALKAL-KAL | 69 | 99m | 1/83-83/1 | 81-83 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17MALKAL-MAL | 14 | 99m | 1/19-19/2 | 16-19 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17NATRAD-NAT | 5 | 42m | 1/12-12/7 | 8-12 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17NATRAD-RAD | 79 | 42m | 0 | 88-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17SCHDAD-DAD | 19 | 99m | 0 | 30-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17SCHDAD-SCH | 54 | 99m | 1/69-69/35 | 65-69 | 15 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17SERZEL-SER | 45 | 99m | 0 | 55-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17SERZEL-ZEL | 30 | 99m | 1/46-46/2 | 44-46 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17SMICIR-CIR | 27 | 99m | 0 | 39-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17SMICIR-SMI | 45 | 99m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17STOLEW-LEW | 22 | 99m | 0 | 33-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17STOLEW-STO | 53 | 99m | 0 | 62-67 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17TSYMAR-MAR | 45 | 99m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17TSYMAR-TSY | 27 | 99m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17UDVNIJ-NIJ | 24 | 99m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17UDVNIJ-UDV | 47 | 99m | 0 | 60-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17ZHAWAN-WAN | 54 | 99m | 0 | 66-67 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17ZHAWAN-ZHA | 19 | 99m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL17BASCAR-B | 60 | 12m | 1/65-65/1 | 63-65 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 41 tracked game(s) ({'WAKING': 38, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL17COLVAC | ATP_MAIN | 1.9 | 1 | **OPEN** |
| ATPMATCH-26JUL17VALTRA | ATP_MAIN | 0.5 | 1 | **OPEN** |
| ITFWMATCH-26JUL17KHRVAN | ITF_W | 1.233 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17GALCOP | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17NIJDEN | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL17BLAGHA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL17JADDUR | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL17KIMDOI | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL17KOIFIT | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL17LANBOS | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL17MCKTSI | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL17OMABER | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL17PALPAP | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL17SAHMOS | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL17STAORL | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL17THORUL | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL17TURPAP | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL17VELROB | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL17WIECUE | ITF_M | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL17BAIDOD | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL17BROBRA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL17DANPAV | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL17DUDKLU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL17FITSED | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL17HORROU | ITF_W | 0.167 | 3 | **WAKING** |
| ITFWMATCH-26JUL17JANSCH | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL17KARRIC | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL17KUBSHI | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL17KUCSIS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL17KUHSTR | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL17KUZPAV | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL17MALKAL | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL17NATRAD | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL17SCHDAD | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL17SERZEL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL17SMICIR | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL17STOLEW | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL17TSYMAR | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL17UDVNIJ | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL17ZHAWAN | ITF_W | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL17BASCAR | WTA_CHALL | 0.033 | 2 | **WAKING** |

## PATTERNS (sub-B) — 3
- reality_divergence: KXITFWMATCH-26JUL17BROBRA-BRA {"kind": "resting_bid", "ref": 32.0, "market_mid": 77.0, "divergence": -45.0}
- reality_divergence: KXITFWMATCH-26JUL17BROBRA-BRO {"kind": "resting_bid", "ref": 18.0, "market_mid": 53.5, "divergence": -35.5}
- half_arm_aging: KXITFWMATCH-26JUL17BROBRA-BRA {"fill": 32, "age_min": 62, "mode": "NO_BID(sib rested earlier, none now)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
