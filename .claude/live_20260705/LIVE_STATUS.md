# LIVE VALIDATION — rolling status

- cycle 188 @ **2026-07-07 11:56:07 PM ET** | build `3f340e7` | session boot 07-07 23:12 ET | log `live_v3_20260707.jsonl` | 36335 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 15 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:12 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 87 | 91 | -4 (window_cell) | — | pre | single |  | MIXED |
| 23:13 | ITFMATCH-26JUL07LOMTOM-TOM | ITF_M | ? | 62 | 59 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 23:15 | ITFMATCH-26JUL07OKIMAT-OKI | ITF_M | ? | 53 | 50 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 23:16 | ITFWMATCH-26JUL07CHOCAO-CAO | ITF_W | ? | 49 | 45 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 23:19 | ITFWMATCH-26JUL08TUPPAN-PAN | ITF_W | underdog | 14 | 8 | +6 (place_cell) | — | pre | single |  | PENDING |
| 23:24 | ITFMATCH-26JUL07NASLEE-LEE | ITF_M | ? | 25 | 21 | +4 (fill_est) | — | pre | single |  | PENDING |
| 23:32 | ITFMATCH-26JUL07NAKSHI-NAK | ITF_M | ? | 40 | 36 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 23:35 | ITFMATCH-26JUL07NAKSHI-SHI | ITF_M | ? | 57 | 54 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 23:37 | ITFMATCH-26JUL07YAMNAK-YAM | ITF_M | ? | 90 | 87 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 23:39 | ITFWMATCH-26JUL07WEISUN-WEI | ITF_W | ? | 79 | 77 | +2 (adopted_est) | — | pre | pair | 97 | PENDING |
| 23:41 | ITFWMATCH-26JUL07WEISUN-SUN | ITF_W | ? | 18 | 14 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 23:43 | ITFMATCH-26JUL07BORZEN-ZEN | ITF_M | ? | 42 | 38 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 23:45 | ITFWMATCH-26JUL07GURKAL-KAL | ITF_W | ? | 65 | 63 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 23:54 | ITFWMATCH-26JUL07LIURUO-RUO | ITF_W | ? | 23 | 19 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 23:55 | ITFWMATCH-26JUL08HARMAI-HAR | ITF_W | ? | 4 | 1 | +3 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 35 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 12, 'NO_FLOW': 23} | repriceable now: true 9 / false 26 | **cumulative bid_grade lines: 5331 (repriceable true 512 / false 4819)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07ADAIMA-ADA | 1 | 17m | 211/2-5/42476 | 6-3 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→2 |
| ITFMATCH-26JUL07ICHOCH-OCH | 28 | 6m | 175/54-81/6626 | 80-48 | 26 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08GHAGEN-GEN | 34 | 14m | 0 | 34-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08GHAGEN-GHA | 65 | 25m | 1/66-66/10 | 65-66 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→66 |
| ITFMATCH-26JUL08HARBEA-BEA | 90 | 3m | 2/93-94/201 | 90-94 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→93 |
| ITFMATCH-26JUL08HARBEA-HAR | 8 | 13m | 0 | 8-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KUNMEN-MEN | 64 | 13m | 0 | 64-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAPGAR-GAR | 59 | 24m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAPGAR-LAP | 36 | 24m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PELDUH-DUH | 22 | 26m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PELDUH-PEL | 74 | 13m | 0 | 74-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PIEPRA-PIE | 82 | 24m | 0 | 82-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PIEPRA-PRA | 14 | 24m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-SHI | 61 | 13m | 0 | 61-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-VUJ | 34 | 14m | 0 | 34-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08ZHAISH-ZHA | 86 | 6m | 4/89-90/201 | 86-91 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| ITFWMATCH-26JUL08BOSBOY-BOY | 3 | 2m | 0 | 3-5 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CAVPLO-CAV | 2 | 10m | 0 | 3-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CAVPLO-CAV | 3 | 3m | 0 | 3-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CAVPLO-PLO | 3 | 25m | 0 | 4-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CAVPLO-PLO | 4 | 3m | 0 | 4-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CIRBRE-CIR | 85 | 25m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HARMAI-MAI | 93 | 1m | 0 | 97-95 | — | **NO_FLOW** | 93 |  |
| ITFWMATCH-26JUL08HAYGIO-GIO | 31 | 44m | 0 | 31-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08KUBSHK-KUB | 95 | 28m | 4/97-97/205 | 95-97 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→97 |
| ITFWMATCH-26JUL08KUBSHK-SHK | 2 | 41m | 1/5-5/93 | 2-5 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→5 |
| ITFWMATCH-26JUL08MANKAV-KAV | 3 | 40m | 3/5-5/25 | 3-5 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→5 |
| ITFWMATCH-26JUL08MANKAV-MAN | 95 | 39m | 6/97-97/307 | 94-97 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→97 |
| ITFWMATCH-26JUL08MANKAV-MAN | 94 | 6m | 6/97-97/307 | 94-97 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→97 |
| ITFWMATCH-26JUL08ROSPAR-ROS | 47 | 40m | 0 | 47-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHOSUV-SHO | 52 | 44m | 3/74-76/24 | 71-74 | 22 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-TUP | 83 | 33m | 7/96-98/34 | 97-97 | 13 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08VAJKAR-KAR | 96 | 2m | 0 | 96-97 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08VANWON-VAN | 44 | 25m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANOHX-WAN | 79 | 1m | 0 | 79-82 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07DELKOY | 87 | 1 | **88** | 97 | -9 |
| ITFWMATCH-26JUL08HARMAI | 4 | 95 | **99** | 97 | +2 |
| ITFWMATCH-26JUL08TUPPAN | 14 | 97 | **111** | 97 | +14 |

## PATTERNS (sub-B) — 6
- half_arm_aging: KXITFMATCH-26JUL07DELKOY-DEL {"fill": 87, "age_min": 44, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07LOMTOM-TOM {"fill": 62, "age_min": 42, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07OKIMAT-OKI {"fill": 53, "age_min": 41, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07CHOCAO-CAO {"fill": 49, "age_min": 40, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-07 11:56:07 PM ET"}
- half_arm_aging: KXITFWMATCH-26JUL08TUPPAN-PAN {"fill": 14, "age_min": 37, "mode": "SET_BELOW_FLOW(prints 13c above)", "emitted_et": "2026-07-07 11:56:07 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL07NASLEE-LEE {"fill": 25, "age_min": 32, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
