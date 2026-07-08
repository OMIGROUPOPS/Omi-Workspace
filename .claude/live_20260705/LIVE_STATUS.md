# LIVE VALIDATION — rolling status

- cycle 32 @ **2026-07-08 07:42:21 PM ET** | build `a67fc2e` | session boot 07-08 17:25 ET | log `live_v3_20260708.jsonl` | 10262 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 16 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17:26 | ATPCHALLENGERMATCH-26JUL08MILUCH-M | ATP_CHALL | ? | 63 | 61 | +2 (window_cell) | 4.5 | pre | single |  | GIFT_CLASS |
| 17:30 | ITFWMATCH-26JUL08EKSLUX-EKS | ITF_W | underdog | 11 | 8 | +3 (place_cell) | — | pre | pair | 97 | MIXED |
| 17:33 | ITFWMATCH-26JUL08EKSLUX-LUX | ITF_W | leader | 86 | 87 | -1 (place_cell) | — | pre | pair | 97 | MIXED |
| 17:34 | ITFWMATCH-26JUL08PLADIG-DIG | ITF_W | leader | 89 | 91 | -2 (place_cell) | — | pre | pair | 95 | GIFT_CLASS |
| 17:39 | ATPCHALLENGERMATCH-26JUL08CASBLA-B | ATP_CHALL | ? | 59 | 57 | +2 (window_cell) | -22.5 | pre | pair | 97 | EARNED |
| 17:40 | ITFWMATCH-26JUL08PLADIG-PLA | ITF_W | underdog | 6 | 7 | -1 (place_cell) | — | pre | pair | 95 | EARNED |
| 17:43 | ATPCHALLENGERMATCH-26JUL08CASBLA-C | ATP_CHALL | ? | 38 | 38 | +0 (window_cell) | 19.5 | pre | pair | 97 | EARNED |
| 17:48 | WTACHALLENGERMATCH-26JUL08YAMMIN-Y | WTA_CHALL | ? | 9 | 7 | +2 (window_cell) | -0.5 | pre | single |  | MIXED |
| 17:53 | WTACHALLENGERMATCH-26JUL07SAWDOL-D | WTA_CHALL | ? | 35 | 32 | +3 (fill_est) | 1.0 | pre | single |  | MIXED |
| 17:54 | ITFMATCH-26JUL08THUPEC-THU | ITF_M | ? | 21 | 37 | -16 (window_cell) | — | pre | single |  | EARNED |
| 18:31 | ATPCHALLENGERMATCH-26JUL08JOHMAL-J | ATP_CHALL | ? | 42 | 38 | +4 (window_cell) | 2.0 | pre | pair | 97 | MIXED |
| 18:49 | ATPCHALLENGERMATCH-26JUL08JOHMAL-M | ATP_CHALL | ? | 55 | 58 | -3 (window_cell) | -5.5 | pre | pair | 97 | EARNED |
| 18:56 | ITFMATCH-26JUL08LAPKIR-LAP | ITF_M | ? | 9 | 5 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 19:01 | ITFMATCH-26JUL08DERMIL-MIL | ITF_M | ? | 26 | 22 | +4 (fill_est) | — | pre | single |  | PENDING |
| 19:06 | WTACHALLENGERMATCH-26JUL08VIDANS-A | WTA_CHALL | ? | 12 | 10 | +2 (window_cell) | 4.0 | pre | single |  | GIFT_CLASS |
| 19:17 | ITFMATCH-26JUL08STHBER-BER | ITF_M | ? | 40 | 41 | -1 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 28 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 23, 'NO_FLOW': 5} | repriceable now: true 19 / false 9 | **cumulative bid_grade lines: 5811 (repriceable true 587 / false 5224)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 10m | 19/64-64/1484 | 63-63 | 6 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08DELKUS-DEL | 89 | 72m | 6/91-91/114 | 89-91 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| ITFMATCH-26JUL08DELKUS-KUS | 10 | 13m | 3/12-12/273 | 10-12 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→12 |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 72m | 6/54-54/31 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL08HONNAK-NAK | 43 | 43m | 2/47-47/14 | 43-47 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 72m | 7/68-69/103 | 67-69 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 72m | 2/31-31/8 | 30-31 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→31 |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 72m | 1/47-47/6 | 46-47 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL08MOCTAN-TAN | 51 | 72m | 0 | 51-55 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08OCHSAM-OCH | 14 | 136m | 27/15-15/1273 | 14-15 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL08OCHSAM-SAM | 85 | 136m | 7/87-87/90 | 85-87 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→87 |
| ITFMATCH-26JUL08TAKJAS-JAS | 52 | 10m | 1/56-56/0 | 52-56 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ITFMATCH-26JUL08TAKJAS-TAK | 45 | 10m | 1/47-47/2 | 45-47 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL08ZIVMIK-ZIV | 5 | 137m | 2/9-21/2 | 8-10 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→9 |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 12m | 0 | 31-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 12m | 1/69-69/14 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08NAKMAL-MAL | 23 | 10m | 0 | 23-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NAKMAL-NAK | 76 | 12m | 0 | 76-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08RUOKAL-KAL | 78 | 101m | 1/80-80/0 | 78-80 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 101m | 3/22-22/26 | 21-22 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL08SNINON-NON | 25 | 10m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 101m | 1/21-21/1 | 19-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 100m | 1/80-80/0 | 77-80 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08TIKZHA-TIK | 69 | 46m | 2/74-74/1 | 69-74 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08TIKZHA-ZHA | 26 | 59m | 2/31-31/7 | 26-30 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 101m | 9/13-13/286 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 96m | 1/88-88/0 | 85-88 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→88 |
| WTACHALLENGERMATCH-26JUL08VIDANS-V | 85 | 36m | 39/87-93/14757 | 87-87 | 2 | **FLOW_ABOVE** | 85 | flow above but bound 85c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08THUPEC | 21 | 1 | **22** | 97 | -75 |
| ATPCHALLENGERMATCH-26JUL08MILUCH | 63 | 2 | **65** | 97 | -32 |
| WTACHALLENGERMATCH-26JUL08YAMMIN | 9 | 79 | **88** | 97 | -9 |
| ITFMATCH-26JUL08STHBER | 40 | 49 | **89** | 97 | -8 |
| WTACHALLENGERMATCH-26JUL08VIDANS | 12 | 87 | **99** | 97 | +2 |

