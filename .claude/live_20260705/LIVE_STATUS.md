# LIVE VALIDATION — rolling status

- cycle 90 @ **2026-07-06 02:05:29 AM ET** | build `f23330a` | session boot 07-05 23:50 ET | log `live_v3_20260705.jsonl` | 48187 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 01:01:56 | **combined_over_goal** | KXITFWMATCH-26JUL06TODSAG | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |
| 01:12:30 | **combined_over_goal** | KXITFWMATCH-26JUL06VAJRAM | pair combined 101c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 25 graded (session)
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

## RESTING BIDS — 100 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 32, 'FLOW_AT_LEVEL': 8, 'NO_FLOW': 60} | repriceable now: true 16 / false 84 | **cumulative bid_grade lines: 1069 (repriceable true 118 / false 951)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06CAMDE-CA | 58 | 42m | 1/61-61/312 | 59-61 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ATPCHALLENGERMATCH-26JUL06CAMDE-DE | 39 | 65m | 1/41-41/17 | 39-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ATPCHALLENGERMATCH-26JUL06DALCAR-C | 3 | 35m | 4/4-4/250 | 3-4 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→4 |
| ATPCHALLENGERMATCH-26JUL06DALCAR-D | 96 | 35m | 2/97-97/155 | 96-97 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→97 |
| ATPCHALLENGERMATCH-26JUL06DELWAL-D | 27 | 5m | 0 | 27-30 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06DELWAL-W | 71 | 5m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-G | 71 | 35m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06GOMLUZ-L | 26 | 15m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06KRACRI-C | 6 | 125m | 26/8-9/1439 | 6-8 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ATPCHALLENGERMATCH-26JUL06KRACRI-K | 92 | 84m | 8/92-94/301 | 92-94 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARBER-B | 58 | 35m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06MARBER-M | 40 | 35m | 1/42-42/44 | 40-42 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→42 |
| ATPCHALLENGERMATCH-26JUL06NIJRAH-N | 57 | 11m | 1/60-60/41 | 59-59 | 3 | **FLOW_ABOVE** | 57 | flow above but bound 57c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL06PAPJAN-P | 53 | 5m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PIEMOL-P | 44 | 35m | 0 | 44-46 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-F | 58 | 35m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06POTFEL-P | 40 | 35m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06PRIORA-O | 40 | 100m | 5/43-43/72 | 42-43 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-B | 36 | 5m | 0 | 36-37 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEGBRA-S | 61 | 5m | 0 | 61-63 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-M | 10 | 34m | 0 | 10-12 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06SEYMAR-S | 88 | 35m | 1/90-90/0 | 88-90 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| ATPCHALLENGERMATCH-26JUL06STALEC-L | 33 | 65m | 1/35-35/349 | 33-34 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→35 |
| ATPCHALLENGERMATCH-26JUL06STALEC-S | 64 | 30m | 1/66-66/34 | 64-66 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ATPCHALLENGERMATCH-26JUL06VILBOC-B | 22 | 21m | 0 | 26-25 | — | **NO_FLOW** | 22 |  |
| ITFMATCH-26JUL06BEASCO-BEA | 64 | 59m | 4/73-76/9 | 67-66 | 9 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ITFMATCH-26JUL06CASBAY-CAS | 6 | 2m | 0 | 6-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-DUG | 56 | 4m | 0 | 56-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06DUGHOF-HOF | 13 | 3m | 0 | 13-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-ELD | 59 | 92m | 1/69-69/1 | 59-69 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06ELDHAU-HAU | 30 | 88m | 0 | 30-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06GENAZO-AZO | 16 | 33m | 5/15-18/61 | 18-15 | -1 | **FLOW_AT_LEVEL** | 16 |  |
| ITFMATCH-26JUL06HERNAG-HER | 52 | 2m | 0 | 52-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06HERNAG-NAG | 5 | 2m | 0 | 5-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06KASLIL-LIL | 6 | 3m | 0 | 6-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LARJIM-JIM | 52 | 2m | 0 | 52-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LARJIM-LAR | 35 | 3m | 5/49-51/314 | 35-43 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06LAZVAC-VAC | 35 | 0m | 0 | 35-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-LEN | 27 | 34m | 0 | 27-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06LENTHE-THE | 65 | 30m | 0 | 65-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06MEHCOU-MEH | 25 | 4m | 0 | 25-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL06SALBRE-BRE | 6 | 34m | 1/11-11/17 | 6-8 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALBRE-SAL | 89 | 30m | 1/94-94/21 | 89-93 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALNGW-NGW | 39 | 129m | 5/44-45/91 | 39-44 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL06SALNGW-SAL | 55 | 16m | 4/60-60/35 | 55-60 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOI | 77 | 2m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOIBOY-BOY | 17 | 2m | 0 | 17-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOSTOP-BOS | 64 | 5m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BOSTOP-TOP | 33 | 5m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06BRESAF-SAF | 34 | 56m | 35/34-44/1055 | 41-38 | 0 | **FLOW_AT_LEVEL** | 34 |  |
| ITFWMATCH-26JUL06DIANIK-DIA | 28 | 48m | 0 | 28-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06DZJMCK-DZJ | 65 | 86m | 5/77-78/14 | 65-78 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06DZJMCK-MCK | 22 | 2m | 0 | 22-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-GAL | 73 | 34m | 0 | 73-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06GALTSE-TSE | 20 | 34m | 0 | 20-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HEDCHI-CHI | 3 | 33m | 0 | 24-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06HOSFEH-HOS | 14 | 6m | 3/88-92/17 | 84-58 | 74 | **FLOW_ABOVE** | 36 | flow above but bound 36c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ILIEBE-EBE | 52 | 4m | 0 | 52-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06ILIEBE-ILI | 10 | 2m | 0 | 41-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06IVAKUH-IVA | 62 | 41m | 0 | 62-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06IVAKUH-KUH | 37 | 63m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KARBAS-KAR | 71 | 90m | 5/75-76/40 | 71-72 | 4 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06KOTCHI-KOT | 28 | 2m | 0 | 28-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-GON | 20 | 34m | 0 | 20-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06KULGON-KUL | 75 | 21m | 0 | 75-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06LUCGAD-GAD | 37 | 102m | 666/29-57/29264 | 44-34 | -8 | **FLOW_AT_LEVEL** | 37 |  |
| ITFWMATCH-26JUL06LUKNOE-LUK | 68 | 90m | 3/74-74/39 | 68-74 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06LUKNOE-NOE | 25 | 94m | 1/31-31/4 | 25-31 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL06OKUPRI-PRI | 31 | 1m | 0 | 31-54 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PACLOV-LOV | 41 | 4m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PACLOV-PAC | 56 | 4m | 0 | 56-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PASCOP-PAS | 8 | 5m | 168/8-13/26586 | 14-11 | 0 | **FLOW_AT_LEVEL** | 12 |  |
| ITFWMATCH-26JUL06PEEPAH-PAH | 41 | 2m | 0 | 45-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06PEEPAH-PEE | 33 | 2m | 0 | 34-54 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06POPSOL-SOL | 61 | 43m | 7/66-75/43 | 62-63 | 5 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06RICMIT-MIT | 7 | 64m | 14/8-90/149 | 7-9 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→8 |
| ITFWMATCH-26JUL06SACLAZ-SAC | 78 | 125m | 54/79-86/430 | 80-82 | 1 | **FLOW_ABOVE** | 78 | flow above but bound 78c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06SIMCIR-CIR | 14 | 52m | 215/13-29/27139 | 18-16 | -1 | **FLOW_AT_LEVEL** | 16 |  |
| ITFWMATCH-26JUL06SPIMED-MED | 5 | 34m | 0 | 5-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06SPIMED-SPI | 83 | 34m | 0 | 83-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-SCH | 6 | 2m | 0 | 6-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TEISCH-TEI | 53 | 2m | 0 | 53-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06TRIVOR-TRI | 5 | 2m | 0 | 5-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VAJRAM-RAM | 15 | 52m | 22/9-25/301 | 20-13 | -6 | **FLOW_AT_LEVEL** | 15 |  |
| ITFWMATCH-26JUL06VLADIL-DIL | 55 | 48m | 0 | 55-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06VLADIL-VLA | 40 | 68m | 0 | 40-44 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06WAGYOU-WAG | 20 | 1m | 0 | 20-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06WAGYOU-YOU | 59 | 1m | 0 | 61-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL06WONIBR-WON | 32 | 50m | 9/72-77/32 | 78-57 | 40 | **FLOW_ABOVE** | 32 | flow above but bound 32c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL06ZRNLUE-ZRN | 28 | 30m | 0 | 50-39 | — | **NO_FLOW** | 28 |  |
| WTACHALLENGERMATCH-26JUL06BOUKOT-B | 22 | 65m | 1/23-23/20 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| WTACHALLENGERMATCH-26JUL06BOUKOT-K | 77 | 57m | 0 | 77-78 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BULSTR-B | 71 | 65m | 0 | 71-74 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06BULSTR-S | 27 | 0m | 0 | 27-29 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06HERNGU-H | 41 | 65m | 1/43-43/28 | 41-43 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| WTACHALLENGERMATCH-26JUL06HERNGU-N | 57 | 48m | 0 | 57-59 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL06MONPOP-M | 44 | 65m | 6/47-48/222 | 45-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| WTACHALLENGERMATCH-26JUL06MONPOP-P | 54 | 63m | 1/55-55/22 | 54-55 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| WTACHALLENGERMATCH-26JUL06NOHBUR-B | 21 | 60m | 8/22-23/162 | 21-22 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| WTAMATCH-26JUL06KRUKOS-KRU | 31 | 5m | 4/31-32/181 | 32-32 | 0 | **FLOW_AT_LEVEL** | 99 |  |

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

## PATTERNS (sub-B) — 7
- half_arm_aging: KXITFWMATCH-26JUL06SACLAZ-LAZ {"fill": 19, "age_min": 121, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06HOSFEH-FEH {"fill": 61, "age_min": 120, "mode": "SET_BELOW_FLOW(prints 74c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06WONIBR-IBR {"fill": 65, "age_min": 92, "mode": "SET_BELOW_FLOW(prints 40c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06KARBAS-BAS {"fill": 26, "age_min": 91, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06ZRNLUE-LUE {"fill": 69, "age_min": 70, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFMATCH-26JUL06BEASCO-SCO {"fill": 33, "age_min": 65, "mode": "SET_BELOW_FLOW(prints 9c above)"}
- half_arm_aging: KXITFWMATCH-26JUL06POPSOL-POP {"fill": 36, "age_min": 43, "mode": "SET_BELOW_FLOW(prints 5c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
