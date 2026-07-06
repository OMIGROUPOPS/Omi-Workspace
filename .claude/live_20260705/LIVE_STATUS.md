# LIVE VALIDATION — rolling status

- cycle 137 @ **2026-07-06 10:11:44 AM ET** | build `5b49917` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 167732 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 31 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 23:50:46 | **walk_cap_breach** | KXITFWMATCH-26JUL06SIMCIR-SIM | buy 83c > ceiling 73c (conception 69 + cap) ref=join_bid |
| 00:30:15 | **walk_cap_breach** | KXITFWMATCH-26JUL06LUKNOE-LUK | buy 56c > ceiling 18c (conception 14 + cap) ref=join_bid |
| 00:31:45 | **walk_cap_breach** | KXITFMATCH-26JUL06ELDHAU-ELD | buy 58c > ceiling 20c (conception 16 + cap) ref=join_bid |
| 00:32:43 | **walk_cap_breach** | KXITFWMATCH-26JUL06WONIBR-IBR | buy 65c > ceiling 9c (conception 5 + cap) ref=join_bid |
| 00:54:46 | **walk_cap_breach** | KXITFWMATCH-26JUL06VLADIL-VLA | buy 38c > ceiling 31c (conception 27 + cap) ref=join_bid |
| 01:01:56 | **combined_over_goal** | KXITFWMATCH-26JUL06TODSAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 01:12:30 | **combined_over_goal** | KXITFWMATCH-26JUL06VAJRAM | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |
| 01:30:43 | **walk_cap_breach** | KXITFMATCH-26JUL06LENTHE-THE | buy 59c > ceiling 34c (conception 30 + cap) ref=join_bid |
| 01:30:45 | **walk_cap_breach** | KXITFMATCH-26JUL06LENTHE-THE | buy 60c > ceiling 34c (conception 30 + cap) ref=join_bid |
| 01:30:46 | **walk_cap_breach** | KXITFWMATCH-26JUL06SPIMED-SPI | buy 82c > ceiling 78c (conception 74 + cap) ref=join_bid |
| 02:03:10 | **walk_cap_breach** | KXITFWMATCH-26JUL06BOIBOY-BOI | buy 77c > ceiling 72c (conception 68 + cap) ref=join_bid |
| 02:23:23 | **walk_cap_breach** | KXITFMATCH-26JUL06TSIAND-TSI | buy 50c > ceiling 38c (conception 34 + cap) ref=join_bid |
| 02:23:24 | **walk_cap_breach** | KXITFMATCH-26JUL06TSIAND-TSI | buy 51c > ceiling 38c (conception 34 + cap) ref=join_bid |
| 03:38:20 | **combined_over_goal** | KXITFWMATCH-26JUL06DZJMCK | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 03:59:23 | **walk_cap_breach** | KXITFMATCH-26JUL06HOSGAT-GAT | buy 35c > ceiling 23c (conception 19 + cap) ref=join_bid |
| 03:59:23 | **walk_cap_breach** | KXITFMATCH-26JUL06HOSGAT-GAT | buy 38c > ceiling 23c (conception 19 + cap) ref=join_bid |
| 04:09:27 | **walk_cap_breach** | KXITFMATCH-26JUL06GANVER-VER | buy 46c > ceiling 45c (conception 41 + cap) ref=join_bid |
| 05:04:30 | **combined_over_goal** | KXITFMATCH-26JUL06HERNAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 05:09:22 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL06HERNGU | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 06:03:37 | **walk_cap_breach** | KXITFMATCH-26JUL06TEXCAR-TEX | buy 66c > ceiling 55c (conception 51 + cap) ref=join_bid |
| 06:03:46 | **walk_cap_breach** | KXITFMATCH-26JUL06TEXCAR-TEX | buy 67c > ceiling 55c (conception 51 + cap) ref=join_bid |
| 06:24:17 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL06POTFEL | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |
| 06:29:40 | **combined_over_goal** | KXITFMATCH-26JUL06TSIAND | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |
| 06:40:21 | **combined_over_goal** | KXATPCHALLENGERMATCH-26JUL06ERHSIN | pair combined 100c > goal 97c [organic: DEFECT-CLASS] |
| 06:55:43 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL06HESPAL | pair combined 102c > goal 97c [organic: DEFECT-CLASS] |
| 07:06:49 | **combined_over_goal** | KXITFMATCH-26JUL06DUHCAR | pair combined 100c > goal 97c [organic: DEFECT-CLASS] |
| 07:55:16 | **combined_over_goal** | KXITFMATCH-26JUL06GARCIO | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 08:02:23 | **combined_over_goal** | KXITFMATCH-26JUL06TEUHAS | pair combined 105c > goal 97c [organic: DEFECT-CLASS] |
| 08:23:44 | **combined_over_goal** | KXITFWMATCH-26JUL06PACLOV | pair combined 106c > goal 97c [organic: DEFECT-CLASS] |
| 09:50:55 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL06BASBAD | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 10:00:08 | **combined_over_goal** | KXITFWMATCH-26JUL06SILDIG | pair combined 107c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 277 graded (session)
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
| 03:16 | ITFWMATCH-26JUL06BOIBOY-BOI | ITF_W | leader | 77 | 75 | +2 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 03:29 | ITFMATCH-26JUL06SALNGW-NGW | ITF_M | ? | 39 | 32 | +7 (place_cell) | — | pre | pair | 97 | MIXED |
| 03:31 | ITFWMATCH-26JUL06KULGON-GON | ITF_W | ? | 22 | 16 | +6 (place_cell) | — | pre | single |  | MIXED |
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
| 04:11 | ATPCHALLENGERMATCH-26JUL06CAMDE-DE | ATP_CHALL | underdog | 39 | 36 | +3 (place_cell) | -6.5 | pre | pair | 97 | EARNED |
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
| 05:07 | WTACHALLENGERMATCH-26JUL06OLIUCH-U | WTA_CHALL | underdog | 39 | 37 | +2 (place_cell) | 1.5 | pre | pair | 97 | MIXED |
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
| 05:11 | ATPCHALLENGERMATCH-26JUL06CAMDE-CA | ATP_CHALL | leader | 58 | 56 | +2 (place_cell) | 4.5 | pre | pair | 97 | GIFT_CLASS |
| 05:11 | ITFWMATCH-26JUL06PIERAD-RAD | ITF_W | underdog | 33 | 18 | +15 (place_cell) | — | pre | single |  | PENDING |
| 05:12 | WTACHALLENGERMATCH-26JUL06NOHBUR-N | WTA_CHALL | leader | 75 | 73 | +2 (place_cell) | 37.0 | pre | pair | 97 | GIFT_CLASS |
| 05:12 | ATPCHALLENGERMATCH-26JUL06PAPJAN-P | ATP_CHALL | ? | 53 | 50 | +3 (place_cell) | 19.5 | pre | single |  | GIFT_CLASS |
| 05:12 | WTACHALLENGERMATCH-26JUL06BULSTR-B | WTA_CHALL | ? | 68 | 68 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:13 | ITFWMATCH-26JUL06TRIVOR-VOR | ITF_W | leader | 89 | 49 | +40 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:15 | ITFWMATCH-26JUL06TRIVOR-TRI | ITF_W | ? | 8 | 1 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:15 | ITFWMATCH-26JUL06TEISCH-SCH | ITF_W | ? | 4 | 2 | +2 (place_cell) | — | pre | pair | 90 | EARNED |
| 05:16 | ITFWMATCH-26JUL06POPSOL-SOL | ITF_W | ? | 61 | 50 | +11 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:17 | ATPCHALLENGERMATCH-26JUL06STALEC-L | ATP_CHALL | underdog | 32 | 30 | +2 (place_cell) | — | pre | pair | 96 | EARNED |
| 05:18 | ITFMATCH-26JUL06LENTHE-THE | ITF_M | ? | 65 | 56 | +9 (place_cell) | — | pre | pair | 65 | GIFT_CLASS |
| 05:20 | WTACHALLENGERMATCH-26JUL06MONPOP-M | WTA_CHALL | underdog | 43 | 41 | +2 (place_cell) | -35.5 | pre | pair | 97 | EARNED |
| 05:22 | ATPCHALLENGERMATCH-26JUL06PRIORA-O | ATP_CHALL | ? | 39 | 37 | +2 (place_cell) | -5.0 | pre | pair | 95 | EARNED |
| 05:25 | ITFWMATCH-26JUL06RICMIT-MIT | ITF_W | ? | 9 | 3 | +6 (place_cell) | — | pre | single |  | MIXED |
| 05:26 | ATPMATCH-26JUL06DECOB-COB | ATP_MAIN | underdog | 23 | 22 | +1 (place_cell) | -5.5 | pre | pair | 97 | EARNED |
| 05:28 | ITFWMATCH-26JUL06IVAKUH-KUH | ITF_W | ? | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:30 | ITFMATCH-26JUL06DUGHOF-HOF | ITF_M | ? | 21 | 6 | +15 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:31 | ITFWMATCH-26JUL06PEEPAH-PAH | ITF_W | ? | 58 | 6 | +52 (place_cell) | -26.5 | pre | pair | 96 | EARNED |
| 05:32 | ITFWMATCH-26JUL06JOSKUM-KUM | ITF_W | underdog | 28 | 31 | -3 (place_cell) | — | pre | pair | 95 | EARNED |
| 05:32 | ATPCHALLENGERMATCH-26JUL06NIJRAH-N | ATP_CHALL | ? | 56 | 57 | -1 (window_cell) | — | pre | pair | 96 | MIXED |
| 05:32 | ITFWMATCH-26JUL06SPIMED-MED | ITF_W | ? | 8 | 1 | +7 (place_cell) | — | pre | pair | 96 | EARNED |
| 05:35 | ITFWMATCH-26JUL06GALTSE-GAL | ITF_W | leader | 77 | 71 | +6 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 05:38 | ITFWMATCH-26JUL06MILHER-HER | ITF_W | underdog | 16 | 3 | +13 (place_cell) | 14.5 | pre | pair | 97 | GIFT_CLASS |
| 05:39 | ATPCHALLENGERMATCH-26JUL06PIEMOL-P | ATP_CHALL | ? | 45 | 41 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:40 | ITFMATCH-26JUL06BEASCO-BEA | ITF_M | leader | 64 | 63 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:40 | ATPCHALLENGERMATCH-26JUL06SEYMAR-M | ATP_CHALL | underdog | 10 | 6 | +4 (place_cell) | — | pre | single |  | MIXED |
| 05:41 | ATPCHALLENGERMATCH-26JUL06POLHAI-P | ATP_CHALL | underdog | 31 | 28 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:41 | WTACHALLENGERMATCH-26JUL06LEWMAR-M | WTA_CHALL | ? | 43 | 40 | +3 (place_cell) | -24.5 | pre | pair | 97 | EARNED |
| 05:41 | ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | ATP_CHALL | underdog | 26 | 23 | +3 (place_cell) | 20.5 | pre | pair | 97 | GIFT_CLASS |
| 05:42 | ATPCHALLENGERMATCH-26JUL06GOMLUZ-G | ATP_CHALL | ? | 71 | 68 | +3 (place_cell) | -26.5 | pre | pair | 97 | EARNED |
| 05:44 | ATPCHALLENGERMATCH-26JUL06DALCAR-C | ATP_CHALL | underdog | 3 | 2 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:45 | WTACHALLENGERMATCH-26JUL06BOUKOT-B | WTA_CHALL | underdog | 20 | 20 | +0 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:46 | ITFMATCH-26JUL06MEHCOU-COU | ITF_M | leader | 55 | 48 | +7 (place_cell) | — | pre | pair | 89 | PENDING |
| 05:51 | ATPCHALLENGERMATCH-26JUL06DALCAR-D | ATP_CHALL | leader | 94 | 93 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:51 | ITFMATCH-26JUL06SALBRE-SAL | ITF_M | leader | 90 | 86 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:52 | ITFWMATCH-26JUL06IVAKUH-IVA | ITF_W | ? | 60 | 59 | +1 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 05:54 | ITFMATCH-26JUL06ALEREG-ALE | ITF_M | leader | 51 | 48 | +3 (place_cell) | — | pre | single |  | PENDING |
| 05:56 | ITFWMATCH-26JUL06SPIMED-SPI | ITF_W | ? | 88 | 81 | +7 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 05:57 | ITFWMATCH-26JUL06GANPUI-GAN | ITF_W | leader | 83 | 79 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:58 | ITFWMATCH-26JUL06KOTCHI-KOT | ITF_W | underdog | 52 | 21 | +31 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:58 | WTACHALLENGERMATCH-26JUL06OLIUCH-O | WTA_CHALL | leader | 58 | 57 | +1 (place_cell) | 2.5 | pre | pair | 97 | MIXED |
| 06:02 | ITFWMATCH-26JUL06PEEPAH-PEE | ITF_W | underdog | 38 | 4 | +34 (place_cell) | 23.5 | pre | pair | 96 | GIFT_CLASS |
| 06:05 | ITFMATCH-26JUL06TEXCAR-TEX | ITF_M | leader | 67 | 74 | -7 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 06:06 | ITFWMATCH-26JUL06KOTCHI-CHI | ITF_W | ? | 45 | 23 | +22 (window_cell) | — | pre | pair | 97 | MIXED |
| 06:06 | ITFWMATCH-26JUL06PODLUK-LUK | ITF_W | leader | 70 | 53 | +17 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:07 | ITFMATCH-26JUL06VANHOR-VAN | ITF_M | leader | 63 | 60 | +3 (place_cell) | — | pre | single |  | PENDING |
| 06:07 | ITFWMATCH-26JUL06KARVIS-VIS | ITF_W | ? | 21 | 8 | +13 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:09 | ITFWMATCH-26JUL06VLADIL-DIL | ITF_W | leader | 56 | 52 | +4 (place_cell) | -32.0 | pre | pair | 97 | EARNED |
| 06:09 | ATPMATCH-26JUL06DIMFER-FER | ATP_MAIN | underdog | 33 | 31 | +2 (place_cell) | — | pre | single |  | MIXED |
| 06:11 | ITFWMATCH-26JUL06ILIEBE-ILI | ITF_W | underdog | 45 | 37 | +8 (place_cell) | — | pre | pair | 97 | EARNED |
| 06:11 | ATPCHALLENGERMATCH-26JUL06DELWAL-D | ATP_CHALL | underdog | 28 | 24 | +4 (place_cell) | -16.5 | pre | pair | 97 | EARNED |
| 06:11 | ATPCHALLENGERMATCH-26JUL06BASHOE-H | ATP_CHALL | leader | 51 | 48 | +3 (place_cell) | -47.5 | pre | pair | 96 | EARNED |
| 06:12 | WTAMATCH-26JUL06KRUKOS-KOS | WTA_MAIN | ? | 66 | 71 | -5 (window_cell) | -18.0 | pre | pair | 97 | EARNED |
| 06:12 | ATPCHALLENGERMATCH-26JUL06SEGBRA-B | ATP_CHALL | underdog | 36 | 33 | +3 (place_cell) | -47.5 | pre | pair | 97 | EARNED |
| 06:14 | ITFMATCH-26JUL06TEXCAR-CAR | ITF_M | underdog | 30 | 32 | -2 (place_cell) | — | pre | pair | 97 | EARNED |
| 06:15 | ITFWMATCH-26JUL06ILIEBE-EBE | ITF_W | ? | 52 | 49 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 06:15 | ITFWMATCH-26JUL06PACLOV-LOV | ITF_W | ? | 45 | 37 | +8 (place_cell) | — | pre | pair | 106 | MIXED |
| 06:15 | ATPCHALLENGERMATCH-26JUL06POTFEL-P | ATP_CHALL | ? | 40 | 37 | +3 (place_cell) | 26.5 | pre | pair | 101 | GIFT_CLASS |
| 06:15 | ITFMATCH-26JUL06MEHCOU-MEH | ITF_M | ? | 34 | 21 | +13 (place_cell) | — | pre | pair | 89 | PENDING |
| 06:18 | ATPCHALLENGERMATCH-26JUL06SEGBRA-S | ATP_CHALL | ? | 61 | 58 | +3 (place_cell) | 45.0 | pre | pair | 97 | GIFT_CLASS |
| 06:20 | ITFWMATCH-26JUL06GANPUI-PUI | ITF_W | underdog | 14 | 4 | +10 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:24 | ATPCHALLENGERMATCH-26JUL06POTFEL-F | ATP_CHALL | ? | 61 | 55 | +6 (place_cell) | -25.5 | pre | pair | 101 | EARNED |
| 06:27 | ITFMATCH-26JUL06TSIAND-AND | ITF_M | underdog | 24 | 4 | +20 (place_cell) | — | pre | pair | 101 | EARNED |
| 06:29 | ITFMATCH-26JUL06TSIAND-TSI | ITF_M | ? | 77 | 4 | +73 (place_cell) | — | pre | pair | 101 | GIFT_CLASS |
| 06:31 | ITFWMATCH-26JUL06EWAMAN-EWA | ITF_W | ? | 70 | 63 | +7 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 06:35 | WTACHALLENGERMATCH-26JUL06GRAMAS-M | WTA_CHALL | ? | 67 | 64 | +3 (place_cell) | -10.5 | pre | pair | 96 | EARNED |
| 06:36 | ATPCHALLENGERMATCH-26JUL06MARHAM-H | ATP_CHALL | underdog | 5 | 3 | +2 (place_cell) | — | pre | pair | 96 | MIXED |
| 06:40 | ATPCHALLENGERMATCH-26JUL06ERHSIN-E | ATP_CHALL | ? | 96 | 92 | +4 (place_cell) | — | pre | pair | 100 | GIFT_CLASS |
| 06:40 | ATPCHALLENGERMATCH-26JUL06ERHSIN-S | ATP_CHALL | underdog | 4 | 2 | +2 (place_cell) | — | pre | pair | 100 | MIXED |
| 06:40 | ATPCHALLENGERMATCH-26JUL06ZORDEV-D | ATP_CHALL | ? | 42 | 39 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 06:41 | ITFMATCH-26JUL06HOSGAT-GAT | ITF_M | underdog | 38 | 34 | +4 (place_cell) | — | pre | pair | 95 | MIXED |
| 06:43 | ATPCHALLENGERMATCH-26JUL06ZORDEV-Z | ATP_CHALL | leader | 55 | 53 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:43 | ATPCHALLENGERMATCH-26JUL06PIEMOL-M | ATP_CHALL | leader | 52 | 49 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:44 | ATPCHALLENGERMATCH-26JUL06DELWAL-W | ATP_CHALL | ? | 69 | 68 | +1 (place_cell) | 16.0 | pre | pair | 97 | GIFT_CLASS |
| 06:48 | ITFMATCH-26JUL06DUGHOF-DUG | ITF_M | ? | 76 | 51 | +25 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:48 | ATPCHALLENGERMATCH-26JUL06MARHAM-M | ATP_CHALL | ? | 91 | 91 | +0 (place_cell) | — | pre | pair | 96 | MIXED |
| 06:48 | WTACHALLENGERMATCH-26JUL06ROMSEM-S | WTA_CHALL | leader | 57 | 53 | +4 (place_cell) | 40.0 | pre | single |  | GIFT_CLASS |
| 06:53 | WTACHALLENGERMATCH-26JUL06LEWMAR-L | WTA_CHALL | leader | 54 | 52 | +2 (place_cell) | 21.5 | pre | pair | 97 | GIFT_CLASS |
| 06:53 | ITFWMATCH-26JUL06MILHER-MIL | ITF_W | ? | 81 | 49 | +32 (place_cell) | -17.5 | pre | pair | 97 | EARNED |
| 06:55 | WTACHALLENGERMATCH-26JUL06HESPAL-H | WTA_CHALL | ? | 33 | 26 | +7 (place_cell) | -59.5 | pre | pair | 102 | EARNED |
| 06:55 | WTACHALLENGERMATCH-26JUL06HESPAL-P | WTA_CHALL | leader | 69 | 66 | +3 (place_cell) | 60.0 | pre | pair | 102 | GIFT_CLASS |
| 06:57 | ATPCHALLENGERMATCH-26JUL06KUZSTR-S | ATP_CHALL | ? | 26 | 23 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:57 | ITFMATCH-26JUL06SALBRE-BRE | ITF_M | ? | 7 | 2 | +5 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:57 | ITFWMATCH-26JUL06PODLUK-POD | ITF_W | ? | 27 | 18 | +9 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:59 | ATPCHALLENGERMATCH-26JUL06RAQRIB-R | ATP_CHALL | leader | 61 | 61 | +0 (place_cell) | -3.5 | pre | pair | 97 | EARNED |
| 07:02 | ATPCHALLENGERMATCH-26JUL06DONCIZ-C | ATP_CHALL | ? | 24 | 20 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:03 | ATPCHALLENGERMATCH-26JUL06CHEYEV-Y | ATP_CHALL | ? | 37 | 34 | +3 (place_cell) | — | pre | pair | 96 | MIXED |
| 07:06 | ITFMATCH-26JUL06DUHCAR-DUH | ITF_M | ? | 88 | 79 | +9 (place_cell) | — | pre | pair | 100 | PENDING |
| 07:06 | ITFMATCH-26JUL06DUHCAR-CAR | ITF_M | underdog | 12 | 5 | +7 (place_cell) | — | pre | pair | 100 | PENDING |
| 07:06 | ATPCHALLENGERMATCH-26JUL06CHEYEV-C | ATP_CHALL | ? | 59 | 58 | +1 (place_cell) | — | pre | pair | 96 | MIXED |
| 07:09 | ITFWMATCH-26JUL06EWAMAN-MAN | ITF_W | ? | 27 | 14 | +13 (place_cell) | — | pre | pair | 97 | EARNED |
| 07:10 | ATPCHALLENGERMATCH-26JUL06KUZSTR-K | ATP_CHALL | ? | 71 | 70 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:11 | WTAMATCH-26JUL06PAOEAL-PAO | WTA_MAIN | underdog | 39 | 37 | +2 (place_cell) | -1.5 | pre | pair | 97 | MIXED |
| 07:14 | ATPCHALLENGERMATCH-26JUL06HUAPUR-H | ATP_CHALL | ? | 35 | 32 | +3 (place_cell) | 0.5 | pre | pair | 96 | MIXED |
| 07:16 | ATPCHALLENGERMATCH-26JUL06MARBER-B | ATP_CHALL | ? | 58 | 55 | +3 (place_cell) | -33.5 | pre | pair | 97 | EARNED |
| 07:18 | ITFMATCH-26JUL06TIMJEF-TIM | ITF_M | ? | 20 | 15 | +5 (place_cell) | — | pre | pair | 92 | MIXED |
| 07:18 | ITFWMATCH-26JUL06POZMLA-MLA | ITF_W | ? | 8 | 1 | +7 (place_cell) | — | pre | pair | 97 | EARNED |
| 07:20 | ATPCHALLENGERMATCH-26JUL06MARBER-M | ATP_CHALL | ? | 39 | 37 | +2 (place_cell) | 30.5 | pre | pair | 97 | EARNED |
| 07:22 | WTAMATCH-26JUL06BOUMER-BOU | WTA_MAIN | underdog | 47 | 43 | +4 (place_cell) | 1.0 | pre | pair | 97 | MIXED |
| 07:24 | ITFMATCH-26JUL06TIMJEF-JEF | ITF_M | ? | 72 | 67 | +5 (place_cell) | — | pre | pair | 92 | MIXED |
| 07:26 | ITFWMATCH-26JUL06BOSTOP-BOS | ITF_W | leader | 68 | 62 | +6 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:29 | ITFWMATCH-26JUL06FAVKLY-KLY | ITF_W | ? | 40 | 4 | +36 (place_cell) | — | pre | pair | 55 | MIXED |
| 07:29 | WTACHALLENGERMATCH-26JUL06GRAMAS-G | WTA_CHALL | ? | 29 | 29 | +0 (place_cell) | 4.5 | pre | pair | 96 | GIFT_CLASS |
| 07:30 | ITFWMATCH-26JUL06FAVKLY-FAV | ITF_W | underdog | 15 | 3 | +12 (place_cell) | — | pre | pair | 55 | EARNED |
| 07:34 | ITFWMATCH-26JUL06MCAENC-ENC | ITF_W | leader | 51 | 49 | +2 (place_cell) | — | pre | pair | 93 | MIXED |
| 07:39 | ATPCHALLENGERMATCH-26JUL06HUAPUR-P | ATP_CHALL | ? | 61 | 60 | +1 (place_cell) | -2.5 | pre | pair | 96 | MIXED |
| 07:39 | WTACHALLENGERMATCH-26JUL06MATPUT-M | WTA_CHALL | underdog | 9 | 6 | +3 (place_cell) | -0.5 | pre | pair | 97 | MIXED |
| 07:40 | ATPCHALLENGERMATCH-26JUL06IVADIN-D | ATP_CHALL | underdog | 20 | 17 | +3 (place_cell) | -0.5 | pre | pair | 97 | MIXED |
| 07:42 | WTACHALLENGERMATCH-26JUL06MATPUT-P | WTA_CHALL | ? | 88 | 86 | +2 (place_cell) | -2.5 | pre | pair | 97 | GIFT_CLASS |
| 07:43 | ITFWMATCH-26JUL06VIRKOV-KOV | ITF_W | underdog | 41 | 24 | +17 (place_cell) | — | pre | pair | 97 | EARNED |
| 07:44 | ATPCHALLENGERMATCH-26JUL06OPIPET-O | ATP_CHALL | underdog | 28 | 23 | +5 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:44 | ITFMATCH-26JUL06STAGUI-GUI | ITF_M | underdog | 37 | 8 | +29 (place_cell) | — | pre | single |  | MIXED |
| 07:44 | WTACHALLENGERMATCH-26JUL06BLIAND-B | WTA_CHALL | leader | 64 | 61 | +3 (place_cell) | 16.5 | pre | pair | 97 | GIFT_CLASS |
| 07:46 | ITFWMATCH-26JUL06BOSTOP-TOP | ITF_W | ? | 29 | 29 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:53 | ITFWMATCH-26JUL06VIRKOV-VIR | ITF_W | ? | 56 | 54 | +2 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 07:53 | ITFWMATCH-26JUL06OKASAK-OKA | ITF_W | ? | 40 | 20 | +20 (place_cell) | — | pre | single |  | MIXED |
| 07:55 | WTACHALLENGERMATCH-26JUL06ARANIL-A | WTA_CHALL | leader | 73 | 70 | +3 (place_cell) | -24.5 | pre | pair | 97 | EARNED |
| 07:55 | ITFMATCH-26JUL06GARCIO-GAR | ITF_M | leader | 57 | 55 | +2 (place_cell) | — | pre | pair | 98 | MIXED |
| 07:55 | ITFMATCH-26JUL06GARCIO-CIO | ITF_M | underdog | 41 | 32 | +9 (place_cell) | — | pre | pair | 98 | MIXED |
| 07:55 | WTAMATCH-26JUL06BOUMER-MER | WTA_MAIN | leader | 50 | 55 | -5 (place_cell) | -4.5 | pre | pair | 97 | EARNED |
| 07:58 | ITFMATCH-26JUL06TEUHAS-HAS | ITF_M | leader | 67 | 61 | +6 (place_cell) | — | pre | pair | 105 | MIXED |
| 07:59 | ITFMATCH-26JUL06ALIMIS-ALI | ITF_M | leader | 91 | 83 | +8 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 08:01 | ITFWMATCH-26JUL06POZMLA-POZ | ITF_W | ? | 89 | 75 | +14 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 08:02 | ITFMATCH-26JUL06TEUHAS-TEU | ITF_M | ? | 38 | 22 | +16 (place_cell) | — | pre | pair | 105 | MIXED |
| 08:02 | ATPCHALLENGERMATCH-26JUL06BASHOE-B | ATP_CHALL | ? | 45 | 44 | +1 (place_cell) | 43.5 | pre | pair | 96 | EARNED |
| 08:04 | ATPCHALLENGERMATCH-26JUL06POLHAI-H | ATP_CHALL | leader | 66 | 65 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:07 | ITFMATCH-26JUL06ROJBEC-ROJ | ITF_M | ? | 10 | 7 | +3 (place_cell) | — | pre | single |  | PENDING |
| 08:07 | ITFWMATCH-26JUL06KARVIS-KAR | ITF_W | ? | 76 | 73 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:09 | ATPCHALLENGERMATCH-26JUL06CHIJAN-J | ATP_CHALL | ? | 22 | 20 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:09 | ITFMATCH-26JUL06STEAUN-AUN | ITF_M | ? | 14 | 10 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 08:11 | ATPCHALLENGERMATCH-26JUL06REHKOU-K | ATP_CHALL | underdog | 44 | 41 | +3 (place_cell) | — | pre | single |  | MIXED |
| 08:12 | WTAMATCH-26JUL06KEYNOS-NOS | WTA_MAIN | ? | 43 | 40 | +3 (place_cell) | — | pre | single |  | MIXED |
| 08:13 | ITFMATCH-26JUL06STEAUN-STE | ITF_M | leader | 83 | 79 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 08:16 | ATPCHALLENGERMATCH-26JUL06VALZHU-V | ATP_CHALL | leader | 71 | 68 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 08:16 | ATPMATCH-26JUL06DECOB-DE | ATP_MAIN | leader | 74 | 77 | -3 (place_cell) | 2.5 | pre | pair | 97 | MIXED |
| 08:19 | ITFWMATCH-26JUL06BUYALV-ALV | ITF_W | ? | 28 | 16 | +12 (place_cell) | — | pre | single |  | MIXED |
| 08:19 | ATPCHALLENGERMATCH-26JUL06WEHVAN-V | ATP_CHALL | ? | 42 | 39 | +3 (place_cell) | 38.5 | pre | single |  | GIFT_CLASS |
| 08:19 | ATPCHALLENGERMATCH-26JUL06WALNEU-N | ATP_CHALL | ? | 28 | 25 | +3 (place_cell) | 22.0 | pre | pair | 97 | GIFT_CLASS |
| 08:22 | ATPCHALLENGERMATCH-26JUL06WALNEU-W | ATP_CHALL | leader | 69 | 67 | +2 (place_cell) | -23.0 | pre | pair | 97 | EARNED |
| 08:23 | ATPCHALLENGERMATCH-26JUL06VALZHU-Z | ATP_CHALL | ? | 26 | 23 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 08:23 | ITFWMATCH-26JUL06PACLOV-PAC | ITF_W | ? | 61 | 54 | +7 (place_cell) | — | pre | pair | 106 | GIFT_CLASS |
| 08:24 | ITFMATCH-26JUL06TRUTRA-TRA | ITF_M | underdog | 27 | 20 | +7 (place_cell) | — | pre | single |  | MIXED |
| 08:29 | ITFWMATCH-26JUL06ADKFER-FER | ITF_W | underdog | 20 | 12 | +8 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:32 | ITFWMATCH-26JUL06ADKFER-ADK | ITF_W | ? | 77 | 49 | +28 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:32 | WTACHALLENGERMATCH-26JUL06ARANIL-N | WTA_CHALL | ? | 24 | 22 | +2 (place_cell) | 21.5 | pre | pair | 97 | GIFT_CLASS |
| 08:34 | ITFMATCH-26JUL06LENTHE-LEN | ITF_M | ? | 0 | 23 | -23 (place_cell) | — | pre | pair | 65 | MIXED |
| 08:36 | ITFWMATCH-26JUL06PRINIJ-NIJ | ITF_W | underdog | 30 | 26 | +4 (place_cell) | — | pre | single |  | MIXED |
| 08:40 | WTAMATCH-26JUL06PAOEAL-EAL | WTA_MAIN | leader | 58 | 60 | -2 (place_cell) | -1.5 | pre | pair | 97 | MIXED |
| 08:41 | ATPCHALLENGERMATCH-26JUL06RAQRIB-R | ATP_CHALL | ? | 36 | 29 | +7 (place_cell) | 1.5 | pre | pair | 97 | EARNED |
| 08:42 | WTACHALLENGERMATCH-26JUL06BLIAND-A | WTA_CHALL | underdog | 33 | 32 | +1 (place_cell) | -15.5 | pre | pair | 97 | EARNED |
| 08:46 | ITFWMATCH-26JUL06URREVA-EVA | ITF_W | ? | 37 | 19 | +18 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:52 | ATPCHALLENGERMATCH-26JUL06OPIPET-P | ATP_CHALL | leader | 69 | 69 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:58 | ITFMATCH-26JUL06BONFAU-BON | ITF_M | ? | 66 | 63 | +3 (place_cell) | — | pre | pair | 94 | GIFT_CLASS |
| 09:05 | ATPCHALLENGERMATCH-26JUL06PAPMID-P | ATP_CHALL | underdog | 47 | 44 | +3 (place_cell) | — | pre | single |  | PENDING |
| 09:05 | ITFMATCH-26JUL06BONFAU-FAU | ITF_M | ? | 28 | 21 | +7 (place_cell) | — | pre | pair | 94 | EARNED |
| 09:05 | ITFWMATCH-26JUL06KOVDAE-KOV | ITF_W | ? | 76 | 73 | +3 (place_cell) | — | pre | pair | 94 | GIFT_CLASS |
| 09:07 | ITFWMATCH-26JUL06EVARHO-RHO | ITF_W | underdog | 18 | 6 | +12 (place_cell) | — | pre | single |  | PENDING |
| 09:09 | ITFWMATCH-26JUL06SILDIG-SIL | ITF_W | underdog | 9 | 7 | +2 (place_cell) | — | pre | pair | 107 | PENDING |
| 09:10 | ITFWMATCH-26JUL06KOVDAE-DAE | ITF_W | underdog | 18 | 14 | +4 (place_cell) | — | pre | pair | 94 | EARNED |
| 09:10 | WTACHALLENGERMATCH-26JUL06WERSAL-W | WTA_CHALL | underdog | 32 | 28 | +4 (place_cell) | — | pre | single |  | MIXED |
| 09:12 | ITFMATCH-26JUL06LIBNAK-LIB | ITF_M | ? | 40 | 34 | +6 (place_cell) | — | pre | single |  | PENDING |
| 09:13 | ATPCHALLENGERMATCH-26JUL06DONCIZ-D | ATP_CHALL | leader | 73 | 72 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:13 | ITFWMATCH-26JUL06HIEGUT-GUT | ITF_W | leader | 56 | 53 | +3 (place_cell) | — | pre | pair | 96 | PENDING |
| 09:15 | ITFWMATCH-26JUL06MELRAB-RAB | ITF_W | underdog | 12 | 9 | +3 (place_cell) | — | pre | single |  | PENDING |
| 09:15 | ITFWMATCH-26JUL06HIEGUT-HIE | ITF_W | ? | 40 | 37 | +3 (place_cell) | — | pre | pair | 96 | PENDING |
| 09:16 | ITFMATCH-26JUL06TISVER-VER | ITF_M | underdog | 53 | 15 | +38 (place_cell) | — | pre | pair | 97 | PENDING |
| 09:18 | ITFMATCH-26JUL06TISVER-TIS | ITF_M | ? | 44 | 3 | +41 (place_cell) | — | pre | pair | 97 | PENDING |
| 09:19 | ITFMATCH-26JUL06HOSGAT-HOS | ITF_M | ? | 57 | 52 | +5 (place_cell) | — | pre | pair | 95 | MIXED |
| 09:21 | ITFMATCH-26JUL06NAPPIN-PIN | ITF_M | leader | 58 | 55 | +3 (place_cell) | — | pre | pair | 97 | PENDING |
| 09:24 | ATPCHALLENGERMATCH-26JUL06CHIJAN-C | ATP_CHALL | ? | 75 | 73 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:29 | ATPCHALLENGERMATCH-26JUL06BARDAL-B | ATP_CHALL | ? | 56 | 53 | +3 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 09:32 | ITFWMATCH-26JUL06MCAENC-MCA | ITF_W | ? | 42 | 30 | +12 (place_cell) | — | pre | pair | 93 | EARNED |
| 09:32 | ITFMATCH-26JUL06GANVER-GAN | ITF_M | ? | 47 | 42 | +5 (place_cell) | — | pre | pair | 97 | EARNED |
| 09:32 | ATPCHALLENGERMATCH-26JUL06DAMHUE-H | ATP_CHALL | ? | 20 | 16 | +4 (place_cell) | — | pre | single |  | MIXED |
| 09:33 | ITFWMATCH-26JUL06URREVA-URR | ITF_W | ? | 60 | 54 | +6 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:36 | ITFMATCH-26JUL06FIXSAL-FIX | ITF_M | leader | 80 | 91 | -11 (place_cell) | — | pre | pair | 97 | PENDING |
| 09:36 | ITFWMATCH-26JUL06RABELI-ELI | ITF_W | ? | 18 | 5 | +13 (place_cell) | — | pre | single |  | PENDING |
| 09:37 | WTACHALLENGERMATCH-26JUL06WALKAW-K | WTA_CHALL | underdog | 43 | 40 | +3 (place_cell) | 1.5 | pre | pair | 97 | MIXED |
| 09:37 | ITFMATCH-26JUL06GANVER-VER | ITF_M | underdog | 50 | 42 | +8 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:39 | ITFWMATCH-26JUL06KULVOG-VOG | ITF_W | ? | 39 | 32 | +7 (place_cell) | — | pre | single |  | MIXED |
| 09:39 | ITFMATCH-26JUL06NAPPIN-NAP | ITF_M | ? | 39 | 48 | -9 (place_cell) | — | pre | pair | 97 | PENDING |
| 09:40 | ATPCHALLENGERMATCH-26JUL06CHADEM-C | ATP_CHALL | underdog | 48 | 45 | +3 (place_cell) | — | pre | single |  | MIXED |
| 09:41 | ITFMATCH-26JUL06BRABAR-BRA | ITF_M | underdog | 35 | 25 | +10 (place_cell) | — | pre | pair | 97 | PENDING |
| 09:43 | ITFMATCH-26JUL06FIXSAL-SAL | ITF_M | underdog | 17 | 22 | -5 (place_cell) | — | pre | pair | 97 | PENDING |
| 09:43 | ATPCHALLENGERMATCH-26JUL06BARDAL-D | ATP_CHALL | ? | 40 | 38 | +2 (place_cell) | — | pre | pair | 96 | MIXED |
| 09:44 | ITFMATCH-26JUL06BRABAR-BAR | ITF_M | ? | 62 | 59 | +3 (fill_est) | — | pre | pair | 97 | PENDING |
| 09:46 | ATPCHALLENGERMATCH-26JUL06KYMFAU-K | ATP_CHALL | leader | 67 | 64 | +3 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 09:50 | ITFWMATCH-26JUL06LACSTO-STO | ITF_W | ? | 38 | 13 | +25 (place_cell) | — | pre | pair | 97 | MIXED |
| 09:50 | ATPCHALLENGERMATCH-26JUL06KYMFAU-F | ATP_CHALL | ? | 28 | 29 | -1 (place_cell) | — | pre | pair | 95 | EARNED |
| 09:50 | WTACHALLENGERMATCH-26JUL06BASBAD-B | WTA_CHALL | ? | 25 | 21 | +4 (place_cell) | 2.0 | pre | pair | 99 | MIXED |
| 09:50 | WTACHALLENGERMATCH-26JUL06BASBAD-B | WTA_CHALL | leader | 74 | 71 | +3 (place_cell) | -3.0 | pre | pair | 99 | EARNED |
| 09:54 | ATPCHALLENGERMATCH-26JUL06IVADIN-I | ATP_CHALL | ? | 77 | 75 | +2 (place_cell) | -2.5 | pre | pair | 97 | MIXED |
| 09:55 | ITFWMATCH-26JUL06BOWMAT-MAT | ITF_W | leader | 88 | 49 | +39 (place_cell) | — | pre | pair | 96 | PENDING |
| 09:57 | WTACHALLENGERMATCH-26JUL06WALKAW-W | WTA_CHALL | ? | 54 | 52 | +2 (place_cell) | -4.5 | pre | pair | 97 | EARNED |
| 10:00 | ITFWMATCH-26JUL06SILDIG-DIG | ITF_W | leader | 98 | 92 | +6 (place_cell) | — | pre | pair | 107 | PENDING |
| 10:01 | ITFMATCH-26JUL06JAIHEN-JAI | ITF_M | underdog | 46 | 41 | +5 (place_cell) | — | pre | single |  | PENDING |
| 10:03 | ITFMATCH-26JUL06ALIMIS-MIS | ITF_M | ? | 6 | 2 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 10:05 | ATPCHALLENGERMATCH-26JUL06ZEBAND-Z | ATP_CHALL | underdog | 20 | 17 | +3 (place_cell) | — | pre | single |  | PENDING |
| 10:06 | ITFMATCH-26JUL06ROURAM-ROU | ITF_M | ? | 37 | 33 | +4 (place_cell) | — | pre | single |  | PENDING |
| 10:06 | ITFWMATCH-26JUL06SCHELI-ELI | ITF_W | underdog | 41 | 1 | +40 (place_cell) | — | pre | single |  | PENDING |
| 10:08 | ITFWMATCH-26JUL06LACSTO-LAC | ITF_W | leader | 59 | 84 | -25 (place_cell) | — | pre | pair | 97 | MIXED |
| 10:10 | ATPCHALLENGERMATCH-26JUL06FOMDHA-D | ATP_CHALL | ? | 52 | 49 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 10:10 | ITFWMATCH-26JUL06REEION-ION | ITF_W | ? | 59 | 49 | +10 (place_cell) | — | pre | single |  | PENDING |
| 10:10 | ITFMATCH-26JUL06LAPCIO-CIO | ITF_M | ? | 42 | 37 | +5 (place_cell) | — | pre | single |  | PENDING |
| 10:11 | ITFWMATCH-26JUL06BOWMAT-BOW | ITF_W | underdog | 8 | 2 | +6 (place_cell) | — | pre | pair | 96 | PENDING |

