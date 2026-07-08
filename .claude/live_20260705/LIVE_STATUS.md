# LIVE VALIDATION — rolling status

- cycle 177 @ **2026-07-07 10:01:33 PM ET** | build `fd806dc` | session boot 07-07 19:38 ET | log `live_v3_20260707.jsonl` | 30571 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 20:21:09 | **combined_over_goal** | KXITFMATCH-26JUL07TANCHE | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 22 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 19:39 | ITFMATCH-26JUL07OGUJAS-OGU | ITF_M | ? | 25 | 21 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 19:39 | ITFMATCH-26JUL07DELKOY-DEL | ITF_M | ? | 90 | 87 | +3 (adopted_est) | — | pre | pair | 98 | PENDING |
| 19:42 | ATPCHALLENGERMATCH-26JUL07VANMIL-V | ATP_CHALL | ? | 47 | 44 | +3 (fill_est) | -4.0 | 1.4 | single |  | EARNED |
| 19:58 | ITFMATCH-26JUL07ISOTOM-ISO | ITF_M | ? | 80 | 77 | +3 (adopted_est) | — | pre | pair | 96 | PENDING |
| 20:17 | ITFWMATCH-26JUL07ZHOLEO-ZHO | ITF_W | ? | 17 | 13 | +4 (adopted_est) | — | pre | single |  | PENDING |
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

## RESTING BIDS — 39 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 13, 'NO_FLOW': 24, 'FLOW_AT_LEVEL': 2} | repriceable now: true 12 / false 27 | **cumulative bid_grade lines: 5168 (repriceable true 483 / false 4685)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL07KUSTAG-TAG | 63 | 20m | 331/62-78/22946 | 78-63 | -1 | **FLOW_AT_LEVEL** | 63 |  |
| ITFMATCH-26JUL07MOXSAR-MOX | 70 | 60m | 1/73-73/3 | 70-71 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→73 |
| ITFMATCH-26JUL07MOXSAR-SAR | 28 | 3m | 0 | 28-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07NAKSHI-NAK | 39 | 120m | 1/43-43/2 | 39-43 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFMATCH-26JUL07NAKSHI-SHI | 57 | 121m | 4/60-61/98 | 57-60 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| ITFMATCH-26JUL07YAMNAK-NAK | 7 | 77m | 13/10-10/689 | 7-10 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL07YAMNAK-YAM | 90 | 65m | 1/94-94/1 | 90-94 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→94 |
| ITFMATCH-26JUL07YAMTAN-TAN | 81 | 121m | 2/85-85/5 | 81-85 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→85 |
| ITFMATCH-26JUL07YAMTAN-YAM | 15 | 121m | 3/17-18/145 | 15-17 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→17 |
| ITFMATCH-26JUL08KIMROH-KIM | 64 | 91m | 2/68-68/3 | 64-68 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08KIMROH-ROH | 31 | 91m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LIUSHI-SHI | 13 | 82m | 0 | 13-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08SAKVAN-SAK | 25 | 1m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07CHOCAO-CHO | 49 | 142m | 1/50-50/1 | 49-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |
| ITFWMATCH-26JUL07TIKCHO-TIK | 81 | 71m | 5/81-85/45 | 81-85 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL08BALGOL-BAL | 38 | 1m | 0 | 38-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08BALGOL-GOL | 59 | 1m | 0 | 59-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CEUMCK-CEU | 74 | 1m | 0 | 74-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CEUMCK-MCK | 20 | 1m | 0 | 20-25 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-GIO | 31 | 1m | 0 | 31-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08HAYGIO-HAY | 65 | 1m | 0 | 65-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08IUSSAG-IUS | 66 | 11m | 0 | 66-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08LIXYAM-LIX | 8 | 103m | 4/9-9/214 | 8-9 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL08MAMBEL-BEL | 12 | 31m | 0 | 12-15 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08MAMBEL-MAM | 84 | 31m | 0 | 84-88 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NONYUA-NON | 14 | 61m | 0 | 14-17 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NONYUA-YUA | 83 | 26m | 1/86-86/28 | 83-86 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→86 |
| ITFWMATCH-26JUL08PUSBUR-BUR | 88 | 1m | 0 | 88-91 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08PUSBUR-PUS | 7 | 1m | 0 | 7-11 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RICSTR-RIC | 26 | 1m | 0 | 26-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RICSTR-STR | 68 | 1m | 0 | 68-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SEDSTA-SED | 28 | 1m | 0 | 29-45 | — | **NO_FLOW** | 46 |  |
| ITFWMATCH-26JUL08SHEWAN-SHE | 38 | 60m | 0 | 38-41 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHEWAN-WAN | 59 | 35m | 0 | 59-62 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SHOSUV-SUV | 6 | 27m | 0 | 6-82 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-PAN | 7 | 8m | 0 | 7-43 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TUPPAN-TUP | 18 | 32m | 2/92-93/16 | 66-92 | 74 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08WANOHX-OHX | 18 | 44m | 0 | 18-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WUXSNI-SNI | 48 | 66m | 2/50-50/10 | 48-50 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→50 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL08SEDSTA | 51 | 45 | **96** | 97 | -1 |

## PATTERNS (sub-B) — 8
- half_arm_aging: KXITFMATCH-26JUL07OGUJAS-OGU {"fill": 25, "age_min": 143, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL07VANMIL-VAN {"fill": 47, "age_min": 139, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07ZHOLEO-ZHO {"fill": 17, "age_min": 104, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07ICHOCH-OCH {"fill": 29, "age_min": 103, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFWMATCH-26JUL07WANLEE-WAN {"fill": 69, "age_min": 76, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07ADAIMA-IMA {"fill": 92, "age_min": 56, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL07IDOHON-IDO {"fill": 7, "age_min": 34, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-07 10:01:33 PM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07NASLEE {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-07 10:01:33 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
