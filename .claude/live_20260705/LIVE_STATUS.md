# LIVE VALIDATION — rolling status

- cycle 65 @ **2026-07-09 01:21:10 AM ET** | build `5a331a0` | session boot 07-09 00:36 ET | log `live_v3_20260709.jsonl` | 5095 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 00:40:05 | **combined_over_goal** | KXITFWMATCH-26JUL09SEDKRO | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 13 graded (session)
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
| 01:09 | ITFWMATCH-26JUL09SHONIS-NIS | ITF_W | underdog | 13 | 5 | +8 (place_cell) | — | pre | single |  | PENDING |
| 01:14 | ITFWMATCH-26JUL09AHLMAK-MAK | ITF_W | ? | 66 | 64 | +2 (fill_est) | — | pre | pair | 97 | PENDING |

## RESTING BIDS — 75 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 17, 'NO_FLOW': 57, 'FLOW_AT_LEVEL': 1} | repriceable now: true 13 / false 62 | **cumulative bid_grade lines: 6197 (repriceable true 694 / false 5503)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL08DERMIL-DER | 71 | 45m | 3/73-75/12 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL09AGWMAT-AGW | 37 | 21m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09AGWMAT-MAT | 64 | 19m | 0 | 64-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ARCALU-ALU | 49 | 44m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ARCALU-ARC | 48 | 45m | 0 | 48-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BEAVAN-BEA | 52 | 11m | 1/52-52/1 | 52-53 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL09BEAVAN-VAN | 46 | 40m | 4/47-47/217 | 46-47 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL09BECADD-ADD | 74 | 6m | 0 | 74-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BECADD-BEC | 22 | 6m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BERCRA-BER | 26 | 6m | 0 | 26-30 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BERCRA-CRA | 69 | 6m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BLATAL-BLA | 45 | 42m | 0 | 45-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09DUHTYA-DUH | 35 | 8m | 0 | 35-36 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09DUHTYA-TYA | 62 | 10m | 0 | 62-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GHAGAR-GAR | 35 | 21m | 0 | 35-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09GHAGAR-GHA | 63 | 10m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAKROB-MAK | 38 | 39m | 0 | 38-41 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAKROB-ROB | 58 | 44m | 0 | 58-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAZMUR-MAZ | 79 | 20m | 0 | 79-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MENROH-MEN | 19 | 21m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MENROH-ROH | 78 | 21m | 0 | 78-81 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MICRIV-MIC | 73 | 1m | 0 | 73-77 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MILREC-MIL | 30 | 21m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MILREC-REC | 65 | 21m | 0 | 65-70 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MONBAD-BAD | 39 | 21m | 0 | 39-41 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MONBAD-MON | 58 | 38m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09NASBOR-BOR | 54 | 9m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09NASBOR-NAS | 41 | 9m | 1/45-45/54 | 41-45 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→45 |
| ITFMATCH-26JUL09SARCHE-CHE | 40 | 19m | 0 | 40-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SARCHE-SAR | 58 | 21m | 0 | 58-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09SINFIX-FIX | 15 | 20m | 6/18-19/517 | 15-19 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→18 |
| ITFMATCH-26JUL09SINFIX-SIN | 82 | 21m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09THIJER-THI | 18 | 21m | 2/21-21/3 | 18-20 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFMATCH-26JUL09TROKOI-KOI | 54 | 21m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09TROKOI-TRO | 41 | 21m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09VACBAY-VAC | 56 | 10m | 2/61-61/72 | 56-61 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL09XILPOE-POE | 28 | 21m | 0 | 28-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09XILPOE-XIL | 67 | 21m | 0 | 67-72 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ZGIKOE-KOE | 53 | 10m | 0 | 53-54 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 45m | 464/74-89/31956 | 87-75 | 7 | **FLOW_ABOVE** | 86 |  |
| ITFWMATCH-26JUL08LUENAT-NAT | 12 | 30m | 2/18-19/22 | 15-18 | 6 | **FLOW_ABOVE** | 19 |  |
| ITFWMATCH-26JUL09BOSGOL-BOS | 49 | 5m | 1/52-52/18 | 49-52 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ITFWMATCH-26JUL09BOSGOL-GOL | 49 | 42m | 6/51-51/594 | 49-51 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| ITFWMATCH-26JUL09BURERC-ERC | 26 | 42m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CAPCEN-CAP | 37 | 20m | 0 | 37-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CAPCEN-CEN | 60 | 20m | 0 | 60-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-BER | 73 | 42m | 1/75-75/14 | 73-75 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| ITFWMATCH-26JUL09CEUBER-CEU | 26 | 11m | 0 | 26-28 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CHASMI-CHA | 24 | 20m | 0 | 24-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CHASMI-SMI | 70 | 20m | 0 | 70-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DANHOS-DAN | 25 | 20m | 0 | 25-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DANHOS-HOS | 71 | 20m | 0 | 71-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DENKAZ-DEN | 70 | 4m | 0 | 71-73 | — | **NO_FLOW** | 70 |  |
| ITFWMATCH-26JUL09DUEYOU-DUE | 92 | 4m | 0 | 92-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09JAKAST-AST | 77 | 20m | 0 | 77-81 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09JAKAST-JAK | 18 | 20m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KOMPER-KOM | 28 | 42m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KORSAG-KOR | 28 | 5m | 1/30-30/6 | 28-30 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→30 |
| ITFWMATCH-26JUL09KUHGAN-KUH | 44 | 4m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09LOVSTR-LOV | 23 | 1m | 0 | 23-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-MAI | 23 | 40m | 6/27-27/362 | 23-27 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ITFWMATCH-26JUL09MATDYU-DYU | 8 | 14m | 3/13-13/33 | 12-12 | 5 | **FLOW_ABOVE** | 11 | flow above but bound 11c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL09PAWTEI-PAW | 79 | 40m | 0 | 79-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SAILEE-LEE | 82 | 20m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SAILEE-SAI | 15 | 19m | 0 | 15-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHIDIL-DIL | 20 | 20m | 0 | 20-23 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHIDIL-SHI | 77 | 20m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-SHO | 83 | 26m | 8/86-86/47 | 83-85 | 3 | **FLOW_ABOVE** | 84 | REPRICEABLE→84 |
| ITFWMATCH-26JUL09SPIVAN-SPI | 8 | 20m | 1/10-10/9 | 8-10 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFWMATCH-26JUL09SPIVAN-VAN | 90 | 20m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VANOZE-OZE | 38 | 20m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VANOZE-VAN | 61 | 12m | 0 | 61-62 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VONZID-VON | 20 | 15m | 0 | 20-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09VONZID-ZID | 77 | 15m | 0 | 77-81 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL09WALROM-W | 62 | 21m | 1/63-63/124 | 62-63 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08NAKMAL | 23 | 67 | **90** | 97 | -7 |
| ITFWMATCH-26JUL08LUENAT | 78 | 18 | **96** | 97 | -1 |
| ITFWMATCH-26JUL09MATDYU | 86 | 12 | **98** | 97 | +1 |
| ITFWMATCH-26JUL09SHONIS | 13 | 85 | **98** | 97 | +1 |
| ITFWMATCH-26JUL09DENKAZ | 27 | 73 | **100** | 97 | +3 |

