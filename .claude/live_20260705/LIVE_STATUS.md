# LIVE VALIDATION — rolling status

- cycle 92 @ **2026-07-06 02:25:44 AM ET** | build `28d16bf` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 50092 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 01:01:56 | **combined_over_goal** | KXITFWMATCH-26JUL06TODSAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 01:12:30 | **combined_over_goal** | KXITFWMATCH-26JUL06VAJRAM | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 26 graded (session)
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
| 00:55 | ITFWMATCH-26JUL06ZRNLUE-LUE | ITF_W | underdog | 69 | 6 | +63 (place_cell) | — | pre | single |  | PENDING |
| 01:00 | ITFMATCH-26JUL06VULCOU-VUL | ITF_M | leader | 81 | 80 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:00 | ITFMATCH-26JUL06BEASCO-SCO | ITF_M | underdog | 33 | 21 | +12 (place_cell) | — | pre | single |  | PENDING |
| 01:01 | ITFWMATCH-26JUL06TODSAG-SAG | ITF_W | ? | 30 | 25 | +5 (place_cell) | — | pre | pair | 98 | PENDING |
| 01:05 | ITFWMATCH-26JUL06BRESAF-SAF | ITF_W | underdog | 34 | 32 | +2 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:12 | ITFWMATCH-26JUL06VAJRAM-RAM | ITF_W | ? | 19 | 9 | +10 (place_cell) | — | pre | pair | 101 | PENDING |
| 01:22 | ITFWMATCH-26JUL06POPSOL-POP | ITF_W | underdog | 36 | 21 | +15 (place_cell) | — | pre | single |  | PENDING |
| 01:23 | ITFMATCH-26JUL06GENAZO-GEN | ITF_M | leader | 81 | 73 | +8 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:44 | ATPCHALLENGERMATCH-26JUL06VILBOC-V | ATP_CHALL | leader | 75 | 72 | +3 (place_cell) | — | pre | single |  | PENDING |
| 01:51 | ATPCHALLENGERMATCH-26JUL06NIJRAH-R | ATP_CHALL | underdog | 40 | 37 | +3 (place_cell) | — | pre | single |  | PENDING |
| 02:21 | ITFWMATCH-26JUL06WAGYOU-YOU | ITF_W | leader | 63 | 49 | +14 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 110 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 34, 'FLOW_AT_LEVEL': 8, 'NO_FLOW': 68} | repriceable now: true 20 / false 90 | **cumulative bid_grade lines: 1125 (repriceable true 123 / false 1002)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06CAMDE-CA | 58 | 63m | 1/61-61/312 | 59-61 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ATPCHALLENGERMATCH-26JUL06CAMDE-DE | 39 | 85m | 1/41-41/17 | 39-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPCHALLENGERMATCH-26JUL06DALCAR-C | 3 | 55m | 6/4-4/366 | 3-4 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→4 |
| ATPCHALLENGERMATCH-26JUL06DALCAR-D | 96 | 55m | 2/97-97/155 | 96-97 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→97 |
| ATPCHALLENGERMATCH-26JUL06DELWAL-D | 27 | 25m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DELWAL-W | 71 | 25m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-G | 71 | 55m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | 26 | 35m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 145m | 26/8-9/1439 | 6-8 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ATPCHALLENGERMATCH-26JUL06KRACRI-K | 92 | 104m | 8/92-94/301 | 92-94 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARBER-B | 58 | 55m | 1/59-59/8 | 58-59 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ATPCHALLENGERMATCH-26JUL06MARBER-M | 40 | 55m | 2/42-42/80 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH-N | 57 | 31m | 1/60-60/41 | 59-59 | 3 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PAPJAN-P | 53 | 25m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-M | 52 | 6m | 0 | 52-56 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-P | 44 | 55m | 0 | 44-46 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-F | 58 | 55m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-P | 40 | 55m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 121m | 5/43-43/72 | 42-43 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-B | 36 | 25m | 0 | 36-37 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-S | 61 | 25m | 0 | 61-63 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-M | 10 | 54m | 0 | 10-12 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-S | 88 | 55m | 1/90-90/0 | 88-90 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 85m | 1/35-35/349 | 33-34 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ATPCHALLENGERMATCH-26JUL06STALEC-S | 64 | 51m | 1/66-66/34 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 22 | 41m | 0 | 25-25 | — | **NO_FLOW** | 22 |  |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 79m | 4/73-76/9 | 67-66 | 9 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06CASBAY-CAS | 6 | 22m | 0 | 6-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-DUG | 62 | 13m | 0 | 62-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-HOF | 18 | 14m | 0 | 18-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-ELD | 64 | 11m | 0 | 64-69 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 30 | 108m | 0 | 30-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 54m | 5/15-18/61 | 18-15 | -1 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06HERNAG-HER | 52 | 22m | 0 | 52-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HERNAG-NAG | 5 | 23m | 0 | 5-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-KAS | 51 | 8m | 0 | 51-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-LIL | 21 | 8m | 0 | 21-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LARJIM-JIM | 57 | 11m | 0 | 57-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LARJIM-LAR | 39 | 18m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LAZVAC-LAZ | 54 | 7m | 0 | 54-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LAZVAC-VAC | 36 | 18m | 0 | 36-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 27 | 55m | 0 | 27-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-THE | 65 | 50m | 0 | 65-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MEHCOU-MEH | 25 | 24m | 0 | 25-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALBRE-BRE | 6 | 54m | 1/11-11/17 | 6-8 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALBRE-SAL | 89 | 50m | 1/94-94/21 | 89-93 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALNGW-NGW | 39 | 149m | 5/44-45/91 | 39-40 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALNGW-SAL | 56 | 19m | 1/60-60/3 | 56-60 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFMATCH-26JUL06TSIAND-AND | 21 | 1m | 0 | 21-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-TSI | 54 | 1m | 0 | 54-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOI | 77 | 23m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 17 | 23m | 0 | 17-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOSTOP-BOS | 64 | 25m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOSTOP-TOP | 33 | 25m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 76m | 40/34-44/1216 | 41-38 | 0 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06DIANIK-DIA | 28 | 69m | 0 | 28-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DZJMCK-DZJ | 65 | 107m | 5/77-78/14 | 65-78 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06DZJMCK-MCK | 22 | 22m | 0 | 22-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-GAL | 76 | 5m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-TSE | 21 | 16m | 0 | 21-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-GAN | 82 | 6m | 0 | 82-90 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-PUI | 10 | 3m | 0 | 10-18 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HEDCHI-CHI | 25 | 1m | 0 | 25-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HEDCHI-HED | 25 | 1m | 0 | 25-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 14 | 9m | 1/83-83/5 | 84-58 | 69 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ILIEBE-EBE | 52 | 24m | 0 | 52-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ILIEBE-ILI | 35 | 1m | 0 | 35-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06IVAKUH-IVA | 62 | 62m | 10/63-64/546 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL06IVAKUH-KUH | 37 | 83m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARBAS-KAR | 71 | 110m | 5/75-76/40 | 71-72 | 4 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARBAS-KAR | 67 | 13m | 0 | 71-72 | — | **NO_FLOW** | 71 |  |
| ITFWMATCH-26JUL06KARVIS-KAR | 75 | 5m | 0 | 75-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARVIS-VIS | 12 | 5m | 0 | 12-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOTCHI-KOT | 31 | 0m | 0 | 31-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-GON | 22 | 9m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 76 | 11m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 122m | 1356/23-57/96134 | 46-24 | -14 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06LUKNOE-LUK | 69 | 6m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUKNOE-NOE | 25 | 114m | 1/31-31/4 | 25-30 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-PRI | 35 | 8m | 0 | 35-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PACLOV-LOV | 41 | 24m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PACLOV-PAC | 56 | 24m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 26m | 875/2-13/120087 | 14-3 | -6 | **FLOW_AT_LEVEL** | 12 |  |
| ITFWMATCH-26JUL06PEEPAH-PAH | 57 | 1m | 0 | 57-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PEEPAH-PEE | 37 | 3m | 0 | 37-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06POPSOL-SOL | 61 | 63m | 7/66-75/43 | 62-63 | 5 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06RICMIT-MIT | 7 | 84m | 17/8-90/164 | 7-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 145m | 56/79-86/440 | 80-82 | 1 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 72m | 2205/13-70/323883 | 53-16 | -1 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06SPIMED-MED | 5 | 54m | 0 | 5-14 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SPIMED-SPI | 86 | 6m | 3/95-95/25 | 86-95 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-SCH | 6 | 22m | 0 | 6-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-TEI | 54 | 10m | 0 | 54-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-TRI | 8 | 12m | 0 | 8-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 72m | 56/9-25/1920 | 20-13 | -6 | **FLOW_AT_LEVEL** | 15 |  |
| ITFWMATCH-26JUL06VLADIL-DIL | 55 | 69m | 2/60-60/19 | 55-60 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-VLA | 40 | 88m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06WAGYOU-WAG | 29 | 5m | 0 | 29-48 | — | **NO_FLOW** | 34 |  |
| ITFWMATCH-26JUL06WONIBR-WON | 32 | 71m | 16/72-92/49 | 88-57 | 40 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 28 | 50m | 0 | 50-39 | — | **NO_FLOW** | 28 |  |
| WTACHALLENGERMATCH-26JUL06BOUKOT-B | 22 | 85m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| WTACHALLENGERMATCH-26JUL06BOUKOT-K | 77 | 78m | 2/79-79/616 | 77-78 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→79 |
| WTACHALLENGERMATCH-26JUL06BULSTR-B | 71 | 85m | 1/74-74/15 | 71-74 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| WTACHALLENGERMATCH-26JUL06BULSTR-S | 27 | 20m | 0 | 27-28 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 41 | 85m | 1/43-43/28 | 41-43 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| WTACHALLENGERMATCH-26JUL06HERNGU-N | 57 | 68m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MONPOP-M | 44 | 85m | 6/47-48/222 | 45-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| WTACHALLENGERMATCH-26JUL06MONPOP-P | 54 | 83m | 1/55-55/22 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| WTACHALLENGERMATCH-26JUL06NOHBUR-B | 22 | 15m | 0 | 23-23 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL06KRUKOS-KRU | 31 | 25m | 12/31-32/1428 | 32-32 | 0 | **FLOW_AT_LEVEL** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL06KARBAS | 26 | 72 | **98** | 97 | +1 |
| ITFMATCH-26JUL06BEASCO | 33 | 66 | **99** | 97 | +2 |
| ITFWMATCH-26JUL06POPSOL | 36 | 63 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH | 40 | 59 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL06VILBOC | 75 | 25 | **100** | 97 | +3 |
| ITFWMATCH-26JUL06SACLAZ | 19 | 82 | **101** | 97 | +4 |
| ITFWMATCH-26JUL06ZRNLUE | 69 | 39 | **108** | 97 | +11 |
| ITFWMATCH-26JUL06WAGYOU | 63 | 48 | **111** | 97 | +14 |
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ITFWMATCH-26JUL06WONIBR | 65 | 57 | **122** | 97 | +25 |

## PATTERNS (sub-B) — 9
- half_arm_aging: KXITFWMATCH-26JUL06SACLAZ-LAZ {"fill": 19, "age_min": 142, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 140, "mode": "SET_BELOW_FLOW(prints 69c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 113, "mode": "SET_BELOW_FLOW(prints 40c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06KARBAS-BAS {"fill": 26, "age_min": 111, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06ZRNLUE-LUE {"fill": 69, "age_min": 91, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFMATCH-26JUL06BEASCO-SCO {"fill": 33, "age_min": 85, "mode": "SET_BELOW_FLOW(prints 9c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06POPSOL-POP {"fill": 36, "age_min": 63, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VILBOC-VIL {"fill": 75, "age_min": 41, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06NIJRAH-RAH {"fill": 40, "age_min": 34, "mode": "SET_BELOW_FLOW(prints 3c above)", "emitted_et": "2026-07-06 02:25:44 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
