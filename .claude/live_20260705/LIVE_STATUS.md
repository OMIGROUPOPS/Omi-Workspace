# LIVE VALIDATION — rolling status

- cycle 62 @ **2026-07-05 07:30:39 AM ET** | build `34e17e3` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 59982 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 5 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 05:08:08 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05SCHDE | pair combined 99c > goal 97c |
| 06:39:12 | **walk_cap_breach** | KXATPCHALLENGERMATCH-26JUL05JANRYA-JAN | buy 94c > ceiling 81c (conception 78 + cap) ref=None |
| 06:54:48 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05JANRYA | pair combined 99c > goal 97c |
| 07:07:09 | **grace_breach** | KXATPCHALLENGERMATCH-26JUL05IEMBER-BER | fill 98c 5.1min past latch (grace 300s) |
| 07:07:09 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05IEMBER | pair combined 102c > goal 97c |

## FILLS — 72 graded (session)
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
| 06:10 | ATPCHALLENGERMATCH-26JUL05MELWAL-W | ATP_CHALL | leader | 63 | 63 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:14 | ATPCHALLENGERMATCH-26JUL05MELWAL-M | ATP_CHALL | underdog | 34 | 30 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:15 | ATPMATCH-26JUL05AUGDAV-AUG | ATP_MAIN | leader | 63 | 64 | -1 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 06:16 | ATPCHALLENGERMATCH-26JUL05RATRAH-R | ATP_CHALL | underdog | 39 | 35 | +4 (place_cell) | 14.5 | pre | pair | 97 | GIFT_CLASS |
| 06:18 | WTAMATCH-26JUL05MUCKRE-KRE | WTA_MAIN | underdog | 38 | 37 | +1 (place_cell) | — | pre | single |  | MIXED |
| 06:18 | ATPCHALLENGERMATCH-26JUL05PRIROT-R | ATP_CHALL | underdog | 27 | 28 | -1 (place_cell) | 17.5 | pre | pair | 97 | EARNED |
| 06:19 | ATPCHALLENGERMATCH-26JUL05MARNVS-N | ATP_CHALL | underdog | 5 | 2 | +3 (place_cell) | — | pre | single |  | MIXED |
| 06:26 | ATPCHALLENGERMATCH-26JUL05PAPPAR-P | ATP_CHALL | leader | 82 | 82 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 06:28 | ATPCHALLENGERMATCH-26JUL05NIJBER-B | ATP_CHALL | underdog | 23 | 20 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:31 | ATPCHALLENGERMATCH-26JUL05SEYMAJ-M | ATP_CHALL | ? | 4 | 2 | +2 (place_cell) | — | pre | single |  | MIXED |
| 06:37 | ATPCHALLENGERMATCH-26JUL05FRUSIN-F | ATP_CHALL | underdog | 5 | 2 | +3 (place_cell) | — | pre | single |  | MIXED |
| 06:40 | ATPMATCH-26JUL05SAFDJO-DJO | ATP_MAIN | leader | 85 | 85 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 06:40 | ITFMATCH-26JUL05BOUDOU-DOU | ITF_M | leader | 75 | 75 | +0 (place_cell) | 13.0 | pre | pair | 97 | GIFT_CLASS |
| 06:40 | ITFMATCH-26JUL05ELIAZO-ELI | ITF_M | underdog | 18 | 14 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:40 | ATPCHALLENGERMATCH-26JUL05NIJBER-N | ATP_CHALL | ? | 74 | 74 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:41 | ITFMATCH-26JUL05ELIAZO-AZO | ITF_M | leader | 79 | 78 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:44 | ATPCHALLENGERMATCH-26JUL05JANRYA-R | ATP_CHALL | underdog | 5 | 2 | +3 (place_cell) | — | pre | pair | 99 | EARNED |
| 06:49 | ATPCHALLENGERMATCH-26JUL05PARHAM-H | ATP_CHALL | leader | 90 | 87 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 06:54 | ATPCHALLENGERMATCH-26JUL05JANRYA-J | ATP_CHALL | leader | 94 | 94 | +0 (place_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 06:58 | ATPCHALLENGERMATCH-26JUL05KUZMAT-M | ATP_CHALL | underdog | 7 | 4 | +3 (place_cell) | — | pre | single |  | MIXED |
| 06:58 | ITFMATCH-26JUL05BOUDOU-BOU | ITF_M | underdog | 22 | 15 | +7 (place_cell) | -14.0 | 3.9 | pair | 97 | EARNED |
| 07:01 | ATPCHALLENGERMATCH-26JUL05IEMBER-I | ATP_CHALL | underdog | 4 | 2 | +2 (place_cell) | 2.0 | pre | pair | 102 | MIXED |
| 07:01 | ITFWMATCH-26JUL05SPIGAR-GAR | ITF_W | underdog | 1 | 1 | +0 (place_cell) | — | pre | single |  | MIXED |
| 07:07 | ATPCHALLENGERMATCH-26JUL05IEMBER-B | ATP_CHALL | leader | 98 | 95 | +3 (place_cell) | -5.5 | 5.1 | pair | 102 | EARNED |
| 07:13 | ATPCHALLENGERMATCH-26JUL05LUZSAN-L | ATP_CHALL | ? | 19 | 16 | +3 (place_cell) | — | pre | single |  | MIXED |
| 07:13 | ITFMATCH-26JUL05MORHAU-MOR | ITF_M | underdog | 6 | 2 | +4 (place_cell) | — | pre | pair | 89 | EARNED |
| 07:14 | ATPCHALLENGERMATCH-26JUL05STALOC-S | ATP_CHALL | leader | 94 | 94 | +0 (place_cell) | 18.5 | pre | pair | 97 | GIFT_CLASS |
| 07:14 | WTACHALLENGERMATCH-26JUL05MORNGU-M | WTA_CHALL | underdog | 6 | 3 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:15 | ATPCHALLENGERMATCH-26JUL05PARHAM-P | ATP_CHALL | underdog | 7 | 6 | +1 (place_cell) | — | pre | pair | 97 | EARNED |
| 07:15 | ITFMATCH-26JUL05MORHAU-HAU | ITF_M | leader | 83 | 56 | +27 (place_cell) | — | pre | pair | 89 | MIXED |
| 07:15 | ATPCHALLENGERMATCH-26JUL05GOMMAJ-G | ATP_CHALL | leader | 80 | 80 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 07:18 | WTACHALLENGERMATCH-26JUL05BARPOP-P | WTA_CHALL | leader | 65 | 63 | +2 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 07:18 | ATPCHALLENGERMATCH-26JUL05STALOC-L | ATP_CHALL | underdog | 3 | 3 | +0 (place_cell) | -5.0 | 0.6 | pair | 97 | EARNED |
| 07:19 | WTACHALLENGERMATCH-26JUL05MORNGU-N | WTA_CHALL | leader | 91 | 91 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:21 | WTAMATCH-26JUL05SABOSA-OSA | WTA_MAIN | underdog | 31 | 28 | +3 (place_cell) | — | pre | single |  | MIXED |
| 07:24 | ATPCHALLENGERMATCH-26JUL05INGFEL-I | ATP_CHALL | ? | 25 | 20 | +5 (place_cell) | — | pre | single |  | MIXED |
| 07:28 | ATPCHALLENGERMATCH-26JUL05CARCER-C | ATP_CHALL | leader | 93 | 92 | +1 (place_cell) | -1.0 | pre | single |  | GIFT_CLASS |
| 07:30 | ATPCHALLENGERMATCH-26JUL05MACBRA-B | ATP_CHALL | leader | 94 | 94 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 88 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 36, 'NO_FLOW': 36, 'FLOW_AT_LEVEL': 16} | repriceable now: true 10 / false 78 | **cumulative bid_grade lines: 352 (repriceable true 38 / false 314)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05ALBZOR-A | 87 | 49m | 0 | 87-93 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05ALBZOR-Z | 6 | 50m | 0 | 6-13 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BASRIB-B | 36 | 70m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BASRIB-R | 60 | 0m | 0 | 60-63 | — | **NO_FLOW** | 62 |  |
| ATPCHALLENGERMATCH-26JUL05CAMBID-B | 15 | 91m | 93/1-39/12505 | 1-2 | -14 | **FLOW_AT_LEVEL** | 14 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 4 | 3m | 9/7-7/998 | 4-7 | 3 | **FLOW_ABOVE** | 4 | flow above but bound 4c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05CHESPE-C | 58 | 130m | 3/61-61/64 | 58-61 | 3 | **FLOW_ABOVE** | 61 | REPRICEABLE→61 |
| ATPCHALLENGERMATCH-26JUL05CHESPE-S | 39 | 130m | 1/42-42/10 | 39-42 | 3 | **FLOW_ABOVE** | 39 | flow above but bound 39c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05COVDEL-C | 28 | 80m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05COVDEL-D | 69 | 80m | 2/72-73/19 | 71-73 | 3 | **FLOW_ABOVE** | 72 | REPRICEABLE→72 |
| ATPCHALLENGERMATCH-26JUL05DALARI-A | 6 | 270m | 0 | 6-7 | — | **NO_FLOW** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 93 | 50m | 1/94-94/6 | 93-94 | 1 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05DESYEV-D | 29 | 20m | 0 | 29-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05DESYEV-Y | 69 | 4m | 0 | 69-71 | — | **NO_FLOW** | 71 |  |
| ATPCHALLENGERMATCH-26JUL05DONGRE-D | 80 | 13m | 0 | 80-82 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05DONGRE-G | 19 | 50m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05FRUSIN-S | 92 | 53m | 50/93-99/5786 | 97-97 | 1 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05FRUSIN-S | 92 | 53m | 50/93-99/5786 | 97-97 | 1 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05GOMMAJ-M | 17 | 15m | 19/21-35/789 | 25-24 | 4 | **FLOW_ABOVE** | 17 | flow above but bound 17c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05HUANOC-H | 27 | 0m | 0 | 27-31 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05HUANOC-N | 70 | 0m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05INGFEL-F | 72 | 6m | 0 | 76-77 | — | **NO_FLOW** | 72 |  |
| ATPCHALLENGERMATCH-26JUL05JANRYA-R | 1 | 25m | 51/1-6/10429 | 4-1 | 0 | **FLOW_AT_LEVEL** | 3 |  |
| ATPCHALLENGERMATCH-26JUL05KAMVAN-K | 10 | 0m | 0 | 11-14 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05KAMVAN-V | 87 | 0m | 0 | 87-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05KUZMAT-K | 90 | 32m | 0 | 93-95 | — | **NO_FLOW** | 90 |  |
| ATPCHALLENGERMATCH-26JUL05LUZSAN-S | 78 | 17m | 11/84-92/1060 | 90-82 | 6 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MACBRA-M | 3 | 0m | 0 | 6-7 | — | **NO_FLOW** | 3 |  |
| ATPCHALLENGERMATCH-26JUL05MARNVS-M | 92 | 71m | 42/97-99/4994 | 98-99 | 5 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MARZAN-M | 88 | 33m | 0 | 94-95 | — | **NO_FLOW** | 91 |  |
| ATPCHALLENGERMATCH-26JUL05MELWAL-W | 63 | 67m | 70/70-95/5330 | 92-71 | 7 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05NIJBER-B | 15 | 1m | 0 | 61-28 | — | **NO_FLOW** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05PAPPAR-P | 14 | 64m | 179/2-46/29658 | 34-3 | -12 | **FLOW_AT_LEVEL** | 12 |  |
| ATPCHALLENGERMATCH-26JUL05PIELAR-L | 4 | 159m | 708/1-21/109667 | 19-1 | -3 | **FLOW_AT_LEVEL** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05POTANG-P | 52 | 51m | 6/54-55/228 | 54-55 | 2 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PRIROT-P | 86 | 49m | 99/79-96/7120 | 93-81 | -7 | **FLOW_AT_LEVEL** | 70 |  |
| ATPCHALLENGERMATCH-26JUL05RAQMAS-M | 9 | 70m | 0 | 9-11 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05RAQMAS-R | 88 | 70m | 1/89-89/250 | 88-89 | 1 | **FLOW_ABOVE** | 89 | REPRICEABLE→89 |
| ATPCHALLENGERMATCH-26JUL05RATRAH-R | 33 | 66m | 384/1-52/26621 | 21-1 | -32 | **FLOW_AT_LEVEL** | 36 |  |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 20 | 135m | 0 | 31-85 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 20 | 134m | 134/1-31/13364 | 12-1 | -19 | **FLOW_AT_LEVEL** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 17 | 129m | 125/1-31/13202 | 12-1 | -16 | **FLOW_AT_LEVEL** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-O | 81 | 50m | 2/82-82/132 | 81-82 | 1 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SCIORA-S | 19 | 45m | 0 | 19-21 | — | **NO_FLOW** | 17 |  |
| ATPCHALLENGERMATCH-26JUL05SEGHAB-H | 8 | 80m | 2/9-11/31 | 8-9 | 1 | **FLOW_ABOVE** | 6 | flow above but bound 6c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SEGHAB-S | 90 | 33m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ-S | 93 | 59m | 47/97-99/15876 | 99-99 | 4 | **FLOW_ABOVE** | 93 | flow above but bound 93c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SMIPIR-P | 58 | 98m | 352/80-99/31973 | 99-59 | 22 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05STEDIN-D | 71 | 10m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05STEDIN-S | 27 | 1m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SZYSTR-S | 53 | 51m | 2/56-56/308 | 53-57 | 3 | **FLOW_ABOVE** | 56 | REPRICEABLE→56 |
| ATPCHALLENGERMATCH-26JUL05SZYSTR-S | 43 | 59m | 16/46-47/1027 | 43-47 | 3 | **FLOW_ABOVE** | 43 | flow above but bound 43c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05TIXLEC-L | 80 | 13m | 3/81-84/59 | 80-84 | 1 | **FLOW_ABOVE** | 81 | REPRICEABLE→81 |
| ATPCHALLENGERMATCH-26JUL05TIXLEC-T | 19 | 140m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05UTADEV-D | 39 | 50m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05UTADEV-U | 59 | 50m | 2/60-61/9 | 60-61 | 1 | **FLOW_ABOVE** | 60 | REPRICEABLE→60 |
| ATPCHALLENGERMATCH-26JUL05VALREJ-R | 30 | 10m | 0 | 30-33 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05VALREJ-V | 67 | 3m | 0 | 67-70 | — | **NO_FLOW** | 70 |  |
| ATPCHALLENGERMATCH-26JUL05VILPUR-P | 80 | 0m | 0 | 80-83 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05VILPUR-V | 16 | 0m | 0 | 16-20 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05WEHIFI-I | 11 | 70m | 0 | 11-14 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05WEHIFI-W | 86 | 70m | 0 | 86-89 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL05AUGDAV-DAV | 34 | 75m | 20/39-40/1236 | 38-39 | 5 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05HURSTR-HUR | 73 | 51m | 12/74-74/281 | 73-74 | 1 | **FLOW_ABOVE** | 73 | flow above but bound 73c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05HURSTR-STR | 26 | 150m | 105/26-27/29782 | 26-27 | 0 | **FLOW_AT_LEVEL** | 26 |  |
| ATPMATCH-26JUL05SAFDJO-SAF | 12 | 50m | 39/15-16/10536 | 15-16 | 3 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05SINMOC-MOC | 3 | 150m | 37/4-4/8081 | 3-4 | 1 | **FLOW_ABOVE** | 3 | flow above but bound 3c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05SINMOC-SIN | 96 | 51m | 4/97-97/56 | 96-97 | 1 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05ELIAZO-AZO | 70 | 43m | 3/99-99/406 | 99-80 | 29 | **FLOW_ABOVE** | 79 | flow above but bound 79c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05MORHAU-MOR | 11 | 15m | 9/7-64/531 | 5-7 | -4 | **FLOW_AT_LEVEL** | 14 |  |
| ITFWMATCH-26JUL04BROKOI-BRO | 76 | 596m | 1350/80-99/350336 | 99-78 | 4 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 598m | 545/86-99/126759 | 99-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05SPIGAR-SPI | 96 | 28m | 0 | 99-99 | — | **NO_FLOW** | 94 |  |
| WTACHALLENGERMATCH-26JUL05BARPOP-B | 32 | 8m | 26/36-41/4579 | 41-35 | 4 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05BAYMAR-B | 25 | 70m | 0 | 25-28 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05BAYMAR-M | 71 | 70m | 1/75-75/5 | 72-75 | 4 | **FLOW_ABOVE** | 75 | REPRICEABLE→75 |
| WTACHALLENGERMATCH-26JUL05DITLEW-D | 31 | 68m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05DITLEW-L | 68 | 70m | 1/70-70/5 | 69-70 | 2 | **FLOW_ABOVE** | 70 | REPRICEABLE→70 |
| WTACHALLENGERMATCH-26JUL05MONGIM-G | 25 | 119m | 161/1-32/16236 | 26-1 | -24 | **FLOW_AT_LEVEL** | 26 |  |
| WTACHALLENGERMATCH-26JUL05MORKOT-K | 92 | 140m | 1/95-95/6 | 92-94 | 3 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| WTACHALLENGERMATCH-26JUL05MORKOT-M | 6 | 140m | 6/8-8/256 | 6-8 | 2 | **FLOW_ABOVE** | 5 | flow above but bound 5c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05MORNGU-M | 4 | 10m | 38/4-12/9747 | 3-4 | 0 | **FLOW_AT_LEVEL** | 5 |  |
| WTAMATCH-26JUL05BENGAU-BEN | 48 | 51m | 13/48-49/1292 | 48-49 | 0 | **FLOW_AT_LEVEL** | 46 |  |
| WTAMATCH-26JUL05BENGAU-GAU | 51 | 51m | 28/51-52/1946 | 51-52 | 0 | **FLOW_AT_LEVEL** | 52 |  |
| WTAMATCH-26JUL05MUCKRE-MUC | 59 | 72m | 35/62-64/4905 | 63-63 | 3 | **FLOW_ABOVE** | 59 | flow above but bound 59c < flow -- chasing breaks goal |
| WTAMATCH-26JUL05PEGJOV-JOV | 30 | 51m | 37/30-31/4826 | 30-31 | 0 | **FLOW_AT_LEVEL** | 29 |  |
| WTAMATCH-26JUL05PEGJOV-PEG | 70 | 51m | 31/70-71/3464 | 70-71 | 0 | **FLOW_AT_LEVEL** | 71 |  |
| WTAMATCH-26JUL05SABOSA-SAB | 66 | 9m | 8/68-69/620 | 68-69 | 2 | **FLOW_ABOVE** | 66 | flow above but bound 66c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN | 80 | 1 | **81** | 97 | -16 |
| ITFWMATCH-26JUL04BROKOI | 21 | 78 | **99** | 97 | +2 |
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |
| ITFWMATCH-26JUL05SPIGAR | 1 | 99 | **100** | 97 | +3 |
| WTACHALLENGERMATCH-26JUL05BARPOP | 65 | 35 | **100** | 97 | +3 |
| WTAMATCH-26JUL05SABOSA | 31 | 69 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05CARCER | 93 | 7 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05MARZAN | 6 | 95 | **101** | 97 | +4 |
| WTAMATCH-26JUL05MUCKRE | 38 | 63 | **101** | 97 | +4 |
| ATPMATCH-26JUL05SAFDJO | 85 | 16 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05LUZSAN | 19 | 82 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05MACBRA | 94 | 7 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05POTANG | 47 | 55 | **102** | 97 | +5 |
| ATPMATCH-26JUL05AUGDAV | 63 | 39 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05FRUSIN | 5 | 97 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05KUZMAT | 7 | 95 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05INGFEL | 25 | 77 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ | 4 | 99 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL05MARNVS | 5 | 99 | **104** | 97 | +7 |
| ATPCHALLENGERMATCH-26JUL05GOMMAJ | 80 | 24 | **104** | 97 | +7 |

