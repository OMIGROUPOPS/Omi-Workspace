# LIVE VALIDATION — rolling status

- cycle 16 @ **2026-07-05 01:35:38 PM ET** | build `fb3f93b` | session boot 07-05 10:39 ET | log `live_v3_20260705.jsonl` | 31198 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 7 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 10:48:45 | **grace_breach** | KXITFMATCH-26JUL05SALCON-CON | fill 13c 5.2min past latch (grace 300s) |
| 11:10:44 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05TENBER | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 11:15:35 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL05KOBLEW | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 11:28:58 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05PEROPI | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 12:05:34 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05HUANOC | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 12:07:26 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05KAMVAN | pair combined 100c > goal 97c [organic: DEFECT-CLASS] |
| 13:19:41 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05MARHAI | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 68 graded (session)
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
| 11:54 | ATPCHALLENGERMATCH-26JUL05GOIAND-G | ATP_CHALL | underdog | 31 | 26 | +5 (place_cell) | — | pre | single |  | MIXED |
| 11:56 | ATPCHALLENGERMATCH-26JUL05GANZIN-G | ATP_CHALL | underdog | 29 | 25 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 12:01 | ITFMATCH-26JUL05XUXCHE-CHE | ITF_M | underdog | 2 | 1 | +1 (place_cell) | — | pre | single |  | MIXED |
| 12:01 | ITFMATCH-26JUL05FARBRO-FAR | ITF_M | ? | 64 | 64 | +0 (place_cell) | 17.0 | pre | pair | 96 | GIFT_CLASS |
| 12:03 | ITFMATCH-26JUL05THUGRE-THU | ITF_M | leader | 98 | 98 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 12:05 | ATPCHALLENGERMATCH-26JUL05HUANOC-N | ATP_CHALL | ? | 69 | 71 | -2 (window_cell) | — | pre | pair | 98 | GIFT_CLASS |
| 12:07 | ATPCHALLENGERMATCH-26JUL05KAMVAN-V | ATP_CHALL | ? | 87 | 87 | +0 (adopted_est) | — | pre | pair | 100 | PENDING |
| 12:08 | ATPMATCH-26JUL05SINMOC-SIN | ATP_MAIN | ? | 96 | 96 | +0 (adopted_est) | -0.5 | pre | single |  | MIXED |
| 12:12 | ITFMATCH-26JUL05FARBRO-BRO | ITF_M | ? | 32 | 30 | +2 (window_cell) | -18.0 | pre | pair | 96 | EARNED |
| 12:13 | ITFWMATCH-26JUL05KULVAN-KUL | ITF_W | ? | 55 | 60 | -5 (window_cell) | -14.0 | pre | pair | 94 | EARNED |
| 12:13 | ATPCHALLENGERMATCH-26JUL05PDACAS-P | ATP_CHALL | leader | 58 | 61 | -3 (place_cell) | 11.5 | pre | pair | 97 | GIFT_CLASS |
| 12:16 | ATPCHALLENGERMATCH-26JUL05IVAGAN-G | ATP_CHALL | ? | 22 | 23 | -1 (window_cell) | — | pre | single |  | EARNED |
| 12:17 | ATPCHALLENGERMATCH-26JUL05MARJUN-J | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | single |  | MIXED |
| 12:17 | ATPCHALLENGERMATCH-26JUL05BINPOL-P | ATP_CHALL | ? | 38 | 38 | +0 (window_cell) | 20.0 | pre | pair | 97 | EARNED |
| 12:21 | ATPCHALLENGERMATCH-26JUL05MARHAI-H | ATP_CHALL | ? | 96 | 94 | +2 (window_cell) | -1.5 | pre | pair | 99 | GIFT_CLASS |
| 12:21 | ATPCHALLENGERMATCH-26JUL05MORMAR-M | ATP_CHALL | leader | 59 | 59 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 12:24 | ITFWMATCH-26JUL05KULVAN-VAN | ITF_W | ? | 39 | 43 | -4 (window_cell) | 13.0 | pre | pair | 94 | EARNED |
| 12:38 | ATPCHALLENGERMATCH-26JUL05SANROD-R | ATP_CHALL | leader | 82 | 82 | +0 (place_cell) | — | pre | single |  | MIXED |
| 12:50 | ATPCHALLENGERMATCH-26JUL05POPCAS-P | ATP_CHALL | leader | 93 | 93 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 12:50 | ATPCHALLENGERMATCH-26JUL05ELLJOH-J | ATP_CHALL | ? | 33 | 30 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 13:01 | ITFMATCH-26JUL05SLOKHR-KHR | ITF_M | underdog | 39 | 35 | +4 (place_cell) | 15.0 | pre | single |  | GIFT_CLASS |
| 13:01 | ITFMATCH-26JUL05MCKBER-BER | ITF_M | leader | 96 | 96 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 13:03 | ATPCHALLENGERMATCH-26JUL05ELLJOH-E | ATP_CHALL | leader | 64 | 65 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 13:06 | ITFMATCH-26JUL05CRIMAR-CRI | ITF_M | leader | 93 | 93 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 13:12 | ITFMATCH-26JUL05CRIMAR-MAR | ITF_M | underdog | 4 | 1 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 13:12 | ATPCHALLENGERMATCH-26JUL05GANZIN-Z | ATP_CHALL | ? | 68 | 70 | -2 (place_cell) | — | pre | pair | 97 | MIXED |
| 13:19 | ATPCHALLENGERMATCH-26JUL05MARHAI-M | ATP_CHALL | ? | 3 | 5 | -2 (window_cell) | — | pre | pair | 99 | EARNED |
| 13:28 | WTACHALLENGERMATCH-26JUL05YAMOVC-O | WTA_CHALL | underdog | 28 | 25 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 13:28 | ATPCHALLENGERMATCH-26JUL05NUNCLA-C | ATP_CHALL | leader | 57 | 57 | +0 (place_cell) | — | pre | single |  | MIXED |
| 13:29 | ATPCHALLENGERMATCH-26JUL05MONHUR-H | ATP_CHALL | underdog | 4 | 2 | +2 (place_cell) | — | pre | single |  | MIXED |
| 13:31 | WTACHALLENGERMATCH-26JUL05YAMOVC-Y | WTA_CHALL | leader | 69 | 70 | -1 (place_cell) | — | pre | pair | 97 | MIXED |

