# LIVE VALIDATION — rolling status

- cycle 94 @ **2026-07-12 04:28:50 AM ET** | build `4b3facb0` | session boot 07-11 00:38 ET | log `live_v3_20260711.jsonl` | 159470 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 8 item(s)
- **half_arm_aging**: KXITFMATCH-26JUL12MILARZ-ARZ {"fill": 27, "age_min": 193, "mode": "NO_BID(sib rested earlier, none now)"}
- **half_arm_aging**: KXATPCHALLENGERMATCH-26JUL12ALVVAN-VAN {"fill": 22, "age_min": 189, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- **half_arm_aging**: KXITFMATCH-26JUL12MONSHI-MON {"fill": 85, "age_min": 148, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- **half_arm_aging**: KXATPCHALLENGERMATCH-26JUL12DELMAK-DEL {"fill": 8, "age_min": 132, "mode": "STARVATION(no prints since post)"}
- **half_arm_aging**: KXWTAMATCH-26JUL12GARPRI-GAR {"fill": 39, "age_min": 88, "mode": "NO_BID(sib rested earlier, none now)"}
- **half_arm_aging**: KXWTAMATCH-26JUL12KULZAA-ZAA {"fill": 67, "age_min": 83, "mode": "NO_BID(sib rested earlier, none now)"}
- **half_arm_aging**: KXITFWMATCH-26JUL12TOMKAR-KAR {"fill": 54, "age_min": 66, "mode": "NO_BID(sib rested earlier, none now)"}
- **reality_divergence**: KXITFMATCH-26JUL12REYBAR-BAR {"kind": "resting_bid", "ref": 6.0, "market_mid": 73.0, "divergence": -67.0}
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 14 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 04:10:14 | **bell_missing** | KXITFWMATCH-26JUL11STATOM | min_past_start 10.2 |
| 05:10:23 | **bell_missing** | KXITFMATCH-26JUL11SNIMAZ | min_past_start 10.4 |
| 08:08:27 | **combined_over_goal** | KXWTACHALLENGERMATCH-26JUL11WALBAD | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 10:40:46 | **bell_missing** | KXWTAMATCH-26JUL11YASGLU | min_past_start 10.8 |
| 11:10:11 | **bell_missing** | KXATPCHALLENGERMATCH-26JUL11SOTCLA | min_past_start 10.2 |
| 11:10:11 | **bell_missing** | KXITFWMATCH-26JUL11FULSOU | min_past_start 10.2 |
| 12:10:31 | **bell_missing** | KXWTACHALLENGERMATCH-26JUL11MINVOL | min_past_start 10.5 |
| 12:10:31 | **bell_missing** | KXITFMATCH-26JUL11BAXLOK | min_past_start 10.5 |
| 13:00:30 | **bell_missing** | KXWTAMATCH-26JUL11MORSZI | min_past_start 10.5 |
| 13:08:57 | **combined_over_goal** | KXITFWMATCH-26JUL11MIRMAL | pair combined 99c > goal 97c [organic: DEFECT-CLASS] |
| 13:10:17 | **bell_missing** | KXITFMATCH-26JUL11JOHKLA | min_past_start 10.3 |
| 16:10:04 | **bell_missing** | KXITFMATCH-26JUL11SAMLOP | min_past_start 10.1 |
| 17:10:09 | **bell_missing** | KXITFMATCH-26JUL11RICHAR | min_past_start 10.2 |
| 17:10:09 | **bell_missing** | KXITFMATCH-26JUL11BERBEN | min_past_start 10.2 |

## FILLS — 130 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 01:00 | ITFWMATCH-26JUL11MAKSHO-SHO | ITF_W | ? | 50 | 42 | +8 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 01:01 | ITFMATCH-26JUL11LAGRIV-LAG | ITF_M | leader | 69 | 67 | +2 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 01:25 | ITFWMATCH-26JUL11ERCHRU-HRU | ITF_W | ? | 82 | 80 | +2 (fill_est) | — | pre | single |  | PENDING |
| 01:33 | ITFMATCH-26JUL11DOUROB-ROB | ITF_M | underdog | 11 | 6 | +5 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:34 | ITFWMATCH-26JUL11SAGYOD-SAG | ITF_W | underdog | 41 | 38 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 01:46 | ITFMATCH-26JUL11SNIMAZ-SNI | ITF_M | leader | 75 | 71 | +4 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 01:49 | ITFMATCH-26JUL11SHIROB-ROB | ITF_M | leader | 68 | 67 | +1 (place_cell) | — | pre | single |  | MIXED |
| 02:04 | ITFWMATCH-26JUL11SAGYOD-YOD | ITF_W | ? | 56 | 53 | +3 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 02:08 | ATPMATCH-26JUL11HUEBUT-BUT | ATP_MAIN | leader | 51 | 52 | -1 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 02:46 | ATPMATCH-26JUL11MONHER-MON | ATP_MAIN | leader | 59 | 60 | -1 (place_cell) | 11.5 | pre | single |  | GIFT_CLASS |
| 03:18 | ITFWMATCH-26JUL11STATOM-STA | ITF_W | leader | 62 | 60 | +2 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 03:23 | ITFWMATCH-26JUL11SHEYAM-YAM | ITF_W | leader | 53 | 50 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 03:32 | ITFWMATCH-26JUL11HOSCIR-HOS | ITF_W | leader | 64 | 64 | +0 (place_cell) | — | pre | single |  | MIXED |
| 03:35 | ITFWMATCH-26JUL11SMILEY-LEY | ITF_W | leader | 61 | 60 | +1 (place_cell) | — | pre | single |  | MIXED |
| 03:42 | ITFWMATCH-26JUL11KUBRYS-RYS | ITF_W | ? | 33 | 92 | -59 (window_cell) | — | pre | single |  | EARNED |
| 03:53 | ITFWMATCH-26JUL11PERWIE-WIE | ITF_W | underdog | 18 | 15 | +3 (place_cell) | — | pre | single |  | PENDING |
| 04:03 | ITFWMATCH-26JUL11DENSTR-DEN | ITF_W | leader | 51 | 50 | +1 (place_cell) | — | pre | single |  | PENDING |
| 04:05 | ATPMATCH-26JUL11VIRDIE-VIR | ATP_MAIN | leader | 65 | 66 | -1 (place_cell) | 4.5 | pre | single |  | GIFT_CLASS |
| 04:06 | ITFWMATCH-26JUL11KALTIK-TIK | ITF_W | leader | 63 | 62 | +1 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 04:06 | ITFWMATCH-26JUL11KARSUP-SUP | ITF_W | underdog | 40 | 36 | +4 (place_cell) | — | pre | single |  | MIXED |
| 04:10 | ITFWMATCH-26JUL11KALTIK-KAL | ITF_W | underdog | 32 | 37 | -5 (place_cell) | — | pre | pair | 95 | EARNED |
| 04:10 | ITFWMATCH-26JUL11STATOM-TOM | ITF_W | underdog | 35 | 32 | +3 (place_cell) | — | pre | pair | 97 | EARNED |
| 04:31 | ITFMATCH-26JUL11DOUROB-DOU | ITF_M | ? | 86 | 85 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 04:32 | ITFMATCH-26JUL11DURBAR-BAR | ITF_M | underdog | 39 | 35 | +4 (place_cell) | — | pre | single |  | MIXED |
| 04:36 | ITFWMATCH-26JUL11FONROJ-ROJ | ITF_W | ? | 44 | 40 | +4 (place_cell) | — | pre | single |  | EARNED |
| 04:46 | ITFMATCH-26JUL11TALPAP-PAP | ITF_M | leader | 58 | 50 | +8 (place_cell) | — | pre | single |  | MIXED |
| 04:50 | ATPMATCH-26JUL11DHASAC-DHA | ATP_MAIN | underdog | 35 | 32 | +3 (place_cell) | 1.5 | pre | single |  | MIXED |
| 05:00 | ATPMATCH-26JUL11MICHEM-HEM | ATP_MAIN | underdog | 49 | 50 | -1 (place_cell) | 0.0 | pre | single |  | MIXED |
| 05:07 | ATPCHALLENGERMATCH-26JUL11RINCHO-R | ATP_CHALL | underdog | 32 | 29 | +3 (place_cell) | 14.5 | pre | single |  | GIFT_CLASS |
| 05:31 | ITFMATCH-26JUL11ROHBOR-ROH | ITF_M | leader | 53 | 50 | +3 (place_cell) | — | pre | single |  | PENDING |
| 05:33 | WTAMATCH-26JUL11ASLSIE-SIE | WTA_MAIN | leader | 89 | 89 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 05:43 | ITFMATCH-26JUL11FABARZ-ARZ | ITF_M | leader | 71 | 68 | +3 (place_cell) | — | pre | single |  | MIXED |
| 05:58 | ATPMATCH-26JUL11CINZAH-CIN | ATP_MAIN | ? | 87 | 87 | +0 (place_cell) | 1.5 | pre | single |  | GIFT_CLASS |
| 05:58 | ITFWMATCH-26JUL11BOSKAR-KAR | ITF_W | underdog | 39 | 34 | +5 (place_cell) | — | pre | single |  | EARNED |
| 06:03 | ITFWMATCH-26JUL11LEEJOR-JOR | ITF_W | underdog | 43 | 39 | +4 (place_cell) | — | pre | single |  | MIXED |
| 06:10 | ITFMATCH-26JUL11NORKOI-NOR | ITF_M | leader | 62 | 58 | +4 (place_cell) | — | pre | single |  | MIXED |
| 06:29 | ATPMATCH-26JUL11SKACHA-CHA | ATP_MAIN | underdog | 6 | 5 | +1 (place_cell) | 0.5 | pre | single |  | MIXED |
| 06:33 | ATPCHALLENGERMATCH-26JUL11CHIGRA-C | ATP_CHALL | underdog | 42 | 39 | +3 (place_cell) | -46.5 | pre | pair | 97 | EARNED |
| 06:39 | ITFMATCH-26JUL11NICJUA-NIC | ITF_M | leader | 73 | 71 | +2 (place_cell) | — | pre | single |  | MIXED |
| 06:44 | ITFMATCH-26JUL11RECWIS-REC | ITF_M | ? | 32 | 27 | +5 (place_cell) | — | pre | pair | 97 | PENDING |
| 06:49 | ITFMATCH-26JUL11RECWIS-WIS | ITF_M | leader | 65 | 64 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 07:13 | ITFWMATCH-26JUL11SHIGAO-GAO | ITF_W | leader | 61 | 58 | +3 (place_cell) | — | pre | single |  | MIXED |
| 07:19 | ITFWMATCH-26JUL11KOVVED-KOV | ITF_W | underdog | 42 | 37 | +5 (place_cell) | — | pre | pair | 97 | MIXED |
| 07:23 | WTAMATCH-26JUL11HODCHA-HOD | WTA_MAIN | leader | 91 | 90 | +1 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 08:04 | ATPMATCH-26JUL11NARGUE-NAR | ATP_MAIN | leader | 57 | 57 | +0 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 08:05 | ATPCHALLENGERMATCH-26JUL11SEABAS-B | ATP_CHALL | ? | 22 | 19 | +3 (place_cell) | -1.5 | pre | single |  | MIXED |
| 08:08 | WTACHALLENGERMATCH-26JUL11WALBAD-W | WTA_CHALL | underdog | 28 | 26 | +2 (place_cell) | — | pre | pair | 99 | MIXED |
| 08:08 | WTACHALLENGERMATCH-26JUL11WALBAD-B | WTA_CHALL | leader | 71 | 69 | +2 (place_cell) | — | pre | pair | 99 | GIFT_CLASS |
| 08:12 | ITFWMATCH-26JUL11SOBAVD-SOB | ITF_W | leader | 60 | 57 | +3 (place_cell) | — | pre | single |  | MIXED |
| 08:19 | ATPMATCH-26JUL11TOPMAR-MAR | ATP_MAIN | leader | 62 | 61 | +1 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 08:20 | ATPMATCH-26JUL11VUKOLI-OLI | ATP_MAIN | ? | 70 | 72 | -2 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 08:21 | ATPCHALLENGERMATCH-26JUL11GIUDAM-D | ATP_CHALL | ? | 39 | 36 | +3 (place_cell) | 1.0 | pre | single |  | MIXED |
| 08:21 | ATPCHALLENGERMATCH-26JUL11BERDEL-B | ATP_CHALL | underdog | 30 | 27 | +3 (place_cell) | — | pre | single |  | MIXED |
| 08:23 | ITFMATCH-26JUL11KELWES-KEL | ITF_M | ? | 63 | 60 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 08:23 | ATPCHALLENGERMATCH-26JUL11CHIGRA-G | ATP_CHALL | ? | 55 | 55 | +0 (place_cell) | 43.5 | pre | pair | 97 | GIFT_CLASS |
| 08:49 | WTAMATCH-26JUL11YASGLU-YAS | WTA_MAIN | ? | 16 | 14 | +2 (place_cell) | 2.5 | pre | pair | 97 | MIXED |
| 08:49 | ITFWMATCH-26JUL11KOVVED-VED | ITF_W | ? | 55 | 54 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 08:52 | WTAMATCH-26JUL11TSEMAN-MAN | WTA_MAIN | leader | 94 | 93 | +1 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 08:59 | WTAMATCH-26JUL11MICNIN-NIN | WTA_MAIN | ? | 16 | 14 | +2 (place_cell) | — | pre | single |  | MIXED |
| 09:06 | ATPCHALLENGERMATCH-26JUL11PIRKYM-P | ATP_CHALL | leader | 59 | 55 | +4 (place_cell) | 0.5 | pre | single |  | GIFT_CLASS |
| 09:28 | ITFWMATCH-26JUL11MARPAR-MAR | ITF_W | leader | 51 | 49 | +2 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 09:59 | ATPCHALLENGERMATCH-26JUL11DIAGAS-G | ATP_CHALL | underdog | 34 | 31 | +3 (place_cell) | 20.5 | pre | pair | 97 | GIFT_CLASS |
| 10:01 | ATPCHALLENGERMATCH-26JUL11DIAGAS-D | ATP_CHALL | leader | 63 | 61 | +2 (place_cell) | -23.0 | pre | pair | 97 | EARNED |
| 10:02 | ITFWMATCH-26JUL11BABGER-BAB | ITF_W | ? | 82 | 77 | +5 (place_cell) | — | pre | pair | 96 | PENDING |
| 10:05 | ITFMATCH-26JUL11SAMLOP-SAM | ITF_M | underdog | 8 | 4 | +4 (place_cell) | — | pre | pair | 83 | PENDING |
| 10:07 | ITFWMATCH-26JUL11MARPAR-PAR | ITF_W | ? | 46 | 42 | +4 (place_cell) | — | pre | pair | 97 | EARNED |
| 10:07 | ITFWMATCH-26JUL11HOSDAA-DAA | ITF_W | ? | 42 | 37 | +5 (place_cell) | — | pre | single |  | MIXED |
| 10:08 | ITFMATCH-26JUL11MCIALF-ALF | ITF_M | underdog | 17 | 18 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 10:09 | ITFMATCH-26JUL11FRAMAR-MAR | ITF_M | leader | 61 | 91 | -30 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 10:11 | ITFWMATCH-26JUL11BABGER-GER | ITF_W | underdog | 14 | 17 | -3 (place_cell) | — | pre | pair | 96 | PENDING |
| 10:20 | ITFMATCH-26JUL11MCIALF-MCI | ITF_M | ? | 80 | 83 | -3 (window_cell) | — | pre | pair | 97 | MIXED |
| 10:29 | WTAMATCH-26JUL11RENTON-REN | WTA_MAIN | ? | 12 | 10 | +2 (place_cell) | — | pre | single |  | MIXED |
| 10:29 | WTACHALLENGERMATCH-26JUL11MINVOL-M | WTA_CHALL | underdog | 47 | 44 | +3 (place_cell) | — | pre | single |  | MIXED |
| 10:47 | ITFMATCH-26JUL11SAMLOP-LOP | ITF_M | ? | 75 | 91 | -16 (place_cell) | — | pre | pair | 83 | PENDING |
| 10:52 | ATPMATCH-26JUL11CECAJD-CEC | ATP_MAIN | ? | 74 | 74 | +0 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 10:55 | ITFMATCH-26JUL11CIGZAR-CIG | ITF_M | underdog | 26 | 20 | +6 (place_cell) | — | pre | single |  | MIXED |
| 11:11 | ITFWMATCH-26JUL11FULSOU-FUL | ITF_W | leader | 77 | 73 | +4 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 11:14 | ATPCHALLENGERMATCH-26JUL11SOTCLA-C | ATP_CHALL | underdog | 35 | 32 | +3 (place_cell) | — | pre | single |  | MIXED |
| 11:19 | ATPMATCH-26JUL11BRAGOM-BRA | ATP_MAIN | leader | 54 | 54 | +0 (place_cell) | 1.0 | pre | single |  | GIFT_CLASS |
| 11:23 | ITFMATCH-26JUL11BAXLOK-LOK | ITF_M | leader | 60 | 57 | +3 (place_cell) | — | pre | pair | 97 | PENDING |
| 11:24 | ITFMATCH-26JUL11MIYLEG-MIY | ITF_M | underdog | 41 | 36 | +5 (place_cell) | -21.0 | pre | single |  | EARNED |
| 11:27 | ITFMATCH-26JUL11SVAZHU-SVA | ITF_M | leader | 85 | 82 | +3 (place_cell) | — | pre | single |  | MIXED |
| 11:27 | ITFWMATCH-26JUL11GORKOS-GOR | ITF_W | underdog | 25 | 21 | +4 (place_cell) | — | pre | pair | 97 | EARNED |
| 11:35 | ATPMATCH-26JUL11CECAJD-AJD | ATP_MAIN | underdog | 23 | 24 | -1 (place_cell) | — | pre | pair | 97 | EARNED |
| 11:37 | WTAMATCH-26JUL11PANKUL-PAN | WTA_MAIN | underdog | 9 | 6 | +3 (place_cell) | — | pre | single |  | MIXED |
| 11:39 | ITFWMATCH-26JUL11GORKOS-KOS | ITF_W | leader | 72 | 71 | +1 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 11:39 | WTAMATCH-26JUL11MORSZI-SZI | WTA_MAIN | underdog | 22 | 20 | +2 (place_cell) | 9.5 | pre | pair | 97 | GIFT_CLASS |
| 11:42 | WTAMATCH-26JUL11YASGLU-GLU | WTA_MAIN | leader | 81 | 83 | -2 (place_cell) | -6.5 | pre | pair | 97 | EARNED |
| 11:46 | ITFMATCH-26JUL11BERBEN-BEN | ITF_M | leader | 86 | 83 | +3 (place_cell) | — | pre | pair | 96 | MIXED |
| 11:49 | ATPCHALLENGERMATCH-26JUL11WALMIC-W | ATP_CHALL | underdog | 33 | 30 | +3 (place_cell) | -23.5 | pre | single |  | EARNED |
| 11:50 | ATPCHALLENGERMATCH-26JUL11GALFEA-G | ATP_CHALL | underdog | 30 | 27 | +3 (place_cell) | -1.0 | pre | single |  | MIXED |
| 11:52 | ITFMATCH-26JUL11FRAMAR-FRA | ITF_M | ? | 36 | 47 | -11 (window_cell) | — | pre | pair | 97 | EARNED |
| 11:52 | WTAMATCH-26JUL11TANNEP-TAN | WTA_MAIN | underdog | 35 | 33 | +2 (place_cell) | -40.0 | pre | pair | 97 | EARNED |
| 11:55 | ITFMATCH-26JUL11ERECRA-CRA | ITF_M | ? | 60 | 56 | +4 (place_cell) | — | pre | single |  | PENDING |
| 12:04 | ITFMATCH-26JUL11YOUKIM-YOU | ITF_M | ? | 48 | 43 | +5 (place_cell) | — | pre | single |  | EARNED |
| 12:05 | WTAMATCH-26JUL11TANNEP-NEP | WTA_MAIN | leader | 62 | 63 | -1 (place_cell) | 35.5 | pre | pair | 97 | GIFT_CLASS |
| 12:09 | ITFMATCH-26JUL11WEIGHA-WEI | ITF_M | leader | 70 | 67 | +3 (place_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 12:10 | ITFMATCH-26JUL11WEIGHA-GHA | ITF_M | underdog | 27 | 23 | +4 (place_cell) | — | pre | pair | 97 | EARNED |
| 12:15 | ITFMATCH-26JUL11JOHKLA-KLA | ITF_M | underdog | 26 | 21 | +5 (place_cell) | — | pre | pair | 97 | MIXED |
| 12:15 | ITFMATCH-26JUL11BERBEN-BER | ITF_M | underdog | 10 | 9 | +1 (place_cell) | — | pre | pair | 96 | MIXED |
| 12:20 | ITFMATCH-26JUL11BAXLOK-BAX | ITF_M | underdog | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 12:24 | ATPMATCH-26JUL11PRAMAJ-MAJ | ATP_MAIN | underdog | 15 | 13 | +2 (place_cell) | -3.5 | pre | single |  | EARNED |
| 12:29 | ATPMATCH-26JUL11NEUPOL-POL | ATP_MAIN | underdog | 30 | 27 | +3 (place_cell) | 25.0 | pre | pair | 97 | GIFT_CLASS |
| 12:31 | ATPMATCH-26JUL11NEUPOL-NEU | ATP_MAIN | leader | 67 | 70 | -3 (place_cell) | -28.0 | pre | pair | 97 | EARNED |
| 12:52 | ITFWMATCH-26JUL11MIRMAL-MIR | ITF_W | leader | 87 | 83 | +4 (place_cell) | — | pre | pair | 99 | MIXED |
| 13:02 | ATPCHALLENGERMATCH-26JUL11MEJVAR-V | ATP_CHALL | underdog | 34 | 31 | +3 (place_cell) | 12.0 | pre | single |  | GIFT_CLASS |
| 13:07 | ITFMATCH-26JUL11SYDGON-SYD | ITF_M | leader | 94 | 90 | +4 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 13:08 | ITFWMATCH-26JUL11MIRMAL-MAL | ITF_W | ? | 12 | 10 | +2 (place_cell) | — | pre | pair | 99 | MIXED |
| 13:16 | ITFMATCH-26JUL11JOHKLA-JOH | ITF_M | leader | 71 | 70 | +1 (place_cell) | — | pre | pair | 97 | MIXED |
| 13:22 | WTAMATCH-26JUL11MORSZI-MOR | WTA_MAIN | leader | 75 | 77 | -2 (place_cell) | -11.5 | pre | pair | 97 | EARNED |
| 13:43 | ITFMATCH-26JUL11BECANG-BEC | ITF_M | underdog | 75 | 91 | -16 (place_cell) | 2.5 | pre | pair | 97 | EARNED |
| 13:49 | ITFMATCH-26JUL11BECANG-ANG | ITF_M | underdog | 22 | 1 | +21 (place_cell) | -5.0 | 3.5 | pair | 97 | EARNED |
| 14:01 | ITFWMATCH-26JUL11SHCCHA-CHA | ITF_W | ? | 19 | 14 | +5 (place_cell) | — | pre | single |  | EARNED |
| 19:37 | ITFMATCH-26JUL11JASMAT-JAS | ITF_M | leader | 64 | 62 | +2 (place_cell) | — | pre | pair | 97 | MIXED |
| 22:05 | ITFMATCH-26JUL11JASMAT-MAT | ITF_M | ? | 33 | 11 | +22 (window_cell) | — | pre | pair | 97 | MIXED |
| 01:15 | ITFMATCH-26JUL12MILARZ-ARZ | ITF_M | underdog | 27 | 23 | +4 (place_cell) | — | pre | single |  | PENDING |
| 01:19 | ATPCHALLENGERMATCH-26JUL12ALVVAN-V | ATP_CHALL | underdog | 22 | 19 | +3 (place_cell) | — | pre | single |  | MIXED |
| 02:00 | ITFMATCH-26JUL12MONSHI-MON | ITF_M | leader | 85 | 80 | +5 (place_cell) | — | pre | single |  | PENDING |
| 02:16 | ATPCHALLENGERMATCH-26JUL12DELMAK-D | ATP_CHALL | underdog | 8 | 5 | +3 (place_cell) | — | pre | single |  | PENDING |
| 02:31 | ITFWMATCH-26JUL12CORBRU-BRU | ITF_W | leader | 65 | 74 | -9 (place_cell) | — | pre | pair | 97 | PENDING |
| 02:36 | ATPCHALLENGERMATCH-26JUL12GANJAN-G | ATP_CHALL | ? | 20 | 15 | +5 (place_cell) | — | pre | pair | 97 | MIXED |
| 02:43 | ITFWMATCH-26JUL12CORBRU-COR | ITF_W | underdog | 32 | 45 | -13 (place_cell) | — | pre | pair | 97 | PENDING |
| 03:01 | WTAMATCH-26JUL12GARPRI-GAR | WTA_MAIN | ? | 39 | 37 | +2 (place_cell) | — | pre | single |  | MIXED |
| 03:05 | WTAMATCH-26JUL12KULZAA-ZAA | WTA_MAIN | leader | 67 | 68 | -1 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 03:23 | ITFWMATCH-26JUL12TOMKAR-KAR | ITF_W | leader | 54 | 54 | +0 (place_cell) | — | pre | single |  | PENDING |
| 04:07 | ATPCHALLENGERMATCH-26JUL12VILRAH-V | ATP_CHALL | leader | 68 | 65 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 04:20 | ATPCHALLENGERMATCH-26JUL12GANJAN-J | ATP_CHALL | leader | 77 | 73 | +4 (place_cell) | — | pre | pair | 97 | MIXED |
| 04:23 | ITFWMATCH-26JUL12LIUPUS-LIU | ITF_W | underdog | 22 | 11 | +11 (place_cell) | — | pre | single |  | PENDING |
| 04:23 | ITFMATCH-26JUL12LOPLAG-LOP | ITF_M | leader | 62 | 60 | +2 (place_cell) | — | pre | single |  | PENDING |
| 04:28 | ITFWMATCH-26JUL12GUPFER-GUP | ITF_W | underdog | 18 | 42 | -24 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 73 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 4, 'FLOW_ABOVE': 35, 'NO_FLOW': 34} | repriceable now: true 29 / false 44 | **cumulative bid_grade lines: 8350 (repriceable true 1210 / false 7140)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL11SEABAS-S | 75 | 1223m | 344/72-99/86610 | 98-99 | -3 | **FLOW_AT_LEVEL** | 75 |  |
| ATPCHALLENGERMATCH-26JUL12ALVVAN-A | 73 | 208m | 4/78-79/20 | 75-77 | 5 | **FLOW_ABOVE** | 75 | flow above but bound 75c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL12BALPET-B | 12 | 184m | 0 | 12-14 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL12BALPET-P | 85 | 187m | 5/85-88/59 | 85-87 | 0 | **FLOW_AT_LEVEL** | 84 |  |
| ATPCHALLENGERMATCH-26JUL12CHAJON-C | 41 | 88m | 1/43-43/42 | 41-43 | 2 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL12CHAJON-J | 56 | 88m | 2/59-59/400 | 57-57 | 3 | **FLOW_ABOVE** | 56 | flow above but bound 56c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL12CRIBAS-B | 64 | 178m | 3/64-66/10 | 64-65 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL12CRIBAS-C | 35 | 124m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL12DELMAK-M | 89 | 132m | 0 | 92-93 | — | **NO_FLOW** | 89 |  |
| ATPCHALLENGERMATCH-26JUL12GUTCAM-G | 31 | 19m | 0 | 31-33 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL12KRALOR-K | 94 | 88m | 0 | 94-95 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL12KUZDE-DE | 15 | 28m | 0 | 15-18 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL12PIETAB-P | 65 | 88m | 1/66-66/16 | 66-66 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ATPCHALLENGERMATCH-26JUL12PIETAB-T | 32 | 88m | 1/33-33/3 | 32-33 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| ATPCHALLENGERMATCH-26JUL12POLVIN-P | 38 | 88m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL12POLVIN-V | 59 | 88m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL12RAQKUM-K | 52 | 208m | 8/54-57/361 | 53-54 | 2 | **FLOW_ABOVE** | 52 | flow above but bound 52c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL12RAQKUM-R | 43 | 174m | 0 | 45-46 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL12YEVBOR-B | 5 | 28m | 0 | 5-7 | — | **NO_FLOW** | 4 |  |
| ATPCHALLENGERMATCH-26JUL12YEVBOR-Y | 93 | 28m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12ALTGAS-ALT | 57 | 191m | 1/58-58/36 | 57-59 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→58 |
| ATPMATCH-26JUL12ALTGAS-GAS | 42 | 202m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12CORDAN-COR | 29 | 58m | 0 | 29-30 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12DEJGAU-GAU | 32 | 168m | 1/33-33/1 | 32-34 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| ATPMATCH-26JUL12FARWAW-FAR | 63 | 304m | 8/64-67/1332 | 67-64 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ATPMATCH-26JUL12MOLFAU-FAU | 33 | 58m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12OFNTIR-OFN | 42 | 242m | 2/44-44/64 | 42-43 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ATPMATCH-26JUL12OFNTIR-TIR | 56 | 184m | 0 | 57-58 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12PASKAS-KAS | 48 | 73m | 3/49-50/1054 | 48-49 | 1 | **FLOW_ABOVE** | 50 | REPRICEABLE→49 |
| ATPMATCH-26JUL12SONSCH-SCH | 32 | 271m | 0 | 35-35 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12SVRDIM-SVR | 34 | 88m | 0 | 34-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL12BORNOR-BOR | 65 | 87m | 1/67-67/217 | 66-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFMATCH-26JUL12BORNOR-NOR | 33 | 148m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL12DONWIS-WIS | 49 | 88m | 1/51-51/94 | 49-51 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| ITFMATCH-26JUL12DURDOU-DOU | 72 | 103m | 4/74-74/157 | 72-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| ITFMATCH-26JUL12DURDOU-DUR | 27 | 5m | 0 | 27-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL12MONSHI-SHI | 12 | 148m | 21/14-18/506 | 15-15 | 2 | **FLOW_ABOVE** | 12 | flow above but bound 12c < flow -- chasing breaks goal |
| ITFMATCH-26JUL12PAPSNI-PAP | 27 | 88m | 1/31-31/8 | 27-30 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→31 |
| ITFMATCH-26JUL12PAPSNI-SNI | 70 | 61m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL12REYBAR-BAR | 6 | 21m | 0 | 52-95 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL12WESJUA-JUA | 53 | 145m | 1/54-54/89 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL12WESJUA-WES | 45 | 148m | 0 | 45-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL12GUPFER-FER | 72 | 0m | 0 | 72-81 | — | **NO_FLOW** | 79 |  |
| ITFWMATCH-26JUL12LEEGAO-GAO | 46 | 27m | 0 | 46-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL12LEYHOS-HOS | 46 | 238m | 2/50-50/38 | 46-49 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL12LEYHOS-LEY | 52 | 73m | 1/54-54/5 | 52-53 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFWMATCH-26JUL12LIUPUS-PUS | 73 | 2m | 0 | 74-78 | — | **NO_FLOW** | 75 |  |
| ITFWMATCH-26JUL12ROJPER-PER | 56 | 196m | 2/60-60/1 | 56-59 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL12ROJPER-ROJ | 41 | 196m | 2/44-44/119 | 41-43 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ITFWMATCH-26JUL12RYSHRU-HRU | 58 | 61m | 9/59-60/519 | 59-59 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFWMATCH-26JUL12RYSHRU-RYS | 40 | 101m | 4/43-44/1532 | 40-43 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFWMATCH-26JUL12SOBGOR-GOR | 29 | 88m | 0 | 29-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL12SOBGOR-SOB | 66 | 87m | 1/70-70/6 | 66-70 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→70 |
| ITFWMATCH-26JUL12VEDBOS-BOS | 34 | 58m | 0 | 34-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL12VEDBOS-VED | 62 | 53m | 0 | 62-64 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL12ARIZHA-Z | 63 | 203m | 1/65-65/307 | 63-65 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| WTACHALLENGERMATCH-26JUL12BOSKOV-B | 93 | 191m | 0 | 94-95 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL12CIRHUA-C | 6 | 58m | 0 | 6-7 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL12FEICHE-C | 24 | 118m | 5/25-26/367 | 24-26 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→25 |
| WTACHALLENGERMATCH-26JUL12FEICHE-F | 74 | 118m | 2/76-76/25 | 74-76 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| WTACHALLENGERMATCH-26JUL12PALCOL-C | 21 | 87m | 0 | 21-24 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL12PALCOL-P | 76 | 118m | 0 | 76-79 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL12PANYOR-P | 83 | 58m | 1/85-85/22 | 84-84 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| WTACHALLENGERMATCH-26JUL12PANYOR-Y | 15 | 3m | 4/16-17/144 | 16-16 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→16 |
| WTACHALLENGERMATCH-26JUL12SHITUR-S | 82 | 148m | 4/84-85/37 | 82-83 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→84 |
| WTACHALLENGERMATCH-26JUL12SHITUR-T | 16 | 132m | 3/18-18/525 | 16-18 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| WTACHALLENGERMATCH-26JUL12ZELFAL-F | 78 | 58m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL12ZELFAL-Z | 20 | 58m | 1/21-21/451 | 20-21 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| WTAMATCH-26JUL12AVASEI-AVA | 88 | 148m | 2/89-89/6 | 88-89 | 1 | **FLOW_ABOVE** | 89 | REPRICEABLE→89 |
| WTAMATCH-26JUL12AVASEI-SEI | 11 | 148m | 4/11-11/281 | 11-12 | 0 | **FLOW_AT_LEVEL** | 9 |  |
| WTAMATCH-26JUL12HERKAZ-KAZ | 46 | 149m | 23/47-47/4736 | 46-47 | 1 | **FLOW_ABOVE** | 44 | flow above but bound 44c < flow -- chasing breaks goal |
| WTAMATCH-26JUL12LIUPOP-POP | 13 | 58m | 0 | 13-14 | — | **NO_FLOW** | 12 |  |
| WTAMATCH-26JUL12WERAMA-WER | 78 | 178m | 21/80-83/639 | 81-79 | 2 | **FLOW_ABOVE** | 81 | REPRICEABLE→80 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL11KUBRYS | 33 | 1 | **34** | 97 | -63 |
| ATPCHALLENGERMATCH-26JUL11WALMIC | 33 | 1 | **34** | 97 | -63 |
| ITFMATCH-26JUL11MIYLEG | 41 | 1 | **42** | 97 | -55 |
| ATPCHALLENGERMATCH-26JUL11GALFEA | 30 | 14 | **44** | 97 | -53 |
| ITFWMATCH-26JUL11FONROJ | 44 | 1 | **45** | 97 | -52 |
| WTAMATCH-26JUL12GARPRI | 39 | 10 | **49** | 97 | -48 |
| ATPMATCH-26JUL11MICHEM | 49 | 1 | **50** | 97 | -47 |
| ITFMATCH-26JUL11TALPAP | 58 | 1 | **59** | 97 | -38 |
| ATPMATCH-26JUL11MONHER | 59 | 1 | **60** | 97 | -37 |
| ATPCHALLENGERMATCH-26JUL11PIRKYM | 59 | 1 | **60** | 97 | -37 |
| ITFWMATCH-26JUL11SMILEY | 61 | 1 | **62** | 97 | -35 |
| ITFWMATCH-26JUL11SHIGAO | 61 | 1 | **62** | 97 | -35 |
| ITFMATCH-26JUL11NORKOI | 62 | 1 | **63** | 97 | -34 |
| ITFWMATCH-26JUL11HOSCIR | 64 | 1 | **65** | 97 | -32 |
| ITFWMATCH-26JUL11SOBAVD | 60 | 6 | **66** | 97 | -31 |
| ITFMATCH-26JUL11LAGRIV | 69 | 1 | **70** | 97 | -27 |
| ITFMATCH-26JUL11FABARZ | 71 | 1 | **72** | 97 | -25 |
| ATPMATCH-26JUL11VUKOLI | 70 | 3 | **73** | 97 | -24 |
| ITFWMATCH-26JUL11SHCCHA | 19 | 55 | **74** | 97 | -23 |
| ITFMATCH-26JUL11SNIMAZ | 75 | 1 | **76** | 97 | -21 |
| ITFMATCH-26JUL11YOUKIM | 48 | 33 | **81** | 97 | -16 |
| ITFMATCH-26JUL11ROHBOR | 53 | 29 | **82** | 97 | -15 |
| ITFMATCH-26JUL11SVAZHU | 85 | 1 | **86** | 97 | -11 |
| ATPCHALLENGERMATCH-26JUL11MEJVAR | 34 | 53 | **87** | 97 | -10 |
| ITFMATCH-26JUL11SHIROB | 68 | 20 | **88** | 97 | -9 |
| ATPMATCH-26JUL11CINZAH | 87 | 1 | **88** | 97 | -9 |
| WTAMATCH-26JUL11ASLSIE | 89 | 1 | **90** | 97 | -7 |
| WTAMATCH-26JUL12KULZAA | 67 | 24 | **91** | 97 | -6 |
| ITFWMATCH-26JUL11LEEJOR | 43 | 49 | **92** | 97 | -5 |
| WTAMATCH-26JUL11HODCHA | 91 | 3 | **94** | 97 | -3 |
| ATPCHALLENGERMATCH-26JUL12VILRAH | 68 | 26 | **94** | 97 | -3 |
| WTAMATCH-26JUL11TSEMAN | 94 | 1 | **95** | 97 | -2 |
| ITFMATCH-26JUL11SYDGON | 94 | 1 | **95** | 97 | -2 |
| ATPMATCH-26JUL11HUEBUT | 51 | 46 | **97** | 97 | +0 |
| ATPCHALLENGERMATCH-26JUL12ALVVAN | 22 | 77 | **99** | 97 | +2 |
| ITFWMATCH-26JUL12GUPFER | 18 | 81 | **99** | 97 | +2 |
| ITFMATCH-26JUL12MONSHI | 85 | 15 | **100** | 97 | +3 |
| ITFWMATCH-26JUL12LIUPUS | 22 | 78 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL12DELMAK | 8 | 93 | **101** | 97 | +4 |
| ATPMATCH-26JUL11PRAMAJ | 15 | 89 | **104** | 97 | +7 |
| ATPMATCH-26JUL11SKACHA | 6 | 99 | **105** | 97 | +8 |
| WTAMATCH-26JUL11PANKUL | 9 | 99 | **108** | 97 | +11 |
| ITFWMATCH-26JUL11SHEYAM | 53 | 57 | **110** | 97 | +13 |
| WTAMATCH-26JUL11RENTON | 12 | 99 | **111** | 97 | +14 |
| ITFWMATCH-26JUL11BOSKAR | 39 | 73 | **112** | 97 | +15 |
| ATPCHALLENGERMATCH-26JUL11BERDEL | 30 | 82 | **112** | 97 | +15 |
| ATPMATCH-26JUL11BRAGOM | 54 | 58 | **112** | 97 | +15 |
| WTAMATCH-26JUL11MICNIN | 16 | 99 | **115** | 97 | +18 |
| ATPCHALLENGERMATCH-26JUL11SEABAS | 22 | 99 | **121** | 97 | +24 |
| ITFWMATCH-26JUL11MAKSHO | 50 | 73 | **123** | 97 | +26 |
| ITFWMATCH-26JUL11KARSUP | 40 | 83 | **123** | 97 | +26 |
| ITFMATCH-26JUL11CIGZAR | 26 | 99 | **125** | 97 | +28 |
| ATPCHALLENGERMATCH-26JUL11SOTCLA | 35 | 90 | **125** | 97 | +28 |
| ATPCHALLENGERMATCH-26JUL11RINCHO | 32 | 99 | **131** | 97 | +34 |
| ITFMATCH-26JUL11DURBAR | 39 | 94 | **133** | 97 | +36 |
| ATPMATCH-26JUL11DHASAC | 35 | 99 | **134** | 97 | +37 |
| ATPCHALLENGERMATCH-26JUL11GIUDAM | 39 | 99 | **138** | 97 | +41 |
| ITFWMATCH-26JUL11HOSDAA | 42 | 98 | **140** | 97 | +43 |
| ATPMATCH-26JUL11VIRDIE | 65 | 79 | **144** | 97 | +47 |
| WTACHALLENGERMATCH-26JUL11MINVOL | 47 | 97 | **144** | 97 | +47 |
| ATPMATCH-26JUL11NARGUE | 57 | 90 | **147** | 97 | +50 |
| ATPMATCH-26JUL11TOPMAR | 62 | 99 | **161** | 97 | +64 |
| ITFMATCH-26JUL11KELWES | 63 | 98 | **161** | 97 | +64 |
| ITFMATCH-26JUL11NICJUA | 73 | 90 | **163** | 97 | +66 |
| ITFWMATCH-26JUL11FULSOU | 77 | 94 | **171** | 97 | +74 |

## FLOW-STATE — 144 tracked game(s) ({'QUIET': 72, 'WAKING': 70, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL12LOPLAG | ITF_M | 0.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL12RYSHRU | ITF_W | 0.333 | 3 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL11BERDEL | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL11CHIGRA | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL11DIAGAS | ATP_CHALL | 0.0 | 8 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL11GALFEA | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL11MEJVAR | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL11PIRKYM | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL11RINCHO | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL11SOTCLA | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL11WALMIC | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPMATCH-26JUL11BRAGOM | ATP_MAIN | 0.0 | — | **QUIET** |
| ATPMATCH-26JUL11HUEBUT | ATP_MAIN | 0.0 | — | **QUIET** |
| ATPMATCH-26JUL11MICHEM | ATP_MAIN | 0.0 | — | **QUIET** |
| ATPMATCH-26JUL11MONHER | ATP_MAIN | 0.0 | — | **QUIET** |
| ATPMATCH-26JUL11NEUPOL | ATP_MAIN | 0.0 | — | **QUIET** |
| ATPMATCH-26JUL11PRAMAJ | ATP_MAIN | 0.0 | — | **QUIET** |
| ATPMATCH-26JUL11TOPMAR | ATP_MAIN | 0.0 | — | **QUIET** |
| ATPMATCH-26JUL11VIRDIE | ATP_MAIN | 0.0 | — | **QUIET** |
| ATPMATCH-26JUL11VUKOLI | ATP_MAIN | 0.0 | — | **QUIET** |
| ATPMATCH-26JUL12FARWAW | ATP_MAIN | 0.0 | — | **QUIET** |
| ATPMATCH-26JUL12SONSCH | ATP_MAIN | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11BECANG | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11CIGZAR | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11DOUROB | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11DURBAR | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11FABARZ | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11JASMAT | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11JOHKLA | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11KELWES | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11LAGRIV | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11MCIALF | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11MIYLEG | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11NICJUA | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11NORKOI | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11RECWIS | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11ROHBOR | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11SHIROB | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11SNIMAZ | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11SVAZHU | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11TALPAP | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11WEIGHA | ITF_M | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL11YOUKIM | ITF_M | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11BOSKAR | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11DENSTR | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11ERCHRU | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11FONROJ | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11FULSOU | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11GORKOS | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11HOSCIR | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11KALTIK | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11KARSUP | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11KOVVED | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11KUBRYS | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11LEEJOR | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11MAKSHO | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11MIRMAL | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11PERWIE | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11SAGYOD | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11SHCCHA | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11SHEYAM | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11SHIGAO | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11SMILEY | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11SOBAVD | ITF_W | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL11STATOM | ITF_W | 0.0 | — | **QUIET** |
| WTACHALLENGERMATCH-26JUL11MINVOL | WTA_CHALL | 0.0 | — | **QUIET** |
| WTACHALLENGERMATCH-26JUL11WALBAD | WTA_CHALL | 0.0 | — | **QUIET** |
| WTAMATCH-26JUL11ASLSIE | WTA_MAIN | 0.0 | — | **QUIET** |
| WTAMATCH-26JUL11HODCHA | WTA_MAIN | 0.0 | — | **QUIET** |
| WTAMATCH-26JUL11MORSZI | WTA_MAIN | 0.0 | — | **QUIET** |
| WTAMATCH-26JUL11RENTON | WTA_MAIN | 0.0 | — | **QUIET** |
| WTAMATCH-26JUL11TANNEP | WTA_MAIN | 0.0 | — | **QUIET** |
| WTAMATCH-26JUL11TSEMAN | WTA_MAIN | 0.0 | — | **QUIET** |
| WTAMATCH-26JUL11YASGLU | WTA_MAIN | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL11GIUDAM | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL11SEABAS | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12ALVVAN | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12BALPET | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12CHAJON | ATP_CHALL | 0.067 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12CRIBAS | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12DELMAK | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12GANJAN | ATP_CHALL | 5.1 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12GUTCAM | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12KRALOR | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12KUZDE | ATP_CHALL | 0.0 | 3 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12PIETAB | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12POLVIN | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12RAQKUM | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12VILRAH | ATP_CHALL | 1.867 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL12YEVBOR | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPMATCH-26JUL11CECAJD | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL11CINZAH | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL11DHASAC | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL11NARGUE | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL11SKACHA | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL12CORDAN | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL12DEJGAU | ATP_MAIN | 0.0 | 2 | **WAKING** |
| ATPMATCH-26JUL12MOLFAU | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL12OFNTIR | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL12PASKAS | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ATPMATCH-26JUL12SVRDIM | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11BAXLOK | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11BERBEN | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11ERECRA | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11FRAMAR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11SAMLOP | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL11SYDGON | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL12BORNOR | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL12DONWIS | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL12DURDOU | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL12MILARZ | ITF_M | 1.8 | — | **WAKING** |
| ITFMATCH-26JUL12MONSHI | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL12PAPSNI | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL12REYBAR | ITF_M | 0.033 | 43 | **WAKING** |
| ITFMATCH-26JUL12WESJUA | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL11BABGER | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL11HOSDAA | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL11MARPAR | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL12CORBRU | ITF_W | 64.333 | — | **WAKING** |
| ITFWMATCH-26JUL12GUPFER | ITF_W | 0.233 | 9 | **WAKING** |
| ITFWMATCH-26JUL12LEEGAO | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL12LEYHOS | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL12LIUPUS | ITF_W | 0.433 | 4 | **WAKING** |
| ITFWMATCH-26JUL12ROJPER | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL12SOBGOR | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL12TOMKAR | ITF_W | 4.133 | — | **WAKING** |
| ITFWMATCH-26JUL12VEDBOS | ITF_W | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL12ARIZHA | WTA_CHALL | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL12BOSKOV | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL12CIRHUA | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL12FEICHE | WTA_CHALL | 0.167 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL12PALCOL | WTA_CHALL | 0.0 | 3 | **WAKING** |
| WTACHALLENGERMATCH-26JUL12PANYOR | WTA_CHALL | 0.3 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL12SHITUR | WTA_CHALL | 0.1 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL12ZELFAL | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL11MICNIN | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL11PANKUL | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL12AVASEI | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL12GARPRI | WTA_MAIN | 14.333 | — | **WAKING** |
| WTAMATCH-26JUL12HERKAZ | WTA_MAIN | 0.367 | 1 | **WAKING** |
| WTAMATCH-26JUL12KULZAA | WTA_MAIN | 14.3 | — | **WAKING** |
| WTAMATCH-26JUL12LIUPOP | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL12WERAMA | WTA_MAIN | 0.233 | — | **WAKING** |

## PATTERNS (sub-B) — 161
- pre_conception_buy: KXITFMATCH-26JUL11SHIROB-SHI {"price": 31, "conception_ts": 1783762200.9655762, "detail": "buy 31c predates the conception stamp by 291min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11HOSCIR-CIR {"price": 33, "conception_ts": 1783762200.071836, "detail": "buy 33c predates the conception stamp by 291min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11SMILEY-SMI {"price": 38, "conception_ts": 1783762218.6075966, "detail": "buy 38c predates the conception stamp by 291min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11KUBRYS-KUB {"price": 66, "conception_ts": 1783762248.9930575, "detail": "buy 66c predates the conception stamp by 292min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11SHEYAM-YAM {"price": 52, "conception_ts": 1783764001.9625702, "detail": "buy 52c predates the conception stamp by 321min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11STATOM-STA {"price": 62, "conception_ts": 1783764058.815446, "detail": "buy 62c predates the conception stamp by 322min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL11SHIROB-SHI {"price": 30, "conception_ts": 1783762200.9655762, "detail": "buy 30c predates the conception stamp by 289min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11STATOM-STA {"price": 62, "conception_ts": 1783764058.815446, "detail": "buy 62c predates the conception stamp by 320min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11HOSCIR-CIR {"price": 33, "conception_ts": 1783762200.071836, "detail": "buy 33c predates the conception stamp by 289min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11SMILEY-SMI {"price": 38, "conception_ts": 1783762218.6075966, "detail": "buy 38c predates the conception stamp by 289min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11KUBRYS-KUB {"price": 66, "conception_ts": 1783762248.9930575, "detail": "buy 66c predates the conception stamp by 290min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL11SHIROB-SHI {"price": 31, "conception_ts": 1783762200.9655762, "detail": "buy 31c predates the conception stamp by 287min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL11DURBAR-BAR {"price": 38, "conception_ts": 1783765834.1028724, "detail": "buy 38c predates the conception stamp by 340min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL11DURBAR-BAR {"price": 39, "conception_ts": 1783765834.1028724, "detail": "buy 39c predates the conception stamp by 339min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11KARSUP-SUP {"price": 40, "conception_ts": 1783764058.7665915, "detail": "buy 40c predates the conception stamp by 306min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL11MAKSHO-SHO {"fill": 50, "age_min": 1648, "mode": "PAIRING(sib never rested)"}
- pre_conception_buy: KXITFMATCH-26JUL11TALPAP-TAL {"price": 44, "conception_ts": 1783767614.1347365, "detail": "buy 44c predates the conception stamp by 359min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFMATCH-26JUL11LAGRIV-LAG {"fill": 69, "age_min": 1647, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFWMATCH-26JUL11SHEYAM-YAM {"price": 52, "conception_ts": 1783764001.9625702, "detail": "buy 52c predates the conception stamp by 291min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL11ERCHRU-HRU {"fill": 82, "age_min": 1624, "mode": "PAIRING(sib never rested)"}
- pre_conception_buy: KXITFMATCH-26JUL11SNIMAZ-SNI {"price": 73, "conception_ts": 1783767621.4914367, "detail": "buy 73c predates the conception stamp by 332min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL11SNIMAZ-SNI {"price": 74, "conception_ts": 1783767621.4914367, "detail": "buy 74c predates the conception stamp by 330min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL11MILARS-ARS {"price": 19, "conception_ts": 1783769404.7842388, "detail": "buy 19c predates the conception stamp by 359min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11FONROJ-FON {"price": 54, "conception_ts": 1783765834.1442504, "detail": "buy 54c predates the conception stamp by 300min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL11SNIMAZ-SNI {"price": 75, "conception_ts": 1783767621.4914367, "detail": "buy 75c predates the conception stamp by 325min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL11FABARZ-FAB {"price": 28, "conception_ts": 1783769434.9547288, "detail": "buy 28c predates the conception stamp by 352min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFMATCH-26JUL11SNIMAZ-SNI {"fill": 75, "age_min": 1602, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFMATCH-26JUL11SHIROB-SHI {"price": 32, "conception_ts": 1783762200.9655762, "detail": "buy 32c predates the conception stamp by 220min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFMATCH-26JUL11SHIROB-ROB {"fill": 68, "age_min": 1599, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFMATCH-26JUL11NORKOI-KOI {"price": 36, "conception_ts": 1783771219.5736032, "detail": "buy 36c predates the conception stamp by 359min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11BOSKAR-BOS {"price": 59, "conception_ts": 1783771200.9869418, "detail": "buy 59c predates the conception stamp by 359min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11KALTIK-TIK {"price": 60, "conception_ts": 1783764006.5823317, "detail": "buy 60c predates the conception stamp by 235min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11KALTIK-TIK {"price": 61, "conception_ts": 1783764006.5823317, "detail": "buy 61c predates the conception stamp by 235min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXATPMATCH-26JUL11HUEBUT-BUT {"fill": 51, "age_min": 1580, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFWMATCH-26JUL11KALTIK-TIK {"price": 62, "conception_ts": 1783764006.5823317, "detail": "buy 62c predates the conception stamp by 226min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11KALTIK-TIK {"price": 63, "conception_ts": 1783764006.5823317, "detail": "buy 63c predates the conception stamp by 209min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11LEEJOR-JOR {"price": 43, "conception_ts": 1783771227.1400104, "detail": "buy 43c predates the conception stamp by 329min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11HOSCIR-CIR {"price": 35, "conception_ts": 1783762200.071836, "detail": "buy 35c predates the conception stamp by 178min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11BOSKAR-BOS {"price": 60, "conception_ts": 1783771200.9869418, "detail": "buy 60c predates the conception stamp by 320min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXATPMATCH-26JUL11MONHER-MON {"fill": 59, "age_min": 1542, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFWMATCH-26JUL11SHEYAM-YAM {"price": 53, "conception_ts": 1783764001.9625702, "detail": "buy 53c predates the conception stamp by 171min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL11SHEYAM-YAM {"fill": 53, "age_min": 1505, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL11HOSCIR-HOS {"fill": 64, "age_min": 1496, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL11SMILEY-LEY {"fill": 61, "age_min": 1493, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL11KUBRYS-RYS {"fill": 33, "age_min": 1486, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL11PERWIE-WIE {"fill": 18, "age_min": 1475, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL11DENSTR-DEN {"fill": 51, "age_min": 1466, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPMATCH-26JUL11VIRDIE-VIR {"fill": 65, "age_min": 1463, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL11KARSUP-SUP {"fill": 40, "age_min": 1462, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL11DURBAR-BAR {"fill": 39, "age_min": 1436, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL11FONROJ-ROJ {"fill": 44, "age_min": 1432, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL11TALPAP-PAP {"fill": 58, "age_min": 1423, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXITFWMATCH-26JUL11STATOM-STA {"kind": "position_basis", "ref": 62.0, "market_mid": 36.0, "divergence": 26.0}
- half_arm_aging: KXATPMATCH-26JUL11DHASAC-DHA {"fill": 35, "age_min": 1418, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPMATCH-26JUL11MICHEM-HEM {"fill": 49, "age_min": 1409, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFMATCH-26JUL11KELWES-KEL {"price": 63, "conception_ts": 1783782002.6228535, "detail": "buy 63c predates the conception stamp by 359min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11SOBAVD-AVD {"price": 37, "conception_ts": 1783782001.028226, "detail": "buy 37c predates the conception stamp by 359min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL11RINCHO-RIN {"fill": 32, "age_min": 1401, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXITFWMATCH-26JUL11STATOM-STA {"kind": "position_basis", "ref": 62.0, "market_mid": 32.0, "divergence": 30.0}
- half_arm_aging: KXITFMATCH-26JUL11ROHBOR-ROH {"fill": 53, "age_min": 1377, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTAMATCH-26JUL11ASLSIE-SIE {"fill": 89, "age_min": 1375, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFWMATCH-26JUL11SOBAVD-AVD {"price": 38, "conception_ts": 1783782001.028226, "detail": "buy 38c predates the conception stamp by 325min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFMATCH-26JUL11FABARZ-ARZ {"fill": 71, "age_min": 1365, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXITFWMATCH-26JUL11KARSUP-SUP {"kind": "position_basis", "ref": 40.0, "market_mid": 3.5, "divergence": 36.5}
- half_arm_aging: KXATPMATCH-26JUL11CINZAH-CIN {"fill": 87, "age_min": 1350, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL11BOSKAR-KAR {"fill": 39, "age_min": 1350, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFWMATCH-26JUL11MARPAR-MAR {"price": 51, "conception_ts": 1783785600.50721, "detail": "buy 51c predates the conception stamp by 358min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11SOBAVD-AVD {"price": 39, "conception_ts": 1783782001.028226, "detail": "buy 39c predates the conception stamp by 297min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL11LEEJOR-JOR {"fill": 43, "age_min": 1345, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXITFWMATCH-26JUL11SHEYAM-YAM {"kind": "position_basis", "ref": 53.0, "market_mid": 24.5, "divergence": 28.5}
- half_arm_aging: KXITFMATCH-26JUL11NORKOI-NOR {"fill": 62, "age_min": 1338, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPMATCH-26JUL11SKACHA-CHA {"fill": 6, "age_min": 1319, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL11CHIGRA-CHI {"entry_minus_fv_burst": -46.5}
- pre_conception_buy: KXITFWMATCH-26JUL11SOBAVD-AVD {"price": 40, "conception_ts": 1783782001.028226, "detail": "buy 40c predates the conception stamp by 263min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFMATCH-26JUL11NICJUA-NIC {"fill": 73, "age_min": 1309, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXATPMATCH-26JUL11VUKOLI-OLI {"price": 71, "conception_ts": 1783778446.5553095, "detail": "buy 71c predates the conception stamp by 180min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11FULSOU-FUL {"price": 75, "conception_ts": 1783789248.7720008, "detail": "buy 75c predates the conception stamp by 360min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11FULSOU-FUL {"price": 77, "conception_ts": 1783789248.7720008, "detail": "buy 77c predates the conception stamp by 352min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXITFWMATCH-26JUL11SHIGAO-GAO {"fill": 61, "age_min": 1275, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTAMATCH-26JUL11HODCHA-HOD {"fill": 91, "age_min": 1265, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFWMATCH-26JUL11GORKOS-KOS {"price": 73, "conception_ts": 1783791033.819245, "detail": "buy 73c predates the conception stamp by 361min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL11SVAZHU-ZHU {"price": 13, "conception_ts": 1783792885.4055567, "detail": "buy 13c predates the conception stamp by 361min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL11WEIGHA-WEI {"price": 70, "conception_ts": 1783792885.5350878, "detail": "buy 70c predates the conception stamp by 361min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXATPMATCH-26JUL11NARGUE-NAR {"fill": 57, "age_min": 1224, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL11SEABAS-BAS {"fill": 22, "age_min": 1223, "mode": "QUEUE(flow at/below our level, unfilled)"}
- half_arm_aging: KXITFWMATCH-26JUL11SOBAVD-SOB {"fill": 60, "age_min": 1216, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPMATCH-26JUL11TOPMAR-MAR {"fill": 62, "age_min": 1209, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPMATCH-26JUL11VUKOLI-OLI {"fill": 70, "age_min": 1208, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL11GIUDAM-DAM {"fill": 39, "age_min": 1208, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL11BERDEL-BER {"fill": 30, "age_min": 1207, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL11KELWES-KEL {"fill": 63, "age_min": 1205, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTAMATCH-26JUL11TSEMAN-MAN {"fill": 94, "age_min": 1177, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTAMATCH-26JUL11MICNIN-NIN {"fill": 16, "age_min": 1169, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFWMATCH-26JUL11MIRMAL-MAL {"price": 11, "conception_ts": 1783796433.7335737, "detail": "buy 11c predates the conception stamp by 360min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFMATCH-26JUL11JOHKLA-KLA {"price": 25, "conception_ts": 1783796433.7166665, "detail": "buy 25c predates the conception stamp by 360min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL11PIRKYM-PIR {"fill": 59, "age_min": 1162, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFMATCH-26JUL11SVAZHU-ZHU {"price": 14, "conception_ts": 1783792885.4055567, "detail": "buy 14c predates the conception stamp by 290min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- reality_divergence: KXATPMATCH-26JUL11VIRDIE-VIR {"kind": "position_basis", "ref": 65.0, "market_mid": 21.5, "divergence": 43.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL11DIAGAS-DIA {"entry_minus_fv_burst": -23.0}
- half_arm_aging: KXITFWMATCH-26JUL11HOSDAA-DAA {"fill": 42, "age_min": 1101, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFMATCH-26JUL11FRAMAR-MAR {"price": 61, "conception_ts": 1783785601.4098248, "detail": "buy 61c predates the conception stamp by 112min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- pre_conception_buy: KXITFWMATCH-26JUL11MIRMAL-MAL {"price": 12, "conception_ts": 1783796433.7335737, "detail": "buy 12c predates the conception stamp by 286min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- reality_divergence: KXATPMATCH-26JUL11VIRDIE-VIR {"kind": "position_basis", "ref": 65.0, "market_mid": 29.0, "divergence": 36.0}
- half_arm_aging: KXWTAMATCH-26JUL11RENTON-REN {"fill": 12, "age_min": 1080, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL11MINVOL-MIN {"fill": 47, "age_min": 1079, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFWMATCH-26JUL11SHCCHA-SHC {"price": 79, "conception_ts": 1783800000.7910926, "detail": "buy 79c predates the conception stamp by 330min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- reality_divergence: KXITFMATCH-26JUL11KELWES-KEL {"kind": "position_basis", "ref": 63.0, "market_mid": 22.0, "divergence": 41.0}
- reality_divergence: KXITFMATCH-26JUL11FRAMAR-FRA {"kind": "resting_bid", "ref": 36.0, "market_mid": 76.5, "divergence": -40.5}
- reality_divergence: KXITFMATCH-26JUL11FRAMAR-MAR {"kind": "position_basis", "ref": 61.0, "market_mid": 24.0, "divergence": 37.0}
- half_arm_aging: KXITFMATCH-26JUL11CIGZAR-CIG {"fill": 26, "age_min": 1053, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFWMATCH-26JUL11GORKOS-KOS {"price": 74, "conception_ts": 1783791033.819245, "detail": "buy 74c predates the conception stamp by 147min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- reality_divergence: KXITFMATCH-26JUL11KELWES-KEL {"kind": "position_basis", "ref": 63.0, "market_mid": 5.5, "divergence": 57.5}
- half_arm_aging: KXITFWMATCH-26JUL11FULSOU-FUL {"fill": 77, "age_min": 1037, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL11SOTCLA-CLA {"fill": 35, "age_min": 1035, "mode": "NO_BID(sib rested earlier, none now)"}
- pre_conception_buy: KXITFMATCH-26JUL11JOHKLA-KLA {"price": 26, "conception_ts": 1783796433.7166665, "detail": "buy 26c predates the conception stamp by 222min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- half_arm_aging: KXATPMATCH-26JUL11BRAGOM-BRA {"fill": 54, "age_min": 1030, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPMATCH-26JUL11CECAJD-AJD {"kind": "resting_bid", "ref": 23.0, "market_mid": 49.5, "divergence": -26.5}
- reality_divergence: KXITFMATCH-26JUL11FRAMAR-FRA {"kind": "resting_bid", "ref": 36.0, "market_mid": 64.0, "divergence": -28.0}
- reality_divergence: KXITFMATCH-26JUL11MCIALF-MCI {"kind": "position_basis", "ref": 80.0, "market_mid": 45.5, "divergence": 34.5}
- pre_conception_buy: KXITFWMATCH-26JUL11SHCCHA-SHC {"price": 80, "conception_ts": 1783800000.7910926, "detail": "buy 80c predates the conception stamp by 277min \u2014 honest-window buy, cap not yet defined (ungradeable)"}
- deep_neg_fv: KXITFMATCH-26JUL11MIYLEG-MIY {"entry_minus_fv_burst": -21.0}
- half_arm_aging: KXITFMATCH-26JUL11MIYLEG-MIY {"fill": 41, "age_min": 1024, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL11SVAZHU-SVA {"fill": 85, "age_min": 1021, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTAMATCH-26JUL11PANKUL-PAN {"fill": 9, "age_min": 1011, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL11WALMIC-WAL {"entry_minus_fv_burst": -23.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL11WALMIC-WAL {"fill": 33, "age_min": 999, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL11GALFEA-GAL {"fill": 30, "age_min": 999, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPMATCH-26JUL11NARGUE-NAR {"kind": "position_basis", "ref": 57.0, "market_mid": 30.5, "divergence": 26.5}
- reality_divergence: KXATPMATCH-26JUL11TOPMAR-MAR {"kind": "position_basis", "ref": 62.0, "market_mid": 35.5, "divergence": 26.5}
- deep_neg_fv: KXWTAMATCH-26JUL11TANNEP-TAN {"entry_minus_fv_burst": -40.0}
- half_arm_aging: KXITFMATCH-26JUL11ERECRA-CRA {"fill": 60, "age_min": 993, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL11YOUKIM-YOU {"fill": 48, "age_min": 984, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXITFMATCH-26JUL11FRAMAR-MAR {"kind": "position_basis", "ref": 61.0, "market_mid": 17.0, "divergence": 44.0}
- reality_divergence: KXITFWMATCH-26JUL11FULSOU-FUL {"kind": "position_basis", "ref": 77.0, "market_mid": 43.5, "divergence": 33.5}
- reality_divergence: KXITFMATCH-26JUL11ERECRA-CRA {"kind": "position_basis", "ref": 60.0, "market_mid": 20.5, "divergence": 39.5}
- reality_divergence: KXITFMATCH-26JUL11MCIALF-MCI {"kind": "position_basis", "ref": 80.0, "market_mid": 37.0, "divergence": 43.0}
- reality_divergence: KXITFMATCH-26JUL11YOUKIM-YOU {"kind": "position_basis", "ref": 48.0, "market_mid": 21.5, "divergence": 26.5}
- half_arm_aging: KXATPMATCH-26JUL11PRAMAJ-MAJ {"fill": 15, "age_min": 964, "mode": "NO_BID(sib rested earlier, none now)"}
- deep_neg_fv: KXATPMATCH-26JUL11NEUPOL-NEU {"entry_minus_fv_burst": -28.0}
- reality_divergence: KXATPMATCH-26JUL11NARGUE-NAR {"kind": "position_basis", "ref": 57.0, "market_mid": 17.5, "divergence": 39.5}
- reality_divergence: KXITFWMATCH-26JUL11FULSOU-FUL {"kind": "position_basis", "ref": 77.0, "market_mid": 5.0, "divergence": 72.0}
- reality_divergence: KXITFWMATCH-26JUL11GORKOS-KOS {"kind": "position_basis", "ref": 72.0, "market_mid": 44.5, "divergence": 27.5}
- reality_divergence: KXITFMATCH-26JUL11ERECRA-CRA {"kind": "position_basis", "ref": 60.0, "market_mid": 9.5, "divergence": 50.5}
- reality_divergence: KXITFMATCH-26JUL11WEIGHA-WEI {"kind": "position_basis", "ref": 70.0, "market_mid": 38.5, "divergence": 31.5}
- reality_divergence: KXITFMATCH-26JUL11YOUKIM-YOU {"kind": "position_basis", "ref": 48.0, "market_mid": 14.5, "divergence": 33.5}
- reality_divergence: KXWTAMATCH-26JUL11TANNEP-NEP {"kind": "position_basis", "ref": 62.0, "market_mid": 30.5, "divergence": 31.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL11MEJVAR-VAR {"fill": 34, "age_min": 926, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL11SYDGON-SYD {"fill": 94, "age_min": 921, "mode": "PAIRING(sib never rested)"}
- reality_divergence: KXITFMATCH-26JUL11BAXLOK-BAX {"kind": "position_basis", "ref": 37.0, "market_mid": 11.5, "divergence": 25.5}
- reality_divergence: KXITFWMATCH-26JUL11GORKOS-KOS {"kind": "position_basis", "ref": 72.0, "market_mid": 1.0, "divergence": 71.0}
- deep_neg_fv: KXWTAMATCH-26JUL11MORSZI-MOR {"entry_minus_fv_burst": -11.5}
- reality_divergence: KXATPMATCH-26JUL11NEUPOL-POL {"kind": "position_basis", "ref": 30.0, "market_mid": 3.5, "divergence": 26.5}
- half_arm_aging: KXITFWMATCH-26JUL11SHCCHA-CHA {"fill": 19, "age_min": 867, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL12MILARZ-ARZ {"fill": 27, "age_min": 193, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL12ALVVAN-VAN {"fill": 22, "age_min": 189, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFMATCH-26JUL12MONSHI-MON {"fill": 85, "age_min": 148, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL12DELMAK-DEL {"fill": 8, "age_min": 132, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXWTAMATCH-26JUL12GARPRI-GAR {"fill": 39, "age_min": 88, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTAMATCH-26JUL12KULZAA-ZAA {"fill": 67, "age_min": 83, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFWMATCH-26JUL12TOMKAR-KAR {"fill": 54, "age_min": 66, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXITFMATCH-26JUL12REYBAR-BAR {"kind": "resting_bid", "ref": 6.0, "market_mid": 73.0, "divergence": -67.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
