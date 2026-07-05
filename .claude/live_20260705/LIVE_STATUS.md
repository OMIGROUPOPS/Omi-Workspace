# LIVE VALIDATION — rolling status

- cycle 66 @ **2026-07-05 08:11:39 AM ET** | build `1b4bc74` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 97582 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 6 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 05:08:08 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05SCHDE | pair combined 99c > goal 97c |
| 06:39:12 | **walk_cap_breach** | KXATPCHALLENGERMATCH-26JUL05JANRYA-JAN | buy 94c > ceiling 81c (conception 78 + cap) ref=None |
| 06:54:48 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05JANRYA | pair combined 99c > goal 97c |
| 07:07:09 | **grace_breach** | KXATPCHALLENGERMATCH-26JUL05IEMBER-BER | fill 98c 5.1min past latch (grace 300s) |
| 07:07:09 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05IEMBER | pair combined 102c > goal 97c |
| 07:54:36 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05COVDEL | pair combined 99c > goal 97c |

## FILLS — 90 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:32 | ITFWMATCH-26JUL04MAXSTE-MAX | ITF_W | underdog | 14 | 10 | +4 (place_cell) | — | pre | single |  | MIXED |
| 21:34 | ITFWMATCH-26JUL04BROKOI-KOI | ITF_W | underdog | 21 | 18 | +3 (place_cell) | — | pre | single |  | MIXED |
| 21:40 | ATPCHALLENGERMATCH-26JUL04LEGWIN-L | ATP_CHALL | ? | 80 | 83 | -3 (window_cell) | -34.0 | pre | single |  | EARNED |
| 03:09 | ATPCHALLENGERMATCH-26JUL05MARZAN-Z | ATP_CHALL | underdog | 6 | 11 | -5 (place_cell) | — | pre | single |  | EARNED |
| 04:03 | ATPCHALLENGERMATCH-26JUL05PIELAR-P | ATP_CHALL | leader | 91 | 91 | +0 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 04:04 | ATPCHALLENGERMATCH-26JUL05VILKOV-K | ATP_CHALL | underdog | 47 | 44 | +3 (place_cell) | -5.0 | pre | pair | 97 | EARNED |
| 04:09 | ATPCHALLENGERMATCH-26JUL05CRIRUB-R | ATP_CHALL | leader | 72 | 73 | -1 (place_cell) | 17.5 | pre | pair | 97 | GIFT_CLASS |
| 04:10 | ATPCHALLENGERMATCH-26JUL05PRIROT-P | ATP_CHALL | leader | 70 | 70 | +0 (place_cell) | -2.0 | pre | pair | 97 | GIFT_CLASS |
| 04:10 | ATPCHALLENGERMATCH-26JUL05SEIMOL-M | ATP_CHALL | leader | 84 | 84 | +0 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 04:11 | ATPCHALLENGERMATCH-26JUL05VILKOV-V | ATP_CHALL | ? | 50 | 53 | -3 (window_cell) | 6.5 | pre | pair | 97 | GIFT_CLASS |
| 04:11 | ATPCHALLENGERMATCH-26JUL05SEIMOL-S | ATP_CHALL | underdog | 11 | 11 | +0 (place_cell) | — | pre | pair | 95 | EARNED |
| 04:44 | ATPCHALLENGERMATCH-26JUL05PIELAR-L | ATP_CHALL | underdog | 5 | 5 | +0 (place_cell) | — | pre | pair | 96 | EARNED |
| 04:48 | WTACHALLENGERMATCH-26JUL05KUDBOU-B | WTA_CHALL | underdog | 5 | 2 | +3 (place_cell) | -15.0 | pre | pair | 97 | EARNED |
| 05:06 | WTACHALLENGERMATCH-26JUL05HERVAI-H | WTA_CHALL | leader | 81 | 83 | -2 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:07 | ATPCHALLENGERMATCH-26JUL05SCHDE-DE | ATP_CHALL | leader | 75 | 75 | +0 (place_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 05:08 | ATPCHALLENGERMATCH-26JUL05SCHDE-SC | ATP_CHALL | underdog | 24 | 20 | +4 (place_cell) | — | pre | pair | 99 | MIXED |
| 05:09 | ATPCHALLENGERMATCH-26JUL05SMIPIR-P | ATP_CHALL | leader | 71 | 72 | -1 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 05:10 | ATPCHALLENGERMATCH-26JUL05BERBOC-B | ATP_CHALL | underdog | 22 | 17 | +5 (place_cell) | 12.5 | pre | pair | 97 | EARNED |
| 05:10 | WTACHALLENGERMATCH-26JUL05MONGIM-G | WTA_CHALL | underdog | 26 | 26 | +0 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:17 | ATPCHALLENGERMATCH-26JUL05BERBOC-B | ATP_CHALL | leader | 75 | 75 | +0 (place_cell) | -15.0 | pre | pair | 97 | EARNED |
| 05:21 | WTACHALLENGERMATCH-26JUL05MONGIM-M | WTA_CHALL | leader | 71 | 71 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:21 | ATPCHALLENGERMATCH-26JUL05DIACEC-D | ATP_CHALL | leader | 65 | 66 | -1 (place_cell) | 18.0 | pre | pair | 96 | GIFT_CLASS |
| 05:21 | ATPCHALLENGERMATCH-26JUL05CRIRUB-C | ATP_CHALL | underdog | 25 | 22 | +3 (place_cell) | -21.0 | pre | pair | 97 | EARNED |
| 05:22 | ATPCHALLENGERMATCH-26JUL05RATRAH-R | ATP_CHALL | leader | 58 | 58 | +0 (place_cell) | -17.5 | pre | pair | 97 | EARNED |
| 05:25 | ATPCHALLENGERMATCH-26JUL05DIACEC-C | ATP_CHALL | ? | 31 | 33 | -2 (window_cell) | -19.0 | pre | pair | 96 | EARNED |
| 05:34 | ATPCHALLENGERMATCH-26JUL05SMIPIR-S | ATP_CHALL | underdog | 26 | 26 | +0 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:35 | ATPCHALLENGERMATCH-26JUL05MARDUR-D | ATP_CHALL | leader | 63 | 63 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 05:35 | ATPCHALLENGERMATCH-26JUL05CAMBID-C | ATP_CHALL | leader | 82 | 82 | +0 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 05:41 | WTACHALLENGERMATCH-26JUL05KUDBOU-K | WTA_CHALL | leader | 92 | 93 | -1 (place_cell) | 15.5 | pre | pair | 97 | GIFT_CLASS |
| 05:44 | ATPCHALLENGERMATCH-26JUL05CAMBID-B | ATP_CHALL | underdog | 14 | 14 | +0 (place_cell) | — | pre | pair | 96 | EARNED |
| 05:45 | WTACHALLENGERMATCH-26JUL05HERVAI-V | WTA_CHALL | underdog | 16 | 13 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:50 | ATPCHALLENGERMATCH-26JUL05MARDUR-M | ATP_CHALL | underdog | 34 | 31 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:56 | ATPCHALLENGERMATCH-26JUL05POTANG-A | ATP_CHALL | underdog | 47 | 44 | +3 (place_cell) | — | pre | single |  | EARNED |
| 06:07 | ATPCHALLENGERMATCH-26JUL05PAPPAR-P | ATP_CHALL | underdog | 15 | 12 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:10 | ATPCHALLENGERMATCH-26JUL05MELWAL-W | ATP_CHALL | leader | 63 | 63 | +0 (place_cell) | -54.0 | pre | pair | 97 | EARNED |
| 06:14 | ATPCHALLENGERMATCH-26JUL05MELWAL-M | ATP_CHALL | underdog | 34 | 30 | +4 (place_cell) | 24.5 | pre | pair | 97 | GIFT_CLASS |
| 06:15 | ATPMATCH-26JUL05AUGDAV-AUG | ATP_MAIN | leader | 63 | 64 | -1 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 06:16 | ATPCHALLENGERMATCH-26JUL05RATRAH-R | ATP_CHALL | underdog | 39 | 35 | +4 (place_cell) | 14.5 | pre | pair | 97 | GIFT_CLASS |
| 06:18 | WTAMATCH-26JUL05MUCKRE-KRE | WTA_MAIN | underdog | 38 | 37 | +1 (place_cell) | — | pre | single |  | MIXED |
| 06:18 | ATPCHALLENGERMATCH-26JUL05PRIROT-R | ATP_CHALL | underdog | 27 | 28 | -1 (place_cell) | 17.5 | pre | pair | 97 | EARNED |
| 06:19 | ATPCHALLENGERMATCH-26JUL05MARNVS-N | ATP_CHALL | underdog | 5 | 2 | +3 (place_cell) | — | pre | single |  | MIXED |
| 06:26 | ATPCHALLENGERMATCH-26JUL05PAPPAR-P | ATP_CHALL | leader | 82 | 82 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 06:28 | ATPCHALLENGERMATCH-26JUL05NIJBER-B | ATP_CHALL | underdog | 23 | 20 | +3 (place_cell) | -23.0 | pre | pair | 97 | EARNED |
| 06:31 | ATPCHALLENGERMATCH-26JUL05SEYMAJ-M | ATP_CHALL | ? | 4 | 2 | +2 (place_cell) | — | pre | single |  | MIXED |
| 06:37 | ATPCHALLENGERMATCH-26JUL05FRUSIN-F | ATP_CHALL | underdog | 5 | 2 | +3 (place_cell) | — | pre | single |  | MIXED |
| 06:40 | ATPMATCH-26JUL05SAFDJO-DJO | ATP_MAIN | leader | 85 | 85 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 06:40 | ITFMATCH-26JUL05BOUDOU-DOU | ITF_M | leader | 75 | 75 | +0 (place_cell) | 13.0 | pre | pair | 97 | GIFT_CLASS |
| 06:40 | ITFMATCH-26JUL05ELIAZO-ELI | ITF_M | underdog | 18 | 14 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:40 | ATPCHALLENGERMATCH-26JUL05NIJBER-N | ATP_CHALL | ? | 74 | 74 | +0 (place_cell) | 39.5 | pre | pair | 97 | GIFT_CLASS |
| 06:41 | ITFMATCH-26JUL05ELIAZO-AZO | ITF_M | leader | 79 | 78 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:44 | ATPCHALLENGERMATCH-26JUL05JANRYA-R | ATP_CHALL | underdog | 5 | 2 | +3 (place_cell) | — | pre | pair | 99 | EARNED |
| 06:49 | ATPCHALLENGERMATCH-26JUL05PARHAM-H | ATP_CHALL | leader | 90 | 87 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 06:54 | ATPCHALLENGERMATCH-26JUL05JANRYA-J | ATP_CHALL | leader | 94 | 94 | +0 (place_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 06:58 | ATPCHALLENGERMATCH-26JUL05KUZMAT-M | ATP_CHALL | underdog | 7 | 4 | +3 (place_cell) | — | pre | single |  | MIXED |
| 06:58 | ITFMATCH-26JUL05BOUDOU-BOU | ITF_M | underdog | 22 | 15 | +7 (place_cell) | -14.0 | 3.9 | pair | 97 | EARNED |
| 07:01 | ATPCHALLENGERMATCH-26JUL05IEMBER-I | ATP_CHALL | underdog | 4 | 2 | +2 (place_cell) | 2.0 | pre | pair | 102 | MIXED |
| 07:01 | ITFWMATCH-26JUL05SPIGAR-GAR | ITF_W | underdog | 1 | 1 | +0 (place_cell) | — | pre | single |  | MIXED |
| 07:07 | ATPCHALLENGERMATCH-26JUL05IEMBER-B | ATP_CHALL | leader | 98 | 95 | +3 (place_cell) | -5.5 | 5.1 | pair | 102 | EARNED |
| 07:13 | ATPCHALLENGERMATCH-26JUL05LUZSAN-L | ATP_CHALL | ? | 19 | 16 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:13 | ITFMATCH-26JUL05MORHAU-MOR | ITF_M | underdog | 6 | 2 | +4 (place_cell) | — | pre | pair | 89 | EARNED |
| 07:14 | ATPCHALLENGERMATCH-26JUL05STALOC-S | ATP_CHALL | leader | 94 | 94 | +0 (place_cell) | 18.5 | pre | pair | 97 | GIFT_CLASS |
| 07:14 | WTACHALLENGERMATCH-26JUL05MORNGU-M | WTA_CHALL | underdog | 6 | 3 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:15 | ATPCHALLENGERMATCH-26JUL05PARHAM-P | ATP_CHALL | underdog | 7 | 6 | +1 (place_cell) | — | pre | pair | 97 | EARNED |
| 07:15 | ITFMATCH-26JUL05MORHAU-HAU | ITF_M | leader | 83 | 56 | +27 (place_cell) | — | pre | pair | 89 | MIXED |
| 07:15 | ATPCHALLENGERMATCH-26JUL05GOMMAJ-G | ATP_CHALL | leader | 80 | 80 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 07:18 | WTACHALLENGERMATCH-26JUL05BARPOP-P | WTA_CHALL | leader | 65 | 63 | +2 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 07:18 | ATPCHALLENGERMATCH-26JUL05STALOC-L | ATP_CHALL | underdog | 3 | 3 | +0 (place_cell) | -5.0 | 0.6 | pair | 97 | EARNED |
| 07:19 | WTACHALLENGERMATCH-26JUL05MORNGU-N | WTA_CHALL | leader | 91 | 91 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:21 | WTAMATCH-26JUL05SABOSA-OSA | WTA_MAIN | underdog | 31 | 28 | +3 (place_cell) | — | pre | single |  | MIXED |
| 07:24 | ATPCHALLENGERMATCH-26JUL05INGFEL-I | ATP_CHALL | ? | 25 | 20 | +5 (place_cell) | — | pre | single |  | MIXED |
| 07:28 | ATPCHALLENGERMATCH-26JUL05CARCER-C | ATP_CHALL | leader | 93 | 92 | +1 (place_cell) | -1.0 | pre | single |  | GIFT_CLASS |
| 07:30 | ATPCHALLENGERMATCH-26JUL05MACBRA-B | ATP_CHALL | leader | 94 | 94 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 07:31 | WTACHALLENGERMATCH-26JUL05BARPOP-B | WTA_CHALL | underdog | 32 | 30 | +2 (place_cell) | — | pre | pair | 97 | EARNED |
| 07:39 | ATPCHALLENGERMATCH-26JUL05TIXLEC-L | ATP_CHALL | leader | 80 | 77 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 07:40 | ATPCHALLENGERMATCH-26JUL05DONGRE-G | ATP_CHALL | underdog | 19 | 16 | +3 (place_cell) | — | pre | single |  | MIXED |
| 07:40 | ATPCHALLENGERMATCH-26JUL05LUZSAN-S | ATP_CHALL | leader | 78 | 78 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:41 | ATPCHALLENGERMATCH-26JUL05CHESPE-S | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | single |  | EARNED |
| 07:45 | WTACHALLENGERMATCH-26JUL05MORKOT-M | WTA_CHALL | underdog | 6 | 5 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:45 | WTAMATCH-26JUL05PEGJOV-PEG | WTA_MAIN | leader | 70 | 70 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 07:48 | ATPCHALLENGERMATCH-26JUL05GOMMAJ-M | ATP_CHALL | underdog | 17 | 14 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 07:49 | ATPCHALLENGERMATCH-26JUL05SCIORA-O | ATP_CHALL | leader | 81 | 80 | +1 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 07:50 | ATPCHALLENGERMATCH-26JUL05SEGHAB-S | ATP_CHALL | leader | 90 | 89 | +1 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 07:52 | WTACHALLENGERMATCH-26JUL05MORKOT-K | WTA_CHALL | leader | 91 | 92 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:53 | ATPCHALLENGERMATCH-26JUL05COVDEL-D | ATP_CHALL | leader | 68 | 69 | -1 (place_cell) | — | pre | pair | 99 | MIXED |
| 07:54 | ATPCHALLENGERMATCH-26JUL05VALREJ-V | ATP_CHALL | leader | 67 | 67 | +0 (place_cell) | — | pre | single |  | MIXED |
| 07:54 | ATPCHALLENGERMATCH-26JUL05COVDEL-C | ATP_CHALL | underdog | 31 | 25 | +6 (place_cell) | — | pre | pair | 99 | MIXED |
| 08:01 | ITFMATCH-26JUL05DELNIC-DEL | ITF_M | underdog | 23 | 20 | +3 (place_cell) | — | pre | single |  | MIXED |
| 08:03 | ATPCHALLENGERMATCH-26JUL05TIXLEC-T | ATP_CHALL | ? | 17 | 16 | +1 (place_cell) | — | pre | pair | 97 | EARNED |
| 08:05 | ATPCHALLENGERMATCH-26JUL05SCIORA-S | ATP_CHALL | ? | 16 | 14 | +2 (place_cell) | — | pre | pair | 97 | EARNED |
| 08:08 | WTAMATCH-26JUL05PEGJOV-JOV | WTA_MAIN | underdog | 27 | 28 | -1 (place_cell) | — | pre | pair | 97 | EARNED |

## RESTING BIDS — 96 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 39, 'NO_FLOW': 41, 'FLOW_AT_LEVEL': 16} | repriceable now: true 7 / false 89 | **cumulative bid_grade lines: 420 (repriceable true 41 / false 379)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05ALBZOR-A | 91 | 14m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05ALBZOR-Z | 6 | 91m | 0 | 6-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BASRIB-B | 36 | 111m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BASRIB-R | 60 | 41m | 4/63-64/43 | 60-63 | 3 | **FLOW_ABOVE** | 62 | REPRICEABLE→62 |
| ATPCHALLENGERMATCH-26JUL05BLIPET-B | 5 | 31m | 3/6-6/60 | 5-6 | 1 | **FLOW_ABOVE** | 3 | flow above but bound 3c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05BLIPET-P | 94 | 11m | 0 | 94-95 | — | **NO_FLOW** | 94 |  |
| ATPCHALLENGERMATCH-26JUL05CAMBID-B | 15 | 132m | 93/1-39/12505 | 1-2 | -14 | **FLOW_AT_LEVEL** | 14 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 4 | 44m | 10/7-7/1132 | 4-6 | 3 | **FLOW_ABOVE** | 4 | flow above but bound 4c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05CHESPE-C | 58 | 171m | 76/61-90/12898 | 88-61 | 3 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05CHESPE-C | 58 | 11m | 24/81-90/2252 | 88-61 | 23 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | 69 | 13m | 0 | 69-72 | — | **NO_FLOW** | 73 |  |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | 28 | 20m | 0 | 28-31 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05COVDEL-C | 27 | 3m | 5/19-27/263 | 19-20 | -8 | **FLOW_AT_LEVEL** | 27 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-A | 6 | 311m | 0 | 6-7 | — | **NO_FLOW** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 93 | 91m | 1/94-94/6 | 93-94 | 1 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05DESYEV-D | 29 | 61m | 0 | 29-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05DESYEV-Y | 70 | 19m | 0 | 70-72 | — | **NO_FLOW** | 71 |  |
| ATPCHALLENGERMATCH-26JUL05DONGRE-D | 78 | 31m | 1/83-83/99 | 82-82 | 5 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05FELMOE-F | 75 | 8m | 0 | 75-76 | — | **NO_FLOW** | 76 |  |
| ATPCHALLENGERMATCH-26JUL05FELMOE-M | 24 | 17m | 2/25-25/184 | 24-25 | 1 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05FRUSIN-S | 92 | 94m | 70/93-99/7782 | 99-97 | 1 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05FRUSIN-S | 92 | 94m | 70/93-99/7782 | 99-97 | 1 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05HUANOC-H | 29 | 24m | 0 | 29-32 | — | **NO_FLOW** | 28 |  |
| ATPCHALLENGERMATCH-26JUL05INGFEL-F | 72 | 47m | 1/77-77/20 | 77-78 | 5 | **FLOW_ABOVE** | 72 | flow above but bound 72c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05JANRYA-R | 1 | 66m | 51/1-6/10429 | 4-1 | 0 | **FLOW_AT_LEVEL** | 3 |  |
| ATPCHALLENGERMATCH-26JUL05KAMVAN-K | 12 | 29m | 0 | 12-13 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05KAMVAN-V | 87 | 41m | 0 | 87-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05KUZMAT-K | 90 | 73m | 0 | 93-95 | — | **NO_FLOW** | 90 |  |
| ATPCHALLENGERMATCH-26JUL05MACBRA-M | 3 | 41m | 58/4-10/8531 | 6-4 | 1 | **FLOW_ABOVE** | 3 | flow above but bound 3c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MARNVS-M | 92 | 112m | 43/97-99/5494 | 99-99 | 5 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MARZAN-M | 88 | 74m | 0 | 89-95 | — | **NO_FLOW** | 91 |  |
| ATPCHALLENGERMATCH-26JUL05PAPPAR-P | 14 | 105m | 273/1-46/55921 | 34-1 | -13 | **FLOW_AT_LEVEL** | 12 |  |
| ATPCHALLENGERMATCH-26JUL05PARHAM-H | 90 | 32m | 29/97-99/5450 | 99-93 | 7 | **FLOW_ABOVE** | 90 | flow above but bound 90c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PEROPI-O | 24 | 31m | 0 | 24-26 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PEROPI-P | 73 | 31m | 0 | 73-76 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PIELAR-L | 4 | 200m | 708/1-21/109667 | 19-1 | -3 | **FLOW_AT_LEVEL** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05POTANG-P | 52 | 92m | 8/54-56/243 | 55-55 | 2 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PRIROT-P | 86 | 90m | 378/79-99/90114 | 99-81 | -7 | **FLOW_AT_LEVEL** | 70 |  |
| ATPCHALLENGERMATCH-26JUL05RAMNEU-N | 61 | 13m | 0 | 61-62 | — | **NO_FLOW** | 62 |  |
| ATPCHALLENGERMATCH-26JUL05RAMNEU-R | 36 | 20m | 0 | 36-38 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05RAQMAS-M | 10 | 19m | 0 | 10-11 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05RAQMAS-R | 89 | 33m | 0 | 89-92 | — | **NO_FLOW** | 89 |  |
| ATPCHALLENGERMATCH-26JUL05RATRAH-R | 33 | 107m | 385/1-52/26626 | 21-1 | -32 | **FLOW_AT_LEVEL** | 36 |  |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 20 | 176m | 0 | 31-84 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 20 | 174m | 134/1-31/13364 | 12-1 | -19 | **FLOW_AT_LEVEL** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 17 | 170m | 125/1-31/13202 | 12-1 | -16 | **FLOW_AT_LEVEL** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-S | 16 | 2m | 3/21-26/124 | 26-17 | 5 | **FLOW_ABOVE** | 16 | flow above but bound 16c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SEGHAB-H | 1 | 5m | 14/3-5/1438 | 4-4 | 2 | **FLOW_ABOVE** | 6 | REPRICEABLE→3 |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ-S | 93 | 100m | 47/97-99/15876 | 99-99 | 4 | **FLOW_ABOVE** | 93 | flow above but bound 93c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SMIPIR-P | 58 | 139m | 352/80-99/31973 | 99-59 | 22 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05STALOC-S | 70 | 29m | 18/99-99/1913 | 99-71 | 29 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05STEDIN-D | 71 | 51m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05STEDIN-S | 27 | 42m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SZYSTR-S | 53 | 92m | 2/56-56/308 | 53-57 | 3 | **FLOW_ABOVE** | 56 | REPRICEABLE→56 |
| ATPCHALLENGERMATCH-26JUL05SZYSTR-S | 43 | 99m | 16/46-47/1027 | 45-47 | 3 | **FLOW_ABOVE** | 43 | flow above but bound 43c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05UTADEV-D | 39 | 91m | 0 | 39-41 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05UTADEV-U | 59 | 91m | 4/60-61/515 | 59-61 | 1 | **FLOW_ABOVE** | 60 | REPRICEABLE→60 |
| ATPCHALLENGERMATCH-26JUL05VALREJ-R | 30 | 14m | 0 | 34-35 | — | **NO_FLOW** | 30 |  |
| ATPCHALLENGERMATCH-26JUL05VILPUR-P | 80 | 41m | 0 | 80-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05VILPUR-V | 19 | 38m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05WALVAR-V | 2 | 20m | 0 | 2-3 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05WALVAR-W | 97 | 20m | 0 | 97-98 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05WEHIFI-I | 11 | 111m | 0 | 11-14 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05WEHIFI-W | 86 | 111m | 0 | 86-89 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05WEIHOE-H | 57 | 23m | 0 | 57-59 | — | **NO_FLOW** | 59 |  |
| ATPCHALLENGERMATCH-26JUL05WEIHOE-W | 39 | 36m | 0 | 39-42 | — | **NO_FLOW** | 37 |  |
| ATPMATCH-26JUL05AUGDAV-DAV | 34 | 116m | 40/39-40/2785 | 38-39 | 5 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05HURSTR-HUR | 73 | 92m | 26/74-74/871 | 73-74 | 1 | **FLOW_ABOVE** | 73 | flow above but bound 73c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05HURSTR-STR | 26 | 191m | 125/26-27/32754 | 26-27 | 0 | **FLOW_AT_LEVEL** | 26 |  |
| ATPMATCH-26JUL05SAFDJO-SAF | 12 | 91m | 117/15-17/32650 | 15-16 | 3 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05SINMOC-MOC | 3 | 191m | 52/4-4/12151 | 3-4 | 1 | **FLOW_ABOVE** | 3 | flow above but bound 3c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05SINMOC-SIN | 96 | 92m | 13/97-97/645 | 96-97 | 1 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05DELNIC-NIC | 74 | 8m | 0 | 82-79 | — | **NO_FLOW** | 74 |  |
| ITFMATCH-26JUL05ELIAZO-AZO | 70 | 84m | 3/99-99/406 | 99-80 | 29 | **FLOW_ABOVE** | 79 | flow above but bound 79c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05LENJON-JON | 19 | 6m | 0 | 19-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL05LENJON-LEN | 72 | 11m | 0 | 72-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL05MORHAU-MOR | 11 | 56m | 72/1-64/5274 | 2-1 | -10 | **FLOW_AT_LEVEL** | 14 |  |
| ITFWMATCH-26JUL04BROKOI-BRO | 76 | 637m | 1350/80-99/350336 | 99-78 | 4 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 639m | 545/86-99/126759 | 99-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05KARMAT-MAT | 1 | 11m | 10/1-3/727 | 2-2 | 0 | **FLOW_AT_LEVEL** | 1 |  |
| ITFWMATCH-26JUL05KUHEBE-KUH | 37 | 3m | 0 | 37-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL05PRIYUL-PRI | 79 | 2m | 1/89-89/22 | 79-81 | 10 | **FLOW_ABOVE** | 85 | flow above but bound 85c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05PRIYUL-YUL | 11 | 3m | 0 | 11-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL05SPIGAR-SPI | 96 | 69m | 0 | 99-99 | — | **NO_FLOW** | 94 |  |
| WTACHALLENGERMATCH-26JUL05BARPOP-P | 50 | 3m | 15/82-85/2288 | 81-58 | 32 | **FLOW_ABOVE** | 65 | flow above but bound 65c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05BAYMAR-B | 25 | 111m | 0 | 25-27 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05BAYMAR-M | 71 | 111m | 1/75-75/5 | 73-75 | 4 | **FLOW_ABOVE** | 75 | REPRICEABLE→75 |
| WTACHALLENGERMATCH-26JUL05DITLEW-D | 31 | 109m | 2/32-32/298 | 31-32 | 1 | **FLOW_ABOVE** | 29 | flow above but bound 29c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05DITLEW-L | 68 | 111m | 1/70-70/5 | 69-70 | 2 | **FLOW_ABOVE** | 70 | REPRICEABLE→70 |
| WTACHALLENGERMATCH-26JUL05MONGIM-G | 25 | 160m | 161/1-32/16236 | 26-1 | -24 | **FLOW_AT_LEVEL** | 26 |  |
| WTACHALLENGERMATCH-26JUL05MORKOT-M | 6 | 18m | 90/13-35/12925 | 30-7 | 7 | **FLOW_ABOVE** | 5 | flow above but bound 5c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05MORNGU-M | 4 | 51m | 110/1-12/31581 | 2-1 | -3 | **FLOW_AT_LEVEL** | 5 |  |
| WTAMATCH-26JUL05BENGAU-BEN | 48 | 92m | 20/48-49/1961 | 48-49 | 0 | **FLOW_AT_LEVEL** | 46 |  |
| WTAMATCH-26JUL05BENGAU-GAU | 51 | 92m | 53/51-52/4999 | 51-52 | 0 | **FLOW_AT_LEVEL** | 52 |  |
| WTAMATCH-26JUL05MUCKRE-MUC | 59 | 113m | 83/62-64/10950 | 63-63 | 3 | **FLOW_ABOVE** | 59 | flow above but bound 59c < flow -- chasing breaks goal |
| WTAMATCH-26JUL05SABOSA-SAB | 66 | 50m | 38/68-69/4293 | 68-69 | 2 | **FLOW_ABOVE** | 66 | flow above but bound 66c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN | 80 | 1 | **81** | 97 | -16 |
| ATPCHALLENGERMATCH-26JUL05SEGHAB | 90 | 4 | **94** | 97 | -3 |
| ATPCHALLENGERMATCH-26JUL05MACBRA | 94 | 4 | **98** | 97 | +1 |
| ITFWMATCH-26JUL04BROKOI | 21 | 78 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL05CARCER | 93 | 6 | **99** | 97 | +2 |
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |
| ITFWMATCH-26JUL05SPIGAR | 1 | 99 | **100** | 97 | +3 |
| WTAMATCH-26JUL05SABOSA | 31 | 69 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05CHESPE | 39 | 61 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05MARZAN | 6 | 95 | **101** | 97 | +4 |
| WTAMATCH-26JUL05MUCKRE | 38 | 63 | **101** | 97 | +4 |
| ATPMATCH-26JUL05SAFDJO | 85 | 16 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05DONGRE | 19 | 82 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05POTANG | 47 | 55 | **102** | 97 | +5 |
| ATPMATCH-26JUL05AUGDAV | 63 | 39 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05FRUSIN | 5 | 97 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05KUZMAT | 7 | 95 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05VALREJ | 67 | 35 | **102** | 97 | +5 |
| ITFMATCH-26JUL05DELNIC | 23 | 79 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ | 4 | 99 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL05INGFEL | 25 | 78 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL05MARNVS | 5 | 99 | **104** | 97 | +7 |

## PATTERNS (sub-B) — 28
- half_arm_aging: KXITFWMATCH-26JUL04MAXSTE-MAX {"fill": 14, "age_min": 639, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL04BROKOI-KOI {"fill": 21, "age_min": 637, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"entry_minus_fv_burst": -34.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"fill": 80, "age_min": 631, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARZAN-ZAN {"fill": 6, "age_min": 302, "mode": "STARVATION(no prints since post)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL05KUDBOU-BOU {"entry_minus_fv_burst": -15.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05BERBOC-BOC {"entry_minus_fv_burst": -15.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05CRIRUB-CRI {"entry_minus_fv_burst": -21.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05RATRAH-RAH {"entry_minus_fv_burst": -17.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05DIACEC-CEC {"entry_minus_fv_burst": -19.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05POTANG-ANG {"fill": 47, "age_min": 135, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05MELWAL-WAL {"entry_minus_fv_burst": -54.0}
- half_arm_aging: KXATPMATCH-26JUL05AUGDAV-AUG {"fill": 63, "age_min": 116, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXWTAMATCH-26JUL05MUCKRE-KRE {"fill": 38, "age_min": 114, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARNVS-NVS {"fill": 5, "age_min": 113, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05NIJBER-BER {"entry_minus_fv_burst": -23.0, "emitted_et": "2026-07-05 08:11:38 AM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05SEYMAJ-MAJ {"fill": 4, "age_min": 100, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05FRUSIN-FRU {"fill": 5, "age_min": 94, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXATPMATCH-26JUL05SAFDJO-DJO {"fill": 85, "age_min": 91, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05KUZMAT-MAT {"fill": 7, "age_min": 73, "mode": "STARVATION(no prints since post)"}
- deep_neg_fv: KXITFMATCH-26JUL05BOUDOU-BOU {"entry_minus_fv_burst": -14.0}
- half_arm_aging: KXITFWMATCH-26JUL05SPIGAR-GAR {"fill": 1, "age_min": 70, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXWTAMATCH-26JUL05SABOSA-OSA {"fill": 31, "age_min": 50, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05INGFEL-ING {"fill": 25, "age_min": 47, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05CARCER-CER {"fill": 93, "age_min": 44, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MACBRA-BRA {"fill": 94, "age_min": 41, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05DONGRE-GRE {"fill": 19, "age_min": 31, "mode": "SET_BELOW_FLOW(prints 5c above)", "emitted_et": "2026-07-05 08:11:38 AM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05CHESPE-SPE {"fill": 39, "age_min": 30, "mode": "SET_BELOW_FLOW(prints 3c above)", "emitted_et": "2026-07-05 08:11:38 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
