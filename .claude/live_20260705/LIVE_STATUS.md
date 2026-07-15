# LIVE VALIDATION — rolling status

- cycle 55 @ **2026-07-15 12:29:35 AM ET** | build `a6b9972c` | session boot 07-15 00:19 ET | log `live_v3_20260715.jsonl` | 3353 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL15MARMAG-MAG aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15OVCCOR-OVC aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15IANDAR-DAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15VISGIA-GIA aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 2 item(s)
- **reality_divergence**: KXITFMATCH-26JUL14ALHVUX-ALH {"kind": "resting_bid", "ref": 8.0, "market_mid": 50.5, "divergence": -42.5, "emitted_et": "2026-07-15 12:29:35 AM ET"}
- **reality_divergence**: KXITFMATCH-26JUL14ALKLIM-LIM {"kind": "resting_bid", "ref": 14.0, "market_mid": 43.0, "divergence": -29.0, "emitted_et": "2026-07-15 12:29:35 AM ET"}
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:25 | ITFMATCH-26JUL14ALHVUX-VUX | ITF_M | underdog | 77 | 87 | -10 (place_cell) | — | pre | single |  | PENDING |
| 00:27 | ITFMATCH-26JUL14KOAYAZ-YAZ | ITF_M | leader | 59 | 72 | -13 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 88 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 84, 'FLOW_ABOVE': 3, 'FLOW_AT_LEVEL': 1} | repriceable now: true 0 / false 88 | **cumulative bid_grade lines: 10089 (repriceable true 1469 / false 8620)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPMATCH-26JUL14RINTAB-TAB | 28 | 8m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15BASTIR-BAS | 27 | 7m | 0 | 30-31 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15BUBHAL-BUB | 65 | 7m | 0 | 69-70 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15CERKEC-KEC | 44 | 7m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15RUBPEL-RUB | 64 | 7m | 0 | 75-76 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15TABMID-MID | 23 | 7m | 0 | 23-27 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15TABMID-TAB | 70 | 7m | 0 | 74-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14ALHVUX-ALH | 8 | 2m | 0 | 12-89 | — | **NO_FLOW** | 20 |  |
| ITFMATCH-26JUL14ALKLIM-ALK | 16 | 1m | 0 | 16-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14ALKLIM-LIM | 14 | 7m | 1/14-14/30 | 16-69 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL14IBRBOB-BOB | 63 | 6m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14IBRBOB-IBR | 15 | 5m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14KOAYAZ-KOA | 29 | 3m | 7/42-66/121 | 36-44 | 13 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ITFMATCH-26JUL14SIKMAT-MAT | 64 | 5m | 0 | 76-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL14SIKMAT-SIK | 19 | 5m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15AUNALV-ALV | 19 | 8m | 0 | 32-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15AUNALV-AUN | 48 | 8m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BAXCOU-BAX | 78 | 6m | 0 | 91-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BENCOR-BEN | 56 | 8m | 0 | 72-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BENCOR-COR | 19 | 8m | 0 | 24-26 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BLAMAR-BLA | 71 | 6m | 0 | 84-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BONBER-BER | 37 | 6m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15BONBER-BON | 30 | 6m | 0 | 43-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CARBAR-BAR | 72 | 4m | 0 | 85-90 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CARBAR-CAR | 8 | 6m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CASCHE-CAS | 42 | 6m | 0 | 58-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15CASCHE-CHE | 23 | 6m | 0 | 36-41 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15DOMBER-BER | 31 | 6m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15GLOHAL-GLO | 11 | 6m | 0 | 17-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15GLOHAL-HAL | 66 | 6m | 0 | 79-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HERPED-HER | 19 | 8m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HERPED-PED | 50 | 8m | 0 | 64-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HOSDUH-HOS | 32 | 6m | 0 | 45-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15JADAUB-AUB | 18 | 8m | 0 | 24-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15JADAUB-JAD | 57 | 8m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15LOPTAL-LOP | 47 | 8m | 0 | 61-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15LOPTAL-TAL | 24 | 8m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PEICHA-CHA | 38 | 8m | 0 | 55-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PEICHA-PEI | 29 | 8m | 0 | 42-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PERBEA-BEA | 35 | 6m | 0 | 50-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PERBEA-PER | 31 | 6m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PERGAR-GAR | 5 | 7m | 0 | 8-11 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PERGAR-PER | 76 | 8m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PRAGHA-GHA | 75 | 8m | 0 | 88-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15PRAGHA-PRA | 5 | 8m | 0 | 11-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15SAHLAL-LAL | 15 | 8m | 0 | 28-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15SAHLAL-SAH | 53 | 8m | 0 | 67-71 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15STEMAK-MAK | 39 | 8m | 1/58-58/83 | 53-58 | 19 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15STEMAK-STE | 28 | 8m | 0 | 41-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WIEWIT-WIE | 72 | 8m | 0 | 84-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WIEWIT-WIT | 10 | 8m | 0 | 12-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ARYMAM-ARY | 15 | 8m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ARYMAM-MAM | 65 | 8m | 0 | 77-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CHADAD-CHA | 22 | 8m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CHADAD-DAD | 50 | 8m | 0 | 67-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CHILEW-CHI | 20 | 7m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15CHILEW-LEW | 52 | 7m | 0 | 65-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ERCBIE-BIE | 5 | 5m | 0 | 11-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15ERCBIE-ERC | 75 | 5m | 0 | 87-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15JANISM-ISM | 45 | 8m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15JANISM-JAN | 27 | 8m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15KUZBEL-BEL | 57 | 6m | 0 | 70-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15KUZBEL-KUZ | 16 | 6m | 0 | 27-28 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LENBER-BER | 26 | 5m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LENBER-LEN | 46 | 5m | 0 | 59-62 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LEYKHR-LEY | 81 | 6m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LOVROC-LOV | 40 | 6m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LOVROC-ROC | 32 | 6m | 0 | 43-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15MILDYU-DYU | 7 | 6m | 0 | 12-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15MILDYU-MIL | 75 | 6m | 0 | 86-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15PAVCHA-PAV | 76 | 8m | 0 | 91-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SMEROJ-ROJ | 59 | 8m | 0 | 75-77 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SMEROJ-SME | 15 | 8m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SMIVAN-SMI | 81 | 6m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15SOZKEN-KEN | 38 | 8m | 1/53-53/31 | 50-53 | 15 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15SOZKEN-SOZ | 34 | 8m | 0 | 47-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15STEMAS-MAS | 30 | 8m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15STEMAS-STE | 42 | 8m | 0 | 56-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TREHEU-HEU | 16 | 5m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TREHEU-TRE | 62 | 5m | 0 | 75-77 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15VISGIA-VIS | 78 | 6m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15VOGNUU-NUU | 18 | 5m | 0 | 24-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15VOGNUU-VOG | 58 | 6m | 0 | 72-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WAGCIR-CIR | 70 | 5m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WAGCIR-WAG | 9 | 5m | 0 | 15-18 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15IBRBAD-BAD | 77 | 1m | 0 | 85-86 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15OLIPRI-OLI | 50 | 7m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15SHEQUE-SHE | 61 | 7m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL14KOAYAZ | 59 | 44 | **103** | 97 | +6 |
| ITFMATCH-26JUL14ALHVUX | 77 | 89 | **166** | 97 | +69 |

