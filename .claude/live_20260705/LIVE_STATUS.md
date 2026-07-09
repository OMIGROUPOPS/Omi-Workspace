# LIVE VALIDATION — rolling status

- cycle 72 @ **2026-07-09 02:32:51 AM ET** | build `04bb209` | session boot 07-09 00:36 ET | log `live_v3_20260709.jsonl` | 10020 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 00:40:05 | **combined_over_goal** | KXITFWMATCH-26JUL09SEDKRO | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 23 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:36 | ITFWMATCH-26JUL09SEDKRO-SED | ITF_W | ? | 8 | 14 | -6 (window_cell) | — | pre | pair | 98 | EARNED |
| 00:36 | ITFMATCH-26JUL08MUJBEL-MUJ | ITF_M | ? | 39 | 35 | +4 (adopted_est) | -3.0 | pre | single |  | EARNED |
| 00:40 | ITFWMATCH-26JUL09SEDKRO-KRO | ITF_W | ? | 90 | 81 | +9 (window_cell) | — | pre | pair | 98 | GIFT_CLASS |
| 00:41 | ITFWMATCH-26JUL08NAKMAL-MAL | ITF_W | ? | 23 | 18 | +5 (window_cell) | — | pre | single |  | MIXED |
| 00:48 | ITFWMATCH-26JUL09AHLMAK-AHL | ITF_W | ? | 31 | 8 | +23 (window_cell) | — | pre | pair | 97 | MIXED |
| 00:50 | ITFWMATCH-26JUL08LUENAT-LUE | ITF_W | ? | 78 | 76 | +2 (fill_est) | -14.5 | pre | pair | 90 | EARNED |
| 00:51 | ITFWMATCH-26JUL09MAMJAN-MAM | ITF_W | ? | 54 | 36 | +18 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 00:54 | ITFWMATCH-26JUL09TUPNUP-NUP | ITF_W | underdog | 9 | 4 | +5 (place_cell) | — | pre | pair | 97 | PENDING |
| 00:57 | ITFWMATCH-26JUL09TUPNUP-TUP | ITF_W | ? | 88 | 86 | +2 (fill_est) | — | pre | pair | 97 | PENDING |
| 01:05 | ITFWMATCH-26JUL09MATDYU-MAT | ITF_W | leader | 86 | 84 | +2 (place_cell) | — | pre | single |  | PENDING |
| 01:08 | ITFWMATCH-26JUL09DENKAZ-KAZ | ITF_W | underdog | 27 | 22 | +5 (place_cell) | — | pre | pair | 97 | PENDING |
| 01:09 | ITFWMATCH-26JUL09SHONIS-NIS | ITF_W | underdog | 13 | 5 | +8 (place_cell) | — | pre | pair | 97 | MIXED |
| 01:14 | ITFWMATCH-26JUL09AHLMAK-MAK | ITF_W | ? | 66 | 85 | -19 (window_cell) | — | pre | pair | 97 | MIXED |
| 01:24 | ITFWMATCH-26JUL09BOSGOL-BOS | ITF_W | ? | 49 | 45 | +4 (fill_est) | — | pre | single |  | PENDING |
| 01:24 | ITFWMATCH-26JUL08CHOYAM-YAM | ITF_W | ? | 67 | 86 | -19 (window_cell) | — | pre | single |  | MIXED |
| 01:26 | ITFWMATCH-26JUL09CEUBER-CEU | ITF_W | ? | 26 | 22 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 01:32 | ITFMATCH-26JUL09BEAVAN-BEA | ITF_M | ? | 52 | 49 | +3 (fill_est) | — | pre | single |  | PENDING |
| 01:40 | ITFMATCH-26JUL08GILOBR-GIL | ITF_M | ? | 10 | 6 | +4 (adopted_est) | 1.0 | pre | single |  | MIXED |
| 01:40 | ITFWMATCH-26JUL09SHONIS-SHO | ITF_W | ? | 84 | 86 | -2 (window_cell) | — | pre | pair | 97 | MIXED |
| 01:59 | ITFWMATCH-26JUL08LUENAT-NAT | ITF_W | underdog | 12 | 10 | +2 (place_cell) | -18.5 | pre | pair | 90 | EARNED |
| 02:04 | ITFWMATCH-26JUL09DENKAZ-DEN | ITF_W | ? | 70 | 68 | +2 (adopted_est) | — | pre | pair | 97 | PENDING |
| 02:24 | ITFWMATCH-26JUL09DESYOD-DES | ITF_W | ? | 36 | 32 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 02:25 | ITFWMATCH-26JUL09KORSAG-KOR | ITF_W | ? | 28 | 24 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 138 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 6, 'NO_FLOW': 102, 'FLOW_ABOVE': 30} | repriceable now: true 23 / false 115 | **cumulative bid_grade lines: 6332 (repriceable true 719 / false 5613)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09DANKOL-D | 58 | 1m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09DANKOL-K | 41 | 0m | 0 | 41-42 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09GAUDIA-D | 62 | 31m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09GAUDIA-G | 37 | 31m | 1/38-38/2 | 37-38 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| ATPCHALLENGERMATCH-26JUL09MONAZK-A | 19 | 32m | 2/20-20/118 | 19-20 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ATPCHALLENGERMATCH-26JUL09MONAZK-M | 80 | 31m | 0 | 80-81 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL09PLAGIL-G | 77 | 31m | 7/78-78/206 | 77-78 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ATPCHALLENGERMATCH-26JUL09PLAGIL-P | 21 | 32m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08DERMIL-DER | 71 | 116m | 24/71-76/301 | 71-74 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08GILOBR-OBR | 87 | 52m | 1/89-89/11 | 89-93 | 2 | **FLOW_ABOVE** | 87 | flow above but bound 87c < flow -- chasing breaks goal |
| ITFMATCH-26JUL09AGWMAT-AGW | 37 | 92m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09AGWMAT-MAT | 64 | 90m | 1/65-65/0 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| ITFMATCH-26JUL09ALABAR-ALA | 17 | 23m | 0 | 17-19 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ALABAR-BAR | 81 | 31m | 0 | 81-84 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ARCALU-ALU | 49 | 116m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ARCALU-ARC | 48 | 116m | 0 | 48-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BALGSC-BAL | 26 | 55m | 1/27-27/0 | 26-27 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ITFMATCH-26JUL09BARTSI-BAR | 42 | 62m | 0 | 42-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BARTSI-TSI | 56 | 53m | 2/56-56/2 | 56-57 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL09BEAVAN-VAN | 43 | 11m | 0 | 45-49 | — | **NO_FLOW** | 45 |  |
| ITFMATCH-26JUL09BECADD-ADD | 74 | 77m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BECADD-BEC | 22 | 77m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BERCRA-BER | 27 | 31m | 0 | 27-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BERCRA-CRA | 70 | 57m | 0 | 70-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BLATAL-BLA | 45 | 114m | 0 | 45-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09CLAPAA-CLA | 88 | 31m | 0 | 88-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09CLAPAA-PAA | 9 | 11m | 0 | 9-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09DOUSTE-STE | 9 | 28m | 0 | 9-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09DUHTYA-DUH | 35 | 79m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09DUHTYA-TYA | 62 | 82m | 0 | 62-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ERIPHO-ERI | 83 | 42m | 0 | 83-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ERIPHO-PHO | 13 | 42m | 0 | 13-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09FILJED-FIL | 77 | 62m | 0 | 77-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09FILJED-JED | 18 | 62m | 0 | 18-23 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GHAGAR-GAR | 35 | 92m | 0 | 35-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GHAGAR-GHA | 63 | 82m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GUTROS-GUT | 36 | 62m | 0 | 36-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GUTROS-ROS | 61 | 62m | 1/64-64/0 | 61-64 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ITFMATCH-26JUL09IAKZAP-IAK | 59 | 31m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09IAKZAP-ZAP | 39 | 31m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09JONVAS-JON | 60 | 31m | 0 | 60-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09JONVAS-VAS | 35 | 31m | 0 | 35-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09LOPKAM-LOP | 75 | 48m | 1/76-76/12 | 75-76 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| ITFMATCH-26JUL09MAKROB-MAK | 38 | 110m | 0 | 38-41 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAKROB-ROB | 58 | 116m | 0 | 58-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAZMUR-MAZ | 79 | 92m | 0 | 79-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAZMUR-MUR | 18 | 23m | 1/19-19/1 | 18-19 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ITFMATCH-26JUL09MENROH-MEN | 20 | 33m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MENROH-ROH | 78 | 92m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MICRIV-MIC | 75 | 31m | 0 | 75-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MILREC-MIL | 30 | 92m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MILREC-REC | 65 | 92m | 0 | 65-71 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MONBAD-BAD | 39 | 92m | 1/41-41/0 | 39-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→41 |
| ITFMATCH-26JUL09MONBAD-MON | 58 | 109m | 1/59-59/16 | 58-59 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFMATCH-26JUL09NASBOR-BOR | 54 | 81m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09NASBOR-NAS | 41 | 81m | 1/45-45/54 | 41-45 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL09ORLCHL-CHL | 13 | 23m | 0 | 13-16 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ORLCHL-ORL | 84 | 32m | 0 | 84-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09PLEJON-JON | 43 | 18m | 0 | 43-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09PLEJON-PLE | 54 | 31m | 0 | 54-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09RADERE-RAD | 33 | 59m | 1/37-37/0 | 33-37 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFMATCH-26JUL09SALWEI-SAL | 20 | 7m | 0 | 20-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SARCHE-CHE | 40 | 90m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SARCHE-SAR | 58 | 92m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SELFOR-FOR | 48 | 31m | 1/49-49/19 | 48-49 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→49 |
| ITFMATCH-26JUL09SHIBRO-BRO | 19 | 31m | 0 | 19-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SHIBRO-SHI | 78 | 12m | 0 | 78-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SINFIX-FIX | 15 | 92m | 6/18-19/517 | 15-19 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| ITFMATCH-26JUL09SINFIX-SIN | 82 | 92m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-JER | 81 | 22m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-THI | 18 | 93m | 5/20-21/243 | 18-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ITFMATCH-26JUL09TROKOI-KOI | 55 | 58m | 0 | 55-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09TROKOI-TRO | 41 | 92m | 0 | 41-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09VACBAY-VAC | 58 | 67m | 0 | 58-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09VELHAS-HAS | 23 | 30m | 0 | 23-26 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09VELHAS-VEL | 74 | 19m | 0 | 74-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09VIRBRA-BRA | 77 | 31m | 0 | 77-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09VIRBRA-VIR | 19 | 28m | 0 | 19-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09XILPOE-POE | 28 | 92m | 0 | 28-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09XILPOE-XIL | 67 | 92m | 0 | 67-73 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ZGIKOE-KOE | 53 | 82m | 0 | 53-54 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ZGIKOE-ZGI | 48 | 50m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09BOSGOL-GOL | 48 | 68m | 253/49-72/25198 | 70-64 | 1 | **FLOW_ABOVE** | 48 | flow above but bound 48c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09BURERC-ERC | 26 | 114m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CAPCEN-CAP | 37 | 92m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CAPCEN-CEN | 60 | 92m | 0 | 60-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-BER | 71 | 66m | 16/72-75/191 | 72-73 | 1 | **FLOW_ABOVE** | 71 | flow above but bound 71c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09CHASMI-CHA | 24 | 92m | 0 | 24-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CHASMI-SMI | 71 | 52m | 1/76-76/12 | 71-76 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL09CIRPAH-CIR | 77 | 52m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CIRPAH-PAH | 20 | 62m | 0 | 20-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DANHOS-DAN | 25 | 92m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DANHOS-HOS | 72 | 40m | 0 | 72-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DEPFOU-DEP | 13 | 31m | 0 | 13-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DEPFOU-FOU | 84 | 31m | 0 | 84-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DESYOD-YOD | 61 | 3m | 1/64-64/3 | 61-64 | 3 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09DUEYOU-DUE | 93 | 53m | 0 | 93-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09JAKAST-AST | 79 | 71m | 0 | 79-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09JAKAST-JAK | 18 | 92m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KASROJ-KAS | 13 | 31m | 0 | 13-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KASROJ-ROJ | 83 | 31m | 0 | 83-87 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KOMPER-KOM | 28 | 114m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KORSAG-SAG | 69 | 7m | 22/71-83/767 | 78-71 | 2 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09KUHGAN-GAN | 53 | 56m | 5/55-56/233 | 53-56 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFWMATCH-26JUL09KUHGAN-KUH | 46 | 12m | 1/46-46/7 | 46-48 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09KULNOE-KUL | 80 | 15m | 0 | 80-83 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KULNOE-NOE | 16 | 15m | 0 | 16-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KULSTE-KUL | 31 | 31m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KULSTE-STE | 64 | 31m | 0 | 64-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09LOVSTR-LOV | 23 | 72m | 0 | 23-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-ALL | 76 | 11m | 1/78-78/5 | 76-78 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→78 |
| ITFWMATCH-26JUL09MAIALL-MAI | 23 | 111m | 12/26-27/418 | 23-26 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→26 |
| ITFWMATCH-26JUL09MARWIE-MAR | 58 | 31m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MARWIE-WIE | 39 | 31m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MATDYU-DYU | 11 | 31m | 8/16-17/247 | 14-17 | 5 | **FLOW_ABOVE** | 11 | flow above but bound 11c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09PAQKAR-KAR | 35 | 31m | 1/35-35/375 | 35-40 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09PAQKAR-PAQ | 61 | 11m | 0 | 61-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09PAVJOR-JOR | 81 | 16m | 0 | 81-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09PAVJOR-PAV | 16 | 16m | 0 | 16-19 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09PAWTEI-PAW | 79 | 112m | 1/80-80/0 | 79-80 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL09PODVOL-POD | 66 | 16m | 0 | 66-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09PODVOL-VOL | 30 | 16m | 0 | 30-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09RYSCER-CER | 27 | 44m | 0 | 27-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09RYSCER-RYS | 71 | 44m | 1/73-73/13 | 71-74 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFWMATCH-26JUL09SAILEE-LEE | 82 | 92m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SAILEE-SAI | 15 | 91m | 0 | 15-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHIDIL-DIL | 21 | 49m | 0 | 21-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHIDIL-SHI | 77 | 92m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SPIVAN-SPI | 8 | 92m | 1/10-10/9 | 8-9 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL09SPIVAN-VAN | 90 | 92m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SRABAR-SRA | 8 | 35m | 1/8-8/5 | 8-9 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09VANLEY-VAN | 30 | 63m | 0 | 30-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VANOZE-OZE | 38 | 92m | 1/38-38/0 | 38-39 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09VANOZE-VAN | 62 | 46m | 1/64-64/0 | 62-64 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ITFWMATCH-26JUL09VONZID-VON | 20 | 87m | 0 | 20-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VONZID-ZID | 77 | 87m | 0 | 77-81 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL09WALROM-R | 36 | 52m | 2/37-37/14 | 36-37 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| WTACHALLENGERMATCH-26JUL09WALROM-W | 63 | 11m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08CHOYAM | 67 | 1 | **68** | 97 | -29 |
| ITFWMATCH-26JUL08NAKMAL | 23 | 67 | **90** | 97 | -7 |
| ITFWMATCH-26JUL09CEUBER | 26 | 73 | **99** | 97 | +2 |
| ITFWMATCH-26JUL09KORSAG | 28 | 71 | **99** | 97 | +2 |
| ITFWMATCH-26JUL09DESYOD | 36 | 64 | **100** | 97 | +3 |
| ITFMATCH-26JUL09BEAVAN | 52 | 49 | **101** | 97 | +4 |
| ITFWMATCH-26JUL09MATDYU | 86 | 17 | **103** | 97 | +6 |
| ITFMATCH-26JUL08GILOBR | 10 | 93 | **103** | 97 | +6 |
| ITFWMATCH-26JUL09BOSGOL | 49 | 64 | **113** | 97 | +16 |
| ITFWMATCH-26JUL09MAMJAN | 54 | 61 | **115** | 97 | +18 |

