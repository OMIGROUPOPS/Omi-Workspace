# LIVE VALIDATION — rolling status

- cycle 70 @ **2026-07-09 02:12:11 AM ET** | build `6f4df32` | session boot 07-09 00:36 ET | log `live_v3_20260709.jsonl` | 8616 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 00:40:05 | **combined_over_goal** | KXITFWMATCH-26JUL09SEDKRO | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 21 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:36 | ITFWMATCH-26JUL09SEDKRO-SED | ITF_W | ? | 8 | 4 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
| 00:36 | ITFMATCH-26JUL08MUJBEL-MUJ | ITF_M | ? | 39 | 35 | +4 (adopted_est) | -3.0 | pre | single |  | EARNED |
| 00:40 | ITFWMATCH-26JUL09SEDKRO-KRO | ITF_W | ? | 90 | 88 | +2 (fill_est) | — | pre | pair | 98 | PENDING |
| 00:41 | ITFWMATCH-26JUL08NAKMAL-MAL | ITF_W | ? | 23 | 18 | +5 (window_cell) | — | pre | single |  | MIXED |
| 00:48 | ITFWMATCH-26JUL09AHLMAK-AHL | ITF_W | ? | 31 | 27 | +4 (fill_est) | — | pre | pair | 97 | PENDING |
| 00:50 | ITFWMATCH-26JUL08LUENAT-LUE | ITF_W | ? | 78 | 76 | +2 (fill_est) | -14.5 | pre | pair | 90 | EARNED |
| 00:51 | ITFWMATCH-26JUL09MAMJAN-MAM | ITF_W | ? | 54 | 52 | +2 (fill_est) | — | pre | single |  | PENDING |
| 00:54 | ITFWMATCH-26JUL09TUPNUP-NUP | ITF_W | underdog | 9 | 4 | +5 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:57 | ITFWMATCH-26JUL09TUPNUP-TUP | ITF_W | ? | 88 | 86 | +2 (fill_est) | — | pre | pair | 97 | PENDING |
| 01:05 | ITFWMATCH-26JUL09MATDYU-MAT | ITF_W | leader | 86 | 84 | +2 (place_cell) | — | pre | single |  | PENDING |
| 01:08 | ITFWMATCH-26JUL09DENKAZ-KAZ | ITF_W | underdog | 27 | 22 | +5 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:09 | ITFWMATCH-26JUL09SHONIS-NIS | ITF_W | underdog | 13 | 5 | +8 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:14 | ITFWMATCH-26JUL09AHLMAK-MAK | ITF_W | ? | 66 | 64 | +2 (fill_est) | — | pre | pair | 97 | PENDING |
| 01:24 | ITFWMATCH-26JUL09BOSGOL-BOS | ITF_W | ? | 49 | 45 | +4 (fill_est) | — | pre | single |  | PENDING |
| 01:24 | ITFWMATCH-26JUL08CHOYAM-YAM | ITF_W | ? | 67 | 86 | -19 (window_cell) | — | pre | single |  | MIXED |
| 01:26 | ITFWMATCH-26JUL09CEUBER-CEU | ITF_W | ? | 26 | 22 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 01:32 | ITFMATCH-26JUL09BEAVAN-BEA | ITF_M | ? | 52 | 49 | +3 (fill_est) | — | pre | single |  | PENDING |
| 01:40 | ITFMATCH-26JUL08GILOBR-GIL | ITF_M | ? | 10 | 6 | +4 (adopted_est) | 1.0 | pre | single |  | MIXED |
| 01:40 | ITFWMATCH-26JUL09SHONIS-SHO | ITF_W | ? | 84 | 82 | +2 (adopted_est) | — | pre | pair | 97 | PENDING |
| 01:59 | ITFWMATCH-26JUL08LUENAT-NAT | ITF_W | underdog | 12 | 10 | +2 (place_cell) | -18.5 | pre | pair | 90 | EARNED |
| 02:04 | ITFWMATCH-26JUL09DENKAZ-DEN | ITF_W | ? | 70 | 68 | +2 (adopted_est) | — | pre | pair | 97 | PENDING |