## FLOW-STATE — 53 tracked game(s) ({'WAKING': 53}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL14RINTAB | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL15BUBHAL | ATP_MAIN | 0.033 | 1 | **WAKING** |
| ATPMATCH-26JUL15CERKEC | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ATPMATCH-26JUL15TABMID | ATP_MAIN | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL14ALHVUX | ITF_M | 0.1 | 13 | **WAKING** |
| ITFMATCH-26JUL14ALKLIM | ITF_M | 0.133 | 43 | **WAKING** |
| ITFMATCH-26JUL14IBRBOB | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL14KOAYAZ | ITF_M | 0.6 | 8 | **WAKING** |
| ITFMATCH-26JUL14SIKMAT | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL15AUNALV | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL15BAXCOU | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15BENCOR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15BLAMAR | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15BONBER | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15CARBAR | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL15CASCHE | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15DOMBER | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15GLOHAL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15HERPED | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15HOSDUH | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15JADAUB | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15LOPTAL | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL15PEICHA | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15PERBEA | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15PERGAR | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL15PRAGHA | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL15SAHLAL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL15STEMAK | ITF_M | 0.067 | 5 | **WAKING** |
| ITFMATCH-26JUL15WIEWIT | ITF_M | 0.133 | 2 | **WAKING** |
| ITFWMATCH-26JUL15ARYMAM | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL15CHADAD | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15CHILEW | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15ERCBIE | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15JANISM | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL15KUZBEL | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL15LENBER | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15LEYKHR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15LOVROC | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15MILDYU | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL15PAVCHA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15SMEROJ | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15SMIVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15SOZKEN | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL15STEMAS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15TREHEU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15VISGIA | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15VOGNUU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15WAGCIR | ITF_W | 0.0 | 3 | **WAKING** |
| WTAMATCH-26JUL15IBRBAD | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL15OLIPRI | WTA_MAIN | 0.1 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 2
- reality_divergence: KXITFMATCH-26JUL14ALHVUX-ALH {"kind": "resting_bid", "ref": 8.0, "market_mid": 50.5, "divergence": -42.5, "emitted_et": "2026-07-15 12:29:35 AM ET"}
- reality_divergence: KXITFMATCH-26JUL14ALKLIM-LIM {"kind": "resting_bid", "ref": 14.0, "market_mid": 43.0, "divergence": -29.0, "emitted_et": "2026-07-15 12:29:35 AM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
