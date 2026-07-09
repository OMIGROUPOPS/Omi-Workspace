# LIVE VALIDATION — rolling status

- cycle 68 @ **2026-07-09 01:51:34 AM ET** | build `3c8431b` | session boot 07-09 00:36 ET | log `live_v3_20260709.jsonl` | 7133 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 00:40:05 | **combined_over_goal** | KXITFWMATCH-26JUL09SEDKRO | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 19 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:36 | ITFWMATCH-26JUL09SEDKRO-SED | ITF_W | ? | 8 | 4 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
| 00:36 | ITFMATCH-26JUL08MUJBEL-MUJ | ITF_M | ? | 39 | 35 | +4 (adopted_est) | -3.0 | pre | single |  | EARNED |
| 00:40 | ITFWMATCH-26JUL09SEDKRO-KRO | ITF_W | ? | 90 | 88 | +2 (fill_est) | — | pre | pair | 98 | PENDING |
| 00:41 | ITFWMATCH-26JUL08NAKMAL-MAL | ITF_W | ? | 23 | 18 | +5 (window_cell) | — | pre | single |  | MIXED |
| 00:48 | ITFWMATCH-26JUL09AHLMAK-AHL | ITF_W | ? | 31 | 27 | +4 (fill_est) | — | pre | pair | 97 | PENDING |
| 00:50 | ITFWMATCH-26JUL08LUENAT-LUE | ITF_W | ? | 78 | 76 | +2 (fill_est) | — | pre | single |  | PENDING |
| 00:51 | ITFWMATCH-26JUL09MAMJAN-MAM | ITF_W | ? | 54 | 52 | +2 (fill_est) | — | pre | single |  | PENDING |
| 00:54 | ITFWMATCH-26JUL09TUPNUP-NUP | ITF_W | underdog | 9 | 4 | +5 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:57 | ITFWMATCH-26JUL09TUPNUP-TUP | ITF_W | ? | 88 | 86 | +2 (fill_est) | — | pre | pair | 97 | PENDING |
| 01:05 | ITFWMATCH-26JUL09MATDYU-MAT | ITF_W | leader | 86 | 84 | +2 (place_cell) | — | pre | single |  | PENDING |
| 01:08 | ITFWMATCH-26JUL09DENKAZ-KAZ | ITF_W | underdog | 27 | 22 | +5 (place_cell) | — | pre | single |  | PENDING |
| 01:09 | ITFWMATCH-26JUL09SHONIS-NIS | ITF_W | underdog | 13 | 5 | +8 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:14 | ITFWMATCH-26JUL09AHLMAK-MAK | ITF_W | ? | 66 | 64 | +2 (fill_est) | — | pre | pair | 97 | PENDING |
| 01:24 | ITFWMATCH-26JUL09BOSGOL-BOS | ITF_W | ? | 49 | 45 | +4 (fill_est) | — | pre | single |  | PENDING |
| 01:24 | ITFWMATCH-26JUL08CHOYAM-YAM | ITF_W | ? | 67 | 86 | -19 (window_cell) | — | pre | single |  | MIXED |
| 01:26 | ITFWMATCH-26JUL09CEUBER-CEU | ITF_W | ? | 26 | 22 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 01:32 | ITFMATCH-26JUL09BEAVAN-BEA | ITF_M | ? | 52 | 49 | +3 (fill_est) | — | pre | single |  | PENDING |
| 01:40 | ITFMATCH-26JUL08GILOBR-GIL | ITF_M | ? | 10 | 6 | +4 (adopted_est) | 1.0 | pre | single |  | MIXED |
| 01:40 | ITFWMATCH-26JUL09SHONIS-SHO | ITF_W | ? | 84 | 82 | +2 (adopted_est) | — | pre | pair | 97 | PENDING |