## FLOW-STATE — 91 tracked game(s) ({'OPEN': 15, 'WAKING': 75, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL09DANKOL | ATP_CHALL | 0.3 | 1 | **OPEN** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.3 | 3 | **OPEN** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 41.967 | 1 | **OPEN** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 12.367 | 1 | **OPEN** |
| ITFWMATCH-26JUL09CEUBER | ITF_W | 1.033 | 3 | **OPEN** |
| ITFWMATCH-26JUL09DENKAZ | ITF_W | 12.1 | 1 | **OPEN** |
| ITFWMATCH-26JUL09DESYOD | ITF_W | 0.567 | 3 | **OPEN** |
| ITFWMATCH-26JUL09KORSAG | ITF_W | 1.633 | 2 | **OPEN** |
| ITFWMATCH-26JUL09KUHGAN | ITF_W | 0.333 | 2 | **OPEN** |
| ITFWMATCH-26JUL09MAIALL | ITF_W | 0.2 | 2 | **OPEN** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 20.833 | 1 | **OPEN** |
| ITFWMATCH-26JUL09MATDYU | ITF_W | 0.333 | 3 | **OPEN** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 38.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 85.467 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL09WALROM | WTA_CHALL | 0.367 | 1 | **OPEN** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL09GAUDIA | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09MONAZK | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL09PLAGIL | ATP_CHALL | 0.233 | 1 | **WAKING** |
| ITFMATCH-26JUL08GILOBR | ITF_M | 0.133 | 3 | **WAKING** |
| ITFMATCH-26JUL08MUJBEL | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL09AGWMAT | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09ALABAR | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL09ARCALU | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09BALGSC | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09BARTSI | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09BEAVAN | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL09BECADD | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09BERCRA | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09BLATAL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09CLAPAA | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09DOUSTE | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09DUHTYA | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09ERIPHO | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09FILJED | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09GHAGAR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09GUTROS | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09IAKZAP | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09JONVAS | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09LOPKAM | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09MAKROB | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09MAZMUR | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09MENROH | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09MICRIV | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09MILREC | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09MONBAD | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09NASBOR | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09ORLCHL | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09PLEJON | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09RADERE | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL09SALWEI | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL09SARCHE | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL09SELFOR | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL09SHIBRO | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09SINFIX | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09THIJER | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL09TROKOI | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09VACBAY | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09VELHAS | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09VIRBRA | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09XILPOE | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL09ZGIKOE | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 42.267 | — | **WAKING** |
| ITFWMATCH-26JUL08LUENAT | ITF_W | 0.1 | 14 | **WAKING** |
| ITFWMATCH-26JUL09BURERC | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09CAPCEN | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09CHASMI | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL09CIRPAH | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09DANHOS | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09DEPFOU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09DUEYOU | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09JAKAST | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09KASROJ | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09KOMPER | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09KULNOE | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09KULSTE | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09LOVSTR | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09MARWIE | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09PAQKAR | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL09PAVJOR | ITF_W | 0.033 | 3 | **WAKING** |
| ITFWMATCH-26JUL09PAWTEI | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09PODVOL | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09RYSCER | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09SAILEE | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09SHIDIL | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09SPIVAN | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09SRABAR | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 5.567 | — | **WAKING** |
| ITFWMATCH-26JUL09VANLEY | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09VANOZE | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL09VONZID | ITF_W | 0.0 | 2 | **WAKING** |

