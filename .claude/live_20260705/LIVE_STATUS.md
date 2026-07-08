# LIVE VALIDATION — rolling status

- cycle 23 @ **2026-07-08 06:10:21 PM ET** | build `8af7307` | session boot 07-08 17:25 ET | log `live_v3_20260708.jsonl` | 3185 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 10 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:26 | ATPCHALLENGERMATCH-26JUL08MILUCH-M | ATP_CHALL | ? | 63 | 61 | +2 (window_cell) | 4.5 | pre | single |  | GIFT_CLASS |
| 17:30 | ITFWMATCH-26JUL08EKSLUX-EKS | ITF_W | underdog | 11 | 8 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 17:33 | ITFWMATCH-26JUL08EKSLUX-LUX | ITF_W | leader | 86 | 87 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 17:34 | ITFWMATCH-26JUL08PLADIG-DIG | ITF_W | leader | 89 | 91 | -2 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 17:39 | ATPCHALLENGERMATCH-26JUL08CASBLA-B | ATP_CHALL | ? | 59 | 57 | +2 (window_cell) | — | pre | pair | 97 | GIFT_CLASS |
| 17:40 | ITFWMATCH-26JUL08PLADIG-PLA | ITF_W | underdog | 6 | 7 | -1 (place_cell) | — | pre | pair | 95 | EARNED |
| 17:43 | ATPCHALLENGERMATCH-26JUL08CASBLA-C | ATP_CHALL | ? | 38 | 38 | +0 (window_cell) | — | pre | pair | 97 | EARNED |
| 17:48 | WTACHALLENGERMATCH-26JUL08YAMMIN-Y | WTA_CHALL | ? | 9 | 7 | +2 (window_cell) | — | pre | single |  | MIXED |
| 17:53 | WTACHALLENGERMATCH-26JUL07SAWDOL-D | WTA_CHALL | ? | 35 | 32 | +3 (fill_est) | 1.0 | pre | single |  | MIXED |
| 17:54 | ITFMATCH-26JUL08THUPEC-THU | ITF_M | ? | 21 | 37 | -16 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 18 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 10} | repriceable now: true 3 / false 15 | **cumulative bid_grade lines: 5756 (repriceable true 567 / false 5189)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 45m | 9/63-63/334 | 62-63 | 5 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL08JOHMAL-J | 40 | 45m | 3/41-41/148 | 40-41 | 1 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08LAPKIR-LAP | 8 | 2m | 33/11-14/3964 | 12-11 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→11 |
| ITFMATCH-26JUL08OCHSAM-OCH | 14 | 44m | 5/15-15/99 | 14-15 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL08OCHSAM-SAM | 85 | 44m | 0 | 85-87 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08STHBER-BER | 40 | 44m | 5/49-49/643 | 44-49 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-JAS | 51 | 45m | 0 | 51-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-TAK | 44 | 45m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 45m | 0 | 10-13 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 78 | 9m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 9m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 9m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 8m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 9m | 0 | 12-14 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 4m | 0 | 85-88 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08STEZHA-S | 77 | 45m | 26/81-82/11570 | 81-82 | 4 | **FLOW_ABOVE** | 78 | REPRICEABLE→78 |
| WTACHALLENGERMATCH-26JUL08VIDANS-V | 88 | 29m | 2/89-89/340 | 88-89 | 1 | **FLOW_ABOVE** | 85 | flow above but bound 85c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL08YAMMIN-M | 88 | 22m | 8/90-91/307 | 90-91 | 2 | **FLOW_ABOVE** | 88 | flow above but bound 88c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08MILUCH | 63 | 18 | **81** | 97 | -16 |
| ITFMATCH-26JUL08THUPEC | 21 | 75 | **96** | 97 | -1 |
| WTACHALLENGERMATCH-26JUL08YAMMIN | 9 | 91 | **100** | 97 | +3 |

## FLOW-STATE — 19 tracked game(s) ({'WAKING': 15, 'QUIET': 1, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL08PLADIG | ITF_W | 4.0 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08STEZHA | WTA_CHALL | 0.833 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08YAMMIN | WTA_CHALL | 2.233 | 1 | **OPEN** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL08CASBLA | ATP_CHALL | 19.9 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.233 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08JOHMAL | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08MILUCH | ATP_CHALL | 7.767 | — | **WAKING** |
| ITFMATCH-26JUL08LAPKIR | ITF_M | 1.467 | — | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL08STHBER | ITF_M | 0.167 | 5 | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 23.6 | — | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.033 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL07SAWDOL | WTA_CHALL | 9.7 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VIDANS | WTA_CHALL | 0.067 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL08MILUCH-MIL {"fill": 63, "age_min": 44, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
