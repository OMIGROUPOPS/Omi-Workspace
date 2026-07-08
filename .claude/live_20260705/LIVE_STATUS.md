# LIVE VALIDATION — rolling status

- cycle 186 @ **2026-07-07 11:35:16 PM ET** | build `2c9b8c3` | session boot 07-07 23:12 ET | log `live_v3_20260707.jsonl` | 24639 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 8 graded (session)
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

## RESTING BIDS — 30 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 7, 'NO_FLOW': 23} | repriceable now: true 3 / false 27 | **cumulative bid_grade lines: 5308 (repriceable true 505 / false 4803)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07ADAIMA-ADA | 2 | 2m | 35/5-7/3461 | 6-5 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→5 |
| ITFMATCH-26JUL07ICHOCH-OCH | 28 | 23m | 453/46-62/25757 | 61-48 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08GHAGEN-GEN | 33 | 4m | 0 | 33-38 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08GHAGEN-GHA | 65 | 4m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08HARBEA-BEA | 88 | 2m | 0 | 89-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08HARBEA-HAR | 7 | 5m | 0 | 7-12 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KUNMEN-MEN | 63 | 5m | 1/68-68/0 | 63-68 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08LAPGAR-GAR | 59 | 3m | 0 | 59-63 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAPGAR-LAP | 36 | 3m | 0 | 36-40 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PELDUH-DUH | 22 | 5m | 0 | 22-25 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PELDUH-PEL | 73 | 5m | 0 | 73-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PIEPRA-PIE | 82 | 3m | 0 | 82-86 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08PIEPRA-PRA | 14 | 3m | 0 | 14-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-SHI | 60 | 4m | 0 | 60-66 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SHIVUJ-VUJ | 33 | 4m | 0 | 33-37 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CAVPLO-PLO | 3 | 4m | 0 | 3-95 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CIRBRE-BRE | 10 | 4m | 0 | 10-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CIRBRE-CIR | 85 | 4m | 0 | 85-90 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HARMAI-HAR | 3 | 23m | 0 | 3-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-GIO | 31 | 23m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08KUBSHK-KUB | 95 | 8m | 0 | 95-97 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08KUBSHK-SHK | 2 | 20m | 1/5-5/93 | 2-5 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→5 |
| ITFWMATCH-26JUL08MANKAV-KAV | 3 | 19m | 2/5-5/10 | 3-5 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→5 |
| ITFWMATCH-26JUL08MANKAV-MAN | 95 | 19m | 0 | 95-97 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MIXKRU-MIX | 34 | 1m | 0 | 34-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ROSPAR-ROS | 47 | 19m | 0 | 47-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHOSUV-SHO | 52 | 23m | 1/76-76/1 | 69-74 | 24 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-TUP | 83 | 12m | 3/96-97/25 | 96-97 | 13 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08VANWON-VAN | 44 | 4m | 0 | 44-47 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08VANWON-WON | 52 | 4m | 0 | 52-56 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07DELKOY | 87 | 1 | **88** | 97 | -9 |
| ITFWMATCH-26JUL08TUPPAN | 14 | 97 | **111** | 97 | +14 |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
