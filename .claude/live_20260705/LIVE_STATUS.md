# LIVE VALIDATION — rolling status

- cycle 121 @ **2026-07-06 07:23:44 AM ET** | build `3dfc70f` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 126806 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 15 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 23:50:46 | **walk_cap_breach** | KXITFWMATCH-26JUL06SIMCIR-SIM | buy 83c > ceiling 73c (conception 69 + cap) ref=join_bid |
| 00:30:15 | **walk_cap_breach** | KXITFWMATCH-26JUL06LUKNOE-LUK | buy 56c > ceiling 18c (conception 14 + cap) ref=join_bid |
| 00:31:45 | **walk_cap_breach** | KXITFMATCH-26JUL06ELDHAU-ELD | buy 58c > ceiling 20c (conception 16 + cap) ref=join_bid |
| 00:32:43 | **walk_cap_breach** | KXITFWMATCH-26JUL06WONIBR-IBR | buy 65c > ceiling 9c (conception 5 + cap) ref=join_bid |
| 00:54:46 | **walk_cap_breach** | KXITFWMATCH-26JUL06VLADIL-VLA | buy 38c > ceiling 31c (conception 27 + cap) ref=join_bid |
| 01:01:56 | **combined_over_goal** | KXITFWMATCH-26JUL06TODSAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 01:12:30 | **combined_over_goal** | KXITFWMATCH-26JUL06VAJRAM | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |
| 03:38:20 | **combined_over_goal** | KXITFWMATCH-26JUL06DZJMCK | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 05:04:30 | **combined_over_goal** | KXITFMATCH-26JUL06HERNAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 05:09:22 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL06HERNGU | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 06:24:17 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL06POTFEL | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |
| 06:29:40 | **combined_over_goal** | KXITFMATCH-26JUL06TSIAND | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |
| 06:40:21 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL06ERHSIN | pair combined 100c > goal 97c [organic: DEFECT-CLASS] |
| 06:55:43 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL06HESPAL | pair combined 102c > goal 97c [organic: DEFECT-CLASS] |
| 07:06:49 | **combined_over_goal** | KXITFMATCH-26JUL06DUHCAR | pair combined 100c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 171 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:51 | ITFWMATCH-26JUL06PASCOP-PAS | ITF_W | underdog | 12 | 8 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:51 | ITFWMATCH-26JUL06LUCGAD-GAD | ITF_W | underdog | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:52 | ITFWMATCH-26JUL06PASCOP-COP | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:59 | ITFWMATCH-26JUL06BRESAF-BRE | ITF_W | leader | 63 | 61 | +2 (place_cell) | 4.0 | pre | pair | 97 | GIFT_CLASS |
| 00:04 | ITFWMATCH-26JUL06SIMCIR-CIR | ITF_W | underdog | 16 | 12 | +4 (place_cell) | -30.0 | pre | pair | 97 | EARNED |
| 00:04 | ITFWMATCH-26JUL06SACLAZ-LAZ | ITF_W | underdog | 19 | 11 | +8 (place_cell) | -6.0 | pre | pair | 97 | EARNED |
| 00:05 | ITFWMATCH-26JUL06HOSFEH-FEH | ITF_W | underdog | 61 | 63 | -2 (place_cell) | — | pre | single |  | PENDING |
| 00:06 | ITFWMATCH-26JUL06VAJRAM-VAJ | ITF_W | leader | 82 | 74 | +8 (place_cell) | — | pre | pair | 101 | MIXED |
| 00:10 | ITFWMATCH-26JUL06LUCGAD-LUC | ITF_W | leader | 60 | 60 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:17 | ITFMATCH-26JUL06GENAZO-AZO | ITF_M | underdog | 16 | 9 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:22 | ITFMATCH-26JUL06VULCOU-COU | ITF_M | ? | 16 | 10 | +6 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:33 | ITFWMATCH-26JUL06WONIBR-IBR | ITF_W | leader | 65 | 52 | +13 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 00:33 | ITFWMATCH-26JUL06SIMCIR-SIM | ITF_W | leader | 81 | 81 | +0 (place_cell) | 26.5 | pre | pair | 97 | GIFT_CLASS |
| 00:34 | ITFWMATCH-26JUL06KARBAS-BAS | ITF_W | underdog | 26 | 26 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:47 | ITFWMATCH-26JUL06TODSAG-TOD | ITF_W | leader | 68 | 62 | +6 (place_cell) | — | pre | pair | 98 | MIXED |
| 00:55 | ITFWMATCH-26JUL06ZRNLUE-LUE | ITF_W | underdog | 69 | 6 | +63 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06VULCOU-VUL | ITF_M | leader | 81 | 80 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06BEASCO-SCO | ITF_M | underdog | 33 | 21 | +12 (place_cell) | — | pre | pair | 97 | MIXED |
| 01:01 | ITFWMATCH-26JUL06TODSAG-SAG | ITF_W | ? | 30 | 25 | +5 (place_cell) | — | pre | pair | 98 | MIXED |
| 01:05 | ITFWMATCH-26JUL06BRESAF-SAF | ITF_W | underdog | 34 | 32 | +2 (place_cell) | -6.5 | pre | pair | 97 | EARNED |
| 01:12 | ITFWMATCH-26JUL06VAJRAM-RAM | ITF_W | ? | 19 | 9 | +10 (place_cell) | — | pre | pair | 101 | MIXED |
| 01:22 | ITFWMATCH-26JUL06POPSOL-POP | ITF_W | underdog | 36 | 21 | +15 (place_cell) | — | pre | pair | 97 | EARNED |
| 01:23 | ITFMATCH-26JUL06GENAZO-GEN | ITF_M | leader | 81 | 73 | +8 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:44 | ATPCHALLENGERMATCH-26JUL06VILBOC-V | ATP_CHALL | leader | 75 | 72 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 01:51 | ATPCHALLENGERMATCH-26JUL06NIJRAH-R | ATP_CHALL | underdog | 40 | 37 | +3 (place_cell) | — | pre | pair | 96 | MIXED |
| 02:21 | ITFWMATCH-26JUL06WAGYOU-YOU | ITF_W | leader | 63 | 49 | +14 (place_cell) | — | pre | pair | 97 | MIXED |
| 03:05 | ITFWMATCH-26JUL06ZRNLUE-ZRN | ITF_W | ? | 28 | 2 | +26 (place_cell) | — | pre | pair | 97 | PENDING |
| 03:16 | ITFWMATCH-26JUL06BOIBOY-BOI | ITF_W | leader | 77 | 75 | +2 (place_cell) | — | pre | single |  | PENDING |
| 03:29 | ITFMATCH-26JUL06SALNGW-NGW | ITF_M | ? | 39 | 32 | +7 (place_cell) | — | pre | pair | 97 | MIXED |
| 03:31 | ITFWMATCH-26JUL06KULGON-GON | ITF_W | ? | 22 | 16 | +6 (place_cell) | — | pre | single |  | PENDING |
| 03:34 | ITFMATCH-26JUL06HERNAG-HER | ITF_M | ? | 70 | 49 | +21 (place_cell) | — | pre | pair | 98 | PENDING |
| 03:38 | ITFWMATCH-26JUL06DZJMCK-DZJ | ITF_W | leader | 77 | 41 | +36 (place_cell) | — | pre | pair | 99 | PENDING |
| 03:38 | ITFWMATCH-26JUL06DZJMCK-MCK | ITF_W | underdog | 22 | 12 | +10 (place_cell) | — | pre | pair | 99 | PENDING |
| 03:39 | ITFWMATCH-26JUL06JOSKUM-JOS | ITF_W | underdog | 67 | 79 | -12 (place_cell) | — | pre | pair | 95 | MIXED |
| 03:39 | ITFWMATCH-26JUL06HEDCHI-CHI | ITF_W | underdog | 51 | 20 | +31 (place_cell) | — | pre | pair | 95 | EARNED |
| 03:41 | ITFWMATCH-26JUL06VLADIL-VLA | ITF_W | underdog | 41 | 34 | +7 (place_cell) | 19.5 | pre | pair | 97 | GIFT_CLASS |
| 03:50 | ITFWMATCH-26JUL06HEDCHI-HED | ITF_W | underdog | 44 | 13 | +31 (place_cell) | — | pre | pair | 95 | MIXED |
| 03:55 | ITFMATCH-26JUL06SALNGW-SAL | ITF_M | leader | 58 | 48 | +10 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:00 | ATPCHALLENGERMATCH-26JUL06PRIORA-P | ATP_CHALL | leader | 56 | 54 | +2 (place_cell) | 2.5 | pre | pair | 95 | GIFT_CLASS |
| 04:01 | ITFMATCH-26JUL06LARJIM-LAR | ITF_M | underdog | 40 | 31 | +9 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:07 | ITFWMATCH-26JUL06DIANIK-NIK | ITF_W | leader | 52 | 49 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 04:09 | ATPCHALLENGERMATCH-26JUL06KRACRI-C | ATP_CHALL | underdog | 6 | 6 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:10 | ITFMATCH-26JUL06LARJIM-JIM | ITF_M | ? | 57 | 48 | +9 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:10 | ITFMATCH-26JUL06KASLIL-LIL | ITF_M | ? | 31 | 1 | +30 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:10 | ITFMATCH-26JUL06LAZVAC-VAC | ITF_M | underdog | 39 | 30 | +9 (place_cell) | — | pre | pair | 95 | PENDING |
| 04:11 | ATPCHALLENGERMATCH-26JUL06CAMDE-DE | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:12 | ITFWMATCH-26JUL06SACLAZ-SAC | ITF_W | leader | 78 | 73 | +5 (place_cell) | -3.0 | pre | pair | 97 | EARNED |
| 04:13 | ITFMATCH-26JUL06LAZVAC-LAZ | ITF_M | leader | 56 | 48 | +8 (place_cell) | — | pre | pair | 95 | PENDING |
| 04:13 | ATPCHALLENGERMATCH-26JUL06KRACRI-K | ATP_CHALL | leader | 91 | 89 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:16 | ITFMATCH-26JUL06KASLIL-KAS | ITF_M | underdog | 66 | 3 | +63 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:21 | ITFMATCH-26JUL06CASBAY-CAS | ITF_M | underdog | 45 | 2 | +43 (place_cell) | — | pre | single |  | MIXED |
| 04:36 | ITFWMATCH-26JUL06LUKNOE-LUK | ITF_W | leader | 69 | 72 | -3 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 04:44 | ITFWMATCH-26JUL06KARBAS-KAR | ITF_W | ? | 71 | 70 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:47 | ITFWMATCH-26JUL06LUKNOE-NOE | ITF_W | underdog | 26 | 27 | -1 (place_cell) | — | pre | pair | 95 | EARNED |
| 04:53 | WTAMATCH-26JUL06KRUKOS-KRU | WTA_MAIN | ? | 31 | 30 | +1 (place_cell) | 16.5 | pre | pair | 97 | GIFT_CLASS |
| 04:59 | ITFWMATCH-26JUL06DIANIK-DIA | ITF_W | underdog | 45 | 24 | +21 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:03 | ITFMATCH-26JUL06ELDHAU-ELD | ITF_M | leader | 65 | 56 | +9 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 05:04 | ITFMATCH-26JUL06HERNAG-NAG | ITF_M | ? | 28 | 1 | +27 (place_cell) | — | pre | pair | 98 | PENDING |
| 05:06 | ITFWMATCH-26JUL06OKUPRI-PRI | ITF_W | underdog | 41 | 25 | +16 (place_cell) | -45.5 | pre | pair | 97 | EARNED |
| 05:06 | ATPCHALLENGERMATCH-26JUL06VILBOC-B | ATP_CHALL | underdog | 22 | 21 | +1 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:07 | WTACHALLENGERMATCH-26JUL06OLIUCH-U | WTA_CHALL | underdog | 39 | 37 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:07 | WTACHALLENGERMATCH-26JUL06BOUKOT-K | WTA_CHALL | leader | 77 | 74 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 05:08 | ITFWMATCH-26JUL06TEISCH-TEI | ITF_W | ? | 86 | 51 | +35 (place_cell) | — | pre | pair | 90 | GIFT_CLASS |
| 05:09 | ITFWMATCH-26JUL06OKUPRI-OKU | ITF_W | leader | 56 | 49 | +7 (place_cell) | 44.0 | pre | pair | 97 | GIFT_CLASS |
| 05:09 | WTACHALLENGERMATCH-26JUL06HERNGU-H | WTA_CHALL | ? | 40 | 38 | +2 (place_cell) | — | pre | pair | 98 | EARNED |
| 05:09 | WTACHALLENGERMATCH-26JUL06HERNGU-N | WTA_CHALL | leader | 58 | 54 | +4 (place_cell) | — | pre | pair | 98 | GIFT_CLASS |
| 05:09 | WTACHALLENGERMATCH-26JUL06NOHBUR-B | WTA_CHALL | ? | 22 | 20 | +2 (place_cell) | -48.5 | pre | pair | 97 | EARNED |
| 05:09 | WTACHALLENGERMATCH-26JUL06BULSTR-S | WTA_CHALL | underdog | 29 | 23 | +6 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:09 | ITFWMATCH-26JUL06WAGYOU-WAG | ITF_W | underdog | 34 | 10 | +24 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:10 | WTACHALLENGERMATCH-26JUL06MONPOP-P | WTA_CHALL | ? | 54 | 51 | +3 (place_cell) | 36.0 | pre | pair | 97 | GIFT_CLASS |
| 05:10 | ATPCHALLENGERMATCH-26JUL06STALEC-S | ATP_CHALL | leader | 64 | 61 | +3 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 05:11 | ITFMATCH-26JUL06ELDHAU-HAU | ITF_M | underdog | 32 | 23 | +9 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:11 | ATPCHALLENGERMATCH-26JUL06CAMDE-CA | ATP_CHALL | leader | 58 | 56 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:11 | ITFWMATCH-26JUL06PIERAD-RAD | ITF_W | underdog | 33 | 18 | +15 (place_cell) | — | pre | single |  | PENDING |
| 05:12 | WTACHALLENGERMATCH-26JUL06NOHBUR-N | WTA_CHALL | leader | 75 | 73 | +2 (place_cell) | 37.0 | pre | pair | 97 | GIFT_CLASS |
| 05:12 | ATPCHALLENGERMATCH-26JUL06PAPJAN-P | ATP_CHALL | ? | 53 | 50 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 05:12 | WTACHALLENGERMATCH-26JUL06BULSTR-B | WTA_CHALL | ? | 68 | 68 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:13 | ITFWMATCH-26JUL06TRIVOR-VOR | ITF_W | leader | 89 | 49 | +40 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:15 | ITFWMATCH-26JUL06TRIVOR-TRI | ITF_W | ? | 8 | 1 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:15 | ITFWMATCH-26JUL06TEISCH-SCH | ITF_W | ? | 4 | 2 | +2 (place_cell) | — | pre | pair | 90 | EARNED |
| 05:16 | ITFWMATCH-26JUL06POPSOL-SOL | ITF_W | ? | 61 | 50 | +11 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:17 | ATPCHALLENGERMATCH-26JUL06STALEC-L | ATP_CHALL | underdog | 32 | 30 | +2 (place_cell) | — | pre | pair | 96 | EARNED |
| 05:18 | ITFMATCH-26JUL06LENTHE-THE | ITF_M | ? | 65 | 56 | +9 (place_cell) | — | pre | single |  | PENDING |
| 05:20 | WTACHALLENGERMATCH-26JUL06MONPOP-M | WTA_CHALL | underdog | 43 | 41 | +2 (place_cell) | -35.5 | pre | pair | 97 | EARNED |
| 05:22 | ATPCHALLENGERMATCH-26JUL06PRIORA-O | ATP_CHALL | ? | 39 | 37 | +2 (place_cell) | -5.0 | pre | pair | 95 | EARNED |
| 05:25 | ITFWMATCH-26JUL06RICMIT-MIT | ITF_W | ? | 9 | 3 | +6 (place_cell) | — | pre | single |  | MIXED |
| 05:26 | ATPMATCH-26JUL06DECOB-COB | ATP_MAIN | underdog | 23 | 22 | +1 (place_cell) | — | pre | single |  | MIXED |
| 05:28 | ITFWMATCH-26JUL06IVAKUH-KUH | ITF_W | ? | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:30 | ITFMATCH-26JUL06DUGHOF-HOF | ITF_M | ? | 21 | 6 | +15 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:31 | ITFWMATCH-26JUL06PEEPAH-PAH | ITF_W | ? | 58 | 6 | +52 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 05:32 | ITFWMATCH-26JUL06JOSKUM-KUM | ITF_W | underdog | 28 | 31 | -3 (place_cell) | — | pre | pair | 95 | EARNED |
| 05:32 | ATPCHALLENGERMATCH-26JUL06NIJRAH-N | ATP_CHALL | ? | 56 | 57 | -1 (window_cell) | — | pre | pair | 96 | MIXED |
| 05:32 | ITFWMATCH-26JUL06SPIMED-MED | ITF_W | ? | 8 | 1 | +7 (place_cell) | — | pre | pair | 96 | PENDING |
| 05:35 | ITFWMATCH-26JUL06GALTSE-GAL | ITF_W | leader | 77 | 71 | +6 (place_cell) | — | pre | single |  | PENDING |
| 05:38 | ITFWMATCH-26JUL06MILHER-HER | ITF_W | underdog | 16 | 3 | +13 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:39 | ATPCHALLENGERMATCH-26JUL06PIEMOL-P | ATP_CHALL | ? | 45 | 41 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:40 | ITFMATCH-26JUL06BEASCO-BEA | ITF_M | leader | 64 | 63 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:40 | ATPCHALLENGERMATCH-26JUL06SEYMAR-M | ATP_CHALL | underdog | 10 | 6 | +4 (place_cell) | — | pre | single |  | MIXED |
| 05:41 | ATPCHALLENGERMATCH-26JUL06POLHAI-P | ATP_CHALL | underdog | 31 | 28 | +3 (place_cell) | — | pre | single |  | PENDING |
| 05:41 | WTACHALLENGERMATCH-26JUL06LEWMAR-M | WTA_CHALL | ? | 43 | 40 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:41 | ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | ATP_CHALL | underdog | 26 | 23 | +3 (place_cell) | 20.5 | pre | pair | 97 | GIFT_CLASS |
| 05:42 | ATPCHALLENGERMATCH-26JUL06GOMLUZ-G | ATP_CHALL | ? | 71 | 68 | +3 (place_cell) | -26.5 | pre | pair | 97 | EARNED |
| 05:44 | ATPCHALLENGERMATCH-26JUL06DALCAR-C | ATP_CHALL | underdog | 3 | 2 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:45 | WTACHALLENGERMATCH-26JUL06BOUKOT-B | WTA_CHALL | underdog | 20 | 20 | +0 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:46 | ITFMATCH-26JUL06MEHCOU-COU | ITF_M | leader | 55 | 48 | +7 (place_cell) | — | pre | pair | 89 | PENDING |
| 05:51 | ATPCHALLENGERMATCH-26JUL06DALCAR-D | ATP_CHALL | leader | 94 | 93 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:51 | ITFMATCH-26JUL06SALBRE-SAL | ITF_M | leader | 90 | 86 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:52 | ITFWMATCH-26JUL06IVAKUH-IVA | ITF_W | ? | 60 | 59 | +1 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 05:54 | ITFMATCH-26JUL06ALEREG-ALE | ITF_M | leader | 51 | 48 | +3 (place_cell) | — | pre | single |  | PENDING |
| 05:56 | ITFWMATCH-26JUL06SPIMED-SPI | ITF_W | ? | 88 | 81 | +7 (place_cell) | — | pre | pair | 96 | PENDING |
| 05:57 | ITFWMATCH-26JUL06GANPUI-GAN | ITF_W | leader | 83 | 79 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:58 | ITFWMATCH-26JUL06KOTCHI-KOT | ITF_W | underdog | 52 | 21 | +31 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:58 | WTACHALLENGERMATCH-26JUL06OLIUCH-O | WTA_CHALL | leader | 58 | 57 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:02 | ITFWMATCH-26JUL06PEEPAH-PEE | ITF_W | underdog | 38 | 4 | +34 (place_cell) | — | pre | pair | 96 | MIXED |
| 06:05 | ITFMATCH-26JUL06TEXCAR-TEX | ITF_M | leader | 67 | 74 | -7 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:06 | ITFWMATCH-26JUL06KOTCHI-CHI | ITF_W | ? | 45 | 23 | +22 (window_cell) | — | pre | pair | 97 | MIXED |
| 06:06 | ITFWMATCH-26JUL06PODLUK-LUK | ITF_W | leader | 70 | 53 | +17 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:07 | ITFMATCH-26JUL06VANHOR-VAN | ITF_M | leader | 63 | 60 | +3 (place_cell) | — | pre | single |  | PENDING |
| 06:07 | ITFWMATCH-26JUL06KARVIS-VIS | ITF_W | ? | 21 | 8 | +13 (place_cell) | — | pre | single |  | PENDING |
| 06:09 | ITFWMATCH-26JUL06VLADIL-DIL | ITF_W | leader | 56 | 52 | +4 (place_cell) | -32.0 | pre | pair | 97 | EARNED |
| 06:09 | ATPMATCH-26JUL06DIMFER-FER | ATP_MAIN | underdog | 33 | 31 | +2 (place_cell) | — | pre | single |  | MIXED |
| 06:11 | ITFWMATCH-26JUL06ILIEBE-ILI | ITF_W | underdog | 45 | 37 | +8 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:11 | ATPCHALLENGERMATCH-26JUL06DELWAL-D | ATP_CHALL | underdog | 28 | 24 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:11 | ATPCHALLENGERMATCH-26JUL06BASHOE-H | ATP_CHALL | leader | 51 | 48 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 06:12 | WTAMATCH-26JUL06KRUKOS-KOS | WTA_MAIN | ? | 66 | 71 | -5 (window_cell) | -18.0 | pre | pair | 97 | EARNED |
| 06:12 | ATPCHALLENGERMATCH-26JUL06SEGBRA-B | ATP_CHALL | underdog | 36 | 33 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:14 | ITFMATCH-26JUL06TEXCAR-CAR | ITF_M | underdog | 30 | 32 | -2 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:15 | ITFWMATCH-26JUL06ILIEBE-EBE | ITF_W | ? | 52 | 49 | +3 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:15 | ITFWMATCH-26JUL06PACLOV-LOV | ITF_W | ? | 45 | 37 | +8 (place_cell) | — | pre | single |  | PENDING |
| 06:15 | ATPCHALLENGERMATCH-26JUL06POTFEL-P | ATP_CHALL | ? | 40 | 37 | +3 (place_cell) | — | pre | pair | 101 | MIXED |
| 06:15 | ITFMATCH-26JUL06MEHCOU-MEH | ITF_M | ? | 34 | 21 | +13 (place_cell) | — | pre | pair | 89 | PENDING |
| 06:18 | ATPCHALLENGERMATCH-26JUL06SEGBRA-S | ATP_CHALL | ? | 61 | 58 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 06:20 | ITFWMATCH-26JUL06GANPUI-PUI | ITF_W | underdog | 14 | 4 | +10 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:24 | ATPCHALLENGERMATCH-26JUL06POTFEL-F | ATP_CHALL | ? | 61 | 55 | +6 (place_cell) | — | pre | pair | 101 | GIFT_CLASS |
| 06:27 | ITFMATCH-26JUL06TSIAND-AND | ITF_M | underdog | 24 | 4 | +20 (place_cell) | — | pre | pair | 101 | PENDING |
| 06:29 | ITFMATCH-26JUL06TSIAND-TSI | ITF_M | ? | 77 | 4 | +73 (place_cell) | — | pre | pair | 101 | PENDING |
| 06:31 | ITFWMATCH-26JUL06EWAMAN-EWA | ITF_W | ? | 70 | 63 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:35 | WTACHALLENGERMATCH-26JUL06GRAMAS-M | WTA_CHALL | ? | 67 | 64 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 06:36 | ATPCHALLENGERMATCH-26JUL06MARHAM-H | ATP_CHALL | underdog | 5 | 3 | +2 (place_cell) | — | pre | pair | 96 | MIXED |
| 06:40 | ATPCHALLENGERMATCH-26JUL06ERHSIN-E | ATP_CHALL | ? | 96 | 92 | +4 (place_cell) | — | pre | pair | 100 | GIFT_CLASS |
| 06:40 | ATPCHALLENGERMATCH-26JUL06ERHSIN-S | ATP_CHALL | underdog | 4 | 2 | +2 (place_cell) | — | pre | pair | 100 | MIXED |
| 06:40 | ATPCHALLENGERMATCH-26JUL06ZORDEV-D | ATP_CHALL | ? | 42 | 39 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 06:41 | ITFMATCH-26JUL06HOSGAT-GAT | ITF_M | underdog | 38 | 34 | +4 (place_cell) | — | pre | single |  | PENDING |
| 06:43 | ATPCHALLENGERMATCH-26JUL06ZORDEV-Z | ATP_CHALL | leader | 55 | 53 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:43 | ATPCHALLENGERMATCH-26JUL06PIEMOL-M | ATP_CHALL | leader | 52 | 49 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:44 | ATPCHALLENGERMATCH-26JUL06DELWAL-W | ATP_CHALL | ? | 69 | 68 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:48 | ITFMATCH-26JUL06DUGHOF-DUG | ITF_M | ? | 76 | 51 | +25 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:48 | ATPCHALLENGERMATCH-26JUL06MARHAM-M | ATP_CHALL | ? | 91 | 91 | +0 (place_cell) | — | pre | pair | 96 | MIXED |
| 06:48 | WTACHALLENGERMATCH-26JUL06ROMSEM-S | WTA_CHALL | leader | 57 | 53 | +4 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 06:53 | WTACHALLENGERMATCH-26JUL06LEWMAR-L | WTA_CHALL | leader | 54 | 52 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:53 | ITFWMATCH-26JUL06MILHER-MIL | ITF_W | ? | 81 | 49 | +32 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:55 | WTACHALLENGERMATCH-26JUL06HESPAL-H | WTA_CHALL | ? | 33 | 26 | +7 (place_cell) | — | pre | pair | 102 | MIXED |
| 06:55 | WTACHALLENGERMATCH-26JUL06HESPAL-P | WTA_CHALL | leader | 69 | 66 | +3 (place_cell) | — | pre | pair | 102 | GIFT_CLASS |
| 06:57 | ATPCHALLENGERMATCH-26JUL06KUZSTR-S | ATP_CHALL | ? | 26 | 23 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:57 | ITFMATCH-26JUL06SALBRE-BRE | ITF_M | ? | 7 | 2 | +5 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:57 | ITFWMATCH-26JUL06PODLUK-POD | ITF_W | ? | 27 | 18 | +9 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:59 | ATPCHALLENGERMATCH-26JUL06RAQRIB-R | ATP_CHALL | leader | 61 | 61 | +0 (place_cell) | — | pre | single |  | MIXED |
| 07:02 | ATPCHALLENGERMATCH-26JUL06DONCIZ-C | ATP_CHALL | ? | 24 | 20 | +4 (place_cell) | — | pre | single |  | MIXED |
| 07:03 | ATPCHALLENGERMATCH-26JUL06CHEYEV-Y | ATP_CHALL | ? | 37 | 34 | +3 (place_cell) | — | pre | pair | 96 | MIXED |
| 07:06 | ITFMATCH-26JUL06DUHCAR-DUH | ITF_M | ? | 88 | 79 | +9 (place_cell) | — | pre | pair | 100 | PENDING |
| 07:06 | ITFMATCH-26JUL06DUHCAR-CAR | ITF_M | underdog | 12 | 5 | +7 (place_cell) | — | pre | pair | 100 | PENDING |
| 07:06 | ATPCHALLENGERMATCH-26JUL06CHEYEV-C | ATP_CHALL | ? | 59 | 58 | +1 (place_cell) | — | pre | pair | 96 | MIXED |
| 07:09 | ITFWMATCH-26JUL06EWAMAN-MAN | ITF_W | ? | 27 | 14 | +13 (place_cell) | — | pre | pair | 97 | PENDING |
| 07:10 | ATPCHALLENGERMATCH-26JUL06KUZSTR-K | ATP_CHALL | ? | 71 | 70 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:11 | WTAMATCH-26JUL06PAOEAL-PAO | WTA_MAIN | underdog | 39 | 37 | +2 (place_cell) | — | pre | single |  | MIXED |
| 07:14 | ATPCHALLENGERMATCH-26JUL06HUAPUR-H | ATP_CHALL | ? | 35 | 32 | +3 (place_cell) | — | pre | single |  | MIXED |
| 07:16 | ATPCHALLENGERMATCH-26JUL06MARBER-B | ATP_CHALL | ? | 58 | 55 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 07:18 | ITFMATCH-26JUL06TIMJEF-TIM | ITF_M | ? | 20 | 15 | +5 (place_cell) | — | pre | single |  | PENDING |
| 07:18 | ITFWMATCH-26JUL06POZMLA-MLA | ITF_W | ? | 8 | 1 | +7 (place_cell) | — | pre | single |  | PENDING |
| 07:20 | ATPCHALLENGERMATCH-26JUL06MARBER-M | ATP_CHALL | ? | 39 | 37 | +2 (place_cell) | — | pre | pair | 97 | EARNED |
| 07:22 | WTAMATCH-26JUL06BOUMER-BOU | WTA_MAIN | underdog | 47 | 43 | +4 (place_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 210 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 21, 'NO_FLOW': 127, 'FLOW_ABOVE': 62} | repriceable now: true 22 / false 188 | **cumulative bid_grade lines: 1941 (repriceable true 193 / false 1748)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06BARDAL-B | 56 | 142m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06BARDAL-D | 41 | 142m | 1/42-42/20 | 42-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06BARZIN-B | 52 | 22m | 0 | 52-54 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06BARZIN-Z | 45 | 22m | 0 | 47-48 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06BASHOE-B | 46 | 72m | 1/51-51/174 | 50-51 | 5 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06BASHOE-B | 46 | 16m | 1/51-51/174 | 50-51 | 5 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06CHADEM-C | 48 | 143m | 0 | 48-51 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CHADEM-D | 49 | 20m | 0 | 51-52 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CHIJAN-C | 77 | 12m | 0 | 77-78 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CHIJAN-J | 23 | 140m | 0 | 23-24 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CLAPAP-C | 72 | 22m | 0 | 74-75 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CLAPAP-P | 26 | 22m | 0 | 26-28 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DAMHUE-D | 79 | 143m | 1/80-80/30 | 79-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ATPCHALLENGERMATCH-26JUL06DAMHUE-H | 19 | 143m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DEHUD-DE | 38 | 142m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DEHUD-HU | 61 | 142m | 0 | 61-62 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-D | 73 | 21m | 0 | 77-79 | — | **NO_FLOW** | 73 |  |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-D | 73 | 20m | 0 | 77-79 | — | **NO_FLOW** | 73 |  |
| ATPCHALLENGERMATCH-26JUL06FOMDHA-D | 52 | 143m | 0 | 52-54 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06FOMDHA-F | 45 | 143m | 2/46-46/39 | 45-46 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | 23 | 91m | 149/1-25/45244 | 2-1 | -22 | **FLOW_AT_LEVEL** | 23 |  |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-P | 61 | 293m | 5/67-69/134 | 67-80 | 6 | **FLOW_ABOVE** | 62 | flow above but bound 62c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-P | 62 | 7m | 0 | 67-80 | — | **NO_FLOW** | 62 |  |
| ATPCHALLENGERMATCH-26JUL06HUETEN-H | 60 | 22m | 0 | 67-71 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HUETEN-T | 28 | 22m | 0 | 28-33 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ILARYB-I | 52 | 21m | 0 | 52-55 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ILARYB-R | 45 | 21m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-D | 20 | 233m | 5/20-21/547 | 20-21 | 0 | **FLOW_AT_LEVEL** | 18 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-I | 80 | 94m | 0 | 80-82 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KASCIN-C | 54 | 113m | 1/56-56/5 | 55-56 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ATPCHALLENGERMATCH-26JUL06KASCIN-K | 43 | 113m | 1/44-44/31 | 43-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ATPCHALLENGERMATCH-26JUL06KOZJOH-J | 30 | 20m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KOZJOH-K | 66 | 20m | 0 | 66-69 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 5 | 189m | 338/1-21/41967 | 19-1 | -4 | **FLOW_AT_LEVEL** | 5 |  |
| ATPCHALLENGERMATCH-26JUL06KYMFAU-F | 32 | 112m | 0 | 32-33 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KYMFAU-K | 67 | 102m | 1/68-68/28 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPCHALLENGERMATCH-26JUL06MAXGHI-G | 55 | 53m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MAXGHI-M | 43 | 53m | 0 | 43-45 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06OLIDAN-D | 64 | 22m | 3/66-66/20 | 65-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ATPCHALLENGERMATCH-26JUL06OLIDAN-O | 34 | 22m | 0 | 34-36 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06OPIPET-O | 28 | 94m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06OPIPET-P | 71 | 203m | 1/72-72/5 | 71-72 | 1 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PAPMID-M | 51 | 20m | 0 | 51-52 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PAPMID-P | 47 | 20m | 2/49-49/43 | 47-49 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→49 |
| ATPCHALLENGERMATCH-26JUL06POLHAI-H | 66 | 102m | 2/72-72/105 | 72-73 | 6 | **FLOW_ABOVE** | 66 | flow above but bound 66c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06POLHAI-H | 66 | 20m | 1/72-72/100 | 72-73 | 6 | **FLOW_ABOVE** | 66 | flow above but bound 66c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06POPSAN-P | 90 | 17m | 0 | 90-95 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POPSAN-S | 5 | 20m | 0 | 6-7 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 36 | 25m | 56/40-63/8415 | 60-46 | 4 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06REHKOU-K | 44 | 113m | 6/45-45/920 | 44-45 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ATPCHALLENGERMATCH-26JUL06REHKOU-R | 55 | 94m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-B | 36 | 30m | 50/36-74/13081 | 59-66 | 0 | **FLOW_AT_LEVEL** | 34 |  |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 94m | 111/1-60/13885 | 4-1 | -32 | **FLOW_AT_LEVEL** | 33 |  |
| ATPCHALLENGERMATCH-26JUL06VALZHU-V | 71 | 233m | 2/73-73/22 | 71-74 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ATPCHALLENGERMATCH-26JUL06VALZHU-Z | 27 | 233m | 2/29-29/81 | 27-29 | 2 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06WALNEU-N | 28 | 201m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06WALNEU-W | 70 | 203m | 1/73-73/5 | 70-73 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ATPCHALLENGERMATCH-26JUL06WEHVAN-V | 42 | 163m | 1/43-43/0 | 42-43 | 1 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06WEHVAN-W | 57 | 94m | 8/58-60/471 | 57-59 | 1 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06WEIGRA-G | 81 | 52m | 0 | 81-82 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06WEIGRA-W | 18 | 53m | 0 | 18-19 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL06DECOB-DE | 74 | 117m | 50/78-79/3597 | 78-79 | 4 | **FLOW_ABOVE** | 74 | flow above but bound 74c < flow -- chasing breaks goal |
| ATPMATCH-26JUL06DECOB-DE | 74 | 52m | 21/78-79/1024 | 78-79 | 4 | **FLOW_ABOVE** | 74 | flow above but bound 74c < flow -- chasing breaks goal |
| ATPMATCH-26JUL06DIMFER-DIM | 64 | 74m | 32/67-68/1732 | 67-68 | 3 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ATPMATCH-26JUL06DIMFER-DIM | 64 | 16m | 10/68-68/222 | 67-68 | 4 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06ALEREG-REG | 40 | 200m | 99/49-99/9602 | 99-99 | 9 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06ALIMIS-ALI | 91 | 181m | 0 | 91-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-MIS | 6 | 291m | 0 | 6-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BONFAU-BON | 66 | 94m | 0 | 66-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BONFAU-FAU | 26 | 78m | 0 | 26-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BROTHU-BRO | 36 | 22m | 0 | 36-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BROTHU-THU | 54 | 19m | 0 | 54-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DONDEV-DEV | 20 | 20m | 0 | 20-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DONDEV-DON | 69 | 23m | 0 | 69-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GANVER-GAN | 20 | 30m | 7/52-53/108 | 46-53 | 32 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06GANVER-VER | 48 | 87m | 0 | 48-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GARCIO-CIO | 39 | 204m | 1/43-43/22 | 39-44 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFMATCH-26JUL06GARCIO-GAR | 56 | 211m | 2/59-61/15 | 56-61 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 352m | 213/1-19/18095 | 18-1 | -15 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06HOSGAT-HOS | 56 | 177m | 24/62-93/1652 | 59-67 | 6 | **FLOW_ABOVE** | 59 | flow above but bound 59c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06HOSGAT-HOS | 59 | 13m | 0 | 59-67 | — | **NO_FLOW** | 59 |  |
| ITFMATCH-26JUL06IAMBEN-BEN | 19 | 9m | 0 | 19-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06IAMBEN-IAM | 51 | 8m | 0 | 51-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06JAIHEN-JAI | 45 | 201m | 0 | 45-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-LIL | 28 | 185m | 205/1-55/9114 | 1-1 | -27 | **FLOW_AT_LEVEL** | 31 |  |
| ITFMATCH-26JUL06LAPCIO-CIO | 41 | 82m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LAPCIO-LAP | 54 | 80m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 32 | 78m | 1/32-32/0 | 32-60 | 0 | **FLOW_AT_LEVEL** | 32 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 32 | 14m | 0 | 32-60 | — | **NO_FLOW** | 32 |  |
| ITFMATCH-26JUL06LIBNAK-LIB | 38 | 126m | 0 | 38-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LIBNAK-NAK | 55 | 126m | 0 | 55-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LUEVAN-LUE | 65 | 93m | 0 | 65-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LUEVAN-VAN | 20 | 140m | 0 | 20-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06PESTER-PES | 31 | 3m | 0 | 31-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-BEC | 87 | 203m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-ROJ | 10 | 203m | 1/12-12/37 | 10-12 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→12 |
| ITFMATCH-26JUL06ROURAM-RAM | 53 | 81m | 0 | 53-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROURAM-ROU | 37 | 82m | 0 | 37-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STAGUI-GUI | 37 | 97m | 0 | 37-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STAGUI-STA | 49 | 55m | 0 | 49-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STEAUN-AUN | 14 | 203m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STEAUN-STE | 82 | 203m | 0 | 82-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SURMED-SUR | 21 | 9m | 0 | 21-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TEUHAS-HAS | 63 | 175m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TEUHAS-TEU | 33 | 201m | 0 | 33-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TIMJEF-JEF | 72 | 5m | 0 | 72-73 | — | **NO_FLOW** | 77 |  |
| ITFMATCH-26JUL06TIMJEF-JEF | 68 | 5m | 0 | 72-73 | — | **NO_FLOW** | 77 |  |
| ITFMATCH-26JUL06TISVER-TIS | 35 | 13m | 0 | 35-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TISVER-VER | 26 | 14m | 0 | 26-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRA | 24 | 261m | 0 | 24-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRU | 67 | 168m | 0 | 67-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VANHOR-HOR | 30 | 81m | 1/36-36/1 | 30-36 | 6 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06VANHOR-HOR | 26 | 17m | 0 | 30-36 | — | **NO_FLOW** | 34 |  |
| ITFMATCH-26JUL06VULCOU-VUL | 81 | 186m | 11/98-99/1550 | 99-85 | 17 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ADKFER-ADK | 53 | 278m | 0 | 53-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ADKFER-FER | 18 | 278m | 0 | 18-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 247m | 0 | 26-32 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 193m | 0 | 26-32 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06BOSTOP-BOS | 68 | 84m | 0 | 68-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOSTOP-TOP | 33 | 323m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOWMAT-BOW | 7 | 34m | 0 | 7-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOWMAT-MAT | 51 | 34m | 0 | 51-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 374m | 4430/1-99/518199 | 5-1 | -33 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06BUYALV-ALV | 22 | 254m | 1/46-46/5 | 22-50 | 24 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06BUYALV-BUY | 54 | 215m | 0 | 54-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CENBUL-BUL | 19 | 140m | 0 | 19-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CENBUL-CEN | 50 | 47m | 0 | 70-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06COHXAV-COH | 5 | 9m | 0 | 5-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DRISLA-DRI | 26 | 34m | 0 | 26-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DRISLA-SLA | 60 | 34m | 0 | 60-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EVARHO-EVA | 53 | 14m | 0 | 53-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EVARHO-RHO | 14 | 14m | 0 | 14-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06FAVKLY-FAV | 13 | 55m | 0 | 13-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06FAVKLY-KLY | 8 | 126m | 0 | 8-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-TSE | 20 | 15m | 24/27-35/3060 | 24-27 | 7 | **FLOW_ABOVE** | 20 | flow above but bound 20c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06HIEGUT-GUT | 56 | 139m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HIEGUT-HIE | 41 | 143m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 25 | 168m | 1/99-99/12 | 99-58 | 74 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARVIS-KAR | 76 | 76m | 67/84-98/3212 | 95-95 | 8 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARVIS-KAR | 76 | 16m | 33/94-98/2655 | 95-95 | 18 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KOVDAE-DAE | 20 | 64m | 1/24-24/24 | 20-24 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFWMATCH-26JUL06KOVDAE-KOV | 75 | 233m | 0 | 75-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 232m | 14/79-87/544 | 86-88 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 232m | 14/79-87/544 | 86-88 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 8m | 11/81-87/533 | 86-88 | 6 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULVOG-KUL | 55 | 40m | 0 | 55-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULVOG-VOG | 39 | 38m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LABTSY-LAB | 27 | 112m | 0 | 27-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LABTSY-TSY | 59 | 112m | 0 | 59-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 420m | 3895/23-99/459986 | 99-24 | -14 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06MARGLU-GLU | 66 | 176m | 0 | 66-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARGLU-MAR | 28 | 201m | 0 | 28-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-ENC | 51 | 250m | 1/57-57/16 | 51-57 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-MCA | 42 | 239m | 0 | 42-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MULCIS-CIS | 34 | 22m | 0 | 34-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MULCIS-MUL | 53 | 20m | 0 | 53-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKASAK-OKA | 35 | 10m | 0 | 35-54 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-PRI | 41 | 86m | 737/36-98/98724 | 94-78 | -5 | **FLOW_AT_LEVEL** | 41 |  |
| ITFWMATCH-26JUL06PACLOV-PAC | 52 | 68m | 4/57-60/97 | 53-58 | 5 | **FLOW_ABOVE** | 52 | flow above but bound 52c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06PACLOV-PAC | 52 | 67m | 4/57-60/97 | 53-58 | 5 | **FLOW_ABOVE** | 52 | flow above but bound 52c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 324m | 1942/1-13/312225 | 14-1 | -7 | **FLOW_AT_LEVEL** | 12 |  |
| ITFWMATCH-26JUL06PEEPAH-PEE | 39 | 38m | 20/11-51/514 | 13-18 | -28 | **FLOW_AT_LEVEL** | 36 |  |
| ITFWMATCH-26JUL06PIERAD-PIE | 64 | 132m | 117/84-99/4782 | 99-90 | 20 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06POZMLA-POZ | 89 | 5m | 5/95-97/132 | 96-95 | 6 | **FLOW_ABOVE** | 89 | flow above but bound 89c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06PRINIJ-NIJ | 30 | 232m | 0 | 30-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-PRI | 63 | 232m | 0 | 63-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06RABELI-ELI | 9 | 19m | 0 | 9-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06REEION-ION | 51 | 34m | 0 | 51-67 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06REEION-REE | 33 | 34m | 0 | 33-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SACLAZ-LAZ | 15 | 179m | 648/1-33/45125 | 40-1 | -14 | **FLOW_AT_LEVEL** | 1 |  |
| ITFWMATCH-26JUL06SCHELI-ELI | 34 | 34m | 0 | 34-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 370m | 16366/1-95/1383948 | 83-1 | -13 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06SINUSU-SIN | 9 | 20m | 0 | 9-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06STETRA-STE | 78 | 140m | 0 | 78-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06STETRA-TRA | 16 | 140m | 0 | 16-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-EVA | 37 | 111m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-URR | 61 | 203m | 1/65-65/10 | 61-65 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 370m | 6096/1-29/750264 | 21-1 | -14 | **FLOW_AT_LEVEL** | 5 |  |
| ITFWMATCH-26JUL06VARMUN-MUN | 13 | 52m | 0 | 13-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VARMUN-VAR | 83 | 50m | 0 | 83-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VIRKOV-KOV | 31 | 42m | 0 | 31-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VIRKOV-VIR | 56 | 247m | 2/70-70/23 | 56-65 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-VLA | 30 | 66m | 573/1-54/39141 | 1-2 | -29 | **FLOW_AT_LEVEL** | 23 |  |
| WTACHALLENGERMATCH-26JUL06ARANIL-A | 73 | 280m | 4/74-75/114 | 73-75 | 1 | **FLOW_ABOVE** | 72 | flow above but bound 72c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ARANIL-N | 25 | 293m | 1/26-26/9 | 25-26 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 74 | 203m | 1/76-76/25 | 74-76 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 24 | 203m | 1/25-25/102 | 24-26 | 1 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06BLIAND-A | 35 | 203m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BLIAND-B | 64 | 203m | 2/65-65/52 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| WTACHALLENGERMATCH-26JUL06DENQUE-D | 4 | 113m | 0 | 4-6 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06DENQUE-Q | 93 | 113m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06GRAMAS-G | 30 | 48m | 0 | 32-33 | — | **NO_FLOW** | 30 |  |
| WTACHALLENGERMATCH-26JUL06GRAMAS-G | 29 | 47m | 0 | 32-33 | — | **NO_FLOW** | 30 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 39 | 93m | 108/84-99/18486 | 99-99 | 45 | **FLOW_ABOVE** | 39 | flow above but bound 39c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ISHCRO-C | 61 | 22m | 0 | 61-62 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06ISHCRO-I | 38 | 22m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06LINMAR-L | 6 | 20m | 1/7-7/7 | 6-7 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→7 |
| WTACHALLENGERMATCH-26JUL06LINMAR-M | 93 | 20m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MATPUT-M | 9 | 293m | 4/9-10/119 | 9-10 | 0 | **FLOW_AT_LEVEL** | 7 |  |
| WTACHALLENGERMATCH-26JUL06MATPUT-P | 89 | 293m | 4/90-92/55 | 91-93 | 1 | **FLOW_ABOVE** | 87 | flow above but bound 87c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06OLIUCH-U | 39 | 80m | 762/18-56/87839 | 45-36 | -21 | **FLOW_AT_LEVEL** | 37 |  |
| WTACHALLENGERMATCH-26JUL06ROMSEM-R | 40 | 35m | 100/45-77/8408 | 71-72 | 5 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06WALKAW-K | 43 | 203m | 4/44-44/206 | 43-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| WTACHALLENGERMATCH-26JUL06WALKAW-W | 56 | 34m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-S | 67 | 203m | 1/68-68/17 | 67-69 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| WTACHALLENGERMATCH-26JUL06WERSAL-W | 31 | 203m | 0 | 31-33 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL06BOUMER-MER | 50 | 1m | 2/55-55/6 | 54-55 | 5 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| WTAMATCH-26JUL06KEYNOS-KEY | 58 | 80m | 25/58-59/1031 | 58-59 | 0 | **FLOW_AT_LEVEL** | 59 |  |
| WTAMATCH-26JUL06KEYNOS-NOS | 43 | 77m | 10/43-44/715 | 43-44 | 0 | **FLOW_AT_LEVEL** | 41 |  |
| WTAMATCH-26JUL06PAOEAL-EAL | 58 | 13m | 10/61-61/402 | 60-61 | 3 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06PAPJAN | 53 | 21 | **74** | 97 | -23 |
| ITFMATCH-26JUL06TIMJEF | 20 | 73 | **93** | 97 | -4 |
| ITFMATCH-26JUL06VANHOR | 63 | 36 | **99** | 97 | +2 |
| WTACHALLENGERMATCH-26JUL06GRAMAS | 67 | 33 | **100** | 97 | +3 |
| WTAMATCH-26JUL06PAOEAL | 39 | 61 | **100** | 97 | +3 |
| ATPMATCH-26JUL06DIMFER | 33 | 68 | **101** | 97 | +4 |
| ATPMATCH-26JUL06DECOB | 23 | 79 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL06BASHOE | 51 | 51 | **102** | 97 | +5 |
| WTAMATCH-26JUL06BOUMER | 47 | 55 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06PACLOV | 45 | 58 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL06DONCIZ | 24 | 79 | **103** | 97 | +6 |
| ITFWMATCH-26JUL06POZMLA | 8 | 95 | **103** | 97 | +6 |
| ITFWMATCH-26JUL06GALTSE | 77 | 27 | **104** | 97 | +7 |
| ATPCHALLENGERMATCH-26JUL06POLHAI | 31 | 73 | **104** | 97 | +7 |
| ITFMATCH-26JUL06HOSGAT | 38 | 67 | **105** | 97 | +8 |
| ATPCHALLENGERMATCH-26JUL06RAQRIB | 61 | 46 | **107** | 97 | +10 |
| ITFWMATCH-26JUL06RICMIT | 9 | 99 | **108** | 97 | +11 |
| ITFWMATCH-26JUL06BOIBOY | 77 | 32 | **109** | 97 | +12 |
| ATPCHALLENGERMATCH-26JUL06SEYMAR | 10 | 99 | **109** | 97 | +12 |
| ITFWMATCH-26JUL06KULGON | 22 | 88 | **110** | 97 | +13 |
| ATPCHALLENGERMATCH-26JUL06HUAPUR | 35 | 80 | **115** | 97 | +18 |
| ITFMATCH-26JUL06CASBAY | 45 | 71 | **116** | 97 | +19 |
| ITFWMATCH-26JUL06KARVIS | 21 | 95 | **116** | 97 | +19 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ITFWMATCH-26JUL06PIERAD | 33 | 90 | **123** | 97 | +26 |
| ITFMATCH-26JUL06LENTHE | 65 | 60 | **125** | 97 | +28 |
| WTACHALLENGERMATCH-26JUL06ROMSEM | 57 | 72 | **129** | 97 | +32 |
| ITFMATCH-26JUL06ALEREG | 51 | 99 | **150** | 97 | +53 |
| ITFWMATCH-26JUL06WONIBR | 65 | 99 | **164** | 97 | +67 |

