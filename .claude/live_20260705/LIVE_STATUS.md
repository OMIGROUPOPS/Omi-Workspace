# LIVE VALIDATION — rolling status

- cycle 24 @ **2026-07-08 06:20:35 PM ET** | build `30c143c` | session boot 07-08 17:25 ET | log `live_v3_20260708.jsonl` | 4092 session events | monitor READ-ONLY
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
| 17:39 | ATPCHALLENGERMATCH-26JUL08CASBLA-B | ATP_CHALL | ? | 59 | 57 | +2 (window_cell) | -22.5 | pre | pair | 97 | EARNED |
| 17:40 | ITFWMATCH-26JUL08PLADIG-PLA | ITF_W | underdog | 6 | 7 | -1 (place_cell) | — | pre | pair | 95 | EARNED |
| 17:43 | ATPCHALLENGERMATCH-26JUL08CASBLA-C | ATP_CHALL | ? | 38 | 38 | +0 (window_cell) | 19.5 | pre | pair | 97 | EARNED |
| 17:48 | WTACHALLENGERMATCH-26JUL08YAMMIN-Y | WTA_CHALL | ? | 9 | 7 | +2 (window_cell) | — | pre | single |  | MIXED |
| 17:53 | WTACHALLENGERMATCH-26JUL07SAWDOL-D | WTA_CHALL | ? | 35 | 32 | +3 (fill_est) | 1.0 | pre | single |  | MIXED |
| 17:54 | ITFMATCH-26JUL08THUPEC-THU | ITF_M | ? | 21 | 37 | -16 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 18 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 10, 'NO_FLOW': 8} | repriceable now: true 3 / false 15 | **cumulative bid_grade lines: 5759 (repriceable true 568 / false 5191)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 55m | 10/63-63/337 | 62-63 | 5 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL08JOHMAL-J | 40 | 55m | 3/41-41/148 | 40-42 | 1 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08LAPKIR-LAP | 9 | 5m | 139/16-20/12688 | 16-15 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08OCHSAM-OCH | 14 | 55m | 5/15-15/99 | 14-15 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL08OCHSAM-SAM | 85 | 55m | 1/87-87/1 | 85-87 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→87 |
| ITFMATCH-26JUL08STHBER-BER | 40 | 55m | 6/47-49/643 | 41-46 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-JAS | 51 | 55m | 0 | 51-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-TAK | 44 | 55m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 55m | 1/21-21/1 | 10-14 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 78 | 19m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 19m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 19m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 19m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 19m | 0 | 12-14 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 15m | 0 | 85-88 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08STEZHA-S | 77 | 55m | 34/81-82/11813 | 81-82 | 4 | **FLOW_ABOVE** | 78 | REPRICEABLE→78 |
| WTACHALLENGERMATCH-26JUL08VIDANS-V | 88 | 39m | 2/89-89/340 | 88-89 | 1 | **FLOW_ABOVE** | 85 | flow above but bound 85c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL08YAMMIN-M | 88 | 32m | 8/90-91/307 | 90-91 | 2 | **FLOW_ABOVE** | 88 | flow above but bound 88c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08MILUCH | 63 | 19 | **82** | 97 | -15 |
| ITFMATCH-26JUL08THUPEC | 21 | 69 | **90** | 97 | -7 |
| WTACHALLENGERMATCH-26JUL08YAMMIN | 9 | 91 | **100** | 97 | +3 |

## FLOW-STATE — 19 tracked game(s) ({'OPEN': 4, 'WAKING': 14, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08CASBLA | ATP_CHALL | 22.267 | 2 | **OPEN** |
| ITFWMATCH-26JUL08PLADIG | ITF_W | 4.533 | 2 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08STEZHA | WTA_CHALL | 0.933 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08YAMMIN | WTA_CHALL | 1.633 | 1 | **OPEN** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.233 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08JOHMAL | ATP_CHALL | 0.033 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08MILUCH | ATP_CHALL | 11.967 | — | **WAKING** |
| ITFMATCH-26JUL08LAPKIR | ITF_M | 11.9 | — | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL08STHBER | ITF_M | 0.2 | 5 | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 25.233 | — | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.0 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL07SAWDOL | WTA_CHALL | 13.567 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VIDANS | WTA_CHALL | 0.067 | 1 | **WAKING** |

## PATTERNS (sub-B) — 3
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL08MILUCH-MIL {"fill": 63, "age_min": 54, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL08CASBLA-BLA {"entry_minus_fv_burst": -22.5, "emitted_et": "2026-07-08 06:20:35 PM ET"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL08YAMMIN-YAM {"fill": 9, "age_min": 32, "mode": "SET_BELOW_FLOW(prints 2c above)", "emitted_et": "2026-07-08 06:20:35 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
