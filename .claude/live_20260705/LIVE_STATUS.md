# LIVE VALIDATION — rolling status

- cycle 9 @ **2026-07-15 05:28:52 PM ET** | build `f9afc809` | session boot 07-15 16:43 ET | log `live_v3_20260715.jsonl` | 2794 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL15YOSSAT-SAT aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15YOSSAT-SAT aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15YOSSAT-SAT aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 5 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 16:55:01 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL15YIBYUN-YUN | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:55:01 | **flatten_leash** | KXWTAMATCH-26JUL15IBRBAD-IBR | flatten DEFERRED: ev -0.18 above margin floor -3.0 |
| 17:09:12 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL15YIBYUN-YUN | flatten DEFERRED: ev -2.56 above margin floor -3.0 |
| 17:09:14 | **taker_capped** | KXWTAMATCH-26JUL15IBRBAD-IBR | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 17:19:32 | **taker_capped** | KXWTAMATCH-26JUL15IBRBAD-IBR | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_taker_capped.md**

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:54 | ATPMATCH-26JUL15RUBPEL-PEL | ATP_MAIN | ? | 27 | 25 | +2 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 26 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 15, 'FLOW_ABOVE': 10, 'FLOW_AT_LEVEL': 1} | repriceable now: true 2 / false 24 | **cumulative bid_grade lines: 11408 (repriceable true 1551 / false 9857)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15NAGTOR-T | 38 | 44m | 0 | 39-40 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15WONSHE-S | 15 | 44m | 3/19-19/65 | 18-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ATPCHALLENGERMATCH-26JUL15WONSHE-W | 76 | 44m | 34/82-83/3991 | 83-84 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15BASTIR-TIR | 65 | 44m | 10/68-69/253 | 68-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPMATCH-26JUL15RUBPEL-RUB | 70 | 34m | 10/72-73/320 | 72-73 | 2 | **FLOW_ABOVE** | 70 | flow above but bound 70c < flow -- chasing breaks goal |
| ITFMATCH-26JUL15FERSIK-FER | 55 | 11m | 0 | 71-76 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15FERSIK-SIK | 18 | 28m | 0 | 24-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HULCHA-CHA | 43 | 44m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HULCHA-HUL | 26 | 44m | 0 | 39-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15OCOELL-OCO | 7 | 8m | 0 | 13-18 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15STHALM-ALM | 43 | 44m | 12/66-66/379 | 60-66 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15STHALM-STH | 22 | 44m | 1/39-39/2 | 34-41 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VIISAC-SAC | 54 | 44m | 1/71-71/1 | 70-71 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VIISAC-VII | 16 | 44m | 0 | 30-31 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15VOLDEL-VOL | 8 | 28m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15DASYAN-DAS | 33 | 8m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-LIN | 41 | 44m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-RUS | 29 | 44m | 0 | 40-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TAY | 23 | 44m | 0 | 29-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TSA | 54 | 44m | 1/71-71/34 | 69-71 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-THO | 21 | 44m | 0 | 27-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-UEM | 56 | 44m | 0 | 69-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WEBFAI-FAI | 36 | 28m | 0 | 47-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WEBFAI-WEB | 41 | 28m | 1/55-55/8 | 54-55 | 14 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL15KREMON-MON | 8 | 44m | 3/8-9/3 | 8-9 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTAMATCH-26JUL15SHEQUE-QUE | 32 | 44m | 1/40-40/11 | 38-39 | 8 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPMATCH-26JUL15RUBPEL | 27 | 73 | **100** | 97 | +3 |

## FLOW-STATE — 17 tracked game(s) ({'WAKING': 16, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15WONSHE | ATP_CHALL | 0.933 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL15NAGTOR | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.3 | 1 | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.4 | 1 | **WAKING** |
| ITFMATCH-26JUL15FERSIK | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15HULCHA | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15OCOELL | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15STHALM | ITF_M | 0.4 | 6 | **WAKING** |
| ITFMATCH-26JUL15VIISAC | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15VOLDEL | ITF_M | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15DASYAN | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL15LINRUS | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL15TAYTSA | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL15UEMTHO | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15WEBFAI | ITF_W | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL15KREMON | WTA_MAIN | 0.1 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.033 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXATPMATCH-26JUL15RUBPEL-PEL {"fill": 27, "age_min": 34, "mode": "SET_BELOW_FLOW(prints 2c above)", "emitted_et": "2026-07-15 05:28:47 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
