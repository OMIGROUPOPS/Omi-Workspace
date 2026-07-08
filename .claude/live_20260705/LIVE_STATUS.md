# LIVE VALIDATION — rolling status

- cycle 196 @ **2026-07-08 01:19:56 AM ET** | build `2313243` | session boot 07-07 23:56 ET | log `live_v3_20260707.jsonl` | 61576 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 25 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:56 | ITFWMATCH-26JUL07LIURUO-RUO | ITF_W | ? | 23 | 23 | +0 (window_cell) | — | pre | pair | 98 | EARNED |
| 23:56 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 87 | 91 | -4 (window_cell) | — | pre | single |  | MIXED |
| 23:57 | ITFMATCH-26JUL07YAMNAK-NAK | ITF_M | ? | 7 | 3 | +4 (fill_est) | — | pre | single |  | PENDING |
| 23:58 | ITFMATCH-26JUL07BORZEN-BOR | ITF_M | ? | 53 | 91 | -38 (window_cell) | — | pre | single |  | MIXED |
| 00:03 | ITFMATCH-26JUL08HARBEA-BEA | ITF_M | leader | 91 | 86 | +5 (place_cell) | — | pre | single |  | PENDING |
| 00:08 | ITFWMATCH-26JUL07CHOCAO-CHO | ITF_W | ? | 50 | 26 | +24 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 00:08 | ITFWMATCH-26JUL07GURKAL-GUR | ITF_W | ? | 32 | 23 | +9 (window_cell) | — | pre | single |  | MIXED |
| 00:19 | ITFMATCH-26JUL07YAMTAN-TAN | ITF_M | ? | 82 | 79 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 00:25 | ITFWMATCH-26JUL08NAKZHA-ZHA | ITF_W | ? | 15 | 11 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 00:25 | ITFMATCH-26JUL07YAMTAN-YAM | ITF_M | ? | 15 | 11 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 00:27 | ITFWMATCH-26JUL07LIURUO-LIU | ITF_W | ? | 75 | 73 | +2 (window_cell) | — | pre | pair | 98 | GIFT_CLASS |
| 00:27 | ITFWMATCH-26JUL08LIUMAL-MAL | ITF_W | ? | 72 | 70 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 00:42 | ITFMATCH-26JUL08KUNMEN-MEN | ITF_M | leader | 65 | 61 | +4 (place_cell) | — | pre | single |  | PENDING |
| 00:44 | ITFMATCH-26JUL08SAKVAN-SAK | ITF_M | ? | 27 | 23 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 00:44 | ITFMATCH-26JUL08STERAD-RAD | ITF_M | underdog | 34 | 30 | +4 (place_cell) | — | pre | single |  | PENDING |
| 00:46 | ITFMATCH-26JUL08ZHAISH-ZHA | ITF_M | ? | 86 | 83 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 00:50 | ITFWMATCH-26JUL08NONYUA-YUA | ITF_W | ? | 83 | 81 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 00:54 | ITFMATCH-26JUL08LIUSHI-LIU | ITF_M | ? | 75 | 72 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 00:54 | ITFWMATCH-26JUL08MAMBEL-BEL | ITF_W | ? | 12 | 8 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 00:55 | ITFMATCH-26JUL08SERROS-ROS | ITF_M | leader | 54 | 48 | +6 (place_cell) | — | pre | single |  | PENDING |
| 01:03 | ITFWMATCH-26JUL08IUSSAG-SAG | ITF_W | ? | 31 | 27 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 01:05 | ITFMATCH-26JUL07MOXSAR-SAR | ITF_M | ? | 27 | 28 | -1 (window_cell) | — | pre | single |  | EARNED |
| 01:11 | ITFWMATCH-26JUL08WANOHX-WAN | ITF_W | ? | 79 | 77 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 01:12 | ITFWMATCH-26JUL08TUPPAN-TUP | ITF_W | ? | 83 | 81 | +2 (fill_est) | — | pre | single |  | PENDING |
| 01:16 | ITFWMATCH-26JUL08IUSSAG-IUS | ITF_W | ? | 66 | 64 | +2 (adopted_est) | — | pre | pair | 97 | PENDING |