## RESTING BIDS — 149 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 27, 'FLOW_ABOVE': 53, 'NO_FLOW': 69} | repriceable now: true 12 / false 137 | **cumulative bid_grade lines: 2274 (repriceable true 215 / false 2059)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06BARZIN-B | 52 | 190m | 0 | 52-54 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06BARZIN-Z | 45 | 190m | 1/48-48/12 | 47-48 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ATPCHALLENGERMATCH-26JUL06CHADEM-D | 49 | 188m | 32/52-83/16830 | 76-77 | 3 | **FLOW_ABOVE** | 49 | flow above but bound 49c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06CHADEM-D | 49 | 29m | 31/60-83/16829 | 76-77 | 11 | **FLOW_ABOVE** | 49 | flow above but bound 49c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06CLAPAP-C | 72 | 190m | 3/74-75/7 | 74-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ATPCHALLENGERMATCH-26JUL06CLAPAP-P | 26 | 190m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DAMHUE-D | 77 | 39m | 54/78-98/11135 | 95-97 | 1 | **FLOW_ABOVE** | 77 | flow above but bound 77c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06DEHUD-DE | 38 | 310m | 2/39-39/122 | 38-39 | 1 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06DEHUD-HU | 61 | 310m | 1/62-62/5 | 61-62 | 1 | **FLOW_ABOVE** | 59 | flow above but bound 59c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06FOMDHA-F | 45 | 311m | 2/46-46/39 | 45-49 | 1 | **FLOW_ABOVE** | 45 | flow above but bound 45c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06FOMDHA-F | 42 | 2m | 0 | 45-49 | — | **NO_FLOW** | 45 |  |
| ATPCHALLENGERMATCH-26JUL06GLIYUN-G | 16 | 11m | 0 | 16-17 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GLIYUN-Y | 83 | 11m | 0 | 83-84 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | 23 | 259m | 149/1-25/45244 | 2-1 | -22 | **FLOW_AT_LEVEL** | 23 |  |
| ATPCHALLENGERMATCH-26JUL06GOMRIB-G | 18 | 11m | 0 | 18-20 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMRIB-R | 80 | 11m | 0 | 80-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HOLSCH-H | 47 | 11m | 0 | 47-49 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HUETEN-H | 60 | 190m | 3/71-73/7 | 70-73 | 11 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HUETEN-T | 28 | 190m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ILARYB-I | 52 | 189m | 1/57-57/2 | 53-56 | 5 | **FLOW_ABOVE** | 54 | flow above but bound 54c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06ILARYB-R | 45 | 189m | 2/47-47/21 | 45-47 | 2 | **FLOW_ABOVE** | 44 | flow above but bound 44c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06JUNMOR-J | 51 | 100m | 1/54-54/13 | 53-54 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ATPCHALLENGERMATCH-26JUL06JUNMOR-M | 46 | 100m | 0 | 46-48 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KASCIN-C | 54 | 281m | 6/56-57/1207 | 55-57 | 2 | **FLOW_ABOVE** | 53 | flow above but bound 53c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06KASCIN-K | 43 | 281m | 5/44-46/741 | 44-45 | 1 | **FLOW_ABOVE** | 41 | flow above but bound 41c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06KOZJOH-J | 31 | 158m | 1/34-34/70 | 31-34 | 3 | **FLOW_ABOVE** | 31 | flow above but bound 31c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06KOZJOH-K | 66 | 188m | 1/68-68/5 | 66-68 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 5 | 357m | 338/1-21/41967 | 19-1 | -4 | **FLOW_AT_LEVEL** | 5 |  |
| ATPCHALLENGERMATCH-26JUL06KYMFAU-K | 69 | 6m | 16/91-93/6048 | 92-94 | 22 | **FLOW_ABOVE** | 66 | flow above but bound 66c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06MAGROD-M | 44 | 101m | 0 | 44-46 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MAGROD-R | 54 | 101m | 0 | 54-56 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MALMAT-M | 43 | 100m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MALMAT-M | 49 | 100m | 0 | 49-51 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MAXGHI-G | 55 | 221m | 1/56-56/129 | 55-57 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ATPCHALLENGERMATCH-26JUL06MAXGHI-M | 43 | 221m | 2/44-45/5 | 43-45 | 1 | **FLOW_ABOVE** | 42 | flow above but bound 42c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06MONCOU-M | 66 | 26m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06OLIDAN-D | 64 | 190m | 5/66-66/27 | 65-66 | 2 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06OLIDAN-O | 35 | 4m | 0 | 35-36 | — | **NO_FLOW** | 32 |  |
| ATPCHALLENGERMATCH-26JUL06PALKOL-K | 75 | 101m | 0 | 75-77 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PALKOL-P | 24 | 101m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PAPMID-M | 50 | 67m | 6/52-54/423 | 53-54 | 2 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PERMEL-M | 95 | 101m | 18/95-95/1500 | 95-96 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PERMEL-P | 4 | 101m | 24/5-5/1849 | 4-5 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→5 |
| ATPCHALLENGERMATCH-26JUL06POPSAN-P | 93 | 108m | 4/94-95/156 | 93-94 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→94 |
| ATPCHALLENGERMATCH-26JUL06POPSAN-S | 8 | 5m | 0 | 8-12 | — | **NO_FLOW** | 6 |  |
| ATPCHALLENGERMATCH-26JUL06REHKOU-R | 53 | 121m | 42/56-81/11610 | 79-80 | 3 | **FLOW_ABOVE** | 53 | flow above but bound 53c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06REHKOU-R | 53 | 11m | 16/77-81/1026 | 79-80 | 24 | **FLOW_ABOVE** | 53 | flow above but bound 53c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-B | 36 | 198m | 172/36-99/38561 | 99-71 | 0 | **FLOW_AT_LEVEL** | 34 |  |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 262m | 111/1-60/13885 | 4-1 | -32 | **FLOW_AT_LEVEL** | 33 |  |
| ATPCHALLENGERMATCH-26JUL06WEIGRA-G | 81 | 220m | 3/82-82/35 | 81-82 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ATPCHALLENGERMATCH-26JUL06WEIGRA-W | 19 | 143m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ZEBAND-A | 77 | 6m | 0 | 79-80 | — | **NO_FLOW** | 77 |  |
| ATPMATCH-26JUL06DIMFER-DIM | 64 | 242m | 179/67-68/29435 | 67-68 | 3 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ATPMATCH-26JUL06DIMFER-DIM | 64 | 184m | 157/67-68/27925 | 67-68 | 3 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ATPMATCH-26JUL06FRIBUB-BUB | 33 | 92m | 37/34-34/4096 | 33-34 | 1 | **FLOW_ABOVE** | 31 | flow above but bound 31c < flow -- chasing breaks goal |
| ATPMATCH-26JUL06FRIBUB-FRI | 66 | 161m | 147/66-67/15991 | 66-67 | 0 | **FLOW_AT_LEVEL** | 67 |  |
| ATPMATCH-26JUL06LEHZVE-LEH | 26 | 92m | 13/27-27/2365 | 26-27 | 1 | **FLOW_ABOVE** | 25 | flow above but bound 25c < flow -- chasing breaks goal |
| ATPMATCH-26JUL06LEHZVE-ZVE | 73 | 130m | 57/73-74/8237 | 73-74 | 0 | **FLOW_AT_LEVEL** | 74 |  |
| ITFMATCH-26JUL06ALEREG-REG | 40 | 368m | 99/49-99/9602 | 99-99 | 9 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BROTHU-BRO | 36 | 190m | 1/45-45/21 | 36-42 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06BROTHU-THU | 57 | 11m | 0 | 57-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06CUNLIM-CUN | 78 | 12m | 0 | 78-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06CUNLIM-LIM | 22 | 11m | 0 | 22-24 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DONDEV-DEV | 20 | 188m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DONDEV-DON | 73 | 26m | 0 | 73-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06FIXSAL-SAL | 17 | 24m | 8/5-15/99 | 4-5 | -12 | **FLOW_AT_LEVEL** | 17 |  |
| ITFMATCH-26JUL06GARPER-GAR | 60 | 7m | 0 | 60-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GARPER-PER | 21 | 6m | 0 | 21-41 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 520m | 213/1-19/18095 | 18-1 | -15 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06IAMBEN-BEN | 20 | 30m | 0 | 20-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06IAMBEN-IAM | 53 | 28m | 0 | 53-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06JAIHEN-HEN | 51 | 2m | 1/66-66/31 | 63-66 | 15 | **FLOW_ABOVE** | 51 | flow above but bound 51c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06KASLIL-LIL | 28 | 353m | 205/1-55/9114 | 1-1 | -27 | **FLOW_AT_LEVEL** | 31 |  |
| ITFMATCH-26JUL06LAPCIO-LAP | 55 | 2m | 1/68-68/35 | 64-68 | 13 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06LENTHE-LEN | 32 | 246m | 203/32-99/19319 | 98-99 | 0 | **FLOW_AT_LEVEL** | 32 |  |
| ITFMATCH-26JUL06LUEVAN-LUE | 73 | 28m | 1/73-73/1 | 73-77 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL06LUEVAN-VAN | 22 | 93m | 0 | 22-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MOUCAR-CAR | 27 | 41m | 0 | 27-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MOUCAR-MOU | 67 | 28m | 0 | 67-73 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06PESTER-PES | 43 | 73m | 1/50-50/5 | 43-64 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-BEC | 87 | 371m | 89/91-99/6543 | 99-99 | 4 | **FLOW_ABOVE** | 87 | flow above but bound 87c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06ROURAM-RAM | 54 | 13m | 1/65-65/1 | 54-64 | 11 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06STEAUN-AUN | 14 | 66m | 433/1-35/61629 | 1-2 | -13 | **FLOW_AT_LEVEL** | 14 |  |
| ITFMATCH-26JUL06SURMED-MED | 56 | 9m | 0 | 56-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SURMED-SUR | 28 | 9m | 0 | 28-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VANHOR-HOR | 30 | 249m | 2/36-36/16 | 31-59 | 6 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06VANHOR-HOR | 31 | 5m | 0 | 31-59 | — | **NO_FLOW** | 34 |  |
| ITFMATCH-26JUL06VULCOU-VUL | 81 | 354m | 11/98-99/1550 | 99-85 | 17 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06XUXBER-BER | 28 | 2m | 0 | 28-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06XUXBER-XUX | 60 | 2m | 0 | 60-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 415m | 155/28-99/15825 | 98-99 | 8 | **FLOW_ABOVE** | 20 | flow above but bound 20c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 542m | 4430/1-99/518199 | 5-1 | -33 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06BUYALV-BUY | 69 | 100m | 196/69-98/15937 | 69-71 | 0 | **FLOW_AT_LEVEL** | 69 |  |
| ITFWMATCH-26JUL06CENBUL-BUL | 20 | 157m | 0 | 20-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CENBUL-CEN | 69 | 86m | 0 | 69-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06COHXAV-COH | 43 | 10m | 0 | 43-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DRISLA-DRI | 36 | 53m | 1/40-40/2 | 36-41 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| ITFWMATCH-26JUL06DRISLA-SLA | 60 | 202m | 0 | 60-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EVARHO-EVA | 79 | 29m | 0 | 88-92 | — | **NO_FLOW** | 79 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 25 | 336m | 1/99-99/12 | 99-58 | 74 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 400m | 73/79-99/2231 | 98-99 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 400m | 73/79-99/2231 | 98-99 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULVOG-KUL | 55 | 208m | 17/60-76/298 | 58-60 | 5 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULVOG-KUL | 58 | 21m | 0 | 58-60 | — | **NO_FLOW** | 58 |  |
| ITFWMATCH-26JUL06LABTSY-LAB | 27 | 280m | 0 | 27-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LABTSY-TSY | 62 | 25m | 0 | 62-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 588m | 3895/23-99/459986 | 99-24 | -14 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06MARBED-BED | 17 | 34m | 0 | 18-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARBED-MAR | 61 | 35m | 0 | 66-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARGLU-GLU | 68 | 24m | 0 | 68-71 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARGLU-MAR | 29 | 157m | 0 | 29-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MULCIS-CIS | 39 | 3m | 0 | 39-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MULCIS-MUL | 55 | 25m | 0 | 55-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-PRI | 41 | 254m | 828/36-99/114162 | 99-99 | -5 | **FLOW_AT_LEVEL** | 41 |  |
| ITFWMATCH-26JUL06OLUZAM-OLU | 41 | 29m | 0 | 41-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 492m | 1942/1-13/312225 | 14-1 | -7 | **FLOW_AT_LEVEL** | 12 |  |
| ITFWMATCH-26JUL06PEEPAH-PEE | 39 | 206m | 195/1-51/28627 | 2-3 | -38 | **FLOW_AT_LEVEL** | 36 |  |
| ITFWMATCH-26JUL06PIERAD-PIE | 64 | 300m | 117/84-99/4782 | 99-90 | 20 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06POHSTU-POH | 28 | 161m | 0 | 28-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06POHSTU-STU | 67 | 25m | 0 | 67-71 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06RABELI-RAB | 79 | 32m | 0 | 89-92 | — | **NO_FLOW** | 79 |  |
| ITFWMATCH-26JUL06REEION-REE | 38 | 2m | 0 | 43-47 | — | **NO_FLOW** | 38 |  |
| ITFWMATCH-26JUL06SACLAZ-LAZ | 15 | 347m | 648/1-33/45125 | 40-1 | -14 | **FLOW_AT_LEVEL** | 1 |  |
| ITFWMATCH-26JUL06SCHELI-SCH | 56 | 3m | 0 | 71-75 | — | **NO_FLOW** | 56 |  |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 538m | 16366/1-95/1383948 | 83-1 | -13 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06SINUSU-SIN | 35 | 6m | 0 | 35-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SINUSU-USU | 53 | 1m | 0 | 55-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06STETRA-STE | 80 | 4m | 0 | 80-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06STETRA-TRA | 17 | 5m | 0 | 17-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 538m | 6096/1-29/750264 | 21-1 | -14 | **FLOW_AT_LEVEL** | 5 |  |
| ITFWMATCH-26JUL06VARMUN-MUN | 15 | 130m | 0 | 15-16 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VARMUN-VAR | 85 | 31m | 0 | 85-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-VLA | 30 | 234m | 573/1-54/39141 | 1-2 | -29 | **FLOW_AT_LEVEL** | 23 |  |
| WTACHALLENGERMATCH-26JUL06COLSMI-C | 38 | 101m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06COLSMI-S | 60 | 101m | 1/62-62/35 | 60-62 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→62 |
| WTACHALLENGERMATCH-26JUL06CURDOD-C | 68 | 161m | 2/70-70/193 | 69-70 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| WTACHALLENGERMATCH-26JUL06CURDOD-D | 31 | 100m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06DENQUE-D | 5 | 145m | 18/5-7/1410 | 5-6 | 0 | **FLOW_AT_LEVEL** | 3 |  |
| WTACHALLENGERMATCH-26JUL06DENQUE-Q | 93 | 281m | 1/95-95/18 | 93-95 | 2 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 39 | 261m | 108/84-99/18486 | 99-99 | 45 | **FLOW_ABOVE** | 39 | flow above but bound 39c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ISHCRO-C | 61 | 190m | 0 | 61-62 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06ISHCRO-I | 38 | 190m | 2/39-39/123 | 38-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| WTACHALLENGERMATCH-26JUL06LINMAR-L | 6 | 188m | 13/6-7/409 | 6-7 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL06LINMAR-M | 93 | 188m | 0 | 94-95 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06OLIUCH-U | 39 | 248m | 2066/11-99/409246 | 99-95 | -28 | **FLOW_AT_LEVEL** | 37 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-S | 65 | 61m | 0 | 69-70 | — | **NO_FLOW** | 65 |  |
| WTAMATCH-26JUL06BOUMER-BOU | 46 | 106m | 1173/1-67/319976 | 5-2 | -45 | **FLOW_AT_LEVEL** | 44 |  |
| WTAMATCH-26JUL06KEYNOS-KEY | 54 | 119m | 104/57-59/8324 | 57-58 | 3 | **FLOW_ABOVE** | 54 | flow above but bound 54c < flow -- chasing breaks goal |
| WTAMATCH-26JUL06KEYNOS-KEY | 54 | 119m | 104/57-59/8324 | 57-58 | 3 | **FLOW_ABOVE** | 54 | flow above but bound 54c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06BUYALV | 28 | 71 | **99** | 97 | +2 |
| ITFWMATCH-26JUL06KULVOG | 39 | 60 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06ZEBAND | 20 | 80 | **100** | 97 | +3 |
| ATPMATCH-26JUL06DIMFER | 33 | 68 | **101** | 97 | +4 |
| WTAMATCH-26JUL06KEYNOS | 43 | 58 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL06PAPMID | 47 | 54 | **101** | 97 | +4 |
| ITFMATCH-26JUL06ROURAM | 37 | 64 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL06FOMDHA | 52 | 49 | **101** | 97 | +4 |
| WTACHALLENGERMATCH-26JUL06WERSAL | 32 | 70 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06REEION | 59 | 47 | **106** | 97 | +9 |
| ITFWMATCH-26JUL06RICMIT | 9 | 99 | **108** | 97 | +11 |
| ATPCHALLENGERMATCH-26JUL06SEYMAR | 10 | 99 | **109** | 97 | +12 |
| ITFMATCH-26JUL06ROJBEC | 10 | 99 | **109** | 97 | +12 |
| ITFWMATCH-26JUL06EVARHO | 18 | 92 | **110** | 97 | +13 |
| ITFWMATCH-26JUL06RABELI | 18 | 92 | **110** | 97 | +13 |
| ITFMATCH-26JUL06LAPCIO | 42 | 68 | **110** | 97 | +13 |
| ITFMATCH-26JUL06JAIHEN | 46 | 66 | **112** | 97 | +15 |
| ITFMATCH-26JUL06CASBAY | 45 | 71 | **116** | 97 | +19 |
| ITFWMATCH-26JUL06SCHELI | 41 | 75 | **116** | 97 | +19 |
| ATPCHALLENGERMATCH-26JUL06DAMHUE | 20 | 97 | **117** | 97 | +20 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ITFWMATCH-26JUL06KULGON | 22 | 99 | **121** | 97 | +24 |
| ATPCHALLENGERMATCH-26JUL06PAPJAN | 53 | 69 | **122** | 97 | +25 |
| ITFMATCH-26JUL06VANHOR | 63 | 59 | **122** | 97 | +25 |
| ITFWMATCH-26JUL06PIERAD | 33 | 90 | **123** | 97 | +26 |
| ATPCHALLENGERMATCH-26JUL06REHKOU | 44 | 80 | **124** | 97 | +27 |
| ATPCHALLENGERMATCH-26JUL06CHADEM | 48 | 77 | **125** | 97 | +28 |
| ITFMATCH-26JUL06TRUTRA | 27 | 99 | **126** | 97 | +29 |
| ITFWMATCH-26JUL06PRINIJ | 30 | 99 | **129** | 97 | +32 |
| ITFMATCH-26JUL06STAGUI | 37 | 99 | **136** | 97 | +39 |
| ITFWMATCH-26JUL06OKASAK | 40 | 99 | **139** | 97 | +42 |
| ATPCHALLENGERMATCH-26JUL06WEHVAN | 42 | 99 | **141** | 97 | +44 |
| WTACHALLENGERMATCH-26JUL06ROMSEM | 57 | 92 | **149** | 97 | +52 |
| ITFMATCH-26JUL06ALEREG | 51 | 99 | **150** | 97 | +53 |
| ITFWMATCH-26JUL06WONIBR | 65 | 99 | **164** | 97 | +67 |
| ITFWMATCH-26JUL06BOIBOY | 77 | 99 | **176** | 97 | +79 |
| ITFWMATCH-26JUL06GALTSE | 77 | 99 | **176** | 97 | +79 |

