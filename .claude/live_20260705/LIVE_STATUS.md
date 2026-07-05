# LIVE VALIDATION — rolling status

- cycle 61 @ **2026-07-05 07:20:24 AM ET** | build `2bf6c90` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 49504 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 5 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 05:08:08 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05SCHDE | pair combined 99c > goal 97c |
| 06:39:12 | **walk_cap_breach** | KXATPCHALLENGERMATCH-26JUL05JANRYA-JAN | buy 94c > ceiling 81c (conception 78 + cap) ref=None |
| 06:54:48 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05JANRYA | pair combined 99c > goal 97c |
| 07:07:09 | **grace_breach** | KXATPCHALLENGERMATCH-26JUL05IEMBER-BER | fill 98c 5.1min past latch (grace 300s) |
| 07:07:09 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05IEMBER | pair combined 102c > goal 97c |

## FILLS — 68 graded (session)
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
| 05:22 | ATPCHALLENGERMATCH-26JUL05RATRAH-R | ATP_CHALL | leader | 58 | 58 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
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
| 06:16 | ATPCHALLENGERMATCH-26JUL05RATRAH-R | ATP_CHALL | underdog | 39 | 35 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
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

## RESTING BIDS — 80 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 37, 'NO_FLOW': 30, 'FLOW_AT_LEVEL': 13} | repriceable now: true 11 / false 69 | **cumulative bid_grade lines: 329 (repriceable true 37 / false 292)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05ALBZOR-A | 87 | 39m | 0 | 87-93 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05ALBZOR-Z | 6 | 40m | 0 | 6-13 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BASRIB-B | 36 | 59m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BASRIB-R | 56 | 59m | 1/62-62/39 | 59-63 | 6 | **FLOW_ABOVE** | 62 |  |
| ATPCHALLENGERMATCH-26JUL05CAMBID-B | 15 | 81m | 93/1-39/12505 | 1-2 | -14 | **FLOW_AT_LEVEL** | 14 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 6 | 40m | 0 | 6-7 | — | **NO_FLOW** | 5 |  |
| ATPCHALLENGERMATCH-26JUL05CARCER-C | 93 | 40m | 0 | 93-96 | — | **NO_FLOW** | 94 |  |
| ATPCHALLENGERMATCH-26JUL05CHESPE-C | 58 | 120m | 3/61-61/64 | 59-61 | 3 | **FLOW_ABOVE** | 61 | REPRICEABLE→61 |
| ATPCHALLENGERMATCH-26JUL05CHESPE-S | 39 | 120m | 1/42-42/10 | 39-42 | 3 | **FLOW_ABOVE** | 39 | flow above but bound 39c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05COVDEL-C | 28 | 70m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05COVDEL-D | 69 | 70m | 2/72-73/19 | 71-72 | 3 | **FLOW_ABOVE** | 72 | REPRICEABLE→72 |
| ATPCHALLENGERMATCH-26JUL05DALARI-A | 6 | 259m | 0 | 6-7 | — | **NO_FLOW** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 93 | 40m | 1/94-94/6 | 93-94 | 1 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05DESYEV-D | 29 | 9m | 0 | 29-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05DONGRE-D | 80 | 3m | 0 | 80-82 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05DONGRE-G | 19 | 40m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05FRUSIN-S | 92 | 43m | 31/93-99/3912 | 92-95 | 1 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05FRUSIN-S | 92 | 43m | 31/93-99/3912 | 92-95 | 1 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05GOMMAJ-M | 17 | 5m | 2/25-25/206 | 22-24 | 8 | **FLOW_ABOVE** | 17 | flow above but bound 17c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05INGFEL-F | 75 | 40m | 1/77-77/10 | 76-77 | 2 | **FLOW_ABOVE** | 77 | REPRICEABLE→77 |
| ATPCHALLENGERMATCH-26JUL05INGFEL-I | 25 | 28m | 0 | 25-26 | — | **NO_FLOW** | 21 |  |
| ATPCHALLENGERMATCH-26JUL05JANRYA-R | 1 | 14m | 45/1-6/8454 | 4-1 | 0 | **FLOW_AT_LEVEL** | 3 |  |
| ATPCHALLENGERMATCH-26JUL05KUZMAT-K | 90 | 22m | 0 | 93-95 | — | **NO_FLOW** | 90 |  |
| ATPCHALLENGERMATCH-26JUL05LUZSAN-S | 78 | 7m | 1/84-84/1 | 81-82 | 6 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MACBRA-B | 94 | 41m | 0 | 94-95 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05MACBRA-M | 6 | 10m | 0 | 6-7 | — | **NO_FLOW** | 3 |  |
| ATPCHALLENGERMATCH-26JUL05MARNVS-M | 92 | 61m | 42/97-99/4994 | 98-99 | 5 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MARZAN-M | 88 | 22m | 0 | 94-95 | — | **NO_FLOW** | 91 |  |
| ATPCHALLENGERMATCH-26JUL05MELWAL-W | 63 | 57m | 48/70-93/2364 | 86-71 | 7 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05NIJBER-B | 18 | 1m | 0 | 59-28 | — | **NO_FLOW** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05PAPPAR-P | 14 | 53m | 145/4-46/24011 | 34-4 | -10 | **FLOW_AT_LEVEL** | 12 |  |
| ATPCHALLENGERMATCH-26JUL05PIELAR-L | 4 | 149m | 708/1-21/109667 | 19-1 | -3 | **FLOW_AT_LEVEL** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05POTANG-P | 52 | 41m | 6/54-55/228 | 54-55 | 2 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PRIROT-P | 86 | 39m | 73/79-96/5414 | 93-81 | -7 | **FLOW_AT_LEVEL** | 70 |  |
| ATPCHALLENGERMATCH-26JUL05RAQMAS-M | 9 | 59m | 0 | 9-11 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05RAQMAS-R | 88 | 59m | 1/89-89/250 | 88-89 | 1 | **FLOW_ABOVE** | 89 | REPRICEABLE→89 |
| ATPCHALLENGERMATCH-26JUL05RATRAH-R | 33 | 55m | 290/16-52/20264 | 21-15 | -17 | **FLOW_AT_LEVEL** | 36 |  |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 20 | 124m | 0 | 31-85 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 20 | 123m | 134/1-31/13364 | 12-1 | -19 | **FLOW_AT_LEVEL** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 17 | 119m | 125/1-31/13202 | 12-1 | -16 | **FLOW_AT_LEVEL** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-O | 81 | 40m | 2/82-82/132 | 81-82 | 1 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SCIORA-S | 19 | 35m | 0 | 19-21 | — | **NO_FLOW** | 17 |  |
| ATPCHALLENGERMATCH-26JUL05SEGHAB-H | 8 | 70m | 2/9-11/31 | 8-9 | 1 | **FLOW_ABOVE** | 6 | flow above but bound 6c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SEGHAB-S | 90 | 23m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ-S | 93 | 48m | 47/97-99/15876 | 99-99 | 4 | **FLOW_ABOVE** | 93 | flow above but bound 93c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SMIPIR-P | 58 | 87m | 352/80-99/31973 | 99-59 | 22 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SZYSTR-S | 53 | 41m | 2/56-56/308 | 54-57 | 3 | **FLOW_ABOVE** | 56 | REPRICEABLE→56 |
| ATPCHALLENGERMATCH-26JUL05SZYSTR-S | 43 | 48m | 0 | 43-46 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05TIXLEC-L | 80 | 3m | 0 | 80-81 | — | **NO_FLOW** | 81 |  |
| ATPCHALLENGERMATCH-26JUL05TIXLEC-T | 19 | 130m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05UTADEV-D | 39 | 40m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05UTADEV-U | 59 | 40m | 2/60-61/9 | 60-61 | 1 | **FLOW_ABOVE** | 60 | REPRICEABLE→60 |
| ATPCHALLENGERMATCH-26JUL05WEHIFI-I | 11 | 59m | 0 | 11-14 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05WEHIFI-W | 86 | 59m | 0 | 86-89 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL05AUGDAV-DAV | 34 | 65m | 15/39-40/770 | 38-39 | 5 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05HURSTR-HUR | 73 | 41m | 10/74-74/279 | 73-74 | 1 | **FLOW_ABOVE** | 73 | flow above but bound 73c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05HURSTR-STR | 26 | 140m | 97/26-27/28783 | 26-27 | 0 | **FLOW_AT_LEVEL** | 26 |  |
| ATPMATCH-26JUL05SAFDJO-SAF | 12 | 40m | 30/16-16/9541 | 15-16 | 4 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05SINMOC-MOC | 3 | 140m | 34/4-4/7473 | 3-4 | 1 | **FLOW_ABOVE** | 3 | flow above but bound 3c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05SINMOC-SIN | 96 | 41m | 4/97-97/56 | 96-97 | 1 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05ELIAZO-AZO | 70 | 33m | 3/99-99/406 | 99-80 | 29 | **FLOW_ABOVE** | 79 | flow above but bound 79c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05MORHAU-MOR | 11 | 4m | 0 | 18-12 | — | **NO_FLOW** | 14 |  |
| ITFWMATCH-26JUL04BROKOI-BRO | 76 | 585m | 1350/80-99/350336 | 99-78 | 4 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 587m | 545/86-99/126759 | 99-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05SPIGAR-SPI | 96 | 18m | 0 | 99-99 | — | **NO_FLOW** | 94 |  |
| WTACHALLENGERMATCH-26JUL05BARPOP-B | 32 | 2m | 7/35-37/3040 | 33-34 | 3 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05BAYMAR-B | 25 | 59m | 0 | 25-28 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05BAYMAR-M | 71 | 59m | 1/75-75/5 | 72-75 | 4 | **FLOW_ABOVE** | 75 | REPRICEABLE→75 |
| WTACHALLENGERMATCH-26JUL05DITLEW-D | 31 | 58m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05DITLEW-L | 68 | 59m | 1/70-70/5 | 68-70 | 2 | **FLOW_ABOVE** | 70 | REPRICEABLE→70 |
| WTACHALLENGERMATCH-26JUL05MONGIM-G | 25 | 108m | 161/1-32/16236 | 26-1 | -24 | **FLOW_AT_LEVEL** | 26 |  |
| WTACHALLENGERMATCH-26JUL05MORKOT-K | 92 | 130m | 1/95-95/6 | 92-94 | 3 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| WTACHALLENGERMATCH-26JUL05MORKOT-M | 6 | 130m | 6/8-8/256 | 6-8 | 2 | **FLOW_ABOVE** | 5 | flow above but bound 5c < flow -- chasing breaks goal |
| WTAMATCH-26JUL05BENGAU-BEN | 48 | 41m | 10/49-49/1238 | 48-49 | 1 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| WTAMATCH-26JUL05BENGAU-GAU | 51 | 41m | 21/51-52/844 | 51-52 | 0 | **FLOW_AT_LEVEL** | 52 |  |
| WTAMATCH-26JUL05MUCKRE-MUC | 59 | 61m | 32/62-63/4849 | 62-63 | 3 | **FLOW_ABOVE** | 59 | flow above but bound 59c < flow -- chasing breaks goal |
| WTAMATCH-26JUL05PEGJOV-JOV | 30 | 41m | 31/30-31/4461 | 30-31 | 0 | **FLOW_AT_LEVEL** | 29 |  |
| WTAMATCH-26JUL05PEGJOV-PEG | 70 | 41m | 25/70-71/2531 | 70-71 | 0 | **FLOW_AT_LEVEL** | 71 |  |
| WTAMATCH-26JUL05SABOSA-OSA | 31 | 40m | 7/32-32/3186 | 31-32 | 1 | **FLOW_ABOVE** | 30 | flow above but bound 30c < flow -- chasing breaks goal |
| WTAMATCH-26JUL05SABOSA-SAB | 68 | 41m | 15/69-70/747 | 68-69 | 1 | **FLOW_ABOVE** | 69 | REPRICEABLE→69 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN | 80 | 1 | **81** | 97 | -16 |
| ITFWMATCH-26JUL04BROKOI | 21 | 78 | **99** | 97 | +2 |
| WTACHALLENGERMATCH-26JUL05BARPOP | 65 | 34 | **99** | 97 | +2 |
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05FRUSIN | 5 | 95 | **100** | 97 | +3 |
| ITFWMATCH-26JUL05SPIGAR | 1 | 99 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05MARZAN | 6 | 95 | **101** | 97 | +4 |
| WTAMATCH-26JUL05MUCKRE | 38 | 63 | **101** | 97 | +4 |
| ATPMATCH-26JUL05SAFDJO | 85 | 16 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05LUZSAN | 19 | 82 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05POTANG | 47 | 55 | **102** | 97 | +5 |
| ATPMATCH-26JUL05AUGDAV | 63 | 39 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05KUZMAT | 7 | 95 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ | 4 | 99 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL05MARNVS | 5 | 99 | **104** | 97 | +7 |
| ATPCHALLENGERMATCH-26JUL05GOMMAJ | 80 | 24 | **104** | 97 | +7 |

