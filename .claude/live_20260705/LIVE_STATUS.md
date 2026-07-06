# LIVE VALIDATION — rolling status

- cycle 127 @ **2026-07-06 08:26:36 AM ET** | build `7e675a7` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 146074 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 28 violation(s)
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

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_combined_over_goal.md**

## FILLS — 214 graded (session)
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
| 05:12 | ATPCHALLENGERMATCH-26JUL06PAPJAN-P | ATP_CHALL | ? | 53 | 50 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 05:12 | WTACHALLENGERMATCH-26JUL06BULSTR-B | WTA_CHALL | ? | 68 | 68 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:13 | ITFWMATCH-26JUL06TRIVOR-VOR | ITF_W | leader | 89 | 49 | +40 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:15 | ITFWMATCH-26JUL06TRIVOR-TRI | ITF_W | ? | 8 | 1 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:15 | ITFWMATCH-26JUL06TEISCH-SCH | ITF_W | ? | 4 | 2 | +2 (place_cell) | — | pre | pair | 90 | EARNED |
| 05:16 | ITFWMATCH-26JUL06POPSOL-SOL | ITF_W | ? | 61 | 50 | +11 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:17 | ATPCHALLENGERMATCH-26JUL06STALEC-L | ATP_CHALL | underdog | 32 | 30 | +2 (place_cell) | — | pre | pair | 96 | EARNED |
| 05:18 | ITFMATCH-26JUL06LENTHE-THE | ITF_M | ? | 65 | 56 | +9 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 05:20 | WTACHALLENGERMATCH-26JUL06MONPOP-M | WTA_CHALL | underdog | 43 | 41 | +2 (place_cell) | -35.5 | pre | pair | 97 | EARNED |
| 05:22 | ATPCHALLENGERMATCH-26JUL06PRIORA-O | ATP_CHALL | ? | 39 | 37 | +2 (place_cell) | -5.0 | pre | pair | 95 | EARNED |
| 05:25 | ITFWMATCH-26JUL06RICMIT-MIT | ITF_W | ? | 9 | 3 | +6 (place_cell) | — | pre | single |  | MIXED |
| 05:26 | ATPMATCH-26JUL06DECOB-COB | ATP_MAIN | underdog | 23 | 22 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:28 | ITFWMATCH-26JUL06IVAKUH-KUH | ITF_W | ? | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:30 | ITFMATCH-26JUL06DUGHOF-HOF | ITF_M | ? | 21 | 6 | +15 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:31 | ITFWMATCH-26JUL06PEEPAH-PAH | ITF_W | ? | 58 | 6 | +52 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 05:32 | ITFWMATCH-26JUL06JOSKUM-KUM | ITF_W | underdog | 28 | 31 | -3 (place_cell) | — | pre | pair | 95 | EARNED |
| 05:32 | ATPCHALLENGERMATCH-26JUL06NIJRAH-N | ATP_CHALL | ? | 56 | 57 | -1 (window_cell) | — | pre | pair | 96 | MIXED |
| 05:32 | ITFWMATCH-26JUL06SPIMED-MED | ITF_W | ? | 8 | 1 | +7 (place_cell) | — | pre | pair | 96 | EARNED |
| 05:35 | ITFWMATCH-26JUL06GALTSE-GAL | ITF_W | leader | 77 | 71 | +6 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 05:38 | ITFWMATCH-26JUL06MILHER-HER | ITF_W | underdog | 16 | 3 | +13 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:39 | ATPCHALLENGERMATCH-26JUL06PIEMOL-P | ATP_CHALL | ? | 45 | 41 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:40 | ITFMATCH-26JUL06BEASCO-BEA | ITF_M | leader | 64 | 63 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:40 | ATPCHALLENGERMATCH-26JUL06SEYMAR-M | ATP_CHALL | underdog | 10 | 6 | +4 (place_cell) | — | pre | single |  | MIXED |
| 05:41 | ATPCHALLENGERMATCH-26JUL06POLHAI-P | ATP_CHALL | underdog | 31 | 28 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:41 | WTACHALLENGERMATCH-26JUL06LEWMAR-M | WTA_CHALL | ? | 43 | 40 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
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
| 06:02 | ITFWMATCH-26JUL06PEEPAH-PEE | ITF_W | underdog | 38 | 4 | +34 (place_cell) | — | pre | pair | 96 | MIXED |
| 06:05 | ITFMATCH-26JUL06TEXCAR-TEX | ITF_M | leader | 67 | 74 | -7 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 06:06 | ITFWMATCH-26JUL06KOTCHI-CHI | ITF_W | ? | 45 | 23 | +22 (window_cell) | — | pre | pair | 97 | MIXED |
| 06:06 | ITFWMATCH-26JUL06PODLUK-LUK | ITF_W | leader | 70 | 53 | +17 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:07 | ITFMATCH-26JUL06VANHOR-VAN | ITF_M | leader | 63 | 60 | +3 (place_cell) | — | pre | single |  | PENDING |
| 06:07 | ITFWMATCH-26JUL06KARVIS-VIS | ITF_W | ? | 21 | 8 | +13 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:09 | ITFWMATCH-26JUL06VLADIL-DIL | ITF_W | leader | 56 | 52 | +4 (place_cell) | -32.0 | pre | pair | 97 | EARNED |
| 06:09 | ATPMATCH-26JUL06DIMFER-FER | ATP_MAIN | underdog | 33 | 31 | +2 (place_cell) | — | pre | single |  | MIXED |
| 06:11 | ITFWMATCH-26JUL06ILIEBE-ILI | ITF_W | underdog | 45 | 37 | +8 (place_cell) | — | pre | pair | 97 | EARNED |
| 06:11 | ATPCHALLENGERMATCH-26JUL06DELWAL-D | ATP_CHALL | underdog | 28 | 24 | +4 (place_cell) | -16.5 | pre | pair | 97 | EARNED |
| 06:11 | ATPCHALLENGERMATCH-26JUL06BASHOE-H | ATP_CHALL | leader | 51 | 48 | +3 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
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
| 06:35 | WTACHALLENGERMATCH-26JUL06GRAMAS-M | WTA_CHALL | ? | 67 | 64 | +3 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 06:36 | ATPCHALLENGERMATCH-26JUL06MARHAM-H | ATP_CHALL | underdog | 5 | 3 | +2 (place_cell) | — | pre | pair | 96 | MIXED |
| 06:40 | ATPCHALLENGERMATCH-26JUL06ERHSIN-E | ATP_CHALL | ? | 96 | 92 | +4 (place_cell) | — | pre | pair | 100 | GIFT_CLASS |
| 06:40 | ATPCHALLENGERMATCH-26JUL06ERHSIN-S | ATP_CHALL | underdog | 4 | 2 | +2 (place_cell) | — | pre | pair | 100 | MIXED |
| 06:40 | ATPCHALLENGERMATCH-26JUL06ZORDEV-D | ATP_CHALL | ? | 42 | 39 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 06:41 | ITFMATCH-26JUL06HOSGAT-GAT | ITF_M | underdog | 38 | 34 | +4 (place_cell) | — | pre | single |  | MIXED |
| 06:43 | ATPCHALLENGERMATCH-26JUL06ZORDEV-Z | ATP_CHALL | leader | 55 | 53 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:43 | ATPCHALLENGERMATCH-26JUL06PIEMOL-M | ATP_CHALL | leader | 52 | 49 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:44 | ATPCHALLENGERMATCH-26JUL06DELWAL-W | ATP_CHALL | ? | 69 | 68 | +1 (place_cell) | 16.0 | pre | pair | 97 | GIFT_CLASS |
| 06:48 | ITFMATCH-26JUL06DUGHOF-DUG | ITF_M | ? | 76 | 51 | +25 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:48 | ATPCHALLENGERMATCH-26JUL06MARHAM-M | ATP_CHALL | ? | 91 | 91 | +0 (place_cell) | — | pre | pair | 96 | MIXED |
| 06:48 | WTACHALLENGERMATCH-26JUL06ROMSEM-S | WTA_CHALL | leader | 57 | 53 | +4 (place_cell) | 40.0 | pre | single |  | GIFT_CLASS |
| 06:53 | WTACHALLENGERMATCH-26JUL06LEWMAR-L | WTA_CHALL | leader | 54 | 52 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:53 | ITFWMATCH-26JUL06MILHER-MIL | ITF_W | ? | 81 | 49 | +32 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:55 | WTACHALLENGERMATCH-26JUL06HESPAL-H | WTA_CHALL | ? | 33 | 26 | +7 (place_cell) | -59.5 | pre | pair | 102 | EARNED |
| 06:55 | WTACHALLENGERMATCH-26JUL06HESPAL-P | WTA_CHALL | leader | 69 | 66 | +3 (place_cell) | 60.0 | pre | pair | 102 | GIFT_CLASS |
| 06:57 | ATPCHALLENGERMATCH-26JUL06KUZSTR-S | ATP_CHALL | ? | 26 | 23 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:57 | ITFMATCH-26JUL06SALBRE-BRE | ITF_M | ? | 7 | 2 | +5 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:57 | ITFWMATCH-26JUL06PODLUK-POD | ITF_W | ? | 27 | 18 | +9 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:59 | ATPCHALLENGERMATCH-26JUL06RAQRIB-R | ATP_CHALL | leader | 61 | 61 | +0 (place_cell) | — | pre | single |  | MIXED |
| 07:02 | ATPCHALLENGERMATCH-26JUL06DONCIZ-C | ATP_CHALL | ? | 24 | 20 | +4 (place_cell) | — | pre | single |  | MIXED |
| 07:03 | ATPCHALLENGERMATCH-26JUL06CHEYEV-Y | ATP_CHALL | ? | 37 | 34 | +3 (place_cell) | — | pre | pair | 96 | MIXED |
| 07:06 | ITFMATCH-26JUL06DUHCAR-DUH | ITF_M | ? | 88 | 79 | +9 (place_cell) | — | pre | pair | 100 | PENDING |
| 07:06 | ITFMATCH-26JUL06DUHCAR-CAR | ITF_M | underdog | 12 | 5 | +7 (place_cell) | — | pre | pair | 100 | PENDING |
| 07:06 | ATPCHALLENGERMATCH-26JUL06CHEYEV-C | ATP_CHALL | ? | 59 | 58 | +1 (place_cell) | — | pre | pair | 96 | MIXED |
| 07:09 | ITFWMATCH-26JUL06EWAMAN-MAN | ITF_W | ? | 27 | 14 | +13 (place_cell) | — | pre | pair | 97 | EARNED |
| 07:10 | ATPCHALLENGERMATCH-26JUL06KUZSTR-K | ATP_CHALL | ? | 71 | 70 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:11 | WTAMATCH-26JUL06PAOEAL-PAO | WTA_MAIN | underdog | 39 | 37 | +2 (place_cell) | — | pre | single |  | MIXED |
| 07:14 | ATPCHALLENGERMATCH-26JUL06HUAPUR-H | ATP_CHALL | ? | 35 | 32 | +3 (place_cell) | — | pre | pair | 96 | MIXED |
| 07:16 | ATPCHALLENGERMATCH-26JUL06MARBER-B | ATP_CHALL | ? | 58 | 55 | +3 (place_cell) | -33.5 | pre | pair | 97 | EARNED |
| 07:18 | ITFMATCH-26JUL06TIMJEF-TIM | ITF_M | ? | 20 | 15 | +5 (place_cell) | — | pre | pair | 92 | MIXED |
| 07:18 | ITFWMATCH-26JUL06POZMLA-MLA | ITF_W | ? | 8 | 1 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 07:20 | ATPCHALLENGERMATCH-26JUL06MARBER-M | ATP_CHALL | ? | 39 | 37 | +2 (place_cell) | 30.5 | pre | pair | 97 | EARNED |
| 07:22 | WTAMATCH-26JUL06BOUMER-BOU | WTA_MAIN | underdog | 47 | 43 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:24 | ITFMATCH-26JUL06TIMJEF-JEF | ITF_M | ? | 72 | 67 | +5 (place_cell) | — | pre | pair | 92 | MIXED |
| 07:26 | ITFWMATCH-26JUL06BOSTOP-BOS | ITF_W | leader | 68 | 62 | +6 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:29 | ITFWMATCH-26JUL06FAVKLY-KLY | ITF_W | ? | 40 | 4 | +36 (place_cell) | — | pre | pair | 55 | PENDING |
| 07:29 | WTACHALLENGERMATCH-26JUL06GRAMAS-G | WTA_CHALL | ? | 29 | 29 | +0 (place_cell) | — | pre | pair | 96 | MIXED |
| 07:30 | ITFWMATCH-26JUL06FAVKLY-FAV | ITF_W | underdog | 15 | 3 | +12 (place_cell) | — | pre | pair | 55 | PENDING |
| 07:34 | ITFWMATCH-26JUL06MCAENC-ENC | ITF_W | leader | 51 | 49 | +2 (place_cell) | — | pre | single |  | PENDING |
| 07:39 | ATPCHALLENGERMATCH-26JUL06HUAPUR-P | ATP_CHALL | ? | 61 | 60 | +1 (place_cell) | — | pre | pair | 96 | MIXED |
| 07:39 | WTACHALLENGERMATCH-26JUL06MATPUT-M | WTA_CHALL | underdog | 9 | 6 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:40 | ATPCHALLENGERMATCH-26JUL06IVADIN-D | ATP_CHALL | underdog | 20 | 17 | +3 (place_cell) | — | pre | single |  | MIXED |
| 07:42 | WTACHALLENGERMATCH-26JUL06MATPUT-P | WTA_CHALL | ? | 88 | 86 | +2 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 07:43 | ITFWMATCH-26JUL06VIRKOV-KOV | ITF_W | underdog | 41 | 24 | +17 (place_cell) | — | pre | pair | 97 | PENDING |
| 07:44 | ATPCHALLENGERMATCH-26JUL06OPIPET-O | ATP_CHALL | underdog | 28 | 23 | +5 (place_cell) | — | pre | single |  | MIXED |
| 07:44 | ITFMATCH-26JUL06STAGUI-GUI | ITF_M | underdog | 37 | 8 | +29 (place_cell) | — | pre | single |  | PENDING |
| 07:44 | WTACHALLENGERMATCH-26JUL06BLIAND-B | WTA_CHALL | leader | 64 | 61 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 07:46 | ITFWMATCH-26JUL06BOSTOP-TOP | ITF_W | ? | 29 | 29 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:53 | ITFWMATCH-26JUL06VIRKOV-VIR | ITF_W | ? | 56 | 54 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 07:53 | ITFWMATCH-26JUL06OKASAK-OKA | ITF_W | ? | 40 | 20 | +20 (place_cell) | — | pre | single |  | MIXED |
| 07:55 | WTACHALLENGERMATCH-26JUL06ARANIL-A | WTA_CHALL | leader | 73 | 70 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 07:55 | ITFMATCH-26JUL06GARCIO-GAR | ITF_M | leader | 57 | 55 | +2 (place_cell) | — | pre | pair | 98 | MIXED |
| 07:55 | ITFMATCH-26JUL06GARCIO-CIO | ITF_M | underdog | 41 | 32 | +9 (place_cell) | — | pre | pair | 98 | MIXED |
| 07:55 | WTAMATCH-26JUL06BOUMER-MER | WTA_MAIN | leader | 50 | 55 | -5 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:58 | ITFMATCH-26JUL06TEUHAS-HAS | ITF_M | leader | 67 | 61 | +6 (place_cell) | — | pre | pair | 105 | MIXED |
| 07:59 | ITFMATCH-26JUL06ALIMIS-ALI | ITF_M | leader | 91 | 83 | +8 (place_cell) | — | pre | single |  | PENDING |
| 08:01 | ITFWMATCH-26JUL06POZMLA-POZ | ITF_W | ? | 89 | 87 | +2 (fill_est) | — | pre | pair | 97 | PENDING |
| 08:02 | ITFMATCH-26JUL06TEUHAS-TEU | ITF_M | ? | 38 | 22 | +16 (place_cell) | — | pre | pair | 105 | MIXED |
| 08:02 | ATPCHALLENGERMATCH-26JUL06BASHOE-B | ATP_CHALL | ? | 45 | 44 | +1 (place_cell) | — | pre | pair | 96 | EARNED |
| 08:04 | ATPCHALLENGERMATCH-26JUL06POLHAI-H | ATP_CHALL | leader | 66 | 65 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:07 | ITFMATCH-26JUL06ROJBEC-ROJ | ITF_M | ? | 10 | 7 | +3 (place_cell) | — | pre | single |  | PENDING |
| 08:07 | ITFWMATCH-26JUL06KARVIS-KAR | ITF_W | ? | 76 | 73 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:09 | ATPCHALLENGERMATCH-26JUL06CHIJAN-J | ATP_CHALL | ? | 22 | 20 | +2 (place_cell) | — | pre | single |  | MIXED |
| 08:09 | ITFMATCH-26JUL06STEAUN-AUN | ITF_M | ? | 14 | 10 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 08:11 | ATPCHALLENGERMATCH-26JUL06REHKOU-K | ATP_CHALL | underdog | 44 | 41 | +3 (place_cell) | — | pre | single |  | PENDING |
| 08:12 | WTAMATCH-26JUL06KEYNOS-NOS | WTA_MAIN | ? | 43 | 40 | +3 (place_cell) | — | pre | single |  | MIXED |
| 08:13 | ITFMATCH-26JUL06STEAUN-STE | ITF_M | leader | 83 | 79 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 08:16 | ATPCHALLENGERMATCH-26JUL06VALZHU-V | ATP_CHALL | leader | 71 | 68 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 08:16 | ATPMATCH-26JUL06DECOB-DE | ATP_MAIN | leader | 74 | 77 | -3 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:19 | ITFWMATCH-26JUL06BUYALV-ALV | ITF_W | ? | 28 | 16 | +12 (place_cell) | — | pre | single |  | PENDING |
| 08:19 | ATPCHALLENGERMATCH-26JUL06WEHVAN-V | ATP_CHALL | ? | 42 | 39 | +3 (place_cell) | — | pre | single |  | MIXED |
| 08:19 | ATPCHALLENGERMATCH-26JUL06WALNEU-N | ATP_CHALL | ? | 28 | 25 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:22 | ATPCHALLENGERMATCH-26JUL06WALNEU-W | ATP_CHALL | leader | 69 | 67 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:23 | ATPCHALLENGERMATCH-26JUL06VALZHU-Z | ATP_CHALL | ? | 26 | 23 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 08:23 | ITFWMATCH-26JUL06PACLOV-PAC | ITF_W | ? | 61 | 54 | +7 (place_cell) | — | pre | pair | 106 | GIFT_CLASS |
| 08:24 | ITFMATCH-26JUL06TRUTRA-TRA | ITF_M | underdog | 27 | 20 | +7 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 180 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 20, 'FLOW_ABOVE': 61, 'NO_FLOW': 99} | repriceable now: true 22 / false 158 | **cumulative bid_grade lines: 2067 (repriceable true 206 / false 1861)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06BARDAL-B | 56 | 205m | 0 | 56-58 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06BARDAL-D | 41 | 205m | 1/42-42/20 | 42-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06BARZIN-B | 52 | 85m | 0 | 52-54 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06BARZIN-Z | 45 | 85m | 1/48-48/12 | 47-48 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ATPCHALLENGERMATCH-26JUL06CHADEM-C | 48 | 205m | 0 | 48-50 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CHADEM-D | 49 | 83m | 1/52-52/1 | 51-52 | 3 | **FLOW_ABOVE** | 49 | flow above but bound 49c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06CHIJAN-C | 75 | 17m | 0 | 77-78 | — | **NO_FLOW** | 75 |  |
| ATPCHALLENGERMATCH-26JUL06CLAPAP-C | 72 | 85m | 2/74-75/2 | 74-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ATPCHALLENGERMATCH-26JUL06CLAPAP-P | 26 | 85m | 0 | 26-28 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DAMHUE-D | 79 | 205m | 2/80-80/35 | 79-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ATPCHALLENGERMATCH-26JUL06DAMHUE-H | 19 | 205m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DEHUD-DE | 38 | 205m | 2/39-39/122 | 38-39 | 1 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06DEHUD-HU | 61 | 205m | 1/62-62/5 | 61-62 | 1 | **FLOW_ABOVE** | 59 | flow above but bound 59c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-D | 73 | 84m | 0 | 76-79 | — | **NO_FLOW** | 73 |  |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-D | 73 | 83m | 0 | 76-79 | — | **NO_FLOW** | 73 |  |
| ATPCHALLENGERMATCH-26JUL06FOMDHA-D | 52 | 205m | 0 | 52-54 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06FOMDHA-F | 45 | 205m | 2/46-46/39 | 46-47 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | 23 | 154m | 149/1-25/45244 | 2-1 | -22 | **FLOW_AT_LEVEL** | 23 |  |
| ATPCHALLENGERMATCH-26JUL06HUETEN-H | 60 | 85m | 1/71-71/2 | 70-74 | 11 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HUETEN-T | 28 | 85m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ILARYB-I | 52 | 84m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ILARYB-R | 45 | 83m | 0 | 45-47 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-I | 77 | 46m | 0 | 81-83 | — | **NO_FLOW** | 77 |  |
| ATPCHALLENGERMATCH-26JUL06KASCIN-C | 54 | 176m | 2/56-56/7 | 55-56 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ATPCHALLENGERMATCH-26JUL06KASCIN-K | 43 | 176m | 1/44-44/31 | 43-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ATPCHALLENGERMATCH-26JUL06KOZJOH-J | 31 | 53m | 0 | 31-34 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KOZJOH-K | 66 | 83m | 0 | 66-69 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 5 | 252m | 338/1-21/41967 | 19-1 | -4 | **FLOW_AT_LEVEL** | 5 |  |
| ATPCHALLENGERMATCH-26JUL06KYMFAU-F | 32 | 175m | 0 | 32-33 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KYMFAU-K | 67 | 165m | 2/68-68/171 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPCHALLENGERMATCH-26JUL06MAXGHI-G | 55 | 116m | 1/56-56/129 | 56-57 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ATPCHALLENGERMATCH-26JUL06MAXGHI-M | 43 | 116m | 1/44-44/3 | 43-45 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ATPCHALLENGERMATCH-26JUL06OLIDAN-D | 64 | 85m | 3/66-66/20 | 65-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ATPCHALLENGERMATCH-26JUL06OLIDAN-O | 34 | 85m | 0 | 34-36 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06OPIPET-P | 69 | 42m | 12/72-90/810 | 89-90 | 3 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PAPMID-M | 51 | 83m | 0 | 51-52 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PAPMID-P | 47 | 83m | 2/49-49/43 | 47-49 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→49 |
| ATPCHALLENGERMATCH-26JUL06POPSAN-P | 93 | 3m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POPSAN-S | 5 | 83m | 2/7-7/12 | 6-7 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→7 |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 36 | 88m | 224/40-87/24687 | 38-41 | 4 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 36 | 37m | 120/41-87/10613 | 38-41 | 5 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06REHKOU-R | 53 | 15m | 0 | 57-58 | — | **NO_FLOW** | 53 |  |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-B | 36 | 93m | 172/36-99/38561 | 99-71 | 0 | **FLOW_AT_LEVEL** | 34 |  |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 157m | 111/1-60/13885 | 4-1 | -32 | **FLOW_AT_LEVEL** | 33 |  |
| ATPCHALLENGERMATCH-26JUL06WEHVAN-W | 55 | 8m | 1/58-58/16 | 63-64 | 3 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06WEIGRA-G | 81 | 115m | 2/82-82/30 | 81-82 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→82 |
| ATPCHALLENGERMATCH-26JUL06WEIGRA-W | 19 | 38m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL06DIMFER-DIM | 64 | 137m | 64/67-68/4199 | 67-68 | 3 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ATPMATCH-26JUL06DIMFER-DIM | 64 | 79m | 42/68-68/2689 | 67-68 | 4 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ATPMATCH-26JUL06FRIBUB-BUB | 33 | 56m | 25/33-34/1122 | 33-34 | 0 | **FLOW_AT_LEVEL** | 31 |  |
| ATPMATCH-26JUL06FRIBUB-FRI | 66 | 56m | 47/66-67/3078 | 66-67 | 0 | **FLOW_AT_LEVEL** | 67 |  |
| ATPMATCH-26JUL06LEHZVE-LEH | 26 | 25m | 3/27-27/403 | 26-27 | 1 | **FLOW_ABOVE** | 25 | flow above but bound 25c < flow -- chasing breaks goal |
| ATPMATCH-26JUL06LEHZVE-ZVE | 73 | 25m | 3/74-74/49 | 73-74 | 1 | **FLOW_ABOVE** | 74 | REPRICEABLE→74 |
| ITFMATCH-26JUL06ALEREG-REG | 40 | 263m | 99/49-99/9602 | 99-99 | 9 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06ALIMIS-MIS | 6 | 354m | 4/8-15/8 | 7-12 | 2 | **FLOW_ABOVE** | 6 | flow above but bound 6c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06ALIMIS-MIS | 6 | 23m | 0 | 7-12 | — | **NO_FLOW** | 6 |  |
| ITFMATCH-26JUL06BONFAU-BON | 66 | 157m | 0 | 66-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BONFAU-FAU | 26 | 140m | 0 | 26-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BROTHU-BRO | 36 | 85m | 0 | 36-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BROTHU-THU | 54 | 82m | 0 | 54-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DONDEV-DEV | 20 | 83m | 0 | 20-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DONDEV-DON | 69 | 86m | 0 | 69-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GANVER-GAN | 4 | 11m | 0 | 46-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GANVER-VER | 48 | 150m | 0 | 48-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GARCIO-GAR | 56 | 11m | 0 | 57-80 | — | **NO_FLOW** | 56 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 414m | 213/1-19/18095 | 18-1 | -15 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06HOSGAT-HOS | 56 | 239m | 56/60-93/2118 | 84-85 | 4 | **FLOW_ABOVE** | 59 | REPRICEABLE→59 |
| ITFMATCH-26JUL06HOSGAT-HOS | 59 | 76m | 32/60-90/466 | 84-85 | 1 | **FLOW_ABOVE** | 59 | flow above but bound 59c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06IAMBEN-BEN | 19 | 71m | 0 | 19-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06IAMBEN-IAM | 51 | 71m | 0 | 51-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06JAIHEN-JAI | 45 | 264m | 0 | 45-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-LIL | 28 | 247m | 205/1-55/9114 | 1-1 | -27 | **FLOW_AT_LEVEL** | 31 |  |
| ITFMATCH-26JUL06LAPCIO-CIO | 41 | 145m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LAPCIO-LAP | 54 | 143m | 0 | 54-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 32 | 140m | 61/32-97/6018 | 96-97 | 0 | **FLOW_AT_LEVEL** | 32 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 32 | 43m | 44/72-97/5637 | 96-97 | 40 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06LIBNAK-LIB | 38 | 189m | 0 | 38-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LIBNAK-NAK | 55 | 189m | 0 | 55-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LUEVAN-LUE | 65 | 156m | 0 | 65-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LUEVAN-VAN | 20 | 203m | 0 | 20-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06PESTER-PES | 41 | 16m | 0 | 41-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06PESTER-TER | 41 | 17m | 0 | 41-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-BEC | 87 | 266m | 0 | 88-90 | — | **NO_FLOW** | 87 |  |
| ITFMATCH-26JUL06ROJBEC-BEC | 87 | 17m | 0 | 88-90 | — | **NO_FLOW** | 87 |  |
| ITFMATCH-26JUL06ROURAM-RAM | 53 | 144m | 0 | 53-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROURAM-ROU | 37 | 145m | 0 | 37-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STAGUI-STA | 60 | 42m | 12/72-94/110 | 94-95 | 12 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06STEAUN-AUN | 13 | 0m | 0 | 17-19 | — | **NO_FLOW** | 14 |  |
| ITFMATCH-26JUL06SURMED-SUR | 21 | 71m | 0 | 21-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TISVER-TIS | 35 | 76m | 0 | 35-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TISVER-VER | 26 | 77m | 0 | 26-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRU | 70 | 2m | 1/81-81/25 | 84-85 | 11 | **FLOW_ABOVE** | 70 | flow above but bound 70c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06VANHOR-HOR | 30 | 144m | 1/36-36/1 | 30-36 | 6 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06VANHOR-HOR | 26 | 80m | 0 | 30-36 | — | **NO_FLOW** | 34 |  |
| ITFMATCH-26JUL06VULCOU-VUL | 81 | 249m | 11/98-99/1550 | 99-85 | 17 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ADKFER-ADK | 76 | 4m | 0 | 76-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ADKFER-FER | 19 | 4m | 0 | 19-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 310m | 57/28-64/7484 | 64-65 | 8 | **FLOW_ABOVE** | 20 | flow above but bound 20c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 27m | 45/31-64/7074 | 64-65 | 11 | **FLOW_ABOVE** | 20 | flow above but bound 20c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06BOWMAT-BOW | 7 | 97m | 0 | 7-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOWMAT-MAT | 53 | 36m | 0 | 53-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 437m | 4430/1-99/518199 | 5-1 | -33 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06BUYALV-BUY | 59 | 6m | 0 | 59-76 | — | **NO_FLOW** | 69 |  |
| ITFWMATCH-26JUL06CENBUL-BUL | 20 | 52m | 0 | 20-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CENBUL-CEN | 50 | 110m | 0 | 69-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06COHXAV-COH | 7 | 37m | 0 | 7-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DRISLA-DRI | 26 | 97m | 0 | 26-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DRISLA-SLA | 60 | 97m | 0 | 60-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EVARHO-EVA | 63 | 17m | 0 | 63-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EVARHO-RHO | 18 | 18m | 0 | 18-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-TSE | 20 | 78m | 235/24-99/20740 | 82-83 | 4 | **FLOW_ABOVE** | 20 | flow above but bound 20c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06HIEGUT-GUT | 56 | 202m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HIEGUT-HIE | 41 | 206m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 25 | 231m | 1/99-99/12 | 99-58 | 74 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KOVDAE-DAE | 20 | 127m | 1/24-24/24 | 20-25 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| ITFWMATCH-26JUL06KOVDAE-KOV | 75 | 295m | 0 | 75-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 295m | 73/79-99/2231 | 98-99 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 295m | 73/79-99/2231 | 98-99 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULVOG-KUL | 55 | 103m | 0 | 55-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULVOG-VOG | 39 | 101m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LABTSY-LAB | 27 | 175m | 0 | 27-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LABTSY-TSY | 59 | 175m | 0 | 59-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 483m | 3895/23-99/459986 | 99-24 | -14 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06MARBED-BED | 15 | 15m | 0 | 15-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARBED-MAR | 55 | 15m | 0 | 55-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARGLU-GLU | 66 | 239m | 0 | 66-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARGLU-MAR | 29 | 52m | 0 | 29-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-MCA | 42 | 302m | 2/48-48/38 | 42-48 | 6 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06MCAENC-MCA | 38 | 51m | 0 | 42-48 | — | **NO_FLOW** | 46 |  |
| ITFWMATCH-26JUL06MULCIS-CIS | 34 | 85m | 0 | 35-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MULCIS-MUL | 53 | 83m | 0 | 53-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKASAK-SAK | 57 | 33m | 9/68-80/173 | 73-81 | 11 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06OKUPRI-PRI | 41 | 149m | 828/36-99/114162 | 99-99 | -5 | **FLOW_AT_LEVEL** | 41 |  |
| ITFWMATCH-26JUL06OLUZAM-OLU | 35 | 25m | 0 | 35-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 386m | 1942/1-13/312225 | 14-1 | -7 | **FLOW_AT_LEVEL** | 12 |  |
| ITFWMATCH-26JUL06PEEPAH-PEE | 39 | 101m | 111/4-51/7947 | 17-21 | -35 | **FLOW_AT_LEVEL** | 36 |  |
| ITFWMATCH-26JUL06PIERAD-PIE | 64 | 195m | 117/84-99/4782 | 99-90 | 20 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06POHSTU-POH | 28 | 56m | 0 | 28-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06POHSTU-STU | 59 | 56m | 0 | 59-71 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-NIJ | 30 | 295m | 3/36-36/38 | 30-36 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-PRI | 63 | 295m | 0 | 63-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06RABELI-ELI | 17 | 31m | 0 | 17-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06RABELI-RAB | 35 | 30m | 0 | 35-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06REEION-ION | 52 | 37m | 0 | 52-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06REEION-REE | 36 | 35m | 0 | 36-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SACLAZ-LAZ | 15 | 242m | 648/1-33/45125 | 40-1 | -14 | **FLOW_AT_LEVEL** | 1 |  |
| ITFWMATCH-26JUL06SCHELI-ELI | 35 | 37m | 0 | 35-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 433m | 16366/1-95/1383948 | 83-1 | -13 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06SINUSU-SIN | 24 | 33m | 0 | 24-68 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SINUSU-USU | 31 | 33m | 0 | 31-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06STETRA-STE | 79 | 48m | 0 | 79-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06STETRA-TRA | 16 | 203m | 1/22-22/11 | 16-21 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06URREVA-EVA | 37 | 174m | 2/39-39/47 | 37-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL06URREVA-URR | 61 | 266m | 1/65-65/10 | 61-65 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 433m | 6096/1-29/750264 | 21-1 | -14 | **FLOW_AT_LEVEL** | 5 |  |
| ITFWMATCH-26JUL06VARMUN-MUN | 15 | 25m | 0 | 15-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VARMUN-VAR | 83 | 113m | 0 | 83-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-VLA | 30 | 129m | 573/1-54/39141 | 1-2 | -29 | **FLOW_AT_LEVEL** | 23 |  |
| WTACHALLENGERMATCH-26JUL06ARANIL-N | 24 | 15m | 22/30-44/702 | 30-32 | 6 | **FLOW_ABOVE** | 23 | flow above but bound 23c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 74 | 265m | 2/75-76/32 | 74-75 | 1 | **FLOW_ABOVE** | 72 | flow above but bound 72c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 25 | 56m | 1/26-26/10 | 25-26 | 1 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06BLIAND-A | 33 | 42m | 0 | 37-38 | — | **NO_FLOW** | 33 |  |
| WTACHALLENGERMATCH-26JUL06CURDOD-C | 68 | 56m | 0 | 69-70 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06CURDOD-D | 30 | 56m | 0 | 30-33 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06DENQUE-D | 5 | 40m | 13/6-6/1172 | 5-6 | 1 | **FLOW_ABOVE** | 3 | flow above but bound 3c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06DENQUE-Q | 93 | 176m | 0 | 93-96 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 39 | 156m | 108/84-99/18486 | 99-99 | 45 | **FLOW_ABOVE** | 39 | flow above but bound 39c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ISHCRO-C | 61 | 85m | 0 | 61-62 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06ISHCRO-I | 38 | 85m | 2/39-39/123 | 38-39 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| WTACHALLENGERMATCH-26JUL06LINMAR-L | 6 | 83m | 8/7-7/349 | 6-7 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→7 |
| WTACHALLENGERMATCH-26JUL06LINMAR-M | 93 | 83m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06OLIUCH-U | 39 | 143m | 2066/11-99/409246 | 99-95 | -28 | **FLOW_AT_LEVEL** | 37 |  |
| WTACHALLENGERMATCH-26JUL06WALKAW-K | 43 | 265m | 5/44-44/212 | 43-44 | 1 | **FLOW_ABOVE** | 41 | flow above but bound 41c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06WALKAW-W | 56 | 96m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-S | 67 | 266m | 1/68-68/17 | 67-69 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| WTACHALLENGERMATCH-26JUL06WERSAL-W | 32 | 30m | 0 | 32-33 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL06BOUMER-BOU | 46 | 1m | 11/41-48/9722 | 41-44 | -5 | **FLOW_AT_LEVEL** | 44 |  |
| WTAMATCH-26JUL06KEYNOS-KEY | 54 | 14m | 5/58-59/97 | 58-59 | 4 | **FLOW_ABOVE** | 54 | flow above but bound 54c < flow -- chasing breaks goal |
| WTAMATCH-26JUL06KEYNOS-KEY | 54 | 14m | 5/58-59/97 | 58-59 | 4 | **FLOW_ABOVE** | 54 | flow above but bound 54c < flow -- chasing breaks goal |
| WTAMATCH-26JUL06PAOEAL-EAL | 58 | 75m | 106/60-62/8799 | 60-61 | 2 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL06VANHOR | 63 | 36 | **99** | 97 | +2 |
| ITFWMATCH-26JUL06MCAENC | 51 | 48 | **99** | 97 | +2 |
| WTACHALLENGERMATCH-26JUL06ROMSEM | 57 | 43 | **100** | 97 | +3 |
| WTAMATCH-26JUL06PAOEAL | 39 | 61 | **100** | 97 | +3 |
| ITFMATCH-26JUL06ROJBEC | 10 | 90 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL06CHIJAN | 22 | 78 | **100** | 97 | +3 |
| ATPMATCH-26JUL06DIMFER | 33 | 68 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL06RAQRIB | 61 | 41 | **102** | 97 | +5 |
| WTACHALLENGERMATCH-26JUL06BLIAND | 64 | 38 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL06REHKOU | 44 | 58 | **102** | 97 | +5 |
| WTAMATCH-26JUL06KEYNOS | 43 | 59 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL06DONCIZ | 24 | 79 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL06IVADIN | 20 | 83 | **103** | 97 | +6 |
| ITFMATCH-26JUL06ALIMIS | 91 | 12 | **103** | 97 | +6 |
| ITFWMATCH-26JUL06BUYALV | 28 | 76 | **104** | 97 | +7 |
| WTACHALLENGERMATCH-26JUL06ARANIL | 73 | 32 | **105** | 97 | +8 |
| ATPCHALLENGERMATCH-26JUL06WEHVAN | 42 | 64 | **106** | 97 | +9 |
| ITFWMATCH-26JUL06RICMIT | 9 | 99 | **108** | 97 | +11 |
| ATPCHALLENGERMATCH-26JUL06SEYMAR | 10 | 99 | **109** | 97 | +12 |
| ITFMATCH-26JUL06TRUTRA | 27 | 85 | **112** | 97 | +15 |
| ITFMATCH-26JUL06CASBAY | 45 | 71 | **116** | 97 | +19 |
| ATPCHALLENGERMATCH-26JUL06OPIPET | 28 | 90 | **118** | 97 | +21 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ITFWMATCH-26JUL06KULGON | 22 | 99 | **121** | 97 | +24 |
| ITFWMATCH-26JUL06OKASAK | 40 | 81 | **121** | 97 | +24 |
| ITFWMATCH-26JUL06PIERAD | 33 | 90 | **123** | 97 | +26 |
| ITFMATCH-26JUL06HOSGAT | 38 | 85 | **123** | 97 | +26 |
| ATPCHALLENGERMATCH-26JUL06PAPJAN | 53 | 73 | **126** | 97 | +29 |
| ITFMATCH-26JUL06STAGUI | 37 | 95 | **132** | 97 | +35 |
| ITFWMATCH-26JUL06BOIBOY | 77 | 65 | **142** | 97 | +45 |
| ITFMATCH-26JUL06ALEREG | 51 | 99 | **150** | 97 | +53 |
| ITFWMATCH-26JUL06GALTSE | 77 | 83 | **160** | 97 | +63 |
| ITFMATCH-26JUL06LENTHE | 65 | 97 | **162** | 97 | +65 |
| ITFWMATCH-26JUL06WONIBR | 65 | 99 | **164** | 97 | +67 |

