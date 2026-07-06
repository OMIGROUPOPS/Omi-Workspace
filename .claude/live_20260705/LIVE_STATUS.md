# LIVE VALIDATION — rolling status

- cycle 115 @ **2026-07-06 06:21:13 AM ET** | build `3b0211d` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 107065 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 6 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 23:50:46 | **walk_cap_breach** | KXITFWMATCH-26JUL06SIMCIR-SIM | buy 83c > ceiling 73c (conception 69 + cap) ref=join_bid |
| 01:01:56 | **combined_over_goal** | KXITFWMATCH-26JUL06TODSAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 01:12:30 | **combined_over_goal** | KXITFWMATCH-26JUL06VAJRAM | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |
| 03:38:20 | **combined_over_goal** | KXITFWMATCH-26JUL06DZJMCK | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 05:04:30 | **combined_over_goal** | KXITFMATCH-26JUL06HERNAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 05:09:22 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL06HERNGU | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 133 graded (session)
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
| 00:33 | ITFWMATCH-26JUL06WONIBR-IBR | ITF_W | leader | 65 | 52 | +13 (place_cell) | — | pre | single |  | PENDING |
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
| 02:21 | ITFWMATCH-26JUL06WAGYOU-YOU | ITF_W | leader | 63 | 49 | +14 (place_cell) | — | pre | pair | 97 | PENDING |
| 03:05 | ITFWMATCH-26JUL06ZRNLUE-ZRN | ITF_W | ? | 28 | 2 | +26 (place_cell) | — | pre | pair | 97 | PENDING |
| 03:16 | ITFWMATCH-26JUL06BOIBOY-BOI | ITF_W | leader | 77 | 75 | +2 (place_cell) | — | pre | single |  | PENDING |
| 03:29 | ITFMATCH-26JUL06SALNGW-NGW | ITF_M | ? | 39 | 32 | +7 (place_cell) | — | pre | pair | 97 | MIXED |
| 03:31 | ITFWMATCH-26JUL06KULGON-GON | ITF_W | ? | 22 | 16 | +6 (place_cell) | — | pre | single |  | PENDING |
| 03:34 | ITFMATCH-26JUL06HERNAG-HER | ITF_M | ? | 70 | 49 | +21 (place_cell) | — | pre | pair | 98 | PENDING |
| 03:38 | ITFWMATCH-26JUL06DZJMCK-DZJ | ITF_W | leader | 77 | 41 | +36 (place_cell) | — | pre | pair | 99 | PENDING |
| 03:38 | ITFWMATCH-26JUL06DZJMCK-MCK | ITF_W | underdog | 22 | 12 | +10 (place_cell) | — | pre | pair | 99 | PENDING |
| 03:39 | ITFWMATCH-26JUL06JOSKUM-JOS | ITF_W | underdog | 67 | 79 | -12 (place_cell) | — | pre | pair | 95 | MIXED |
| 03:39 | ITFWMATCH-26JUL06HEDCHI-CHI | ITF_W | underdog | 51 | 20 | +31 (place_cell) | — | pre | pair | 95 | EARNED |
| 03:41 | ITFWMATCH-26JUL06VLADIL-VLA | ITF_W | underdog | 41 | 34 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 03:50 | ITFWMATCH-26JUL06HEDCHI-HED | ITF_W | underdog | 44 | 13 | +31 (place_cell) | — | pre | pair | 95 | MIXED |
| 03:55 | ITFMATCH-26JUL06SALNGW-SAL | ITF_M | leader | 58 | 48 | +10 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:00 | ATPCHALLENGERMATCH-26JUL06PRIORA-P | ATP_CHALL | leader | 56 | 54 | +2 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
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
| 04:36 | ITFWMATCH-26JUL06LUKNOE-LUK | ITF_W | leader | 69 | 72 | -3 (place_cell) | — | pre | pair | 95 | PENDING |
| 04:44 | ITFWMATCH-26JUL06KARBAS-KAR | ITF_W | ? | 71 | 70 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:47 | ITFWMATCH-26JUL06LUKNOE-NOE | ITF_W | underdog | 26 | 27 | -1 (place_cell) | — | pre | pair | 95 | PENDING |
| 04:53 | WTAMATCH-26JUL06KRUKOS-KRU | WTA_MAIN | ? | 31 | 30 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:59 | ITFWMATCH-26JUL06DIANIK-DIA | ITF_W | underdog | 45 | 24 | +21 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:03 | ITFMATCH-26JUL06ELDHAU-ELD | ITF_M | leader | 65 | 56 | +9 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:04 | ITFMATCH-26JUL06HERNAG-NAG | ITF_M | ? | 28 | 1 | +27 (place_cell) | — | pre | pair | 98 | PENDING |
| 05:06 | ITFWMATCH-26JUL06OKUPRI-PRI | ITF_W | underdog | 41 | 25 | +16 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:06 | ATPCHALLENGERMATCH-26JUL06VILBOC-B | ATP_CHALL | underdog | 22 | 21 | +1 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:07 | WTACHALLENGERMATCH-26JUL06OLIUCH-U | WTA_CHALL | underdog | 39 | 37 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:07 | WTACHALLENGERMATCH-26JUL06BOUKOT-K | WTA_CHALL | leader | 77 | 74 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 05:08 | ITFWMATCH-26JUL06TEISCH-TEI | ITF_W | ? | 86 | 51 | +35 (place_cell) | — | pre | pair | 90 | PENDING |
| 05:09 | ITFWMATCH-26JUL06OKUPRI-OKU | ITF_W | leader | 56 | 49 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:09 | WTACHALLENGERMATCH-26JUL06HERNGU-H | WTA_CHALL | ? | 40 | 38 | +2 (place_cell) | — | pre | pair | 98 | EARNED |
| 05:09 | WTACHALLENGERMATCH-26JUL06HERNGU-N | WTA_CHALL | leader | 58 | 54 | +4 (place_cell) | — | pre | pair | 98 | GIFT_CLASS |
| 05:09 | WTACHALLENGERMATCH-26JUL06NOHBUR-B | WTA_CHALL | ? | 22 | 20 | +2 (place_cell) | -48.5 | pre | pair | 97 | EARNED |
| 05:09 | WTACHALLENGERMATCH-26JUL06BULSTR-S | WTA_CHALL | underdog | 29 | 23 | +6 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:09 | ITFWMATCH-26JUL06WAGYOU-WAG | ITF_W | underdog | 34 | 10 | +24 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:10 | WTACHALLENGERMATCH-26JUL06MONPOP-P | WTA_CHALL | ? | 54 | 51 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 05:10 | ATPCHALLENGERMATCH-26JUL06STALEC-S | ATP_CHALL | leader | 64 | 61 | +3 (place_cell) | — | pre | pair | 96 | GIFT_CLASS |
| 05:11 | ITFMATCH-26JUL06ELDHAU-HAU | ITF_M | underdog | 32 | 23 | +9 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:11 | ATPCHALLENGERMATCH-26JUL06CAMDE-CA | ATP_CHALL | leader | 58 | 56 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:11 | ITFWMATCH-26JUL06PIERAD-RAD | ITF_W | underdog | 33 | 18 | +15 (place_cell) | — | pre | single |  | PENDING |
| 05:12 | WTACHALLENGERMATCH-26JUL06NOHBUR-N | WTA_CHALL | leader | 75 | 73 | +2 (place_cell) | 37.0 | pre | pair | 97 | GIFT_CLASS |
| 05:12 | ATPCHALLENGERMATCH-26JUL06PAPJAN-P | ATP_CHALL | ? | 53 | 50 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 05:12 | WTACHALLENGERMATCH-26JUL06BULSTR-B | WTA_CHALL | ? | 68 | 68 | +0 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:13 | ITFWMATCH-26JUL06TRIVOR-VOR | ITF_W | leader | 89 | 49 | +40 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:15 | ITFWMATCH-26JUL06TRIVOR-TRI | ITF_W | ? | 8 | 1 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:15 | ITFWMATCH-26JUL06TEISCH-SCH | ITF_W | ? | 4 | 2 | +2 (place_cell) | — | pre | pair | 90 | PENDING |
| 05:16 | ITFWMATCH-26JUL06POPSOL-SOL | ITF_W | ? | 61 | 50 | +11 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:17 | ATPCHALLENGERMATCH-26JUL06STALEC-L | ATP_CHALL | underdog | 32 | 30 | +2 (place_cell) | — | pre | pair | 96 | EARNED |
| 05:18 | ITFMATCH-26JUL06LENTHE-THE | ITF_M | ? | 65 | 56 | +9 (place_cell) | — | pre | single |  | PENDING |
| 05:20 | WTACHALLENGERMATCH-26JUL06MONPOP-M | WTA_CHALL | underdog | 43 | 41 | +2 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:22 | ATPCHALLENGERMATCH-26JUL06PRIORA-O | ATP_CHALL | ? | 39 | 37 | +2 (place_cell) | — | pre | pair | 95 | EARNED |
| 05:25 | ITFWMATCH-26JUL06RICMIT-MIT | ITF_W | ? | 9 | 3 | +6 (place_cell) | — | pre | single |  | PENDING |
| 05:26 | ATPMATCH-26JUL06DECOB-COB | ATP_MAIN | underdog | 23 | 22 | +1 (place_cell) | — | pre | single |  | MIXED |
| 05:28 | ITFWMATCH-26JUL06IVAKUH-KUH | ITF_W | ? | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:30 | ITFMATCH-26JUL06DUGHOF-HOF | ITF_M | ? | 21 | 6 | +15 (place_cell) | — | pre | single |  | PENDING |
| 05:31 | ITFWMATCH-26JUL06PEEPAH-PAH | ITF_W | ? | 58 | 6 | +52 (place_cell) | — | pre | pair | 96 | PENDING |
| 05:32 | ITFWMATCH-26JUL06JOSKUM-KUM | ITF_W | underdog | 28 | 31 | -3 (place_cell) | — | pre | pair | 95 | EARNED |
| 05:32 | ATPCHALLENGERMATCH-26JUL06NIJRAH-N | ATP_CHALL | ? | 56 | 57 | -1 (window_cell) | — | pre | pair | 96 | MIXED |
| 05:32 | ITFWMATCH-26JUL06SPIMED-MED | ITF_W | ? | 8 | 1 | +7 (place_cell) | — | pre | pair | 96 | PENDING |
| 05:35 | ITFWMATCH-26JUL06GALTSE-GAL | ITF_W | leader | 77 | 71 | +6 (place_cell) | — | pre | single |  | PENDING |
| 05:38 | ITFWMATCH-26JUL06MILHER-HER | ITF_W | underdog | 16 | 3 | +13 (place_cell) | — | pre | single |  | PENDING |
| 05:39 | ATPCHALLENGERMATCH-26JUL06PIEMOL-P | ATP_CHALL | ? | 45 | 41 | +4 (place_cell) | — | pre | single |  | MIXED |
| 05:40 | ITFMATCH-26JUL06BEASCO-BEA | ITF_M | leader | 64 | 63 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:40 | ATPCHALLENGERMATCH-26JUL06SEYMAR-M | ATP_CHALL | underdog | 10 | 6 | +4 (place_cell) | — | pre | single |  | MIXED |
| 05:41 | ATPCHALLENGERMATCH-26JUL06POLHAI-P | ATP_CHALL | underdog | 31 | 28 | +3 (place_cell) | — | pre | single |  | PENDING |
| 05:41 | WTACHALLENGERMATCH-26JUL06LEWMAR-M | WTA_CHALL | ? | 43 | 40 | +3 (place_cell) | — | pre | single |  | MIXED |
| 05:41 | ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | ATP_CHALL | underdog | 26 | 23 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:42 | ATPCHALLENGERMATCH-26JUL06GOMLUZ-G | ATP_CHALL | ? | 71 | 68 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:44 | ATPCHALLENGERMATCH-26JUL06DALCAR-C | ATP_CHALL | underdog | 3 | 2 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:45 | WTACHALLENGERMATCH-26JUL06BOUKOT-B | WTA_CHALL | underdog | 20 | 20 | +0 (place_cell) | — | pre | pair | 97 | EARNED |
| 05:46 | ITFMATCH-26JUL06MEHCOU-COU | ITF_M | leader | 55 | 48 | +7 (place_cell) | — | pre | pair | 89 | PENDING |
| 05:51 | ATPCHALLENGERMATCH-26JUL06DALCAR-D | ATP_CHALL | leader | 94 | 93 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 05:51 | ITFMATCH-26JUL06SALBRE-SAL | ITF_M | leader | 90 | 86 | +4 (place_cell) | — | pre | single |  | PENDING |
| 05:52 | ITFWMATCH-26JUL06IVAKUH-IVA | ITF_W | ? | 60 | 59 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:54 | ITFMATCH-26JUL06ALEREG-ALE | ITF_M | leader | 51 | 48 | +3 (place_cell) | — | pre | single |  | PENDING |
| 05:56 | ITFWMATCH-26JUL06SPIMED-SPI | ITF_W | ? | 88 | 81 | +7 (place_cell) | — | pre | pair | 96 | PENDING |
| 05:57 | ITFWMATCH-26JUL06GANPUI-GAN | ITF_W | leader | 83 | 79 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:58 | ITFWMATCH-26JUL06KOTCHI-KOT | ITF_W | underdog | 52 | 21 | +31 (place_cell) | — | pre | pair | 97 | PENDING |
| 05:58 | WTACHALLENGERMATCH-26JUL06OLIUCH-O | WTA_CHALL | leader | 58 | 57 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:02 | ITFWMATCH-26JUL06PEEPAH-PEE | ITF_W | underdog | 38 | 4 | +34 (place_cell) | — | pre | pair | 96 | PENDING |
| 06:05 | ITFMATCH-26JUL06TEXCAR-TEX | ITF_M | leader | 67 | 74 | -7 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:06 | ITFWMATCH-26JUL06KOTCHI-CHI | ITF_W | ? | 45 | 41 | +4 (fill_est) | — | pre | pair | 97 | PENDING |
| 06:06 | ITFWMATCH-26JUL06PODLUK-LUK | ITF_W | leader | 70 | 53 | +17 (place_cell) | — | pre | single |  | PENDING |
| 06:07 | ITFMATCH-26JUL06VANHOR-VAN | ITF_M | leader | 63 | 60 | +3 (place_cell) | — | pre | single |  | PENDING |
| 06:07 | ITFWMATCH-26JUL06KARVIS-VIS | ITF_W | ? | 21 | 8 | +13 (place_cell) | — | pre | single |  | PENDING |
| 06:09 | ITFWMATCH-26JUL06VLADIL-DIL | ITF_W | leader | 56 | 52 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:09 | ATPMATCH-26JUL06DIMFER-FER | ATP_MAIN | underdog | 33 | 31 | +2 (place_cell) | — | pre | single |  | MIXED |
| 06:11 | ITFWMATCH-26JUL06ILIEBE-ILI | ITF_W | underdog | 45 | 37 | +8 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:11 | ATPCHALLENGERMATCH-26JUL06DELWAL-D | ATP_CHALL | underdog | 28 | 24 | +4 (place_cell) | — | pre | single |  | MIXED |
| 06:11 | ATPCHALLENGERMATCH-26JUL06BASHOE-H | ATP_CHALL | leader | 51 | 48 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 06:12 | WTAMATCH-26JUL06KRUKOS-KOS | WTA_MAIN | ? | 66 | 71 | -5 (window_cell) | — | pre | pair | 97 | MIXED |
| 06:12 | ATPCHALLENGERMATCH-26JUL06SEGBRA-B | ATP_CHALL | underdog | 36 | 33 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 06:14 | ITFMATCH-26JUL06TEXCAR-CAR | ITF_M | underdog | 30 | 32 | -2 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:15 | ITFWMATCH-26JUL06ILIEBE-EBE | ITF_W | ? | 52 | 49 | +3 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:15 | ITFWMATCH-26JUL06PACLOV-LOV | ITF_W | ? | 45 | 37 | +8 (place_cell) | — | pre | single |  | PENDING |
| 06:15 | ATPCHALLENGERMATCH-26JUL06POTFEL-P | ATP_CHALL | ? | 40 | 37 | +3 (place_cell) | — | pre | single |  | MIXED |
| 06:15 | ITFMATCH-26JUL06MEHCOU-MEH | ITF_M | ? | 34 | 21 | +13 (place_cell) | — | pre | pair | 89 | PENDING |
| 06:18 | ATPCHALLENGERMATCH-26JUL06SEGBRA-S | ATP_CHALL | ? | 61 | 58 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 06:20 | ITFWMATCH-26JUL06GANPUI-PUI | ITF_W | underdog | 14 | 4 | +10 (place_cell) | — | pre | pair | 97 | PENDING |