## FLOW-STATE — 54 tracked game(s) ({'WAKING': 42, 'OPEN': 12}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL09BEAVAN | ITF_M | 0.233 | 1 | **OPEN** |
| ITFMATCH-26JUL09SINFIX | ITF_M | 0.2 | 3 | **OPEN** |
| ITFMATCH-26JUL09THIJER | ITF_M | 0.233 | 2 | **OPEN** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.9 | 2 | **OPEN** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 0.233 | 2 | **OPEN** |
| ITFWMATCH-26JUL09CEUBER | ITF_W | 0.267 | 2 | **OPEN** |
| ITFWMATCH-26JUL09DENKAZ | ITF_W | 0.667 | 2 | **OPEN** |
| ITFWMATCH-26JUL09MATDYU | ITF_W | 1.033 | 1 | **OPEN** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 1.967 | 3 | **OPEN** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 1.033 | 2 | **OPEN** |
| ITFWMATCH-26JUL09SPIVAN | ITF_W | 0.267 | 2 | **OPEN** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 7.333 | 2 | **OPEN** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL08MUJBEL | ITF_M | 0.7 | 35 | **WAKING** |
| ITFMATCH-26JUL09AGWMAT | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09ARCALU | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09BECADD | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09BERCRA | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09BLATAL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09DUHTYA | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09GHAGAR | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09MAKROB | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09MAZMUR | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09MENROH | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL09MICRIV | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09MILREC | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09MONBAD | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09NASBOR | ITF_M | 0.033 | 4 | **WAKING** |
| ITFMATCH-26JUL09SARCHE | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL09TROKOI | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09VACBAY | ITF_M | 0.067 | 5 | **WAKING** |
| ITFMATCH-26JUL09XILPOE | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09ZGIKOE | ITF_M | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 11.233 | — | **WAKING** |
| ITFWMATCH-26JUL08LUENAT | ITF_W | 0.067 | 3 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 24.3 | — | **WAKING** |
| ITFWMATCH-26JUL09BURERC | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09CAPCEN | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09CHASMI | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL09DANHOS | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09DUEYOU | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09JAKAST | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09KOMPER | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09KORSAG | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL09KUHGAN | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL09LOVSTR | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09MAIALL | ITF_W | 0.2 | 4 | **WAKING** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 2.667 | — | **WAKING** |
| ITFWMATCH-26JUL09PAWTEI | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09SAILEE | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09SHIDIL | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL09VANOZE | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL09VONZID | ITF_W | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL09WALROM | WTA_CHALL | 0.033 | 1 | **WAKING** |

## PATTERNS (sub-B) — 4
- half_arm_aging: KXITFMATCH-26JUL08MUJBEL-MUJ {"fill": 39, "age_min": 45, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08NAKMAL-MAL {"fill": 23, "age_min": 39, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08LUENAT-LUE {"fill": 78, "age_min": 31, "mode": "SET_BELOW_FLOW(prints 6c above)"}
- half_arm_aging: KXITFWMATCH-26JUL09MAMJAN-MAM {"fill": 54, "age_min": 30, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-09 01:21:10 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