## RESTING BIDS — 102 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 22, 'NO_FLOW': 78, 'FLOW_AT_LEVEL': 2} | repriceable now: true 17 / false 85 | **cumulative bid_grade lines: 5481 (repriceable true 531 / false 4950)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07OKIMAT-MAT | 44 | 7m | 176/66-73/8283 | 81-54 | 22 | **FLOW_ABOVE** | 70 |  |
| ITFMATCH-26JUL08BALKAS-BAL | 78 | 69m | 0 | 78-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BALKAS-KAS | 18 | 69m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BERKUM-BER | 63 | 79m | 0 | 63-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BERKUM-KUM | 34 | 79m | 1/37-37/2 | 34-37 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFMATCH-26JUL08BONWEI-BON | 8 | 19m | 0 | 8-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BONWEI-WEI | 88 | 19m | 0 | 88-92 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BRAWYG-BRA | 85 | 79m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BRAWYG-WYG | 11 | 79m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08CARERE-CAR | 6 | 79m | 0 | 6-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08CARERE-ERE | 90 | 19m | 0 | 90-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08DEDPOE-DED | 45 | 14m | 0 | 45-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08DEDPOE-POE | 51 | 12m | 0 | 51-54 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08GHAGEN-GEN | 34 | 83m | 1/38-38/2 | 34-37 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| ITFMATCH-26JUL08GHAGEN-GHA | 64 | 76m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08HARBEA-HAR | 6 | 76m | 1/11-11/8 | 8-11 | 5 | **FLOW_ABOVE** | 6 | flow above but bound 6c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08HOPFIX-FIX | 39 | 16m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08HOPFIX-HOP | 58 | 19m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KAMDEC-DEC | 90 | 49m | 0 | 90-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KAMDEC-KAM | 7 | 49m | 0 | 7-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KIRVAN-KIR | 86 | 49m | 0 | 86-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KIRVAN-VAN | 11 | 49m | 1/11-11/11 | 11-13 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08LAZADD-ADD | 82 | 79m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAZADD-LAZ | 14 | 74m | 0 | 14-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MINFAB-FAB | 48 | 14m | 0 | 48-53 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MINFAB-MIN | 48 | 14m | 0 | 48-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MURGUN-GUN | 91 | 46m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MURGUN-MUR | 5 | 49m | 0 | 5-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PELDUH-PEL | 74 | 83m | 1/76-76/5 | 74-76 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| ITFMATCH-26JUL08PERVAN-PER | 54 | 49m | 0 | 54-58 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PERVAN-VAN | 42 | 37m | 0 | 42-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SERROS-SER | 42 | 24m | 0 | 45-47 | — | **NO_FLOW** | 43 |  |
| ITFMATCH-26JUL08SHAMAT-MAT | 66 | 18m | 0 | 66-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHAMAT-SHA | 31 | 14m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-SHI | 61 | 83m | 1/66-66/3 | 61-65 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-VUJ | 35 | 37m | 0 | 35-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SPIBER-BER | 53 | 18m | 0 | 53-58 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SPIBER-SPI | 43 | 19m | 0 | 43-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STEGSC-GSC | 85 | 79m | 0 | 85-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STEGSC-STE | 14 | 79m | 0 | 14-16 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08THIAND-AND | 38 | 41m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08THIAND-THI | 60 | 20m | 1/63-63/2 | 60-62 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→63 |
| ITFMATCH-26JUL08TYAGAR-GAR | 36 | 40m | 1/37-37/7 | 36-37 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFMATCH-26JUL08TYAGAR-TYA | 61 | 49m | 1/64-64/0 | 61-64 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→64 |
| ITFMATCH-26JUL08XILSTR-STR | 7 | 19m | 0 | 7-10 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08XILSTR-XIL | 90 | 19m | 0 | 90-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07WEISUN-SUN | 18 | 83m | 2343/23-99/188962 | 99-25 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08CIRBRE-BRE | 11 | 83m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08DEPGAR-DEP | 54 | 1m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08DEPGAR-GAR | 45 | 38m | 0 | 45-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08DILSAV-SAV | 39 | 40m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ERCLEM-ERC | 34 | 39m | 0 | 34-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ERCLEM-LEM | 63 | 49m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-GIO | 31 | 83m | 1/34-34/8 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL08ILIPOP-ILI | 23 | 49m | 0 | 23-28 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08KNUSHI-KNU | 40 | 39m | 0 | 40-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08KNUSHI-SHI | 56 | 49m | 0 | 56-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LACTOM-TOM | 83 | 17m | 0 | 83-86 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LIXYAM-YAM | 90 | 42m | 1/92-92/1 | 90-92 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFWMATCH-26JUL08LUENAT-LUE | 53 | 43m | 0 | 53-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LUENAT-NAT | 41 | 39m | 0 | 41-46 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MANKAV-MAN | 94 | 83m | 0 | 94-97 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MILEZZ-EZZ | 56 | 49m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MILMIS-MIL | 5 | 49m | 0 | 5-8 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MILMIS-MIS | 92 | 49m | 0 | 92-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MIXKRU-MIX | 38 | 43m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NEWCOU-COU | 35 | 31m | 0 | 35-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NEWCOU-NEW | 60 | 49m | 0 | 60-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAPCAP-CAP | 51 | 79m | 0 | 51-54 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAPCAP-PAP | 46 | 79m | 1/47-47/2 | 46-47 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFWMATCH-26JUL08PAVAGR-PAV | 91 | 48m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAWLAZ-LAZ | 21 | 44m | 0 | 21-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAWLAZ-PAW | 74 | 49m | 0 | 74-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PRIVON-PRI | 37 | 78m | 1/39-39/2 | 37-39 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL08PRIVON-VON | 60 | 18m | 0 | 60-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08REVHRU-HRU | 92 | 19m | 0 | 92-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ROSPAR-ROS | 47 | 83m | 1/50-50/1 | 47-50 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL08RYSTRA-RYS | 90 | 48m | 0 | 90-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RYSTRA-TRA | 7 | 17m | 0 | 7-10 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHOSUV-SHO | 52 | 83m | 7/74-76/131 | 72-74 | 22 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08SOLRAS-RAS | 41 | 39m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SOLRAS-SOL | 54 | 49m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TRICEN-CEN | 91 | 11m | 0 | 91-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TRICEN-TRI | 8 | 44m | 0 | 8-10 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08VANWON-VAN | 44 | 83m | 1/47-47/2 | 44-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFWMATCH-26JUL08VANWON-WON | 53 | 83m | 0 | 53-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08VOSLEY-LEY | 94 | 19m | 0 | 94-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WIEORT-ORT | 21 | 49m | 0 | 21-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WIEORT-WIE | 74 | 49m | 0 | 74-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08YESGAN-GAN | 45 | 19m | 0 | 45-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08YODKEN-KEN | 17 | 49m | 0 | 17-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08YODKEN-YOD | 78 | 23m | 0 | 78-82 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08BULROM-B | 20 | 19m | 0 | 20-21 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08BULROM-R | 78 | 19m | 1/80-80/2 | 78-79 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| WTACHALLENGERMATCH-26JUL08JONJEA-J | 47 | 19m | 0 | 48-51 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08JONJEA-J | 50 | 19m | 1/52-52/617 | 51-52 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| WTACHALLENGERMATCH-26JUL08KRAHEN-H | 24 | 19m | 0 | 24-25 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08KRAHEN-K | 73 | 19m | 2/74-74/9 | 73-74 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→74 |
| WTACHALLENGERMATCH-26JUL08MASCUR-C | 26 | 19m | 0 | 26-28 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08MASCUR-M | 71 | 19m | 2/73-73/5 | 71-73 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| WTACHALLENGERMATCH-26JUL08RADPUT-P | 66 | 19m | 8/66-67/2612 | 66-67 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTACHALLENGERMATCH-26JUL08RADPUT-R | 33 | 19m | 6/34-34/108 | 33-34 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07BORZEN | 53 | 1 | **54** | 97 | -43 |
| ITFWMATCH-26JUL07CHOCAO | 50 | 31 | **81** | 97 | -16 |
| ITFMATCH-26JUL07DELKOY | 87 | 1 | **88** | 97 | -9 |
| ITFWMATCH-26JUL07GURKAL | 32 | 60 | **92** | 97 | -5 |
| ITFMATCH-26JUL07MOXSAR | 27 | 68 | **95** | 97 | -2 |
| ITFMATCH-26JUL08SERROS | 54 | 47 | **101** | 97 | +4 |
| ITFMATCH-26JUL08HARBEA | 91 | 11 | **102** | 97 | +5 |