## RESTING BIDS — 94 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 23, 'NO_FLOW': 70, 'FLOW_AT_LEVEL': 1} | repriceable now: true 17 / false 77 | **cumulative bid_grade lines: 6244 (repriceable true 703 / false 5541)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL08DERMIL-DER | 71 | 75m | 10/73-76/158 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL08GILOBR-OBR | 87 | 11m | 1/89-89/11 | 89-93 | 2 | **FLOW_ABOVE** | 87 | flow above but bound 87c < flow -- chasing breaks goal |
| ITFMATCH-26JUL09AGWMAT-AGW | 37 | 51m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09AGWMAT-MAT | 64 | 49m | 0 | 64-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ARCALU-ALU | 49 | 75m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ARCALU-ARC | 48 | 75m | 0 | 48-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BALGSC-BAL | 26 | 14m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BARTSI-BAR | 42 | 21m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BARTSI-TSI | 56 | 12m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BEAVAN-VAN | 42 | 18m | 0 | 45-47 | — | **NO_FLOW** | 45 |  |
| ITFMATCH-26JUL09BECADD-ADD | 74 | 36m | 0 | 74-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BECADD-BEC | 22 | 36m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BERCRA-BER | 26 | 36m | 2/29-29/105 | 26-28 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ITFMATCH-26JUL09BERCRA-CRA | 70 | 16m | 0 | 70-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BLATAL-BLA | 45 | 73m | 0 | 45-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09DUHTYA-DUH | 35 | 38m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09DUHTYA-TYA | 62 | 41m | 0 | 62-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ERIPHO-ERI | 83 | 1m | 0 | 83-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ERIPHO-PHO | 13 | 1m | 0 | 13-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09FILJED-FIL | 77 | 21m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09FILJED-JED | 18 | 21m | 0 | 18-23 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GHAGAR-GAR | 35 | 51m | 0 | 35-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GHAGAR-GHA | 63 | 41m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GUTROS-GUT | 36 | 21m | 0 | 36-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GUTROS-ROS | 61 | 21m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09LOPKAM-LOP | 75 | 7m | 1/76-76/12 | 75-76 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| ITFMATCH-26JUL09MAKROB-MAK | 38 | 69m | 0 | 38-41 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAKROB-ROB | 58 | 75m | 0 | 58-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAZMUR-MAZ | 79 | 51m | 0 | 79-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MENROH-MEN | 19 | 51m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MENROH-ROH | 78 | 51m | 0 | 78-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MICRIV-MIC | 74 | 8m | 1/77-77/12 | 74-77 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| ITFMATCH-26JUL09MILREC-MIL | 30 | 51m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MILREC-REC | 65 | 51m | 0 | 65-70 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MONBAD-BAD | 39 | 51m | 1/41-41/0 | 39-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ITFMATCH-26JUL09MONBAD-MON | 58 | 68m | 1/59-59/16 | 58-59 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFMATCH-26JUL09NASBOR-BOR | 54 | 40m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09NASBOR-NAS | 41 | 39m | 1/45-45/54 | 41-45 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL09RADERE-RAD | 33 | 17m | 0 | 33-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SARCHE-CHE | 40 | 49m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SARCHE-SAR | 58 | 51m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SINFIX-FIX | 15 | 51m | 6/18-19/517 | 15-19 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| ITFMATCH-26JUL09SINFIX-SIN | 82 | 51m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-THI | 18 | 51m | 2/21-21/3 | 18-20 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFMATCH-26JUL09TROKOI-KOI | 55 | 17m | 0 | 55-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09TROKOI-TRO | 41 | 51m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09VACBAY-VAC | 58 | 26m | 0 | 58-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09XILPOE-POE | 28 | 51m | 0 | 28-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09XILPOE-XIL | 67 | 51m | 0 | 67-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ZGIKOE-KOE | 53 | 41m | 0 | 53-54 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ZGIKOE-ZGI | 48 | 9m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LUENAT-NAT | 12 | 60m | 6/18-31/37 | 14-19 | 6 | **FLOW_ABOVE** | 19 |  |
| ITFWMATCH-26JUL09BOSGOL-GOL | 48 | 27m | 8/52-52/252 | 49-51 | 4 | **FLOW_ABOVE** | 48 | flow above but bound 48c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09BURERC-ERC | 26 | 73m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CAPCEN-CAP | 37 | 51m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CAPCEN-CEN | 60 | 51m | 0 | 60-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-BER | 71 | 25m | 4/73-75/29 | 73-75 | 2 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09CHASMI-CHA | 24 | 51m | 0 | 24-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CHASMI-SMI | 71 | 11m | 0 | 71-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CIRPAH-CIR | 77 | 11m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CIRPAH-PAH | 20 | 20m | 0 | 20-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DANHOS-DAN | 25 | 51m | 0 | 25-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DANHOS-HOS | 71 | 51m | 0 | 71-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DENKAZ-DEN | 70 | 34m | 11/72-79/82 | 77-73 | 2 | **FLOW_ABOVE** | 70 | flow above but bound 70c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09DESYOD-DES | 36 | 8m | 1/38-38/12 | 36-37 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| ITFWMATCH-26JUL09DESYOD-YOD | 62 | 8m | 2/64-64/4 | 62-63 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ITFWMATCH-26JUL09DUEYOU-DUE | 93 | 12m | 0 | 93-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09JAKAST-AST | 79 | 30m | 0 | 79-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09JAKAST-JAK | 18 | 51m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KOMPER-KOM | 28 | 73m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KORSAG-KOR | 28 | 36m | 6/30-31/308 | 28-30 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→30 |
| ITFWMATCH-26JUL09KORSAG-SAG | 69 | 15m | 4/69-73/7 | 69-72 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09KUHGAN-GAN | 53 | 15m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KUHGAN-KUH | 44 | 34m | 0 | 44-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09LOVSTR-LOV | 23 | 31m | 0 | 23-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-ALL | 74 | 28m | 1/77-77/1 | 74-77 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| ITFWMATCH-26JUL09MAIALL-MAI | 23 | 70m | 6/27-27/362 | 23-27 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ITFWMATCH-26JUL09MATDYU-DYU | 8 | 45m | 6/13-15/49 | 13-12 | 5 | **FLOW_ABOVE** | 11 | flow above but bound 11c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09PAWTEI-PAW | 79 | 70m | 1/80-80/0 | 79-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL09RYSCER-CER | 27 | 3m | 0 | 27-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09RYSCER-RYS | 71 | 3m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SAILEE-LEE | 82 | 51m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SAILEE-SAI | 15 | 49m | 0 | 15-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHIDIL-DIL | 21 | 8m | 0 | 21-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHIDIL-SHI | 77 | 51m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SPIVAN-SPI | 8 | 51m | 1/10-10/9 | 8-10 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL09SPIVAN-VAN | 90 | 51m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VANLEY-VAN | 30 | 22m | 0 | 30-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VANOZE-OZE | 38 | 51m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VANOZE-VAN | 62 | 5m | 0 | 62-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VONZID-VON | 20 | 45m | 0 | 20-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VONZID-ZID | 77 | 45m | 0 | 77-81 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL09WALROM-R | 36 | 11m | 0 | 36-37 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL09WALROM-W | 62 | 51m | 3/63-63/128 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08CHOYAM | 67 | 11 | **78** | 97 | -19 |
| ITFWMATCH-26JUL08NAKMAL | 23 | 67 | **90** | 97 | -7 |
| ITFWMATCH-26JUL08LUENAT | 78 | 19 | **97** | 97 | +0 |
| ITFWMATCH-26JUL09MATDYU | 86 | 12 | **98** | 97 | +1 |
| ITFMATCH-26JUL09BEAVAN | 52 | 47 | **99** | 97 | +2 |
| ITFWMATCH-26JUL09DENKAZ | 27 | 73 | **100** | 97 | +3 |
| ITFWMATCH-26JUL09BOSGOL | 49 | 51 | **100** | 97 | +3 |
| ITFWMATCH-26JUL09CEUBER | 26 | 75 | **101** | 97 | +4 |
| ITFMATCH-26JUL08GILOBR | 10 | 93 | **103** | 97 | +6 |

