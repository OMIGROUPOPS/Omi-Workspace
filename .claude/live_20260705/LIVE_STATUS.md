# LIVE VALIDATION — rolling status

- cycle 129 @ **2026-07-07 01:28:06 PM ET** | build `9d34880` | session boot 07-07 13:13 ET | log `live_v3_20260707.jsonl` | 6614 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 19 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 13:13 | ITFWMATCH-26JUL07MIKPAQ-PAQ | ITF_W | ? | 70 | 68 | +2 (adopted_est) | — | pre | pair | 96 | PENDING |
| 13:13 | ITFMATCH-26JUL07RICMAR-RIC | ITF_M | ? | 53 | 50 | +3 (adopted_est) | — | pre | pair | 98 | PENDING |
| 13:13 | ITFMATCH-26JUL07RICMAR-MAR | ITF_M | ? | 45 | 41 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
| 13:13 | ITFWMATCH-26JUL07EVAGOW-GOW | ITF_W | ? | 14 | 30 | -16 (window_cell) | -8.5 | pre | single |  | EARNED |
| 13:13 | ITFWMATCH-26JUL07GIADIA-GIA | ITF_W | ? | 34 | 30 | +4 (adopted_est) | -60.0 | pre | single |  | EARNED |
| 13:13 | ITFWMATCH-26JUL07MAROLU-OLU | ITF_W | ? | 30 | 26 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 13:13 | ATPCHALLENGERMATCH-26JUL07CLAHER-C | ATP_CHALL | ? | 44 | 41 | +3 (adopted_est) | -18.5 | pre | single |  | EARNED |
| 13:14 | ITFWMATCH-26JUL07SCHZID-SCH | ITF_W | ? | 27 | 23 | +4 (fill_est) | — | pre | single |  | PENDING |
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

## RESTING BIDS — 9 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 3, 'NO_FLOW': 6} | repriceable now: true 1 / false 8 | **cumulative bid_grade lines: 4895 (repriceable true 421 / false 4474)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07HERHAR-H | 15 | 3m | 25/22-28/1046 | 24-22 | 7 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL07PACMEL-M | 48 | 14m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07PACMEL-P | 51 | 14m | 0 | 51-52 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL07ROYNEU-R | 89 | 2m | 9/98-99/1455 | 98-98 | 9 | **FLOW_ABOVE** | 91 | flow above but bound 91c < flow -- chasing breaks goal |
| ITFMATCH-26JUL07ZHALEE-LEE | 31 | 0m | 0 | 36-68 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07ELJRAB-ELJ | 57 | 15m | 29/60-84/672 | 60-61 | 3 | **FLOW_ABOVE** | 78 | REPRICEABLE→60 |
| ITFWMATCH-26JUL07KAYDUN-KAY | 28 | 0m | 0 | 29-61 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07KELXUX-KEL | 33 | 2m | 0 | 33-38 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL07SCHCAN-SCH | 13 | 7m | 0 | 13-16 | — | **NO_FLOW** | 13 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL07ONCCAM | 20 | 44 | **64** | 97 | -33 |
| ITFWMATCH-26JUL07EVAGOW | 14 | 66 | **80** | 97 | -17 |
| ITFWMATCH-26JUL07SCHCAN | 84 | 16 | **100** | 97 | +3 |

## PATTERNS (sub-B) — 7
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL07RICMAR {"combined": 98, "detail": "pair combined 98c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- deep_neg_fv: KXITFWMATCH-26JUL07EVAGOW-GOW {"entry_minus_fv_burst": -8.5}
- deep_neg_fv: KXITFWMATCH-26JUL07GIADIA-GIA {"entry_minus_fv_burst": -60.0}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07CLAHER-CLA {"entry_minus_fv_burst": -18.5}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07MOESAN-SAN {"entry_minus_fv_burst": -15.5, "emitted_et": "2026-07-07 01:28:06 PM ET"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07ONCCAM-CAM {"entry_minus_fv_burst": -37.0, "emitted_et": "2026-07-07 01:28:06 PM ET"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL07SKAPET-PET {"entry_minus_fv_burst": -12.0, "emitted_et": "2026-07-07 01:28:06 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
