# LIVE VALIDATION — rolling status

- cycle 191 @ **2026-07-08 12:27:34 AM ET** | build `9709162` | session boot 07-07 23:56 ET | log `live_v3_20260707.jsonl` | 30189 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 10 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:56 | ITFWMATCH-26JUL07LIURUO-RUO | ITF_W | ? | 23 | 19 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 23:56 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 87 | 91 | -4 (window_cell) | — | pre | single |  | MIXED |
| 23:57 | ITFMATCH-26JUL07YAMNAK-NAK | ITF_M | ? | 7 | 3 | +4 (fill_est) | — | pre | single |  | PENDING |
| 23:58 | ITFMATCH-26JUL07BORZEN-BOR | ITF_M | ? | 53 | 50 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 00:03 | ITFMATCH-26JUL08HARBEA-BEA | ITF_M | leader | 91 | 86 | +5 (place_cell) | — | pre | single |  | PENDING |
| 00:08 | ITFWMATCH-26JUL07CHOCAO-CHO | ITF_W | ? | 50 | 48 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 00:08 | ITFWMATCH-26JUL07GURKAL-GUR | ITF_W | ? | 32 | 28 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 00:19 | ITFMATCH-26JUL07YAMTAN-TAN | ITF_M | ? | 82 | 79 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 00:25 | ITFWMATCH-26JUL08NAKZHA-ZHA | ITF_W | ? | 15 | 11 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 00:25 | ITFMATCH-26JUL07YAMTAN-YAM | ITF_M | ? | 15 | 11 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |

## RESTING BIDS — 40 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 14, 'NO_FLOW': 26} | repriceable now: true 7 / false 33 | **cumulative bid_grade lines: 5383 (repriceable true 519 / false 4864)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07ICHOCH-OCH | 28 | 31m | 927/39-62/55204 | 59-47 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL07OKIMAT-MAT | 44 | 31m | 314/55-70/13582 | 66-59 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08BALKAS-BAL | 78 | 16m | 0 | 78-82 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BALKAS-KAS | 18 | 16m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BERKUM-BER | 63 | 27m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BERKUM-KUM | 34 | 27m | 1/37-37/2 | 34-37 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→37 |
| ITFMATCH-26JUL08BRAWYG-BRA | 85 | 27m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08BRAWYG-WYG | 11 | 27m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08CARERE-CAR | 6 | 26m | 0 | 6-8 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08CARERE-ERE | 89 | 20m | 0 | 89-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08GHAGEN-GEN | 34 | 30m | 1/38-38/2 | 34-38 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→38 |
| ITFMATCH-26JUL08GHAGEN-GHA | 64 | 24m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08HARBEA-HAR | 6 | 24m | 0 | 8-11 | — | **NO_FLOW** | 6 |  |
| ITFMATCH-26JUL08KUNMEN-MEN | 64 | 30m | 1/67-67/5 | 64-67 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFMATCH-26JUL08LAZADD-ADD | 82 | 26m | 0 | 82-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAZADD-LAZ | 14 | 22m | 0 | 14-17 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PELDUH-PEL | 74 | 30m | 0 | 74-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SERROS-ROS | 51 | 27m | 7/56-56/733 | 51-56 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08SERROS-SER | 44 | 19m | 0 | 44-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-SHI | 61 | 30m | 0 | 61-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-VUJ | 34 | 30m | 1/39-39/2 | 34-39 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08STEGSC-GSC | 85 | 27m | 0 | 85-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STEGSC-STE | 14 | 27m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STERAD-RAD | 34 | 27m | 1/36-36/2 | 34-36 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFMATCH-26JUL08STERAD-STE | 64 | 27m | 0 | 64-66 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07WEISUN-SUN | 18 | 31m | 1052/23-59/72097 | 57-25 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08CIRBRE-BRE | 11 | 30m | 0 | 11-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-GIO | 31 | 30m | 1/34-34/8 | 31-34 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→34 |
| ITFWMATCH-26JUL08MANKAV-MAN | 94 | 30m | 0 | 94-97 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAPCAP-CAP | 51 | 26m | 0 | 51-54 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PAPCAP-PAP | 46 | 26m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PRIVON-PRI | 37 | 26m | 0 | 37-39 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PRIVON-VON | 59 | 27m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ROSPAR-ROS | 47 | 30m | 1/50-50/1 | 47-50 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL08SHOSUV-SHO | 52 | 31m | 3/74-74/65 | 71-74 | 22 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08TRICEN-CEN | 87 | 26m | 0 | 87-92 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TRICEN-TRI | 6 | 26m | 0 | 6-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-TUP | 83 | 31m | 3/97-97/45 | 97-98 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08VANWON-VAN | 44 | 30m | 1/47-47/2 | 44-47 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFWMATCH-26JUL08VANWON-WON | 53 | 30m | 0 | 53-56 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07DELKOY | 87 | 1 | **88** | 97 | -9 |
| ITFMATCH-26JUL08HARBEA | 91 | 11 | **102** | 97 | +5 |

## PATTERNS (sub-B) — 3
- half_arm_aging: KXITFWMATCH-26JUL07LIURUO-RUO {"fill": 23, "age_min": 31, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 12:27:34 AM ET"}
- half_arm_aging: KXITFMATCH-26JUL07DELKOY-DEL {"fill": 87, "age_min": 31, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07YAMNAK-NAK {"fill": 7, "age_min": 30, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 12:27:34 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