## PATTERNS (sub-B) — 17
- half_arm_aging: KXITFMATCH-26JUL08MUJBEL-MUJ {"fill": 39, "age_min": 116, "mode": "PAIRING(sib never rested)"}
- pre_conception_buy: KXITFWMATCH-26JUL09AHLMAK-AHL {"price": 30, "conception_ts": 1783578602.5352056, "detail": "buy 30c predates the conception stamp by 113min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-09 02:32:51 AM ET"}
- pre_conception_buy: KXITFWMATCH-26JUL09MAMJAN-MAM {"price": 49, "conception_ts": 1783578610.680465, "detail": "buy 49c predates the conception stamp by 113min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-09 02:32:51 AM ET"}
- pre_conception_buy: KXITFWMATCH-26JUL09MAMJAN-MAM {"price": 50, "conception_ts": 1783578610.680465, "detail": "buy 50c predates the conception stamp by 112min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-09 02:32:51 AM ET"}
- pre_conception_buy: KXITFWMATCH-26JUL09MAMJAN-MAM {"price": 54, "conception_ts": 1783578610.680465, "detail": "buy 54c predates the conception stamp by 111min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-09 02:32:51 AM ET"}
- pre_conception_buy: KXITFWMATCH-26JUL09AHLMAK-AHL {"price": 31, "conception_ts": 1783578602.5352056, "detail": "buy 31c predates the conception stamp by 108min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-09 02:32:51 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL08NAKMAL-MAL {"fill": 23, "age_min": 111, "mode": "PAIRING(sib never rested)"}
- pre_conception_buy: KXITFWMATCH-26JUL09SHONIS-NIS {"price": 13, "conception_ts": 1783578601.3601265, "detail": "buy 13c predates the conception stamp by 103min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-09 02:32:51 AM ET"}
- deep_neg_fv: KXITFWMATCH-26JUL08LUENAT-LUE {"entry_minus_fv_burst": -14.5}
- half_arm_aging: KXITFWMATCH-26JUL09MAMJAN-MAM {"fill": 54, "age_min": 102, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL09MATDYU-MAT {"fill": 86, "age_min": 87, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFWMATCH-26JUL09BOSGOL-BOS {"fill": 49, "age_min": 68, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFWMATCH-26JUL08CHOYAM-YAM {"fill": 67, "age_min": 68, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL09CEUBER-CEU {"fill": 26, "age_min": 66, "mode": "SET_BELOW_FLOW(prints 1c above)"}
- half_arm_aging: KXITFMATCH-26JUL09BEAVAN-BEA {"fill": 52, "age_min": 61, "mode": "STARVATION(no prints since post)"}
- half_arm_aging: KXITFMATCH-26JUL08GILOBR-GIL {"fill": 10, "age_min": 52, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- deep_neg_fv: KXITFWMATCH-26JUL08LUENAT-NAT {"entry_minus_fv_burst": -18.5}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
