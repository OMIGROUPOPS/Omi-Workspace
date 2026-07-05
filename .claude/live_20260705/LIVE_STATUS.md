# LIVE VALIDATION — rolling status

- cycle 76 @ **2026-07-05 09:55:05 AM ET** | build `843f9bc` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 125053 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 13 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 05:08:08 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05SCHDE | pair combined 99c > goal 97c |
| 06:39:12 | **walk_cap_breach** | KXATPCHALLENGERMATCH-26JUL05JANRYA-JAN | buy 94c > ceiling 81c (conception 78 + cap) ref=None |
| 06:54:48 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05JANRYA | pair combined 99c > goal 97c |
| 07:07:09 | **grace_breach** | KXATPCHALLENGERMATCH-26JUL05IEMBER-BER | fill 98c 5.1min past latch (grace 300s) |
| 07:07:09 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05IEMBER | pair combined 102c > goal 97c |
| 07:54:36 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05COVDEL | pair combined 99c > goal 97c |
| 08:46:11 | **combined_over_goal** | KXATPMATCH-26JUL05SAFDJO | pair combined 100c > goal 97c |
| 08:48:48 | **combined_over_goal** | KXWTAMATCH-26JUL05SABOSA | pair combined 100c > goal 97c |
| 08:49:52 | **combined_over_goal** | KXWTAMATCH-26JUL05MUCKRE | pair combined 110c > goal 97c |
| 09:29:37 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL05BAYMAR | pair combined 99c > goal 97c |
| 09:34:56 | **grace_breach** | KXITFMATCH-26JUL05DELNIC-NIC | fill 78c 5.8min past latch (grace 300s) |
| 09:34:56 | **combined_over_goal** | KXITFMATCH-26JUL05DELNIC | pair combined 101c > goal 97c |
| 09:46:50 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL05ILAPLU | pair combined 101c > goal 97c |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_combined_over_goal.md**

