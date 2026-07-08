# LIVE VALIDATION — rolling status

- cycle 178 @ **2026-07-07 10:11:53 PM ET** | build `e9f1825` | session boot 07-07 19:38 ET | log `live_v3_20260707.jsonl` | 32988 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 20:21:09 | **combined_over_goal** | KXITFMATCH-26JUL07TANCHE | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 23 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:39 | ITFMATCH-26JUL07OGUJAS-OGU | ITF_M | ? | 25 | 21 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 19:39 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 90 | 87 | +3 (adopted_est) | — | pre | pair | 98 | PENDING |
| 19:42 | ATPCHALLENGERMATCH-26JUL07VANMIL-V | ATP_CHALL | ? | 47 | 44 | +3 (fill_est) | -4.0 | 1.4 | single |  | EARNED |
| 19:58 | ITFMATCH-26JUL07ISOTOM-ISO | ITF_M | ? | 80 | 77 | +3 (adopted_est) | — | pre | pair | 96 | PENDING |
| 20:17 | ITFWMATCH-26JUL07ZHOLEO-ZHO | ITF_W | ? | 17 | 13 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
| 20:18 | ITFMATCH-26JUL07TANCHE-TAN | ITF_M | underdog | 47 | 42 | +5 (place_cell) | — | pre | pair | 98 | PENDING |
| 20:18 | ITFMATCH-26JUL07ICHOCH-OCH | ITF_M | ? | 29 | 25 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 20:21 | ITFMATCH-26JUL07TANCHE-CHE | ITF_M | ? | 51 | 48 | +3 (adopted_est) | — | pre | pair | 98 | PENDING |
| 20:22 | ITFMATCH-26JUL07TAKSAM-SAM | ITF_M | ? | 88 | 85 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 20:24 | ITFMATCH-26JUL07KUSTAG-TAG | ITF_M | ? | 62 | 59 | +3 (adopted_est) | — | pre | pair | 96 | PENDING |
| 20:28 | ITFMATCH-26JUL07NASLEE-NAS | ITF_M | ? | 72 | 69 | +3 (adopted_est) | — | pre | pair | 99 | PENDING |
| 20:45 | ITFWMATCH-26JUL07WANLEE-WAN | ITF_W | ? | 69 | 67 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 21:05 | ITFMATCH-26JUL07ADAIMA-IMA | ITF_M | ? | 92 | 89 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 21:07 | ITFMATCH-26JUL07TAKSAM-TAK | ITF_M | underdog | 9 | 8 | +1 (place_cell) | — | pre | pair | 97 | PENDING |
| 21:12 | ITFMATCH-26JUL07KUSTAG-KUS | ITF_M | ? | 34 | 30 | +4 (adopted_est) | — | pre | pair | 96 | PENDING |
| 21:14 | ITFMATCH-26JUL07ISOTOM-TOM | ITF_M | underdog | 16 | 16 | +0 (place_cell) | — | pre | pair | 96 | PENDING |
| 21:27 | ITFMATCH-26JUL07IDOHON-IDO | ITF_M | ? | 7 | 3 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 21:34 | ITFMATCH-26JUL07OKIMAT-MAT | ITF_M | ? | 46 | 42 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 21:38 | ITFMATCH-26JUL07LEEHUX-LEE | ITF_M | ? | 69 | 66 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 21:48 | ITFWMATCH-26JUL08SEDSTA-STA | ITF_W | leader | 51 | 49 | +2 (place_cell) | — | pre | single |  | PENDING |
| 21:53 | ITFMATCH-26JUL07NASLEE-LEE | ITF_M | ? | 27 | 23 | +4 (adopted_est) | — | pre | pair | 99 | PENDING |
| 21:57 | ITFMATCH-26JUL07DELKOY-KOY | ITF_M | underdog | 8 | 4 | +4 (place_cell) | — | pre | pair | 98 | PENDING |
| 22:11 | ITFWMATCH-26JUL07ZHOLEO-LEO | ITF_W | ? | 81 | 79 | +2 (adopted_est) | — | pre | pair | 98 | PENDING |

