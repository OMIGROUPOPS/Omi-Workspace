# LIVE VALIDATION — rolling status

- cycle 15 @ **2026-07-15 06:38:35 PM ET** | build `7dfee998` | session boot 07-15 16:43 ET | log `live_v3_20260715.jsonl` | 7454 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 14 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 16:55:01 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL15YIBYUN-YUN | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:55:01 | **flatten_leash** | KXWTAMATCH-26JUL15IBRBAD-IBR | flatten DEFERRED: ev -0.18 above margin floor -3.0 |
| 17:09:12 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL15YIBYUN-YUN | flatten DEFERRED: ev -2.56 above margin floor -3.0 |
| 17:09:14 | **taker_capped** | KXWTAMATCH-26JUL15IBRBAD-IBR | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 17:19:32 | **taker_capped** | KXWTAMATCH-26JUL15IBRBAD-IBR | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 18:05:45 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL15YIBYUN-YUN | flatten DEFERRED: ev -2.56 above margin floor -3.0 |
| 18:08:22 | **w2_fill** | KXITFMATCH-26JUL15STHALM-STH | W2 FILL (buy after start): 22c x5 booking=v4_fingerprint_readopt gun=percat_fitted |
| 18:08:28 | **taker_capped** | KXITFMATCH-26JUL15STHALM-STH | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 18:15:51 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL15YIBYUN-YUN | flatten DEFERRED: ev -2.56 above margin floor -3.0 |
| 18:15:52 | **taker_capped** | KXWTAMATCH-26JUL15IBRBAD-IBR | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 18:25:56 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL15YIBYUN-YUN | flatten DEFERRED: ev -2.56 above margin floor -3.0 |
| 18:25:56 | **taker_capped** | KXWTAMATCH-26JUL15IBRBAD-IBR | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 18:35:59 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL15YIBYUN-YUN | flatten DEFERRED: ev -2.56 above margin floor -3.0 |
| 18:35:59 | **taker_capped** | KXWTAMATCH-26JUL15IBRBAD-IBR | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_taker_capped.md, FORENSIC_flatten_leash.md**

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:54 | ATPMATCH-26JUL15RUBPEL-PEL | ATP_MAIN | ? | 27 | 25 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 18:08 | ITFMATCH-26JUL15STHALM-STH | ITF_M | ? | 22 | 18 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 23 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 19, 'NO_FLOW': 3, 'FLOW_AT_LEVEL': 1} | repriceable now: true 2 / false 21 | **cumulative bid_grade lines: 11421 (repriceable true 1551 / false 9870)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15NAGTOR-T | 38 | 114m | 1/40-40/35 | 39-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| ATPMATCH-26JUL15BASTIR-TIR | 65 | 114m | 22/68-69/771 | 68-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPMATCH-26JUL15RUBPEL-RUB | 70 | 103m | 35/72-73/1998 | 72-73 | 2 | **FLOW_ABOVE** | 70 | flow above but bound 70c < flow -- chasing breaks goal |
| ITFMATCH-26JUL15FERSIK-FER | 55 | 80m | 2/71-76/4 | 72-74 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15FERSIK-SIK | 18 | 98m | 3/25-28/52 | 25-27 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15HULCHA-CHA | 43 | 114m | 7/60-61/626 | 59-60 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15HULCHA-HUL | 26 | 114m | 0 | 38-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15VIISAC-SAC | 54 | 114m | 4/70-71/19 | 70-71 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VIISAC-VII | 16 | 114m | 8/30-32/200 | 28-29 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VOLDEL-DEL | 68 | 26m | 1/83-83/2 | 81-83 | 15 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VOLDEL-VOL | 8 | 98m | 3/17-18/47 | 16-17 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15DASYAN-DAS | 33 | 78m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15DASYAN-YAN | 40 | 51m | 0 | 53-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-LIN | 41 | 114m | 1/59-59/16 | 54-58 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-RUS | 29 | 114m | 4/45-45/319 | 45-46 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TAY | 23 | 114m | 4/32-34/45 | 30-32 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TSA | 54 | 114m | 2/71-71/40 | 69-71 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-THO | 21 | 114m | 4/29-32/39 | 27-29 | 8 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-UEM | 56 | 114m | 2/70-70/27 | 70-72 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15WEBFAI-FAI | 36 | 98m | 1/48-48/80 | 47-48 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15WEBFAI-WEB | 41 | 98m | 7/54-55/216 | 54-55 | 13 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL15KREMON-MON | 8 | 114m | 6/8-9/110 | 8-9 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTAMATCH-26JUL15SHEQUE-QUE | 32 | 114m | 1/40-40/11 | 38-39 | 8 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPMATCH-26JUL15RUBPEL | 27 | 73 | **100** | 97 | +3 |

## FLOW-STATE — 15 tracked game(s) ({'WAKING': 12, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.567 | 1 | **OPEN** |
| ITFMATCH-26JUL15VIISAC | ITF_M | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL15WEBFAI | ITF_W | 0.233 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL15NAGTOR | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL15FERSIK | ITF_M | 0.1 | 2 | **WAKING** |
| ITFMATCH-26JUL15HULCHA | ITF_M | 0.1 | 1 | **WAKING** |
| ITFMATCH-26JUL15STHALM | ITF_M | 24.467 | — | **WAKING** |
| ITFMATCH-26JUL15VOLDEL | ITF_M | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL15DASYAN | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15LINRUS | ITF_W | 0.133 | 1 | **WAKING** |
| ITFWMATCH-26JUL15TAYTSA | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL15UEMTHO | ITF_W | 0.167 | 2 | **WAKING** |
| WTAMATCH-26JUL15KREMON | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 2
- half_arm_aging: KXATPMATCH-26JUL15RUBPEL-PEL {"fill": 27, "age_min": 104, "mode": "SET_BELOW_FLOW(prints 2c above)"}
- half_arm_aging: KXITFMATCH-26JUL15STHALM-STH {"fill": 22, "age_min": 30, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-15 06:38:29 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
