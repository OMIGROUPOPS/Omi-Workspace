# LIVE VALIDATION — rolling status

- cycle 167 @ **2026-07-07 08:18:08 PM ET** | build `0b070d3` | session boot 07-07 19:38 ET | log `live_v3_20260707.jsonl` | 6078 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 6 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:39 | ITFMATCH-26JUL07OGUJAS-OGU | ITF_M | ? | 25 | 21 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 19:39 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 90 | 87 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 19:42 | ATPCHALLENGERMATCH-26JUL07VANMIL-V | ATP_CHALL | ? | 47 | 44 | +3 (fill_est) | -4.0 | 1.4 | single |  | EARNED |
| 19:58 | ITFMATCH-26JUL07ISOTOM-ISO | ITF_M | ? | 80 | 77 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 20:17 | ITFWMATCH-26JUL07ZHOLEO-ZHO | ITF_W | ? | 17 | 13 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 20:18 | ITFMATCH-26JUL07TANCHE-TAN | ITF_M | underdog | 47 | 42 | +5 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 10 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 7, 'FLOW_ABOVE': 3} | repriceable now: true 2 / false 8 | **cumulative bid_grade lines: 5113 (repriceable true 470 / false 4643)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07ISOTOM-TOM | 16 | 18m | 24/22-22/1085 | 20-21 | 6 | **FLOW_ABOVE** | 17 | flow above but bound 17c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07MOXSAR-MOX | 69 | 9m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07NAKSHI-NAK | 39 | 17m | 0 | 39-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07NAKSHI-SHI | 57 | 17m | 0 | 57-61 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07TAKSAM-TAK | 9 | 19m | 47/11-13/1870 | 10-10 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFMATCH-26JUL07YAMNAK-NAK | 6 | 16m | 3/10-10/47 | 6-10 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL07YAMNAK-YAM | 89 | 14m | 0 | 89-93 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07YAMTAN-TAN | 81 | 17m | 0 | 81-85 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07YAMTAN-YAM | 15 | 17m | 0 | 15-18 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07CHOCAO-CHO | 49 | 39m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07ISOTOM | 80 | 21 | **101** | 97 | +4 |

## PATTERNS (sub-B) — 3
- half_arm_aging: KXITFMATCH-26JUL07OGUJAS-OGU {"fill": 25, "age_min": 39, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07DELKOY-DEL {"fill": 90, "age_min": 39, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-07 08:18:08 PM ET"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07VANMIL-VAN {"fill": 47, "age_min": 35, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
