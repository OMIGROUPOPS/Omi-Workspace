# LIVE VALIDATION — rolling status

- cycle 185 @ **2026-07-07 11:24:58 PM ET** | build `1e3edee` | session boot 07-07 23:12 ET | log `live_v3_20260707.jsonl` | 16196 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 6 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23:12 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 87 | 91 | -4 (window_cell) | — | pre | single |  | MIXED |
| 23:13 | ITFMATCH-26JUL07LOMTOM-TOM | ITF_M | ? | 62 | 59 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 23:15 | ITFMATCH-26JUL07OKIMAT-OKI | ITF_M | ? | 53 | 50 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 23:16 | ITFWMATCH-26JUL07CHOCAO-CAO | ITF_W | ? | 49 | 45 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 23:19 | ITFWMATCH-26JUL08TUPPAN-PAN | ITF_W | underdog | 14 | 8 | +6 (place_cell) | — | pre | single |  | PENDING |
| 23:24 | ITFMATCH-26JUL07NASLEE-LEE | ITF_M | ? | 25 | 21 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 12 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 5, 'NO_FLOW': 7} | repriceable now: true 1 / false 11 | **cumulative bid_grade lines: 5285 (repriceable true 503 / false 4782)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07ADAIMA-ADA | 3 | 1m | 2/8-8/95 | 6-8 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL07ICHOCH-OCH | 28 | 13m | 190/46-56/13431 | 53-48 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08KUNMEN-MEN | 62 | 8m | 2/69-69/16 | 62-69 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08HARMAI-HAR | 3 | 12m | 0 | 3-94 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-GIO | 31 | 12m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08KUBSHK-KUB | 94 | 9m | 0 | 94-97 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08KUBSHK-SHK | 2 | 9m | 1/5-5/93 | 2-5 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→5 |
| ITFWMATCH-26JUL08MANKAV-KAV | 3 | 9m | 0 | 3-5 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MANKAV-MAN | 95 | 8m | 0 | 95-97 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08ROSPAR-ROS | 47 | 9m | 0 | 47-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHOSUV-SHO | 52 | 13m | 0 | 64-79 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-TUP | 83 | 2m | 3/96-97/25 | 96-97 | 13 | **FLOW_ABOVE** | 83 | flow above but bound 83c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07DELKOY | 87 | 1 | **88** | 97 | -9 |
| ITFWMATCH-26JUL08TUPPAN | 14 | 97 | **111** | 97 | +14 |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
