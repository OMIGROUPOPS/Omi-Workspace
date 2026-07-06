# LIVE VALIDATION — rolling status

- cycle 99 @ **2026-07-06 03:36:58 AM ET** | build `05f90f6` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 56936 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 01:01:56 | **combined_over_goal** | KXITFWMATCH-26JUL06TODSAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 01:12:30 | **combined_over_goal** | KXITFWMATCH-26JUL06VAJRAM | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 31 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:51 | ITFWMATCH-26JUL06PASCOP-PAS | ITF_W | underdog | 12 | 8 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:51 | ITFWMATCH-26JUL06LUCGAD-GAD | ITF_W | underdog | 37 | 33 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:52 | ITFWMATCH-26JUL06PASCOP-COP | ITF_W | leader | 85 | 83 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 23:59 | ITFWMATCH-26JUL06BRESAF-BRE | ITF_W | leader | 63 | 61 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:04 | ITFWMATCH-26JUL06SIMCIR-CIR | ITF_W | underdog | 16 | 12 | +4 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:04 | ITFWMATCH-26JUL06SACLAZ-LAZ | ITF_W | underdog | 19 | 11 | +8 (place_cell) | — | pre | single |  | PENDING |
| 00:05 | ITFWMATCH-26JUL06HOSFEH-FEH | ITF_W | underdog | 61 | 63 | -2 (place_cell) | — | pre | single |  | PENDING |
| 00:06 | ITFWMATCH-26JUL06VAJRAM-VAJ | ITF_W | leader | 82 | 74 | +8 (place_cell) | — | pre | pair | 101 | PENDING |
| 00:10 | ITFWMATCH-26JUL06LUCGAD-LUC | ITF_W | leader | 60 | 60 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:17 | ITFMATCH-26JUL06GENAZO-AZO | ITF_M | underdog | 16 | 9 | +7 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:22 | ITFMATCH-26JUL06VULCOU-COU | ITF_M | ? | 16 | 10 | +6 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:33 | ITFWMATCH-26JUL06WONIBR-IBR | ITF_W | leader | 65 | 52 | +13 (place_cell) | — | pre | single |  | PENDING |
| 00:33 | ITFWMATCH-26JUL06SIMCIR-SIM | ITF_W | leader | 81 | 81 | +0 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:34 | ITFWMATCH-26JUL06KARBAS-BAS | ITF_W | underdog | 26 | 26 | +0 (place_cell) | — | pre | single |  | PENDING |
| 00:47 | ITFWMATCH-26JUL06TODSAG-TOD | ITF_W | leader | 68 | 62 | +6 (place_cell) | — | pre | pair | 98 | PENDING |
| 00:55 | ITFWMATCH-26JUL06ZRNLUE-LUE | ITF_W | underdog | 69 | 6 | +63 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06VULCOU-VUL | ITF_M | leader | 81 | 80 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06BEASCO-SCO | ITF_M | underdog | 33 | 21 | +12 (place_cell) | — | pre | single |  | PENDING |
| 01:01 | ITFWMATCH-26JUL06TODSAG-SAG | ITF_W | ? | 30 | 25 | +5 (place_cell) | — | pre | pair | 98 | PENDING |
| 01:05 | ITFWMATCH-26JUL06BRESAF-SAF | ITF_W | underdog | 34 | 32 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:12 | ITFWMATCH-26JUL06VAJRAM-RAM | ITF_W | ? | 19 | 9 | +10 (place_cell) | — | pre | pair | 101 | PENDING |
| 01:22 | ITFWMATCH-26JUL06POPSOL-POP | ITF_W | underdog | 36 | 21 | +15 (place_cell) | — | pre | single |  | PENDING |
| 01:23 | ITFMATCH-26JUL06GENAZO-GEN | ITF_M | leader | 81 | 73 | +8 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:44 | ATPCHALLENGERMATCH-26JUL06VILBOC-V | ATP_CHALL | leader | 75 | 72 | +3 (place_cell) | — | pre | single |  | GIFT_CLASS |
| 01:51 | ATPCHALLENGERMATCH-26JUL06NIJRAH-R | ATP_CHALL | underdog | 40 | 37 | +3 (place_cell) | — | pre | single |  | PENDING |
| 02:21 | ITFWMATCH-26JUL06WAGYOU-YOU | ITF_W | leader | 63 | 49 | +14 (place_cell) | — | pre | single |  | PENDING |
| 03:05 | ITFWMATCH-26JUL06ZRNLUE-ZRN | ITF_W | ? | 28 | 2 | +26 (place_cell) | — | pre | pair | 97 | PENDING |
| 03:16 | ITFWMATCH-26JUL06BOIBOY-BOI | ITF_W | leader | 77 | 75 | +2 (place_cell) | — | pre | single |  | PENDING |
| 03:29 | ITFMATCH-26JUL06SALNGW-NGW | ITF_M | ? | 39 | 32 | +7 (place_cell) | — | pre | single |  | PENDING |
| 03:31 | ITFWMATCH-26JUL06KULGON-GON | ITF_W | ? | 22 | 16 | +6 (place_cell) | — | pre | single |  | PENDING |
| 03:34 | ITFMATCH-26JUL06HERNAG-HER | ITF_M | ? | 70 | 49 | +21 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 179 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 56, 'FLOW_AT_LEVEL': 13, 'NO_FLOW': 110} | repriceable now: true 36 / false 143 | **cumulative bid_grade lines: 1335 (repriceable true 144 / false 1191)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06BASHOE-B | 47 | 6m | 0 | 47-50 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06BASHOE-H | 51 | 6m | 0 | 51-52 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06CAMDE-CA | 58 | 134m | 2/61-62/317 | 59-61 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ATPCHALLENGERMATCH-26JUL06CAMDE-DE | 39 | 156m | 1/41-41/17 | 39-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPCHALLENGERMATCH-26JUL06CHEYEV-C | 61 | 36m | 1/62-62/9 | 61-62 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→62 |
| ATPCHALLENGERMATCH-26JUL06CHEYEV-Y | 37 | 36m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DALCAR-C | 3 | 126m | 9/4-4/518 | 3-4 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→4 |
| ATPCHALLENGERMATCH-26JUL06DALCAR-D | 96 | 126m | 2/97-97/155 | 96-97 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→97 |
| ATPCHALLENGERMATCH-26JUL06DELWAL-D | 27 | 96m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DELWAL-W | 71 | 96m | 1/71-71/9 | 71-73 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-E | 95 | 66m | 0 | 95-96 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-S | 4 | 66m | 0 | 4-5 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-G | 71 | 126m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | 26 | 107m | 2/27-27/523 | 27-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-H | 35 | 66m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-P | 61 | 66m | 2/67-67/29 | 63-67 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-D | 20 | 6m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06IVADIN-I | 78 | 6m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 217m | 26/8-9/1439 | 6-8 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ATPCHALLENGERMATCH-26JUL06KRACRI-K | 92 | 175m | 9/92-94/304 | 92-94 | 0 | **FLOW_AT_LEVEL** | 91 |  |
| ATPCHALLENGERMATCH-26JUL06KUZSTR-K | 73 | 36m | 0 | 73-74 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KUZSTR-S | 26 | 36m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARBER-B | 58 | 126m | 1/59-59/8 | 58-59 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ATPCHALLENGERMATCH-26JUL06MARBER-M | 40 | 126m | 2/42-42/80 | 40-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06MARHAM-H | 5 | 66m | 0 | 5-6 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARHAM-M | 94 | 52m | 1/95-95/0 | 94-95 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→95 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH-N | 57 | 102m | 4/60-60/66 | 59-59 | 3 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06OPIPET-O | 26 | 36m | 1/27-27/0 | 26-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ATPCHALLENGERMATCH-26JUL06PAPJAN-P | 53 | 96m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-M | 52 | 77m | 3/56-56/272 | 53-56 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-P | 44 | 126m | 5/46-46/424 | 46-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ATPCHALLENGERMATCH-26JUL06POTFEL-F | 58 | 126m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-P | 40 | 126m | 1/42-42/15 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 192m | 15/42-45/1707 | 43-43 | 2 | **FLOW_ABOVE** | 40 | flow above but bound 40c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PRIORA-P | 56 | 66m | 11/56-58/470 | 57-58 | 0 | **FLOW_AT_LEVEL** | 55 |  |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 61 | 66m | 0 | 65-69 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 32 | 65m | 0 | 32-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-B | 36 | 96m | 1/37-37/7 | 36-37 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-S | 61 | 96m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-M | 10 | 125m | 1/10-10/0 | 10-12 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-S | 88 | 126m | 1/90-90/0 | 88-90 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 156m | 1/35-35/349 | 33-34 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ATPCHALLENGERMATCH-26JUL06STALEC-S | 64 | 122m | 4/66-66/59 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ATPCHALLENGERMATCH-26JUL06VALZHU-V | 71 | 6m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06VALZHU-Z | 27 | 6m | 0 | 27-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 22 | 112m | 7/27-28/337 | 27-25 | 5 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 22 | 36m | 0 | 27-25 | — | **NO_FLOW** | 22 |  |
| ATPCHALLENGERMATCH-26JUL06WEHVAN-V | 42 | 18m | 0 | 45-46 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-D | 42 | 66m | 1/44-44/11 | 42-44 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-Z | 56 | 66m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-ALI | 86 | 65m | 0 | 86-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-MIS | 6 | 65m | 0 | 6-14 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 150m | 15/69-83/118 | 67-66 | 5 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 65m | 11/69-83/109 | 69-66 | 5 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BONFAU-FAU | 25 | 65m | 0 | 25-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06CASBAY-CAS | 6 | 93m | 0 | 6-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-DUG | 63 | 53m | 0 | 63-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-HOF | 20 | 52m | 0 | 20-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-ELD | 64 | 83m | 1/69-69/2 | 64-69 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 30 | 179m | 0 | 30-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 125m | 12/14-19/260 | 18-15 | -2 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06HERNAG-NAG | 11 | 1m | 0 | 12-47 | — | **NO_FLOW** | 27 |  |
| ITFMATCH-26JUL06KASLIL-KAS | 63 | 36m | 0 | 63-69 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-LIL | 30 | 14m | 0 | 30-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LARJIM-JIM | 57 | 83m | 0 | 57-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LARJIM-LAR | 39 | 89m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LAZVAC-LAZ | 54 | 78m | 1/60-60/3 | 54-60 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06LAZVAC-VAC | 39 | 62m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 32 | 53m | 0 | 32-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-THE | 65 | 121m | 0 | 65-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MEHCOU-MEH | 25 | 95m | 0 | 25-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALBRE-BRE | 6 | 125m | 3/11-11/29 | 6-8 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALBRE-SAL | 89 | 121m | 1/94-94/21 | 89-93 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALNGW-SAL | 58 | 5m | 4/68-69/39 | 61-60 | 10 | **FLOW_ABOVE** | 58 | flow above but bound 58c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06STAGUI-GUI | 16 | 13m | 0 | 16-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06STAGUI-STA | 16 | 13m | 0 | 16-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRA | 24 | 34m | 0 | 24-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TRUTRA-TRU | 66 | 36m | 0 | 66-75 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-AND | 22 | 49m | 0 | 22-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-TSI | 55 | 49m | 0 | 55-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ADKFER-ADK | 53 | 52m | 0 | 53-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ADKFER-FER | 18 | 52m | 0 | 18-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 20 | 20m | 0 | 28-32 | — | **NO_FLOW** | 20 |  |
| ITFWMATCH-26JUL06BOSTOP-BOS | 67 | 5m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOSTOP-TOP | 33 | 97m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 148m | 109/30-50/3306 | 50-36 | -4 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06BUYALV-ALV | 22 | 27m | 0 | 22-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BUYALV-BUY | 53 | 27m | 0 | 53-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DIANIK-DIA | 44 | 16m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DIANIK-NIK | 52 | 13m | 0 | 52-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DZJMCK-DZJ | 74 | 61m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DZJMCK-MCK | 22 | 93m | 2/26-27/17 | 22-27 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFWMATCH-26JUL06EWAMAN-EWA | 65 | 41m | 0 | 65-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EWAMAN-MAN | 20 | 18m | 0 | 20-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-GAL | 76 | 76m | 1/80-80/2 | 76-80 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL06GALTSE-TSE | 21 | 87m | 0 | 21-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-GAN | 83 | 65m | 0 | 83-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-PUI | 11 | 57m | 0 | 11-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HEDCHI-CHI | 46 | 10m | 0 | 46-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HEDCHI-HED | 43 | 10m | 1/55-55/8 | 43-55 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 4 | 6m | 0 | 84-58 | — | **NO_FLOW** | 36 |  |
| ITFWMATCH-26JUL06ILIEBE-EBE | 52 | 95m | 0 | 52-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ILIEBE-ILI | 38 | 27m | 0 | 38-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06IVAKUH-IVA | 62 | 133m | 10/63-64/546 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL06IVAKUH-KUH | 37 | 154m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06JOSKUM-JOS | 61 | 0m | 0 | 64-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARBAS-KAR | 71 | 181m | 5/75-76/40 | 71-72 | 4 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARBAS-KAR | 67 | 84m | 0 | 71-72 | — | **NO_FLOW** | 71 |  |
| ITFWMATCH-26JUL06KARVIS-KAR | 76 | 67m | 0 | 76-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARVIS-VIS | 14 | 64m | 0 | 14-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOTCHI-KOT | 33 | 69m | 0 | 33-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOVDAE-DAE | 18 | 6m | 0 | 18-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOVDAE-KOV | 75 | 6m | 0 | 75-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 6m | 0 | 76-80 | — | **NO_FLOW** | 75 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 6m | 0 | 76-80 | — | **NO_FLOW** | 75 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 193m | 3851/23-99/439323 | 99-24 | -14 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06LUKNOE-LUK | 69 | 77m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUKNOE-NOE | 25 | 185m | 1/31-31/4 | 25-30 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-ENC | 51 | 23m | 0 | 51-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MCAENC-MCA | 42 | 12m | 0 | 42-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MILHER-HER | 14 | 23m | 0 | 14-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06MILHER-MIL | 64 | 23m | 0 | 64-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKASAK-OKA | 25 | 28m | 0 | 25-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-OKU | 54 | 21m | 0 | 54-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-PRI | 39 | 23m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PACLOV-LOV | 41 | 95m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PACLOV-PAC | 56 | 95m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 97m | 1942/1-13/312225 | 14-1 | -7 | **FLOW_AT_LEVEL** | 12 |  |
| ITFWMATCH-26JUL06PEEPAH-PAH | 58 | 48m | 0 | 58-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PEEPAH-PEE | 37 | 74m | 0 | 37-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PIERAD-PIE | 58 | 25m | 0 | 58-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PIERAD-RAD | 27 | 27m | 0 | 27-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PODLUK-LUK | 68 | 23m | 0 | 68-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PODLUK-POD | 26 | 26m | 0 | 26-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06POPSOL-SOL | 61 | 134m | 8/66-75/47 | 65-63 | 5 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06POPSOL-SOL | 59 | 65m | 1/66-66/4 | 65-63 | 7 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06PRINIJ-NIJ | 30 | 6m | 0 | 30-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PRINIJ-PRI | 63 | 6m | 0 | 63-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06RICMIT-MIT | 7 | 156m | 18/8-90/167 | 7-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 216m | 91/79-90/1285 | 80-82 | 1 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 144m | 11098/13-90/925686 | 83-16 | -1 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06SPIMED-MED | 5 | 125m | 1/14-14/14 | 5-14 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06SPIMED-SPI | 86 | 77m | 3/95-95/25 | 86-95 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-SCH | 6 | 93m | 0 | 6-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-TEI | 73 | 5m | 0 | 73-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-TRI | 8 | 83m | 0 | 8-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-VOR | 56 | 13m | 0 | 56-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-EVA | 34 | 4m | 0 | 34-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06URREVA-URR | 56 | 5m | 0 | 56-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 143m | 873/3-26/63653 | 20-5 | -12 | **FLOW_AT_LEVEL** | 15 |  |
| ITFWMATCH-26JUL06VIRKOV-KOV | 28 | 21m | 0 | 28-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VIRKOV-VIR | 56 | 21m | 0 | 56-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-DIL | 59 | 35m | 2/60-60/208 | 60-60 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFWMATCH-26JUL06VLADIL-VLA | 41 | 24m | 0 | 41-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06WAGYOU-WAG | 34 | 44m | 0 | 34-58 | — | **NO_FLOW** | 34 |  |
| ITFWMATCH-26JUL06WONIBR-WON | 32 | 142m | 16/72-92/49 | 87-57 | 40 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL06ARANIL-A | 73 | 53m | 1/75-75/56 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| WTACHALLENGERMATCH-26JUL06ARANIL-N | 25 | 66m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BOUKOT-B | 22 | 156m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| WTACHALLENGERMATCH-26JUL06BOUKOT-K | 77 | 149m | 3/78-79/638 | 77-78 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| WTACHALLENGERMATCH-26JUL06BULSTR-B | 71 | 156m | 2/71-74/23 | 71-74 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BULSTR-S | 27 | 92m | 2/28-29/56 | 27-29 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→28 |
| WTACHALLENGERMATCH-26JUL06GRAMAS-G | 32 | 66m | 1/33-33/100 | 32-33 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| WTACHALLENGERMATCH-26JUL06GRAMAS-M | 67 | 66m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 41 | 156m | 1/43-43/28 | 41-43 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| WTACHALLENGERMATCH-26JUL06HERNGU-N | 58 | 20m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HESPAL-H | 30 | 67m | 0 | 30-31 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HESPAL-P | 69 | 67m | 0 | 69-70 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06LEWMAR-L | 55 | 66m | 0 | 55-57 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06LEWMAR-M | 43 | 66m | 1/44-44/12 | 43-44 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→44 |
| WTACHALLENGERMATCH-26JUL06MATPUT-M | 9 | 66m | 1/9-9/0 | 9-10 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MATPUT-P | 89 | 66m | 2/91-91/35 | 90-91 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| WTACHALLENGERMATCH-26JUL06MONPOP-M | 46 | 13m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MONPOP-P | 54 | 154m | 2/55-55/1177 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| WTACHALLENGERMATCH-26JUL06NOHBUR-B | 22 | 86m | 4/24-24/393 | 23-23 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| WTACHALLENGERMATCH-26JUL06OLIUCH-U | 39 | 36m | 4/40-40/128 | 40-40 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| WTACHALLENGERMATCH-26JUL06ROMSEM-R | 42 | 36m | 0 | 43-44 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06ROMSEM-S | 56 | 67m | 1/57-57/8 | 56-57 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| WTAMATCH-26JUL06KRUKOS-KRU | 31 | 96m | 46/31-32/4937 | 32-32 | 0 | **FLOW_AT_LEVEL** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06KARBAS | 26 | 72 | **98** | 97 | +1 |
| ITFMATCH-26JUL06BEASCO | 33 | 66 | **99** | 97 | +2 |
| ITFWMATCH-26JUL06POPSOL | 36 | 63 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH | 40 | 59 | **99** | 97 | +2 |
| ITFMATCH-26JUL06SALNGW | 39 | 60 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06VILBOC | 75 | 25 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06SACLAZ | 19 | 82 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06KULGON | 22 | 80 | **102** | 97 | +5 |
| ITFWMATCH-26JUL06BOIBOY | 77 | 32 | **109** | 97 | +12 |
| ITFMATCH-26JUL06HERNAG | 70 | 47 | **117** | 97 | +20 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ITFWMATCH-26JUL06WAGYOU | 63 | 58 | **121** | 97 | +24 |
| ITFWMATCH-26JUL06WONIBR | 65 | 57 | **122** | 97 | +25 |

## PATTERNS (sub-B) — 9
- half_arm_aging: KXITFWMATCH-26JUL06SACLAZ-LAZ {"fill": 19, "age_min": 213, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 211, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 184, "mode": "SET_BELOW_FLOW(prints 40c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06KARBAS-BAS {"fill": 26, "age_min": 182, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFMATCH-26JUL06BEASCO-SCO {"fill": 33, "age_min": 156, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06POPSOL-POP {"fill": 36, "age_min": 134, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VILBOC-VIL {"fill": 75, "age_min": 112, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06NIJRAH-RAH {"fill": 40, "age_min": 105, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06WAGYOU-YOU {"fill": 63, "age_min": 76, "mode": "STARVATION(no prints since post)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