## RESTING BIDS — 40 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 19, 'NO_FLOW': 13, 'FLOW_AT_LEVEL': 8} | repriceable now: true 4 / false 36 | **cumulative bid_grade lines: 755 (repriceable true 73 / false 682)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BANMAR-B | 65 | 175m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BANMAR-M | 33 | 175m | 7/33-37/340 | 33-37 | 0 | **FLOW_AT_LEVEL** | 33 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 91 | 158m | 39/97-99/5892 | 99-99 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05FARMAT-F | 38 | 35m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05FARMAT-M | 59 | 35m | 1/61-61/31 | 59-61 | 2 | **FLOW_ABOVE** | 61 | REPRICEABLE→61 |
| ATPCHALLENGERMATCH-26JUL05GOIAND-A | 66 | 101m | 124/69-95/13605 | 94-88 | 3 | **FLOW_ABOVE** | 66 | flow above but bound 66c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05HUEZEB-Z | 28 | 5m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IMAMIL-I | 41 | 104m | 0 | 42-44 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05IMAMIL-M | 58 | 104m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05KOZMAY-K | 46 | 104m | 2/47-47/180 | 46-47 | 1 | **FLOW_ABOVE** | 44 | flow above but bound 44c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05KOZMAY-M | 53 | 104m | 6/53-55/255 | 53-55 | 0 | **FLOW_AT_LEVEL** | 54 |  |
| ATPCHALLENGERMATCH-26JUL05MARJUN-M | 58 | 78m | 5/62-62/27 | 60-62 | 4 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MONHUR-M | 93 | 6m | 4/97-98/2657 | 97-98 | 4 | **FLOW_ABOVE** | 93 | flow above but bound 93c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MORMAR-M | 38 | 8m | 19/43-48/1124 | 39-45 | 5 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05NUNCLA-N | 39 | 75m | 0 | 43-46 | — | **NO_FLOW** | 40 |  |
| ATPCHALLENGERMATCH-26JUL05PAPMBI-M | 65 | 75m | 2/68-68/45 | 66-68 | 3 | **FLOW_ABOVE** | 68 | REPRICEABLE→68 |
| ATPCHALLENGERMATCH-26JUL05PAPMBI-P | 33 | 75m | 1/35-35/2 | 33-35 | 2 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05POPCAS-C | 4 | 45m | 3/20-27/10 | 8-16 | 16 | **FLOW_ABOVE** | 4 | flow above but bound 4c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PRICOU-P | 47 | 124m | 96/1-59/22582 | 1-1 | -46 | **FLOW_AT_LEVEL** | 47 |  |
| ATPCHALLENGERMATCH-26JUL05RAMNEU-N | 61 | 176m | 17/98-99/2359 | 99-98 | 37 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SANROD-S | 15 | 52m | 111/31-99/16132 | 99-50 | 16 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SEKMAL-M | 33 | 35m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SEKMAL-S | 64 | 35m | 1/66-66/29 | 64-66 | 2 | **FLOW_ABOVE** | 66 | REPRICEABLE→66 |
| ATPCHALLENGERMATCH-26JUL05TENBER-B | 55 | 136m | 740/1-99/92948 | 49-1 | -54 | **FLOW_AT_LEVEL** | 55 |  |
| ATPCHALLENGERMATCH-26JUL05URRMEL-M | 95 | 5m | 0 | 95-96 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05URRMEL-U | 4 | 5m | 0 | 4-5 | — | **NO_FLOW** | 2 |  |
| ATPCHALLENGERMATCH-26JUL05VANTRO-T | 54 | 5m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05VANTRO-V | 46 | 5m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05VILPER-P | 12 | 4m | 0 | 12-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL05CRIMAR-MAR | 2 | 19m | 215/1-9/26852 | 7-2 | -1 | **FLOW_AT_LEVEL** | 3 |  |
| ITFMATCH-26JUL05GELBRE-GEL | 46 | 162m | 1040/1-62/71189 | 14-1 | -45 | **FLOW_AT_LEVEL** | 40 |  |
| ITFMATCH-26JUL05SLOKHR-SLO | 50 | 7m | 401/88-99/70371 | 97-59 | 38 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05XUXCHE-XUX | 95 | 94m | 183/97-99/12747 | 99-98 | 2 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05KULVAN-KUL | 58 | 62m | 804/48-96/61095 | 93-60 | -10 | **FLOW_AT_LEVEL** | 58 |  |
| WTACHALLENGERMATCH-26JUL05ARSOSU-A | 62 | 35m | 1/64-64/76 | 62-64 | 2 | **FLOW_ABOVE** | 64 | REPRICEABLE→64 |
| WTACHALLENGERMATCH-26JUL05ARSOSU-O | 35 | 35m | 0 | 35-37 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05KOBLEW-L | 8 | 140m | 723/1-25/97116 | 1-1 | -7 | **FLOW_AT_LEVEL** | 8 |  |
| WTACHALLENGERMATCH-26JUL05SMIJAR-J | 20 | 104m | 2/21-22/23 | 20-22 | 1 | **FLOW_ABOVE** | 18 | flow above but bound 18c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05SMIJAR-S | 81 | 103m | 4/82-82/87 | 81-82 | 1 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| WTAMATCH-26JUL05SABOSA-OSA | 25 | 54m | 2704/38-80/1229400 | 76-59 | 13 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05CIZCAZ | 23 | 1 | **24** | 97 | -73 |
| ITFWMATCH-26JUL05TUBSOB | 24 | 1 | **25** | 97 | -72 |
| ATPCHALLENGERMATCH-26JUL05VALREJ | 62 | 4 | **66** | 97 | -31 |
| ITFMATCH-26JUL05SLOKHR | 39 | 59 | **98** | 97 | +1 |
| ITFMATCH-26JUL05THUGRE | 98 | 1 | **99** | 97 | +2 |
| ITFMATCH-26JUL05MCKBER | 96 | 3 | **99** | 97 | +2 |
| ITFMATCH-26JUL05XUXCHE | 2 | 98 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05MARJUN | 39 | 62 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05MONHUR | 4 | 98 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05NUNCLA | 57 | 46 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL05MORMAR | 59 | 45 | **104** | 97 | +7 |
| ITFMATCH-26JUL05BONBRA | 13 | 93 | **106** | 97 | +9 |
| ATPCHALLENGERMATCH-26JUL05POPCAS | 93 | 16 | **109** | 97 | +12 |
| ATPCHALLENGERMATCH-26JUL05RYBTUN | 73 | 37 | **110** | 97 | +13 |
| ITFMATCH-26JUL05SALCON | 13 | 99 | **112** | 97 | +15 |
| ATPCHALLENGERMATCH-26JUL05IVAGAN | 22 | 91 | **113** | 97 | +16 |
| ATPCHALLENGERMATCH-26JUL05GOIAND | 31 | 88 | **119** | 97 | +22 |
| ATPCHALLENGERMATCH-26JUL05HUEMAR | 31 | 99 | **130** | 97 | +33 |
| ATPCHALLENGERMATCH-26JUL05SANROD | 82 | 50 | **132** | 97 | +35 |
| ATPCHALLENGERMATCH-26JUL05RAMNEU | 36 | 98 | **134** | 97 | +37 |
| ITFMATCH-26JUL05SABMIS | 81 | 94 | **175** | 97 | +78 |

