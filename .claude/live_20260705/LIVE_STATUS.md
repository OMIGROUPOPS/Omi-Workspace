# LIVE VALIDATION — rolling status

- cycle 56 @ **2026-07-15 12:39:45 AM ET** | build `468536ef` | session boot 07-15 00:19 ET | log `live_v3_20260715.jsonl` | 13542 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL15POZMIL-MIL aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PAVCHA-CHA aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PAVCHA-CHA aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PAVCHA-CHA aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 2 item(s)
- **reality_divergence**: KXITFMATCH-26JUL14ALHVUX-ALH {"kind": "resting_bid", "ref": 8.0, "market_mid": 50.5, "divergence": -42.5}
- **reality_divergence**: KXITFMATCH-26JUL14ALKLIM-LIM {"kind": "resting_bid", "ref": 14.0, "market_mid": 43.0, "divergence": -29.0}
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 00:36:58 | **flatten_leash** | KXITFMATCH-26JUL14ALHVUX-VUX | flatten DEFERRED: ev -2.33 above margin floor -3.0 |

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:25 | ITFMATCH-26JUL14ALHVUX-VUX | ITF_M | underdog | 77 | 87 | -10 (place_cell) | — | pre | single |  | PENDING |
| 00:27 | ITFMATCH-26JUL14KOAYAZ-YAZ | ITF_M | leader | 59 | 72 | -13 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 154 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 133, 'FLOW_ABOVE': 20, 'FLOW_AT_LEVEL': 1} | repriceable now: true 1 / false 153 | **cumulative bid_grade lines: 10168 (repriceable true 1470 / false 8698)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL14RINTAB-TAB | 28 | 18m | 1/36-36/26 | 35-36 | 8 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15BASTIR-BAS | 27 | 18m | 0 | 30-31 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15BUBHAL-BUB | 65 | 18m | 1/70-70/5 | 69-70 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15CERKEC-CER | 47 | 2m | 0 | 50-53 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15CERKEC-KEC | 44 | 18m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15COLSON-COL | 61 | 8m | 10/66-66/386 | 65-66 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15RUBPEL-RUB | 64 | 18m | 0 | 75-76 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15TABMID-MID | 23 | 18m | 0 | 24-27 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15TABMID-TAB | 70 | 18m | 0 | 74-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14ALHVUX-ALH | 8 | 12m | 1/71-71/10 | 71-72 | 63 | **FLOW_ABOVE** | 20 | flow above but bound 20c < flow -- chasing breaks goal |
| ITFMATCH-26JUL14ALKLIM-ALK | 16 | 11m | 2/34-48/13 | 34-55 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL14ALKLIM-LIM | 14 | 18m | 10/14-53/178 | 21-46 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL14IBRBOB-BOB | 63 | 16m | 1/81-81/12 | 76-81 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL14IBRBOB-IBR | 15 | 16m | 1/21-21/1 | 20-21 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL14SIKMAT-MAT | 64 | 15m | 2/77-77/17 | 76-77 | 13 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL14SIKMAT-SIK | 19 | 15m | 2/25-26/1 | 22-26 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15AUNALV-ALV | 19 | 18m | 0 | 32-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15AUNALV-AUN | 48 | 18m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BAXCOU-BAX | 78 | 16m | 0 | 91-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BENCOR-BEN | 56 | 18m | 0 | 72-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BENCOR-COR | 19 | 18m | 1/26-26/0 | 24-26 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15BLAMAR-BLA | 71 | 16m | 0 | 84-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BONBER-BER | 37 | 16m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BONBER-BON | 30 | 16m | 0 | 43-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BROVUJ-BRO | 17 | 9m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BROVUJ-VUJ | 49 | 9m | 0 | 65-71 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CARBAR-BAR | 72 | 14m | 0 | 85-90 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CARBAR-CAR | 8 | 16m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CARJAM-CAR | 59 | 8m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CARJAM-JAM | 13 | 8m | 0 | 19-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CASCHE-CAS | 42 | 17m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CASCHE-CHE | 23 | 17m | 0 | 36-41 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CLEALU-ALU | 50 | 8m | 0 | 66-71 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CLEALU-CLE | 16 | 8m | 0 | 29-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15COCMIS-MIS | 33 | 8m | 0 | 46-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15COLLOP-COL | 37 | 8m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15COLLOP-LOP | 29 | 8m | 0 | 42-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DHOPLE-DHO | 12 | 8m | 0 | 18-20 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DHOPLE-PLE | 66 | 8m | 0 | 79-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DINCOM-COM | 27 | 9m | 0 | 40-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DINCOM-DIN | 38 | 9m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DOIVAN-DOI | 26 | 9m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DOIVAN-VAN | 40 | 9m | 0 | 56-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DOLDOU-DOL | 10 | 8m | 0 | 11-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DOMBER-BER | 31 | 16m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DUTKLA-DUT | 45 | 8m | 0 | 61-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DUTKLA-KLA | 20 | 8m | 0 | 34-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15GLOHAL-GLO | 11 | 17m | 0 | 17-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15GLOHAL-HAL | 66 | 17m | 0 | 79-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HERPED-HER | 19 | 18m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HERPED-PED | 50 | 18m | 0 | 64-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HOSDUH-HOS | 32 | 17m | 0 | 45-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15JADAUB-AUB | 18 | 18m | 0 | 24-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15JADAUB-JAD | 57 | 18m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15LOPTAL-LOP | 47 | 18m | 0 | 61-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15LOPTAL-TAL | 24 | 18m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MAKMAB-MAB | 36 | 8m | 0 | 52-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MAKMAB-MAK | 31 | 8m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MANKAR-KAR | 27 | 9m | 0 | 40-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MANKAR-MAN | 38 | 9m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MARSIL-MAR | 52 | 8m | 0 | 68-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MARSIL-SIL | 13 | 8m | 0 | 26-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MCHSCH-MCH | 45 | 8m | 0 | 61-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MCHSCH-SCH | 20 | 8m | 0 | 33-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MONLEA-LEA | 43 | 8m | 0 | 59-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15MONLEA-MON | 23 | 8m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PALTAZ-PAL | 72 | 8m | 0 | 85-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PEICHA-CHA | 38 | 18m | 0 | 55-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PEICHA-PEI | 29 | 18m | 0 | 42-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PERBEA-BEA | 35 | 17m | 0 | 50-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PERBEA-PER | 31 | 17m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PERGAR-GAR | 5 | 17m | 0 | 8-11 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PERGAR-PER | 76 | 18m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PLATOR-PLA | 12 | 8m | 0 | 18-23 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PLATOR-TOR | 63 | 8m | 0 | 76-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PRAGHA-GHA | 75 | 18m | 0 | 88-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PRAGHA-PRA | 5 | 18m | 12/12-13/950 | 11-12 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15SAHLAL-LAL | 15 | 18m | 0 | 28-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15SAHLAL-SAH | 53 | 18m | 1/71-71/4 | 67-71 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15SHISTR-SHI | 72 | 9m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15SHISTR-STR | 5 | 9m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15STEMAK-MAK | 39 | 18m | 3/58-58/117 | 53-58 | 19 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15STEMAK-STE | 28 | 18m | 0 | 41-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15TAIGUA-GUA | 7 | 8m | 0 | 13-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15TAIGUA-TAI | 68 | 8m | 0 | 81-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15TRIBAG-BAG | 16 | 8m | 0 | 29-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15TRIBAG-TRI | 49 | 5m | 0 | 65-69 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WERJOV-JOV | 80 | 9m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WIEWIT-WIE | 72 | 18m | 0 | 84-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WIEWIT-WIT | 10 | 18m | 0 | 12-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15ZAKLUE-LUE | 19 | 8m | 0 | 32-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15ZAKLUE-ZAK | 46 | 8m | 0 | 62-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ADKINO-ADK | 20 | 8m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ADKINO-INO | 54 | 8m | 0 | 67-71 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ANSSAV-ANS | 5 | 8m | 0 | 11-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ARYMAM-ARY | 15 | 18m | 1/22-22/1 | 21-22 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15ARYMAM-MAM | 65 | 18m | 0 | 77-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15BALVOR-BAL | 38 | 8m | 0 | 51-54 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15BALVOR-VOR | 34 | 8m | 0 | 45-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CAKVAR-CAK | 6 | 8m | 0 | 12-14 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CAKVAR-VAR | 73 | 8m | 0 | 85-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CASPAS-CAS | 6 | 8m | 0 | 12-14 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CASPAS-PAS | 74 | 8m | 0 | 86-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CHADAD-CHA | 22 | 18m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CHADAD-DAD | 50 | 18m | 0 | 67-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CHILEW-CHI | 20 | 17m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CHILEW-LEW | 52 | 17m | 0 | 65-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CROCHA-CHA | 57 | 8m | 0 | 67-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CROCHA-CRO | 18 | 8m | 0 | 29-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15DANGHI-DAN | 18 | 9m | 0 | 29-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15DANGHI-GHI | 55 | 9m | 0 | 68-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ERCBIE-BIE | 5 | 15m | 0 | 11-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ERCBIE-ERC | 75 | 15m | 0 | 87-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15JANISM-ISM | 45 | 18m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15JANISM-JAN | 27 | 18m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15KRUDUE-DUE | 40 | 9m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15KRUDUE-KRU | 33 | 9m | 0 | 44-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15KUZBEL-BEL | 57 | 17m | 0 | 70-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15KUZBEL-KUZ | 16 | 16m | 1/28-28/0 | 27-28 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15LENBER-BER | 26 | 15m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LENBER-LEN | 46 | 15m | 0 | 59-62 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LEYKHR-LEY | 81 | 17m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LLIULR-LLI | 27 | 8m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LLIULR-ULR | 46 | 8m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LOVROC-LOV | 40 | 16m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LOVROC-ROC | 32 | 16m | 0 | 43-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15MILDYU-DYU | 7 | 17m | 1/13-13/1 | 12-13 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15MILDYU-MIL | 75 | 17m | 0 | 87-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15PAVCHA-PAV | 76 | 18m | 0 | 91-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SCHHOS-HOS | 79 | 8m | 0 | 91-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SERKRE-KRE | 28 | 8m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SERKRE-SER | 44 | 8m | 0 | 57-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SMEROJ-ROJ | 59 | 18m | 0 | 75-77 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SMEROJ-SME | 15 | 18m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SMIVAN-SMI | 81 | 16m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SOZKEN-KEN | 38 | 18m | 3/53-53/41 | 50-53 | 15 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15SOZKEN-SOZ | 34 | 18m | 0 | 47-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15STEMAS-MAS | 30 | 18m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15STEMAS-STE | 42 | 18m | 0 | 56-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TREHEU-HEU | 16 | 15m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TREHEU-TRE | 62 | 15m | 0 | 75-77 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15VISGIA-VIS | 78 | 16m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15VOGNUU-NUU | 18 | 15m | 0 | 24-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15VOGNUU-VOG | 58 | 16m | 0 | 72-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WAGCIR-CIR | 70 | 15m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WAGCIR-WAG | 9 | 15m | 0 | 15-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15YODAHL-AHL | 35 | 8m | 2/46-47/11 | 46-47 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15YODAHL-YOD | 41 | 8m | 0 | 53-54 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL15RADCHI-C | 32 | 8m | 1/36-36/2 | 35-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| WTACHALLENGERMATCH-26JUL15RADCHI-R | 63 | 8m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL15YANLAN-L | 15 | 8m | 0 | 18-19 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15IBRBAD-BAD | 77 | 11m | 0 | 85-86 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15OLIPRI-OLI | 50 | 18m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15SHEQUE-SHE | 61 | 18m | 1/66-66/4 | 65-66 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL14ALHVUX | 77 | 72 | **149** | 97 | +52 |

