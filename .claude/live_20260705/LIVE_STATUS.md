# LIVE VALIDATION — rolling status

- cycle 114 @ **2026-07-07 10:47:59 AM ET** | build `fea5aa0` | session boot 07-07 10:21 ET | log `live_v3_20260707.jsonl` | 18794 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 10:38:44 | **grace_breach** | KXATPMATCH-26JUL07AUGDJO-DJO | fill 61c 5.7min past latch (grace 300s) |
| 10:38:44 | **combined_over_goal** | KXATPMATCH-26JUL07AUGDJO | pair combined 100c > goal 97c [complete_cross_insurance: cap102 by design (d?)] |

## FILLS — 35 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10:21 | WTACHALLENGERMATCH-26JUL07ZANJAC-Z | WTA_CHALL | ? | 28 | 25 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | WTACHALLENGERMATCH-26JUL07ZANJAC-J | WTA_CHALL | ? | 69 | 66 | +3 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | ITFMATCH-26JUL07MOUMON-MOU | ITF_M | ? | 34 | 30 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
| 10:21 | ATPCHALLENGERMATCH-26JUL07HAMWAL-H | ATP_CHALL | ? | 13 | 11 | +2 (window_cell) | — | pre | single |  | MIXED |
| 10:21 | ITFWMATCH-26JUL07BUEXAV-XAV | ITF_W | ? | 68 | 66 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 10:21 | ATPCHALLENGERMATCH-26JUL07GASCHE-C | ATP_CHALL | ? | 24 | 21 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 10:21 | ITFWMATCH-26JUL07SIMROU-SIM | ITF_W | ? | 33 | 66 | -33 (window_cell) | -61.5 | pre | single |  | EARNED |
| 10:21 | ITFWMATCH-26JUL07KHRYOU-KHR | ITF_W | ? | 44 | 40 | +4 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | ITFWMATCH-26JUL07KHRYOU-YOU | ITF_W | ? | 53 | 51 | +2 (adopted_est) | — | pre | pair | 97 | PENDING |
| 10:21 | ATPCHALLENGERMATCH-26JUL07WALVAL-W | ATP_CHALL | ? | 32 | 2 | +30 (window_cell) | — | pre | single |  | MIXED |
| 10:21 | ITFWMATCH-26JUL07GUESAN-SAN | ITF_W | ? | 8 | 4 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 10:21 | ITFMATCH-26JUL07URSPOU-POU | ITF_M | ? | 50 | 33 | +17 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 10:21 | ITFWMATCH-26JUL07MALKOM-KOM | ITF_W | ? | 10 | 6 | +4 (adopted_est) | -9.0 | pre | single |  | EARNED |
| 10:21 | ITFWMATCH-26JUL07VRARUG-RUG | ITF_W | ? | 61 | 43 | +18 (window_cell) | 30.5 | pre | single |  | GIFT_CLASS |
| 10:23 | ATPCHALLENGERMATCH-26JUL07ZAHSEA-S | ATP_CHALL | ? | 82 | 79 | +3 (fill_est) | -2.5 | pre | single |  | MIXED |
| 10:23 | ITFWMATCH-26JUL07MELDIG-MEL | ITF_W | underdog | 4 | 2 | +2 (place_cell) | — | pre | pair | 95 | PENDING |
| 10:23 | ATPCHALLENGERMATCH-26JUL07GUEDON-D | ATP_CHALL | ? | 29 | 29 | +0 (window_cell) | — | pre | single |  | EARNED |
| 10:25 | WTACHALLENGERMATCH-26JUL07GALRIN-G | WTA_CHALL | ? | 63 | 60 | +3 (fill_est) | -7.5 | 0.8 | single |  | EARNED |
| 10:25 | ITFMATCH-26JUL07GAGMED-MED | ITF_M | ? | 10 | 6 | +4 (fill_est) | -5.5 | 1.1 | single |  | EARNED |
| 10:25 | ITFMATCH-26JUL07TSIHER-TSI | ITF_M | ? | 50 | 47 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 10:27 | ITFWMATCH-26JUL07MELROD-MEL | ITF_W | ? | 74 | 72 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 10:27 | ATPCHALLENGERMATCH-26JUL07BROWEH-W | ATP_CHALL | ? | 35 | 32 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 10:28 | ITFMATCH-26JUL07URSPOU-URS | ITF_M | ? | 47 | 60 | -13 (window_cell) | — | pre | pair | 97 | EARNED |
| 10:29 | ITFWMATCH-26JUL07BROGAR-GAR | ITF_W | ? | 5 | 1 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 10:29 | ATPCHALLENGERMATCH-26JUL07RODAND-R | ATP_CHALL | ? | 39 | 36 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 10:31 | ITFWMATCH-26JUL07ARCOLI-OLI | ITF_W | ? | 72 | 70 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 10:31 | ITFWMATCH-26JUL07MELDIG-DIG | ITF_W | ? | 91 | 89 | +2 (adopted_est) | — | pre | pair | 95 | PENDING |
| 10:33 | ATPCHALLENGERMATCH-26JUL07POLHEI-H | ATP_CHALL | ? | 92 | 91 | +1 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 10:34 | ATPMATCH-26JUL07AUGDJO-AUG | ATP_MAIN | underdog | 39 | 37 | +2 (place_cell) | -0.5 | 1.7 | pair | 100 | MIXED |
| 10:37 | WTACHALLENGERMATCH-26JUL07SCOSTO-S | WTA_CHALL | leader | 82 | 79 | +3 (place_cell) | — | pre | single |  | PENDING |
| 10:38 | ATPMATCH-26JUL07AUGDJO-DJO | ATP_MAIN | leader | 61 | 60 | +1 (place_cell) | -0.5 | 5.7 | pair | 100 | MIXED |
| 10:40 | ITFMATCH-26JUL07MOUMON-MON | ITF_M | ? | 64 | 61 | +3 (adopted_est) | — | pre | pair | 98 | PENDING |
| 10:40 | WTACHALLENGERMATCH-26JUL07ZAALEP-Z | WTA_CHALL | ? | 58 | 55 | +3 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 10:41 | ITFMATCH-26JUL07GREKAS-GRE | ITF_M | ? | 91 | 88 | +3 (adopted_est) | — | pre | pair | 99 | PENDING |
| 10:44 | ITFMATCH-26JUL07GREKAS-KAS | ITF_M | ? | 8 | 4 | +4 (adopted_est) | — | pre | pair | 99 | PENDING |

