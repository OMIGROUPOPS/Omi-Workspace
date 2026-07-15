# LIVE VALIDATION — rolling status

- cycle 4 @ **2026-07-15 04:29:33 PM ET** | build `315d4de1` | session boot 07-15 15:52 ET | log `live_v3_20260715.jsonl` | 3721 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL15PONSAN-SAN aim=84 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
- refused:below_leg_floor UL15PONSAN-PON aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,sh
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

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_w2_fill.md**

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:54 | ITFWMATCH-26JUL15MATSHC-MAT | ITF_W | ? | 17 | 5 | +12 (window_cell) | — | pre | single |  | MIXED |
| 16:23 | ITFWMATCH-26JUL15KONPED-KON | ITF_W | ? | 5 | 12 | -7 (window_cell) | — | pre | single |  | EARNED |

## RESTING BIDS — 28 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 17, 'NO_FLOW': 11} | repriceable now: true 5 / false 23 | **cumulative bid_grade lines: 11396 (repriceable true 1550 / false 9846)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL15LAJKRU-K | 28 | 35m | 0 | 32-33 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15LAJKRU-L | 64 | 35m | 6/69-69/575 | 68-69 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15NAGTOR-T | 38 | 19m | 1/41-41/1 | 39-41 | 3 | **FLOW_ABOVE** | 38 | flow above but bound 38c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL15WONSHE-S | 15 | 29m | 0 | 18-19 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15WONSHE-W | 76 | 29m | 4/82-82/33 | 81-82 | 6 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL15YIBYUN-Y | 53 | 35m | 0 | 57-58 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL15BASTIR-TIR | 65 | 35m | 1/69-69/1 | 68-69 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| ATPMATCH-26JUL15RUBPEL-PEL | 27 | 35m | 1/29-29/1 | 27-28 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ATPMATCH-26JUL15RUBPEL-RUB | 71 | 35m | 7/72-73/121 | 72-73 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→72 |
| ITFMATCH-26JUL15BERKLI-BER | 55 | 35m | 2/77-78/3 | 66-77 | 22 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15BERKLI-KLI | 17 | 35m | 6/21-26/40 | 21-26 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ITFMATCH-26JUL15HAZSIN-SIN | 40 | 29m | 27/56-58/1209 | 56-58 | 16 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15HULCHA-CHA | 43 | 29m | 2/61-61/9 | 59-61 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15HULCHA-HUL | 26 | 29m | 0 | 39-44 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15STHALM-ALM | 43 | 35m | 6/66-66/385 | 60-66 | 23 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15STHALM-STH | 22 | 35m | 0 | 35-39 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15VIISAC-SAC | 54 | 29m | 2/71-71/7 | 70-71 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15VIISAC-VII | 16 | 29m | 0 | 29-33 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL15WILFAL-FAL | 11 | 35m | 15/25-30/825 | 14-29 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL15WILFAL-WIL | 55 | 35m | 7/81-83/77 | 69-81 | 26 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-LIN | 41 | 29m | 2/58-58/9 | 54-58 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15LINRUS-RUS | 29 | 29m | 0 | 40-45 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TAY | 23 | 28m | 0 | 29-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15TAYTSA-TSA | 54 | 28m | 1/71-71/7 | 67-71 | 17 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-THO | 21 | 28m | 0 | 27-32 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL15UEMTHO-UEM | 56 | 28m | 0 | 69-73 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL15KREMON-MON | 8 | 35m | 1/10-10/4 | 8-9 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→10 |
| WTAMATCH-26JUL15SHEQUE-QUE | 32 | 35m | 0 | 38-39 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL15KONPED | 5 | 94 | **99** | 97 | +2 |
| ITFWMATCH-26JUL15MATSHC | 17 | 92 | **109** | 97 | +12 |

## FLOW-STATE — 19 tracked game(s) ({'WAKING': 16, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL15HAZSIN | ITF_M | 0.9 | 2 | **OPEN** |
| ITFWMATCH-26JUL15KONPED | ITF_W | 22.067 | 1 | **OPEN** |
| ITFWMATCH-26JUL15MATSHC | ITF_W | 4.233 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL15LAJKRU | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15NAGTOR | ATP_CHALL | 0.033 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15WONSHE | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL15YIBYUN | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL15BASTIR | ATP_MAIN | 0.033 | 1 | **WAKING** |
| ATPMATCH-26JUL15RUBPEL | ATP_MAIN | 0.233 | 1 | **WAKING** |
| ITFMATCH-26JUL15BERKLI | ITF_M | 0.267 | 5 | **WAKING** |
| ITFMATCH-26JUL15HULCHA | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL15STHALM | ITF_M | 0.167 | 4 | **WAKING** |
| ITFMATCH-26JUL15VIISAC | ITF_M | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL15WILFAL | ITF_M | 0.733 | 12 | **WAKING** |
| ITFWMATCH-26JUL15LINRUS | ITF_W | 0.067 | 4 | **WAKING** |
| ITFWMATCH-26JUL15TAYTSA | ITF_W | 0.033 | 4 | **WAKING** |
| ITFWMATCH-26JUL15UEMTHO | ITF_W | 0.0 | 4 | **WAKING** |
| WTAMATCH-26JUL15KREMON | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL15SHEQUE | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 2
- half_arm_aging: KXITFWMATCH-26JUL15MATSHC-MAT {"fill": 17, "age_min": 35, "mode": "NO_BID(sib rested earlier, none now)", "emitted_et": "2026-07-15 04:29:27 PM ET"}
- reality_divergence: KXITFWMATCH-26JUL15MATSHC-SHC {"kind": "resting_bid", "ref": 55.0, "market_mid": 88.5, "divergence": -33.5}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
