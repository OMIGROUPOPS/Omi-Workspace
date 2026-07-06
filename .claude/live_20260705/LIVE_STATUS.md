# LIVE VALIDATION — rolling status

- cycle 104 @ **2026-07-06 04:28:01 AM ET** | build `edaa04e` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 71227 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 4 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 23:50:46 | **walk_cap_breach** | KXITFWMATCH-26JUL06SIMCIR-SIM | buy 83c > ceiling 73c (conception 69 + cap) ref=join_bid |
| 01:01:56 | **combined_over_goal** | KXITFWMATCH-26JUL06TODSAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 01:12:30 | **combined_over_goal** | KXITFWMATCH-26JUL06VAJRAM | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |
| 03:38:20 | **combined_over_goal** | KXITFWMATCH-26JUL06DZJMCK | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 51 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:51 | ITFWMATCH-26JUL06PASCOP-PAS | ITF_W | underdog | 12 | 8 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:51 | ITFWMATCH-26JUL06LUCGAD-GAD | ITF_W | underdog | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:52 | ITFWMATCH-26JUL06PASCOP-COP | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:59 | ITFWMATCH-26JUL06BRESAF-BRE | ITF_W | leader | 63 | 61 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:04 | ITFWMATCH-26JUL06SIMCIR-CIR | ITF_W | underdog | 16 | 12 | +4 (place_cell) | -30.0 | pre | pair | 97 | EARNED |
| 00:04 | ITFWMATCH-26JUL06SACLAZ-LAZ | ITF_W | underdog | 19 | 11 | +8 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:05 | ITFWMATCH-26JUL06HOSFEH-FEH | ITF_W | underdog | 61 | 63 | -2 (place_cell) | — | pre | single |  | PENDING |
| 00:06 | ITFWMATCH-26JUL06VAJRAM-VAJ | ITF_W | leader | 82 | 74 | +8 (place_cell) | — | pre | pair | 101 | PENDING |
| 00:10 | ITFWMATCH-26JUL06LUCGAD-LUC | ITF_W | leader | 60 | 60 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:17 | ITFMATCH-26JUL06GENAZO-AZO | ITF_M | underdog | 16 | 9 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:22 | ITFMATCH-26JUL06VULCOU-COU | ITF_M | ? | 16 | 10 | +6 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:33 | ITFWMATCH-26JUL06WONIBR-IBR | ITF_W | leader | 65 | 52 | +13 (place_cell) | — | pre | single |  | PENDING |
| 00:33 | ITFWMATCH-26JUL06SIMCIR-SIM | ITF_W | leader | 81 | 81 | +0 (place_cell) | 26.5 | pre | pair | 97 | GIFT_CLASS |
| 00:34 | ITFWMATCH-26JUL06KARBAS-BAS | ITF_W | underdog | 26 | 26 | +0 (place_cell) | — | pre | single |  | PENDING |
| 00:47 | ITFWMATCH-26JUL06TODSAG-TOD | ITF_W | leader | 68 | 62 | +6 (place_cell) | — | pre | pair | 98 | PENDING |
| 00:55 | ITFWMATCH-26JUL06ZRNLUE-LUE | ITF_W | underdog | 69 | 6 | +63 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06VULCOU-VUL | ITF_M | leader | 81 | 80 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06BEASCO-SCO | ITF_M | underdog | 33 | 21 | +12 (place_cell) | — | pre | single |  | PENDING |
| 01:01 | ITFWMATCH-26JUL06TODSAG-SAG | ITF_W | ? | 30 | 25 | +5 (place_cell) | — | pre | pair | 98 | PENDING |
| 01:05 | ITFWMATCH-26JUL06BRESAF-SAF | ITF_W | underdog | 34 | 32 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:12 | ITFWMATCH-26JUL06VAJRAM-RAM | ITF_W | ? | 19 | 9 | +10 (place_cell) | — | pre | pair | 101 | PENDING |
| 01:22 | ITFWMATCH-26JUL06POPSOL-POP | ITF_W | underdog | 36 | 21 | +15 (place_cell) | — | pre | single |  | PENDING |
| 01:23 | ITFMATCH-26JUL06GENAZO-GEN | ITF_M | leader | 81 | 73 | +8 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:44 | ATPCHALLENGERMATCH-26JUL06VILBOC-V | ATP_CHALL | leader | 75 | 72 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 01:51 | ATPCHALLENGERMATCH-26JUL06NIJRAH-R | ATP_CHALL | underdog | 40 | 37 | +3 (place_cell) | — | pre | single |  | PENDING |
| 02:21 | ITFWMATCH-26JUL06WAGYOU-YOU | ITF_W | leader | 63 | 49 | +14 (place_cell) | — | pre | single |  | PENDING |
| 03:05 | ITFWMATCH-26JUL06ZRNLUE-ZRN | ITF_W | ? | 28 | 2 | +26 (place_cell) | — | pre | pair | 97 | PENDING |
| 03:16 | ITFWMATCH-26JUL06BOIBOY-BOI | ITF_W | leader | 77 | 75 | +2 (place_cell) | — | pre | single |  | PENDING |
| 03:29 | ITFMATCH-26JUL06SALNGW-NGW | ITF_M | ? | 39 | 32 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 03:31 | ITFWMATCH-26JUL06KULGON-GON | ITF_W | ? | 22 | 16 | +6 (place_cell) | — | pre | single |  | PENDING |
| 03:34 | ITFMATCH-26JUL06HERNAG-HER | ITF_M | ? | 70 | 49 | +21 (place_cell) | — | pre | single |  | PENDING |
| 03:38 | ITFWMATCH-26JUL06DZJMCK-DZJ | ITF_W | leader | 77 | 41 | +36 (place_cell) | — | pre | pair | 99 | PENDING |
| 03:38 | ITFWMATCH-26JUL06DZJMCK-MCK | ITF_W | underdog | 22 | 12 | +10 (place_cell) | — | pre | pair | 99 | PENDING |
| 03:39 | ITFWMATCH-26JUL06JOSKUM-JOS | ITF_W | underdog | 67 | 79 | -12 (place_cell) | — | pre | single |  | PENDING |
| 03:39 | ITFWMATCH-26JUL06HEDCHI-CHI | ITF_W | underdog | 51 | 20 | +31 (place_cell) | — | pre | pair | 95 | PENDING |
| 03:41 | ITFWMATCH-26JUL06VLADIL-VLA | ITF_W | underdog | 41 | 34 | +7 (place_cell) | — | pre | single |  | PENDING |
| 03:50 | ITFWMATCH-26JUL06HEDCHI-HED | ITF_W | underdog | 44 | 13 | +31 (place_cell) | — | pre | pair | 95 | PENDING |
| 03:55 | ITFMATCH-26JUL06SALNGW-SAL | ITF_M | leader | 58 | 48 | +10 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:00 | ATPCHALLENGERMATCH-26JUL06PRIORA-P | ATP_CHALL | leader | 56 | 54 | +2 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 04:01 | ITFMATCH-26JUL06LARJIM-LAR | ITF_M | underdog | 40 | 31 | +9 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:07 | ITFWMATCH-26JUL06DIANIK-NIK | ITF_W | leader | 52 | 49 | +3 (place_cell) | — | pre | single |  | PENDING |
| 04:09 | ATPCHALLENGERMATCH-26JUL06KRACRI-C | ATP_CHALL | underdog | 6 | 6 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:10 | ITFMATCH-26JUL06LARJIM-JIM | ITF_M | ? | 57 | 48 | +9 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:10 | ITFMATCH-26JUL06KASLIL-LIL | ITF_M | ? | 31 | 1 | +30 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:10 | ITFMATCH-26JUL06LAZVAC-VAC | ITF_M | underdog | 39 | 30 | +9 (place_cell) | — | pre | pair | 95 | PENDING |
| 04:11 | ATPCHALLENGERMATCH-26JUL06CAMDE-DE | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | single |  | MIXED |
| 04:12 | ITFWMATCH-26JUL06SACLAZ-SAC | ITF_W | leader | 78 | 73 | +5 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:13 | ITFMATCH-26JUL06LAZVAC-LAZ | ITF_M | leader | 56 | 48 | +8 (place_cell) | — | pre | pair | 95 | PENDING |
| 04:13 | ATPCHALLENGERMATCH-26JUL06KRACRI-K | ATP_CHALL | leader | 91 | 89 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:16 | ITFMATCH-26JUL06KASLIL-KAS | ITF_M | underdog | 66 | 3 | +63 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:21 | ITFMATCH-26JUL06CASBAY-CAS | ITF_M | underdog | 45 | 2 | +43 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 209 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 14, 'FLOW_ABOVE': 73, 'NO_FLOW': 122} | repriceable now: true 32 / false 177 | **cumulative bid_grade lines: 1498 (repriceable true 161 / false 1337)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06BASHOE-B | 47 | 57m | 1/50-50/20 | 47-50 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ATPCHALLENGERMATCH-26JUL06BASHOE-H | 51 | 57m | 1/52-52/46 | 51-52 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ATPCHALLENGERMATCH-26JUL06CAMDE-CA | 58 | 185m | 6/61-63/431 | 60-61 | 3 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06CAMDE-CA | 58 | 16m | 1/63-63/8 | 60-61 | 5 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06CHEYEV-C | 61 | 87m | 3/62-62/57 | 61-62 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→62 |
| ATPCHALLENGERMATCH-26JUL06CHEYEV-Y | 37 | 87m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DALCAR-C | 3 | 177m | 16/4-4/1042 | 3-4 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06DALCAR-D | 96 | 177m | 8/97-97/359 | 96-97 | 1 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06DELWAL-D | 27 | 147m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DELWAL-W | 71 | 147m | 1/71-71/9 | 71-73 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-C | 24 | 27m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-D | 75 | 20m | 0 | 75-76 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-E | 95 | 117m | 0 | 95-96 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-S | 4 | 117m | 0 | 4-5 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-G | 71 | 177m | 0 | 72-74 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | 26 | 158m | 2/27-27/523 | 26-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-H | 35 | 117m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-P | 61 | 117m | 2/67-67/29 | 63-67 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-D | 20 | 57m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-I | 78 | 57m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 5 | 13m | 114/6-21/10628 | 19-6 | 1 | **FLOW_ABOVE** | 5 | flow above but bound 5c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06KUZSTR-K | 73 | 87m | 1/74-74/32 | 73-74 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ATPCHALLENGERMATCH-26JUL06KUZSTR-S | 26 | 87m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARBER-B | 58 | 177m | 3/59-59/133 | 59-59 | 1 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06MARBER-M | 40 | 177m | 5/41-42/196 | 40-42 | 1 | **FLOW_ABOVE** | 39 | flow above but bound 39c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06MARHAM-H | 5 | 117m | 0 | 5-6 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARHAM-M | 94 | 103m | 1/95-95/0 | 94-95 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→95 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH-N | 57 | 153m | 9/60-60/378 | 59-59 | 3 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06OPIPET-O | 26 | 87m | 2/27-27/352 | 28-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ATPCHALLENGERMATCH-26JUL06OPIPET-P | 71 | 27m | 0 | 72-72 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PAPJAN-P | 53 | 147m | 2/55-55/54 | 54-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-M | 53 | 46m | 1/55-55/100 | 53-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-P | 45 | 47m | 11/47-47/1066 | 45-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ATPCHALLENGERMATCH-26JUL06POLHAI-H | 68 | 28m | 0 | 68-70 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POLHAI-P | 31 | 28m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-F | 58 | 177m | 2/60-60/181 | 58-60 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ATPCHALLENGERMATCH-26JUL06POTFEL-P | 40 | 177m | 1/42-42/15 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 243m | 22/42-45/2489 | 44-43 | 2 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 26m | 1/45-45/10 | 44-43 | 5 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 61 | 117m | 0 | 65-69 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 32 | 116m | 0 | 32-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-B | 36 | 147m | 1/37-37/7 | 36-37 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-S | 61 | 147m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-M | 10 | 176m | 1/10-10/0 | 10-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-S | 88 | 177m | 1/90-90/0 | 88-90 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 207m | 1/35-35/349 | 33-34 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ATPCHALLENGERMATCH-26JUL06STALEC-S | 64 | 173m | 6/66-67/166 | 64-66 | 2 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06VALZHU-V | 71 | 57m | 1/73-73/17 | 71-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ATPCHALLENGERMATCH-26JUL06VALZHU-Z | 27 | 57m | 0 | 27-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 22 | 163m | 159/25-47/10976 | 37-25 | 3 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 20 | 1m | 5/38-39/185 | 37-25 | 18 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06WALNEU-N | 28 | 26m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06WALNEU-W | 70 | 27m | 0 | 70-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-D | 42 | 117m | 1/44-44/11 | 42-44 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-Z | 56 | 117m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL06DECOB-COB | 23 | 27m | 14/23-24/12385 | 23-24 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL06ALEREG-ALE | 51 | 23m | 0 | 51-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALEREG-REG | 40 | 24m | 0 | 40-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-ALI | 91 | 6m | 0 | 91-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-MIS | 6 | 116m | 0 | 6-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 201m | 118/66-88/15757 | 87-66 | 2 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 5m | 31/82-88/1598 | 87-66 | 18 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BONFAU-FAU | 25 | 116m | 0 | 25-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-DUG | 63 | 104m | 0 | 63-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-HOF | 20 | 103m | 0 | 20-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUHCAR-CAR | 12 | 26m | 0 | 12-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUHCAR-DUH | 83 | 29m | 0 | 83-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-ELD | 64 | 134m | 1/69-69/2 | 64-69 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 31 | 29m | 0 | 31-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GANVER-GAN | 4 | 17m | 0 | 46-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GANVER-VER | 47 | 1m | 0 | 47-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GARCIO-CIO | 39 | 29m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GARCIO-GAR | 56 | 35m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 176m | 208/1-19/17506 | 18-1 | -15 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06HERNAG-NAG | 27 | 28m | 0 | 27-51 | — | **NO_FLOW** | 27 |  |
| ITFMATCH-26JUL06HOSGAT-GAT | 38 | 29m | 0 | 38-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HOSGAT-HOS | 56 | 1m | 0 | 56-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06JAIHEN-JAI | 45 | 26m | 0 | 45-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-LIL | 28 | 9m | 16/28-44/516 | 29-29 | 0 | **FLOW_AT_LEVEL** | 31 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 32 | 104m | 0 | 32-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-THE | 65 | 172m | 0 | 65-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MEHCOU-COU | 52 | 23m | 0 | 52-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MEHCOU-MEH | 26 | 40m | 0 | 26-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-BEC | 87 | 27m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-ROJ | 10 | 27m | 0 | 10-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALBRE-BRE | 6 | 176m | 3/11-11/29 | 6-8 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALBRE-SAL | 89 | 172m | 1/94-94/21 | 89-93 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06STAGUI-GUI | 26 | 6m | 0 | 26-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STAGUI-STA | 25 | 6m | 0 | 25-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STEAUN-AUN | 14 | 27m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STEAUN-STE | 82 | 27m | 0 | 82-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TEUHAS-HAS | 56 | 1m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TEUHAS-TEU | 33 | 26m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TIMJEF-JEF | 71 | 18m | 0 | 71-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TIMJEF-TIM | 19 | 40m | 0 | 19-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRA | 24 | 85m | 0 | 24-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRU | 66 | 87m | 0 | 66-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-AND | 24 | 14m | 0 | 24-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-TSI | 59 | 14m | 0 | 59-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VULCOU-VUL | 81 | 11m | 11/98-99/1550 | 99-85 | 17 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ADKFER-ADK | 53 | 103m | 0 | 53-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ADKFER-FER | 18 | 103m | 0 | 18-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 71m | 0 | 28-31 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 17m | 0 | 28-31 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06BOSTOP-BOS | 67 | 56m | 2/68-68/4 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFWMATCH-26JUL06BOSTOP-TOP | 33 | 148m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 199m | 1129/21-59/137829 | 58-22 | -13 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06BUYALV-ALV | 22 | 78m | 0 | 22-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BUYALV-BUY | 54 | 39m | 0 | 54-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DIANIK-DIA | 44 | 67m | 0 | 46-56 | — | **NO_FLOW** | 45 |  |
| ITFWMATCH-26JUL06DIANIK-DIA | 45 | 13m | 0 | 46-56 | — | **NO_FLOW** | 45 |  |
| ITFWMATCH-26JUL06EWAMAN-EWA | 66 | 40m | 0 | 66-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EWAMAN-MAN | 20 | 69m | 0 | 20-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-GAL | 76 | 127m | 1/80-80/2 | 76-80 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL06GALTSE-TSE | 21 | 138m | 0 | 21-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-GAN | 83 | 116m | 1/89-89/2 | 83-89 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-PUI | 11 | 108m | 0 | 11-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 25 | 1m | 23/95-99/781 | 98-58 | 70 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ILIEBE-EBE | 52 | 147m | 0 | 52-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ILIEBE-ILI | 38 | 78m | 0 | 38-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06IVAKUH-IVA | 62 | 184m | 15/63-64/931 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL06IVAKUH-KUH | 37 | 205m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06JOSKUM-KUM | 30 | 6m | 148/51-75/9761 | 75-35 | 21 | **FLOW_ABOVE** | 30 | flow above but bound 30c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARBAS-KAR | 71 | 232m | 5/75-76/40 | 71-72 | 4 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARBAS-KAR | 67 | 135m | 0 | 72-72 | — | **NO_FLOW** | 71 |  |
| ITFWMATCH-26JUL06KARVIS-KAR | 77 | 23m | 0 | 77-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARVIS-VIS | 14 | 115m | 0 | 14-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOTCHI-KOT | 33 | 121m | 0 | 33-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOVDAE-DAE | 18 | 57m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOVDAE-KOV | 75 | 57m | 0 | 75-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 57m | 1/79-79/5 | 75-79 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 57m | 1/79-79/5 | 75-79 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 244m | 3895/23-99/459986 | 99-24 | -14 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06LUKNOE-LUK | 69 | 128m | 1/74-74/6 | 69-74 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06LUKNOE-NOE | 27 | 3m | 0 | 27-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARGLU-GLU | 66 | 1m | 0 | 66-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARGLU-MAR | 28 | 26m | 0 | 28-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-ENC | 51 | 74m | 0 | 51-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-MCA | 42 | 63m | 0 | 42-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MILHER-HER | 14 | 74m | 0 | 14-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MILHER-MIL | 65 | 39m | 0 | 65-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKASAK-OKA | 26 | 39m | 0 | 26-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-OKU | 54 | 72m | 0 | 54-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-PRI | 39 | 74m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PACLOV-LOV | 45 | 47m | 7/46-47/654 | 45-46 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL06PACLOV-PAC | 56 | 146m | 1/56-56/50 | 56-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 148m | 1942/1-13/312225 | 14-1 | -7 | **FLOW_AT_LEVEL** | 12 |  |
| ITFWMATCH-26JUL06PEEPAH-PAH | 58 | 99m | 4/64-65/93 | 58-64 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06PEEPAH-PEE | 37 | 125m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PIERAD-PIE | 58 | 76m | 0 | 58-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PIERAD-RAD | 29 | 4m | 0 | 29-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PODLUK-LUK | 68 | 74m | 0 | 68-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PODLUK-POD | 26 | 77m | 0 | 26-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06POPSOL-SOL | 61 | 185m | 11/66-76/49 | 66-63 | 5 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06POPSOL-SOL | 61 | 10m | 2/66-76/1 | 66-63 | 5 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06POZMLA-MLA | 5 | 39m | 0 | 5-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-NIJ | 30 | 57m | 0 | 30-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-PRI | 63 | 57m | 0 | 63-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06RICMIT-MIT | 7 | 207m | 18/8-90/167 | 7-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFWMATCH-26JUL06SACLAZ-LAZ | 15 | 4m | 60/16-28/2795 | 40-16 | 1 | **FLOW_ABOVE** | 19 | REPRICEABLE→16 |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 195m | 16366/1-95/1383948 | 83-1 | -13 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06SPIMED-MED | 5 | 176m | 2/14-14/24 | 5-14 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06SPIMED-SPI | 86 | 128m | 3/95-95/25 | 86-95 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-SCH | 6 | 144m | 0 | 6-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-TEI | 78 | 6m | 0 | 78-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-TRI | 8 | 134m | 0 | 8-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-VOR | 65 | 6m | 0 | 65-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-EVA | 36 | 33m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-URR | 61 | 27m | 0 | 61-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 194m | 3560/3-29/445489 | 20-4 | -12 | **FLOW_AT_LEVEL** | 15 |  |
| ITFWMATCH-26JUL06VIRKOV-KOV | 29 | 39m | 0 | 29-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VIRKOV-VIR | 56 | 72m | 0 | 56-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-DIL | 56 | 47m | 8/60-65/329 | 60-60 | 4 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06WAGYOU-WAG | 34 | 95m | 0 | 34-52 | — | **NO_FLOW** | 34 |  |
| ITFWMATCH-26JUL06WAGYOU-WAG | 34 | 23m | 0 | 34-52 | — | **NO_FLOW** | 34 |  |
| ITFWMATCH-26JUL06WONIBR-WON | 32 | 193m | 18/72-92/75 | 79-57 | 40 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ARANIL-A | 73 | 104m | 1/75-75/56 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| WTACHALLENGERMATCH-26JUL06ARANIL-N | 25 | 117m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 74 | 27m | 0 | 74-76 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 24 | 27m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BLIAND-A | 35 | 27m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BLIAND-B | 64 | 27m | 0 | 64-65 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BOUKOT-B | 22 | 207m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| WTACHALLENGERMATCH-26JUL06BOUKOT-K | 77 | 200m | 4/78-79/1520 | 77-78 | 1 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06BULSTR-B | 71 | 207m | 2/71-74/23 | 71-74 | 0 | **FLOW_AT_LEVEL** | 68 |  |
| WTACHALLENGERMATCH-26JUL06BULSTR-S | 27 | 143m | 2/28-29/56 | 27-29 | 1 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06GRAMAS-G | 32 | 117m | 1/33-33/100 | 32-33 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| WTACHALLENGERMATCH-26JUL06GRAMAS-M | 67 | 117m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 41 | 207m | 1/43-43/28 | 41-43 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| WTACHALLENGERMATCH-26JUL06HERNGU-N | 58 | 71m | 3/59-59/950 | 58-59 | 1 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06HESPAL-H | 30 | 118m | 0 | 30-31 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HESPAL-P | 69 | 118m | 1/70-70/24 | 69-70 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| WTACHALLENGERMATCH-26JUL06LEWMAR-L | 55 | 117m | 0 | 55-57 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06LEWMAR-M | 43 | 117m | 1/44-44/12 | 43-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| WTACHALLENGERMATCH-26JUL06MATPUT-M | 9 | 117m | 1/9-9/0 | 9-10 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MATPUT-P | 89 | 117m | 2/91-91/35 | 90-91 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| WTACHALLENGERMATCH-26JUL06MONPOP-M | 46 | 64m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MONPOP-P | 54 | 205m | 3/55-55/1441 | 54-55 | 1 | **FLOW_ABOVE** | 52 | flow above but bound 52c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06NOHBUR-B | 22 | 137m | 5/24-24/472 | 23-23 | 2 | **FLOW_ABOVE** | 21 | flow above but bound 21c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06NOHBUR-N | 75 | 27m | 0 | 75-76 | — | **NO_FLOW** | 73 |  |
| WTACHALLENGERMATCH-26JUL06OLIUCH-O | 59 | 27m | 5/61-61/805 | 60-60 | 2 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06OLIUCH-U | 39 | 87m | 5/40-40/247 | 40-40 | 1 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ROMSEM-R | 42 | 87m | 0 | 43-44 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06ROMSEM-S | 56 | 118m | 1/57-57/8 | 56-57 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| WTACHALLENGERMATCH-26JUL06WALKAW-K | 43 | 27m | 1/44-44/11 | 43-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| WTACHALLENGERMATCH-26JUL06WALKAW-W | 55 | 27m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-S | 67 | 27m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-W | 31 | 27m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL06KRUKOS-KRU | 31 | 147m | 57/31-32/5634 | 32-32 | 0 | **FLOW_AT_LEVEL** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06KARBAS | 26 | 72 | **98** | 97 | +1 |
| ITFMATCH-26JUL06BEASCO | 33 | 66 | **99** | 97 | +2 |
| ITFWMATCH-26JUL06POPSOL | 36 | 63 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH | 40 | 59 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06PRIORA | 56 | 43 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06VILBOC | 75 | 25 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL06CAMDE | 39 | 61 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06KULGON | 22 | 79 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06VLADIL | 41 | 60 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06JOSKUM | 67 | 35 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06BOIBOY | 77 | 31 | **108** | 97 | +11 |
| ITFWMATCH-26JUL06DIANIK | 52 | 56 | **108** | 97 | +11 |
| ITFWMATCH-26JUL06WAGYOU | 63 | 52 | **115** | 97 | +18 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ITFMATCH-26JUL06HERNAG | 70 | 51 | **121** | 97 | +24 |
| ITFWMATCH-26JUL06WONIBR | 65 | 57 | **122** | 97 | +25 |

