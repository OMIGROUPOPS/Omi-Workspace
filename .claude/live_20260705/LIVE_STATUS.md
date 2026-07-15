# LIVE VALIDATION — rolling status

- cycle 12 @ **2026-07-15 06:04:39 PM ET** | build `aed806bb` | session boot 07-15 16:43 ET | log `live_v3_20260715.jsonl` | 5065 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 52 min ago (>30 tripwire; source observed_starts.db)

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
- classes now: {'FLOW_ABOVE': 16, 'NO_FLOW': 7, 'FLOW_AT_LEVEL': 1} | repriceable now: true 3 / false 21 | **cumulative bid_grade lines: 11415 (repriceable true 1551 / false 9864)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15NAGTOR-T | 38 | 80m | 1/40-40/35 | 38-40 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |
| ATPMATCH-26JUL15BASTIR-TIR | 65 | 80m | 19/68-69/591 | 68-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPMATCH-26JUL15RUBPEL-RUB | 70 | 70m | 19/72-73/594 | 72-73 | 2 | **FLOW_ABOVE** | 70 | flow above but bound 70c < flow -- chasing breaks goal |
| ITFMATCH-26JUL15FERSIK-FER | 55 | 47m | 2/71-76/4 | 72-74 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15FERSIK-SIK | 18 | 64m | 0 | 25-28 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HULCHA-CHA | 43 | 80m | 4/60-61/604 | 59-61 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15HULCHA-HUL | 26 | 80m | 0 | 39-43 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15OCOELL-OCO | 7 | 44m | 1/18-18/5 | 14-17 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15STHALM-STH | 22 | 80m | 91/25-47/2788 | 30-28 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→25 |
| ITFMATCH-26JUL15VIISAC-SAC | 54 | 80m | 2/70-71/4 | 70-71 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VIISAC-VII | 16 | 80m | 1/32-32/0 | 29-31 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VOLDEL-VOL | 8 | 64m | 2/18-18/20 | 16-17 | 10 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15DASYAN-DAS | 33 | 44m | 0 | 44-49 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15DASYAN-YAN | 40 | 17m | 0 | 53-56 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-LIN | 41 | 80m | 1/59-59/16 | 57-59 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-RUS | 29 | 80m | 0 | 40-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TAY | 23 | 80m | 1/34-34/2 | 30-33 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TSA | 54 | 80m | 2/71-71/40 | 69-71 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-THO | 21 | 80m | 1/32-32/3 | 29-31 | 11 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-UEM | 56 | 80m | 0 | 70-72 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WEBFAI-FAI | 36 | 64m | 0 | 47-48 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WEBFAI-WEB | 41 | 64m | 1/55-55/8 | 54-55 | 14 | **FLOW_ABOVE** | 99 |  |
| WTAMATCH-26JUL15KREMON-MON | 8 | 80m | 5/8-9/64 | 8-9 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTAMATCH-26JUL15SHEQUE-QUE | 32 | 80m | 1/40-40/11 | 38-39 | 8 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPMATCH-26JUL15RUBPEL | 27 | 73 | **100** | 97 | +3 |

## FLOW-STATE — 16 tracked game(s) ({'WAKING': 16}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15NAGTOR | ATP_CHALL | 0.033 | 2 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.2 | 1 | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.3 | 1 | **WAKING** |
| ITFMATCH-26JUL15FERSIK | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL15HULCHA | ITF_M | 0.133 | 2 | **WAKING** |
| ITFMATCH-26JUL15OCOELL | ITF_M | 0.033 | 3 | **WAKING** |
| ITFMATCH-26JUL15STHALM | ITF_M | 2.967 | — | **WAKING** |
| ITFMATCH-26JUL15VIISAC | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL15VOLDEL | ITF_M | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL15DASYAN | ITF_W | 0.0 | 3 | **WAKING** |
| ITFWMATCH-26JUL15LINRUS | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL15TAYTSA | ITF_W | 0.067 | 2 | **WAKING** |
| ITFWMATCH-26JUL15UEMTHO | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL15WEBFAI | ITF_W | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL15KREMON | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXATPMATCH-26JUL15RUBPEL-PEL {"fill": 27, "age_min": 70, "mode": "SET_BELOW_FLOW(prints 2c above)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