## FLOW-STATE — 66 tracked game(s) ({'OPEN': 7, 'QUIET': 1, 'WAKING': 58}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.233 | 2 | **OPEN** |
| ITFMATCH-26JUL08GILOBR | ITF_M | 0.667 | 2 | **OPEN** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 0.9 | 2 | **OPEN** |
| ITFWMATCH-26JUL09CEUBER | ITF_W | 0.567 | 2 | **OPEN** |
| ITFWMATCH-26JUL09DESYOD | ITF_W | 0.267 | 1 | **OPEN** |
| ITFWMATCH-26JUL09KORSAG | ITF_W | 0.433 | 2 | **OPEN** |
| ITFWMATCH-26JUL09MATDYU | ITF_W | 0.233 | 2 | **OPEN** |
| ITFMATCH-26JUL08MUJBEL | ITF_M | 0.0 | 29 | **QUIET** |
| ITFMATCH-26JUL09AGWMAT | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09ARCALU | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09BALGSC | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09BARTSI | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09BEAVAN | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL09BECADD | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09BERCRA | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL09BLATAL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09DUHTYA | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09ERIPHO | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09FILJED | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL09GHAGAR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09GUTROS | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09LOPKAM | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09MAKROB | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09MAZMUR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09MENROH | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL09MICRIV | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL09MILREC | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09MONBAD | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL09NASBOR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09RADERE | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09SARCHE | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL09SINFIX | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09THIJER | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL09TROKOI | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09VACBAY | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09XILPOE | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09ZGIKOE | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 32.567 | — | **WAKING** |
| ITFWMATCH-26JUL08LUENAT | ITF_W | 0.167 | 5 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 27.767 | — | **WAKING** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 13.367 | — | **WAKING** |
| ITFWMATCH-26JUL09BURERC | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09CAPCEN | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09CHASMI | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL09CIRPAH | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09DANHOS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09DENKAZ | ITF_W | 0.567 | 5 | **WAKING** |
| ITFWMATCH-26JUL09DUEYOU | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09JAKAST | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09KOMPER | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09KUHGAN | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL09LOVSTR | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09MAIALL | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 6.167 | — | **WAKING** |
| ITFWMATCH-26JUL09PAWTEI | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL09RYSCER | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09SAILEE | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 12.967 | — | **WAKING** |
| ITFWMATCH-26JUL09SHIDIL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 23.5 | — | **WAKING** |
| ITFWMATCH-26JUL09SPIVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 13.1 | — | **WAKING** |
| ITFWMATCH-26JUL09VANLEY | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09VANOZE | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09VONZID | ITF_W | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL09WALROM | WTA_CHALL | 0.067 | 1 | **WAKING** |

## PATTERNS (sub-B) — 6
- half_arm_aging: KXITFMATCH-26JUL08MUJBEL-MUJ {"fill": 39, "age_min": 75, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08NAKMAL-MAL {"fill": 23, "age_min": 70, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08LUENAT-LUE {"fill": 78, "age_min": 61, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- half_arm_aging: KXITFWMATCH-26JUL09MAMJAN-MAM {"fill": 54, "age_min": 60, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL09MATDYU-MAT {"fill": 86, "age_min": 46, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFWMATCH-26JUL09DENKAZ-KAZ {"fill": 27, "age_min": 43, "mode": "SET_BELOW_FLOW(prints 2c above)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