## RESTING BIDS — 131 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 28, 'NO_FLOW': 100, 'FLOW_AT_LEVEL': 3} | repriceable now: true 23 / false 108 | **cumulative bid_grade lines: 6301 (repriceable true 711 / false 5590)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09GAUDIA-D | 62 | 10m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09GAUDIA-G | 37 | 10m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09MONAZK-A | 19 | 11m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09MONAZK-M | 80 | 10m | 0 | 80-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09PLAGIL-G | 77 | 10m | 0 | 77-78 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09PLAGIL-P | 21 | 11m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 96m | 18/73-76/228 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL08GILOBR-OBR | 87 | 31m | 1/89-89/11 | 88-92 | 2 | **FLOW_ABOVE** | 87 | flow above but bound 87c < flow -- chasing breaks goal |
| ITFMATCH-26JUL09AGWMAT-AGW | 37 | 72m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09AGWMAT-MAT | 64 | 69m | 1/65-65/0 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFMATCH-26JUL09ALABAR-ALA | 17 | 2m | 0 | 17-19 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ALABAR-BAR | 81 | 10m | 0 | 81-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ARCALU-ALU | 49 | 95m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ARCALU-ARC | 48 | 95m | 0 | 48-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BALGSC-BAL | 26 | 34m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BARTSI-BAR | 42 | 41m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BARTSI-TSI | 56 | 33m | 1/56-56/1 | 56-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL09BEAVAN-VAN | 42 | 38m | 0 | 45-47 | — | **NO_FLOW** | 45 |  |
| ITFMATCH-26JUL09BECADD-ADD | 74 | 57m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BECADD-BEC | 22 | 57m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BERCRA-BER | 27 | 10m | 0 | 27-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BERCRA-CRA | 70 | 37m | 0 | 70-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BLATAL-BLA | 45 | 93m | 0 | 45-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09CLAPAA-CLA | 88 | 10m | 0 | 88-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09CLAPAA-PAA | 8 | 10m | 0 | 8-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09DOUSTE-STE | 9 | 7m | 0 | 9-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09DUHTYA-DUH | 35 | 59m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09DUHTYA-TYA | 62 | 61m | 0 | 62-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ERIPHO-ERI | 83 | 22m | 0 | 83-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ERIPHO-PHO | 13 | 22m | 0 | 13-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09FILJED-FIL | 77 | 41m | 0 | 77-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09FILJED-JED | 18 | 41m | 0 | 18-23 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GHAGAR-GAR | 35 | 71m | 0 | 35-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GHAGAR-GHA | 63 | 61m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GUTROS-GUT | 36 | 41m | 0 | 36-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GUTROS-ROS | 61 | 41m | 1/64-64/0 | 61-64 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ITFMATCH-26JUL09IAKZAP-IAK | 59 | 10m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09IAKZAP-ZAP | 39 | 10m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09JONVAS-JON | 60 | 10m | 0 | 60-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09JONVAS-VAS | 35 | 10m | 0 | 35-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09LOPKAM-LOP | 75 | 28m | 1/76-76/12 | 75-76 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| ITFMATCH-26JUL09MAKROB-MAK | 38 | 89m | 0 | 38-41 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAKROB-ROB | 58 | 95m | 0 | 58-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAZMUR-MAZ | 79 | 71m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAZMUR-MUR | 18 | 3m | 0 | 18-19 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MENROH-MEN | 20 | 13m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MENROH-ROH | 78 | 71m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MICRIV-MIC | 75 | 10m | 0 | 75-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MILREC-MIL | 30 | 72m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MILREC-REC | 65 | 72m | 0 | 65-70 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MONBAD-BAD | 39 | 71m | 1/41-41/0 | 39-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ITFMATCH-26JUL09MONBAD-MON | 58 | 89m | 1/59-59/16 | 58-59 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFMATCH-26JUL09NASBOR-BOR | 54 | 60m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09NASBOR-NAS | 41 | 60m | 1/45-45/54 | 41-45 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL09ORLCHL-CHL | 13 | 2m | 0 | 13-16 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ORLCHL-ORL | 84 | 11m | 0 | 84-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09PLEJON-JON | 42 | 10m | 0 | 42-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09PLEJON-PLE | 54 | 10m | 0 | 54-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09RADERE-RAD | 33 | 38m | 0 | 33-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SARCHE-CHE | 40 | 69m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SARCHE-SAR | 58 | 71m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SELFOR-FOR | 48 | 10m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SHIBRO-BRO | 19 | 10m | 0 | 19-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SHIBRO-SHI | 77 | 10m | 0 | 77-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SINFIX-FIX | 15 | 71m | 6/18-19/517 | 15-19 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| ITFMATCH-26JUL09SINFIX-SIN | 82 | 72m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-JER | 81 | 1m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-THI | 18 | 72m | 5/20-21/243 | 18-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL09TROKOI-KOI | 55 | 37m | 0 | 55-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09TROKOI-TRO | 41 | 71m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09VACBAY-VAC | 58 | 47m | 0 | 58-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09VELHAS-HAS | 23 | 10m | 0 | 23-26 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09VELHAS-VEL | 73 | 10m | 0 | 73-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09VIRBRA-BRA | 77 | 10m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09VIRBRA-VIR | 19 | 7m | 0 | 19-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09XILPOE-POE | 28 | 72m | 0 | 28-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09XILPOE-XIL | 67 | 72m | 0 | 67-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ZGIKOE-KOE | 53 | 61m | 0 | 53-54 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ZGIKOE-ZGI | 48 | 29m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09BOSGOL-GOL | 48 | 47m | 84/49-59/12270 | 58-51 | 1 | **FLOW_ABOVE** | 48 | flow above but bound 48c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09BURERC-ERC | 26 | 93m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CAPCEN-CAP | 37 | 71m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CAPCEN-CEN | 60 | 71m | 0 | 60-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-BER | 71 | 46m | 6/73-75/41 | 73-75 | 2 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09CHASMI-CHA | 24 | 71m | 0 | 24-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CHASMI-SMI | 71 | 31m | 1/76-76/12 | 71-76 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL09CIRPAH-CIR | 77 | 31m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CIRPAH-PAH | 20 | 41m | 0 | 20-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DANHOS-DAN | 25 | 71m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DANHOS-HOS | 72 | 19m | 0 | 72-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DEPFOU-DEP | 13 | 10m | 0 | 13-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DEPFOU-FOU | 84 | 10m | 0 | 84-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DESYOD-DES | 36 | 28m | 2/38-38/22 | 36-38 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| ITFWMATCH-26JUL09DESYOD-YOD | 62 | 28m | 8/64-64/527 | 62-64 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ITFWMATCH-26JUL09DUEYOU-DUE | 93 | 33m | 0 | 93-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09JAKAST-AST | 79 | 51m | 0 | 79-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09JAKAST-JAK | 18 | 71m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KASROJ-KAS | 13 | 10m | 0 | 13-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KASROJ-ROJ | 83 | 10m | 0 | 83-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KOMPER-KOM | 28 | 93m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KORSAG-KOR | 28 | 56m | 9/30-31/392 | 28-30 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→30 |
| ITFWMATCH-26JUL09KORSAG-SAG | 70 | 19m | 3/73-73/12 | 70-73 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFWMATCH-26JUL09KUHGAN-GAN | 53 | 36m | 1/55-55/99 | 53-56 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFWMATCH-26JUL09KUHGAN-KUH | 44 | 54m | 1/48-48/10 | 44-48 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→48 |
| ITFWMATCH-26JUL09KULSTE-KUL | 31 | 10m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KULSTE-STE | 64 | 10m | 0 | 64-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09LOVSTR-LOV | 23 | 51m | 0 | 23-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-ALL | 74 | 49m | 2/77-77/13 | 74-77 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→77 |
| ITFWMATCH-26JUL09MAIALL-MAI | 23 | 90m | 10/26-27/411 | 23-26 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFWMATCH-26JUL09MARWIE-MAR | 58 | 10m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MARWIE-WIE | 39 | 10m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MATDYU-DYU | 11 | 10m | 2/16-16/28 | 14-16 | 5 | **FLOW_ABOVE** | 11 | flow above but bound 11c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09PAQKAR-KAR | 35 | 10m | 1/35-35/375 | 35-40 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09PAQKAR-PAQ | 60 | 10m | 0 | 60-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09PAWTEI-PAW | 79 | 91m | 1/80-80/0 | 79-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL09RYSCER-CER | 27 | 23m | 0 | 27-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09RYSCER-RYS | 71 | 23m | 1/73-73/13 | 71-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFWMATCH-26JUL09SAILEE-LEE | 82 | 71m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SAILEE-SAI | 15 | 70m | 0 | 15-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHIDIL-DIL | 21 | 28m | 0 | 21-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHIDIL-SHI | 77 | 71m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SPIVAN-SPI | 8 | 71m | 1/10-10/9 | 8-10 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL09SPIVAN-VAN | 90 | 71m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SRABAR-SRA | 8 | 14m | 0 | 8-9 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VANLEY-VAN | 30 | 43m | 0 | 30-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VANOZE-OZE | 38 | 71m | 1/38-38/0 | 38-39 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09VANOZE-VAN | 62 | 25m | 1/64-64/0 | 62-64 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ITFWMATCH-26JUL09VONZID-VON | 20 | 66m | 0 | 20-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VONZID-ZID | 77 | 66m | 0 | 77-81 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL09WALROM-R | 36 | 31m | 2/37-37/14 | 36-37 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| WTACHALLENGERMATCH-26JUL09WALROM-W | 62 | 72m | 6/63-63/271 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08CHOYAM | 67 | 4 | **71** | 97 | -26 |
| ITFWMATCH-26JUL08NAKMAL | 23 | 67 | **90** | 97 | -7 |
| ITFMATCH-26JUL09BEAVAN | 52 | 47 | **99** | 97 | +2 |
| ITFWMATCH-26JUL09BOSGOL | 49 | 51 | **100** | 97 | +3 |
| ITFWMATCH-26JUL09CEUBER | 26 | 75 | **101** | 97 | +4 |
| ITFWMATCH-26JUL09MATDYU | 86 | 16 | **102** | 97 | +5 |
| ITFMATCH-26JUL08GILOBR | 10 | 92 | **102** | 97 | +5 |

