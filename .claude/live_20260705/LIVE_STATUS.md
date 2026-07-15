# LIVE VALIDATION — rolling status

- cycle 5 @ **2026-07-15 04:41:41 PM ET** | build `7a07b139` | session boot 07-15 15:52 ET | log `live_v3_20260715.jsonl` | 4384 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15YOSSAT-SAT aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15YOSSAT-SAT aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 6 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:54:23 | **w2_fill** | KXITFWMATCH-26JUL15MATSHC-MAT | W2 FILL (buy after start): 17c x5 booking=reconcile_adoption gun=percat_fitted |
| 15:56:22 | **bell_missing** | KXATPCHALLENGERMATCH-26JUL15YIBYUN | min_past_start 115.4 |
| 15:56:22 | **bell_missing** | KXITFMATCH-26JUL15WILFAL | min_past_start 55.4 |
| 15:56:22 | **bell_missing** | KXITFMATCH-26JUL15BERKLI | min_past_start 55.4 |
| 16:23:54 | **w2_fill** | KXITFWMATCH-26JUL15KONPED-KON | W2 FILL (buy after start): 5c x5 booking=v4_fingerprint_readopt gun=percat_fitted |
| 16:24:55 | **flatten_leash** | KXITFWMATCH-26JUL15KONPED-KON | flatten DEFERRED: ev -0.5 above margin floor -3.0 |

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:54 | ITFWMATCH-26JUL15MATSHC-MAT | ITF_W | ? | 17 | 5 | +12 (window_cell) | — | pre | single |  | MIXED |
| 16:23 | ITFWMATCH-26JUL15KONPED-KON | ITF_W | ? | 5 | 12 | -7 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 26 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 17, 'NO_FLOW': 9} | repriceable now: true 6 / false 20 | **cumulative bid_grade lines: 11397 (repriceable true 1551 / false 9846)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15LAJKRU-K | 28 | 47m | 0 | 32-33 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15LAJKRU-L | 64 | 47m | 10/69-69/833 | 68-69 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15NAGTOR-T | 38 | 31m | 1/41-41/1 | 39-41 | 3 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL15WONSHE-S | 15 | 41m | 1/19-19/24 | 18-19 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→19 |
| ATPCHALLENGERMATCH-26JUL15WONSHE-W | 76 | 41m | 5/82-82/33 | 81-82 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL15BASTIR-TIR | 65 | 47m | 1/69-69/1 | 68-69 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ATPMATCH-26JUL15RUBPEL-PEL | 27 | 47m | 1/29-29/1 | 27-28 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ATPMATCH-26JUL15RUBPEL-RUB | 71 | 47m | 9/72-73/204 | 72-73 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→72 |
| ITFMATCH-26JUL15BERKLI-BER | 55 | 47m | 3/77-78/9 | 62-77 | 22 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15BERKLI-KLI | 17 | 47m | 8/21-29/56 | 21-26 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFMATCH-26JUL15HULCHA-CHA | 43 | 41m | 2/61-61/9 | 59-61 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15HULCHA-HUL | 26 | 41m | 0 | 39-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15STHALM-ALM | 43 | 47m | 6/66-66/385 | 60-66 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15STHALM-STH | 22 | 47m | 0 | 35-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15VIISAC-SAC | 54 | 41m | 2/71-71/7 | 70-71 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VIISAC-VII | 16 | 41m | 0 | 29-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WILFAL-FAL | 11 | 47m | 15/25-30/825 | 16-29 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15WILFAL-WIL | 55 | 47m | 7/81-83/77 | 68-81 | 26 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-LIN | 41 | 41m | 2/58-58/9 | 54-58 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-RUS | 29 | 41m | 0 | 40-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TAY | 23 | 40m | 0 | 29-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TSA | 54 | 40m | 1/71-71/7 | 67-71 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-THO | 21 | 40m | 0 | 27-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-UEM | 56 | 40m | 0 | 69-73 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15KREMON-MON | 8 | 47m | 1/10-10/4 | 8-9 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| WTAMATCH-26JUL15SHEQUE-QUE | 32 | 47m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL15KONPED | 5 | 75 | **80** | 97 | -17 |
| ITFWMATCH-26JUL15MATSHC | 17 | 97 | **114** | 97 | +17 |

## FLOW-STATE — 17 tracked game(s) ({'OPEN': 3, 'WAKING': 14}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15LAJKRU | ATP_CHALL | 0.3 | 1 | **OPEN** |
| ITFWMATCH-26JUL15KONPED | ITF_W | 22.567 | 1 | **OPEN** |
| ITFWMATCH-26JUL15MATSHC | ITF_W | 5.333 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL15NAGTOR | ATP_CHALL | 0.033 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15WONSHE | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.033 | 1 | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.3 | 1 | **WAKING** |
| ITFMATCH-26JUL15BERKLI | ITF_M | 0.367 | 5 | **WAKING** |
| ITFMATCH-26JUL15HULCHA | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL15STHALM | ITF_M | 0.167 | 4 | **WAKING** |
| ITFMATCH-26JUL15VIISAC | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL15WILFAL | ITF_M | 0.7 | 13 | **WAKING** |
| ITFWMATCH-26JUL15LINRUS | ITF_W | 0.067 | 4 | **WAKING** |
| ITFWMATCH-26JUL15TAYTSA | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL15UEMTHO | ITF_W | 0.0 | 4 | **WAKING** |
| WTAMATCH-26JUL15KREMON | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 2
- half_arm_aging: KXITFWMATCH-26JUL15MATSHC-MAT {"fill": 17, "age_min": 47, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXITFWMATCH-26JUL15MATSHC-SHC {"kind": "resting_bid", "ref": 55.0, "market_mid": 88.5, "divergence": -33.5}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
