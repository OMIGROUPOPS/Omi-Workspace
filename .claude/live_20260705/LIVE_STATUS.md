# LIVE VALIDATION — rolling status

- cycle 171 @ **2026-07-07 08:59:32 PM ET** | build `1eff5f0` | session boot 07-07 19:38 ET | log `live_v3_20260707.jsonl` | 12128 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 20:21:09 | **combined_over_goal** | KXITFMATCH-26JUL07TANCHE | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 12 graded (session)
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
| 20:45 | ITFWMATCH-26JUL07WANLEE-WAN | ITF_W | ? | 69 | 67 | +2 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 17 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 11, 'NO_FLOW': 6} | repriceable now: true 9 / false 8 | **cumulative bid_grade lines: 5131 (repriceable true 478 / false 4653)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07ISOTOM-TOM | 16 | 60m | 67/20-22/3362 | 20-21 | 4 | **FLOW_ABOVE** | 17 | REPRICEABLE→17 |
| ITFMATCH-26JUL07MOXSAR-MOX | 69 | 50m | 1/74-74/1 | 69-74 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL07MOXSAR-SAR | 26 | 8m | 0 | 26-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07NAKSHI-NAK | 39 | 58m | 1/43-43/2 | 39-43 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFMATCH-26JUL07NAKSHI-SHI | 57 | 59m | 1/61-61/1 | 57-61 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→61 |
| ITFMATCH-26JUL07TAKSAM-TAK | 9 | 60m | 253/11-35/15924 | 23-10 | 2 | **FLOW_ABOVE** | 9 | flow above but bound 9c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07YAMNAK-NAK | 7 | 15m | 4/10-10/62 | 7-10 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL07YAMNAK-YAM | 90 | 3m | 0 | 90-94 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07YAMTAN-TAN | 81 | 59m | 1/85-85/2 | 81-85 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFMATCH-26JUL07YAMTAN-YAM | 15 | 59m | 2/17-18/7 | 15-17 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→17 |
| ITFMATCH-26JUL08KIMROH-KIM | 64 | 29m | 1/68-68/2 | 64-68 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08KIMROH-ROH | 31 | 29m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LIUSHI-SHI | 13 | 20m | 0 | 13-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07CHOCAO-CHO | 49 | 80m | 1/50-50/1 | 49-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL07TIKCHO-TIK | 81 | 9m | 1/85-85/5 | 81-85 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFWMATCH-26JUL08LIXYAM-LIX | 8 | 41m | 0 | 8-9 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WUXSNI-SNI | 48 | 4m | 0 | 48-50 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL07TAKSAM | 88 | 10 | **98** | 97 | +1 |
| ITFMATCH-26JUL07ISOTOM | 80 | 21 | **101** | 97 | +4 |

## PATTERNS (sub-B) — 9
- half_arm_aging: KXITFMATCH-26JUL07OGUJAS-OGU {"fill": 25, "age_min": 81, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07DELKOY-DEL {"fill": 90, "age_min": 81, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07VANMIL-VAN {"fill": 47, "age_min": 77, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07ISOTOM-ISO {"fill": 80, "age_min": 61, "mode": "SET_BELOW_FLOW(prints 4c above)"}
- half_arm_aging: KXITFWMATCH-26JUL07ZHOLEO-ZHO {"fill": 17, "age_min": 42, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07ICHOCH-OCH {"fill": 29, "age_min": 41, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07TAKSAM-SAM {"fill": 88, "age_min": 37, "mode": "SET_BELOW_FLOW(prints 2c above)", "emitted_et": "2026-07-07 08:59:32 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL07KUSTAG-TAG {"fill": 62, "age_min": 35, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-07 08:59:32 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL07NASLEE-NAS {"fill": 72, "age_min": 31, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-07 08:59:32 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