## PATTERNS (sub-B) — 96
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TODSAG-SAG {"price": 25, "ceiling": 21}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 23, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 25, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SACLAZ-LAZ {"price": 12, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06BRESAF-BRE {"price": 58, "ceiling": 47}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06BRESAF-BRE {"price": 63, "ceiling": 47}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SACLAZ-LAZ {"price": 16, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TODSAG-SAG {"price": 29, "ceiling": 21}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TODSAG-SAG {"price": 30, "ceiling": 21}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 27, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VAJRAM-RAM {"price": 14, "ceiling": 13}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 28, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TODSAG-SAG {"price": 31, "ceiling": 21}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VAJRAM-RAM {"price": 15, "ceiling": 13}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06SALNGW-NGW {"price": 39, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VAJRAM-RAM {"price": 16, "ceiling": 13}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VAJRAM-RAM {"price": 17, "ceiling": 13}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SACLAZ-LAZ {"price": 17, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SIMCIR-SIM {"price": 84, "ceiling": 73}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SACLAZ-LAZ {"price": 18, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SACLAZ-LAZ {"price": 19, "ceiling": 9}
- deep_neg_fv: KXITFWMATCH-26JUL06SIMCIR-CIR {"entry_minus_fv_burst": -30.0}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 438, "mode": "SET_BELOW_FLOW(prints 74c above)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 29, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 30, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 31, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 32, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LUKNOE-LUK {"price": 59, "ceiling": 18}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LUKNOE-LUK {"price": 66, "ceiling": 18}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 411, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LUKNOE-LUK {"price": 67, "ceiling": 18}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ELDHAU-ELD {"price": 59, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LUKNOE-LUK {"price": 68, "ceiling": 18}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 33, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VLADIL-VLA {"price": 39, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VLADIL-VLA {"price": 40, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06IVAKUH-IVA {"price": 60, "ceiling": 54}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06IVAKUH-IVA {"price": 61, "ceiling": 54}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06IVAKUH-IVA {"price": 62, "ceiling": 54}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 18, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 19, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 20, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 21, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 22, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 23, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ELDHAU-ELD {"price": 60, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 24, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ELDHAU-ELD {"price": 64, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 25, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 26, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 28, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LUKNOE-LUK {"price": 69, "ceiling": 18}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 29, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06GANPUI-PUI {"price": 10, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06GANPUI-PUI {"price": 11, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 51, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 52, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VLADIL-VLA {"price": 41, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 53, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 54, "ceiling": 31}
- half_arm_aging: KXITFWMATCH-26JUL06BOIBOY-BOI {"fill": 77, "age_min": 247, "mode": "STARVATION(no prints since post)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06DIANIK-NIK {"price": 41, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06DIANIK-NIK {"price": 52, "ceiling": 38}
- half_arm_aging: KXITFWMATCH-26JUL06KULGON-GON {"fill": 22, "age_min": 233, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06JOSKUM-JOS {"price": 61, "ceiling": 59}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06JOSKUM-JOS {"price": 67, "ceiling": 59}
- half_arm_aging: KXITFMATCH-26JUL06CASBAY-CAS {"fill": 45, "age_min": 182, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TEISCH-TEI {"price": 80, "ceiling": 79}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TEISCH-TEI {"price": 81, "ceiling": 79}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ELDHAU-ELD {"price": 65, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 60, "ceiling": 31}
- deep_neg_fv: KXITFWMATCH-26JUL06OKUPRI-PRI {"entry_minus_fv_burst": -45.5, "emitted_et": "2026-07-06 07:23:44 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TEISCH-TEI {"price": 82, "ceiling": 79}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TEISCH-TEI {"price": 87, "ceiling": 79}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06NOHBUR-BUR {"entry_minus_fv_burst": -48.5}
- half_arm_aging: KXITFWMATCH-26JUL06PIERAD-RAD {"fill": 33, "age_min": 132, "mode": "SET_BELOW_FLOW(prints 20c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06PAPJAN-PAP {"fill": 53, "age_min": 131, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL06LENTHE-THE {"fill": 65, "age_min": 125, "mode": "QUEUE(flow at/below our level, unfilled)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06MONPOP-MON {"entry_minus_fv_burst": -35.5}
- half_arm_aging: KXITFWMATCH-26JUL06RICMIT-MIT {"fill": 9, "age_min": 118, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPMATCH-26JUL06DECOB-COB {"fill": 23, "age_min": 117, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06GALTSE-GAL {"fill": 77, "age_min": 108, "mode": "SET_BELOW_FLOW(prints 7c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SEYMAR-MAR {"fill": 10, "age_min": 103, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06POLHAI-POL {"fill": 31, "age_min": 102, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06GOMLUZ-GOM {"entry_minus_fv_burst": -26.5}
- half_arm_aging: KXITFMATCH-26JUL06ALEREG-ALE {"fill": 51, "age_min": 89, "mode": "SET_BELOW_FLOW(prints 9c above)"}
- half_arm_aging: KXITFMATCH-26JUL06VANHOR-VAN {"fill": 63, "age_min": 77, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06KARVIS-VIS {"fill": 21, "age_min": 77, "mode": "SET_BELOW_FLOW(prints 8c above)"}
- deep_neg_fv: KXITFWMATCH-26JUL06VLADIL-DIL {"entry_minus_fv_burst": -32.0}
- half_arm_aging: KXATPMATCH-26JUL06DIMFER-FER {"fill": 33, "age_min": 74, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06BASHOE-HOE {"fill": 51, "age_min": 72, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- deep_neg_fv: KXWTAMATCH-26JUL06KRUKOS-KOS {"entry_minus_fv_burst": -18.0}
- half_arm_aging: KXITFWMATCH-26JUL06PACLOV-LOV {"fill": 45, "age_min": 68, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06GRAMAS-MAS {"fill": 67, "age_min": 48, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFMATCH-26JUL06HOSGAT-GAT {"fill": 38, "age_min": 42, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06ROMSEM-SEM {"fill": 57, "age_min": 35, "mode": "SET_BELOW_FLOW(prints 5c above)", "emitted_et": "2026-07-06 07:23:44 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
