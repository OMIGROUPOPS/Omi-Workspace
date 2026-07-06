# LIVE VALIDATION — rolling status

- cycle 108 @ **2026-07-06 05:08:57 AM ET** | build `458d616` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 82783 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 5 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 23:50:46 | **walk_cap_breach** | KXITFWMATCH-26JUL06SIMCIR-SIM | buy 83c > ceiling 73c (conception 69 + cap) ref=join_bid |
| 01:01:56 | **combined_over_goal** | KXITFWMATCH-26JUL06TODSAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 01:12:30 | **combined_over_goal** | KXITFWMATCH-26JUL06VAJRAM | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |
| 03:38:20 | **combined_over_goal** | KXITFWMATCH-26JUL06DZJMCK | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 05:04:30 | **combined_over_goal** | KXITFMATCH-26JUL06HERNAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 63 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:51 | ITFWMATCH-26JUL06PASCOP-PAS | ITF_W | underdog | 12 | 8 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:51 | ITFWMATCH-26JUL06LUCGAD-GAD | ITF_W | underdog | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:52 | ITFWMATCH-26JUL06PASCOP-COP | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:59 | ITFWMATCH-26JUL06BRESAF-BRE | ITF_W | leader | 63 | 61 | +2 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 00:04 | ITFWMATCH-26JUL06SIMCIR-CIR | ITF_W | underdog | 16 | 12 | +4 (place_cell) | -30.0 | pre | pair | 97 | EARNED |
| 00:04 | ITFWMATCH-26JUL06SACLAZ-LAZ | ITF_W | underdog | 19 | 11 | +8 (place_cell) | — | pre | pair | 97 | MIXED |
| 00:05 | ITFWMATCH-26JUL06HOSFEH-FEH | ITF_W | underdog | 61 | 63 | -2 (place_cell) | — | pre | single |  | PENDING |
| 00:06 | ITFWMATCH-26JUL06VAJRAM-VAJ | ITF_W | leader | 82 | 74 | +8 (place_cell) | — | pre | pair | 101 | MIXED |
| 00:10 | ITFWMATCH-26JUL06LUCGAD-LUC | ITF_W | leader | 60 | 60 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:17 | ITFMATCH-26JUL06GENAZO-AZO | ITF_M | underdog | 16 | 9 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:22 | ITFMATCH-26JUL06VULCOU-COU | ITF_M | ? | 16 | 10 | +6 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:33 | ITFWMATCH-26JUL06WONIBR-IBR | ITF_W | leader | 65 | 52 | +13 (place_cell) | — | pre | single |  | PENDING |
| 00:33 | ITFWMATCH-26JUL06SIMCIR-SIM | ITF_W | leader | 81 | 81 | +0 (place_cell) | 26.5 | pre | pair | 97 | GIFT_CLASS |
| 00:34 | ITFWMATCH-26JUL06KARBAS-BAS | ITF_W | underdog | 26 | 26 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:47 | ITFWMATCH-26JUL06TODSAG-TOD | ITF_W | leader | 68 | 62 | +6 (place_cell) | — | pre | pair | 98 | MIXED |
| 00:55 | ITFWMATCH-26JUL06ZRNLUE-LUE | ITF_W | underdog | 69 | 6 | +63 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06VULCOU-VUL | ITF_M | leader | 81 | 80 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06BEASCO-SCO | ITF_M | underdog | 33 | 21 | +12 (place_cell) | — | pre | single |  | PENDING |
| 01:01 | ITFWMATCH-26JUL06TODSAG-SAG | ITF_W | ? | 30 | 25 | +5 (place_cell) | — | pre | pair | 98 | MIXED |
| 01:05 | ITFWMATCH-26JUL06BRESAF-SAF | ITF_W | underdog | 34 | 32 | +2 (place_cell) | — | pre | pair | 97 | EARNED |
| 01:12 | ITFWMATCH-26JUL06VAJRAM-RAM | ITF_W | ? | 19 | 9 | +10 (place_cell) | — | pre | pair | 101 | MIXED |
| 01:22 | ITFWMATCH-26JUL06POPSOL-POP | ITF_W | underdog | 36 | 21 | +15 (place_cell) | — | pre | single |  | PENDING |
| 01:23 | ITFMATCH-26JUL06GENAZO-GEN | ITF_M | leader | 81 | 73 | +8 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:44 | ATPCHALLENGERMATCH-26JUL06VILBOC-V | ATP_CHALL | leader | 75 | 72 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 01:51 | ATPCHALLENGERMATCH-26JUL06NIJRAH-R | ATP_CHALL | underdog | 40 | 37 | +3 (place_cell) | — | pre | single |  | MIXED |
| 02:21 | ITFWMATCH-26JUL06WAGYOU-YOU | ITF_W | leader | 63 | 49 | +14 (place_cell) | — | pre | single |  | PENDING |
| 03:05 | ITFWMATCH-26JUL06ZRNLUE-ZRN | ITF_W | ? | 28 | 2 | +26 (place_cell) | — | pre | pair | 97 | PENDING |
| 03:16 | ITFWMATCH-26JUL06BOIBOY-BOI | ITF_W | leader | 77 | 75 | +2 (place_cell) | — | pre | single |  | PENDING |
| 03:29 | ITFMATCH-26JUL06SALNGW-NGW | ITF_M | ? | 39 | 32 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 03:31 | ITFWMATCH-26JUL06KULGON-GON | ITF_W | ? | 22 | 16 | +6 (place_cell) | — | pre | single |  | PENDING |
| 03:34 | ITFMATCH-26JUL06HERNAG-HER | ITF_M | ? | 70 | 49 | +21 (place_cell) | — | pre | pair | 98 | PENDING |
| 03:38 | ITFWMATCH-26JUL06DZJMCK-DZJ | ITF_W | leader | 77 | 41 | +36 (place_cell) | — | pre | pair | 99 | PENDING |
| 03:38 | ITFWMATCH-26JUL06DZJMCK-MCK | ITF_W | underdog | 22 | 12 | +10 (place_cell) | — | pre | pair | 99 | PENDING |
| 03:39 | ITFWMATCH-26JUL06JOSKUM-JOS | ITF_W | underdog | 67 | 79 | -12 (place_cell) | — | pre | single |  | PENDING |
| 03:39 | ITFWMATCH-26JUL06HEDCHI-CHI | ITF_W | underdog | 51 | 20 | +31 (place_cell) | — | pre | pair | 95 | PENDING |
| 03:41 | ITFWMATCH-26JUL06VLADIL-VLA | ITF_W | underdog | 41 | 34 | +7 (place_cell) | — | pre | single |  | PENDING |
| 03:50 | ITFWMATCH-26JUL06HEDCHI-HED | ITF_W | underdog | 44 | 13 | +31 (place_cell) | — | pre | pair | 95 | PENDING |
| 03:55 | ITFMATCH-26JUL06SALNGW-SAL | ITF_M | leader | 58 | 48 | +10 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:00 | ATPCHALLENGERMATCH-26JUL06PRIORA-P | ATP_CHALL | leader | 56 | 54 | +2 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 04:01 | ITFMATCH-26JUL06LARJIM-LAR | ITF_M | underdog | 40 | 31 | +9 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:07 | ITFWMATCH-26JUL06DIANIK-NIK | ITF_W | leader | 52 | 49 | +3 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:09 | ATPCHALLENGERMATCH-26JUL06KRACRI-C | ATP_CHALL | underdog | 6 | 6 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:10 | ITFMATCH-26JUL06LARJIM-JIM | ITF_M | ? | 57 | 48 | +9 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:10 | ITFMATCH-26JUL06KASLIL-LIL | ITF_M | ? | 31 | 1 | +30 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:10 | ITFMATCH-26JUL06LAZVAC-VAC | ITF_M | underdog | 39 | 30 | +9 (place_cell) | — | pre | pair | 95 | PENDING |
| 04:11 | ATPCHALLENGERMATCH-26JUL06CAMDE-DE | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | single |  | MIXED |
| 04:12 | ITFWMATCH-26JUL06SACLAZ-SAC | ITF_W | leader | 78 | 73 | +5 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:13 | ITFMATCH-26JUL06LAZVAC-LAZ | ITF_M | leader | 56 | 48 | +8 (place_cell) | — | pre | pair | 95 | PENDING |
| 04:13 | ATPCHALLENGERMATCH-26JUL06KRACRI-K | ATP_CHALL | leader | 91 | 89 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:16 | ITFMATCH-26JUL06KASLIL-KAS | ITF_M | underdog | 66 | 3 | +63 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:21 | ITFMATCH-26JUL06CASBAY-CAS | ITF_M | underdog | 45 | 2 | +43 (place_cell) | — | pre | single |  | PENDING |
| 04:36 | ITFWMATCH-26JUL06LUKNOE-LUK | ITF_W | leader | 69 | 72 | -3 (place_cell) | — | pre | pair | 95 | PENDING |
| 04:44 | ITFWMATCH-26JUL06KARBAS-KAR | ITF_W | ? | 71 | 70 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:47 | ITFWMATCH-26JUL06LUKNOE-NOE | ITF_W | underdog | 26 | 27 | -1 (place_cell) | — | pre | pair | 95 | PENDING |
| 04:53 | WTAMATCH-26JUL06KRUKOS-KRU | WTA_MAIN | ? | 31 | 30 | +1 (place_cell) | — | pre | single |  | MIXED |
| 04:59 | ITFWMATCH-26JUL06DIANIK-DIA | ITF_W | underdog | 45 | 24 | +21 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:03 | ITFMATCH-26JUL06ELDHAU-ELD | ITF_M | leader | 65 | 56 | +9 (place_cell) | — | pre | single |  | PENDING |
| 05:04 | ITFMATCH-26JUL06HERNAG-NAG | ITF_M | ? | 28 | 1 | +27 (place_cell) | — | pre | pair | 98 | PENDING |
| 05:06 | ITFWMATCH-26JUL06OKUPRI-PRI | ITF_W | underdog | 41 | 25 | +16 (place_cell) | — | pre | single |  | PENDING |
| 05:06 | ATPCHALLENGERMATCH-26JUL06VILBOC-B | ATP_CHALL | underdog | 22 | 21 | +1 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:07 | WTACHALLENGERMATCH-26JUL06OLIUCH-U | WTA_CHALL | underdog | 39 | 37 | +2 (place_cell) | — | pre | single |  | MIXED |
| 05:07 | WTACHALLENGERMATCH-26JUL06BOUKOT-K | WTA_CHALL | leader | 77 | 74 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 05:08 | ITFWMATCH-26JUL06TEISCH-TEI | ITF_W | ? | 86 | 51 | +35 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 221 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 17, 'FLOW_ABOVE': 77, 'NO_FLOW': 127} | repriceable now: true 33 / false 188 | **cumulative bid_grade lines: 1599 (repriceable true 171 / false 1428)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06BARDAL-B | 56 | 8m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06BARDAL-D | 41 | 8m | 0 | 41-42 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06BASHOE-B | 47 | 98m | 2/49-50/30 | 48-49 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→49 |
| ATPCHALLENGERMATCH-26JUL06BASHOE-H | 51 | 98m | 1/52-52/46 | 51-52 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ATPCHALLENGERMATCH-26JUL06CAMDE-CA | 58 | 226m | 7/61-63/715 | 60-61 | 3 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06CAMDE-CA | 58 | 57m | 2/63-63/292 | 60-61 | 5 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06CHADEM-C | 48 | 8m | 0 | 48-51 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CHEYEV-C | 61 | 128m | 4/62-62/111 | 61-62 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→62 |
| ATPCHALLENGERMATCH-26JUL06CHEYEV-Y | 37 | 128m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CHIJAN-C | 76 | 8m | 0 | 76-77 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CHIJAN-J | 23 | 5m | 0 | 23-24 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DALCAR-C | 3 | 218m | 29/4-4/1770 | 3-4 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06DALCAR-D | 96 | 218m | 8/97-97/359 | 96-97 | 1 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06DAMHUE-D | 79 | 8m | 0 | 79-80 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DAMHUE-H | 19 | 8m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DEHUD-DE | 38 | 8m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DEHUD-HU | 61 | 8m | 0 | 61-62 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DELWAL-D | 27 | 188m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DELWAL-W | 71 | 188m | 2/71-73/14 | 71-73 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-C | 24 | 68m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-D | 76 | 31m | 1/77-77/32 | 76-77 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-E | 95 | 158m | 0 | 95-96 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-S | 4 | 158m | 0 | 4-5 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06FOMDHA-D | 52 | 8m | 0 | 52-55 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06FOMDHA-F | 45 | 8m | 0 | 45-46 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-G | 71 | 218m | 1/74-74/5 | 71-74 | 3 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | 26 | 199m | 2/27-27/523 | 26-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-H | 35 | 158m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-P | 61 | 158m | 2/67-67/29 | 64-67 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-D | 20 | 98m | 1/21-21/22 | 20-21 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ATPCHALLENGERMATCH-26JUL06IVADIN-I | 79 | 2m | 1/81-81/30 | 79-80 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→81 |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 5 | 54m | 331/1-21/40759 | 19-1 | -4 | **FLOW_AT_LEVEL** | 5 |  |
| ATPCHALLENGERMATCH-26JUL06KUZSTR-K | 73 | 128m | 1/74-74/32 | 73-74 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ATPCHALLENGERMATCH-26JUL06KUZSTR-S | 26 | 128m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARBER-B | 58 | 218m | 4/59-60/138 | 58-59 | 1 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06MARBER-M | 40 | 218m | 5/41-42/196 | 41-42 | 1 | **FLOW_ABOVE** | 39 | flow above but bound 39c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06MARHAM-H | 5 | 158m | 0 | 5-6 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARHAM-M | 94 | 144m | 1/95-95/0 | 94-95 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→95 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH-N | 57 | 194m | 15/59-60/799 | 59-59 | 2 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06OPIPET-O | 26 | 128m | 2/27-27/352 | 28-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ATPCHALLENGERMATCH-26JUL06OPIPET-P | 71 | 68m | 0 | 72-72 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PAPJAN-P | 53 | 188m | 2/55-55/54 | 54-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-M | 53 | 87m | 4/55-56/275 | 53-55 | 2 | **FLOW_ABOVE** | 52 | flow above but bound 52c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-P | 45 | 88m | 12/47-48/1068 | 45-46 | 2 | **FLOW_ABOVE** | 44 | flow above but bound 44c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06POLHAI-H | 68 | 69m | 0 | 70-71 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POLHAI-P | 31 | 69m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-F | 58 | 218m | 3/60-60/186 | 58-60 | 2 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06POTFEL-P | 40 | 218m | 1/42-42/15 | 40-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 284m | 46/42-55/10634 | 51-43 | 2 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 41 | 6m | 7/53-55/1504 | 51-43 | 12 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 61 | 158m | 2/69-69/19 | 65-68 | 8 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 32 | 157m | 0 | 32-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-B | 36 | 188m | 1/37-37/7 | 36-37 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-S | 61 | 188m | 1/64-64/5 | 61-64 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-M | 10 | 217m | 3/10-12/101 | 10-12 | 0 | **FLOW_AT_LEVEL** | 9 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-S | 88 | 218m | 2/90-91/1 | 88-90 | 2 | **FLOW_ABOVE** | 88 | flow above but bound 88c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 248m | 1/35-35/349 | 33-35 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ATPCHALLENGERMATCH-26JUL06STALEC-S | 64 | 214m | 6/66-67/166 | 64-66 | 2 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06VALZHU-V | 71 | 98m | 1/73-73/17 | 71-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ATPCHALLENGERMATCH-26JUL06VALZHU-Z | 27 | 98m | 0 | 27-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06WALNEU-N | 28 | 67m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06WALNEU-W | 70 | 68m | 0 | 70-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06WEHVAN-V | 42 | 28m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-D | 42 | 158m | 1/44-44/11 | 42-44 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-Z | 56 | 158m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL06DECOB-COB | 23 | 68m | 43/23-24/14656 | 23-24 | 0 | **FLOW_AT_LEVEL** | 22 |  |
| ATPMATCH-26JUL06DECOB-DE | 76 | 8m | 7/77-78/147 | 77-77 | 1 | **FLOW_ABOVE** | 78 | REPRICEABLE→77 |
| ITFMATCH-26JUL06ALEREG-ALE | 51 | 64m | 0 | 51-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALEREG-REG | 40 | 65m | 0 | 40-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-ALI | 91 | 47m | 0 | 91-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-MIS | 6 | 157m | 0 | 6-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 242m | 272/66-97/37805 | 92-66 | 2 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BEASCO-BEA | 60 | 2m | 2/85-85/293 | 92-66 | 25 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BONFAU-FAU | 25 | 157m | 0 | 25-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-DUG | 63 | 145m | 0 | 63-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-HOF | 20 | 144m | 0 | 20-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUHCAR-CAR | 12 | 67m | 0 | 12-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUHCAR-DUH | 83 | 70m | 0 | 83-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 32 | 5m | 6/41-47/381 | 36-38 | 9 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06ELDHAU-HAU | 32 | 4m | 4/41-47/70 | 36-38 | 9 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06GANVER-GAN | 4 | 58m | 0 | 46-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GANVER-VER | 47 | 42m | 0 | 47-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GARCIO-CIO | 39 | 70m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GARCIO-GAR | 56 | 76m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 217m | 213/1-19/18095 | 18-1 | -15 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06HOSGAT-GAT | 38 | 70m | 0 | 38-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HOSGAT-HOS | 56 | 42m | 0 | 56-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06JAIHEN-JAI | 45 | 67m | 0 | 45-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-LIL | 28 | 50m | 114/8-55/4577 | 43-11 | -20 | **FLOW_AT_LEVEL** | 31 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 34 | 31m | 0 | 34-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-THE | 65 | 213m | 1/68-68/2 | 65-66 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL06LUEVAN-LUE | 64 | 5m | 0 | 64-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LUEVAN-VAN | 20 | 5m | 0 | 20-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MEHCOU-COU | 55 | 4m | 0 | 55-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MEHCOU-MEH | 29 | 4m | 0 | 29-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-BEC | 87 | 68m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-ROJ | 10 | 68m | 0 | 10-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALBRE-BRE | 6 | 217m | 3/11-11/29 | 6-8 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALBRE-SAL | 89 | 213m | 1/94-94/21 | 89-93 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06STAGUI-GUI | 28 | 18m | 0 | 28-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STAGUI-STA | 32 | 0m | 0 | 34-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STEAUN-AUN | 14 | 68m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STEAUN-STE | 82 | 68m | 0 | 82-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TEUHAS-HAS | 63 | 40m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TEUHAS-TEU | 33 | 67m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TIMJEF-JEF | 71 | 58m | 0 | 71-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TIMJEF-TIM | 20 | 38m | 0 | 20-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRA | 24 | 126m | 0 | 24-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRU | 67 | 34m | 0 | 67-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-AND | 24 | 55m | 0 | 24-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-TSI | 62 | 22m | 0 | 62-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VULCOU-VUL | 81 | 51m | 11/98-99/1550 | 99-85 | 17 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ADKFER-ADK | 53 | 144m | 0 | 53-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ADKFER-FER | 18 | 144m | 0 | 18-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 112m | 0 | 28-31 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 58m | 0 | 28-31 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06BOSTOP-BOS | 67 | 97m | 2/68-68/4 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFWMATCH-26JUL06BOSTOP-TOP | 33 | 189m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 240m | 2357/21-80/293789 | 76-22 | -13 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06BUYALV-ALV | 22 | 119m | 0 | 22-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BUYALV-BUY | 54 | 80m | 0 | 54-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CENBUL-BUL | 19 | 5m | 0 | 19-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CENBUL-CEN | 6 | 2m | 0 | 67-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EWAMAN-EWA | 67 | 19m | 0 | 67-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EWAMAN-MAN | 20 | 110m | 0 | 20-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-GAL | 77 | 14m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-TSE | 21 | 179m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-GAN | 83 | 157m | 1/89-89/2 | 83-89 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-PUI | 11 | 149m | 0 | 11-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HIEGUT-GUT | 56 | 4m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HIEGUT-HIE | 41 | 8m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 25 | 33m | 1/99-99/12 | 99-58 | 74 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ILIEBE-EBE | 52 | 187m | 0 | 52-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ILIEBE-ILI | 38 | 119m | 0 | 38-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06IVAKUH-IVA | 62 | 225m | 15/63-64/931 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL06IVAKUH-KUH | 37 | 246m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06JOSKUM-KUM | 30 | 2m | 25/35-45/860 | 75-35 | 5 | **FLOW_ABOVE** | 30 | flow above but bound 30c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARVIS-KAR | 77 | 64m | 0 | 77-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARVIS-VIS | 14 | 156m | 0 | 14-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOTCHI-KOT | 46 | 5m | 0 | 46-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOVDAE-DAE | 18 | 98m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOVDAE-KOV | 75 | 98m | 0 | 75-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 98m | 1/79-79/5 | 75-79 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 98m | 1/79-79/5 | 75-79 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULGON-KUL | 71 | 14m | 0 | 75-79 | — | **NO_FLOW** | 75 |  |
| ITFWMATCH-26JUL06KULVOG-KUL | 54 | 5m | 0 | 54-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULVOG-VOG | 36 | 5m | 0 | 36-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 285m | 3895/23-99/459986 | 99-24 | -14 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06MARGLU-GLU | 66 | 41m | 0 | 66-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARGLU-MAR | 28 | 67m | 0 | 28-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-ENC | 51 | 115m | 0 | 51-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-MCA | 42 | 104m | 0 | 42-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MILHER-HER | 14 | 115m | 0 | 14-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MILHER-MIL | 65 | 80m | 0 | 65-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKASAK-OKA | 27 | 25m | 0 | 27-51 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-OKU | 56 | 3m | 1/56-56/1 | 56-58 | 0 | **FLOW_AT_LEVEL** | 56 |  |
| ITFWMATCH-26JUL06PACLOV-LOV | 45 | 88m | 7/46-47/654 | 45-46 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL06PACLOV-PAC | 56 | 187m | 1/56-56/50 | 56-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 189m | 1942/1-13/312225 | 14-1 | -7 | **FLOW_AT_LEVEL** | 12 |  |
| ITFWMATCH-26JUL06PEEPAH-PAH | 58 | 140m | 4/64-65/93 | 58-64 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06PEEPAH-PEE | 37 | 166m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PIERAD-PIE | 58 | 117m | 0 | 58-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PIERAD-RAD | 30 | 7m | 0 | 30-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PODLUK-LUK | 69 | 17m | 0 | 69-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PODLUK-POD | 26 | 118m | 0 | 26-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06POPSOL-SOL | 61 | 226m | 24/66-82/225 | 76-63 | 5 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06POPSOL-SOL | 60 | 2m | 0 | 76-63 | — | **NO_FLOW** | 61 |  |
| ITFWMATCH-26JUL06POZMLA-MLA | 5 | 80m | 0 | 5-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-NIJ | 30 | 98m | 0 | 30-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-PRI | 63 | 98m | 0 | 63-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06RICMIT-MIT | 9 | 26m | 2/10-10/16 | 9-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL06SACLAZ-LAZ | 15 | 45m | 542/2-33/31478 | 40-3 | -13 | **FLOW_AT_LEVEL** | 1 |  |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 236m | 16366/1-95/1383948 | 83-1 | -13 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06SPIMED-MED | 8 | 16m | 0 | 8-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SPIMED-SPI | 87 | 19m | 0 | 87-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06STETRA-STE | 78 | 5m | 0 | 78-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06STETRA-TRA | 16 | 5m | 0 | 16-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-SCH | 10 | 0m | 1/17-17/2463 | 12-16 | 7 | **FLOW_ABOVE** | 11 | flow above but bound 11c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06TRIVOR-TRI | 8 | 175m | 0 | 8-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-VOR | 69 | 14m | 0 | 69-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-EVA | 36 | 74m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-URR | 61 | 68m | 0 | 61-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 235m | 5946/2-29/727026 | 21-4 | -13 | **FLOW_AT_LEVEL** | 5 |  |
| ITFWMATCH-26JUL06VIRKOV-KOV | 29 | 80m | 0 | 29-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VIRKOV-VIR | 56 | 113m | 0 | 56-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-DIL | 56 | 5m | 1/71-71/2 | 76-60 | 15 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06WAGYOU-WAG | 34 | 136m | 8/44-52/164 | 34-35 | 10 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06WAGYOU-WAG | 34 | 64m | 8/44-52/164 | 34-35 | 10 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06WAGYOU-WAG | 34 | 1m | 0 | 34-35 | — | **NO_FLOW** | 34 |  |
| ITFWMATCH-26JUL06WONIBR-WON | 32 | 234m | 25/72-92/101 | 87-57 | 40 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ARANIL-A | 73 | 145m | 2/75-75/114 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| WTACHALLENGERMATCH-26JUL06ARANIL-N | 25 | 158m | 1/26-26/9 | 25-26 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 74 | 68m | 1/76-76/25 | 74-76 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 24 | 68m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BLIAND-A | 35 | 68m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BLIAND-B | 64 | 68m | 1/65-65/22 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| WTACHALLENGERMATCH-26JUL06BOUKOT-B | 20 | 1m | 1/27-27/50 | 26-23 | 7 | **FLOW_ABOVE** | 20 | flow above but bound 20c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06BULSTR-B | 71 | 248m | 7/71-75/292 | 71-74 | 0 | **FLOW_AT_LEVEL** | 68 |  |
| WTACHALLENGERMATCH-26JUL06BULSTR-S | 27 | 184m | 4/28-30/87 | 27-30 | 1 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06GRAMAS-G | 32 | 158m | 1/33-33/100 | 32-33 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| WTACHALLENGERMATCH-26JUL06GRAMAS-M | 67 | 158m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 41 | 248m | 3/43-44/68 | 42-43 | 2 | **FLOW_ABOVE** | 41 | flow above but bound 41c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06HERNGU-N | 58 | 112m | 4/58-59/955 | 57-58 | 0 | **FLOW_AT_LEVEL** | 56 |  |
| WTACHALLENGERMATCH-26JUL06HESPAL-H | 30 | 159m | 0 | 30-31 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HESPAL-P | 69 | 159m | 1/70-70/24 | 69-70 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| WTACHALLENGERMATCH-26JUL06LEWMAR-L | 55 | 158m | 0 | 55-57 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06LEWMAR-M | 43 | 158m | 1/44-44/12 | 43-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| WTACHALLENGERMATCH-26JUL06MATPUT-M | 9 | 158m | 2/9-10/47 | 9-10 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MATPUT-P | 89 | 158m | 2/91-91/35 | 90-91 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| WTACHALLENGERMATCH-26JUL06MONPOP-M | 46 | 105m | 1/48-48/12 | 46-47 | 2 | **FLOW_ABOVE** | 45 | flow above but bound 45c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06MONPOP-P | 54 | 246m | 6/55-55/1743 | 54-55 | 1 | **FLOW_ABOVE** | 52 | flow above but bound 52c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06NOHBUR-B | 22 | 178m | 30/23-28/1716 | 26-23 | 1 | **FLOW_ABOVE** | 21 | flow above but bound 21c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06NOHBUR-N | 75 | 68m | 9/76-79/878 | 75-76 | 1 | **FLOW_ABOVE** | 73 | flow above but bound 73c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06OLIUCH-O | 58 | 1m | 0 | 61-60 | — | **NO_FLOW** | 58 |  |
| WTACHALLENGERMATCH-26JUL06ROMSEM-R | 42 | 128m | 0 | 43-44 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06ROMSEM-S | 56 | 159m | 1/57-57/8 | 56-57 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| WTACHALLENGERMATCH-26JUL06WALKAW-K | 43 | 68m | 1/44-44/11 | 43-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| WTACHALLENGERMATCH-26JUL06WALKAW-W | 55 | 68m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-S | 67 | 68m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-W | 31 | 68m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL06KRUKOS-KOS | 66 | 15m | 11/70-71/356 | 70-68 | 4 | **FLOW_ABOVE** | 66 | flow above but bound 66c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06WAGYOU | 63 | 35 | **98** | 97 | +1 |
| ITFMATCH-26JUL06BEASCO | 33 | 66 | **99** | 97 | +2 |
| ITFWMATCH-26JUL06POPSOL | 36 | 63 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH | 40 | 59 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06PRIORA | 56 | 43 | **99** | 97 | +2 |
| WTAMATCH-26JUL06KRUKOS | 31 | 68 | **99** | 97 | +2 |
| ITFWMATCH-26JUL06OKUPRI | 41 | 58 | **99** | 97 | +2 |
| WTACHALLENGERMATCH-26JUL06OLIUCH | 39 | 60 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06CAMDE | 39 | 61 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL06BOUKOT | 77 | 23 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06KULGON | 22 | 79 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06VLADIL | 41 | 60 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06JOSKUM | 67 | 35 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06TEISCH | 86 | 16 | **102** | 97 | +5 |
| ITFMATCH-26JUL06ELDHAU | 65 | 38 | **103** | 97 | +6 |
| ITFWMATCH-26JUL06BOIBOY | 77 | 31 | **108** | 97 | +11 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ITFWMATCH-26JUL06WONIBR | 65 | 57 | **122** | 97 | +25 |

