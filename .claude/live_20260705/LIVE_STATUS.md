# LIVE VALIDATION — rolling status

- cycle 78 @ **2026-07-05 10:16:04 AM ET** | build `2d1540e` | session boot 07-04 21:32 ET | log `live_v3_20260704.jsonl` | 128743 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 15 violation(s)
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
| 10:03:14 | **combined_over_goal** | KXITFWMATCH-26JUL05TUBSOB | pair combined 99c > goal 97c |
| 10:06:25 | **combined_over_goal** | KXITFWMATCH-26JUL05TRAABB | pair combined 98c > goal 97c |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_combined_over_goal.md**

## FILLS — 160 graded (session)
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
| 06:58 | ATPCHALLENGERMATCH-26JUL05KUZMAT-M | ATP_CHALL | underdog | 7 | 4 | +3 (place_cell) | 2.0 | pre | pair | 97 | MIXED |
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
| 07:21 | WTAMATCH-26JUL05SABOSA-OSA | WTA_MAIN | underdog | 31 | 28 | +3 (place_cell) | -0.5 | pre | pair | 100 | MIXED |
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
| 08:18 | ATPCHALLENGERMATCH-26JUL05UTADEV-U | ATP_CHALL | leader | 59 | 59 | +0 (place_cell) | 16.5 | pre | pair | 97 | GIFT_CLASS |
| 08:19 | ATPCHALLENGERMATCH-26JUL05CARCER-C | ATP_CHALL | underdog | 4 | 2 | +2 (place_cell) | -1.5 | pre | pair | 97 | EARNED |
| 08:23 | ATPCHALLENGERMATCH-26JUL05RAQMAS-R | ATP_CHALL | leader | 89 | 88 | +1 (place_cell) | — | pre | pair | 94 | GIFT_CLASS |
| 08:26 | ATPCHALLENGERMATCH-26JUL05RAQMAS-M | ATP_CHALL | underdog | 5 | 6 | -1 (place_cell) | — | pre | pair | 94 | EARNED |
| 08:26 | ATPCHALLENGERMATCH-26JUL05UTADEV-D | ATP_CHALL | underdog | 38 | 36 | +2 (place_cell) | -18.0 | pre | pair | 97 | EARNED |
| 08:30 | ITFWMATCH-26JUL05MONFER-FER | ITF_W | leader | 74 | 72 | +2 (place_cell) | — | pre | pair | 94 | MIXED |
| 08:30 | ITFMATCH-26JUL05RECDUB-DUB | ITF_M | underdog | 38 | 34 | +4 (place_cell) | -13.5 | pre | pair | 97 | EARNED |
| 08:32 | ITFWMATCH-26JUL05PRIYUL-PRI | ITF_W | leader | 89 | 75 | +14 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 08:33 | ATPCHALLENGERMATCH-26JUL05SEGHAB-H | ATP_CHALL | underdog | 1 | 5 | -4 (place_cell) | — | pre | pair | 91 | EARNED |
| 08:34 | ITFWMATCH-26JUL05MONFER-MON | ITF_W | ? | 20 | 16 | +4 (window_cell) | — | pre | pair | 94 | MIXED |
| 08:34 | ITFMATCH-26JUL05RECDUB-REC | ITF_M | ? | 59 | 64 | -5 (window_cell) | 18.0 | pre | pair | 97 | GIFT_CLASS |
| 08:37 | ITFWMATCH-26JUL05KUHEBE-EBE | ITF_W | underdog | 57 | 32 | +25 (place_cell) | — | pre | pair | 93 | EARNED |
| 08:39 | ATPCHALLENGERMATCH-26JUL05FELMOE-F | ATP_CHALL | leader | 76 | 75 | +1 (place_cell) | 16.5 | pre | pair | 97 | GIFT_CLASS |
| 08:41 | ITFWMATCH-26JUL05KUHEBE-KUH | ITF_W | underdog | 36 | 25 | +11 (place_cell) | — | pre | pair | 93 | EARNED |
| 08:45 | WTACHALLENGERMATCH-26JUL05BAYMAR-M | WTA_CHALL | leader | 71 | 71 | +0 (place_cell) | -22.5 | pre | pair | 99 | EARNED |
| 08:45 | ITFMATCH-26JUL05LENJON-JON | ITF_M | underdog | 22 | 14 | +8 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:46 | ATPMATCH-26JUL05SAFDJO-SAF | ATP_MAIN | underdog | 15 | 12 | +3 (place_cell) | -3.5 | pre | pair | 100 | EARNED |
| 08:46 | ATPCHALLENGERMATCH-26JUL05WEIHOE-H | ATP_CHALL | leader | 57 | 57 | +0 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 08:48 | WTAMATCH-26JUL05SABOSA-SAB | WTA_MAIN | leader | 69 | 68 | +1 (place_cell) | 0.5 | pre | pair | 100 | GIFT_CLASS |
| 08:49 | WTAMATCH-26JUL05MUCKRE-MUC | WTA_MAIN | ? | 72 | 63 | +9 (window_cell) | -1.5 | pre | pair | 110 | GIFT_CLASS |
| 08:49 | ATPMATCH-26JUL05HURSTR-STR | ATP_MAIN | ? | 26 | 25 | +1 (place_cell) | 0.0 | pre | single |  | MIXED |
| 08:50 | ITFWMATCH-26JUL05PRIYUL-YUL | ITF_W | underdog | 6 | 4 | +2 (place_cell) | — | pre | pair | 95 | EARNED |
| 08:53 | ITFMATCH-26JUL05LENJON-LEN | ITF_M | leader | 75 | 72 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:58 | ATPCHALLENGERMATCH-26JUL05SZYSTR-S | ATP_CHALL | ? | 53 | 53 | +0 (place_cell) | -45.0 | pre | pair | 96 | EARNED |
| 09:01 | ITFWMATCH-26JUL05ALVJOH-JOH | ITF_W | leader | 73 | 74 | -1 (place_cell) | 29.5 | pre | single |  | GIFT_CLASS |
| 09:01 | ITFWMATCH-26JUL05LIMHAG-HAG | ITF_W | underdog | 13 | 9 | +4 (place_cell) | — | pre | single |  | MIXED |
| 09:03 | ATPCHALLENGERMATCH-26JUL05SZYSTR-S | ATP_CHALL | underdog | 43 | 40 | +3 (place_cell) | 41.0 | pre | pair | 96 | EARNED |
| 09:05 | ATPCHALLENGERMATCH-26JUL05WEIHOE-W | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | pair | 96 | MIXED |
| 09:09 | ATPCHALLENGERMATCH-26JUL05VALREJ-R | ATP_CHALL | ? | 29 | 27 | +2 (place_cell) | — | pre | pair | 96 | EARNED |
| 09:13 | ITFWMATCH-26JUL05COHTSE-COH | ITF_W | underdog | 12 | 4 | +8 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:13 | ITFWMATCH-26JUL05DEKCAK-CAK | ITF_W | underdog | 25 | 22 | +3 (place_cell) | 9.0 | pre | single |  | EARNED |
| 09:14 | ATPCHALLENGERMATCH-26JUL05FELMOE-M | ATP_CHALL | underdog | 21 | 21 | +0 (place_cell) | -23.0 | pre | pair | 97 | EARNED |
| 09:18 | ATPCHALLENGERMATCH-26JUL05DESYEV-D | ATP_CHALL | underdog | 29 | 26 | +3 (place_cell) | -22.5 | pre | pair | 97 | EARNED |
| 09:20 | ITFMATCH-26JUL05SALCON-SAL | ITF_M | leader | 89 | 89 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 09:20 | ATPCHALLENGERMATCH-26JUL05BASRIB-R | ATP_CHALL | ? | 61 | 58 | +3 (place_cell) | 23.0 | pre | pair | 96 | GIFT_CLASS |
| 09:21 | ITFWMATCH-26JUL05AITDAE-AIT | ITF_W | underdog | 16 | 12 | +4 (place_cell) | — | pre | single |  | MIXED |
| 09:23 | ATPCHALLENGERMATCH-26JUL05SLABAS-B | ATP_CHALL | leader | 57 | 57 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:23 | ITFWMATCH-26JUL05BUYCOH-COH | ITF_W | underdog | 15 | 29 | -14 (place_cell) | — | pre | single |  | EARNED |
| 09:24 | ATPCHALLENGERMATCH-26JUL05BASRIB-B | ATP_CHALL | underdog | 35 | 34 | +1 (place_cell) | -19.5 | pre | pair | 96 | EARNED |
| 09:24 | WTACHALLENGERMATCH-26JUL05DITLEW-D | WTA_CHALL | underdog | 31 | 28 | +3 (place_cell) | -4.5 | pre | pair | 97 | EARNED |
| 09:24 | ATPCHALLENGERMATCH-26JUL05STEDIN-D | ATP_CHALL | leader | 71 | 71 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 09:26 | ITFWMATCH-26JUL05VARGRO-GRO | ITF_W | underdog | 13 | 8 | +5 (place_cell) | — | pre | single |  | MIXED |
| 09:27 | WTACHALLENGERMATCH-26JUL05DITLEW-L | WTA_CHALL | leader | 66 | 68 | -2 (place_cell) | 9.0 | pre | pair | 97 | GIFT_CLASS |
| 09:29 | WTACHALLENGERMATCH-26JUL05BAYMAR-B | WTA_CHALL | underdog | 28 | 22 | +6 (place_cell) | 23.5 | pre | pair | 99 | GIFT_CLASS |
| 09:32 | ATPCHALLENGERMATCH-26JUL05IVAGAN-I | ATP_CHALL | leader | 75 | 75 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 09:33 | ITFMATCH-26JUL05SHVFAU-SHV | ITF_M | underdog | 8 | 5 | +3 (place_cell) | — | pre | single |  | MIXED |
| 09:33 | ITFWMATCH-26JUL05COHTSE-TSE | ITF_W | leader | 85 | 86 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:34 | ATPCHALLENGERMATCH-26JUL05DESYEV-Y | ATP_CHALL | leader | 68 | 69 | -1 (place_cell) | 23.0 | pre | pair | 97 | GIFT_CLASS |
| 09:34 | ITFMATCH-26JUL05DELNIC-NIC | ITF_M | ? | 78 | 81 | -3 (window_cell) | -19.0 | 5.8 | pair | 101 | EARNED |
| 09:37 | ATPCHALLENGERMATCH-26JUL05KUZMAT-K | ATP_CHALL | leader | 90 | 92 | -2 (place_cell) | -7.0 | pre | pair | 97 | EARNED |
| 09:38 | ATPCHALLENGERMATCH-26JUL05RAMNEU-R | ATP_CHALL | underdog | 36 | 33 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:39 | ATPCHALLENGERMATCH-26JUL05WEHIFI-W | ATP_CHALL | leader | 88 | 86 | +2 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 09:44 | ATPCHALLENGERMATCH-26JUL05VILPUR-P | ATP_CHALL | leader | 81 | 80 | +1 (place_cell) | 27.5 | pre | single |  | GIFT_CLASS |
| 09:46 | ATPCHALLENGERMATCH-26JUL05RAMNEU-N | ATP_CHALL | ? | 61 | 61 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 09:46 | ATPCHALLENGERMATCH-26JUL05ILAPLU-I | ATP_CHALL | leader | 95 | 94 | +1 (place_cell) | — | pre | pair | 101 | GIFT_CLASS |
| 09:46 | ATPCHALLENGERMATCH-26JUL05ILAPLU-P | ATP_CHALL | underdog | 6 | 3 | +3 (place_cell) | — | pre | pair | 101 | MIXED |
| 09:56 | ATPCHALLENGERMATCH-26JUL05BLIPET-B | ATP_CHALL | underdog | 6 | 2 | +4 (place_cell) | — | pre | single |  | MIXED |
| 09:58 | ATPCHALLENGERMATCH-26JUL05WEHIFI-I | ATP_CHALL | underdog | 7 | 8 | -1 (place_cell) | — | pre | pair | 95 | EARNED |
| 10:03 | ITFWMATCH-26JUL05TUBSOB-TUB | ITF_W | leader | 72 | 73 | -1 (place_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 10:03 | ITFWMATCH-26JUL05TUBSOB-SOB | ITF_W | underdog | 27 | 23 | +4 (place_cell) | — | pre | pair | 99 | MIXED |
| 10:05 | ITFWMATCH-26JUL05TRAABB-TRA | ITF_W | underdog | 31 | 29 | +2 (place_cell) | — | pre | pair | 98 | EARNED |
| 10:06 | ITFWMATCH-26JUL05TRAABB-ABB | ITF_W | leader | 67 | 57 | +10 (place_cell) | — | pre | pair | 98 | GIFT_CLASS |
| 10:08 | ATPCHALLENGERMATCH-26JUL05DALARI-A | ATP_CHALL | underdog | 6 | 3 | +3 (place_cell) | -1.5 | pre | single |  | EARNED |
| 10:10 | ITFWMATCH-26JUL05MUNGAD-MUN | ITF_W | underdog | 42 | 28 | +14 (place_cell) | — | pre | pair | 97 | EARNED |
| 10:11 | ITFWMATCH-26JUL05MUNGAD-GAD | ITF_W | leader | 55 | 53 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 10:12 | ATPCHALLENGERMATCH-26JUL05SLABAS-S | ATP_CHALL | underdog | 40 | 36 | +4 (place_cell) | — | pre | pair | 97 | MIXED |

## RESTING BIDS — 89 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 36, 'FLOW_AT_LEVEL': 26, 'NO_FLOW': 27} | repriceable now: true 3 / false 86 | **cumulative bid_grade lines: 617 (repriceable true 55 / false 562)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05ALBZOR-A | 91 | 82m | 657/1-96/61078 | 15-1 | -90 | **FLOW_AT_LEVEL** | 91 |  |
| ATPCHALLENGERMATCH-26JUL05BINPOL-B | 59 | 75m | 1/60-60/95 | 59-60 | 1 | **FLOW_ABOVE** | 60 | REPRICEABLE→60 |
| ATPCHALLENGERMATCH-26JUL05BINPOL-P | 38 | 75m | 0 | 39-41 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BLIPET-P | 91 | 20m | 0 | 93-95 | — | **NO_FLOW** | 91 |  |
| ATPCHALLENGERMATCH-26JUL05CAMBID-B | 15 | 256m | 93/1-39/12505 | 1-2 | -14 | **FLOW_AT_LEVEL** | 14 |  |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | 69 | 138m | 3/71-72/25 | 69-71 | 2 | **FLOW_ABOVE** | 73 | REPRICEABLE→71 |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | 29 | 78m | 1/31-31/2 | 29-31 | 2 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05COVDEL-C | 27 | 127m | 152/1-27/13680 | 8-1 | -26 | **FLOW_AT_LEVEL** | 27 |  |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 91 | 7m | 123/94-96/4766 | 91-94 | 3 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05DONGRE-D | 78 | 156m | 96/83-99/12972 | 99-96 | 5 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05FRUSIN-S | 92 | 218m | 70/93-99/7782 | 99-97 | 1 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05FRUSIN-S | 92 | 218m | 70/93-99/7782 | 99-97 | 1 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05HIGZHU-H | 38 | 105m | 0 | 39-41 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05HIGZHU-Z | 58 | 105m | 1/61-61/10 | 59-61 | 3 | **FLOW_ABOVE** | 61 | REPRICEABLE→61 |
| ATPCHALLENGERMATCH-26JUL05HUANOC-H | 29 | 148m | 0 | 29-32 | — | **NO_FLOW** | 28 |  |
| ATPCHALLENGERMATCH-26JUL05HUANOC-N | 69 | 118m | 0 | 70-72 | — | **NO_FLOW** | 71 |  |
| ATPCHALLENGERMATCH-26JUL05HUEMAR-H | 61 | 15m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05HUEMAR-M | 31 | 14m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05INGFEL-F | 72 | 172m | 30/76-93/2135 | 92-93 | 4 | **FLOW_ABOVE** | 72 | flow above but bound 72c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05IVAGAN-G | 22 | 43m | 1/27-27/70 | 26-27 | 5 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05JANRYA-R | 1 | 190m | 51/1-6/10429 | 4-1 | 0 | **FLOW_AT_LEVEL** | 3 |  |
| ATPCHALLENGERMATCH-26JUL05KAMVAN-K | 13 | 79m | 0 | 13-14 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05KAMVAN-V | 87 | 166m | 0 | 87-88 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05KUZMAT-M | 5 | 27m | 104/2-8/24511 | 4-3 | -3 | **FLOW_AT_LEVEL** | 4 |  |
| ATPCHALLENGERMATCH-26JUL05MARHAI-H | 97 | 73m | 1/97-97/7 | 97-98 | 0 | **FLOW_AT_LEVEL** | 94 |  |
| ATPCHALLENGERMATCH-26JUL05MARHAI-M | 3 | 10m | 1/4-4/7 | 3-7 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05MARNVS-M | 92 | 237m | 43/97-99/5494 | 99-99 | 5 | **FLOW_ABOVE** | 92 | flow above but bound 92c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PAPPAR-P | 14 | 229m | 273/1-46/55921 | 34-1 | -13 | **FLOW_AT_LEVEL** | 12 |  |
| ATPCHALLENGERMATCH-26JUL05PARHAM-H | 90 | 156m | 29/97-99/5450 | 99-93 | 7 | **FLOW_ABOVE** | 90 | flow above but bound 90c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05PEROPI-O | 25 | 20m | 0 | 25-27 | — | **NO_FLOW** | 24 |  |
| ATPCHALLENGERMATCH-26JUL05PEROPI-P | 73 | 156m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PIELAR-L | 4 | 324m | 708/1-21/109667 | 19-1 | -3 | **FLOW_AT_LEVEL** | 6 |  |
| ATPCHALLENGERMATCH-26JUL05PRICOU-C | 51 | 15m | 0 | 51-53 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PRICOU-P | 47 | 15m | 0 | 47-48 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PRIROT-P | 86 | 214m | 378/79-99/90114 | 99-81 | -7 | **FLOW_AT_LEVEL** | 70 |  |
| ATPCHALLENGERMATCH-26JUL05RAMNEU-R | 36 | 9m | 8/36-50/215 | 40-39 | 0 | **FLOW_AT_LEVEL** | 35 |  |
| ATPCHALLENGERMATCH-26JUL05RATRAH-R | 33 | 231m | 385/1-52/26626 | 21-1 | -32 | **FLOW_AT_LEVEL** | 36 |  |
| ATPCHALLENGERMATCH-26JUL05RONRIB-R | 20 | 300m | 1/58-58/8 | 54-60 | 38 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05RYBTUN-R | 25 | 45m | 1/26-26/73 | 25-26 | 1 | **FLOW_ABOVE** | 23 | flow above but bound 23c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05RYBTUN-T | 73 | 45m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 20 | 299m | 134/1-31/13364 | 12-1 | -19 | **FLOW_AT_LEVEL** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCHDE-SC | 17 | 295m | 125/1-31/13202 | 12-1 | -16 | **FLOW_AT_LEVEL** | 20 |  |
| ATPCHALLENGERMATCH-26JUL05SCIORA-S | 16 | 126m | 116/1-26/11967 | 1-1 | -15 | **FLOW_AT_LEVEL** | 16 |  |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ-S | 93 | 224m | 47/97-99/15876 | 99-99 | 4 | **FLOW_ABOVE** | 93 | flow above but bound 93c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SMIPIR-P | 58 | 263m | 352/80-99/31973 | 99-59 | 22 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05STALOC-S | 70 | 153m | 18/99-99/1913 | 99-71 | 29 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05STEDIN-S | 26 | 29m | 116/28-60/4207 | 56-27 | 2 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05SUNBAR-B | 57 | 45m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05SUNBAR-S | 41 | 45m | 0 | 41-42 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05TENBER-B | 57 | 15m | 0 | 57-58 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05TENBER-T | 42 | 15m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05UTADEV-U | 59 | 101m | 416/12-88/29750 | 47-15 | -47 | **FLOW_AT_LEVEL** | 59 |  |
| ATPCHALLENGERMATCH-26JUL05VILPUR-V | 16 | 32m | 190/23-66/15985 | 44-44 | 7 | **FLOW_ABOVE** | 16 | flow above but bound 16c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05WALVAR-V | 3 | 6m | 0 | 3-4 | — | **NO_FLOW** | 2 |  |
| ATPCHALLENGERMATCH-26JUL05WALVAR-W | 97 | 145m | 3/98-98/128 | 97-98 | 1 | **FLOW_ABOVE** | 94 | flow above but bound 94c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05WEHIFI-I | 11 | 10m | 15/11-17/1078 | 10-13 | 0 | **FLOW_AT_LEVEL** | 9 |  |
| ATPCHALLENGERMATCH-26JUL05WEIHOE-W | 40 | 65m | 96/1-52/9436 | 1-2 | -39 | **FLOW_AT_LEVEL** | 37 |  |
| ATPMATCH-26JUL05AUGDAV-DAV | 38 | 94m | 86/39-41/23963 | 40-41 | 1 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05HURSTR-HUR | 71 | 86m | 71/73-77/193374 | 76-77 | 2 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ATPMATCH-26JUL05SINMOC-MOC | 3 | 315m | 151/3-4/32765 | 3-4 | 0 | **FLOW_AT_LEVEL** | 3 |  |
| ATPMATCH-26JUL05SINMOC-SIN | 96 | 94m | 32/96-97/5781 | 96-97 | 0 | **FLOW_AT_LEVEL** | 94 |  |
| ITFMATCH-26JUL05BONBRA-BON | 59 | 1m | 0 | 74-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL05BONBRA-BRA | 13 | 14m | 0 | 13-24 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL05ELIAZO-AZO | 70 | 208m | 3/99-99/406 | 99-80 | 29 | **FLOW_ABOVE** | 79 | flow above but bound 79c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05GELBRE-BRE | 42 | 18m | 2/54-55/17 | 42-54 | 12 | **FLOW_ABOVE** | 53 | flow above but bound 53c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05GELBRE-GEL | 44 | 60m | 4/52-57/25 | 44-53 | 8 | **FLOW_ABOVE** | 57 |  |
| ITFMATCH-26JUL05LENJON-JON | 20 | 79m | 266/1-23/16245 | 2-1 | -19 | **FLOW_AT_LEVEL** | 18 |  |
| ITFMATCH-26JUL05MORHAU-MOR | 11 | 180m | 83/1-64/5584 | 2-1 | -10 | **FLOW_AT_LEVEL** | 14 |  |
| ITFMATCH-26JUL05SABMIS-MIS | 1 | 15m | 0 | 17-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL05SALCON-CON | 8 | 48m | 210/15-37/17398 | 27-22 | 7 | **FLOW_ABOVE** | 8 | flow above but bound 8c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05SHVFAU-FAU | 89 | 43m | 119/94-99/8732 | 97-95 | 5 | **FLOW_ABOVE** | 89 | flow above but bound 89c < flow -- chasing breaks goal |
| ITFMATCH-26JUL05SHVFAU-FAU | 89 | 43m | 119/94-99/8732 | 97-95 | 5 | **FLOW_ABOVE** | 89 | flow above but bound 89c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04BROKOI-BRO | 76 | 761m | 1350/80-99/350336 | 99-78 | 4 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL04MAXSTE-STE | 83 | 763m | 545/86-99/126759 | 99-86 | 3 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05AITDAE-DAE | 81 | 75m | 28/82-94/787 | 88-89 | 1 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05BUYCOH-BUY | 80 | 52m | 42/86-98/1021 | 97-98 | 6 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05KUHEBE-EBE | 61 | 85m | 153/86-99/8262 | 99-99 | 25 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05KULVAN-KUL | 55 | 14m | 0 | 55-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL05KULVAN-VAN | 39 | 14m | 0 | 39-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL05MUNGAD-MUN | 42 | 4m | 25/54-60/1092 | 59-58 | 12 | **FLOW_ABOVE** | 42 | flow above but bound 42c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL05SPIGAR-SPI | 96 | 194m | 0 | 99-99 | — | **NO_FLOW** | 94 |  |
| ITFWMATCH-26JUL05VARGRO-VAR | 84 | 25m | 34/91-97/667 | 95-95 | 7 | **FLOW_ABOVE** | 84 | flow above but bound 84c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL05DITLEW-D | 31 | 30m | 146/13-47/41217 | 17-15 | -18 | **FLOW_AT_LEVEL** | 29 |  |
| WTACHALLENGERMATCH-26JUL05KOBLEW-K | 89 | 44m | 0 | 89-90 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05KOBLEW-L | 10 | 44m | 0 | 10-12 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05MONGIM-G | 25 | 284m | 161/1-32/16236 | 26-1 | -24 | **FLOW_AT_LEVEL** | 26 |  |
| WTACHALLENGERMATCH-26JUL05MORNGU-M | 4 | 175m | 121/1-12/34215 | 2-1 | -3 | **FLOW_AT_LEVEL** | 5 |  |
| WTAMATCH-26JUL05BENGAU-BEN | 48 | 94m | 36/48-49/3877 | 48-49 | 0 | **FLOW_AT_LEVEL** | 46 |  |
| WTAMATCH-26JUL05BENGAU-GAU | 51 | 94m | 103/51-52/7985 | 51-52 | 0 | **FLOW_AT_LEVEL** | 52 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL04LEGWIN | 80 | 1 | **81** | 97 | -16 |
| ATPCHALLENGERMATCH-26JUL05MARZAN | 6 | 89 | **95** | 97 | -2 |
| ITFWMATCH-26JUL05ALVJOH | 73 | 25 | **98** | 97 | +1 |
| ITFWMATCH-26JUL05DEKCAK | 25 | 73 | **98** | 97 | +1 |
| ATPCHALLENGERMATCH-26JUL05STEDIN | 71 | 27 | **98** | 97 | +1 |
| ITFWMATCH-26JUL04BROKOI | 21 | 78 | **99** | 97 | +2 |
| ITFWMATCH-26JUL04MAXSTE | 14 | 86 | **100** | 97 | +3 |
| ITFWMATCH-26JUL05SPIGAR | 1 | 99 | **100** | 97 | +3 |
| ITFWMATCH-26JUL05KARMAT | 1 | 99 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05DALARI | 6 | 94 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL05POTANG | 47 | 54 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05BLIPET | 6 | 95 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05FRUSIN | 5 | 97 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05IVAGAN | 75 | 27 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL05SEYMAJ | 4 | 99 | **103** | 97 | +6 |
| ATPMATCH-26JUL05HURSTR | 26 | 77 | **103** | 97 | +6 |
| ITFMATCH-26JUL05SHVFAU | 8 | 95 | **103** | 97 | +6 |
| ATPMATCH-26JUL05AUGDAV | 63 | 41 | **104** | 97 | +7 |
| ATPCHALLENGERMATCH-26JUL05MARNVS | 5 | 99 | **104** | 97 | +7 |
| ITFWMATCH-26JUL05LIMHAG | 13 | 92 | **105** | 97 | +8 |
| ITFWMATCH-26JUL05AITDAE | 16 | 89 | **105** | 97 | +8 |
| ITFWMATCH-26JUL05VARGRO | 13 | 95 | **108** | 97 | +11 |
| ITFMATCH-26JUL05SALCON | 89 | 22 | **111** | 97 | +14 |
| ITFWMATCH-26JUL05BUYCOH | 15 | 98 | **113** | 97 | +16 |
| ATPCHALLENGERMATCH-26JUL05DONGRE | 19 | 96 | **115** | 97 | +18 |
| ATPCHALLENGERMATCH-26JUL05CHESPE | 39 | 76 | **115** | 97 | +18 |
| ATPCHALLENGERMATCH-26JUL05INGFEL | 25 | 93 | **118** | 97 | +21 |
| ATPCHALLENGERMATCH-26JUL05VILPUR | 81 | 44 | **125** | 97 | +28 |

## PATTERNS (sub-B) — 50
- half_arm_aging: KXITFWMATCH-26JUL04MAXSTE-MAX {"fill": 14, "age_min": 763, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL04BROKOI-KOI {"fill": 21, "age_min": 761, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"entry_minus_fv_burst": -34.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL04LEGWIN-LEG {"fill": 80, "age_min": 756, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARZAN-ZAN {"fill": 6, "age_min": 427, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL05KUDBOU-BOU {"entry_minus_fv_burst": -15.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05BERBOC-BOC {"entry_minus_fv_burst": -15.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05CRIRUB-CRI {"entry_minus_fv_burst": -21.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05RATRAH-RAH {"entry_minus_fv_burst": -17.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05DIACEC-CEC {"entry_minus_fv_burst": -19.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05POTANG-ANG {"fill": 47, "age_min": 259, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05MELWAL-WAL {"entry_minus_fv_burst": -54.0}
- half_arm_aging: KXATPMATCH-26JUL05AUGDAV-AUG {"fill": 63, "age_min": 241, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05MARNVS-NVS {"fill": 5, "age_min": 237, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05NIJBER-BER {"entry_minus_fv_burst": -23.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05SEYMAJ-MAJ {"fill": 4, "age_min": 224, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05FRUSIN-FRU {"fill": 5, "age_min": 218, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- deep_neg_fv: KXITFMATCH-26JUL05BOUDOU-BOU {"entry_minus_fv_burst": -14.0}
- half_arm_aging: KXITFWMATCH-26JUL05SPIGAR-GAR {"fill": 1, "age_min": 195, "mode": "STARVATION(no prints since post)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05LUZSAN-LUZ {"entry_minus_fv_burst": -44.0}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL05BARPOP-POP {"entry_minus_fv_burst": -10.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05INGFEL-ING {"fill": 25, "age_min": 172, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05TIXLEC-LEC {"entry_minus_fv_burst": -12.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05DONGRE-GRE {"fill": 19, "age_min": 156, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05CHESPE-SPE {"fill": 39, "age_min": 155, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL05MORKOT-MOR {"entry_minus_fv_burst": -42.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05SCIORA-ORA {"entry_minus_fv_burst": -14.0}
- deep_neg_fv: KXWTAMATCH-26JUL05PEGJOV-JOV {"entry_minus_fv_burst": -24.5}
- half_arm_aging: KXITFWMATCH-26JUL05KARMAT-MAT {"fill": 1, "age_min": 124, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05ALBZOR-ZOR {"entry_minus_fv_burst": -31.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05UTADEV-DEV {"entry_minus_fv_burst": -18.0, "emitted_et": "2026-07-05 10:16:01 AM ET"}
- deep_neg_fv: KXITFMATCH-26JUL05RECDUB-DUB {"entry_minus_fv_burst": -13.5}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL05BAYMAR-MAR {"entry_minus_fv_burst": -22.5}
- half_arm_aging: KXATPMATCH-26JUL05HURSTR-STR {"fill": 26, "age_min": 86, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05SZYSTR-STR {"entry_minus_fv_burst": -45.0}
- half_arm_aging: KXITFWMATCH-26JUL05ALVJOH-JOH {"fill": 73, "age_min": 75, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL05LIMHAG-HAG {"fill": 13, "age_min": 75, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL05DEKCAK-CAK {"fill": 25, "age_min": 62, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05FELMOE-MOE {"entry_minus_fv_burst": -23.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05DESYEV-DES {"entry_minus_fv_burst": -22.5}
- half_arm_aging: KXITFMATCH-26JUL05SALCON-SAL {"fill": 89, "age_min": 56, "mode": "SET_BELOW_FLOW(prints 7c above)"}
- half_arm_aging: KXITFWMATCH-26JUL05AITDAE-AIT {"fill": 16, "age_min": 54, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL05BUYCOH-COH {"fill": 15, "age_min": 52, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL05BASRIB-BAS {"entry_minus_fv_burst": -19.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05STEDIN-DIN {"fill": 71, "age_min": 52, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFWMATCH-26JUL05VARGRO-GRO {"fill": 13, "age_min": 50, "mode": "SET_BELOW_FLOW(prints 7c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05IVAGAN-IVA {"fill": 75, "age_min": 43, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFMATCH-26JUL05SHVFAU-SHV {"fill": 8, "age_min": 43, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- deep_neg_fv: KXITFMATCH-26JUL05DELNIC-NIC {"entry_minus_fv_burst": -19.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL05VILPUR-PUR {"fill": 81, "age_min": 32, "mode": "SET_BELOW_FLOW(prints 7c above)", "emitted_et": "2026-07-05 10:16:01 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
