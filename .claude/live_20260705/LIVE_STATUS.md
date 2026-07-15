# LIVE VALIDATION — rolling status

- cycle 7 @ **2026-07-15 05:04:54 PM ET** | build `a5b4be9e` | session boot 07-15 16:43 ET | log `live_v3_20260715.jsonl` | 1537 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 51 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15YOSSAT-SAT aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL15YOSSAT-SAT aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 2 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 16:55:01 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL15YIBYUN-YUN | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:55:01 | **flatten_leash** | KXWTAMATCH-26JUL15IBRBAD-IBR | flatten DEFERRED: ev -0.18 above margin floor -3.0 |

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:54 | ATPMATCH-26JUL15RUBPEL-PEL | ATP_MAIN | ? | 27 | 25 | +2 (adopted_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 25 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 16, 'FLOW_ABOVE': 8, 'FLOW_AT_LEVEL': 1} | repriceable now: true 2 / false 23 | **cumulative bid_grade lines: 11403 (repriceable true 1551 / false 9852)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15LAJKRU-K | 28 | 20m | 1/33-33/7 | 32-33 | 5 | **FLOW_ABOVE** | 30 | flow above but bound 30c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL15LAJKRU-L | 64 | 20m | 5/69-69/141 | 68-69 | 5 | **FLOW_ABOVE** | 66 | flow above but bound 66c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL15NAGTOR-T | 38 | 20m | 0 | 39-41 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15WONSHE-S | 15 | 20m | 3/19-19/65 | 18-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ATPCHALLENGERMATCH-26JUL15WONSHE-W | 76 | 20m | 6/82-82/52 | 81-82 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15BASTIR-TIR | 65 | 20m | 3/68-69/84 | 68-69 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→68 |
| ATPMATCH-26JUL15RUBPEL-RUB | 70 | 10m | 1/73-73/12 | 72-73 | 3 | **FLOW_ABOVE** | 70 | flow above but bound 70c < flow -- chasing breaks goal |
| ITFMATCH-26JUL15FERSIK-SIK | 18 | 4m | 0 | 24-29 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HULCHA-CHA | 43 | 20m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15HULCHA-HUL | 26 | 20m | 0 | 39-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15STHALM-ALM | 43 | 20m | 5/66-66/102 | 60-66 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15STHALM-STH | 22 | 20m | 0 | 34-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15VIISAC-SAC | 54 | 20m | 1/71-71/1 | 70-71 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VIISAC-VII | 16 | 20m | 0 | 29-32 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15VOLDEL-VOL | 8 | 4m | 0 | 16-18 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-LIN | 41 | 20m | 0 | 54-58 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-RUS | 29 | 20m | 0 | 40-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TAY | 23 | 20m | 0 | 29-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TSA | 54 | 20m | 0 | 67-71 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-THO | 21 | 20m | 0 | 27-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-UEM | 56 | 20m | 0 | 69-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WEBFAI-FAI | 36 | 4m | 0 | 47-50 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15WEBFAI-WEB | 41 | 4m | 0 | 54-55 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15KREMON-MON | 8 | 20m | 2/8-9/2 | 8-9 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| WTAMATCH-26JUL15SHEQUE-QUE | 32 | 20m | 0 | 38-40 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPMATCH-26JUL15RUBPEL | 27 | 73 | **100** | 97 | +3 |

## FLOW-STATE — 16 tracked game(s) ({'OPEN': 2, 'WAKING': 14}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15LAJKRU | ATP_CHALL | 0.333 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL15WONSHE | ATP_CHALL | 0.367 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL15NAGTOR | ATP_CHALL | 0.0 | 2 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.1 | 1 | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.233 | 1 | **WAKING** |
| ITFMATCH-26JUL15FERSIK | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL15HULCHA | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL15STHALM | ITF_M | 0.167 | 5 | **WAKING** |
| ITFMATCH-26JUL15VIISAC | ITF_M | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL15VOLDEL | ITF_M | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL15LINRUS | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15TAYTSA | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15UEMTHO | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL15WEBFAI | ITF_W | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL15KREMON | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.0 | 2 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
