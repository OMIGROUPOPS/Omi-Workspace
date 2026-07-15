# LIVE VALIDATION — rolling status

- cycle 11 @ **2026-07-15 05:52:53 PM ET** | build `f61ea374` | session boot 07-15 16:43 ET | log `live_v3_20260715.jsonl` | 4126 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 40 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15SUBWAR-WAR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

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

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:54 | ATPMATCH-26JUL15RUBPEL-PEL | ATP_MAIN | ? | 27 | 25 | +2 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 24 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 14, 'NO_FLOW': 9, 'FLOW_AT_LEVEL': 1} | repriceable now: true 2 / false 22 | **cumulative bid_grade lines: 11415 (repriceable true 1551 / false 9864)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15NAGTOR-T | 38 | 68m | 1/40-40/35 | 39-41 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| ATPMATCH-26JUL15BASTIR-TIR | 65 | 68m | 15/68-69/512 | 68-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPMATCH-26JUL15RUBPEL-RUB | 70 | 58m | 15/72-73/466 | 72-73 | 2 | **FLOW_ABOVE** | 70 | flow above but bound 70c < flow -- chasing breaks goal |
| ITFMATCH-26JUL15FERSIK-FER | 55 | 35m | 2/71-76/4 | 72-74 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15FERSIK-SIK | 18 | 52m | 0 | 25-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HULCHA-CHA | 43 | 68m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HULCHA-HUL | 26 | 68m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15OCOELL-OCO | 7 | 32m | 1/18-18/5 | 14-17 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15STHALM-STH | 22 | 68m | 5/39-41/40 | 34-39 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VIISAC-SAC | 54 | 68m | 2/70-71/4 | 70-71 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VIISAC-VII | 16 | 68m | 1/32-32/0 | 29-32 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VOLDEL-VOL | 8 | 52m | 2/18-18/20 | 16-18 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15DASYAN-DAS | 33 | 32m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15DASYAN-YAN | 40 | 5m | 0 | 53-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-LIN | 41 | 68m | 0 | 54-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-RUS | 29 | 68m | 0 | 40-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TAY | 23 | 68m | 1/34-34/2 | 30-33 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TSA | 54 | 68m | 1/71-71/34 | 69-71 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-THO | 21 | 68m | 1/32-32/3 | 29-31 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-UEM | 56 | 68m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WEBFAI-FAI | 36 | 52m | 0 | 47-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WEBFAI-WEB | 41 | 52m | 1/55-55/8 | 54-55 | 14 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL15KREMON-MON | 8 | 68m | 5/8-9/64 | 8-9 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTAMATCH-26JUL15SHEQUE-QUE | 32 | 68m | 1/40-40/11 | 38-39 | 8 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPMATCH-26JUL15RUBPEL | 27 | 73 | **100** | 97 | +3 |

## FLOW-STATE — 16 tracked game(s) ({'WAKING': 16}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15NAGTOR | ATP_CHALL | 0.033 | 2 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.233 | 1 | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.333 | 1 | **WAKING** |
| ITFMATCH-26JUL15FERSIK | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL15HULCHA | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15OCOELL | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL15STHALM | ITF_M | 0.133 | 5 | **WAKING** |
| ITFMATCH-26JUL15VIISAC | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL15VOLDEL | ITF_M | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL15DASYAN | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15LINRUS | ITF_W | 0.0 | 5 | **WAKING** |
| ITFWMATCH-26JUL15TAYTSA | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL15UEMTHO | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL15WEBFAI | ITF_W | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL15KREMON | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXATPMATCH-26JUL15RUBPEL-PEL {"fill": 27, "age_min": 58, "mode": "SET_BELOW_FLOW(prints 2c above)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