## PATTERNS (sub-B) — 15
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SIMCIR-SIM {"price": 84, "ceiling": 73}
- deep_neg_fv: KXITFWMATCH-26JUL06SIMCIR-CIR {"entry_minus_fv_burst": -30.0}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 262, "mode": "SET_BELOW_FLOW(prints 70c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 235, "mode": "SET_BELOW_FLOW(prints 40c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06KARBAS-BAS {"fill": 26, "age_min": 233, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFMATCH-26JUL06BEASCO-SCO {"fill": 33, "age_min": 207, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06POPSOL-POP {"fill": 36, "age_min": 185, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VILBOC-VIL {"fill": 75, "age_min": 163, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06NIJRAH-RAH {"fill": 40, "age_min": 156, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06WAGYOU-YOU {"fill": 63, "age_min": 127, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06BOIBOY-BOI {"fill": 77, "age_min": 72, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06KULGON-GON {"fill": 22, "age_min": 57, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFMATCH-26JUL06HERNAG-HER {"fill": 70, "age_min": 53, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06JOSKUM-JOS {"fill": 67, "age_min": 48, "mode": "SET_BELOW_FLOW(prints 21c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06VLADIL-VLA {"fill": 41, "age_min": 47, "mode": "SET_BELOW_FLOW(prints 4c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
