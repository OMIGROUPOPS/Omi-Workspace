# LIVE VALIDATION — rolling status

- cycle 23 @ **2026-07-05 02:46:28 PM ET** | build `9caacb7` | session boot 07-05 10:39 ET | log `live_v3_20260705.jsonl` | 36589 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 8 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 10:48:45 | **grace_breach** | KXITFMATCH-26JUL05SALCON-CON | fill 13c 5.2min past latch (grace 300s) |
| 11:10:44 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05TENBER | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 11:15:35 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL05KOBLEW | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 11:28:58 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05PEROPI | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 12:05:34 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05HUANOC | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 12:07:26 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05KAMVAN | pair combined 100c > goal 97c [organic: DEFECT-CLASS] |
| 13:19:41 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05MARHAI | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 14:35:43 | **combined_over_goal** | KXATPMATCH-26JUL05SINMOC | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 81 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10:39 | ITFWMATCH-26JUL05TRAABB-ABB | ITF_W | ? | 64 | 64 | +0 (window_cell) | -31.5 | pre | pair | 97 | EARNED |
| 10:39 | ATPCHALLENGERMATCH-26JUL05RAMNEU-R | ATP_CHALL | ? | 36 | 2 | +34 (window_cell) | — | pre | single |  | MIXED |
| 10:39 | ATPCHALLENGERMATCH-26JUL05WEHIFI-I | ATP_CHALL | ? | 11 | 8 | +3 (adopted_est) | 5.5 | pre | single |  | GIFT_CLASS |
| 10:39 | WTACHALLENGERMATCH-26JUL05DITLEW-D | WTA_CHALL | ? | 31 | 28 | +3 (adopted_est) | 25.5 | pre | single |  | GIFT_CLASS |
| 10:39 | ATPCHALLENGERMATCH-26JUL05KUZMAT-M | ATP_CHALL | ? | 5 | 2 | +3 (adopted_est) | -2.5 | pre | single |  | MIXED |
| 10:40 | ITFWMATCH-26JUL05AITDAE-AIT | ITF_W | underdog | 8 | 4 | +4 (place_cell) | -9.0 | pre | pair | 89 | EARNED |
| 10:41 | ATPCHALLENGERMATCH-26JUL05VALREJ-V | ATP_CHALL | leader | 62 | 71 | -9 (place_cell) | 11.5 | pre | single |  | GIFT_CLASS |
| 10:41 | ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | ATP_CHALL | underdog | 23 | 19 | +4 (place_cell) | 8.0 | pre | single |  | GIFT_CLASS |
| 10:41 | ITFMATCH-26JUL05GELBRE-GEL | ITF_M | ? | 44 | 40 | +4 (window_cell) | 18.0 | pre | pair | 92 | GIFT_CLASS |
| 10:42 | WTAMATCH-26JUL05BENGAU-GAU | WTA_MAIN | ? | 50 | 50 | +0 (adopted_est) | 0.5 | pre | single |  | MIXED |
| 10:48 | ITFMATCH-26JUL05SALCON-CON | ITF_M | ? | 13 | 29 | -16 (window_cell) | -10.0 | 5.2 | single |  | EARNED |
| 10:53 | ITFMATCH-26JUL05GELBRE-BRE | ITF_M | ? | 48 | 56 | -8 (window_cell) | -25.0 | pre | pair | 92 | EARNED |
| 10:53 | ATPCHALLENGERMATCH-26JUL05PEROPI-O | ATP_CHALL | ? | 25 | 22 | +3 (window_cell) | -8.0 | pre | pair | 98 | EARNED |
| 10:55 | ATPCHALLENGERMATCH-26JUL05INGFEL-F | ATP_CHALL | ? | 72 | 72 | +0 (adopted_est) | — | pre | single |  | PENDING |
| 11:02 | ITFWMATCH-26JUL05TRAABB-TRA | ITF_W | ? | 33 | 29 | +4 (window_cell) | 29.0 | pre | pair | 97 | GIFT_CLASS |
| 11:07 | ATPCHALLENGERMATCH-26JUL05HUEMAR-M | ATP_CHALL | ? | 31 | 28 | +3 (window_cell) | — | pre | single |  | MIXED |
| 11:07 | ATPCHALLENGERMATCH-26JUL05TENBER-T | ATP_CHALL | ? | 42 | 39 | +3 (window_cell) | -12.5 | pre | pair | 99 | EARNED |
| 11:08 | WTACHALLENGERMATCH-26JUL05KOBLEW-L | WTA_CHALL | ? | 10 | 8 | +2 (window_cell) | — | pre | pair | 99 | MIXED |
| 11:10 | ATPCHALLENGERMATCH-26JUL05TENBER-B | ATP_CHALL | ? | 57 | 60 | -3 (window_cell) | 16.5 | pre | pair | 99 | GIFT_CLASS |
| 11:12 | ITFWMATCH-26JUL05AITDAE-DAE | ITF_W | ? | 81 | 94 | -13 (window_cell) | 2.5 | pre | pair | 89 | MIXED |
| 11:12 | ATPCHALLENGERMATCH-26JUL05SUNBAR-B | ATP_CHALL | ? | 57 | 59 | -2 (window_cell) | -31.0 | pre | pair | 97 | EARNED |
| 11:12 | ATPCHALLENGERMATCH-26JUL05PRICOU-C | ATP_CHALL | ? | 50 | 53 | -3 (window_cell) | — | pre | pair | 97 | MIXED |
| 11:15 | ATPCHALLENGERMATCH-26JUL05SUNBAR-S | ATP_CHALL | ? | 40 | 41 | -1 (window_cell) | 30.0 | pre | pair | 97 | EARNED |
| 11:15 | ATPCHALLENGERMATCH-26JUL05RYBTUN-T | ATP_CHALL | ? | 73 | 75 | -2 (window_cell) | 61.0 | pre | single |  | GIFT_CLASS |
| 11:15 | WTACHALLENGERMATCH-26JUL05KOBLEW-K | WTA_CHALL | ? | 89 | 91 | -2 (window_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 11:16 | ATPCHALLENGERMATCH-26JUL05HUANOC-H | ATP_CHALL | ? | 29 | 29 | +0 (window_cell) | 12.0 | pre | pair | 98 | EARNED |
| 11:16 | ATPCHALLENGERMATCH-26JUL05PRICOU-P | ATP_CHALL | ? | 47 | 54 | -7 (window_cell) | — | pre | pair | 97 | EARNED |
| 11:21 | ITFWMATCH-26JUL05TUBSOB-SOB | ITF_W | ? | 24 | 30 | -6 (window_cell) | 9.0 | pre | single |  | EARNED |
| 11:28 | ATPCHALLENGERMATCH-26JUL05PEROPI-P | ATP_CHALL | ? | 73 | 75 | -2 (window_cell) | 9.0 | pre | pair | 98 | GIFT_CLASS |
| 11:32 | ATPCHALLENGERMATCH-26JUL05PDACAS-C | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | -12.5 | pre | pair | 97 | EARNED |
| 11:33 | ITFMATCH-26JUL05BONBRA-BRA | ITF_M | ? | 13 | 10 | +3 (window_cell) | — | pre | single |  | MIXED |
| 11:37 | ATPCHALLENGERMATCH-26JUL05HIGZHU-H | ATP_CHALL | ? | 38 | 38 | +0 (window_cell) | -8.5 | pre | pair | 96 | EARNED |
| 11:43 | ATPCHALLENGERMATCH-26JUL05HIGZHU-Z | ATP_CHALL | ? | 58 | 61 | -3 (window_cell) | 9.5 | pre | pair | 96 | GIFT_CLASS |
| 11:45 | ATPCHALLENGERMATCH-26JUL05POTANG-P | ATP_CHALL | ? | 50 | 50 | +0 (fill_est) | -15.0 | pre | single |  | EARNED |
| 11:45 | ATPCHALLENGERMATCH-26JUL05KAMVAN-K | ATP_CHALL | ? | 13 | 10 | +3 (adopted_est) | 2.0 | pre | pair | 100 | MIXED |
| 11:47 | ITFMATCH-26JUL05SABMIS-SAB | ITF_M | underdog | 81 | 14 | +67 (place_cell) | 15.0 | pre | single |  | GIFT_CLASS |
| 11:48 | ATPCHALLENGERMATCH-26JUL05BINPOL-B | ATP_CHALL | ? | 59 | 61 | -2 (window_cell) | -31.0 | pre | pair | 97 | EARNED |
| 11:54 | ATPCHALLENGERMATCH-26JUL05GOIAND-G | ATP_CHALL | underdog | 31 | 26 | +5 (place_cell) | 25.0 | pre | single |  | GIFT_CLASS |
| 11:56 | ATPCHALLENGERMATCH-26JUL05GANZIN-G | ATP_CHALL | underdog | 29 | 25 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 12:01 | ITFMATCH-26JUL05XUXCHE-CHE | ITF_M | underdog | 2 | 1 | +1 (place_cell) | — | pre | single |  | MIXED |
| 12:01 | ITFMATCH-26JUL05FARBRO-FAR | ITF_M | ? | 64 | 64 | +0 (place_cell) | 17.0 | pre | pair | 96 | GIFT_CLASS |
| 12:03 | ITFMATCH-26JUL05THUGRE-THU | ITF_M | leader | 98 | 98 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 12:05 | ATPCHALLENGERMATCH-26JUL05HUANOC-N | ATP_CHALL | ? | 69 | 71 | -2 (window_cell) | — | pre | pair | 98 | GIFT_CLASS |
| 12:07 | ATPCHALLENGERMATCH-26JUL05KAMVAN-V | ATP_CHALL | ? | 87 | 87 | +0 (adopted_est) | — | pre | pair | 100 | PENDING |
| 12:08 | ATPMATCH-26JUL05SINMOC-SIN | ATP_MAIN | ? | 96 | 96 | +0 (adopted_est) | -0.5 | pre | pair | 99 | MIXED |
| 12:12 | ITFMATCH-26JUL05FARBRO-BRO | ITF_M | ? | 32 | 30 | +2 (window_cell) | -18.0 | pre | pair | 96 | EARNED |
| 12:13 | ITFWMATCH-26JUL05KULVAN-KUL | ITF_W | ? | 55 | 60 | -5 (window_cell) | -14.0 | pre | pair | 94 | EARNED |
| 12:13 | ATPCHALLENGERMATCH-26JUL05PDACAS-P | ATP_CHALL | leader | 58 | 61 | -3 (place_cell) | 11.5 | pre | pair | 97 | GIFT_CLASS |
| 12:16 | ATPCHALLENGERMATCH-26JUL05IVAGAN-G | ATP_CHALL | ? | 22 | 23 | -1 (window_cell) | — | pre | single |  | EARNED |
| 12:17 | ATPCHALLENGERMATCH-26JUL05MARJUN-J | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 12:17 | ATPCHALLENGERMATCH-26JUL05BINPOL-P | ATP_CHALL | ? | 38 | 38 | +0 (window_cell) | 20.0 | pre | pair | 97 | EARNED |
| 12:21 | ATPCHALLENGERMATCH-26JUL05MARHAI-H | ATP_CHALL | ? | 96 | 94 | +2 (window_cell) | -1.5 | pre | pair | 99 | GIFT_CLASS |
| 12:21 | ATPCHALLENGERMATCH-26JUL05MORMAR-M | ATP_CHALL | leader | 59 | 59 | +0 (place_cell) | -18.5 | pre | pair | 97 | EARNED |
| 12:24 | ITFWMATCH-26JUL05KULVAN-VAN | ITF_W | ? | 39 | 43 | -4 (window_cell) | 13.0 | pre | pair | 94 | EARNED |
| 12:38 | ATPCHALLENGERMATCH-26JUL05SANROD-R | ATP_CHALL | leader | 82 | 82 | +0 (place_cell) | — | pre | single |  | MIXED |
| 12:50 | ATPCHALLENGERMATCH-26JUL05POPCAS-P | ATP_CHALL | leader | 93 | 93 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 12:50 | ATPCHALLENGERMATCH-26JUL05ELLJOH-J | ATP_CHALL | ? | 33 | 30 | +3 (place_cell) | -24.5 | pre | pair | 97 | EARNED |
| 13:01 | ITFMATCH-26JUL05SLOKHR-KHR | ITF_M | underdog | 39 | 35 | +4 (place_cell) | 15.0 | pre | single |  | GIFT_CLASS |
| 13:01 | ITFMATCH-26JUL05MCKBER-BER | ITF_M | leader | 96 | 96 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 13:03 | ATPCHALLENGERMATCH-26JUL05ELLJOH-E | ATP_CHALL | leader | 64 | 65 | -1 (place_cell) | 28.5 | pre | pair | 97 | GIFT_CLASS |
| 13:06 | ITFMATCH-26JUL05CRIMAR-CRI | ITF_M | leader | 93 | 93 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 13:12 | ITFMATCH-26JUL05CRIMAR-MAR | ITF_M | underdog | 4 | 1 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 13:12 | ATPCHALLENGERMATCH-26JUL05GANZIN-Z | ATP_CHALL | ? | 68 | 70 | -2 (place_cell) | — | pre | pair | 97 | MIXED |
| 13:19 | ATPCHALLENGERMATCH-26JUL05MARHAI-M | ATP_CHALL | ? | 3 | 5 | -2 (window_cell) | — | pre | pair | 99 | EARNED |
| 13:28 | WTACHALLENGERMATCH-26JUL05YAMOVC-O | WTA_CHALL | underdog | 28 | 25 | +3 (place_cell) | 4.0 | pre | pair | 97 | GIFT_CLASS |
| 13:28 | ATPCHALLENGERMATCH-26JUL05NUNCLA-C | ATP_CHALL | leader | 57 | 57 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 13:29 | ATPCHALLENGERMATCH-26JUL05MONHUR-H | ATP_CHALL | underdog | 4 | 2 | +2 (place_cell) | — | pre | single |  | MIXED |
| 13:31 | WTACHALLENGERMATCH-26JUL05YAMOVC-Y | WTA_CHALL | leader | 69 | 70 | -1 (place_cell) | -3.0 | pre | pair | 97 | EARNED |
| 13:45 | ATPCHALLENGERMATCH-26JUL05POPCAS-C | ATP_CHALL | underdog | 4 | 4 | +0 (place_cell) | — | pre | pair | 97 | EARNED |
| 13:53 | WTACHALLENGERMATCH-26JUL05SMIJAR-S | WTA_CHALL | leader | 81 | 81 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 14:00 | ATPCHALLENGERMATCH-26JUL05KOZMAY-K | ATP_CHALL | underdog | 46 | 43 | +3 (place_cell) | — | pre | single |  | MIXED |
| 14:00 | ATPCHALLENGERMATCH-26JUL05MORMAR-M | ATP_CHALL | underdog | 38 | 1 | +37 (place_cell) | 10.5 | pre | pair | 97 | EARNED |
| 14:16 | ATPCHALLENGERMATCH-26JUL05NUNCLA-N | ATP_CHALL | underdog | 40 | 37 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 14:22 | ATPCHALLENGERMATCH-26JUL05MARJUN-M | ATP_CHALL | leader | 58 | 59 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 14:28 | ATPCHALLENGERMATCH-26JUL05IMAMIL-M | ATP_CHALL | leader | 58 | 58 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 14:32 | ITFMATCH-26JUL05MILRAM-RAM | ITF_M | leader | 90 | 90 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 14:33 | ITFMATCH-26JUL05IONDAO-DAO | ITF_M | underdog | 10 | 6 | +4 (place_cell) | — | pre | single |  | MIXED |
| 14:35 | ATPMATCH-26JUL05HURSTR-HUR | ATP_MAIN | ? | 71 | 71 | +0 (adopted_est) | — | pre | single |  | PENDING |
| 14:35 | ATPMATCH-26JUL05SINMOC-MOC | ATP_MAIN | ? | 3 | 1 | +2 (adopted_est) | — | pre | pair | 99 | PENDING |
| 14:37 | ATPCHALLENGERMATCH-26JUL05URRMEL-U | ATP_CHALL | underdog | 4 | 2 | +2 (place_cell) | — | pre | single |  | MIXED |
| 14:38 | ATPCHALLENGERMATCH-26JUL05IMAMIL-I | ATP_CHALL | underdog | 39 | 38 | +1 (place_cell) | — | pre | pair | 97 | EARNED |

## RESTING BIDS — 36 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 17, 'NO_FLOW': 9, 'FLOW_AT_LEVEL': 10} | repriceable now: true 6 / false 30 | **cumulative bid_grade lines: 785 (repriceable true 76 / false 709)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BANMAR-B | 65 | 246m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BANMAR-M | 33 | 246m | 7/33-37/340 | 33-37 | 0 | **FLOW_AT_LEVEL** | 33 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 91 | 229m | 39/97-99/5892 | 99-99 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05FARMAT-F | 38 | 106m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05FARMAT-M | 59 | 106m | 1/61-61/31 | 59-60 | 2 | **FLOW_ABOVE** | 61 | REPRICEABLE→61 |
| ATPCHALLENGERMATCH-26JUL05HUEZEB-H | 71 | 48m | 0 | 72-74 | — | **NO_FLOW** | 74 |  |
| ATPCHALLENGERMATCH-26JUL05HUEZEB-Z | 28 | 76m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IMAMIL-M | 54 | 7m | 12/74-79/713 | 76-55 | 20 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05KOZMAY-M | 51 | 46m | 0 | 53-55 | — | **NO_FLOW** | 51 |  |
| ATPCHALLENGERMATCH-26JUL05MORMAR-M | 49 | 44m | 195/47-81/8748 | 71-64 | -2 | **FLOW_AT_LEVEL** | 59 |  |
| ATPCHALLENGERMATCH-26JUL05NUNCLA-C | 57 | 20m | 120/53-68/14941 | 59-53 | -4 | **FLOW_AT_LEVEL** | 57 |  |
| ATPCHALLENGERMATCH-26JUL05PAPMBI-M | 65 | 146m | 3/67-68/74 | 66-68 | 2 | **FLOW_ABOVE** | 68 | REPRICEABLE→67 |
| ATPCHALLENGERMATCH-26JUL05PAPMBI-P | 33 | 145m | 2/34-35/18 | 33-35 | 1 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PRICOU-P | 47 | 195m | 96/1-59/22582 | 1-1 | -46 | **FLOW_AT_LEVEL** | 47 |  |
| ATPCHALLENGERMATCH-26JUL05RAMNEU-N | 61 | 247m | 17/98-99/2359 | 99-98 | 37 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SANROD-S | 15 | 123m | 111/31-99/16132 | 99-50 | 16 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SEKMAL-M | 33 | 106m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SEKMAL-S | 64 | 106m | 2/66-66/95 | 64-66 | 2 | **FLOW_ABOVE** | 66 | REPRICEABLE→66 |
| ATPCHALLENGERMATCH-26JUL05TENBER-B | 55 | 207m | 740/1-99/92948 | 49-1 | -54 | **FLOW_AT_LEVEL** | 55 |  |
| ATPCHALLENGERMATCH-26JUL05URRMEL-M | 93 | 9m | 2/97-97/135 | 95-97 | 4 | **FLOW_ABOVE** | 93 | flow above but bound 93c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05VANTRO-T | 54 | 76m | 1/55-55/3 | 54-55 | 1 | **FLOW_ABOVE** | 55 | REPRICEABLE→55 |
| ATPCHALLENGERMATCH-26JUL05VANTRO-V | 46 | 76m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05VILPER-P | 12 | 74m | 2/13-14/95 | 12-13 | 1 | **FLOW_ABOVE** | 11 | flow above but bound 11c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05VILPER-V | 87 | 1m | 0 | 87-89 | — | **NO_FLOW** | 88 |  |
| ATPMATCH-26JUL05HURSTR-STR | 23 | 11m | 684/15-49/197314 | 48-18 | -8 | **FLOW_AT_LEVEL** | 26 |  |
| ITFMATCH-26JUL05CRIMAR-MAR | 2 | 90m | 260/1-9/31607 | 7-1 | -1 | **FLOW_AT_LEVEL** | 3 |  |
| ITFMATCH-26JUL05GELBRE-GEL | 46 | 233m | 1040/1-62/71189 | 14-1 | -45 | **FLOW_AT_LEVEL** | 40 |  |
| ITFMATCH-26JUL05IONDAO-ION | 87 | 13m | 52/90-96/2270 | 94-91 | 3 | **FLOW_ABOVE** | 87 | flow above but bound 87c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05MILRAM-MIL | 3 | 2m | 5/7-7/430 | 7-7 | 4 | **FLOW_ABOVE** | 6 | REPRICEABLE→6 |
| ITFMATCH-26JUL05XUXCHE-XUX | 95 | 165m | 183/97-99/12747 | 99-98 | 2 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05KULVAN-KUL | 58 | 133m | 4218/29-99/394636 | 99-64 | -29 | **FLOW_AT_LEVEL** | 58 |  |
| WTACHALLENGERMATCH-26JUL05ARSOSU-A | 62 | 106m | 1/64-64/76 | 62-64 | 2 | **FLOW_ABOVE** | 64 | REPRICEABLE→64 |
| WTACHALLENGERMATCH-26JUL05ARSOSU-O | 35 | 106m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05KOBLEW-L | 8 | 211m | 723/1-25/97116 | 1-1 | -7 | **FLOW_AT_LEVEL** | 8 |  |
| WTACHALLENGERMATCH-26JUL05SMIJAR-J | 16 | 53m | 2/19-22/119 | 19-21 | 3 | **FLOW_ABOVE** | 16 | flow above but bound 16c < flow -- chasing breaks goal |
| WTAMATCH-26JUL05SABOSA-OSA | 25 | 125m | 4557/38-99/1677060 | 99-58 | 13 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05CIZCAZ | 23 | 1 | **24** | 97 | -73 |
| ITFWMATCH-26JUL05TUBSOB | 24 | 1 | **25** | 97 | -72 |
| ATPCHALLENGERMATCH-26JUL05VALREJ | 62 | 4 | **66** | 97 | -31 |
| ATPMATCH-26JUL05HURSTR | 71 | 18 | **89** | 97 | -8 |
| ITFMATCH-26JUL05MCKBER | 96 | 1 | **97** | 97 | +0 |
| ITFMATCH-26JUL05MILRAM | 90 | 7 | **97** | 97 | +0 |
| ITFMATCH-26JUL05SLOKHR | 39 | 59 | **98** | 97 | +1 |
| ITFMATCH-26JUL05THUGRE | 98 | 1 | **99** | 97 | +2 |
| ITFMATCH-26JUL05XUXCHE | 2 | 98 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05KOZMAY | 46 | 55 | **101** | 97 | +4 |
| ITFMATCH-26JUL05IONDAO | 10 | 91 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05URRMEL | 4 | 97 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05MONHUR | 4 | 98 | **102** | 97 | +5 |
| WTACHALLENGERMATCH-26JUL05SMIJAR | 81 | 21 | **102** | 97 | +5 |
| ITFMATCH-26JUL05BONBRA | 13 | 93 | **106** | 97 | +9 |
| ATPCHALLENGERMATCH-26JUL05RYBTUN | 73 | 37 | **110** | 97 | +13 |
| ITFMATCH-26JUL05SALCON | 13 | 99 | **112** | 97 | +15 |
| ATPCHALLENGERMATCH-26JUL05IVAGAN | 22 | 91 | **113** | 97 | +16 |
| ATPCHALLENGERMATCH-26JUL05GOIAND | 31 | 88 | **119** | 97 | +22 |
| ATPCHALLENGERMATCH-26JUL05HUEMAR | 31 | 99 | **130** | 97 | +33 |
| ATPCHALLENGERMATCH-26JUL05SANROD | 82 | 50 | **132** | 97 | +35 |
| ATPCHALLENGERMATCH-26JUL05RAMNEU | 36 | 98 | **134** | 97 | +37 |
| ITFMATCH-26JUL05SABMIS | 81 | 94 | **175** | 97 | +78 |

## PATTERNS (sub-B) — 40
- deep_neg_fv: KXITFWMATCH-26JUL05TRAABB-ABB {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05RAMNEU-RAM {"fill": 36, "age_min": 247, "mode": "SET_BELOW_FLOW(prints 37c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05WEHIFI-IFI {"fill": 11, "age_min": 247, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL05DITLEW-DIT {"fill": 31, "age_min": 247, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05KUZMAT-MAT {"fill": 5, "age_min": 247, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXITFWMATCH-26JUL05AITDAE-AIT {"entry_minus_fv_burst": -9.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05VALREJ-VAL {"fill": 62, "age_min": 245, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05CIZCAZ-CIZ {"fill": 23, "age_min": 245, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTAMATCH-26JUL05BENGAU-GAU {"fill": 50, "age_min": 244, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFMATCH-26JUL05SALCON-CON {"entry_minus_fv_burst": -10.0}
- half_arm_aging: KXITFMATCH-26JUL05SALCON-CON {"fill": 13, "age_min": 238, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFMATCH-26JUL05GELBRE-BRE {"entry_minus_fv_burst": -25.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05PEROPI-OPI {"entry_minus_fv_burst": -8.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05INGFEL-FEL {"fill": 72, "age_min": 231, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05HUEMAR-MAR {"fill": 31, "age_min": 219, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05TENBER-TEN {"entry_minus_fv_burst": -12.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05SUNBAR-BAR {"entry_minus_fv_burst": -31.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05RYBTUN-TUN {"fill": 73, "age_min": 211, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL05TUBSOB-SOB {"fill": 24, "age_min": 205, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05PDACAS-CAS {"entry_minus_fv_burst": -12.5}
- half_arm_aging: KXITFMATCH-26JUL05BONBRA-BRA {"fill": 13, "age_min": 193, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05HIGZHU-HIG {"entry_minus_fv_burst": -8.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05POTANG-POT {"entry_minus_fv_burst": -15.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05POTANG-POT {"fill": 50, "age_min": 181, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL05SABMIS-SAB {"fill": 81, "age_min": 179, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05BINPOL-BIN {"entry_minus_fv_burst": -31.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05GOIAND-GOI {"fill": 31, "age_min": 172, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL05XUXCHE-CHE {"fill": 2, "age_min": 165, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFMATCH-26JUL05THUGRE-THU {"fill": 98, "age_min": 163, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXITFMATCH-26JUL05FARBRO-BRO {"entry_minus_fv_burst": -18.0}
- deep_neg_fv: KXITFWMATCH-26JUL05KULVAN-KUL {"entry_minus_fv_burst": -14.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05IVAGAN-GAN {"fill": 22, "age_min": 150, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05MORMAR-MOR {"entry_minus_fv_burst": -18.5, "emitted_et": "2026-07-05 02:46:28 PM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05SANROD-ROD {"fill": 82, "age_min": 128, "mode": "SET_BELOW_FLOW(prints 16c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05ELLJOH-JOH {"entry_minus_fv_burst": -24.5}
- half_arm_aging: KXITFMATCH-26JUL05SLOKHR-KHR {"fill": 39, "age_min": 105, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL05MCKBER-BER {"fill": 96, "age_min": 105, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MONHUR-HUR {"fill": 4, "age_min": 77, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL05SMIJAR-SMI {"fill": 81, "age_min": 53, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05KOZMAY-KOZ {"fill": 46, "age_min": 46, "mode": "STARVATION(no prints since post)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