## FLOW-STATE — 86 tracked game(s) ({'WAKING': 77, 'OPEN': 9}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.4 | 2 | **OPEN** |
| ITFMATCH-26JUL09THIJER | ITF_M | 0.3 | 2 | **OPEN** |
| ITFWMATCH-26JUL08LUENAT | ITF_W | 1.2 | 3 | **OPEN** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 3.933 | 1 | **OPEN** |
| ITFWMATCH-26JUL09CEUBER | ITF_W | 0.267 | 2 | **OPEN** |
| ITFWMATCH-26JUL09DESYOD | ITF_W | 0.333 | 2 | **OPEN** |
| ITFWMATCH-26JUL09KORSAG | ITF_W | 0.4 | 2 | **OPEN** |
| ITFWMATCH-26JUL09MAIALL | ITF_W | 0.2 | 3 | **OPEN** |
| ITFWMATCH-26JUL09MATDYU | ITF_W | 0.533 | 2 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL09GAUDIA | ATP_CHALL | 0.233 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09MONAZK | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09PLAGIL | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL08GILOBR | ITF_M | 0.133 | 3 | **WAKING** |
| ITFMATCH-26JUL08MUJBEL | ITF_M | 0.3 | 20 | **WAKING** |
| ITFMATCH-26JUL09AGWMAT | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09ALABAR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL09ARCALU | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09BALGSC | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09BARTSI | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09BEAVAN | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09BECADD | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09BERCRA | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL09BLATAL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09CLAPAA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09DOUSTE | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09DUHTYA | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09ERIPHO | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09FILJED | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09GHAGAR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09GUTROS | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09IAKZAP | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09JONVAS | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09LOPKAM | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09MAKROB | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09MAZMUR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09MENROH | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09MICRIV | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09MILREC | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09MONBAD | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09NASBOR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09ORLCHL | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09PLEJON | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09RADERE | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09SARCHE | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL09SELFOR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09SHIBRO | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09SINFIX | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09TROKOI | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09VACBAY | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09VELHAS | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09VIRBRA | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09XILPOE | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL09ZGIKOE | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 94.033 | — | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 15.767 | — | **WAKING** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 42.0 | — | **WAKING** |
| ITFWMATCH-26JUL09BURERC | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09CAPCEN | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09CHASMI | ITF_W | 0.033 | 5 | **WAKING** |
| ITFWMATCH-26JUL09CIRPAH | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09DANHOS | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09DENKAZ | ITF_W | 4.167 | — | **WAKING** |
| ITFWMATCH-26JUL09DEPFOU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09DUEYOU | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09JAKAST | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09KASROJ | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09KOMPER | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09KUHGAN | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL09KULSTE | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09LOVSTR | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 16.967 | — | **WAKING** |
| ITFWMATCH-26JUL09MARWIE | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09PAQKAR | ITF_W | 0.033 | 5 | **WAKING** |
| ITFWMATCH-26JUL09PAWTEI | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL09RYSCER | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL09SAILEE | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 34.533 | — | **WAKING** |
| ITFWMATCH-26JUL09SHIDIL | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 95.767 | — | **WAKING** |
| ITFWMATCH-26JUL09SPIVAN | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09SRABAR | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 24.633 | — | **WAKING** |
| ITFWMATCH-26JUL09VANLEY | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09VANOZE | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL09VONZID | ITF_W | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL09WALROM | WTA_CHALL | 0.2 | 1 | **WAKING** |

