# LIVE VALIDATION — rolling status

- cycle 13 @ **2026-07-15 06:15:57 PM ET** | build `8123ef1d` | session boot 07-15 16:43 ET | log `live_v3_20260715.jsonl` | 6033 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 8 violation(s)
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

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_taker_capped.md, FORENSIC_flatten_leash.md**

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:54 | ATPMATCH-26JUL15RUBPEL-PEL | ATP_MAIN | ? | 27 | 25 | +2 (adopted_est) | — | pre | single |  | PENDING |
| 18:08 | ITFMATCH-26JUL15STHALM-STH | ITF_M | ? | 22 | 18 | +4 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 23 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 14, 'NO_FLOW': 8, 'FLOW_AT_LEVEL': 1} | repriceable now: true 2 / false 21 | **cumulative bid_grade lines: 11416 (repriceable true 1551 / false 9865)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15NAGTOR-T | 38 | 91m | 1/40-40/35 | 38-40 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| ATPMATCH-26JUL15BASTIR-TIR | 65 | 91m | 21/68-69/631 | 68-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPMATCH-26JUL15RUBPEL-RUB | 70 | 81m | 21/72-73/631 | 72-73 | 2 | **FLOW_ABOVE** | 70 | flow above but bound 70c < flow -- chasing breaks goal |
| ITFMATCH-26JUL15FERSIK-FER | 55 | 58m | 2/71-76/4 | 72-74 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15FERSIK-SIK | 18 | 75m | 0 | 25-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HULCHA-CHA | 43 | 91m | 4/60-61/604 | 60-61 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15HULCHA-HUL | 26 | 91m | 0 | 38-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15VIISAC-SAC | 54 | 91m | 2/70-71/4 | 70-71 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VIISAC-VII | 16 | 91m | 1/32-32/0 | 29-30 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VOLDEL-DEL | 68 | 3m | 0 | 81-83 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15VOLDEL-VOL | 8 | 75m | 3/17-18/47 | 16-17 | 9 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15DASYAN-DAS | 33 | 55m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15DASYAN-YAN | 40 | 28m | 0 | 53-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-LIN | 41 | 91m | 1/59-59/16 | 57-59 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-RUS | 29 | 91m | 0 | 40-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TAY | 23 | 91m | 3/33-34/31 | 30-32 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TSA | 54 | 91m | 2/71-71/40 | 69-71 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-THO | 21 | 91m | 2/31-32/12 | 29-31 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-UEM | 56 | 91m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WEBFAI-FAI | 36 | 75m | 0 | 47-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WEBFAI-WEB | 41 | 75m | 3/54-55/143 | 54-55 | 13 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL15KREMON-MON | 8 | 91m | 6/8-9/110 | 8-9 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTAMATCH-26JUL15SHEQUE-QUE | 32 | 91m | 1/40-40/11 | 38-39 | 8 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPMATCH-26JUL15RUBPEL | 27 | 73 | **100** | 97 | +3 |

## FLOW-STATE — 15 tracked game(s) ({'WAKING': 15}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15NAGTOR | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.2 | 1 | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.3 | 1 | **WAKING** |
| ITFMATCH-26JUL15FERSIK | ITF_M | 0.0 | 2 | **WAKING** |
| ITFMATCH-26JUL15HULCHA | ITF_M | 0.133 | 1 | **WAKING** |
| ITFMATCH-26JUL15STHALM | ITF_M | 8.8 | — | **WAKING** |
| ITFMATCH-26JUL15VIISAC | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL15VOLDEL | ITF_M | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL15DASYAN | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15LINRUS | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL15TAYTSA | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL15UEMTHO | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL15WEBFAI | ITF_W | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL15KREMON | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXATPMATCH-26JUL15RUBPEL-PEL {"fill": 27, "age_min": 81, "mode": "SET_BELOW_FLOW(prints 2c above)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
