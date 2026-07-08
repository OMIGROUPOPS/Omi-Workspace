# LIVE VALIDATION — rolling status

- cycle 179 @ **2026-07-07 10:22:18 PM ET** | build `3d5f58e` | session boot 07-07 19:38 ET | log `live_v3_20260707.jsonl` | 36108 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 20:21:09 | **combined_over_goal** | KXITFMATCH-26JUL07TANCHE | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 27 graded (session)
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
| 20:45 | ITFWMATCH-26JUL07WANLEE-WAN | ITF_W | ? | 69 | 67 | +2 (adopted_est) | — | pre | pair | 101 | PENDING |
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
| 22:12 | ITFWMATCH-26JUL07TIKCHO-TIK | ITF_W | leader | 82 | 83 | -1 (place_cell) | — | pre | single |  | PENDING |
| 22:12 | ITFWMATCH-26JUL07DESZHA-DES | ITF_W | ? | 28 | 24 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 22:17 | ITFWMATCH-26JUL07WANLEE-LEE | ITF_W | ? | 32 | 28 | +4 (adopted_est) | — | pre | pair | 101 | PENDING |
| 22:19 | ITFMATCH-26JUL07CHENOR-CHE | ITF_M | ? | 23 | 19 | +4 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 44 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 13, 'NO_FLOW': 29, 'FLOW_AT_LEVEL': 2} | repriceable now: true 12 / false 32 | **cumulative bid_grade lines: 5190 (repriceable true 486 / false 4704)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07KUSTAG-TAG | 63 | 41m | 1074/54-86/77008 | 84-55 | -9 | **FLOW_AT_LEVEL** | 63 |  |
| ITFMATCH-26JUL07LEEHUX-LEE | 69 | 8m | 101/59-86/8229 | 77-59 | -10 | **FLOW_AT_LEVEL** | 99 |  |
| ITFMATCH-26JUL07MOXSAR-MOX | 70 | 81m | 1/73-73/3 | 70-71 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL07MOXSAR-SAR | 29 | 15m | 0 | 29-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07NAKSHI-NAK | 40 | 2m | 0 | 40-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07NAKSHI-SHI | 57 | 141m | 4/60-61/98 | 57-60 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFMATCH-26JUL07NASLEE-LEE | 25 | 2m | 54/33-43/3098 | 41-29 | 8 | **FLOW_ABOVE** | 25 | flow above but bound 25c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07YAMNAK-NAK | 7 | 98m | 24/9-12/1045 | 7-9 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFMATCH-26JUL07YAMNAK-YAM | 90 | 86m | 1/94-94/1 | 90-92 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→94 |
| ITFMATCH-26JUL07YAMTAN-TAN | 81 | 141m | 2/85-85/5 | 81-85 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFMATCH-26JUL07YAMTAN-YAM | 15 | 141m | 3/17-18/145 | 15-17 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→17 |
| ITFMATCH-26JUL08KIMROH-KIM | 64 | 112m | 2/68-68/3 | 64-68 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08KIMROH-ROH | 31 | 112m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LIUSHI-SHI | 15 | 1m | 0 | 15-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SAKVAN-SAK | 25 | 22m | 0 | 27-26 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SAKVAN-VAN | 71 | 16m | 0 | 71-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07CHOCAO-CHO | 49 | 163m | 1/50-50/1 | 49-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL08BALGOL-BAL | 38 | 22m | 0 | 38-42 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08BALGOL-GOL | 59 | 22m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CEUMCK-CEU | 74 | 22m | 0 | 74-78 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CEUMCK-MCK | 22 | 18m | 0 | 22-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-HAY | 65 | 22m | 0 | 65-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08IUSSAG-IUS | 66 | 31m | 0 | 66-70 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08IUSSAG-SAG | 31 | 2m | 0 | 31-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LIUMAL-LIU | 26 | 6m | 0 | 26-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LIUMAL-MAL | 71 | 6m | 0 | 71-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LIXYAM-LIX | 8 | 123m | 4/9-9/214 | 8-9 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL08LOVBRE-BRE | 33 | 18m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LOVBRE-LOV | 63 | 20m | 0 | 63-66 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MAMBEL-BEL | 12 | 52m | 1/15-15/125 | 12-15 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFWMATCH-26JUL08MAMBEL-MAM | 84 | 52m | 0 | 84-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NONYUA-NON | 14 | 81m | 0 | 14-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NONYUA-YUA | 83 | 46m | 1/86-86/28 | 83-86 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→86 |
| ITFWMATCH-26JUL08PUSBUR-BUR | 88 | 22m | 0 | 88-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PUSBUR-PUS | 7 | 22m | 0 | 7-11 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RICSTR-RIC | 26 | 22m | 0 | 26-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RICSTR-STR | 69 | 12m | 0 | 69-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SEDSTA-SED | 44 | 4m | 0 | 49-45 | — | **NO_FLOW** | 46 |  |
| ITFWMATCH-26JUL08SHEWAN-SHE | 38 | 81m | 0 | 38-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHEWAN-WAN | 59 | 56m | 0 | 59-62 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHOSUV-SUV | 45 | 5m | 1/47-47/1 | 45-47 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFWMATCH-26JUL08TUPPAN-PAN | 7 | 29m | 0 | 7-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANOHX-OHX | 18 | 65m | 0 | 18-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WUXSNI-SNI | 49 | 16m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08SEDSTA | 51 | 45 | **96** | 97 | -1 |

## PATTERNS (sub-B) — 11
- half_arm_aging: KXITFMATCH-26JUL07OGUJAS-OGU {"fill": 25, "age_min": 163, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07VANMIL-VAN {"fill": 47, "age_min": 160, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07ICHOCH-OCH {"fill": 29, "age_min": 123, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07ADAIMA-IMA {"fill": 92, "age_min": 77, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07IDOHON-IDO {"fill": 7, "age_min": 55, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07OKIMAT-MAT {"fill": 46, "age_min": 47, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07LEEHUX-LEE {"fill": 69, "age_min": 44, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL08SEDSTA-STA {"fill": 51, "age_min": 34, "mode": "STARVATION(no prints since post)", "emitted_et": "2026-07-07 10:22:18 PM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07NASLEE {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFWMATCH-26JUL07ZHOLEO {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFWMATCH-26JUL07WANLEE {"combined": 101, "detail": "pair combined 101c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-07 10:22:18 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