## PATTERNS (sub-B) — 13
- half_arm_aging: KXITFMATCH-26JUL07DELKOY-DEL {"fill": 87, "age_min": 83, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07YAMNAK-NAK {"fill": 7, "age_min": 83, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07BORZEN-BOR {"fill": 53, "age_min": 81, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08HARBEA-BEA {"fill": 91, "age_min": 76, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFWMATCH-26JUL07CHOCAO-CHO {"fill": 50, "age_min": 72, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07GURKAL-GUR {"fill": 32, "age_min": 72, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08NAKZHA-ZHA {"fill": 15, "age_min": 54, "mode": "PAIRING(sib never rested)"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFWMATCH-26JUL07LIURUO {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXITFWMATCH-26JUL08LIUMAL-MAL {"fill": 72, "age_min": 52, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08KUNMEN-MEN {"fill": 65, "age_min": 37, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 01:19:56 AM ET"}
- half_arm_aging: KXITFMATCH-26JUL08SAKVAN-SAK {"fill": 27, "age_min": 35, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 01:19:56 AM ET"}
- half_arm_aging: KXITFMATCH-26JUL08STERAD-RAD {"fill": 34, "age_min": 35, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-08 01:19:56 AM ET"}
- half_arm_aging: KXITFMATCH-26JUL08ZHAISH-ZHA {"fill": 86, "age_min": 34, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 01:19:56 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