## RESTING BIDS — 42 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 14, 'NO_FLOW': 27, 'FLOW_AT_LEVEL': 1} | repriceable now: true 13 / false 29 | **cumulative bid_grade lines: 5181 (repriceable true 485 / false 4696)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07KUSTAG-TAG | 63 | 30m | 612/61-78/48568 | 78-62 | -2 | **FLOW_AT_LEVEL** | 63 |  |
| ITFMATCH-26JUL07MOXSAR-MOX | 70 | 70m | 1/73-73/3 | 70-71 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL07MOXSAR-SAR | 29 | 5m | 0 | 29-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07NAKSHI-NAK | 39 | 131m | 1/43-43/2 | 39-43 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFMATCH-26JUL07NAKSHI-SHI | 57 | 131m | 4/60-61/98 | 57-60 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFMATCH-26JUL07NASLEE-LEE | 25 | 0m | 0 | 33-29 | — | **NO_FLOW** | 25 |  |
| ITFMATCH-26JUL07YAMNAK-NAK | 7 | 88m | 20/10-12/913 | 7-10 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL07YAMNAK-YAM | 90 | 75m | 1/94-94/1 | 90-92 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→94 |
| ITFMATCH-26JUL07YAMTAN-TAN | 81 | 131m | 2/85-85/5 | 81-85 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFMATCH-26JUL07YAMTAN-YAM | 15 | 131m | 3/17-18/145 | 15-17 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→17 |
| ITFMATCH-26JUL08KIMROH-KIM | 64 | 101m | 2/68-68/3 | 64-68 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08KIMROH-ROH | 31 | 101m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LIUSHI-SHI | 13 | 93m | 0 | 13-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SAKVAN-SAK | 25 | 11m | 0 | 26-26 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SAKVAN-VAN | 71 | 6m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07CHOCAO-CHO | 49 | 153m | 1/50-50/1 | 49-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL07TIKCHO-TIK | 82 | 7m | 1/84-84/1 | 82-84 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→84 |
| ITFWMATCH-26JUL07ZHOLEO-ZHO | 14 | 0m | 5/21-21/126 | 20-15 | 7 | **FLOW_ABOVE** | 16 | flow above but bound 16c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL08BALGOL-BAL | 38 | 11m | 0 | 38-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08BALGOL-GOL | 59 | 11m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CEUMCK-CEU | 74 | 11m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CEUMCK-MCK | 22 | 8m | 0 | 22-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-HAY | 65 | 11m | 0 | 65-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08IUSSAG-IUS | 66 | 21m | 0 | 66-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LIXYAM-LIX | 8 | 113m | 4/9-9/214 | 8-9 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL08LOVBRE-BRE | 33 | 8m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LOVBRE-LOV | 63 | 9m | 0 | 63-66 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MAMBEL-BEL | 12 | 41m | 1/15-15/125 | 12-15 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFWMATCH-26JUL08MAMBEL-MAM | 84 | 41m | 0 | 84-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NONYUA-NON | 14 | 71m | 0 | 14-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NONYUA-YUA | 83 | 36m | 1/86-86/28 | 83-86 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→86 |
| ITFWMATCH-26JUL08PUSBUR-BUR | 88 | 11m | 0 | 88-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PUSBUR-PUS | 7 | 11m | 0 | 7-11 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RICSTR-RIC | 26 | 11m | 0 | 26-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RICSTR-STR | 69 | 2m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SEDSTA-SED | 34 | 1m | 0 | 37-45 | — | **NO_FLOW** | 46 |  |
| ITFWMATCH-26JUL08SHEWAN-SHE | 38 | 71m | 0 | 38-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHEWAN-WAN | 59 | 46m | 0 | 59-62 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHOSUV-SUV | 9 | 4m | 0 | 9-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-PAN | 7 | 19m | 0 | 7-8 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANOHX-OHX | 18 | 54m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WUXSNI-SNI | 49 | 5m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08SEDSTA | 51 | 45 | **96** | 97 | -1 |

## PATTERNS (sub-B) — 10
- half_arm_aging: KXITFMATCH-26JUL07OGUJAS-OGU {"fill": 25, "age_min": 153, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07VANMIL-VAN {"fill": 47, "age_min": 149, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07ICHOCH-OCH {"fill": 29, "age_min": 113, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07WANLEE-WAN {"fill": 69, "age_min": 86, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07ADAIMA-IMA {"fill": 92, "age_min": 66, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07IDOHON-IDO {"fill": 7, "age_min": 44, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07OKIMAT-MAT {"fill": 46, "age_min": 37, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-07 10:11:53 PM ET"}
- half_arm_aging: KXITFMATCH-26JUL07LEEHUX-LEE {"fill": 69, "age_min": 34, "mode": "PAIRING(sib never rested)"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07NASLEE {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFWMATCH-26JUL07ZHOLEO {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-07 10:11:53 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
