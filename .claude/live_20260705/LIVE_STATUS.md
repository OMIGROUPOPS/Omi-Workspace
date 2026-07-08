# LIVE VALIDATION — rolling status

- cycle 192 @ **2026-07-08 12:38:08 AM ET** | build `f10c692` | session boot 07-07 23:56 ET | log `live_v3_20260707.jsonl` | 36417 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 12 graded (session)
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

## RESTING BIDS — 72 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 15, 'NO_FLOW': 57} | repriceable now: true 8 / false 64 | **cumulative bid_grade lines: 5421 (repriceable true 521 / false 4900)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07ICHOCH-OCH | 28 | 41m | 1456/39-82/96418 | 80-47 | 11 | **FLOW_ABOVE** | 57 |  |
| ITFMATCH-26JUL07OKIMAT-MAT | 44 | 41m | 482/55-78/33693 | 74-59 | 11 | **FLOW_ABOVE** | 70 |  |
| ITFMATCH-26JUL08BALKAS-BAL | 78 | 27m | 0 | 78-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BALKAS-KAS | 18 | 27m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BERKUM-BER | 63 | 37m | 0 | 63-65 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BERKUM-KUM | 34 | 37m | 1/37-37/2 | 34-37 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFMATCH-26JUL08BRAWYG-BRA | 85 | 37m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BRAWYG-WYG | 11 | 37m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08CARERE-CAR | 6 | 37m | 0 | 6-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08CARERE-ERE | 89 | 31m | 0 | 89-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08GHAGEN-GEN | 34 | 41m | 1/38-38/2 | 34-38 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| ITFMATCH-26JUL08GHAGEN-GHA | 64 | 34m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08HARBEA-HAR | 6 | 34m | 0 | 8-11 | — | **NO_FLOW** | 6 |  |
| ITFMATCH-26JUL08KAMDEC-DEC | 90 | 7m | 0 | 90-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KAMDEC-KAM | 7 | 7m | 0 | 7-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KIRVAN-KIR | 86 | 7m | 0 | 86-88 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KIRVAN-VAN | 11 | 7m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KUNMEN-MEN | 65 | 8m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAZADD-ADD | 82 | 37m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAZADD-LAZ | 14 | 32m | 0 | 14-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MURGUN-GUN | 91 | 4m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MURGUN-MUR | 5 | 7m | 0 | 5-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PELDUH-PEL | 74 | 41m | 0 | 74-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PERVAN-PER | 54 | 7m | 0 | 54-58 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SERROS-ROS | 54 | 6m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SERROS-SER | 44 | 30m | 0 | 44-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-SHI | 61 | 41m | 1/66-66/3 | 61-66 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-VUJ | 34 | 41m | 1/39-39/2 | 34-39 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08STEGSC-GSC | 85 | 37m | 0 | 85-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STEGSC-STE | 14 | 37m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STERAD-RAD | 34 | 37m | 1/36-36/2 | 34-36 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL08STERAD-STE | 64 | 37m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08THIAND-THI | 59 | 7m | 0 | 59-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TYAGAR-TYA | 61 | 7m | 0 | 61-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07WEISUN-SUN | 18 | 41m | 1450/23-61/94415 | 59-25 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08CIRBRE-BRE | 11 | 41m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08DUEPOP-DUE | 93 | 7m | 0 | 93-97 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ERCLEM-LEM | 63 | 7m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-GIO | 31 | 41m | 1/34-34/8 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL08ILIPOP-ILI | 23 | 7m | 0 | 23-28 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ILIPOP-POP | 71 | 7m | 0 | 71-77 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08KNUSHI-SHI | 56 | 7m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LIXYAM-YAM | 90 | 1m | 0 | 90-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LUENAT-LUE | 53 | 2m | 0 | 53-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MANKAV-MAN | 94 | 41m | 0 | 94-97 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MILEZZ-EZZ | 56 | 7m | 0 | 56-57 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MILMIS-MIL | 5 | 7m | 0 | 5-8 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MILMIS-MIS | 92 | 7m | 0 | 92-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MIXKRU-MIX | 38 | 1m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NEWCOU-NEW | 60 | 7m | 0 | 60-65 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAPCAP-CAP | 51 | 37m | 0 | 51-54 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAPCAP-PAP | 46 | 37m | 1/47-47/2 | 46-47 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFWMATCH-26JUL08PAVAGR-PAV | 91 | 6m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAWLAZ-LAZ | 21 | 2m | 0 | 21-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAWLAZ-PAW | 74 | 7m | 0 | 74-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PRIVON-PRI | 37 | 36m | 1/39-39/2 | 37-39 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→39 |
| ITFWMATCH-26JUL08PRIVON-VON | 59 | 37m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08REVHRU-HRU | 91 | 3m | 0 | 91-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ROSPAR-ROS | 47 | 41m | 1/50-50/1 | 47-50 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL08RYSTRA-RYS | 90 | 6m | 0 | 90-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RYSTRA-TRA | 6 | 6m | 0 | 6-10 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHOSUV-SHO | 52 | 41m | 3/74-74/65 | 72-74 | 22 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08SOLRAS-SOL | 54 | 7m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TRICEN-CEN | 87 | 37m | 0 | 87-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TRICEN-TRI | 8 | 3m | 0 | 8-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-TUP | 83 | 41m | 8/97-97/106 | 97-98 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08VANWON-VAN | 44 | 41m | 1/47-47/2 | 44-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFWMATCH-26JUL08VANWON-WON | 53 | 41m | 0 | 53-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08VOSLEY-LEY | 93 | 7m | 0 | 93-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WIEORT-ORT | 21 | 7m | 0 | 21-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WIEORT-WIE | 74 | 7m | 0 | 74-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08YODKEN-KEN | 17 | 7m | 0 | 17-20 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07DELKOY | 87 | 1 | **88** | 97 | -9 |
| ITFMATCH-26JUL08HARBEA | 91 | 11 | **102** | 97 | +5 |

## PATTERNS (sub-B) — 7
- half_arm_aging: KXITFMATCH-26JUL07DELKOY-DEL {"fill": 87, "age_min": 41, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07YAMNAK-NAK {"fill": 7, "age_min": 41, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07BORZEN-BOR {"fill": 53, "age_min": 40, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 12:38:08 AM ET"}
- half_arm_aging: KXITFMATCH-26JUL08HARBEA-BEA {"fill": 91, "age_min": 34, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-08 12:38:08 AM ET"}
- half_arm_aging: KXITFWMATCH-26JUL07CHOCAO-CHO {"fill": 50, "age_min": 30, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07GURKAL-GUR {"fill": 32, "age_min": 30, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 12:38:08 AM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFWMATCH-26JUL07LIURUO {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-08 12:38:08 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
