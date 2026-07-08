# LIVE VALIDATION — rolling status

- cycle 194 @ **2026-07-08 12:59:00 AM ET** | build `90ecc53` | session boot 07-07 23:56 ET | log `live_v3_20260707.jsonl` | 51744 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 20 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:56 | ITFWMATCH-26JUL07LIURUO-RUO | ITF_W | ? | 23 | 19 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
| 23:56 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 87 | 91 | -4 (window_cell) | — | pre | single |  | MIXED |
| 23:57 | ITFMATCH-26JUL07YAMNAK-NAK | ITF_M | ? | 7 | 3 | +4 (fill_est) | — | pre | single |  | PENDING |
| 23:58 | ITFMATCH-26JUL07BORZEN-BOR | ITF_M | ? | 53 | 50 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 00:03 | ITFMATCH-26JUL08HARBEA-BEA | ITF_M | leader | 91 | 86 | +5 (place_cell) | — | pre | single |  | PENDING |
| 00:08 | ITFWMATCH-26JUL07CHOCAO-CHO | ITF_W | ? | 50 | 48 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 00:08 | ITFWMATCH-26JUL07GURKAL-GUR | ITF_W | ? | 32 | 28 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 00:19 | ITFMATCH-26JUL07YAMTAN-TAN | ITF_M | ? | 82 | 79 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 00:25 | ITFWMATCH-26JUL08NAKZHA-ZHA | ITF_W | ? | 15 | 11 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 00:25 | ITFMATCH-26JUL07YAMTAN-YAM | ITF_M | ? | 15 | 11 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 00:27 | ITFWMATCH-26JUL07LIURUO-LIU | ITF_W | ? | 75 | 73 | +2 (adopted_est) | — | pre | pair | 98 | PENDING |
| 00:27 | ITFWMATCH-26JUL08LIUMAL-MAL | ITF_W | ? | 72 | 70 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 00:42 | ITFMATCH-26JUL08KUNMEN-MEN | ITF_M | leader | 65 | 61 | +4 (place_cell) | — | pre | single |  | PENDING |
| 00:44 | ITFMATCH-26JUL08SAKVAN-SAK | ITF_M | ? | 27 | 23 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 00:44 | ITFMATCH-26JUL08STERAD-RAD | ITF_M | underdog | 34 | 30 | +4 (place_cell) | — | pre | single |  | PENDING |
| 00:46 | ITFMATCH-26JUL08ZHAISH-ZHA | ITF_M | ? | 86 | 83 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 00:50 | ITFWMATCH-26JUL08NONYUA-YUA | ITF_W | ? | 83 | 81 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 00:54 | ITFMATCH-26JUL08LIUSHI-LIU | ITF_M | ? | 75 | 72 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 00:54 | ITFWMATCH-26JUL08MAMBEL-BEL | ITF_W | ? | 12 | 8 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 00:55 | ITFMATCH-26JUL08SERROS-ROS | ITF_M | leader | 54 | 48 | +6 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 78 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 15, 'NO_FLOW': 62, 'FLOW_AT_LEVEL': 1} | repriceable now: true 9 / false 69 | **cumulative bid_grade lines: 5440 (repriceable true 523 / false 4917)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07OKIMAT-MAT | 44 | 62m | 1182/55-84/81129 | 79-59 | 11 | **FLOW_ABOVE** | 70 |  |
| ITFMATCH-26JUL08BALKAS-BAL | 78 | 48m | 0 | 78-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BALKAS-KAS | 18 | 48m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BERKUM-BER | 63 | 58m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BERKUM-KUM | 34 | 58m | 1/37-37/2 | 34-37 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFMATCH-26JUL08BRAWYG-BRA | 85 | 58m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BRAWYG-WYG | 11 | 58m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08CARERE-CAR | 6 | 58m | 0 | 6-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08CARERE-ERE | 89 | 52m | 0 | 89-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08GHAGEN-GEN | 34 | 62m | 1/38-38/2 | 34-37 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| ITFMATCH-26JUL08GHAGEN-GHA | 64 | 55m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08HARBEA-HAR | 6 | 55m | 1/11-11/8 | 8-11 | 5 | **FLOW_ABOVE** | 6 | flow above but bound 6c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08KAMDEC-DEC | 90 | 28m | 0 | 90-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KAMDEC-KAM | 7 | 28m | 0 | 7-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KIRVAN-KIR | 86 | 28m | 0 | 86-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KIRVAN-VAN | 11 | 28m | 1/11-11/11 | 11-13 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL08LAZADD-ADD | 82 | 58m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAZADD-LAZ | 14 | 53m | 0 | 14-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MINFAB-MIN | 47 | 18m | 0 | 47-52 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MURGUN-GUN | 91 | 25m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MURGUN-MUR | 5 | 28m | 0 | 5-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PELDUH-PEL | 74 | 62m | 1/76-76/5 | 74-76 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→76 |
| ITFMATCH-26JUL08PERVAN-PER | 54 | 28m | 0 | 54-58 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PERVAN-VAN | 42 | 16m | 0 | 42-46 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SERROS-SER | 42 | 4m | 0 | 45-47 | — | **NO_FLOW** | 43 |  |
| ITFMATCH-26JUL08SHIVUJ-SHI | 61 | 62m | 1/66-66/3 | 61-65 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-VUJ | 35 | 16m | 0 | 35-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STEGSC-GSC | 85 | 58m | 0 | 85-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STEGSC-STE | 14 | 58m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08THIAND-AND | 38 | 20m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08THIAND-THI | 59 | 28m | 0 | 59-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TYAGAR-GAR | 36 | 19m | 0 | 36-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TYAGAR-TYA | 61 | 28m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07WEISUN-SUN | 18 | 62m | 2343/23-99/188962 | 99-25 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08CIRBRE-BRE | 11 | 62m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08DEPGAR-DEP | 52 | 19m | 0 | 52-55 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08DEPGAR-GAR | 45 | 17m | 0 | 45-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08DILSAV-SAV | 39 | 19m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ERCLEM-ERC | 34 | 18m | 0 | 34-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ERCLEM-LEM | 63 | 28m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-GIO | 31 | 62m | 1/34-34/8 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL08ILIPOP-ILI | 23 | 28m | 0 | 23-28 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08KNUSHI-KNU | 40 | 18m | 0 | 40-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08KNUSHI-SHI | 56 | 28m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LIXYAM-YAM | 90 | 21m | 1/92-92/1 | 90-92 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |
| ITFWMATCH-26JUL08LUENAT-LUE | 53 | 22m | 0 | 53-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LUENAT-NAT | 41 | 18m | 0 | 41-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MANKAV-MAN | 94 | 62m | 0 | 94-97 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MILEZZ-EZZ | 56 | 28m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MILMIS-MIL | 5 | 28m | 0 | 5-8 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MILMIS-MIS | 92 | 28m | 0 | 92-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MIXKRU-MIX | 38 | 22m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NEWCOU-COU | 35 | 10m | 0 | 35-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NEWCOU-NEW | 60 | 28m | 0 | 60-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAPCAP-CAP | 51 | 58m | 0 | 51-54 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAPCAP-PAP | 46 | 58m | 1/47-47/2 | 46-47 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFWMATCH-26JUL08PAVAGR-PAV | 91 | 27m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAWLAZ-LAZ | 21 | 23m | 0 | 21-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAWLAZ-PAW | 74 | 28m | 0 | 74-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PRIVON-PRI | 37 | 57m | 1/39-39/2 | 37-39 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL08PRIVON-VON | 59 | 58m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08REVHRU-HRU | 91 | 23m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ROSPAR-ROS | 47 | 62m | 1/50-50/1 | 47-50 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL08RYSTRA-RYS | 90 | 27m | 0 | 90-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RYSTRA-TRA | 6 | 27m | 0 | 6-10 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHOSUV-SHO | 52 | 62m | 6/74-74/130 | 70-74 | 22 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08SOLRAS-RAS | 41 | 18m | 0 | 41-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SOLRAS-SOL | 54 | 28m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TRICEN-CEN | 87 | 58m | 0 | 87-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TRICEN-TRI | 8 | 23m | 0 | 8-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-TUP | 83 | 62m | 40/96-98/836 | 97-98 | 13 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08VANWON-VAN | 44 | 62m | 1/47-47/2 | 44-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFWMATCH-26JUL08VANWON-WON | 53 | 62m | 0 | 53-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08VOSLEY-LEY | 93 | 28m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WIEORT-ORT | 21 | 28m | 0 | 21-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WIEORT-WIE | 74 | 28m | 0 | 74-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08YODKEN-KEN | 17 | 28m | 0 | 17-20 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08YODKEN-YOD | 78 | 2m | 0 | 78-82 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07DELKOY | 87 | 1 | **88** | 97 | -9 |
| ITFMATCH-26JUL08SERROS | 54 | 47 | **101** | 97 | +4 |
| ITFMATCH-26JUL08HARBEA | 91 | 11 | **102** | 97 | +5 |

## PATTERNS (sub-B) — 9
- half_arm_aging: KXITFMATCH-26JUL07DELKOY-DEL {"fill": 87, "age_min": 62, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07YAMNAK-NAK {"fill": 7, "age_min": 62, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07BORZEN-BOR {"fill": 53, "age_min": 61, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08HARBEA-BEA {"fill": 91, "age_min": 55, "mode": "SET_BELOW_FLOW(prints 5c above)"}
- half_arm_aging: KXITFWMATCH-26JUL07CHOCAO-CHO {"fill": 50, "age_min": 51, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07GURKAL-GUR {"fill": 32, "age_min": 51, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08NAKZHA-ZHA {"fill": 15, "age_min": 33, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 12:58:59 AM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFWMATCH-26JUL07LIURUO {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- half_arm_aging: KXITFWMATCH-26JUL08LIUMAL-MAL {"fill": 72, "age_min": 31, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 12:58:59 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