## PATTERNS (sub-B) — 19
- half_arm_aging: KXITFWMATCH-26JUL04MAXSTE-MAX {"fill": 14, "age_min": 598, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL04BROKOI-KOI {"fill": 21, "age_min": 596, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"entry_minus_fv_burst": -34.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"fill": 80, "age_min": 590, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARZAN-ZAN {"fill": 6, "age_min": 261, "mode": "STARVATION(no prints since post)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL05KUDBOU-BOU {"entry_minus_fv_burst": -15.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05BERBOC-BOC {"entry_minus_fv_burst": -15.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05CRIRUB-CRI {"entry_minus_fv_burst": -21.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05RATRAH-RAH {"entry_minus_fv_burst": -17.5, "emitted_et": "2026-07-05 07:30:39 AM ET"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05DIACEC-CEC {"entry_minus_fv_burst": -19.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05POTANG-ANG {"fill": 47, "age_min": 94, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXATPMATCH-26JUL05AUGDAV-AUG {"fill": 63, "age_min": 75, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXWTAMATCH-26JUL05MUCKRE-KRE {"fill": 38, "age_min": 73, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARNVS-NVS {"fill": 5, "age_min": 72, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05SEYMAJ-MAJ {"fill": 4, "age_min": 59, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05FRUSIN-FRU {"fill": 5, "age_min": 53, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXATPMATCH-26JUL05SAFDJO-DJO {"fill": 85, "age_min": 50, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05KUZMAT-MAT {"fill": 7, "age_min": 32, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-05 07:30:39 AM ET"}
- deep_neg_fv: KXITFMATCH-26JUL05BOUDOU-BOU {"entry_minus_fv_burst": -14.0}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
