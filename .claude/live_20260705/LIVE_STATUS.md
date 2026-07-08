# LIVE VALIDATION — rolling status

- cycle 27 @ **2026-07-08 06:51:21 PM ET** | build `4b700dc` | session boot 07-08 17:25 ET | log `live_v3_20260708.jsonl` | 6862 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 12 graded (session)
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
| 18:31 | ATPCHALLENGERMATCH-26JUL08JOHMAL-J | ATP_CHALL | ? | 42 | 38 | +4 (window_cell) | 2.0 | pre | pair | 97 | MIXED |
| 18:49 | ATPCHALLENGERMATCH-26JUL08JOHMAL-M | ATP_CHALL | ? | 55 | 58 | -3 (window_cell) | -5.5 | pre | pair | 97 | EARNED |

## RESTING BIDS — 26 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 11, 'NO_FLOW': 14, 'FLOW_AT_LEVEL': 1} | repriceable now: true 5 / false 21 | **cumulative bid_grade lines: 5782 (repriceable true 571 / false 5211)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 86m | 34/63-63/5407 | 62-63 | 5 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08DELKUS-DEL | 89 | 21m | 0 | 89-91 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08DELKUS-KUS | 8 | 14m | 0 | 8-11 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 21m | 0 | 53-57 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08HONNAK-NAK | 42 | 21m | 0 | 42-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08LAPKIR-LAP | 9 | 36m | 2577/14-42/216376 | 37-15 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 21m | 1/68-68/99 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 21m | 1/31-31/7 | 30-31 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→31 |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 21m | 0 | 46-47 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08MOCTAN-TAN | 51 | 21m | 0 | 51-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08OCHSAM-OCH | 14 | 85m | 7/15-15/161 | 14-15 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL08OCHSAM-SAM | 85 | 85m | 3/87-87/16 | 85-87 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→87 |
| ITFMATCH-26JUL08STHBER-BER | 40 | 4m | 3/48-49/31 | 47-44 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-JAS | 51 | 86m | 0 | 51-56 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08TAKJAS-TAK | 44 | 86m | 0 | 44-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 86m | 1/21-21/1 | 9-12 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 78 | 50m | 0 | 78-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 50m | 0 | 21-22 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 50m | 0 | 19-21 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 49m | 0 | 77-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TIKZHA-ZHA | 26 | 8m | 0 | 26-31 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 50m | 4/13-13/164 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 45m | 0 | 85-88 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL08VIDANS-A | 12 | 30m | 9/12-13/960 | 12-13 | 0 | **FLOW_AT_LEVEL** | 10 |  |
| WTACHALLENGERMATCH-26JUL08VIDANS-V | 88 | 30m | 1/89-89/19 | 88-89 | 1 | **FLOW_ABOVE** | 85 | flow above but bound 85c < flow -- chasing breaks goal |
| WTACHALLENGERMATCH-26JUL08YAMMIN-M | 88 | 30m | 5/91-91/2199 | 90-91 | 3 | **FLOW_ABOVE** | 88 | flow above but bound 88c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08THUPEC | 21 | 1 | **22** | 97 | -75 |
| ATPCHALLENGERMATCH-26JUL08MILUCH | 63 | 2 | **65** | 97 | -32 |
| WTACHALLENGERMATCH-26JUL08YAMMIN | 9 | 91 | **100** | 97 | +3 |

## FLOW-STATE — 23 tracked game(s) ({'WAKING': 19, 'OPEN': 3, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 0.8 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08VIDANS | WTA_CHALL | 0.333 | 1 | **OPEN** |
| WTACHALLENGERMATCH-26JUL08YAMMIN | WTA_CHALL | 1.2 | 1 | **OPEN** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL08CASBLA | ATP_CHALL | 133.0 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08JOHMAL | ATP_CHALL | 9.533 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08MILUCH | ATP_CHALL | 11.267 | — | **WAKING** |
| ITFMATCH-26JUL08DELKUS | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL08LAPKIR | ITF_M | 80.333 | — | **WAKING** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL08STHBER | ITF_M | 1.667 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 120.067 | — | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL08PLADIG | ITF_W | 17.867 | — | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 0.033 | 5 | **WAKING** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.133 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL07SAWDOL | WTA_CHALL | 28.367 | — | **WAKING** |

## PATTERNS (sub-B) — 5
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL08MILUCH-MIL {"fill": 63, "age_min": 85, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL08CASBLA-BLA {"entry_minus_fv_burst": -22.5}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL08YAMMIN-YAM {"fill": 9, "age_min": 63, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07SAWDOL-DOL {"fill": 35, "age_min": 58, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08THUPEC-THU {"fill": 21, "age_min": 56, "mode": "PAIRING(sib never rested)"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
