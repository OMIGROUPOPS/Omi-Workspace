# LIVE VALIDATION — rolling status

- cycle 130 @ **2026-07-07 01:38:26 PM ET** | build `6489bd0` | session boot 07-07 13:13 ET | log `live_v3_20260707.jsonl` | 11282 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 21 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 13:13 | ITFWMATCH-26JUL07MIKPAQ-PAQ | ITF_W | ? | 70 | 68 | +2 (adopted_est) | — | pre | pair | 96 | PENDING |
| 13:13 | ITFMATCH-26JUL07RICMAR-RIC | ITF_M | ? | 53 | 50 | +3 (adopted_est) | — | pre | pair | 98 | PENDING |
| 13:13 | ITFMATCH-26JUL07RICMAR-MAR | ITF_M | ? | 45 | 41 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
| 13:13 | ITFWMATCH-26JUL07EVAGOW-GOW | ITF_W | ? | 14 | 30 | -16 (window_cell) | -8.5 | pre | single |  | EARNED |
| 13:13 | ITFWMATCH-26JUL07GIADIA-GIA | ITF_W | ? | 34 | 30 | +4 (adopted_est) | -60.0 | pre | single |  | EARNED |
| 13:13 | ITFWMATCH-26JUL07MAROLU-OLU | ITF_W | ? | 30 | 26 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 13:13 | ATPCHALLENGERMATCH-26JUL07CLAHER-C | ATP_CHALL | ? | 44 | 41 | +3 (adopted_est) | -18.5 | pre | single |  | EARNED |
| 13:14 | ITFWMATCH-26JUL07SCHZID-SCH | ITF_W | ? | 27 | 7 | +20 (window_cell) | — | pre | single |  | MIXED |
| 13:16 | ITFWMATCH-26JUL07MIKPAQ-MIK | ITF_W | ? | 26 | 22 | +4 (fill_est) | — | pre | pair | 96 | PENDING |
| 13:16 | ITFWMATCH-26JUL07MOROLM-OLM | ITF_W | ? | 54 | 52 | +2 (fill_est) | — | pre | single |  | PENDING |
| 13:18 | ATPCHALLENGERMATCH-26JUL07MOESAN-S | ATP_CHALL | ? | 26 | 23 | +3 (fill_est) | -15.5 | 0.9 | single |  | EARNED |
| 13:18 | ATPCHALLENGERMATCH-26JUL07ONCCAM-C | ATP_CHALL | ? | 20 | 35 | -15 (window_cell) | -37.0 | pre | single |  | EARNED |
| 13:18 | ITFWMATCH-26JUL07FERMED-MED | ITF_W | ? | 86 | 84 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 13:18 | ITFWMATCH-26JUL07SCHCAN-CAN | ITF_W | ? | 84 | 82 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 13:22 | ATPCHALLENGERMATCH-26JUL07SKAPET-P | ATP_CHALL | ? | 36 | 33 | +3 (fill_est) | -12.0 | 3.9 | single |  | EARNED |
| 13:22 | ATPCHALLENGERMATCH-26JUL06MCDWAL-M | ATP_CHALL | ? | 47 | 44 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 13:24 | ATPCHALLENGERMATCH-26JUL07JANGIL-J | ATP_CHALL | ? | 18 | 15 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 13:25 | ITFMATCH-26JUL07KAMMIY-KAM | ITF_M | ? | 5 | 1 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 13:26 | ITFWMATCH-26JUL07AKLRAP-RAP | ITF_W | ? | 44 | 40 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 13:29 | ITFWMATCH-26JUL07ELJRAB-ELJ | ITF_W | ? | 57 | 78 | -21 (window_cell) | — | pre | single |  | MIXED |
| 13:35 | ITFMATCH-26JUL07PUTVAS-VAS | ITF_M | ? | 93 | 90 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 11 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 6, 'FLOW_ABOVE': 4, 'FLOW_AT_LEVEL': 1} | repriceable now: true 1 / false 10 | **cumulative bid_grade lines: 4901 (repriceable true 422 / false 4479)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07DROERH-E | 23 | 5m | 28/23-30/3306 | 29-26 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07HERHAR-H | 15 | 14m | 143/21-40/22235 | 24-25 | 6 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07MENAVE-M | 61 | 10m | 1/62-62/5 | 61-62 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→62 |
| ATPCHALLENGERMATCH-26JUL07PACMEL-M | 48 | 24m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07PACMEL-P | 51 | 24m | 0 | 51-52 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07ROYNEU-R | 89 | 13m | 35/97-99/9062 | 98-99 | 8 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07DAYDEA-DAY | 56 | 10m | 0 | 56-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07ZHALEE-LEE | 44 | 5m | 0 | 44-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07KAYDUN-KAY | 32 | 5m | 0 | 32-62 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07KELXUX-KEL | 33 | 12m | 0 | 33-36 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07SCHCAN-SCH | 13 | 17m | 1/16-16/1 | 14-20 | 3 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07ONCCAM | 20 | 61 | **81** | 97 | -16 |
| ITFWMATCH-26JUL07EVAGOW | 14 | 80 | **94** | 97 | -3 |
| ITFWMATCH-26JUL07ELJRAB | 57 | 45 | **102** | 97 | +5 |
| ITFWMATCH-26JUL07SCHCAN | 84 | 20 | **104** | 97 | +7 |
| ITFWMATCH-26JUL07SCHZID | 27 | 85 | **112** | 97 | +15 |

## PATTERNS (sub-B) — 8
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07RICMAR {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- deep_neg_fv: KXITFWMATCH-26JUL07EVAGOW-GOW {"entry_minus_fv_burst": -8.5}
- deep_neg_fv: KXITFWMATCH-26JUL07GIADIA-GIA {"entry_minus_fv_burst": -60.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07CLAHER-CLA {"entry_minus_fv_burst": -18.5}
- pre_conception_buy: KXITFWMATCH-26JUL07SCHZID-SCH {"price": 27, "conception_ts": 1783445411.2336688, "detail": "buy 27c predates the conception stamp by 17min \u2014 honest-window buy, cap not yet defined (ungradeable)", "emitted_et": "2026-07-07 01:38:26 PM ET"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07MOESAN-SAN {"entry_minus_fv_burst": -15.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07ONCCAM-CAM {"entry_minus_fv_burst": -37.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07SKAPET-PET {"entry_minus_fv_burst": -12.0}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