## FLOW-STATE — 27 tracked game(s) ({'WAKING': 20, 'QUIET': 3, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | ITF_M | 0.3 | 2 | **OPEN** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.2 | 1 | **OPEN** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 0.5 | 1 | **OPEN** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.2 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08MILUCH | ATP_CHALL | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL08CASBLA | ATP_CHALL | 45.667 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 2.333 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08JOHMAL | ATP_CHALL | 71.9 | — | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.133 | 2 | **WAKING** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL08LAPKIR | ITF_M | 51.233 | — | **WAKING** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL08STHBER | ITF_M | 19.033 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 0.1 | 2 | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08PLADIG | ITF_W | 23.333 | — | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 0.133 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL07SAWDOL | WTA_CHALL | 6.267 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VIDANS | WTA_CHALL | 4.6 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL08YAMMIN | WTA_CHALL | 38.133 | — | **WAKING** |

## PATTERNS (sub-B) — 8
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL08MILUCH-MIL {"fill": 63, "age_min": 136, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL08CASBLA-BLA {"entry_minus_fv_burst": -22.5}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL08YAMMIN-YAM {"fill": 9, "age_min": 114, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07SAWDOL-DOL {"fill": 35, "age_min": 109, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08THUPEC-THU {"fill": 21, "age_min": 107, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08LAPKIR-LAP {"fill": 9, "age_min": 46, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08DERMIL-MIL {"fill": 26, "age_min": 41, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL08VIDANS-ANS {"fill": 12, "age_min": 36, "mode": "SET_BELOW_FLOW(prints 2c above)", "emitted_et": "2026-07-08 07:42:21 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
