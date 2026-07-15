# LIVE VALIDATION — rolling status

- cycle 58 @ **2026-07-15 01:00:10 AM ET** | build `7831e157` | session boot 07-15 00:19 ET | log `live_v3_20260715.jsonl` | 31558 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL15BERAGI-AGI aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15BERAGI-AGI aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15OVCCOR-COR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15MIRMUR-MIR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 7 item(s)
- **half_arm_aging**: KXITFMATCH-26JUL14ALHVUX-VUX {"fill": 77, "age_min": 34, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-15 01:00:10 AM ET"}
- **half_arm_aging**: KXITFMATCH-26JUL14KOAYAZ-YAZ {"fill": 59, "age_min": 33, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-15 01:00:10 AM ET"}
- **reality_divergence**: KXITFMATCH-26JUL14ALHVUX-ALH {"kind": "resting_bid", "ref": 8.0, "market_mid": 50.5, "divergence": -42.5}
- **reality_divergence**: KXITFMATCH-26JUL14ALKLIM-LIM {"kind": "resting_bid", "ref": 14.0, "market_mid": 43.0, "divergence": -29.0}
- **reality_divergence**: KXITFMATCH-26JUL14ALHVUX-VUX {"kind": "position_basis", "ref": 77.0, "market_mid": 24.5, "divergence": 52.5}
- **reality_divergence**: KXITFMATCH-26JUL15DOLDOU-DOL {"kind": "resting_bid", "ref": 10.0, "market_mid": 46.5, "divergence": -36.5}
- **reality_divergence**: KXITFMATCH-26JUL15OVCCOR-OVC {"kind": "resting_bid", "ref": 35.0, "market_mid": 71.5, "divergence": -36.5}
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 00:36:58 | **flatten_leash** | KXITFMATCH-26JUL14ALHVUX-VUX | flatten DEFERRED: ev -2.33 above margin floor -3.0 |

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:25 | ITFMATCH-26JUL14ALHVUX-VUX | ITF_M | underdog | 77 | 87 | -10 (place_cell) | — | pre | single |  | PENDING |
| 00:27 | ITFMATCH-26JUL14KOAYAZ-YAZ | ITF_M | leader | 59 | 72 | -13 (place_cell) | — | pre | single |  | PENDING |
| 00:46 | ATPCHALLENGERMATCH-26JUL14DELXIL-D | ATP_CHALL | ? | 85 | 82 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 149 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 119, 'FLOW_ABOVE': 30} | repriceable now: true 4 / false 145 | **cumulative bid_grade lines: 10183 (repriceable true 1473 / false 8710)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL14RINTAB-TAB | 28 | 38m | 10/35-36/768 | 34-35 | 7 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15BASTIR-BAS | 27 | 38m | 0 | 30-31 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15BUBHAL-BUB | 65 | 38m | 3/70-70/370 | 70-71 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15BUBHAL-HAL | 28 | 12m | 3/33-33/714 | 31-32 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15CERKEC-CER | 47 | 23m | 3/53-54/745 | 51-53 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15CERKEC-KEC | 44 | 38m | 1/49-49/17 | 46-49 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15COLSON-COL | 61 | 29m | 73/66-67/22441 | 66-66 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15RUBPEL-RUB | 64 | 38m | 2/76-76/22 | 75-76 | 12 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15TABMID-MID | 23 | 38m | 0 | 23-27 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15TABMID-TAB | 70 | 38m | 2/76-76/15 | 74-76 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL14SIKMAT-MAT | 64 | 36m | 8/77-77/59 | 76-77 | 13 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL14SIKMAT-SIK | 19 | 35m | 2/25-26/1 | 23-26 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15AUNALV-ALV | 19 | 38m | 0 | 32-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15AUNALV-AUN | 48 | 38m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BAXCOU-BAX | 78 | 36m | 0 | 91-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BENCOR-BEN | 56 | 38m | 1/76-76/1 | 73-76 | 20 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15BENCOR-COR | 19 | 38m | 2/26-26/73 | 25-26 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15BLAMAR-BLA | 71 | 36m | 0 | 84-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BONBER-BER | 37 | 37m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BONBER-BON | 30 | 37m | 0 | 43-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BROVUJ-BRO | 17 | 29m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BROVUJ-VUJ | 49 | 29m | 0 | 65-71 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CARBAR-BAR | 72 | 34m | 0 | 85-90 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CARBAR-CAR | 8 | 36m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CARJAM-CAR | 59 | 28m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CARJAM-JAM | 13 | 28m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CASCHE-CAS | 42 | 37m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CASCHE-CHE | 23 | 37m | 0 | 36-41 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CLEALU-ALU | 50 | 28m | 0 | 66-71 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CLEALU-CLE | 16 | 28m | 0 | 29-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15COCMIS-MIS | 33 | 29m | 0 | 46-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15COLLOP-COL | 37 | 29m | 0 | 52-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15COLLOP-LOP | 29 | 29m | 0 | 42-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DHOPLE-DHO | 12 | 28m | 0 | 17-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DHOPLE-PLE | 66 | 29m | 0 | 79-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DINCOM-COM | 27 | 29m | 0 | 40-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DINCOM-DIN | 38 | 30m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DOIVAN-DOI | 26 | 29m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DOIVAN-VAN | 40 | 29m | 0 | 56-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DOLDOU-DOL | 10 | 29m | 0 | 11-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DOMBER-BER | 31 | 36m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DUTKLA-DUT | 45 | 28m | 0 | 61-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DUTKLA-KLA | 20 | 28m | 0 | 34-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15GLOHAL-GLO | 11 | 37m | 0 | 17-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15GLOHAL-HAL | 66 | 37m | 0 | 79-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HERPED-HER | 19 | 38m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HERPED-PED | 50 | 38m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HOSDUH-HOS | 32 | 37m | 0 | 45-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15JADAUB-AUB | 18 | 38m | 0 | 24-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15JADAUB-JAD | 57 | 38m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15LOPTAL-LOP | 47 | 38m | 0 | 61-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15LOPTAL-TAL | 24 | 38m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MAKMAB-MAB | 36 | 28m | 0 | 52-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MAKMAB-MAK | 31 | 28m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MANKAR-KAR | 27 | 30m | 0 | 40-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MANKAR-MAN | 38 | 30m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MARSIL-MAR | 52 | 28m | 0 | 68-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MARSIL-SIL | 13 | 28m | 0 | 26-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MCHSCH-MCH | 45 | 28m | 0 | 61-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MCHSCH-SCH | 20 | 28m | 0 | 33-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MONLEA-LEA | 43 | 29m | 0 | 59-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MONLEA-MON | 23 | 29m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15OVCCOR-OVC | 35 | 18m | 0 | 52-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PALTAZ-PAL | 72 | 28m | 0 | 85-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PEICHA-CHA | 38 | 38m | 1/57-57/1 | 55-57 | 19 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15PEICHA-PEI | 29 | 38m | 0 | 42-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PERBEA-BEA | 35 | 37m | 0 | 50-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PERBEA-PER | 31 | 37m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PERGAR-GAR | 5 | 38m | 0 | 8-11 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PERGAR-PER | 76 | 38m | 0 | 89-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PLATOR-PLA | 12 | 29m | 0 | 18-23 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PLATOR-TOR | 63 | 29m | 0 | 76-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15SAHLAL-LAL | 15 | 38m | 0 | 28-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15SAHLAL-SAH | 53 | 38m | 1/71-71/4 | 67-71 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15SHISTR-SHI | 72 | 30m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15SHISTR-STR | 5 | 30m | 0 | 10-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15STEMAK-MAK | 39 | 38m | 4/58-58/123 | 53-58 | 19 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15STEMAK-STE | 28 | 38m | 1/46-46/4 | 41-46 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15TAIGUA-GUA | 7 | 29m | 0 | 13-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15TAIGUA-TAI | 68 | 29m | 0 | 81-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15TRIBAG-BAG | 16 | 28m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15TRIBAG-TRI | 49 | 25m | 0 | 64-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WERJOV-JOV | 80 | 29m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WIEWIT-WIE | 72 | 38m | 0 | 84-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WIEWIT-WIT | 10 | 38m | 0 | 12-14 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15ZAKLUE-LUE | 19 | 28m | 0 | 32-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15ZAKLUE-ZAK | 46 | 28m | 1/64-64/350 | 62-65 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15ADKINO-ADK | 20 | 28m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ADKINO-INO | 54 | 28m | 0 | 67-71 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ANSSAV-ANS | 5 | 28m | 0 | 11-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ANSSAV-SAV | 75 | 9m | 0 | 87-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ARYMAM-ARY | 15 | 38m | 1/22-22/1 | 21-22 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15ARYMAM-MAM | 65 | 38m | 0 | 77-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15BALVOR-BAL | 38 | 28m | 0 | 51-54 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15BALVOR-VOR | 34 | 28m | 0 | 45-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CAKVAR-CAK | 6 | 29m | 0 | 12-14 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CAKVAR-VAR | 73 | 29m | 0 | 85-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CASPAS-CAS | 6 | 29m | 0 | 12-14 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CASPAS-PAS | 74 | 29m | 0 | 86-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CHADAD-CHA | 22 | 38m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CHADAD-DAD | 50 | 38m | 0 | 67-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CHILEW-CHI | 20 | 37m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CHILEW-LEW | 52 | 37m | 0 | 65-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CROCHA-CHA | 57 | 28m | 0 | 66-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CROCHA-CRO | 18 | 28m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15DANGHI-DAN | 18 | 29m | 0 | 28-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15DANGHI-GHI | 55 | 29m | 0 | 68-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ERCBIE-BIE | 5 | 35m | 0 | 11-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ERCBIE-ERC | 75 | 35m | 0 | 87-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15JANISM-ISM | 45 | 38m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15JANISM-JAN | 27 | 38m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15KRUDUE-DUE | 40 | 30m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15KRUDUE-KRU | 33 | 30m | 0 | 44-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15KUZBEL-BEL | 57 | 37m | 1/74-74/1 | 70-74 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15KUZBEL-KUZ | 16 | 37m | 1/28-28/0 | 28-29 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15LENBER-BER | 26 | 35m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LENBER-LEN | 46 | 35m | 0 | 59-62 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LEYKHR-LEY | 81 | 37m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LLIULR-LLI | 27 | 28m | 0 | 38-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LLIULR-ULR | 46 | 28m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LOVROC-LOV | 40 | 36m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LOVROC-ROC | 32 | 36m | 0 | 43-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15MILDYU-DYU | 7 | 37m | 2/13-13/146 | 11-13 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15MILDYU-MIL | 75 | 37m | 0 | 87-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15PAVCHA-PAV | 76 | 38m | 0 | 91-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SCHHOS-HOS | 79 | 28m | 0 | 91-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SERKRE-KRE | 28 | 28m | 0 | 38-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SERKRE-SER | 44 | 28m | 0 | 58-62 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SMEROJ-ROJ | 59 | 38m | 0 | 75-77 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SMEROJ-SME | 15 | 38m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SMIVAN-SMI | 81 | 36m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15STEMAS-MAS | 30 | 38m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15STEMAS-STE | 42 | 38m | 0 | 56-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TREHEU-HEU | 16 | 35m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TREHEU-TRE | 62 | 35m | 0 | 75-77 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15VISGIA-VIS | 78 | 36m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15VOGNUU-NUU | 18 | 36m | 0 | 24-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15VOGNUU-VOG | 58 | 36m | 0 | 72-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WAGCIR-CIR | 70 | 35m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WAGCIR-WAG | 9 | 35m | 0 | 15-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15YODAHL-AHL | 35 | 28m | 2/46-47/11 | 45-47 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15YODAHL-YOD | 41 | 28m | 1/54-54/1 | 53-54 | 13 | **FLOW_ABOVE** | 99 |  |
| WTACHALLENGERMATCH-26JUL15RADCHI-C | 32 | 29m | 4/36-36/672 | 35-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| WTACHALLENGERMATCH-26JUL15RADCHI-R | 63 | 29m | 2/66-66/15 | 65-66 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| WTACHALLENGERMATCH-26JUL15YANLAN-L | 15 | 29m | 8/19-20/2148 | 19-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| WTACHALLENGERMATCH-26JUL15YANLAN-Y | 78 | 9m | 1/82-82/59 | 81-82 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| WTAMATCH-26JUL15IBRBAD-BAD | 77 | 32m | 2/86-86/33 | 82-86 | 9 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL15OLIPRI-OLI | 50 | 38m | 1/56-56/20 | 54-56 | 6 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL15SHEQUE-SHE | 61 | 38m | 1/66-66/4 | 65-66 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL14KOAYAZ | 59 | 41 | **100** | 97 | +3 |

## FLOW-STATE — 88 tracked game(s) ({'WAKING': 84, 'OPEN': 2, 'QUIET': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL14SIKMAT | ITF_M | 0.333 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL15YANLAN | WTA_CHALL | 0.3 | 1 | **OPEN** |
| ITFMATCH-26JUL15DOLDOU | ITF_M | 0.0 | 71 | **QUIET** |
| ITFMATCH-26JUL15OVCCOR | ITF_M | 0.0 | 40 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL14DELXIL | ATP_CHALL | 0.1 | 2 | **WAKING** |
| ATPMATCH-26JUL14RINTAB | ATP_MAIN | 0.333 | 1 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL15BUBHAL | ATP_MAIN | 0.333 | 1 | **WAKING** |
| ATPMATCH-26JUL15CERKEC | ATP_MAIN | 0.2 | 2 | **WAKING** |
| ATPMATCH-26JUL15COLSON | ATP_MAIN | 2.433 | — | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ATPMATCH-26JUL15TABMID | ATP_MAIN | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL14ALHVUX | ITF_M | 22.567 | — | **WAKING** |
| ITFMATCH-26JUL14KOAYAZ | ITF_M | 26.267 | — | **WAKING** |
| ITFMATCH-26JUL15AUNALV | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15BAXCOU | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15BENCOR | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL15BLAMAR | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15BONBER | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15BROVUJ | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15CARBAR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15CARJAM | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15CASCHE | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15CLEALU | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL15COCMIS | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15COLLOP | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15DHOPLE | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL15DINCOM | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15DOIVAN | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15DOMBER | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15DUTKLA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15GLOHAL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15HERPED | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15HOSDUH | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15JADAUB | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15LOPTAL | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15MAKMAB | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL15MANKAR | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15MARSIL | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15MCHSCH | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15MONLEA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15PALTAZ | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL15PEICHA | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL15PERBEA | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15PERGAR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15PLATOR | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15SAHLAL | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL15SHISTR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15STEMAK | ITF_M | 0.133 | 5 | **WAKING** |
| ITFMATCH-26JUL15TAIGUA | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15TRIBAG | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15WERJOV | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15WIEWIT | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15ZAKLUE | ITF_M | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL15ADKINO | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL15ANSSAV | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15ARYMAM | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL15BALVOR | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15CAKVAR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15CASPAS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15CHADAD | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15CHILEW | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15CROCHA | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15DANGHI | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15ERCBIE | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15JANISM | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL15KRUDUE | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15KUZBEL | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL15LENBER | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15LEYKHR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15LLIULR | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15LOVROC | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15MILDYU | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL15PAVCHA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15SCHHOS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15SERKRE | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15SMEROJ | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15SMIVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15STEMAS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15TREHEU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15VISGIA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15VOGNUU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15WAGCIR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15YODAHL | ITF_W | 0.1 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL15RADCHI | WTA_CHALL | 0.2 | 1 | **WAKING** |
| WTAMATCH-26JUL15IBRBAD | WTA_MAIN | 0.067 | 4 | **WAKING** |
| WTAMATCH-26JUL15OLIPRI | WTA_MAIN | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.033 | 1 | **WAKING** |

## PATTERNS (sub-B) — 7
- half_arm_aging: KXITFMATCH-26JUL14ALHVUX-VUX {"fill": 77, "age_min": 34, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-15 01:00:10 AM ET"}
- half_arm_aging: KXITFMATCH-26JUL14KOAYAZ-YAZ {"fill": 59, "age_min": 33, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-15 01:00:10 AM ET"}
- reality_divergence: KXITFMATCH-26JUL14ALHVUX-ALH {"kind": "resting_bid", "ref": 8.0, "market_mid": 50.5, "divergence": -42.5}
- reality_divergence: KXITFMATCH-26JUL14ALKLIM-LIM {"kind": "resting_bid", "ref": 14.0, "market_mid": 43.0, "divergence": -29.0}
- reality_divergence: KXITFMATCH-26JUL14ALHVUX-VUX {"kind": "position_basis", "ref": 77.0, "market_mid": 24.5, "divergence": 52.5}
- reality_divergence: KXITFMATCH-26JUL15DOLDOU-DOL {"kind": "resting_bid", "ref": 10.0, "market_mid": 46.5, "divergence": -36.5}
- reality_divergence: KXITFMATCH-26JUL15OVCCOR-OVC {"kind": "resting_bid", "ref": 35.0, "market_mid": 71.5, "divergence": -36.5}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
