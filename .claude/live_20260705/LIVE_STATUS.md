# LIVE VALIDATION — rolling status

- cycle 105 @ **2026-07-06 04:38:25 AM ET** | build `21e2b14` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 74407 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 4 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 23:50:46 | **walk_cap_breach** | KXITFWMATCH-26JUL06SIMCIR-SIM | buy 83c > ceiling 73c (conception 69 + cap) ref=join_bid |
| 01:01:56 | **combined_over_goal** | KXITFWMATCH-26JUL06TODSAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 01:12:30 | **combined_over_goal** | KXITFWMATCH-26JUL06VAJRAM | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |
| 03:38:20 | **combined_over_goal** | KXITFWMATCH-26JUL06DZJMCK | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 52 graded (session)
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
| 01:51 | ATPCHALLENGERMATCH-26JUL06NIJRAH-R | ATP_CHALL | underdog | 40 | 37 | +3 (place_cell) | — | pre | single |  | MIXED |
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
| 04:36 | ITFWMATCH-26JUL06LUKNOE-LUK | ITF_W | leader | 69 | 72 | -3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 208 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 15, 'FLOW_ABOVE': 77, 'NO_FLOW': 116} | repriceable now: true 31 / false 177 | **cumulative bid_grade lines: 1520 (repriceable true 164 / false 1356)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06BASHOE-B | 47 | 68m | 1/50-50/20 | 48-50 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ATPCHALLENGERMATCH-26JUL06BASHOE-H | 51 | 68m | 1/52-52/46 | 51-52 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ATPCHALLENGERMATCH-26JUL06CAMDE-CA | 58 | 195m | 6/61-63/431 | 60-61 | 3 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06CAMDE-CA | 58 | 27m | 1/63-63/8 | 60-61 | 5 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06CHEYEV-C | 61 | 98m | 3/62-62/57 | 61-62 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→62 |
| ATPCHALLENGERMATCH-26JUL06CHEYEV-Y | 37 | 98m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DALCAR-C | 3 | 188m | 19/4-4/1207 | 3-4 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06DALCAR-D | 96 | 188m | 8/97-97/359 | 96-97 | 1 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06DELWAL-D | 27 | 158m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DELWAL-W | 71 | 158m | 2/71-73/14 | 71-73 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-C | 24 | 37m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-D | 76 | 1m | 0 | 76-78 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-E | 95 | 128m | 0 | 95-96 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-S | 4 | 128m | 0 | 4-5 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-G | 71 | 188m | 1/74-74/5 | 71-74 | 3 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | 26 | 168m | 2/27-27/523 | 26-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-H | 35 | 128m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-P | 61 | 128m | 2/67-67/29 | 63-67 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-D | 20 | 68m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-I | 78 | 68m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 5 | 23m | 169/6-21/17591 | 19-6 | 1 | **FLOW_ABOVE** | 5 | flow above but bound 5c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06KUZSTR-K | 73 | 98m | 1/74-74/32 | 73-74 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ATPCHALLENGERMATCH-26JUL06KUZSTR-S | 26 | 98m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARBER-B | 58 | 188m | 4/59-60/138 | 59-59 | 1 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06MARBER-M | 40 | 188m | 5/41-42/196 | 40-42 | 1 | **FLOW_ABOVE** | 39 | flow above but bound 39c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06MARHAM-H | 5 | 128m | 0 | 5-6 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARHAM-M | 94 | 114m | 1/95-95/0 | 94-95 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→95 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH-N | 57 | 163m | 11/59-60/483 | 59-59 | 2 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06OPIPET-O | 26 | 98m | 2/27-27/352 | 27-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ATPCHALLENGERMATCH-26JUL06OPIPET-P | 71 | 37m | 0 | 72-72 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PAPJAN-P | 53 | 158m | 2/55-55/54 | 54-55 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-M | 53 | 57m | 1/55-55/100 | 53-55 | 2 | **FLOW_ABOVE** | 52 | flow above but bound 52c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-P | 45 | 57m | 11/47-47/1066 | 45-46 | 2 | **FLOW_ABOVE** | 44 | flow above but bound 44c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06POLHAI-H | 68 | 38m | 0 | 68-71 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POLHAI-P | 31 | 38m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-F | 58 | 188m | 3/60-60/186 | 58-60 | 2 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06POTFEL-P | 40 | 188m | 1/42-42/15 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 253m | 24/42-45/2619 | 44-43 | 2 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 37m | 3/45-45/140 | 44-43 | 5 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 61 | 128m | 1/69-69/5 | 65-69 | 8 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 32 | 126m | 0 | 32-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-B | 36 | 158m | 1/37-37/7 | 36-37 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-S | 61 | 158m | 1/64-64/5 | 61-64 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-M | 10 | 187m | 1/10-10/0 | 10-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-S | 88 | 188m | 1/90-90/0 | 88-90 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 218m | 1/35-35/349 | 33-34 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ATPCHALLENGERMATCH-26JUL06STALEC-S | 64 | 183m | 6/66-67/166 | 64-66 | 2 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06VALZHU-V | 71 | 68m | 1/73-73/17 | 71-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ATPCHALLENGERMATCH-26JUL06VALZHU-Z | 27 | 68m | 0 | 27-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 22 | 174m | 268/25-48/19255 | 33-25 | 3 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 22 | 6m | 76/28-48/6597 | 33-25 | 6 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06WALNEU-N | 28 | 36m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06WALNEU-W | 70 | 37m | 0 | 70-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-D | 42 | 128m | 1/44-44/11 | 42-44 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-Z | 56 | 128m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL06DECOB-COB | 23 | 37m | 18/23-24/12474 | 23-24 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL06ALEREG-ALE | 51 | 34m | 0 | 51-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALEREG-REG | 40 | 35m | 0 | 40-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-ALI | 91 | 16m | 0 | 91-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-MIS | 6 | 126m | 0 | 6-10 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 212m | 153/66-89/16819 | 87-66 | 2 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BEASCO-BEA | 60 | 1m | 0 | 87-66 | — | **NO_FLOW** | 64 |  |
| ITFMATCH-26JUL06BONFAU-FAU | 25 | 126m | 0 | 25-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-DUG | 63 | 114m | 0 | 63-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-HOF | 20 | 113m | 0 | 20-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUHCAR-CAR | 12 | 36m | 0 | 12-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUHCAR-DUH | 83 | 39m | 0 | 83-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-ELD | 64 | 144m | 1/69-69/2 | 64-69 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 31 | 39m | 0 | 31-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GANVER-GAN | 4 | 27m | 0 | 46-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GANVER-VER | 47 | 11m | 0 | 47-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GARCIO-CIO | 39 | 39m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GARCIO-GAR | 56 | 46m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 186m | 213/1-19/18095 | 18-1 | -15 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06HERNAG-NAG | 27 | 38m | 0 | 27-51 | — | **NO_FLOW** | 27 |  |
| ITFMATCH-26JUL06HOSGAT-GAT | 38 | 39m | 0 | 38-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HOSGAT-HOS | 56 | 11m | 0 | 56-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06JAIHEN-JAI | 45 | 36m | 0 | 45-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-LIL | 28 | 19m | 26/28-44/1139 | 38-29 | 0 | **FLOW_AT_LEVEL** | 31 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 34 | 1m | 0 | 34-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-THE | 65 | 183m | 1/68-68/2 | 65-66 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL06MEHCOU-COU | 52 | 33m | 0 | 52-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MEHCOU-MEH | 26 | 50m | 0 | 26-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-BEC | 87 | 38m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-ROJ | 10 | 37m | 0 | 10-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALBRE-BRE | 6 | 187m | 3/11-11/29 | 6-8 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALBRE-SAL | 89 | 183m | 1/94-94/21 | 89-93 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06STAGUI-GUI | 27 | 8m | 0 | 27-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STAGUI-STA | 26 | 7m | 0 | 26-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STEAUN-AUN | 14 | 37m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STEAUN-STE | 82 | 37m | 0 | 82-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TEUHAS-HAS | 63 | 10m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TEUHAS-TEU | 33 | 36m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TIMJEF-JEF | 71 | 28m | 0 | 71-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TIMJEF-TIM | 20 | 8m | 0 | 20-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRA | 24 | 95m | 0 | 24-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRU | 67 | 3m | 0 | 67-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-AND | 24 | 24m | 0 | 24-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-TSI | 59 | 24m | 0 | 59-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VULCOU-VUL | 81 | 21m | 11/98-99/1550 | 99-85 | 17 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ADKFER-ADK | 53 | 113m | 0 | 53-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ADKFER-FER | 18 | 113m | 0 | 18-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 82m | 0 | 28-31 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 28m | 0 | 28-31 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06BOSTOP-BOS | 67 | 66m | 2/68-68/4 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFWMATCH-26JUL06BOSTOP-TOP | 33 | 158m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 209m | 1507/21-62/196373 | 58-22 | -13 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06BUYALV-ALV | 22 | 88m | 0 | 22-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BUYALV-BUY | 54 | 49m | 0 | 54-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DIANIK-DIA | 44 | 78m | 0 | 52-65 | — | **NO_FLOW** | 45 |  |
| ITFWMATCH-26JUL06DIANIK-DIA | 45 | 23m | 0 | 52-65 | — | **NO_FLOW** | 45 |  |
| ITFWMATCH-26JUL06EWAMAN-EWA | 66 | 50m | 0 | 66-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EWAMAN-MAN | 20 | 80m | 0 | 20-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-GAL | 76 | 138m | 1/80-80/2 | 76-80 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL06GALTSE-TSE | 21 | 149m | 0 | 21-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-GAN | 83 | 126m | 1/89-89/2 | 83-89 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-PUI | 11 | 119m | 0 | 11-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 25 | 3m | 0 | 99-58 | — | **NO_FLOW** | 36 |  |
| ITFWMATCH-26JUL06ILIEBE-EBE | 52 | 157m | 0 | 52-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ILIEBE-ILI | 38 | 88m | 0 | 38-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06IVAKUH-IVA | 62 | 194m | 15/63-64/931 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL06IVAKUH-KUH | 37 | 215m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06JOSKUM-KUM | 30 | 16m | 338/42-75/26217 | 75-35 | 12 | **FLOW_ABOVE** | 30 | flow above but bound 30c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARBAS-KAR | 71 | 242m | 6/75-76/41 | 75-72 | 4 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARBAS-KAR | 67 | 145m | 1/76-76/1 | 75-72 | 9 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARVIS-KAR | 77 | 33m | 0 | 77-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARVIS-VIS | 14 | 126m | 0 | 14-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOTCHI-KOT | 34 | 8m | 0 | 34-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOVDAE-DAE | 18 | 68m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOVDAE-KOV | 75 | 67m | 0 | 75-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 67m | 1/79-79/5 | 75-79 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 67m | 1/79-79/5 | 75-79 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 255m | 3895/23-99/459986 | 99-24 | -14 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06LUKNOE-NOE | 27 | 14m | 8/34-41/139 | 27-31 | 7 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06MARGLU-GLU | 66 | 11m | 0 | 66-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARGLU-MAR | 28 | 36m | 0 | 28-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-ENC | 51 | 85m | 0 | 51-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-MCA | 42 | 74m | 0 | 42-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MILHER-HER | 14 | 84m | 0 | 14-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MILHER-MIL | 65 | 49m | 0 | 65-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKASAK-OKA | 26 | 49m | 0 | 26-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-OKU | 54 | 83m | 0 | 54-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-PRI | 39 | 84m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PACLOV-LOV | 45 | 57m | 7/46-47/654 | 45-46 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ITFWMATCH-26JUL06PACLOV-PAC | 56 | 156m | 1/56-56/50 | 56-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 158m | 1942/1-13/312225 | 14-1 | -7 | **FLOW_AT_LEVEL** | 12 |  |
| ITFWMATCH-26JUL06PEEPAH-PAH | 58 | 110m | 4/64-65/93 | 58-64 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06PEEPAH-PEE | 37 | 135m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PIERAD-PIE | 58 | 87m | 0 | 58-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PIERAD-RAD | 29 | 14m | 0 | 29-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PODLUK-LUK | 68 | 84m | 0 | 68-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PODLUK-POD | 26 | 87m | 0 | 26-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06POPSOL-SOL | 61 | 196m | 12/66-76/50 | 65-63 | 5 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06POPSOL-SOL | 61 | 21m | 3/66-76/2 | 67-63 | 5 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06POZMLA-MLA | 5 | 49m | 0 | 5-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-NIJ | 30 | 67m | 0 | 30-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-PRI | 63 | 67m | 0 | 63-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06RICMIT-MIT | 7 | 217m | 18/8-90/167 | 7-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFWMATCH-26JUL06SACLAZ-LAZ | 15 | 14m | 178/14-33/8673 | 40-16 | -1 | **FLOW_AT_LEVEL** | 19 |  |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 205m | 16366/1-95/1383948 | 83-1 | -13 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06SPIMED-MED | 5 | 187m | 2/14-14/24 | 5-14 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06SPIMED-SPI | 86 | 138m | 3/95-95/25 | 86-95 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-SCH | 6 | 155m | 0 | 6-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-TEI | 79 | 7m | 0 | 79-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-TRI | 8 | 145m | 0 | 8-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-VOR | 66 | 7m | 0 | 66-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-EVA | 36 | 43m | 0 | 36-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-URR | 61 | 38m | 0 | 61-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 205m | 4291/3-29/548753 | 20-4 | -12 | **FLOW_AT_LEVEL** | 15 |  |
| ITFWMATCH-26JUL06VIRKOV-KOV | 29 | 49m | 0 | 29-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VIRKOV-VIR | 56 | 82m | 0 | 56-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-DIL | 56 | 57m | 10/60-65/341 | 60-60 | 4 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06WAGYOU-WAG | 34 | 106m | 0 | 34-53 | — | **NO_FLOW** | 34 |  |
| ITFWMATCH-26JUL06WAGYOU-WAG | 34 | 33m | 0 | 34-53 | — | **NO_FLOW** | 34 |  |
| ITFWMATCH-26JUL06WONIBR-WON | 32 | 203m | 19/72-92/75 | 87-57 | 40 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ARANIL-A | 73 | 115m | 1/75-75/56 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| WTACHALLENGERMATCH-26JUL06ARANIL-N | 25 | 128m | 1/26-26/9 | 25-26 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 74 | 37m | 0 | 74-76 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 24 | 37m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BLIAND-A | 35 | 37m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BLIAND-B | 64 | 37m | 0 | 64-65 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BOUKOT-B | 22 | 218m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| WTACHALLENGERMATCH-26JUL06BOUKOT-K | 77 | 210m | 4/78-79/1520 | 77-78 | 1 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06BULSTR-B | 71 | 218m | 2/71-74/23 | 71-74 | 0 | **FLOW_AT_LEVEL** | 68 |  |
| WTACHALLENGERMATCH-26JUL06BULSTR-S | 27 | 153m | 2/28-29/56 | 27-29 | 1 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06GRAMAS-G | 32 | 128m | 1/33-33/100 | 32-33 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| WTACHALLENGERMATCH-26JUL06GRAMAS-M | 67 | 128m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 41 | 218m | 1/43-43/28 | 41-43 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| WTACHALLENGERMATCH-26JUL06HERNGU-N | 58 | 82m | 3/59-59/950 | 58-59 | 1 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06HESPAL-H | 30 | 128m | 0 | 30-31 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HESPAL-P | 69 | 128m | 1/70-70/24 | 69-70 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| WTACHALLENGERMATCH-26JUL06LEWMAR-L | 55 | 128m | 0 | 55-58 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06LEWMAR-M | 43 | 128m | 1/44-44/12 | 43-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| WTACHALLENGERMATCH-26JUL06MATPUT-M | 9 | 128m | 1/9-9/0 | 9-10 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MATPUT-P | 89 | 128m | 2/91-91/35 | 90-91 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| WTACHALLENGERMATCH-26JUL06MONPOP-M | 46 | 74m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MONPOP-P | 54 | 215m | 3/55-55/1441 | 54-55 | 1 | **FLOW_ABOVE** | 52 | flow above but bound 52c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06NOHBUR-B | 22 | 147m | 7/24-24/667 | 23-23 | 2 | **FLOW_ABOVE** | 21 | flow above but bound 21c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06NOHBUR-N | 75 | 37m | 1/76-76/165 | 75-76 | 1 | **FLOW_ABOVE** | 73 | flow above but bound 73c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06OLIUCH-O | 59 | 37m | 7/61-61/894 | 60-60 | 2 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06OLIUCH-U | 39 | 98m | 7/40-40/296 | 40-40 | 1 | **FLOW_ABOVE** | 37 | flow above but bound 37c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ROMSEM-R | 42 | 98m | 0 | 43-44 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06ROMSEM-S | 56 | 128m | 1/57-57/8 | 56-57 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| WTACHALLENGERMATCH-26JUL06WALKAW-K | 43 | 37m | 1/44-44/11 | 43-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| WTACHALLENGERMATCH-26JUL06WALKAW-W | 55 | 37m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-S | 67 | 37m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-W | 31 | 37m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL06KRUKOS-KRU | 31 | 158m | 61/31-32/5684 | 32-32 | 0 | **FLOW_AT_LEVEL** | 99 |  |

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
| ITFWMATCH-26JUL06LUKNOE | 69 | 31 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06KULGON | 22 | 79 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06VLADIL | 41 | 60 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06JOSKUM | 67 | 35 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06BOIBOY | 77 | 31 | **108** | 97 | +11 |
| ITFWMATCH-26JUL06WAGYOU | 63 | 53 | **116** | 97 | +19 |
| ITFWMATCH-26JUL06DIANIK | 52 | 65 | **117** | 97 | +20 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ITFMATCH-26JUL06HERNAG | 70 | 50 | **120** | 97 | +23 |
| ITFWMATCH-26JUL06WONIBR | 65 | 57 | **122** | 97 | +25 |