## PATTERNS (sub-B) — 11
- half_arm_aging: KXITFMATCH-26JUL08MUJBEL-MUJ {"fill": 39, "age_min": 96, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08NAKMAL-MAL {"fill": 23, "age_min": 90, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXITFWMATCH-26JUL08LUENAT-LUE {"entry_minus_fv_burst": -14.5, "emitted_et": "2026-07-09 02:12:11 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL09MAMJAN-MAM {"fill": 54, "age_min": 81, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL09MATDYU-MAT {"fill": 86, "age_min": 67, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFWMATCH-26JUL09BOSGOL-BOS {"fill": 49, "age_min": 47, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL08CHOYAM-YAM {"fill": 67, "age_min": 47, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL09CEUBER-CEU {"fill": 26, "age_min": 46, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFMATCH-26JUL09BEAVAN-BEA {"fill": 52, "age_min": 40, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-09 02:12:11 AM ET"}
- half_arm_aging: KXITFMATCH-26JUL08GILOBR-GIL {"fill": 10, "age_min": 31, "mode": "SET_BELOW_FLOW(prints 2c above)", "emitted_et": "2026-07-09 02:12:11 AM ET"}
- deep_neg_fv: KXITFWMATCH-26JUL08LUENAT-NAT {"entry_minus_fv_burst": -18.5, "emitted_et": "2026-07-09 02:12:11 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