## PATTERNS (sub-B) — 30
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TODSAG-SAG {"price": 25, "ceiling": 21, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SACLAZ-LAZ {"price": 12, "ceiling": 9, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06BRESAF-BRE {"price": 58, "ceiling": 47, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06BRESAF-BRE {"price": 63, "ceiling": 47, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SACLAZ-LAZ {"price": 16, "ceiling": 9, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TODSAG-SAG {"price": 29, "ceiling": 21, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TODSAG-SAG {"price": 30, "ceiling": 21, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VAJRAM-RAM {"price": 14, "ceiling": 13, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TODSAG-SAG {"price": 31, "ceiling": 21, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VAJRAM-RAM {"price": 15, "ceiling": 13, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VAJRAM-RAM {"price": 16, "ceiling": 13, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VAJRAM-RAM {"price": 17, "ceiling": 13, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SACLAZ-LAZ {"price": 17, "ceiling": 9, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SIMCIR-SIM {"price": 84, "ceiling": 73}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SACLAZ-LAZ {"price": 18, "ceiling": 9, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SACLAZ-LAZ {"price": 19, "ceiling": 9, "emitted_et": "2026-07-06 05:08:57 AM ET"}
- deep_neg_fv: KXITFWMATCH-26JUL06SIMCIR-CIR {"entry_minus_fv_burst": -30.0}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 303, "mode": "SET_BELOW_FLOW(prints 74c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 276, "mode": "SET_BELOW_FLOW(prints 40c above)"}
- half_arm_aging: KXITFMATCH-26JUL06BEASCO-SCO {"fill": 33, "age_min": 248, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06POPSOL-POP {"fill": 36, "age_min": 226, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06NIJRAH-RAH {"fill": 40, "age_min": 197, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06WAGYOU-YOU {"fill": 63, "age_min": 168, "mode": "SET_BELOW_FLOW(prints 10c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06BOIBOY-BOI {"fill": 77, "age_min": 112, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06KULGON-GON {"fill": 22, "age_min": 98, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06JOSKUM-JOS {"fill": 67, "age_min": 89, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06VLADIL-VLA {"fill": 41, "age_min": 88, "mode": "SET_BELOW_FLOW(prints 15c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06PRIORA-PRI {"fill": 56, "age_min": 68, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06CAMDE-DE {"fill": 39, "age_min": 58, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFMATCH-26JUL06CASBAY-CAS {"fill": 45, "age_min": 47, "mode": "NO_BID(sib rested earlier, none now)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
