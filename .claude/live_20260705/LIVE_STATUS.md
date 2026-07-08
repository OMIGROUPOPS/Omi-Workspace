# LIVE VALIDATION — rolling status

- cycle 22 @ **2026-07-08 06:00:00 PM ET** | build `6a07cd6` | session boot 07-08 17:25 ET | log `live_v3_20260708.jsonl` | 2539 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 10 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:26 | ATPCHALLENGERMATCH-26JUL08MILUCH-M | ATP_CHALL | ? | 63 | 61 | +2 (window_cell) | 4.5 | pre | single |  | GIFT_CLASS |
| 17:30 | ITFWMATCH-26JUL08EKSLUX-EKS | ITF_W | underdog | 11 | 8 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 17:33 | ITFWMATCH-26JUL08EKSLUX-LUX | ITF_W | leader | 86 | 87 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 17:34 | ITFWMATCH-26JUL08PLADIG-DIG | ITF_W | leader | 89 | 91 | -2 (place_cell) | — | pre | pair | 95 | PENDING |
| 17:39 | ATPCHALLENGERMATCH-26JUL08CASBLA-B | ATP_CHALL | ? | 59 | 57 | +2 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 17:40 | ITFWMATCH-26JUL08PLADIG-PLA | ITF_W | underdog | 6 | 7 | -1 (place_cell) | — | pre | pair | 95 | PENDING |
| 17:43 | ATPCHALLENGERMATCH-26JUL08CASBLA-C | ATP_CHALL | ? | 38 | 38 | +0 (window_cell) | — | pre | pair | 97 | EARNED |
| 17:48 | WTACHALLENGERMATCH-26JUL08YAMMIN-Y | WTA_CHALL | ? | 9 | 7 | +2 (window_cell) | — | pre | single |  | MIXED |
| 17:53 | WTACHALLENGERMATCH-26JUL07SAWDOL-D | WTA_CHALL | ? | 35 | 32 | +3 (fill_est) | 1.0 | pre | single |  | MIXED |
| 17:54 | ITFMATCH-26JUL08THUPEC-THU | ITF_M | ? | 21 | 37 | -16 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 12 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 4} | repriceable now: true 2 / false 10 | **cumulative bid_grade lines: 5749 (repriceable true 566 / false 5183)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 34m | 4/63-63/200 | 62-63 | 5 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL08JOHMAL-J | 40 | 34m | 3/41-41/148 | 40-41 | 1 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08LAPKIR-LAP | 9 | 34m | 11/15-15/190 | 12-15 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08OCHSAM-OCH | 14 | 34m | 5/15-15/99 | 14-15 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL08OCHSAM-SAM | 85 | 34m | 0 | 85-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STHBER-BER | 40 | 34m | 3/49-49/627 | 48-49 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-JAS | 51 | 34m | 0 | 51-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-TAK | 44 | 34m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 34m | 0 | 12-15 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08STEZHA-S | 77 | 34m | 17/81-82/9639 | 81-82 | 4 | **FLOW_ABOVE** | 78 | REPRICEABLE→78 |
| WTACHALLENGERMATCH-26JUL08VIDANS-V | 88 | 19m | 2/89-89/340 | 88-89 | 1 | **FLOW_ABOVE** | 85 | flow above but bound 85c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL08YAMMIN-M | 88 | 11m | 6/90-91/291 | 90-91 | 2 | **FLOW_ABOVE** | 88 | flow above but bound 88c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08MILUCH | 63 | 16 | **79** | 97 | -18 |
| ITFMATCH-26JUL08THUPEC | 21 | 73 | **94** | 97 | -3 |
| WTACHALLENGERMATCH-26JUL08YAMMIN | 9 | 91 | **100** | 97 | +3 |

## FLOW-STATE — 16 tracked game(s) ({'WAKING': 12, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08LAPKIR | ITF_M | 0.367 | 3 | **OPEN** |
| ITFWMATCH-26JUL08PLADIG | ITF_W | 4.0 | 3 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08STEZHA | WTA_CHALL | 0.567 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08YAMMIN | WTA_CHALL | 2.233 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08CASBLA | ATP_CHALL | 16.333 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08JOHMAL | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08MILUCH | ATP_CHALL | 6.6 | — | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL08STHBER | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 23.267 | — | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 24.2 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL07SAWDOL | WTA_CHALL | 4.233 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VIDANS | WTA_CHALL | 0.1 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL08MILUCH-MIL {"fill": 63, "age_min": 34, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 06:00:00 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
