# LIVE VALIDATION — rolling status

- cycle 127 @ **2026-07-07 01:07:07 PM ET** | build `01d8dec` | session boot 07-07 12:54 ET | log `live_v3_20260707.jsonl` | 5708 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 15 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 12:54 | ITFMATCH-26JUL07MARBAS-MAR | ITF_M | ? | 36 | 18 | +18 (window_cell) | — | pre | single |  | MIXED |
| 12:54 | ITFWMATCH-26JUL07EVAGOW-GOW | ITF_W | ? | 14 | 13 | +1 (window_cell) | — | pre | single |  | EARNED |
| 12:54 | ITFWMATCH-26JUL07GIADIA-GIA | ITF_W | ? | 34 | 30 | +4 (adopted_est) | -37.0 | pre | single |  | EARNED |
| 12:54 | ITFWMATCH-26JUL07MAROLU-OLU | ITF_W | ? | 30 | 26 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 12:54 | ATPCHALLENGERMATCH-26JUL07CLAHER-C | ATP_CHALL | ? | 44 | 41 | +3 (adopted_est) | -28.0 | pre | single |  | EARNED |
| 12:54 | ATPCHALLENGERMATCH-26JUL07AZKBON-A | ATP_CHALL | ? | 32 | 29 | +3 (adopted_est) | -63.5 | pre | single |  | EARNED |
| 12:55 | ITFWMATCH-26JUL07MOROLM-MOR | ITF_W | ? | 43 | 39 | +4 (fill_est) | — | pre | single |  | PENDING |
| 12:56 | ATPCHALLENGERMATCH-26JUL07SKAPET-S | ATP_CHALL | ? | 61 | 58 | +3 (adopted_est) | 4.5 | pre | single |  | GIFT_CLASS |
| 12:59 | ATPCHALLENGERMATCH-26JUL07MOESAN-S | ATP_CHALL | ? | 27 | 24 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 13:00 | ATPCHALLENGERMATCH-26JUL07OSOSOT-O | ATP_CHALL | ? | 20 | 17 | +3 (fill_est) | -18.5 | 4.2 | single |  | EARNED |
| 13:01 | ITFWMATCH-26JUL07ELJRAB-RAB | ITF_W | underdog | 40 | 38 | +2 (place_cell) | — | pre | single |  | MIXED |
| 13:04 | ITFMATCH-26JUL07SELWAS-WAS | ITF_M | ? | 36 | 32 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 13:06 | ATPCHALLENGERMATCH-26JUL07DROERH-E | ATP_CHALL | ? | 21 | 18 | +3 (fill_est) | -0.5 | 2.0 | single |  | MIXED |
| 13:06 | ATPCHALLENGERMATCH-26JUL07HERHAR-H | ATP_CHALL | ? | 19 | 17 | +2 (window_cell) | — | pre | single |  | MIXED |
| 13:06 | ITFMATCH-26JUL07MARLYN-LYN | ITF_M | ? | 59 | 56 | +3 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 6 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 4, 'FLOW_AT_LEVEL': 1, 'NO_FLOW': 1} | repriceable now: true 0 / false 6 | **cumulative bid_grade lines: 4876 (repriceable true 420 / false 4456)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07MOESAN-S | 26 | 3m | 17/55-57/1021 | 55-58 | 29 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07TOMSHI-S | 36 | 7m | 0 | 36-37 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL07MARBAS-BAS | 61 | 12m | 28/67-79/1727 | 61-63 | 6 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL07EVAGOW-GOW | 18 | 12m | 1/17-17/8 | 18-19 | -1 | **FLOW_AT_LEVEL** | 13 |  |
| ITFWMATCH-26JUL07SCHZID-ZID | 70 | 12m | 4/76-88/78 | 72-73 | 6 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL07OSAMUC-MUC | 44 | 12m | 6/99-99/437 | 97-98 | 55 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL07EVAGOW | 14 | 84 | **98** | 97 | +1 |
| ITFMATCH-26JUL07MARBAS | 36 | 63 | **99** | 97 | +2 |
| ATPCHALLENGERMATCH-26JUL07HERHAR | 19 | 84 | **103** | 97 | +6 |
| ITFWMATCH-26JUL07ELJRAB | 40 | 76 | **116** | 97 | +19 |

## PATTERNS (sub-B) — 4
- deep_neg_fv: KXITFWMATCH-26JUL07GIADIA-GIA {"entry_minus_fv_burst": -37.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07CLAHER-CLA {"entry_minus_fv_burst": -28.0, "emitted_et": "2026-07-07 01:07:07 PM ET"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07AZKBON-AZK {"entry_minus_fv_burst": -63.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07OSOSOT-OSO {"entry_minus_fv_burst": -18.5, "emitted_et": "2026-07-07 01:07:07 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