## RESTING BIDS — 196 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 19, 'FLOW_ABOVE': 59, 'NO_FLOW': 118} | repriceable now: true 18 / false 178 | **cumulative bid_grade lines: 1786 (repriceable true 183 / false 1603)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06BARDAL-B | 56 | 80m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06BARDAL-D | 41 | 80m | 1/42-42/20 | 41-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06BASHOE-B | 46 | 10m | 0 | 50-51 | — | **NO_FLOW** | 46 |  |
| ATPCHALLENGERMATCH-26JUL06CHADEM-C | 48 | 80m | 0 | 48-51 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CHEYEV-C | 61 | 201m | 5/62-62/116 | 61-62 | 1 | **FLOW_ABOVE** | 59 | flow above but bound 59c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06CHEYEV-Y | 37 | 201m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CHIJAN-C | 76 | 80m | 1/77-77/32 | 76-77 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| ATPCHALLENGERMATCH-26JUL06CHIJAN-J | 23 | 78m | 0 | 23-24 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DAMHUE-D | 79 | 80m | 1/80-80/30 | 79-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ATPCHALLENGERMATCH-26JUL06DAMHUE-H | 19 | 80m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DEHUD-DE | 38 | 80m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DEHUD-HU | 61 | 80m | 0 | 61-62 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DELWAL-W | 69 | 10m | 8/79-91/49 | 91-91 | 10 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-C | 24 | 140m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DONCIZ-D | 76 | 103m | 2/77-77/95 | 76-78 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-E | 95 | 230m | 0 | 95-96 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-S | 4 | 230m | 1/5-5/42 | 4-5 | 1 | **FLOW_ABOVE** | 2 | flow above but bound 2c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06FOMDHA-D | 52 | 80m | 0 | 52-54 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06FOMDHA-F | 45 | 80m | 2/46-46/39 | 45-46 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | 23 | 29m | 37/5-25/2429 | 5-6 | -18 | **FLOW_AT_LEVEL** | 23 |  |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-H | 35 | 230m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-P | 61 | 230m | 3/67-67/34 | 65-67 | 6 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06IVADIN-D | 20 | 171m | 2/20-21/322 | 20-21 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-I | 80 | 32m | 0 | 80-82 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KASCIN-C | 54 | 51m | 0 | 54-56 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KASCIN-K | 43 | 51m | 0 | 43-44 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 5 | 126m | 338/1-21/41967 | 19-1 | -4 | **FLOW_AT_LEVEL** | 5 |  |
| ATPCHALLENGERMATCH-26JUL06KUZSTR-K | 73 | 200m | 3/74-74/50 | 73-74 | 1 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06KUZSTR-S | 26 | 200m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KYMFAU-F | 32 | 49m | 0 | 32-33 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KYMFAU-K | 67 | 40m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARBER-B | 58 | 290m | 5/59-60/154 | 58-59 | 1 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06MARBER-M | 40 | 290m | 8/41-42/681 | 41-42 | 1 | **FLOW_ABOVE** | 39 | flow above but bound 39c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06MARHAM-H | 5 | 230m | 0 | 5-6 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARHAM-M | 94 | 217m | 1/95-95/0 | 94-96 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→95 |
| ATPCHALLENGERMATCH-26JUL06OPIPET-O | 28 | 32m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06OPIPET-P | 71 | 140m | 1/72-72/5 | 71-72 | 1 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-M | 52 | 30m | 23/70-86/451 | 75-71 | 18 | **FLOW_ABOVE** | 52 | flow above but bound 52c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06POLHAI-H | 66 | 40m | 0 | 70-72 | — | **NO_FLOW** | 66 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-F | 57 | 5m | 13/68-75/212 | 70-71 | 11 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06POTFEL-F | 57 | 5m | 13/68-75/212 | 70-71 | 11 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 61 | 230m | 2/69-69/19 | 62-68 | 8 | **FLOW_ABOVE** | 66 | flow above but bound 66c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 32 | 229m | 0 | 32-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06REHKOU-K | 44 | 51m | 5/45-45/910 | 44-45 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ATPCHALLENGERMATCH-26JUL06REHKOU-R | 55 | 32m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-S | 87 | 40m | 62/93-98/8075 | 98-97 | 6 | **FLOW_ABOVE** | 87 | flow above but bound 87c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 32m | 87/4-60/10235 | 6-7 | -29 | **FLOW_AT_LEVEL** | 33 |  |
| ATPCHALLENGERMATCH-26JUL06VALZHU-V | 71 | 171m | 2/73-73/22 | 71-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ATPCHALLENGERMATCH-26JUL06VALZHU-Z | 27 | 171m | 0 | 27-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06WALNEU-N | 28 | 139m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06WALNEU-W | 70 | 140m | 0 | 70-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06WEHVAN-V | 42 | 100m | 1/43-43/0 | 42-43 | 1 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06WEHVAN-W | 57 | 32m | 1/58-58/16 | 57-58 | 1 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-D | 42 | 230m | 1/44-44/11 | 42-43 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-Z | 56 | 230m | 1/59-59/83 | 57-59 | 3 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ATPMATCH-26JUL06DECOB-DE | 74 | 54m | 24/78-79/2303 | 78-79 | 4 | **FLOW_ABOVE** | 74 | flow above but bound 74c < flow -- chasing breaks goal |
| ATPMATCH-26JUL06DIMFER-DIM | 64 | 12m | 3/68-68/21 | 67-68 | 4 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06ALEREG-REG | 40 | 138m | 25/49-76/604 | 62-66 | 9 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06ALEREG-REG | 46 | 18m | 17/53-76/478 | 62-66 | 7 | **FLOW_ABOVE** | 46 | flow above but bound 46c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06ALIMIS-ALI | 91 | 119m | 0 | 91-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-MIS | 6 | 229m | 0 | 6-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BONFAU-BON | 66 | 32m | 0 | 66-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BONFAU-FAU | 26 | 15m | 0 | 26-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-DUG | 76 | 11m | 3/91-93/22 | 87-91 | 15 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06DUHCAR-CAR | 12 | 139m | 0 | 12-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUHCAR-DUH | 83 | 142m | 0 | 83-90 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GANVER-GAN | 5 | 49m | 0 | 45-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GANVER-VER | 48 | 25m | 0 | 48-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GARCIO-CIO | 39 | 142m | 1/43-43/22 | 39-44 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFMATCH-26JUL06GARCIO-GAR | 56 | 148m | 0 | 56-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 289m | 213/1-19/18095 | 18-1 | -15 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06HOSGAT-GAT | 38 | 142m | 0 | 38-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HOSGAT-HOS | 56 | 114m | 2/62-63/21 | 56-62 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06JAIHEN-JAI | 45 | 139m | 0 | 45-51 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-LIL | 28 | 122m | 205/1-55/9114 | 1-1 | -27 | **FLOW_AT_LEVEL** | 31 |  |
| ITFMATCH-26JUL06LAPCIO-CIO | 41 | 19m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LAPCIO-LAP | 54 | 18m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 32 | 15m | 0 | 32-65 | — | **NO_FLOW** | 32 |  |
| ITFMATCH-26JUL06LIBNAK-LIB | 38 | 64m | 0 | 38-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LIBNAK-NAK | 55 | 64m | 0 | 55-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LUEVAN-LUE | 65 | 31m | 0 | 65-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LUEVAN-VAN | 20 | 78m | 0 | 20-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-BEC | 87 | 140m | 0 | 87-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROJBEC-ROJ | 10 | 140m | 1/12-12/37 | 10-12 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→12 |
| ITFMATCH-26JUL06ROURAM-RAM | 53 | 18m | 0 | 53-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ROURAM-ROU | 37 | 19m | 0 | 37-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALBRE-BRE | 7 | 15m | 1/15-15/6 | 7-15 | 8 | **FLOW_ABOVE** | 7 | flow above but bound 7c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06STAGUI-GUI | 37 | 34m | 0 | 37-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STAGUI-STA | 48 | 9m | 0 | 48-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STEAUN-AUN | 14 | 140m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STEAUN-STE | 82 | 140m | 0 | 82-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TEUHAS-HAS | 63 | 113m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TEUHAS-TEU | 33 | 139m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TIMJEF-JEF | 71 | 131m | 0 | 71-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TIMJEF-TIM | 20 | 110m | 0 | 20-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TISVER-TIS | 25 | 9m | 0 | 25-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TISVER-VER | 23 | 9m | 0 | 23-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRA | 24 | 198m | 0 | 24-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRU | 67 | 106m | 0 | 67-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-AND | 24 | 127m | 0 | 24-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-TSI | 62 | 95m | 0 | 62-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06VANHOR-HOR | 30 | 19m | 1/36-36/1 | 30-36 | 6 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06VULCOU-VUL | 81 | 124m | 11/98-99/1550 | 99-85 | 17 | **FLOW_ABOVE** | 81 | flow above but bound 81c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ADKFER-ADK | 53 | 216m | 0 | 53-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ADKFER-FER | 18 | 216m | 0 | 18-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 185m | 0 | 28-32 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 131m | 0 | 28-32 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06BOSTOP-BOS | 68 | 21m | 0 | 68-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOSTOP-TOP | 33 | 261m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOWMAT-BOW | 6 | 15m | 0 | 6-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 312m | 4430/1-99/518199 | 5-1 | -33 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06BUYALV-ALV | 22 | 191m | 0 | 22-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BUYALV-BUY | 54 | 152m | 0 | 54-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CENBUL-BUL | 19 | 77m | 0 | 19-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06CENBUL-CEN | 49 | 64m | 0 | 69-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DRISLA-DRI | 25 | 9m | 0 | 25-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DRISLA-SLA | 57 | 12m | 0 | 57-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EWAMAN-EWA | 69 | 32m | 0 | 69-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EWAMAN-MAN | 20 | 182m | 0 | 20-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06FAVKLY-FAV | 12 | 9m | 0 | 12-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06FAVKLY-KLY | 8 | 64m | 0 | 8-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-TSE | 16 | 46m | 0 | 17-22 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06HIEGUT-GUT | 56 | 76m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HIEGUT-HIE | 41 | 80m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 25 | 106m | 1/99-99/12 | 99-58 | 74 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARVIS-KAR | 76 | 14m | 3/84-89/66 | 88-90 | 8 | **FLOW_ABOVE** | 76 | flow above but bound 76c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KOVDAE-DAE | 20 | 1m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOVDAE-KOV | 75 | 170m | 0 | 75-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 170m | 1/79-79/5 | 75-80 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 170m | 1/79-79/5 | 75-80 | 4 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KULGON-KUL | 71 | 87m | 0 | 75-80 | — | **NO_FLOW** | 75 |  |
| ITFWMATCH-26JUL06KULVOG-KUL | 54 | 77m | 0 | 54-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULVOG-VOG | 36 | 77m | 0 | 36-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LABTSY-LAB | 27 | 49m | 0 | 27-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LABTSY-TSY | 59 | 49m | 0 | 59-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 358m | 3895/23-99/459986 | 99-24 | -14 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06MARGLU-GLU | 66 | 114m | 0 | 66-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MARGLU-MAR | 28 | 139m | 0 | 28-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-ENC | 51 | 188m | 0 | 51-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-MCA | 42 | 176m | 0 | 42-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MILHER-MIL | 81 | 54m | 0 | 81-90 | — | **NO_FLOW** | 81 |  |
| ITFWMATCH-26JUL06OKASAK-OKA | 27 | 98m | 0 | 27-51 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-PRI | 41 | 24m | 27/39-72/3174 | 64-62 | -2 | **FLOW_AT_LEVEL** | 41 |  |
| ITFWMATCH-26JUL06PACLOV-PAC | 52 | 6m | 0 | 55-57 | — | **NO_FLOW** | 52 |  |
| ITFWMATCH-26JUL06PACLOV-PAC | 52 | 4m | 0 | 55-57 | — | **NO_FLOW** | 52 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 261m | 1942/1-13/312225 | 14-1 | -7 | **FLOW_AT_LEVEL** | 12 |  |
| ITFWMATCH-26JUL06PIERAD-PIE | 64 | 70m | 84/84-99/3466 | 97-91 | 20 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06PIERAD-PIE | 64 | 9m | 39/90-99/2908 | 97-91 | 26 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06PODLUK-POD | 27 | 51m | 0 | 27-45 | — | **NO_FLOW** | 27 |  |
| ITFWMATCH-26JUL06POZMLA-MLA | 5 | 152m | 0 | 5-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-NIJ | 30 | 170m | 0 | 30-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-PRI | 63 | 170m | 0 | 63-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06REEION-REE | 32 | 15m | 0 | 32-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SACLAZ-LAZ | 15 | 117m | 648/1-33/45125 | 40-1 | -14 | **FLOW_AT_LEVEL** | 1 |  |
| ITFWMATCH-26JUL06SCHELI-ELI | 33 | 9m | 0 | 33-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 308m | 16366/1-95/1383948 | 83-1 | -13 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06STETRA-STE | 78 | 77m | 0 | 78-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06STETRA-TRA | 16 | 77m | 0 | 16-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-EVA | 37 | 48m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-URR | 61 | 140m | 0 | 61-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 308m | 6096/1-29/750264 | 21-1 | -14 | **FLOW_AT_LEVEL** | 5 |  |
| ITFWMATCH-26JUL06VIRKOV-KOV | 29 | 152m | 0 | 29-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VIRKOV-VIR | 56 | 185m | 0 | 56-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-VLA | 30 | 4m | 77/24-41/3896 | 34-29 | -6 | **FLOW_AT_LEVEL** | 41 |  |
| ITFWMATCH-26JUL06WONIBR-WON | 32 | 306m | 76/72-97/3042 | 92-97 | 40 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ARANIL-A | 73 | 218m | 2/75-75/114 | 73-75 | 2 | **FLOW_ABOVE** | 72 | flow above but bound 72c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ARANIL-N | 25 | 230m | 1/26-26/9 | 25-26 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 74 | 140m | 1/76-76/25 | 74-76 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| WTACHALLENGERMATCH-26JUL06BASBAD-B | 24 | 140m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BLIAND-A | 35 | 140m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BLIAND-B | 64 | 140m | 2/65-65/52 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| WTACHALLENGERMATCH-26JUL06BOUKOT-K | 77 | 14m | 55/95-99/3960 | 96-97 | 18 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06DENQUE-D | 4 | 51m | 0 | 4-6 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06DENQUE-Q | 93 | 51m | 0 | 93-96 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06GRAMAS-G | 32 | 230m | 1/33-33/100 | 32-33 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| WTACHALLENGERMATCH-26JUL06GRAMAS-M | 67 | 230m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 39 | 30m | 108/84-99/18486 | 99-99 | 45 | **FLOW_ABOVE** | 39 | flow above but bound 39c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06HESPAL-H | 30 | 231m | 0 | 30-31 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HESPAL-P | 69 | 231m | 2/70-70/24 | 69-70 | 1 | **FLOW_ABOVE** | 67 | flow above but bound 67c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06LEWMAR-L | 54 | 40m | 0 | 55-57 | — | **NO_FLOW** | 54 |  |
| WTACHALLENGERMATCH-26JUL06LEWMAR-L | 54 | 38m | 0 | 55-57 | — | **NO_FLOW** | 54 |  |
| WTACHALLENGERMATCH-26JUL06MATPUT-M | 9 | 230m | 3/9-10/94 | 9-10 | 0 | **FLOW_AT_LEVEL** | 7 |  |
| WTACHALLENGERMATCH-26JUL06MATPUT-P | 89 | 230m | 3/90-91/45 | 90-93 | 1 | **FLOW_ABOVE** | 87 | flow above but bound 87c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06OLIUCH-U | 39 | 17m | 129/20-39/8179 | 26-21 | -19 | **FLOW_AT_LEVEL** | 37 |  |
| WTACHALLENGERMATCH-26JUL06ROMSEM-R | 42 | 200m | 1/44-44/21 | 42-43 | 2 | **FLOW_ABOVE** | 41 | flow above but bound 41c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ROMSEM-S | 57 | 11m | 1/58-58/20 | 57-58 | 1 | **FLOW_ABOVE** | 55 | flow above but bound 55c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06WALKAW-K | 43 | 140m | 4/44-44/206 | 43-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| WTACHALLENGERMATCH-26JUL06WALKAW-W | 55 | 140m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06WERSAL-S | 67 | 140m | 1/68-68/17 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| WTACHALLENGERMATCH-26JUL06WERSAL-W | 31 | 140m | 0 | 31-32 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL06BOUMER-BOU | 46 | 32m | 19/46-47/11172 | 46-47 | 0 | **FLOW_AT_LEVEL** | 44 |  |
| WTAMATCH-26JUL06BOUMER-MER | 54 | 51m | 18/55-55/3245 | 54-55 | 1 | **FLOW_ABOVE** | 55 | REPRICEABLE→55 |
| WTAMATCH-26JUL06KEYNOS-KEY | 58 | 18m | 4/58-59/168 | 58-59 | 0 | **FLOW_AT_LEVEL** | 59 |  |
| WTAMATCH-26JUL06KEYNOS-NOS | 43 | 15m | 3/44-44/329 | 43-44 | 1 | **FLOW_ABOVE** | 41 | flow above but bound 41c < flow -- chasing breaks goal |
| WTAMATCH-26JUL06PAOEAL-EAL | 60 | 32m | 34/60-61/14219 | 60-61 | 0 | **FLOW_AT_LEVEL** | 61 |  |
| WTAMATCH-26JUL06PAOEAL-PAO | 39 | 32m | 7/40-40/415 | 39-40 | 1 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06PAPJAN | 53 | 42 | **95** | 97 | -2 |
| ITFWMATCH-26JUL06GALTSE | 77 | 22 | **99** | 97 | +2 |
| ITFMATCH-26JUL06VANHOR | 63 | 36 | **99** | 97 | +2 |
| WTACHALLENGERMATCH-26JUL06LEWMAR | 43 | 57 | **100** | 97 | +3 |
| ATPMATCH-26JUL06DIMFER | 33 | 68 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06KULGON | 22 | 80 | **102** | 97 | +5 |
| ATPMATCH-26JUL06DECOB | 23 | 79 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL06BASHOE | 51 | 51 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06PACLOV | 45 | 57 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL06POLHAI | 31 | 72 | **103** | 97 | +6 |
| ITFMATCH-26JUL06SALBRE | 90 | 15 | **105** | 97 | +8 |
| ITFWMATCH-26JUL06MILHER | 16 | 90 | **106** | 97 | +9 |
| ATPCHALLENGERMATCH-26JUL06SEYMAR | 10 | 97 | **107** | 97 | +10 |
| ITFWMATCH-26JUL06BOIBOY | 77 | 32 | **109** | 97 | +12 |
| ITFWMATCH-26JUL06KARVIS | 21 | 90 | **111** | 97 | +14 |
| ATPCHALLENGERMATCH-26JUL06POTFEL | 40 | 71 | **111** | 97 | +14 |
| ITFMATCH-26JUL06DUGHOF | 21 | 91 | **112** | 97 | +15 |
| ITFWMATCH-26JUL06PODLUK | 70 | 45 | **115** | 97 | +18 |
| ITFMATCH-26JUL06CASBAY | 45 | 71 | **116** | 97 | +19 |
| ATPCHALLENGERMATCH-26JUL06PIEMOL | 45 | 71 | **116** | 97 | +19 |
| ITFMATCH-26JUL06ALEREG | 51 | 66 | **117** | 97 | +20 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ATPCHALLENGERMATCH-26JUL06DELWAL | 28 | 91 | **119** | 97 | +22 |
| ITFWMATCH-26JUL06PIERAD | 33 | 91 | **124** | 97 | +27 |
| ITFMATCH-26JUL06LENTHE | 65 | 65 | **130** | 97 | +33 |
| ITFWMATCH-26JUL06WONIBR | 65 | 97 | **162** | 97 | +65 |

