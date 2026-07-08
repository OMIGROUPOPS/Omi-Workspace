# LIVE VALIDATION — rolling status

- cycle 169 @ **2026-07-07 08:38:52 PM ET** | build `f1a13b8` | session boot 07-07 19:38 ET | log `live_v3_20260707.jsonl` | 9982 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 20:21:09 | **combined_over_goal** | KXITFMATCH-26JUL07TANCHE | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 11 graded (session)
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
| 20:28 | ITFMATCH-26JUL07NASLEE-NAS | ITF_M | ? | 72 | 69 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 14 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 11, 'FLOW_ABOVE': 3} | repriceable now: true 2 / false 12 | **cumulative bid_grade lines: 5117 (repriceable true 470 / false 4647)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07ISOTOM-TOM | 16 | 39m | 44/20-22/1918 | 20-21 | 4 | **FLOW_ABOVE** | 17 | REPRICEABLE→17 |
| ITFMATCH-26JUL07MOXSAR-MOX | 69 | 29m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07NAKSHI-NAK | 39 | 38m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07NAKSHI-SHI | 57 | 38m | 0 | 57-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07TAKSAM-TAK | 9 | 40m | 154/11-33/13170 | 21-10 | 2 | **FLOW_ABOVE** | 9 | flow above but bound 9c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07YAMNAK-NAK | 6 | 37m | 5/10-10/141 | 6-10 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL07YAMNAK-YAM | 89 | 35m | 0 | 89-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07YAMTAN-TAN | 81 | 38m | 0 | 81-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07YAMTAN-YAM | 15 | 38m | 0 | 15-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KIMROH-KIM | 64 | 8m | 0 | 64-68 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08KIMROH-ROH | 31 | 8m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LIUSHI-SHI | 12 | 2m | 0 | 12-60 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07CHOCAO-CHO | 49 | 60m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LIXYAM-LIX | 8 | 20m | 0 | 8-9 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07TAKSAM | 88 | 10 | **98** | 97 | +1 |
| ITFMATCH-26JUL07ISOTOM | 80 | 21 | **101** | 97 | +4 |

## PATTERNS (sub-B) — 4
- half_arm_aging: KXITFMATCH-26JUL07OGUJAS-OGU {"fill": 25, "age_min": 60, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07DELKOY-DEL {"fill": 90, "age_min": 60, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07VANMIL-VAN {"fill": 47, "age_min": 56, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07ISOTOM-ISO {"fill": 80, "age_min": 40, "mode": "SET_BELOW_FLOW(prints 4c above)", "emitted_et": "2026-07-07 08:38:52 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