## FILLS — 150 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 21:32 | ITFWMATCH-26JUL04MAXSTE-MAX | ITF_W | underdog | 14 | 10 | +4 (place_cell) | — | pre | single |  | MIXED |
| 21:34 | ITFWMATCH-26JUL04BROKOI-KOI | ITF_W | underdog | 21 | 18 | +3 (place_cell) | — | pre | single |  | MIXED |
| 21:40 | ATPCHALLENGERMATCH-26JUL04LEGWIN-L | ATP_CHALL | ? | 80 | 83 | -3 (window_cell) | -34.0 | pre | single |  | EARNED |
| 03:09 | ATPCHALLENGERMATCH-26JUL05MARZAN-Z | ATP_CHALL | underdog | 6 | 11 | -5 (place_cell) | 4.0 | pre | single |  | EARNED |
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
| 06:15 | ATPMATCH-26JUL05AUGDAV-AUG | ATP_MAIN | leader | 63 | 64 | -1 (place_cell) | 3.0 | pre | single |  | GIFT_CLASS |
| 06:16 | ATPCHALLENGERMATCH-26JUL05RATRAH-R | ATP_CHALL | underdog | 39 | 35 | +4 (place_cell) | 14.5 | pre | pair | 97 | GIFT_CLASS |
| 06:18 | WTAMATCH-26JUL05MUCKRE-KRE | WTA_MAIN | underdog | 38 | 37 | +1 (place_cell) | 1.5 | pre | pair | 110 | MIXED |
| 06:18 | ATPCHALLENGERMATCH-26JUL05PRIROT-R | ATP_CHALL | underdog | 27 | 28 | -1 (place_cell) | 17.5 | pre | pair | 97 | EARNED |
| 06:19 | ATPCHALLENGERMATCH-26JUL05MARNVS-N | ATP_CHALL | underdog | 5 | 2 | +3 (place_cell) | — | pre | single |  | MIXED |
| 06:26 | ATPCHALLENGERMATCH-26JUL05PAPPAR-P | ATP_CHALL | leader | 82 | 82 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 06:28 | ATPCHALLENGERMATCH-26JUL05NIJBER-B | ATP_CHALL | underdog | 23 | 20 | +3 (place_cell) | -23.0 | pre | pair | 97 | EARNED |
| 06:31 | ATPCHALLENGERMATCH-26JUL05SEYMAJ-M | ATP_CHALL | ? | 4 | 2 | +2 (place_cell) | — | pre | single |  | MIXED |
| 06:37 | ATPCHALLENGERMATCH-26JUL05FRUSIN-F | ATP_CHALL | underdog | 5 | 2 | +3 (place_cell) | — | pre | single |  | MIXED |
| 06:40 | ATPMATCH-26JUL05SAFDJO-DJO | ATP_MAIN | leader | 85 | 85 | +0 (place_cell) | 0.5 | pre | pair | 100 | GIFT_CLASS |
| 06:40 | ITFMATCH-26JUL05BOUDOU-DOU | ITF_M | leader | 75 | 75 | +0 (place_cell) | 13.0 | pre | pair | 97 | GIFT_CLASS |
| 06:40 | ITFMATCH-26JUL05ELIAZO-ELI | ITF_M | underdog | 18 | 14 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:40 | ATPCHALLENGERMATCH-26JUL05NIJBER-N | ATP_CHALL | ? | 74 | 74 | +0 (place_cell) | 39.5 | pre | pair | 97 | GIFT_CLASS |
| 06:41 | ITFMATCH-26JUL05ELIAZO-AZO | ITF_M | leader | 79 | 78 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:44 | ATPCHALLENGERMATCH-26JUL05JANRYA-R | ATP_CHALL | underdog | 5 | 2 | +3 (place_cell) | — | pre | pair | 99 | EARNED |
| 06:49 | ATPCHALLENGERMATCH-26JUL05PARHAM-H | ATP_CHALL | leader | 90 | 87 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 06:54 | ATPCHALLENGERMATCH-26JUL05JANRYA-J | ATP_CHALL | leader | 94 | 94 | +0 (place_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 06:58 | ATPCHALLENGERMATCH-26JUL05KUZMAT-M | ATP_CHALL | underdog | 7 | 4 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:58 | ITFMATCH-26JUL05BOUDOU-BOU | ITF_M | underdog | 22 | 15 | +7 (place_cell) | -14.0 | 3.9 | pair | 97 | EARNED |
| 07:01 | ATPCHALLENGERMATCH-26JUL05IEMBER-I | ATP_CHALL | underdog | 4 | 2 | +2 (place_cell) | 2.0 | pre | pair | 102 | MIXED |
| 07:01 | ITFWMATCH-26JUL05SPIGAR-GAR | ITF_W | underdog | 1 | 1 | +0 (place_cell) | — | pre | single |  | MIXED |
| 07:07 | ATPCHALLENGERMATCH-26JUL05IEMBER-B | ATP_CHALL | leader | 98 | 95 | +3 (place_cell) | -5.5 | 5.1 | pair | 102 | EARNED |
| 07:13 | ATPCHALLENGERMATCH-26JUL05LUZSAN-L | ATP_CHALL | ? | 19 | 16 | +3 (place_cell) | -44.0 | pre | pair | 97 | EARNED |
| 07:13 | ITFMATCH-26JUL05MORHAU-MOR | ITF_M | underdog | 6 | 2 | +4 (place_cell) | — | pre | pair | 89 | EARNED |
| 07:14 | ATPCHALLENGERMATCH-26JUL05STALOC-S | ATP_CHALL | leader | 94 | 94 | +0 (place_cell) | 18.5 | pre | pair | 97 | GIFT_CLASS |
| 07:14 | WTACHALLENGERMATCH-26JUL05MORNGU-M | WTA_CHALL | underdog | 6 | 3 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:15 | ATPCHALLENGERMATCH-26JUL05PARHAM-P | ATP_CHALL | underdog | 7 | 6 | +1 (place_cell) | — | pre | pair | 97 | EARNED |
| 07:15 | ITFMATCH-26JUL05MORHAU-HAU | ITF_M | leader | 83 | 56 | +27 (place_cell) | — | pre | pair | 89 | MIXED |
| 07:15 | ATPCHALLENGERMATCH-26JUL05GOMMAJ-G | ATP_CHALL | leader | 80 | 80 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 07:18 | WTACHALLENGERMATCH-26JUL05BARPOP-P | WTA_CHALL | leader | 65 | 63 | +2 (place_cell) | -10.5 | pre | pair | 97 | EARNED |
| 07:18 | ATPCHALLENGERMATCH-26JUL05STALOC-L | ATP_CHALL | underdog | 3 | 3 | +0 (place_cell) | -5.0 | 0.6 | pair | 97 | EARNED |
| 07:19 | WTACHALLENGERMATCH-26JUL05MORNGU-N | WTA_CHALL | leader | 91 | 91 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:21 | WTAMATCH-26JUL05SABOSA-OSA | WTA_MAIN | underdog | 31 | 28 | +3 (place_cell) | — | pre | pair | 100 | MIXED |
| 07:24 | ATPCHALLENGERMATCH-26JUL05INGFEL-I | ATP_CHALL | ? | 25 | 20 | +5 (place_cell) | — | pre | single |  | MIXED |
| 07:28 | ATPCHALLENGERMATCH-26JUL05CARCER-C | ATP_CHALL | leader | 93 | 92 | +1 (place_cell) | -1.0 | pre | pair | 97 | GIFT_CLASS |
| 07:30 | ATPCHALLENGERMATCH-26JUL05MACBRA-B | ATP_CHALL | leader | 94 | 94 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 07:31 | WTACHALLENGERMATCH-26JUL05BARPOP-B | WTA_CHALL | underdog | 32 | 30 | +2 (place_cell) | 10.5 | pre | pair | 97 | EARNED |
| 07:39 | ATPCHALLENGERMATCH-26JUL05TIXLEC-L | ATP_CHALL | leader | 80 | 77 | +3 (place_cell) | -12.5 | pre | pair | 97 | EARNED |
| 07:40 | ATPCHALLENGERMATCH-26JUL05DONGRE-G | ATP_CHALL | underdog | 19 | 16 | +3 (place_cell) | — | pre | single |  | MIXED |
| 07:40 | ATPCHALLENGERMATCH-26JUL05LUZSAN-S | ATP_CHALL | leader | 78 | 78 | +0 (place_cell) | 40.0 | pre | pair | 97 | GIFT_CLASS |
| 07:41 | ATPCHALLENGERMATCH-26JUL05CHESPE-S | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | 21.5 | pre | single |  | EARNED |
| 07:45 | WTACHALLENGERMATCH-26JUL05MORKOT-M | WTA_CHALL | underdog | 6 | 5 | +1 (place_cell) | -42.5 | pre | pair | 97 | EARNED |
| 07:45 | WTAMATCH-26JUL05PEGJOV-PEG | WTA_MAIN | leader | 70 | 70 | +0 (place_cell) | 21.5 | pre | pair | 97 | GIFT_CLASS |
| 07:48 | ATPCHALLENGERMATCH-26JUL05GOMMAJ-M | ATP_CHALL | underdog | 17 | 14 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 07:49 | ATPCHALLENGERMATCH-26JUL05SCIORA-O | ATP_CHALL | leader | 81 | 80 | +1 (place_cell) | -14.0 | pre | pair | 97 | EARNED |
| 07:50 | ATPCHALLENGERMATCH-26JUL05SEGHAB-S | ATP_CHALL | leader | 90 | 89 | +1 (place_cell) | — | pre | pair | 91 | GIFT_CLASS |
| 07:52 | WTACHALLENGERMATCH-26JUL05MORKOT-K | WTA_CHALL | leader | 91 | 92 | -1 (place_cell) | 48.0 | pre | pair | 97 | GIFT_CLASS |
| 07:53 | ATPCHALLENGERMATCH-26JUL05COVDEL-D | ATP_CHALL | leader | 68 | 69 | -1 (place_cell) | — | pre | pair | 99 | MIXED |
| 07:54 | ATPCHALLENGERMATCH-26JUL05VALREJ-V | ATP_CHALL | leader | 67 | 67 | +0 (place_cell) | — | pre | pair | 96 | MIXED |
| 07:54 | ATPCHALLENGERMATCH-26JUL05COVDEL-C | ATP_CHALL | underdog | 31 | 25 | +6 (place_cell) | — | pre | pair | 99 | MIXED |
| 08:01 | ITFMATCH-26JUL05DELNIC-DEL | ITF_M | underdog | 23 | 20 | +3 (place_cell) | 16.5 | pre | pair | 101 | GIFT_CLASS |
| 08:03 | ATPCHALLENGERMATCH-26JUL05TIXLEC-T | ATP_CHALL | ? | 17 | 16 | +1 (place_cell) | 11.5 | pre | pair | 97 | EARNED |
| 08:05 | ATPCHALLENGERMATCH-26JUL05SCIORA-S | ATP_CHALL | ? | 16 | 14 | +2 (place_cell) | 12.5 | pre | pair | 97 | EARNED |
| 08:08 | WTAMATCH-26JUL05PEGJOV-JOV | WTA_MAIN | underdog | 27 | 28 | -1 (place_cell) | -24.5 | pre | pair | 97 | EARNED |
| 08:12 | ITFWMATCH-26JUL05KARMAT-MAT | ITF_W | underdog | 1 | 1 | +0 (place_cell) | — | pre | single |  | MIXED |
| 08:13 | ATPCHALLENGERMATCH-26JUL05MACBRA-M | ATP_CHALL | ? | 3 | 2 | +1 (place_cell) | — | pre | pair | 97 | EARNED |
| 08:15 | ATPCHALLENGERMATCH-26JUL05ALBZOR-A | ATP_CHALL | leader | 91 | 86 | +5 (place_cell) | 33.5 | pre | pair | 97 | GIFT_CLASS |
| 08:16 | ATPCHALLENGERMATCH-26JUL05ALBZOR-Z | ATP_CHALL | underdog | 6 | 3 | +3 (place_cell) | -31.0 | pre | pair | 97 | EARNED |
| 08:18 | ATPCHALLENGERMATCH-26JUL05UTADEV-U | ATP_CHALL | leader | 59 | 59 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 08:19 | ATPCHALLENGERMATCH-26JUL05CARCER-C | ATP_CHALL | underdog | 4 | 2 | +2 (place_cell) | -1.5 | pre | pair | 97 | EARNED |
| 08:23 | ATPCHALLENGERMATCH-26JUL05RAQMAS-R | ATP_CHALL | leader | 89 | 88 | +1 (place_cell) | — | pre | pair | 94 | GIFT_CLASS |
| 08:26 | ATPCHALLENGERMATCH-26JUL05RAQMAS-M | ATP_CHALL | underdog | 5 | 6 | -1 (place_cell) | — | pre | pair | 94 | EARNED |
| 08:26 | ATPCHALLENGERMATCH-26JUL05UTADEV-D | ATP_CHALL | underdog | 38 | 36 | +2 (place_cell) | — | pre | pair | 97 | EARNED |
| 08:30 | ITFWMATCH-26JUL05MONFER-FER | ITF_W | leader | 74 | 72 | +2 (place_cell) | — | pre | pair | 94 | MIXED |
| 08:30 | ITFMATCH-26JUL05RECDUB-DUB | ITF_M | underdog | 38 | 34 | +4 (place_cell) | -13.5 | pre | pair | 97 | EARNED |
| 08:32 | ITFWMATCH-26JUL05PRIYUL-PRI | ITF_W | leader | 89 | 75 | +14 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 08:33 | ATPCHALLENGERMATCH-26JUL05SEGHAB-H | ATP_CHALL | underdog | 1 | 5 | -4 (place_cell) | — | pre | pair | 91 | EARNED |
| 08:34 | ITFWMATCH-26JUL05MONFER-MON | ITF_W | ? | 20 | 16 | +4 (window_cell) | — | pre | pair | 94 | MIXED |
| 08:34 | ITFMATCH-26JUL05RECDUB-REC | ITF_M | ? | 59 | 64 | -5 (window_cell) | 18.0 | pre | pair | 97 | GIFT_CLASS |
| 08:37 | ITFWMATCH-26JUL05KUHEBE-EBE | ITF_W | underdog | 57 | 32 | +25 (place_cell) | — | pre | pair | 93 | EARNED |
| 08:39 | ATPCHALLENGERMATCH-26JUL05FELMOE-F | ATP_CHALL | leader | 76 | 75 | +1 (place_cell) | 16.5 | pre | pair | 97 | GIFT_CLASS |
| 08:41 | ITFWMATCH-26JUL05KUHEBE-KUH | ITF_W | underdog | 36 | 25 | +11 (place_cell) | — | pre | pair | 93 | EARNED |
| 08:45 | WTACHALLENGERMATCH-26JUL05BAYMAR-M | WTA_CHALL | leader | 71 | 71 | +0 (place_cell) | — | pre | pair | 99 | MIXED |
| 08:45 | ITFMATCH-26JUL05LENJON-JON | ITF_M | underdog | 22 | 14 | +8 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:46 | ATPMATCH-26JUL05SAFDJO-SAF | ATP_MAIN | underdog | 15 | 12 | +3 (place_cell) | -3.5 | pre | pair | 100 | EARNED |
| 08:46 | ATPCHALLENGERMATCH-26JUL05WEIHOE-H | ATP_CHALL | leader | 57 | 57 | +0 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 08:48 | WTAMATCH-26JUL05SABOSA-SAB | WTA_MAIN | leader | 69 | 68 | +1 (place_cell) | — | pre | pair | 100 | GIFT_CLASS |
| 08:49 | WTAMATCH-26JUL05MUCKRE-MUC | WTA_MAIN | ? | 72 | 63 | +9 (window_cell) | -1.5 | pre | pair | 110 | GIFT_CLASS |
| 08:49 | ATPMATCH-26JUL05HURSTR-STR | ATP_MAIN | ? | 26 | 25 | +1 (place_cell) | 0.0 | pre | single |  | MIXED |
| 08:50 | ITFWMATCH-26JUL05PRIYUL-YUL | ITF_W | underdog | 6 | 4 | +2 (place_cell) | — | pre | pair | 95 | EARNED |
| 08:53 | ITFMATCH-26JUL05LENJON-LEN | ITF_M | leader | 75 | 72 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:58 | ATPCHALLENGERMATCH-26JUL05SZYSTR-S | ATP_CHALL | ? | 53 | 53 | +0 (place_cell) | — | pre | pair | 96 | MIXED |
| 09:01 | ITFWMATCH-26JUL05ALVJOH-JOH | ITF_W | leader | 73 | 74 | -1 (place_cell) | 29.5 | pre | single |  | GIFT_CLASS |
| 09:01 | ITFWMATCH-26JUL05LIMHAG-HAG | ITF_W | underdog | 13 | 9 | +4 (place_cell) | — | pre | single |  | MIXED |
| 09:03 | ATPCHALLENGERMATCH-26JUL05SZYSTR-S | ATP_CHALL | underdog | 43 | 40 | +3 (place_cell) | — | pre | pair | 96 | EARNED |
| 09:05 | ATPCHALLENGERMATCH-26JUL05WEIHOE-W | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | pair | 96 | MIXED |
| 09:09 | ATPCHALLENGERMATCH-26JUL05VALREJ-R | ATP_CHALL | ? | 29 | 27 | +2 (place_cell) | — | pre | pair | 96 | EARNED |
| 09:13 | ITFWMATCH-26JUL05COHTSE-COH | ITF_W | underdog | 12 | 4 | +8 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:13 | ITFWMATCH-26JUL05DEKCAK-CAK | ITF_W | underdog | 25 | 22 | +3 (place_cell) | 9.0 | pre | single |  | EARNED |
| 09:14 | ATPCHALLENGERMATCH-26JUL05FELMOE-M | ATP_CHALL | underdog | 21 | 21 | +0 (place_cell) | -23.0 | pre | pair | 97 | EARNED |
| 09:18 | ATPCHALLENGERMATCH-26JUL05DESYEV-D | ATP_CHALL | underdog | 29 | 26 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:20 | ITFMATCH-26JUL05SALCON-SAL | ITF_M | leader | 89 | 89 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 09:20 | ATPCHALLENGERMATCH-26JUL05BASRIB-R | ATP_CHALL | ? | 61 | 58 | +3 (place_cell) | 23.0 | pre | pair | 96 | GIFT_CLASS |
| 09:21 | ITFWMATCH-26JUL05AITDAE-AIT | ITF_W | underdog | 16 | 12 | +4 (place_cell) | — | pre | single |  | MIXED |
| 09:23 | ATPCHALLENGERMATCH-26JUL05SLABAS-B | ATP_CHALL | leader | 57 | 57 | +0 (place_cell) | — | pre | single |  | MIXED |
| 09:23 | ITFWMATCH-26JUL05BUYCOH-COH | ITF_W | underdog | 15 | 29 | -14 (place_cell) | — | pre | single |  | EARNED |
| 09:24 | ATPCHALLENGERMATCH-26JUL05BASRIB-B | ATP_CHALL | underdog | 35 | 34 | +1 (place_cell) | -19.5 | pre | pair | 96 | EARNED |
| 09:24 | WTACHALLENGERMATCH-26JUL05DITLEW-D | WTA_CHALL | underdog | 31 | 28 | +3 (place_cell) | -4.5 | pre | pair | 97 | EARNED |
| 09:24 | ATPCHALLENGERMATCH-26JUL05STEDIN-D | ATP_CHALL | leader | 71 | 71 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 09:26 | ITFWMATCH-26JUL05VARGRO-GRO | ITF_W | underdog | 13 | 8 | +5 (place_cell) | — | pre | single |  | MIXED |
| 09:27 | WTACHALLENGERMATCH-26JUL05DITLEW-L | WTA_CHALL | leader | 66 | 68 | -2 (place_cell) | 9.0 | pre | pair | 97 | GIFT_CLASS |
| 09:29 | WTACHALLENGERMATCH-26JUL05BAYMAR-B | WTA_CHALL | underdog | 28 | 22 | +6 (place_cell) | — | pre | pair | 99 | MIXED |
| 09:32 | ATPCHALLENGERMATCH-26JUL05IVAGAN-I | ATP_CHALL | leader | 75 | 75 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 09:33 | ITFMATCH-26JUL05SHVFAU-SHV | ITF_M | underdog | 8 | 5 | +3 (place_cell) | — | pre | single |  | MIXED |
| 09:33 | ITFWMATCH-26JUL05COHTSE-TSE | ITF_W | leader | 85 | 86 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:34 | ATPCHALLENGERMATCH-26JUL05DESYEV-Y | ATP_CHALL | leader | 68 | 69 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:34 | ITFMATCH-26JUL05DELNIC-NIC | ITF_M | ? | 78 | 81 | -3 (window_cell) | -19.0 | 5.8 | pair | 101 | EARNED |
| 09:37 | ATPCHALLENGERMATCH-26JUL05KUZMAT-K | ATP_CHALL | leader | 90 | 92 | -2 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:38 | ATPCHALLENGERMATCH-26JUL05RAMNEU-R | ATP_CHALL | underdog | 36 | 33 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:39 | ATPCHALLENGERMATCH-26JUL05WEHIFI-W | ATP_CHALL | leader | 88 | 86 | +2 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 09:44 | ATPCHALLENGERMATCH-26JUL05VILPUR-P | ATP_CHALL | leader | 81 | 80 | +1 (place_cell) | — | pre | single |  | MIXED |
| 09:46 | ATPCHALLENGERMATCH-26JUL05RAMNEU-N | ATP_CHALL | ? | 61 | 61 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 09:46 | ATPCHALLENGERMATCH-26JUL05ILAPLU-I | ATP_CHALL | leader | 95 | 94 | +1 (place_cell) | — | pre | pair | 101 | GIFT_CLASS |
| 09:46 | ATPCHALLENGERMATCH-26JUL05ILAPLU-P | ATP_CHALL | underdog | 6 | 3 | +3 (place_cell) | — | pre | pair | 101 | MIXED |

## RESTING BIDS — 83 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 38, 'NO_FLOW': 22, 'FLOW_AT_LEVEL': 23} | repriceable now: true 4 / false 79 | **cumulative bid_grade lines: 584 (repriceable true 54 / false 530)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05ALBZOR-A | 91 | 61m | 267/36-96/31945 | 79-37 | -55 | **FLOW_AT_LEVEL** | 91 |  |
| ATPCHALLENGERMATCH-26JUL05BASRIB-B | 36 | 17m | 13/53-61/1775 | 50-55 | 17 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05BINPOL-B | 59 | 54m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BINPOL-P | 38 | 54m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BLIPET-B | 6 | 7m | 0 | 6-7 | — | **NO_FLOW** | 3 |  |
| ATPCHALLENGERMATCH-26JUL05BLIPET-P | 94 | 114m | 0 | 94-95 | — | **NO_FLOW** | 94 |  |
| ATPCHALLENGERMATCH-26JUL05CAMBID-B | 15 | 235m | 93/1-39/12505 | 1-2 | -14 | **FLOW_AT_LEVEL** | 14 |  |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | 69 | 117m | 1/71-71/11 | 69-71 | 2 | **FLOW_ABOVE** | 73 | REPRICEABLE→71 |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | 29 | 58m | 0 | 29-31 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05COVDEL-C | 27 | 106m | 152/1-27/13680 | 8-1 | -26 | **FLOW_AT_LEVEL** | 27 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-A | 6 | 414m | 0 | 6-7 | — | **NO_FLOW** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 93 | 194m | 5/94-94/348 | 93-94 | 1 | **FLOW_ABOVE** | 94 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL05DESYEV-D | 29 | 19m | 89/39-71/13223 | 58-45 | 10 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05DONGRE-D | 78 | 135m | 96/83-99/12972 | 99-96 | 5 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05FRUSIN-S | 92 | 197m | 70/93-99/7782 | 99-97 | 1 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05FRUSIN-S | 92 | 197m | 70/93-99/7782 | 99-97 | 1 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05HIGZHU-H | 38 | 84m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05HIGZHU-Z | 58 | 84m | 1/61-61/10 | 59-60 | 3 | **FLOW_ABOVE** | 61 | REPRICEABLE→61 |
| ATPCHALLENGERMATCH-26JUL05HUANOC-H | 29 | 127m | 0 | 29-32 | — | **NO_FLOW** | 28 |  |
| ATPCHALLENGERMATCH-26JUL05HUANOC-N | 69 | 97m | 0 | 70-71 | — | **NO_FLOW** | 71 |  |
| ATPCHALLENGERMATCH-26JUL05INGFEL-F | 72 | 151m | 14/76-90/119 | 90-91 | 4 | **FLOW_ABOVE** | 72 | flow above but bound 72c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05IVAGAN-G | 22 | 22m | 1/27-27/70 | 26-27 | 5 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05JANRYA-R | 1 | 169m | 51/1-6/10429 | 4-1 | 0 | **FLOW_AT_LEVEL** | 3 |  |
| ATPCHALLENGERMATCH-26JUL05KAMVAN-K | 13 | 58m | 0 | 13-14 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05KAMVAN-V | 87 | 145m | 0 | 87-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05KUZMAT-M | 5 | 6m | 20/3-8/2793 | 7-3 | -2 | **FLOW_AT_LEVEL** | 4 |  |
| ATPCHALLENGERMATCH-26JUL05MARHAI-H | 97 | 52m | 0 | 97-98 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05MARHAI-M | 2 | 54m | 4/3-3/1106 | 2-4 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MARNVS-M | 92 | 216m | 43/97-99/5494 | 99-99 | 5 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PAPPAR-P | 14 | 208m | 273/1-46/55921 | 34-1 | -13 | **FLOW_AT_LEVEL** | 12 |  |
| ATPCHALLENGERMATCH-26JUL05PARHAM-H | 90 | 135m | 29/97-99/5450 | 99-93 | 7 | **FLOW_ABOVE** | 90 | flow above but bound 90c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PEROPI-O | 24 | 135m | 1/27-27/35 | 24-27 | 3 | **FLOW_ABOVE** | 24 | flow above but bound 24c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PEROPI-P | 73 | 135m | 0 | 73-76 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PIELAR-L | 4 | 303m | 708/1-21/109667 | 19-1 | -3 | **FLOW_AT_LEVEL** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05POTANG-P | 52 | 196m | 13/54-56/769 | 52-54 | 2 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PRIROT-P | 86 | 193m | 378/79-99/90114 | 99-81 | -7 | **FLOW_AT_LEVEL** | 70 |  |
| ATPCHALLENGERMATCH-26JUL05RATRAH-R | 33 | 210m | 385/1-52/26626 | 21-1 | -32 | **FLOW_AT_LEVEL** | 36 |  |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 20 | 279m | 0 | 53-58 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05RYBTUN-R | 25 | 24m | 1/26-26/73 | 25-26 | 1 | **FLOW_ABOVE** | 23 | flow above but bound 23c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05RYBTUN-T | 73 | 24m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 20 | 278m | 134/1-31/13364 | 12-1 | -19 | **FLOW_AT_LEVEL** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 17 | 274m | 125/1-31/13202 | 12-1 | -16 | **FLOW_AT_LEVEL** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-S | 16 | 105m | 116/1-26/11967 | 1-1 | -15 | **FLOW_AT_LEVEL** | 16 |  |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ-S | 93 | 203m | 47/97-99/15876 | 99-99 | 4 | **FLOW_ABOVE** | 93 | flow above but bound 93c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SLABAS-S | 40 | 31m | 0 | 44-46 | — | **NO_FLOW** | 39 |  |
| ATPCHALLENGERMATCH-26JUL05SMIPIR-P | 58 | 242m | 352/80-99/31973 | 99-59 | 22 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05STALOC-S | 70 | 132m | 18/99-99/1913 | 99-71 | 29 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05STEDIN-S | 26 | 8m | 38/38-56/1101 | 52-32 | 12 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SUNBAR-B | 57 | 24m | 0 | 57-58 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SUNBAR-S | 41 | 24m | 0 | 41-42 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05UTADEV-U | 59 | 80m | 189/38-88/13708 | 45-42 | -21 | **FLOW_AT_LEVEL** | 59 |  |
| ATPCHALLENGERMATCH-26JUL05VILPUR-V | 16 | 11m | 59/23-38/5473 | 32-25 | 7 | **FLOW_ABOVE** | 16 | flow above but bound 16c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05WALVAR-V | 2 | 124m | 4/3-3/326 | 2-3 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05WALVAR-W | 97 | 124m | 0 | 97-98 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05WEHIFI-I | 8 | 2m | 2/11-11/52 | 10-11 | 3 | **FLOW_ABOVE** | 9 | REPRICEABLE→9 |
| ATPCHALLENGERMATCH-26JUL05WEIHOE-W | 40 | 44m | 96/1-52/9436 | 1-2 | -39 | **FLOW_AT_LEVEL** | 37 |  |
| ATPMATCH-26JUL05AUGDAV-DAV | 38 | 73m | 62/39-41/21923 | 40-41 | 1 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05HURSTR-HUR | 71 | 65m | 50/73-76/192610 | 75-76 | 2 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05SINMOC-MOC | 3 | 294m | 134/3-4/30222 | 3-4 | 0 | **FLOW_AT_LEVEL** | 3 |  |
| ATPMATCH-26JUL05SINMOC-SIN | 96 | 73m | 25/96-97/5563 | 96-97 | 0 | **FLOW_AT_LEVEL** | 94 |  |
| ITFMATCH-26JUL05ELIAZO-AZO | 70 | 187m | 3/99-99/406 | 99-80 | 29 | **FLOW_ABOVE** | 79 | flow above but bound 79c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05GELBRE-BRE | 41 | 39m | 6/53-54/108 | 41-54 | 12 | **FLOW_ABOVE** | 53 |  |
| ITFMATCH-26JUL05GELBRE-GEL | 44 | 39m | 3/57-57/24 | 44-57 | 13 | **FLOW_ABOVE** | 57 |  |
| ITFMATCH-26JUL05LENJON-JON | 20 | 58m | 136/5-23/8288 | 8-5 | -15 | **FLOW_AT_LEVEL** | 18 |  |
| ITFMATCH-26JUL05MORHAU-MOR | 11 | 159m | 83/1-64/5584 | 2-1 | -10 | **FLOW_AT_LEVEL** | 14 |  |
| ITFMATCH-26JUL05SALCON-CON | 8 | 27m | 26/15-30/1185 | 28-16 | 7 | **FLOW_ABOVE** | 8 | flow above but bound 8c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05SHVFAU-FAU | 89 | 22m | 34/94-98/772 | 97-95 | 5 | **FLOW_ABOVE** | 89 | flow above but bound 89c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05SHVFAU-FAU | 89 | 22m | 34/94-98/772 | 97-95 | 5 | **FLOW_ABOVE** | 89 | flow above but bound 89c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04BROKOI-BRO | 76 | 740m | 1350/80-99/350336 | 99-78 | 4 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 742m | 545/86-99/126759 | 99-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05AITDAE-DAE | 81 | 54m | 5/86-87/38 | 81-87 | 5 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05BUYCOH-BUY | 80 | 31m | 17/86-95/249 | 92-94 | 6 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05KUHEBE-EBE | 61 | 64m | 153/86-99/8262 | 99-99 | 25 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05SPIGAR-SPI | 96 | 173m | 0 | 99-99 | — | **NO_FLOW** | 94 |  |
| ITFWMATCH-26JUL05VARGRO-VAR | 84 | 4m | 8/91-94/134 | 91-92 | 7 | **FLOW_ABOVE** | 84 | flow above but bound 84c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05BAYMAR-M | 69 | 18m | 52/80-92/4885 | 86-88 | 11 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05DITLEW-D | 31 | 9m | 35/26-47/5688 | 36-29 | -5 | **FLOW_AT_LEVEL** | 29 |  |
| WTACHALLENGERMATCH-26JUL05KOBLEW-K | 89 | 23m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05KOBLEW-L | 10 | 23m | 0 | 10-12 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05MONGIM-G | 25 | 263m | 161/1-32/16236 | 26-1 | -24 | **FLOW_AT_LEVEL** | 26 |  |
| WTACHALLENGERMATCH-26JUL05MORNGU-M | 4 | 154m | 121/1-12/34215 | 2-1 | -3 | **FLOW_AT_LEVEL** | 5 |  |
| WTAMATCH-26JUL05BENGAU-BEN | 48 | 73m | 23/48-49/3186 | 48-49 | 0 | **FLOW_AT_LEVEL** | 46 |  |
| WTAMATCH-26JUL05BENGAU-GAU | 51 | 73m | 75/51-52/5609 | 51-52 | 0 | **FLOW_AT_LEVEL** | 52 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN | 80 | 1 | **81** | 97 | -16 |
| ITFWMATCH-26JUL05DEKCAK | 25 | 73 | **98** | 97 | +1 |
| ITFWMATCH-26JUL04BROKOI | 21 | 78 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL05WEHIFI | 88 | 11 | **99** | 97 | +2 |
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |
| ITFWMATCH-26JUL05SPIGAR | 1 | 99 | **100** | 97 | +3 |
| ITFWMATCH-26JUL05KARMAT | 1 | 99 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05POTANG | 47 | 54 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05MARZAN | 6 | 96 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05FRUSIN | 5 | 97 | **102** | 97 | +5 |
| ATPMATCH-26JUL05HURSTR | 26 | 76 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05IVAGAN | 75 | 27 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ | 4 | 99 | **103** | 97 | +6 |
| ITFWMATCH-26JUL05AITDAE | 16 | 87 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL05SLABAS | 57 | 46 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL05STEDIN | 71 | 32 | **103** | 97 | +6 |
| ITFMATCH-26JUL05SHVFAU | 8 | 95 | **103** | 97 | +6 |
| ATPMATCH-26JUL05AUGDAV | 63 | 41 | **104** | 97 | +7 |
| ATPCHALLENGERMATCH-26JUL05MARNVS | 5 | 99 | **104** | 97 | +7 |
| ITFWMATCH-26JUL05LIMHAG | 13 | 92 | **105** | 97 | +8 |
| ITFMATCH-26JUL05SALCON | 89 | 16 | **105** | 97 | +8 |
| ITFWMATCH-26JUL05VARGRO | 13 | 92 | **105** | 97 | +8 |
| ATPCHALLENGERMATCH-26JUL05VILPUR | 81 | 25 | **106** | 97 | +9 |
| ITFWMATCH-26JUL05BUYCOH | 15 | 94 | **109** | 97 | +12 |
| ATPCHALLENGERMATCH-26JUL05DONGRE | 19 | 96 | **115** | 97 | +18 |
| ATPCHALLENGERMATCH-26JUL05CHESPE | 39 | 76 | **115** | 97 | +18 |
| ATPCHALLENGERMATCH-26JUL05INGFEL | 25 | 91 | **116** | 97 | +19 |
| ITFWMATCH-26JUL05ALVJOH | 73 | 51 | **124** | 97 | +27 |

## PATTERNS (sub-B) — 43
- half_arm_aging: KXITFWMATCH-26JUL04MAXSTE-MAX {"fill": 14, "age_min": 742, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL04BROKOI-KOI {"fill": 21, "age_min": 740, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"entry_minus_fv_burst": -34.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"fill": 80, "age_min": 735, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARZAN-ZAN {"fill": 6, "age_min": 406, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL05KUDBOU-BOU {"entry_minus_fv_burst": -15.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05BERBOC-BOC {"entry_minus_fv_burst": -15.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05CRIRUB-CRI {"entry_minus_fv_burst": -21.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05RATRAH-RAH {"entry_minus_fv_burst": -17.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05DIACEC-CEC {"entry_minus_fv_burst": -19.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05POTANG-ANG {"fill": 47, "age_min": 238, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05MELWAL-WAL {"entry_minus_fv_burst": -54.0}
- half_arm_aging: KXATPMATCH-26JUL05AUGDAV-AUG {"fill": 63, "age_min": 220, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARNVS-NVS {"fill": 5, "age_min": 216, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05NIJBER-BER {"entry_minus_fv_burst": -23.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05SEYMAJ-MAJ {"fill": 4, "age_min": 203, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05FRUSIN-FRU {"fill": 5, "age_min": 197, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- deep_neg_fv: KXITFMATCH-26JUL05BOUDOU-BOU {"entry_minus_fv_burst": -14.0}
- half_arm_aging: KXITFWMATCH-26JUL05SPIGAR-GAR {"fill": 1, "age_min": 174, "mode": "STARVATION(no prints since post)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05LUZSAN-LUZ {"entry_minus_fv_burst": -44.0}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL05BARPOP-POP {"entry_minus_fv_burst": -10.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05INGFEL-ING {"fill": 25, "age_min": 151, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05TIXLEC-LEC {"entry_minus_fv_burst": -12.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05DONGRE-GRE {"fill": 19, "age_min": 135, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05CHESPE-SPE {"fill": 39, "age_min": 134, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL05MORKOT-MOR {"entry_minus_fv_burst": -42.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05SCIORA-ORA {"entry_minus_fv_burst": -14.0}
- deep_neg_fv: KXWTAMATCH-26JUL05PEGJOV-JOV {"entry_minus_fv_burst": -24.5}
- half_arm_aging: KXITFWMATCH-26JUL05KARMAT-MAT {"fill": 1, "age_min": 103, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05ALBZOR-ZOR {"entry_minus_fv_burst": -31.0, "emitted_et": "2026-07-05 09:55:02 AM ET"}
- deep_neg_fv: KXITFMATCH-26JUL05RECDUB-DUB {"entry_minus_fv_burst": -13.5}
- half_arm_aging: KXATPMATCH-26JUL05HURSTR-STR {"fill": 26, "age_min": 65, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFWMATCH-26JUL05ALVJOH-JOH {"fill": 73, "age_min": 54, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL05LIMHAG-HAG {"fill": 13, "age_min": 54, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL05DEKCAK-CAK {"fill": 25, "age_min": 41, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05FELMOE-MOE {"entry_minus_fv_burst": -23.0}
- half_arm_aging: KXITFMATCH-26JUL05SALCON-SAL {"fill": 89, "age_min": 35, "mode": "SET_BELOW_FLOW(prints 7c above)", "emitted_et": "2026-07-05 09:55:02 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL05AITDAE-AIT {"fill": 16, "age_min": 33, "mode": "SET_BELOW_FLOW(prints 5c above)", "emitted_et": "2026-07-05 09:55:02 AM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05SLABAS-BAS {"fill": 57, "age_min": 31, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-05 09:55:02 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL05BUYCOH-COH {"fill": 15, "age_min": 31, "mode": "SET_BELOW_FLOW(prints 6c above)", "emitted_et": "2026-07-05 09:55:02 AM ET"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05BASRIB-BAS {"entry_minus_fv_burst": -19.5, "emitted_et": "2026-07-05 09:55:02 AM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05STEDIN-DIN {"fill": 71, "age_min": 31, "mode": "SET_BELOW_FLOW(prints 12c above)", "emitted_et": "2026-07-05 09:55:02 AM ET"}
- deep_neg_fv: KXITFMATCH-26JUL05DELNIC-NIC {"entry_minus_fv_burst": -19.0}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