## FLOW-STATE — 90 tracked game(s) ({'WAKING': 85, 'OPEN': 4, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL15COLSON | ATP_MAIN | 1.033 | 1 | **OPEN** |
| ITFMATCH-26JUL14ALHVUX | ITF_M | 0.7 | 1 | **OPEN** |
| ITFMATCH-26JUL14SIKMAT | ITF_M | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL15PRAGHA | ITF_M | 0.433 | 1 | **OPEN** |
| ITFMATCH-26JUL15DOLDOU | ITF_M | 0.0 | 71 | **QUIET** |
| ATPMATCH-26JUL14RINTAB | ATP_MAIN | 0.1 | 1 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL15BUBHAL | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ATPMATCH-26JUL15CERKEC | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL15TABMID | ATP_MAIN | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL14ALKLIM | ITF_M | 0.5 | 21 | **WAKING** |
| ITFMATCH-26JUL14IBRBOB | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL14KOAYAZ | ITF_M | 4.933 | — | **WAKING** |
| ITFMATCH-26JUL15AUNALV | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15BAXCOU | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15BENCOR | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL15BLAMAR | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15BONBER | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15BROVUJ | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15CARBAR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15CARJAM | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15CASCHE | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15CLEALU | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL15COCMIS | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15COLLOP | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15DHOPLE | ITF_M | 0.0 | 2 | **WAKING** |
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
| ITFMATCH-26JUL15PEICHA | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15PERBEA | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15PERGAR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15PLATOR | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15SAHLAL | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL15SHISTR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15STEMAK | ITF_M | 0.1 | 5 | **WAKING** |
| ITFMATCH-26JUL15TAIGUA | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15TRIBAG | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15WERJOV | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15WIEWIT | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15ZAKLUE | ITF_M | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15ADKINO | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL15ANSSAV | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15ARYMAM | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL15BALVOR | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15CAKVAR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15CASPAS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15CHADAD | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15CHILEW | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15CROCHA | ITF_W | 0.133 | 3 | **WAKING** |
| ITFWMATCH-26JUL15DANGHI | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15ERCBIE | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15JANISM | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL15KRUDUE | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15KUZBEL | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL15LENBER | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15LEYKHR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15LLIULR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15LOVROC | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15MILDYU | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL15PAVCHA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15SCHHOS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15SERKRE | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15SMEROJ | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15SMIVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15SOZKEN | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL15STEMAS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15TREHEU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15VISGIA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15VOGNUU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15WAGCIR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15YODAHL | ITF_W | 0.1 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL15RADCHI | WTA_CHALL | 0.067 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL15YANLAN | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL15IBRBAD | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL15OLIPRI | WTA_MAIN | 0.1 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.033 | 1 | **WAKING** |

## PATTERNS (sub-B) — 2
- reality_divergence: KXITFMATCH-26JUL14ALHVUX-ALH {"kind": "resting_bid", "ref": 8.0, "market_mid": 50.5, "divergence": -42.5}
- reality_divergence: KXITFMATCH-26JUL14ALKLIM-LIM {"kind": "resting_bid", "ref": 14.0, "market_mid": 43.0, "divergence": -29.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