## PATTERNS (sub-B) — 214
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
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 606, "mode": "SET_BELOW_FLOW(prints 74c above)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 29, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 30, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 31, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 32, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LUKNOE-LUK {"price": 59, "ceiling": 18}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LUKNOE-LUK {"price": 66, "ceiling": 18}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 579, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LUKNOE-LUK {"price": 67, "ceiling": 18}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ELDHAU-ELD {"price": 59, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LUKNOE-LUK {"price": 68, "ceiling": 18}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 33, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VLADIL-VLA {"price": 39, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VLADIL-VLA {"price": 40, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06IVAKUH-IVA {"price": 60, "ceiling": 54}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06IVAKUH-IVA {"price": 61, "ceiling": 54}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06IVAKUH-IVA {"price": 62, "ceiling": 54}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06KULGON-GON {"price": 17, "ceiling": 13}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06KULGON-GON {"price": 20, "ceiling": 13}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SPIMED-SPI {"price": 83, "ceiling": 78}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06LENTHE-THE {"price": 63, "ceiling": 34}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06LENTHE-THE {"price": 65, "ceiling": 34}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06BOSTOP-TOP {"price": 33, "ceiling": 21}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06ILIEBE-EBE {"price": 49, "ceiling": 42}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06ILIEBE-EBE {"price": 51, "ceiling": 42}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06ILIEBE-EBE {"price": 52, "ceiling": 42}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 18, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 19, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 20, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 21, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 22, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SPIMED-SPI {"price": 84, "ceiling": 78}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 23, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SPIMED-SPI {"price": 85, "ceiling": 78}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ELDHAU-ELD {"price": 60, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 24, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ELDHAU-ELD {"price": 64, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 25, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06KULGON-GON {"price": 21, "ceiling": 13}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 26, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06KULGON-GON {"price": 22, "ceiling": 13}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 28, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LUKNOE-LUK {"price": 69, "ceiling": 18}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SPIMED-SPI {"price": 86, "ceiling": 78}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06WAGYOU-WAG {"price": 29, "ceiling": 17}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06GANPUI-PUI {"price": 10, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 54, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ALIMIS-ALI {"price": 85, "ceiling": 84}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ALIMIS-ALI {"price": 86, "ceiling": 84}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06GANPUI-PUI {"price": 11, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 55, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TRUTRA-TRA {"price": 24, "ceiling": 22}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 23, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PODLUK-POD {"price": 16, "ceiling": 11}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 11, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 13, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 24, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PODLUK-POD {"price": 22, "ceiling": 11}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 14, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PODLUK-POD {"price": 23, "ceiling": 11}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 25, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 15, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06BUYALV-ALV {"price": 22, "ceiling": 21}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PODLUK-POD {"price": 25, "ceiling": 11}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PODLUK-POD {"price": 26, "ceiling": 11}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 51, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 52, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VLADIL-VLA {"price": 41, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 53, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VIRKOV-VIR {"price": 55, "ceiling": 32}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 54, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VIRKOV-VIR {"price": 56, "ceiling": 32}
- half_arm_aging: KXITFWMATCH-26JUL06BOIBOY-BOI {"fill": 77, "age_min": 415, "mode": "SET_BELOW_FLOW(prints 8c above)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06DIANIK-NIK {"price": 41, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06DIANIK-NIK {"price": 52, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 16, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PRINIJ-NIJ {"price": 21, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PRINIJ-NIJ {"price": 30, "ceiling": 20}
- half_arm_aging: KXITFWMATCH-26JUL06KULGON-GON {"fill": 22, "age_min": 401, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06JOSKUM-JOS {"price": 61, "ceiling": 59}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06JOSKUM-JOS {"price": 67, "ceiling": 59}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 18, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 56, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 19, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 57, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 20, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 26, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 58, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 21, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 22, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ALIMIS-ALI {"price": 87, "ceiling": 84}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ALIMIS-ALI {"price": 90, "ceiling": 84}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 24, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 59, "ceiling": 38}
- half_arm_aging: KXITFMATCH-26JUL06CASBAY-CAS {"fill": 45, "age_min": 350, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 26, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ALIMIS-ALI {"price": 91, "ceiling": 84}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06GANVER-VER {"price": 47, "ceiling": 45, "emitted_et": "2026-07-06 10:11:44 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 27, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TEISCH-TEI {"price": 80, "ceiling": 79}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 27, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 62, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TEISCH-TEI {"price": 81, "ceiling": 79}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SPIMED-SPI {"price": 87, "ceiling": 78}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 28, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06GALTSE-GAL {"price": 77, "ceiling": 76}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ELDHAU-ELD {"price": 65, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 60, "ceiling": 31}
- deep_neg_fv: KXITFWMATCH-26JUL06OKUPRI-PRI {"entry_minus_fv_burst": -45.5}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TEISCH-TEI {"price": 82, "ceiling": 79}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TEISCH-TEI {"price": 87, "ceiling": 79}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06NOHBUR-BUR {"entry_minus_fv_burst": -48.5}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 29, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 30, "ceiling": 9}
- half_arm_aging: KXITFWMATCH-26JUL06PIERAD-RAD {"fill": 33, "age_min": 300, "mode": "SET_BELOW_FLOW(prints 20c above)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 31, "ceiling": 9}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06PAPJAN-PAP {"fill": 53, "age_min": 299, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 32, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 33, "ceiling": 9}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06MONPOP-MON {"entry_minus_fv_burst": -35.5}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 34, "ceiling": 9}
- half_arm_aging: KXITFWMATCH-26JUL06RICMIT-MIT {"fill": 9, "age_min": 286, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PODLUK-POD {"price": 27, "ceiling": 11}
- deep_neg_fv: KXITFWMATCH-26JUL06PEEPAH-PAH {"entry_minus_fv_burst": -26.5}
- half_arm_aging: KXITFWMATCH-26JUL06GALTSE-GAL {"fill": 77, "age_min": 276, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 35, "ceiling": 9}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SEYMAR-MAR {"fill": 10, "age_min": 271, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06LEWMAR-MAR {"entry_minus_fv_burst": -24.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06GOMLUZ-GOM {"entry_minus_fv_burst": -26.5}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 36, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06STAGUI-GUI {"price": 37, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06EWAMAN-EWA {"price": 69, "ceiling": 68}
- half_arm_aging: KXITFMATCH-26JUL06ALEREG-ALE {"fill": 51, "age_min": 257, "mode": "SET_BELOW_FLOW(prints 9c above)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06GANVER-VER {"price": 48, "ceiling": 45, "emitted_et": "2026-07-06 10:11:44 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06KARVIS-VIS {"price": 18, "ceiling": 16}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06KARVIS-VIS {"price": 21, "ceiling": 16}
- half_arm_aging: KXITFMATCH-26JUL06VANHOR-VAN {"fill": 63, "age_min": 245, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- deep_neg_fv: KXITFWMATCH-26JUL06VLADIL-DIL {"entry_minus_fv_burst": -32.0}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06ILIEBE-EBE {"price": 53, "ceiling": 42}
- half_arm_aging: KXATPMATCH-26JUL06DIMFER-FER {"fill": 33, "age_min": 242, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06ILIEBE-EBE {"price": 58, "ceiling": 42}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06DELWAL-DEL {"entry_minus_fv_burst": -16.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06BASHOE-HOE {"entry_minus_fv_burst": -47.5}
- deep_neg_fv: KXWTAMATCH-26JUL06KRUKOS-KOS {"entry_minus_fv_burst": -18.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06SEGBRA-BRA {"entry_minus_fv_burst": -47.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06POTFEL-FEL {"entry_minus_fv_burst": -25.5}
- uncorrelated_buy_above_ceiling: KXWTACHALLENGERMATCH-26JUL06GRAMAS-GRA {"price": 33, "ceiling": 32}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 69, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 28, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06EWAMAN-EWA {"price": 70, "ceiling": 68}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06GRAMAS-MAS {"entry_minus_fv_burst": -10.5}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06ROMSEM-SEM {"fill": 57, "age_min": 203, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 29, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 30, "ceiling": 20}
- deep_neg_fv: KXITFWMATCH-26JUL06MILHER-MIL {"entry_minus_fv_burst": -17.5}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06HESPAL-HES {"entry_minus_fv_burst": -59.5}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 31, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 34, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 35, "ceiling": 20}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06MARBER-BER {"entry_minus_fv_burst": -33.5}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06FAVKLY-KLY {"price": 41, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TRUTRA-TRA {"price": 25, "ceiling": 22}
- half_arm_aging: KXITFMATCH-26JUL06STAGUI-GUI {"fill": 37, "age_min": 147, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 36, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 37, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 41, "ceiling": 20}
- half_arm_aging: KXITFWMATCH-26JUL06OKASAK-OKA {"fill": 40, "age_min": 138, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06ARANIL-ARA {"entry_minus_fv_burst": -24.5}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TEUHAS-TEU {"price": 35, "ceiling": 34}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06BUYALV-ALV {"price": 23, "ceiling": 21}
- half_arm_aging: KXITFMATCH-26JUL06ROJBEC-ROJ {"fill": 10, "age_min": 125, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TRUTRA-TRA {"price": 26, "ceiling": 22}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06REHKOU-KOU {"fill": 44, "age_min": 121, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TRUTRA-TRA {"price": 27, "ceiling": 22}
- half_arm_aging: KXWTAMATCH-26JUL06KEYNOS-NOS {"fill": 43, "age_min": 120, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06BUYALV-ALV {"fill": 28, "age_min": 113, "mode": "QUEUE(flow at/below our level, unfilled)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06WEHVAN-VAN {"fill": 42, "age_min": 113, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06WALNEU-WAL {"entry_minus_fv_burst": -23.0}
- half_arm_aging: KXITFMATCH-26JUL06TRUTRA-TRA {"fill": 27, "age_min": 107, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL06PRINIJ-NIJ {"fill": 30, "age_min": 95, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06BLIAND-AND {"entry_minus_fv_burst": -15.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06PAPMID-PAP {"fill": 47, "age_min": 67, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06EVARHO-RHO {"fill": 18, "age_min": 65, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06WERSAL-WER {"fill": 32, "age_min": 61, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFMATCH-26JUL06LIBNAK-LIB {"fill": 40, "age_min": 59, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL06MELRAB-RAB {"fill": 12, "age_min": 56, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06GANVER-VER {"price": 49, "ceiling": 45, "emitted_et": "2026-07-06 10:11:44 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06GANVER-VER {"price": 50, "ceiling": 45, "emitted_et": "2026-07-06 10:11:44 AM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06DAMHUE-HUE {"fill": 20, "age_min": 39, "mode": "SET_BELOW_FLOW(prints 1c above)", "emitted_et": "2026-07-06 10:11:44 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL06RABELI-ELI {"fill": 18, "age_min": 35, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-06 10:11:44 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL06KULVOG-VOG {"fill": 39, "age_min": 33, "mode": "SET_BELOW_FLOW(prints 5c above)", "emitted_et": "2026-07-06 10:11:44 AM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06CHADEM-CHA {"fill": 48, "age_min": 32, "mode": "SET_BELOW_FLOW(prints 3c above)", "emitted_et": "2026-07-06 10:11:44 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
