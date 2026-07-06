# LIVE VALIDATION — rolling status

- cycle 88 @ **2026-07-06 01:45:17 AM ET** | build `fbb7c2f` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 44752 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 01:01:56 | **combined_over_goal** | KXITFWMATCH-26JUL06TODSAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 01:12:30 | **combined_over_goal** | KXITFWMATCH-26JUL06VAJRAM | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 24 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:51 | ITFWMATCH-26JUL06PASCOP-PAS | ITF_W | underdog | 12 | 8 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:51 | ITFWMATCH-26JUL06LUCGAD-GAD | ITF_W | underdog | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:52 | ITFWMATCH-26JUL06PASCOP-COP | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:59 | ITFWMATCH-26JUL06BRESAF-BRE | ITF_W | leader | 63 | 61 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:04 | ITFWMATCH-26JUL06SIMCIR-CIR | ITF_W | underdog | 16 | 12 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:04 | ITFWMATCH-26JUL06SACLAZ-LAZ | ITF_W | underdog | 19 | 11 | +8 (place_cell) | — | pre | single |  | PENDING |
| 00:05 | ITFWMATCH-26JUL06HOSFEH-FEH | ITF_W | underdog | 61 | 63 | -2 (place_cell) | — | pre | single |  | PENDING |
| 00:06 | ITFWMATCH-26JUL06VAJRAM-VAJ | ITF_W | leader | 82 | 74 | +8 (place_cell) | — | pre | pair | 101 | PENDING |
| 00:10 | ITFWMATCH-26JUL06LUCGAD-LUC | ITF_W | leader | 60 | 60 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:17 | ITFMATCH-26JUL06GENAZO-AZO | ITF_M | underdog | 16 | 9 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:22 | ITFMATCH-26JUL06VULCOU-COU | ITF_M | ? | 16 | 10 | +6 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:33 | ITFWMATCH-26JUL06WONIBR-IBR | ITF_W | leader | 65 | 52 | +13 (place_cell) | — | pre | single |  | PENDING |
| 00:33 | ITFWMATCH-26JUL06SIMCIR-SIM | ITF_W | leader | 81 | 81 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:34 | ITFWMATCH-26JUL06KARBAS-BAS | ITF_W | underdog | 26 | 26 | +0 (place_cell) | — | pre | single |  | PENDING |
| 00:47 | ITFWMATCH-26JUL06TODSAG-TOD | ITF_W | leader | 68 | 62 | +6 (place_cell) | — | pre | pair | 98 | PENDING |
| 00:55 | ITFWMATCH-26JUL06ZRNLUE-LUE | ITF_W | underdog | 69 | 6 | +63 (place_cell) | — | pre | single |  | PENDING |
| 01:00 | ITFMATCH-26JUL06VULCOU-VUL | ITF_M | leader | 81 | 80 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06BEASCO-SCO | ITF_M | underdog | 33 | 21 | +12 (place_cell) | — | pre | single |  | PENDING |
| 01:01 | ITFWMATCH-26JUL06TODSAG-SAG | ITF_W | ? | 30 | 25 | +5 (place_cell) | — | pre | pair | 98 | PENDING |
| 01:05 | ITFWMATCH-26JUL06BRESAF-SAF | ITF_W | underdog | 34 | 32 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:12 | ITFWMATCH-26JUL06VAJRAM-RAM | ITF_W | ? | 19 | 9 | +10 (place_cell) | — | pre | pair | 101 | PENDING |
| 01:22 | ITFWMATCH-26JUL06POPSOL-POP | ITF_W | underdog | 36 | 21 | +15 (place_cell) | — | pre | single |  | PENDING |
| 01:23 | ITFMATCH-26JUL06GENAZO-GEN | ITF_M | leader | 81 | 73 | +8 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:44 | ATPCHALLENGERMATCH-26JUL06VILBOC-V | ATP_CHALL | leader | 75 | 72 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 67 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 21, 'FLOW_AT_LEVEL': 5, 'NO_FLOW': 41} | repriceable now: true 10 / false 57 | **cumulative bid_grade lines: 1011 (repriceable true 111 / false 900)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06CAMDE-CA | 58 | 22m | 1/61-61/312 | 59-61 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ATPCHALLENGERMATCH-26JUL06CAMDE-DE | 39 | 45m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DALCAR-C | 3 | 15m | 0 | 3-4 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DALCAR-D | 96 | 15m | 0 | 96-97 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-G | 71 | 15m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 105m | 21/8-9/1163 | 6-8 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ATPCHALLENGERMATCH-26JUL06KRACRI-K | 92 | 64m | 8/92-94/301 | 92-94 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARBER-B | 58 | 15m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARBER-M | 40 | 15m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06NIJRAH-R | 40 | 45m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-P | 44 | 15m | 0 | 44-46 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-F | 58 | 15m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-P | 40 | 15m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 80m | 4/43-43/50 | 41-43 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-M | 10 | 14m | 0 | 10-12 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-S | 88 | 15m | 0 | 88-90 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 45m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06STALEC-S | 64 | 10m | 1/66-66/34 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 22 | 1m | 0 | 25-25 | — | **NO_FLOW** | 22 |  |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 39m | 1/76-76/1 | 69-66 | 12 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06ELDHAU-ELD | 59 | 71m | 1/69-69/1 | 59-69 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 30 | 68m | 0 | 30-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 13m | 3/16-18/30 | 18-15 | 0 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 27 | 14m | 0 | 27-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-THE | 65 | 9m | 0 | 65-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALBRE-BRE | 6 | 14m | 0 | 6-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALBRE-SAL | 89 | 9m | 1/94-94/21 | 89-93 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALNGW-NGW | 39 | 108m | 4/45-45/89 | 39-45 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALNGW-SAL | 54 | 98m | 2/60-60/27 | 54-60 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 36m | 10/34-42/275 | 41-38 | 0 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06DIANIK-DIA | 28 | 28m | 0 | 28-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DZJMCK-DZJ | 65 | 66m | 0 | 65-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DZJMCK-MCK | 21 | 42m | 0 | 21-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-GAL | 73 | 14m | 0 | 73-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-TSE | 20 | 14m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HEDCHI-CHI | 3 | 12m | 0 | 24-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 13 | 16m | 0 | 84-58 | — | **NO_FLOW** | 36 |  |
| ITFWMATCH-26JUL06IVAKUH-IVA | 62 | 21m | 0 | 62-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06IVAKUH-KUH | 37 | 42m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARBAS-KAR | 71 | 69m | 5/75-76/40 | 71-72 | 4 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KOTCHI-KOT | 26 | 0m | 0 | 26-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-GON | 20 | 14m | 0 | 20-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 1m | 0 | 75-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 82m | 432/36-57/18595 | 44-40 | -1 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06LUKNOE-LUK | 68 | 69m | 3/74-74/39 | 68-74 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06LUKNOE-NOE | 25 | 74m | 1/31-31/4 | 25-31 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 9 | 30m | 199/12-18/26728 | 14-12 | 3 | **FLOW_ABOVE** | 12 | REPRICEABLE→12 |
| ITFWMATCH-26JUL06POPSOL-SOL | 61 | 23m | 6/71-75/42 | 62-63 | 10 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06RICMIT-MIT | 7 | 44m | 12/8-90/131 | 7-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 105m | 50/79-86/406 | 80-82 | 1 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 32m | 108/13-29/22411 | 18-17 | -1 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06SPIMED-MED | 5 | 14m | 0 | 5-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SPIMED-SPI | 83 | 14m | 0 | 83-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 32m | 5/19-25/59 | 20-20 | 4 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06VLADIL-DIL | 55 | 28m | 0 | 55-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-VLA | 40 | 47m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06WONIBR-WON | 32 | 30m | 0 | 73-57 | — | **NO_FLOW** | 32 |  |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 28 | 9m | 0 | 50-39 | — | **NO_FLOW** | 28 |  |
| WTACHALLENGERMATCH-26JUL06BOUKOT-B | 22 | 45m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| WTACHALLENGERMATCH-26JUL06BOUKOT-K | 77 | 37m | 0 | 77-78 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BULSTR-B | 71 | 45m | 0 | 71-74 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BULSTR-S | 26 | 45m | 0 | 26-29 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 41 | 45m | 0 | 41-43 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-N | 57 | 27m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MONPOP-M | 44 | 45m | 5/47-47/204 | 45-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| WTACHALLENGERMATCH-26JUL06MONPOP-P | 54 | 42m | 1/55-55/22 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| WTACHALLENGERMATCH-26JUL06NOHBUR-B | 21 | 39m | 8/22-23/162 | 21-22 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06KARBAS | 26 | 72 | **98** | 97 | +1 |
| ITFMATCH-26JUL06BEASCO | 33 | 66 | **99** | 97 | +2 |
| ITFWMATCH-26JUL06POPSOL | 36 | 63 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06VILBOC | 75 | 25 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06SACLAZ | 19 | 82 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06ZRNLUE | 69 | 39 | **108** | 97 | +11 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ITFWMATCH-26JUL06WONIBR | 65 | 57 | **122** | 97 | +25 |

## PATTERNS (sub-B) — 6
- half_arm_aging: KXITFWMATCH-26JUL06SACLAZ-LAZ {"fill": 19, "age_min": 101, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 100, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 72, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06KARBAS-BAS {"fill": 26, "age_min": 71, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06ZRNLUE-LUE {"fill": 69, "age_min": 50, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFMATCH-26JUL06BEASCO-SCO {"fill": 33, "age_min": 44, "mode": "SET_BELOW_FLOW(prints 12c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
