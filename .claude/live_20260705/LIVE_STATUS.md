# LIVE VALIDATION — rolling status

- cycle 33 @ **2026-07-08 07:52:35 PM ET** | build `0d555fb` | session boot 07-08 17:25 ET | log `live_v3_20260708.jsonl` | 10540 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 17 graded (session)
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
| 19:47 | ITFMATCH-26JUL08ZIVMIK-ZIV | ITF_M | ? | 5 | 1 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 26 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 22, 'NO_FLOW': 4} | repriceable now: true 20 / false 6 | **cumulative bid_grade lines: 5814 (repriceable true 589 / false 5225)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08FEALAJ-F | 58 | 20m | 41/64-65/3117 | 63-63 | 6 | **FLOW_ABOVE** | 60 | flow above but bound 60c < flow -- chasing breaks goal |
| ITFMATCH-26JUL08DELKUS-DEL | 89 | 82m | 7/91-91/119 | 89-91 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→91 |
| ITFMATCH-26JUL08DELKUS-KUS | 10 | 24m | 3/12-12/273 | 10-12 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→12 |
| ITFMATCH-26JUL08HONNAK-HON | 53 | 82m | 6/54-54/31 | 53-54 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→54 |
| ITFMATCH-26JUL08HONNAK-NAK | 43 | 53m | 3/47-47/15 | 43-47 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL08MATMAT2-MAT | 67 | 82m | 7/68-69/103 | 67-68 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ITFMATCH-26JUL08MATMAT2-MAT2 | 30 | 82m | 4/31-32/161 | 30-32 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→31 |
| ITFMATCH-26JUL08MOCTAN-MOC | 46 | 82m | 4/47-47/44 | 46-47 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFMATCH-26JUL08MOCTAN-TAN | 51 | 82m | 3/55-55/132 | 51-55 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→55 |
| ITFMATCH-26JUL08OCHSAM-OCH | 14 | 147m | 33/15-15/1409 | 14-15 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→15 |
| ITFMATCH-26JUL08OCHSAM-SAM | 85 | 147m | 11/86-87/175 | 85-86 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→86 |
| ITFMATCH-26JUL08TAKJAS-JAS | 52 | 20m | 3/56-56/44 | 52-56 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ITFMATCH-26JUL08TAKJAS-TAK | 45 | 20m | 1/47-47/2 | 45-47 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→47 |
| ITFWMATCH-26JUL08CHOYAM-CHO | 31 | 22m | 0 | 31-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 22m | 3/69-69/21 | 67-69 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ITFWMATCH-26JUL08NAKMAL-MAL | 23 | 20m | 0 | 23-24 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08NAKMAL-NAK | 76 | 22m | 1/80-80/0 | 76-80 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08RUOKAL-KAL | 78 | 111m | 1/80-80/0 | 78-80 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08RUOKAL-RUO | 21 | 111m | 3/22-22/26 | 21-22 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ITFWMATCH-26JUL08SNINON-NON | 25 | 20m | 0 | 25-26 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08SUNCHO-CHO | 19 | 111m | 2/21-21/5 | 19-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFWMATCH-26JUL08SUNCHO-SUN | 77 | 111m | 1/80-80/0 | 77-80 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→80 |
| ITFWMATCH-26JUL08TIKZHA-TIK | 72 | 8m | 0 | 72-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08TIKZHA-ZHA | 26 | 69m | 2/31-31/7 | 26-30 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08WANLEO-LEO | 12 | 111m | 10/13-13/445 | 12-13 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→13 |
| ITFWMATCH-26JUL08WANLEO-WAN | 85 | 107m | 2/88-88/3 | 85-88 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→88 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL08THUPEC | 21 | 1 | **22** | 97 | -75 |
| ATPCHALLENGERMATCH-26JUL08MILUCH | 63 | 2 | **65** | 97 | -32 |
| WTACHALLENGERMATCH-26JUL08YAMMIN | 9 | 79 | **88** | 97 | -9 |
| ITFMATCH-26JUL08STHBER | 40 | 49 | **89** | 97 | -8 |
| WTACHALLENGERMATCH-26JUL08VIDANS | 12 | 87 | **99** | 97 | +2 |

## FLOW-STATE — 27 tracked game(s) ({'QUIET': 5, 'WAKING': 19, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08DELKUS | ITF_M | 0.267 | 2 | **OPEN** |
| ITFMATCH-26JUL08MOCTAN | ITF_M | 0.2 | 1 | **OPEN** |
| ITFMATCH-26JUL08OCHSAM | ITF_M | 0.767 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL08CASBLA | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL08MILUCH | ATP_CHALL | 0.0 | — | **QUIET** |
| ITFMATCH-26JUL08THUPEC | ITF_M | 0.0 | — | **QUIET** |
| ITFWMATCH-26JUL08EKSLUX | ITF_W | 0.0 | — | **QUIET** |
| WTACHALLENGERMATCH-26JUL07SAWDOL | WTA_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL08FEALAJ | ATP_CHALL | 2.267 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL08JOHMAL | ATP_CHALL | 83.667 | — | **WAKING** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.133 | 2 | **WAKING** |
| ITFMATCH-26JUL08HONNAK | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL08LAPKIR | ITF_M | 62.3 | — | **WAKING** |
| ITFMATCH-26JUL08MATMAT2 | ITF_M | 0.167 | 1 | **WAKING** |
| ITFMATCH-26JUL08STHBER | ITF_M | 23.467 | — | **WAKING** |
| ITFMATCH-26JUL08TAKJAS | ITF_M | 0.167 | 2 | **WAKING** |
| ITFMATCH-26JUL08ZIVMIK | ITF_M | 0.167 | 3 | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL08PLADIG | ITF_W | 15.967 | — | **WAKING** |
| ITFWMATCH-26JUL08RUOKAL | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SNINON | ITF_W | 0.0 | 1 | **WAKING** |
| ITFWMATCH-26JUL08SUNCHO | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL08TIKZHA | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL08WANLEO | ITF_W | 0.167 | 1 | **WAKING** |
| WTACHALLENGERMATCH-26JUL08VIDANS | WTA_CHALL | 7.367 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL08YAMMIN | WTA_CHALL | 44.967 | — | **WAKING** |

## PATTERNS (sub-B) — 9
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL08MILUCH-MIL {"fill": 63, "age_min": 146, "mode": "PAIRING(sib never rested)"}
- deep_neg_fv: KXATPCHALLENGERMATCH-26JUL08CASBLA-BLA {"entry_minus_fv_burst": -22.5}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL08YAMMIN-YAM {"fill": 9, "age_min": 124, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL07SAWDOL-DOL {"fill": 35, "age_min": 119, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08THUPEC-THU {"fill": 21, "age_min": 118, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08LAPKIR-LAP {"fill": 9, "age_min": 56, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXITFMATCH-26JUL08DERMIL-MIL {"fill": 26, "age_min": 51, "mode": "PAIRING(sib never rested)"}
- half_arm_aging: KXWTACHALLENGERMATCH-26JUL08VIDANS-ANS {"fill": 12, "age_min": 46, "mode": "NO_BID(sib rested earlier, none now)"}
- half_arm_aging: KXITFMATCH-26JUL08STHBER-BER {"fill": 40, "age_min": 35, "mode": "PAIRING(sib never rested)", "emitted_et": "2026-07-08 07:52:35 PM ET"}

## ERRORS — 0 handler errors this session (ZERO — clean loop)