## RESTING BIDS — 17 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 9, 'FLOW_AT_LEVEL': 2} | repriceable now: true 1 / false 16 | **cumulative bid_grade lines: 4791 (repriceable true 414 / false 4377)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07KRUPIE-K | 60 | 0m | 5/84-85/205 | 84-76 | 24 | **FLOW_ABOVE** | 67 | flow above but bound 67c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07MARBER-B | 58 | 20m | 230/32-72/14400 | 32-33 | -26 | **FLOW_AT_LEVEL** | 61 |  |
| ATPCHALLENGERMATCH-26JUL07POLHEI-P | 4 | 11m | 98/2-12/17231 | 2-2 | -2 | **FLOW_AT_LEVEL** | 4 |  |
| ATPCHALLENGERMATCH-26JUL07POPPDA-P | 57 | 1m | 0 | 57-58 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07ARSWIL-ARS | 46 | 18m | 0 | 46-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07ARSWIL-WIL | 52 | 17m | 0 | 52-54 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07COXBRA-BRA | 4 | 18m | 0 | 20-79 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07DELFER-FER | 6 | 25m | 8/10-40/48 | 7-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| ITFMATCH-26JUL07GREKAS-KAS | 6 | 2m | 1/22-22/4 | 9-22 | 16 | **FLOW_ABOVE** | 6 | flow above but bound 6c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07IAMGAL-GAL | 57 | 26m | 47/79-86/3431 | 83-83 | 22 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL07STRGUR-GUR | 9 | 17m | 0 | 9-10 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07STRGUR-STR | 91 | 16m | 0 | 91-93 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07JAUMAT-JAU | 47 | 26m | 55/70-91/12043 | 84-85 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07MCNREE-REE | 54 | 26m | 30/61-89/1310 | 86-86 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL07MELROD-ROD | 7 | 20m | 0 | 11-25 | — | **NO_FLOW** | 23 |  |
| WTACHALLENGERMATCH-26JUL07SCOSTO-S | 15 | 10m | 0 | 18-19 | — | **NO_FLOW** | 15 |  |
| WTACHALLENGERMATCH-26JUL07SEBBRA-B | 51 | 26m | 0 | 51-52 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL07SIMROU | 33 | 2 | **35** | 97 | -62 |
| ATPCHALLENGERMATCH-26JUL07POLHEI | 92 | 2 | **94** | 97 | -3 |
| ITFWMATCH-26JUL07MELROD | 74 | 25 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL07HAMWAL | 13 | 87 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL07GUEDON | 29 | 71 | **100** | 97 | +3 |
| ITFWMATCH-26JUL07VRARUG | 61 | 40 | **101** | 97 | +4 |
| WTACHALLENGERMATCH-26JUL07SCOSTO | 82 | 19 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL07BROWEH | 35 | 67 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL07WALVAL | 32 | 98 | **130** | 97 | +33 |

## PATTERNS (sub-B) — 4
- deep_neg_fv: KXITFWMATCH-26JUL07SIMROU-SIM {"entry_minus_fv_burst": -61.5, "emitted_et": "2026-07-07 10:47:59 AM ET"}
- deep_neg_fv: KXITFWMATCH-26JUL07MALKOM-KOM {"entry_minus_fv_burst": -9.0, "emitted_et": "2026-07-07 10:47:59 AM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07MOUMON {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-07 10:47:59 AM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07GREKAS {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-07 10:47:59 AM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