## PATTERNS (sub-B) — 17
- half_arm_aging: KXITFWMATCH-26JUL04MAXSTE-MAX {"fill": 14, "age_min": 587, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL04BROKOI-KOI {"fill": 21, "age_min": 585, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"entry_minus_fv_burst": -34.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"fill": 80, "age_min": 580, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARZAN-ZAN {"fill": 6, "age_min": 251, "mode": "STARVATION(no prints since post)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL05KUDBOU-BOU {"entry_minus_fv_burst": -15.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05BERBOC-BOC {"entry_minus_fv_burst": -15.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05CRIRUB-CRI {"entry_minus_fv_burst": -21.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05DIACEC-CEC {"entry_minus_fv_burst": -19.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05POTANG-ANG {"fill": 47, "age_min": 84, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXATPMATCH-26JUL05AUGDAV-AUG {"fill": 63, "age_min": 65, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXWTAMATCH-26JUL05MUCKRE-KRE {"fill": 38, "age_min": 62, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARNVS-NVS {"fill": 5, "age_min": 61, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05SEYMAJ-MAJ {"fill": 4, "age_min": 48, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05FRUSIN-FRU {"fill": 5, "age_min": 43, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXATPMATCH-26JUL05SAFDJO-DJO {"fill": 85, "age_min": 40, "mode": "SET_BELOW_FLOW(prints 4c above)", "emitted_et": "2026-07-05 07:20:24 AM ET"}
- deep_neg_fv: KXITFMATCH-26JUL05BOUDOU-BOU {"entry_minus_fv_burst": -14.0}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