## PATTERNS (sub-B) — 17
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SIMCIR-SIM {"price": 84, "ceiling": 73}
- deep_neg_fv: KXITFWMATCH-26JUL06SIMCIR-CIR {"entry_minus_fv_burst": -30.0}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 273, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 245, "mode": "SET_BELOW_FLOW(prints 40c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06KARBAS-BAS {"fill": 26, "age_min": 244, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFMATCH-26JUL06BEASCO-SCO {"fill": 33, "age_min": 218, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06POPSOL-POP {"fill": 36, "age_min": 196, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VILBOC-VIL {"fill": 75, "age_min": 174, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06NIJRAH-RAH {"fill": 40, "age_min": 167, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06WAGYOU-YOU {"fill": 63, "age_min": 137, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06BOIBOY-BOI {"fill": 77, "age_min": 82, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06KULGON-GON {"fill": 22, "age_min": 67, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFMATCH-26JUL06HERNAG-HER {"fill": 70, "age_min": 64, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06JOSKUM-JOS {"fill": 67, "age_min": 59, "mode": "SET_BELOW_FLOW(prints 12c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06VLADIL-VLA {"fill": 41, "age_min": 57, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06PRIORA-PRI {"fill": 56, "age_min": 38, "mode": "SET_BELOW_FLOW(prints 2c above)", "emitted_et": "2026-07-06 04:38:25 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL06DIANIK-NIK {"fill": 52, "age_min": 31, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-06 04:38:25 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
