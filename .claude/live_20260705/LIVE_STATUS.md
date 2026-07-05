# LIVE VALIDATION — rolling status

- cycle 1 @ **2026-07-05 11:04:18 AM ET** | build `2a45964` | session boot 07-05 10:39 ET | log `live_v3_20260705.jsonl` | 4217 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 10:48:45 | **grace_breach** | KXITFMATCH-26JUL05SALCON-CON | fill 13c 5.2min past latch (grace 300s) |

## FILLS — 15 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10:39 | ITFWMATCH-26JUL05TRAABB-ABB | ITF_W | ? | 64 | 64 | +0 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 10:39 | ATPCHALLENGERMATCH-26JUL05RAMNEU-R | ATP_CHALL | ? | 36 | 2 | +34 (window_cell) | — | pre | single |  | MIXED |
| 10:39 | ATPCHALLENGERMATCH-26JUL05WEHIFI-I | ATP_CHALL | ? | 11 | 8 | +3 (adopted_est) | 5.5 | pre | single |  | GIFT_CLASS |
| 10:39 | WTACHALLENGERMATCH-26JUL05DITLEW-D | WTA_CHALL | ? | 31 | 28 | +3 (adopted_est) | 25.5 | pre | single |  | GIFT_CLASS |
| 10:39 | ATPCHALLENGERMATCH-26JUL05KUZMAT-M | ATP_CHALL | ? | 5 | 2 | +3 (adopted_est) | -2.5 | pre | single |  | MIXED |
| 10:40 | ITFWMATCH-26JUL05AITDAE-AIT | ITF_W | underdog | 8 | 4 | +4 (place_cell) | — | pre | single |  | MIXED |
| 10:41 | ATPCHALLENGERMATCH-26JUL05VALREJ-V | ATP_CHALL | leader | 62 | 71 | -9 (place_cell) | 11.5 | pre | single |  | GIFT_CLASS |
| 10:41 | ATPCHALLENGERMATCH-26JUL05CIZCAZ-C | ATP_CHALL | underdog | 23 | 19 | +4 (place_cell) | — | pre | single |  | MIXED |
| 10:41 | ITFMATCH-26JUL05GELBRE-GEL | ITF_M | ? | 44 | 40 | +4 (window_cell) | — | pre | pair | 92 | MIXED |
| 10:42 | WTAMATCH-26JUL05BENGAU-GAU | WTA_MAIN | ? | 50 | 50 | +0 (adopted_est) | — | pre | single |  | PENDING |
| 10:48 | ITFMATCH-26JUL05SALCON-CON | ITF_M | ? | 13 | 29 | -16 (window_cell) | -10.0 | 5.2 | single |  | EARNED |
| 10:53 | ITFMATCH-26JUL05GELBRE-BRE | ITF_M | ? | 48 | 56 | -8 (window_cell) | — | pre | pair | 92 | EARNED |
| 10:53 | ATPCHALLENGERMATCH-26JUL05PEROPI-O | ATP_CHALL | ? | 25 | 22 | +3 (window_cell) | — | pre | single |  | MIXED |
| 10:55 | ATPCHALLENGERMATCH-26JUL05INGFEL-F | ATP_CHALL | ? | 72 | 72 | +0 (adopted_est) | — | pre | single |  | PENDING |
| 11:02 | ITFWMATCH-26JUL05TRAABB-TRA | ITF_W | ? | 33 | 29 | +4 (window_cell) | — | pre | pair | 97 | MIXED |

## RESTING BIDS — 17 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 10, 'FLOW_AT_LEVEL': 1} | repriceable now: true 1 / false 16 | **cumulative bid_grade lines: 656 (repriceable true 58 / false 598)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL05BANMAR-B | 65 | 24m | 0 | 65-66 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05BANMAR-M | 33 | 24m | 2/36-36/132 | 33-37 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05DALARI-D | 91 | 7m | 19/97-99/2285 | 98-97 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-E | 65 | 24m | 0 | 65-67 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05ELLJOH-J | 33 | 24m | 0 | 33-34 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GANZIN-G | 28 | 24m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05GANZIN-Z | 70 | 24m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PDACAS-C | 39 | 3m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05PDACAS-P | 61 | 3m | 0 | 61-62 | — | **NO_FLOW** | 62 |  |
| ATPCHALLENGERMATCH-26JUL05POTANG-P | 50 | 24m | 2/55-55/4 | 53-55 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL05RAMNEU-N | 61 | 24m | 17/98-99/2359 | 99-98 | 37 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL05STEDIN-S | 26 | 24m | 119/32-63/7406 | 34-33 | 6 | **FLOW_ABOVE** | 55 |  |
| ITFMATCH-26JUL05GELBRE-GEL | 46 | 11m | 28/38-62/2243 | 33-35 | -8 | **FLOW_AT_LEVEL** | 40 |  |
| ITFMATCH-26JUL05SABMIS-SAB | 18 | 1m | 0 | 18-91 | — | **NO_FLOW** | 81 |  |
| ITFWMATCH-26JUL05TUBSOB-SOB | 25 | 24m | 76/29-45/1791 | 37-42 | 4 | **FLOW_ABOVE** | 30 | REPRICEABLE→29 |
| WTACHALLENGERMATCH-26JUL05YAMOVC-O | 28 | 24m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL05YAMOVC-Y | 70 | 24m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL05SALCON | 13 | 87 | **100** | 97 | +3 |
| ITFWMATCH-26JUL05AITDAE | 8 | 93 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL05PEROPI | 25 | 78 | **103** | 97 | +6 |
| ATPCHALLENGERMATCH-26JUL05CIZCAZ | 23 | 84 | **107** | 97 | +10 |
| ATPCHALLENGERMATCH-26JUL05VALREJ | 62 | 71 | **133** | 97 | +36 |
| ATPCHALLENGERMATCH-26JUL05RAMNEU | 36 | 98 | **134** | 97 | +37 |

## PATTERNS (sub-B) — 1
- deep_neg_fv: KXITFMATCH-26JUL05SALCON-CON {"entry_minus_fv_burst": -10.0}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
