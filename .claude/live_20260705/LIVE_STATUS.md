# LIVE VALIDATION — rolling status

- cycle 168 @ **2026-07-07 08:28:23 PM ET** | build `cf7291d` | session boot 07-07 19:38 ET | log `live_v3_20260707.jsonl` | 7369 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 20:21:09 | **combined_over_goal** | KXITFMATCH-26JUL07TANCHE | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 10 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:39 | ITFMATCH-26JUL07OGUJAS-OGU | ITF_M | ? | 25 | 21 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 19:39 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 90 | 87 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 19:42 | ATPCHALLENGERMATCH-26JUL07VANMIL-V | ATP_CHALL | ? | 47 | 44 | +3 (fill_est) | -4.0 | 1.4 | single |  | EARNED |
| 19:58 | ITFMATCH-26JUL07ISOTOM-ISO | ITF_M | ? | 80 | 77 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 20:17 | ITFWMATCH-26JUL07ZHOLEO-ZHO | ITF_W | ? | 17 | 13 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 20:18 | ITFMATCH-26JUL07TANCHE-TAN | ITF_M | underdog | 47 | 42 | +5 (place_cell) | — | pre | pair | 98 | PENDING |
| 20:18 | ITFMATCH-26JUL07ICHOCH-OCH | ITF_M | ? | 29 | 25 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 20:21 | ITFMATCH-26JUL07TANCHE-CHE | ITF_M | ? | 51 | 48 | +3 (adopted_est) | — | pre | pair | 98 | PENDING |
| 20:22 | ITFMATCH-26JUL07TAKSAM-SAM | ITF_M | ? | 88 | 85 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 20:24 | ITFMATCH-26JUL07KUSTAG-TAG | ITF_M | ? | 62 | 59 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 11 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 8, 'FLOW_ABOVE': 3} | repriceable now: true 2 / false 9 | **cumulative bid_grade lines: 5114 (repriceable true 470 / false 4644)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07ISOTOM-TOM | 16 | 29m | 33/20-22/1688 | 20-21 | 4 | **FLOW_ABOVE** | 17 | REPRICEABLE→17 |
| ITFMATCH-26JUL07MOXSAR-MOX | 69 | 19m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07NAKSHI-NAK | 39 | 27m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07NAKSHI-SHI | 57 | 27m | 0 | 57-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07TAKSAM-TAK | 9 | 29m | 72/11-14/3869 | 10-10 | 2 | **FLOW_ABOVE** | 9 | flow above but bound 9c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07YAMNAK-NAK | 6 | 26m | 4/10-10/94 | 6-10 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL07YAMNAK-YAM | 89 | 24m | 0 | 89-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07YAMTAN-TAN | 81 | 27m | 0 | 81-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07YAMTAN-YAM | 15 | 27m | 0 | 15-18 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07CHOCAO-CHO | 49 | 49m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LIXYAM-LIX | 8 | 10m | 0 | 8-9 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07TAKSAM | 88 | 10 | **98** | 97 | +1 |
| ITFMATCH-26JUL07ISOTOM | 80 | 21 | **101** | 97 | +4 |

## PATTERNS (sub-B) — 3
- half_arm_aging: KXITFMATCH-26JUL07OGUJAS-OGU {"fill": 25, "age_min": 49, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07DELKOY-DEL {"fill": 90, "age_min": 49, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07VANMIL-VAN {"fill": 47, "age_min": 46, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
