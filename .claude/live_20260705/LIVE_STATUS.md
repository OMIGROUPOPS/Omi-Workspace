# LIVE VALIDATION — rolling status

- cycle 187 @ **2026-07-07 11:45:42 PM ET** | build `7c81454` | session boot 07-07 23:12 ET | log `live_v3_20260707.jsonl` | 28887 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 13 graded (session)
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

## RESTING BIDS — 28 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 22} | repriceable now: true 3 / false 25 | **cumulative bid_grade lines: 5317 (repriceable true 506 / false 4811)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07ADAIMA-ADA | 1 | 6m | 86/3-5/22510 | 6-4 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→3 |
| ITFMATCH-26JUL07ICHOCH-OCH | 28 | 33m | 659/46-66/38834 | 62-48 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08GHAGEN-GEN | 34 | 3m | 0 | 34-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08GHAGEN-GHA | 65 | 14m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08HARBEA-BEA | 89 | 10m | 0 | 89-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08HARBEA-HAR | 8 | 3m | 0 | 8-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KUNMEN-MEN | 64 | 3m | 0 | 64-67 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAPGAR-GAR | 59 | 14m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAPGAR-LAP | 36 | 14m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PELDUH-DUH | 22 | 15m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PELDUH-PEL | 74 | 3m | 0 | 74-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PIEPRA-PIE | 82 | 14m | 0 | 82-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PIEPRA-PRA | 14 | 14m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-SHI | 61 | 3m | 0 | 61-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-VUJ | 34 | 3m | 0 | 34-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CAVPLO-PLO | 3 | 14m | 0 | 3-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CIRBRE-CIR | 85 | 15m | 0 | 85-89 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HARMAI-HAR | 3 | 33m | 0 | 3-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-GIO | 31 | 33m | 0 | 31-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08KUBSHK-KUB | 95 | 18m | 0 | 95-97 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08KUBSHK-SHK | 2 | 30m | 1/5-5/93 | 2-5 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→5 |
| ITFWMATCH-26JUL08MANKAV-KAV | 3 | 30m | 2/5-5/10 | 3-5 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→5 |
| ITFWMATCH-26JUL08MANKAV-MAN | 95 | 29m | 0 | 95-97 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MIXKRU-MIX | 35 | 3m | 0 | 35-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ROSPAR-ROS | 47 | 30m | 0 | 47-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHOSUV-SHO | 52 | 33m | 3/74-76/24 | 69-74 | 22 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-TUP | 83 | 23m | 4/96-97/25 | 96-97 | 13 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08VANWON-VAN | 44 | 15m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07DELKOY | 87 | 1 | **88** | 97 | -9 |
| ITFWMATCH-26JUL08TUPPAN | 14 | 97 | **111** | 97 | +14 |

## PATTERNS (sub-B) — 3
- half_arm_aging: KXITFMATCH-26JUL07DELKOY-DEL {"fill": 87, "age_min": 33, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07LOMTOM-TOM {"fill": 62, "age_min": 32, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-07 11:45:42 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL07OKIMAT-OKI {"fill": 53, "age_min": 30, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