## PATTERNS (sub-B) — 39
- deep_neg_fv: KXITFWMATCH-26JUL05TRAABB-ABB {"entry_minus_fv_burst": -31.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05RAMNEU-RAM {"fill": 36, "age_min": 176, "mode": "SET_BELOW_FLOW(prints 37c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05WEHIFI-IFI {"fill": 11, "age_min": 176, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL05DITLEW-DIT {"fill": 31, "age_min": 176, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05KUZMAT-MAT {"fill": 5, "age_min": 176, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXITFWMATCH-26JUL05AITDAE-AIT {"entry_minus_fv_burst": -9.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05VALREJ-VAL {"fill": 62, "age_min": 175, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05CIZCAZ-CIZ {"fill": 23, "age_min": 174, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTAMATCH-26JUL05BENGAU-GAU {"fill": 50, "age_min": 173, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFMATCH-26JUL05SALCON-CON {"entry_minus_fv_burst": -10.0}
- half_arm_aging: KXITFMATCH-26JUL05SALCON-CON {"fill": 13, "age_min": 167, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFMATCH-26JUL05GELBRE-BRE {"entry_minus_fv_burst": -25.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05PEROPI-OPI {"entry_minus_fv_burst": -8.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05INGFEL-FEL {"fill": 72, "age_min": 160, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05HUEMAR-MAR {"fill": 31, "age_min": 148, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05TENBER-TEN {"entry_minus_fv_burst": -12.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05SUNBAR-BAR {"entry_minus_fv_burst": -31.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05RYBTUN-TUN {"fill": 73, "age_min": 140, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL05TUBSOB-SOB {"fill": 24, "age_min": 135, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05PDACAS-CAS {"entry_minus_fv_burst": -12.5}
- half_arm_aging: KXITFMATCH-26JUL05BONBRA-BRA {"fill": 13, "age_min": 122, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05HIGZHU-HIG {"entry_minus_fv_burst": -8.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05POTANG-POT {"entry_minus_fv_burst": -15.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05POTANG-POT {"fill": 50, "age_min": 110, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL05SABMIS-SAB {"fill": 81, "age_min": 108, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05BINPOL-BIN {"entry_minus_fv_burst": -31.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05GOIAND-GOI {"fill": 31, "age_min": 101, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFMATCH-26JUL05XUXCHE-CHE {"fill": 2, "age_min": 94, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFMATCH-26JUL05THUGRE-THU {"fill": 98, "age_min": 92, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPMATCH-26JUL05SINMOC-SIN {"fill": 96, "age_min": 87, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFMATCH-26JUL05FARBRO-BRO {"entry_minus_fv_burst": -18.0}
- deep_neg_fv: KXITFWMATCH-26JUL05KULVAN-KUL {"entry_minus_fv_burst": -14.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05IVAGAN-GAN {"fill": 22, "age_min": 79, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARJUN-JUN {"fill": 39, "age_min": 78, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MORMAR-MOR {"fill": 59, "age_min": 74, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05SANROD-ROD {"fill": 82, "age_min": 58, "mode": "SET_BELOW_FLOW(prints 16c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05POPCAS-POP {"fill": 93, "age_min": 45, "mode": "SET_BELOW_FLOW(prints 16c above)"}
- half_arm_aging: KXITFMATCH-26JUL05SLOKHR-KHR {"fill": 39, "age_min": 34, "mode": "SET_BELOW_FLOW(prints 38c above)", "emitted_et": "2026-07-05 01:35:38 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL05MCKBER-BER {"fill": 96, "age_min": 34, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-05 01:35:38 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