## PATTERNS (sub-B) — 157
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
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 501, "mode": "SET_BELOW_FLOW(prints 74c above)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 29, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 30, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 31, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 32, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LUKNOE-LUK {"price": 59, "ceiling": 18}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06LUKNOE-LUK {"price": 66, "ceiling": 18}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 473, "mode": "NO_BID(sib rested earlier, none now)"}
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
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06GANPUI-PUI {"price": 11, "ceiling": 9}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 55, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 23, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PODLUK-POD {"price": 16, "ceiling": 11}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 24, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PODLUK-POD {"price": 22, "ceiling": 11}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PODLUK-POD {"price": 23, "ceiling": 11}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 25, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PODLUK-POD {"price": 25, "ceiling": 11}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PODLUK-POD {"price": 26, "ceiling": 11}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 51, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 52, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06VLADIL-VLA {"price": 41, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 53, "ceiling": 31}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 54, "ceiling": 31}
- half_arm_aging: KXITFWMATCH-26JUL06BOIBOY-BOI {"fill": 77, "age_min": 310, "mode": "SET_BELOW_FLOW(prints 8c above)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06DIANIK-NIK {"price": 41, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06DIANIK-NIK {"price": 52, "ceiling": 38}
- half_arm_aging: KXITFWMATCH-26JUL06KULGON-GON {"fill": 22, "age_min": 295, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06JOSKUM-JOS {"price": 61, "ceiling": 59}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06JOSKUM-JOS {"price": 67, "ceiling": 59}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 56, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 57, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 26, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 58, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 59, "ceiling": 38}
- half_arm_aging: KXITFMATCH-26JUL06CASBAY-CAS {"fill": 45, "age_min": 245, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TEISCH-TEI {"price": 80, "ceiling": 79}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 27, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 62, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TEISCH-TEI {"price": 81, "ceiling": 79}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06SPIMED-SPI {"price": 87, "ceiling": 78}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06GALTSE-GAL {"price": 77, "ceiling": 76}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06ELDHAU-ELD {"price": 65, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKUPRI-OKU {"price": 60, "ceiling": 31}
- deep_neg_fv: KXITFWMATCH-26JUL06OKUPRI-PRI {"entry_minus_fv_burst": -45.5}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TEISCH-TEI {"price": 82, "ceiling": 79}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06TEISCH-TEI {"price": 87, "ceiling": 79}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06NOHBUR-BUR {"entry_minus_fv_burst": -48.5}
- half_arm_aging: KXITFWMATCH-26JUL06PIERAD-RAD {"fill": 33, "age_min": 195, "mode": "SET_BELOW_FLOW(prints 20c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06PAPJAN-PAP {"fill": 53, "age_min": 194, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL06LENTHE-THE {"fill": 65, "age_min": 188, "mode": "QUEUE(flow at/below our level, unfilled)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06MONPOP-MON {"entry_minus_fv_burst": -35.5}
- half_arm_aging: KXITFWMATCH-26JUL06RICMIT-MIT {"fill": 9, "age_min": 181, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06PODLUK-POD {"price": 27, "ceiling": 11}
- half_arm_aging: KXITFWMATCH-26JUL06GALTSE-GAL {"fill": 77, "age_min": 171, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SEYMAR-MAR {"fill": 10, "age_min": 166, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06GOMLUZ-GOM {"entry_minus_fv_burst": -26.5}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06EWAMAN-EWA {"price": 69, "ceiling": 68}
- half_arm_aging: KXITFMATCH-26JUL06ALEREG-ALE {"fill": 51, "age_min": 152, "mode": "SET_BELOW_FLOW(prints 9c above)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06KARVIS-VIS {"price": 18, "ceiling": 16}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06KARVIS-VIS {"price": 21, "ceiling": 16}
- half_arm_aging: KXITFMATCH-26JUL06VANHOR-VAN {"fill": 63, "age_min": 139, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- deep_neg_fv: KXITFWMATCH-26JUL06VLADIL-DIL {"entry_minus_fv_burst": -32.0}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06ILIEBE-EBE {"price": 53, "ceiling": 42}
- half_arm_aging: KXATPMATCH-26JUL06DIMFER-FER {"fill": 33, "age_min": 137, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06ILIEBE-EBE {"price": 58, "ceiling": 42}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06DELWAL-DEL {"entry_minus_fv_burst": -16.5}
- deep_neg_fv: KXWTAMATCH-26JUL06KRUKOS-KOS {"entry_minus_fv_burst": -18.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06SEGBRA-BRA {"entry_minus_fv_burst": -47.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06POTFEL-FEL {"entry_minus_fv_burst": -25.5, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXWTACHALLENGERMATCH-26JUL06GRAMAS-GRA {"price": 33, "ceiling": 32}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TSIAND-TSI {"price": 69, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 28, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06EWAMAN-EWA {"price": 70, "ceiling": 68}
- half_arm_aging: KXITFMATCH-26JUL06HOSGAT-GAT {"fill": 38, "age_min": 105, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06ROMSEM-SEM {"fill": 57, "age_min": 98, "mode": "NO_BID(sib rested earlier, none now)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 29, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 30, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06HESPAL-HES {"entry_minus_fv_burst": -59.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06RAQRIB-RAQ {"fill": 61, "age_min": 87, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06DONCIZ-CIZ {"fill": 24, "age_min": 84, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXWTAMATCH-26JUL06PAOEAL-PAO {"fill": 39, "age_min": 75, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 31, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 34, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 35, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL06MARBER-BER {"entry_minus_fv_burst": -33.5}
- half_arm_aging: KXITFWMATCH-26JUL06MCAENC-ENC {"fill": 51, "age_min": 52, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06IVADIN-DIN {"fill": 20, "age_min": 46, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06OPIPET-OPI {"fill": 28, "age_min": 42, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFMATCH-26JUL06STAGUI-GUI {"fill": 37, "age_min": 42, "mode": "SET_BELOW_FLOW(prints 12c above)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06BLIAND-BLI {"fill": 64, "age_min": 42, "mode": "STARVATION(no prints since post)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 36, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 37, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06OKASAK-OKA {"price": 41, "ceiling": 20, "emitted_et": "2026-07-06 08:26:34 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL06OKASAK-OKA {"fill": 40, "age_min": 33, "mode": "SET_BELOW_FLOW(prints 11c above)", "emitted_et": "2026-07-06 08:26:34 AM ET"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06ARANIL-ARA {"fill": 73, "age_min": 32, "mode": "SET_BELOW_FLOW(prints 6c above)", "emitted_et": "2026-07-06 08:26:34 AM ET"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06TEUHAS-TEU {"price": 35, "ceiling": 34}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