## PATTERNS (sub-B) — 49
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
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 376, "mode": "SET_BELOW_FLOW(prints 74c above)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 29, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 30, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 31, "ceiling": 20}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 32, "ceiling": 20}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 348, "mode": "SET_BELOW_FLOW(prints 40c above)"}
- uncorrelated_buy_above_ceiling: KXITFMATCH-26JUL06BEASCO-SCO {"price": 33, "ceiling": 20}
- half_arm_aging: KXITFWMATCH-26JUL06BOIBOY-BOI {"fill": 77, "age_min": 185, "mode": "STARVATION(no prints since post)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06DIANIK-NIK {"price": 41, "ceiling": 38}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06DIANIK-NIK {"price": 52, "ceiling": 38}
- half_arm_aging: KXITFWMATCH-26JUL06KULGON-GON {"fill": 22, "age_min": 170, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06JOSKUM-JOS {"price": 61, "ceiling": 59}
- uncorrelated_buy_above_ceiling: KXITFWMATCH-26JUL06JOSKUM-JOS {"price": 67, "ceiling": 59}
- half_arm_aging: KXITFMATCH-26JUL06CASBAY-CAS {"fill": 45, "age_min": 119, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXWTACHALLENGERMATCH-26JUL06NOHBUR-BUR {"entry_minus_fv_burst": -48.5, "emitted_et": "2026-07-06 06:21:13 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL06PIERAD-RAD {"fill": 33, "age_min": 70, "mode": "SET_BELOW_FLOW(prints 20c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06PAPJAN-PAP {"fill": 53, "age_min": 68, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL06LENTHE-THE {"fill": 65, "age_min": 63, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06RICMIT-MIT {"fill": 9, "age_min": 56, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPMATCH-26JUL06DECOB-COB {"fill": 23, "age_min": 54, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFMATCH-26JUL06DUGHOF-HOF {"fill": 21, "age_min": 51, "mode": "SET_BELOW_FLOW(prints 15c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06GALTSE-GAL {"fill": 77, "age_min": 46, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06MILHER-HER {"fill": 16, "age_min": 43, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06PIEMOL-PIE {"fill": 45, "age_min": 42, "mode": "SET_BELOW_FLOW(prints 18c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06SEYMAR-MAR {"fill": 10, "age_min": 40, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06POLHAI-POL {"fill": 31, "age_min": 40, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-06 06:21:13 AM ET"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL06LEWMAR-MAR {"fill": 43, "age_min": 40, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-06 06:21:13 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
