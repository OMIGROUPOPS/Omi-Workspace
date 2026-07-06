# LIVE VALIDATION — rolling status

- cycle 94 @ **2026-07-06 02:46:13 AM ET** | build `b4826e4` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 51256 session events | monitor READ-ONLY
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

## RESTING BIDS — 144 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 44, 'FLOW_AT_LEVEL': 9, 'NO_FLOW': 91} | repriceable now: true 27 / false 117 | **cumulative bid_grade lines: 1204 (repriceable true 131 / false 1073)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06CAMDE-CA | 58 | 83m | 1/61-61/312 | 59-61 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ATPCHALLENGERMATCH-26JUL06CAMDE-DE | 39 | 105m | 1/41-41/17 | 39-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPCHALLENGERMATCH-26JUL06DALCAR-C | 3 | 76m | 9/4-4/518 | 3-4 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→4 |
| ATPCHALLENGERMATCH-26JUL06DALCAR-D | 96 | 76m | 2/97-97/155 | 96-97 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→97 |
| ATPCHALLENGERMATCH-26JUL06DELWAL-D | 27 | 45m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DELWAL-W | 71 | 45m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-E | 95 | 15m | 0 | 95-96 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ERHSIN-S | 4 | 15m | 0 | 4-5 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-G | 71 | 76m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | 26 | 56m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-H | 35 | 15m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06HUAPUR-P | 61 | 15m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 166m | 26/8-9/1439 | 6-8 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ATPCHALLENGERMATCH-26JUL06KRACRI-K | 92 | 125m | 9/92-94/304 | 92-94 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARBER-B | 58 | 75m | 1/59-59/8 | 58-59 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ATPCHALLENGERMATCH-26JUL06MARBER-M | 40 | 75m | 2/42-42/80 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06MARHAM-H | 5 | 15m | 0 | 5-6 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARHAM-M | 94 | 2m | 0 | 94-96 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06NIJRAH-N | 57 | 51m | 1/60-60/41 | 59-59 | 3 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PAPJAN-P | 53 | 45m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-M | 52 | 27m | 0 | 52-56 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-P | 44 | 76m | 2/46-46/10 | 44-46 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→46 |
| ATPCHALLENGERMATCH-26JUL06POTFEL-F | 58 | 76m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-P | 40 | 76m | 1/42-42/15 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 141m | 5/43-43/72 | 42-43 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ATPCHALLENGERMATCH-26JUL06PRIORA-P | 56 | 15m | 2/56-56/37 | 57-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 61 | 15m | 0 | 64-68 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06RAQRIB-R | 32 | 14m | 0 | 32-35 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-B | 36 | 45m | 1/37-37/7 | 36-37 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-S | 61 | 45m | 0 | 61-63 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-M | 10 | 74m | 0 | 10-12 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-S | 88 | 76m | 1/90-90/0 | 88-90 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 105m | 1/35-35/349 | 33-34 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ATPCHALLENGERMATCH-26JUL06STALEC-S | 64 | 71m | 2/66-66/42 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 22 | 61m | 7/27-28/337 | 27-25 | 5 | **FLOW_ABOVE** | 22 | flow above but bound 22c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-D | 42 | 15m | 0 | 42-44 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06ZORDEV-Z | 56 | 15m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-ALI | 86 | 14m | 0 | 86-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ALIMIS-MIS | 6 | 14m | 0 | 6-14 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 100m | 4/73-76/9 | 67-66 | 9 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 14m | 0 | 67-66 | — | **NO_FLOW** | 64 |  |
| ITFMATCH-26JUL06BONFAU-FAU | 25 | 14m | 0 | 25-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06CASBAY-CAS | 6 | 42m | 0 | 6-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-DUG | 63 | 2m | 0 | 63-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-HOF | 20 | 1m | 0 | 20-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-ELD | 64 | 32m | 1/69-69/2 | 64-69 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 30 | 128m | 0 | 30-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 74m | 5/15-18/61 | 18-14 | -1 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06HERNAG-HER | 57 | 1m | 0 | 60-95 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HERNAG-NAG | 5 | 43m | 0 | 5-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-KAS | 58 | 5m | 0 | 58-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-LIL | 24 | 5m | 0 | 24-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LARJIM-JIM | 57 | 32m | 0 | 57-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LARJIM-LAR | 39 | 38m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LAZVAC-LAZ | 54 | 28m | 1/60-60/3 | 54-60 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06LAZVAC-VAC | 39 | 11m | 0 | 39-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 32 | 3m | 0 | 32-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-THE | 65 | 70m | 0 | 65-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MEHCOU-MEH | 25 | 45m | 0 | 25-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALBRE-BRE | 6 | 75m | 1/11-11/17 | 6-8 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALBRE-SAL | 89 | 70m | 1/94-94/21 | 89-93 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALNGW-NGW | 39 | 169m | 5/44-45/91 | 39-40 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALNGW-SAL | 58 | 2m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-AND | 21 | 22m | 0 | 21-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06TSIAND-TSI | 54 | 22m | 0 | 54-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ADKFER-ADK | 53 | 1m | 0 | 53-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ADKFER-FER | 18 | 1m | 0 | 18-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOI | 77 | 43m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 17 | 43m | 0 | 17-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOSTOP-BOS | 64 | 46m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOSTOP-TOP | 33 | 46m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 97m | 44/34-44/1241 | 41-36 | 0 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06DIANIK-DIA | 30 | 0m | 0 | 30-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DZJMCK-DZJ | 74 | 10m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DZJMCK-MCK | 22 | 43m | 0 | 22-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06EWAMAN-MAN | 19 | 9m | 0 | 19-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-GAL | 76 | 25m | 0 | 76-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-TSE | 21 | 36m | 0 | 21-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-GAN | 83 | 14m | 0 | 83-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GANPUI-PUI | 11 | 7m | 0 | 11-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HEDCHI-CHI | 36 | 3m | 0 | 36-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HEDCHI-HED | 37 | 3m | 0 | 37-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 16 | 9m | 1/88-88/25 | 84-58 | 72 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ILIEBE-EBE | 52 | 45m | 0 | 52-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ILIEBE-ILI | 36 | 0m | 0 | 36-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06IVAKUH-IVA | 62 | 82m | 10/63-64/546 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFWMATCH-26JUL06IVAKUH-KUH | 37 | 103m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARBAS-KAR | 71 | 130m | 5/75-76/40 | 71-72 | 4 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KARBAS-KAR | 67 | 33m | 0 | 71-72 | — | **NO_FLOW** | 71 |  |
| ITFWMATCH-26JUL06KARVIS-KAR | 76 | 17m | 0 | 76-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARVIS-VIS | 14 | 14m | 0 | 14-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KOTCHI-KOT | 33 | 19m | 0 | 33-52 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-GON | 22 | 30m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 76 | 31m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 143m | 2234/23-69/218396 | 66-24 | -14 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06LUKNOE-LUK | 69 | 26m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUKNOE-NOE | 25 | 134m | 1/31-31/4 | 25-30 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-PRI | 36 | 2m | 0 | 36-53 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PACLOV-LOV | 41 | 44m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PACLOV-PAC | 56 | 44m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 46m | 1425/2-13/210378 | 14-3 | -6 | **FLOW_AT_LEVEL** | 12 |  |
| ITFWMATCH-26JUL06PEEPAH-PAH | 57 | 21m | 0 | 57-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PEEPAH-PEE | 37 | 23m | 0 | 37-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PIERAD-PIE | 55 | 3m | 0 | 55-77 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PIERAD-RAD | 24 | 3m | 0 | 24-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06POPSOL-SOL | 61 | 84m | 7/66-75/43 | 63-63 | 5 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06POPSOL-SOL | 59 | 14m | 0 | 63-63 | — | **NO_FLOW** | 61 |  |
| ITFWMATCH-26JUL06RICMIT-MIT | 7 | 105m | 17/8-90/164 | 7-10 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 166m | 57/79-86/483 | 80-82 | 1 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 93m | 3983/13-73/471748 | 70-16 | -1 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06SPIMED-MED | 5 | 75m | 0 | 5-14 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SPIMED-SPI | 86 | 26m | 3/95-95/25 | 86-95 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-SCH | 6 | 42m | 0 | 6-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-TEI | 63 | 0m | 0 | 63-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-TRI | 8 | 32m | 0 | 8-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-VOR | 51 | 5m | 0 | 51-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 93m | 78/9-25/2591 | 20-13 | -6 | **FLOW_AT_LEVEL** | 15 |  |
| ITFWMATCH-26JUL06VLADIL-DIL | 55 | 89m | 2/60-60/19 | 55-60 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-VLA | 40 | 108m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06WAGYOU-WAG | 31 | 2m | 0 | 31-63 | — | **NO_FLOW** | 34 |  |
| ITFWMATCH-26JUL06WONIBR-WON | 32 | 91m | 16/72-92/49 | 88-57 | 40 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 28 | 70m | 1/39-39/24 | 50-39 | 11 | **FLOW_ABOVE** | 28 | flow above but bound 28c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 28 | 1m | 0 | 50-39 | — | **NO_FLOW** | 28 |  |
| WTACHALLENGERMATCH-26JUL06ARANIL-A | 73 | 3m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06ARANIL-N | 25 | 15m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BOUKOT-B | 22 | 105m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| WTACHALLENGERMATCH-26JUL06BOUKOT-K | 77 | 98m | 3/78-79/638 | 77-78 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| WTACHALLENGERMATCH-26JUL06BULSTR-B | 71 | 105m | 1/74-74/15 | 71-74 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| WTACHALLENGERMATCH-26JUL06BULSTR-S | 27 | 41m | 1/28-28/34 | 27-29 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→28 |
| WTACHALLENGERMATCH-26JUL06GRAMAS-G | 32 | 15m | 1/33-33/100 | 32-33 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→33 |
| WTACHALLENGERMATCH-26JUL06GRAMAS-M | 67 | 15m | 0 | 67-68 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 41 | 105m | 1/43-43/28 | 41-43 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| WTACHALLENGERMATCH-26JUL06HERNGU-N | 57 | 88m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HESPAL-H | 30 | 16m | 0 | 30-31 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HESPAL-P | 69 | 16m | 0 | 69-70 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06LEWMAR-L | 55 | 15m | 0 | 55-57 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06LEWMAR-M | 43 | 15m | 0 | 43-44 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MATPUT-M | 9 | 15m | 0 | 9-10 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MATPUT-P | 89 | 15m | 1/91-91/9 | 89-91 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| WTACHALLENGERMATCH-26JUL06MONPOP-M | 44 | 105m | 6/47-48/222 | 45-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| WTACHALLENGERMATCH-26JUL06MONPOP-P | 54 | 103m | 1/55-55/22 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| WTACHALLENGERMATCH-26JUL06NOHBUR-B | 22 | 35m | 3/24-24/343 | 23-23 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→24 |
| WTACHALLENGERMATCH-26JUL06ROMSEM-S | 56 | 16m | 1/57-57/8 | 56-57 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→57 |
| WTAMATCH-26JUL06KRUKOS-KRU | 31 | 45m | 24/31-32/2319 | 32-32 | 0 | **FLOW_AT_LEVEL** | 99 |  |

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
| ITFWMATCH-26JUL06HOSFEH | 61 | 58 | **119** | 97 | +22 |
| ITFWMATCH-26JUL06WONIBR | 65 | 57 | **122** | 97 | +25 |
| ITFWMATCH-26JUL06WAGYOU | 63 | 63 | **126** | 97 | +29 |

## PATTERNS (sub-B) — 9
- half_arm_aging: KXITFWMATCH-26JUL06SACLAZ-LAZ {"fill": 19, "age_min": 162, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 161, "mode": "SET_BELOW_FLOW(prints 72c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 133, "mode": "SET_BELOW_FLOW(prints 40c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06KARBAS-BAS {"fill": 26, "age_min": 132, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06ZRNLUE-LUE {"fill": 69, "age_min": 111, "mode": "SET_BELOW_FLOW(prints 11c above)"}
- half_arm_aging: KXITFMATCH-26JUL06BEASCO-SCO {"fill": 33, "age_min": 105, "mode": "SET_BELOW_FLOW(prints 9c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06POPSOL-POP {"fill": 36, "age_min": 84, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06VILBOC-VIL {"fill": 75, "age_min": 61, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL06NIJRAH-RAH {"fill": 40, "age_min": 55, "mode": "SET_BELOW_FLOW(prints 3c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
