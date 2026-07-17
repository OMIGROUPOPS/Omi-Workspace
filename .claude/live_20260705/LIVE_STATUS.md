# LIVE VALIDATION — rolling status

- cycle 151 @ **2026-07-17 03:44:25 AM ET** | build `241192cf` | session boot 07-17 02:56 ET | log `live_v3_20260717.jsonl` | 7407 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 150 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL17WAGWIS-WAG aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16SHESTR-STR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16SHESTR-SHE aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL17WAGWIS-WAG aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 5 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 02:57:54 | **self_fill_bell** | KXATPCHALLENGERMATCH-26JUL17NIJDEN-DEN | own buys rose 5c (74->79) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:00:46 | **self_fill_bell** | KXWTACHALLENGERMATCH-26JUL17BASCAR-BAS | own buys rose 4c (60->64) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:28:54 | **w2_fill** | KXATPCHALLENGERMATCH-26JUL17GALCOP-COP | W2 FILL (buy after start): 56c x1 booking=reconcile_adoption gun=percat_fitted |
| 03:28:57 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17GALCOP-COP | flatten DEFERRED: ev -0.65 above margin floor -3.0 |
| 03:40:09 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17GALCOP-COP | flatten DEFERRED: ev -0.65 above margin floor -3.0 |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_flatten_leash.md**

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 03:28 | ATPCHALLENGERMATCH-26JUL17GALCOP-C | ATP_CHALL | ? | 56 | 53 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 03:38 | ATPMATCH-26JUL17VALTRA-TRA | ATP_MAIN | ? | 29 | 27 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 16 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 12, 'FLOW_AT_LEVEL': 2, 'NO_FLOW': 2} | repriceable now: true 4 / false 12 | **cumulative bid_grade lines: 12119 (repriceable true 1595 / false 10524)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17NIJDEN-D | 79 | 46m | 10/79-80/48 | 79-80 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL17NIJDEN-N | 18 | 47m | 1/21-21/24 | 20-21 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→21 |
| ATPMATCH-26JUL17BORDAR-DAR | 54 | 12m | 7/59-59/1367 | 58-59 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL17CERRUU-CER | 23 | 12m | 4/27-27/420 | 26-27 | 4 | **FLOW_ABOVE** | 25 | REPRICEABLE→25 |
| ATPMATCH-26JUL17CERRUU-RUU | 69 | 12m | 4/74-74/251 | 73-74 | 5 | **FLOW_ABOVE** | 74 |  |
| ATPMATCH-26JUL17COLVAC-COL | 56 | 47m | 79/56-58/12238 | 57-57 | 0 | **FLOW_AT_LEVEL** | 58 |  |
| ATPMATCH-26JUL17COLVAC-VAC | 43 | 46m | 45/44-44/5832 | 43-44 | 1 | **FLOW_ABOVE** | 42 | flow above but bound 42c < flow -- chasing breaks goal |
| ATPMATCH-26JUL17VALTRA-VAL | 68 | 6m | 4/72-72/20 | 71-72 | 4 | **FLOW_ABOVE** | 68 | flow above but bound 68c < flow -- chasing breaks goal |
| ITFMATCH-26JUL17KOIFIT-FIT | 50 | 47m | 4/64-64/244 | 61-63 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL17KOIFIT-KOI | 23 | 47m | 1/37-37/87 | 35-39 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17KARRIC-RIC | 25 | 47m | 12/32-34/690 | 30-34 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17SCHDAD-DAD | 30 | 45m | 1/35-35/40 | 30-35 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17SCHDAD-SCH | 65 | 46m | 2/69-69/61 | 65-69 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| WTACHALLENGERMATCH-26JUL17BASCAR-B | 64 | 44m | 0 | 64-65 | — | **NO_FLOW** | 99 |  |
| WTACHALLENGERMATCH-26JUL17BASCAR-C | 35 | 46m | 0 | 35-37 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL17PUTSHE-SHE | 37 | 43m | 6/40-41/198 | 40-41 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPMATCH-26JUL17VALTRA | 29 | 72 | **101** | 97 | +4 |

## FLOW-STATE — 11 tracked game(s) ({'WAKING': 8, 'OPEN': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL17CERRUU | ATP_MAIN | 0.667 | 1 | **OPEN** |
| ATPMATCH-26JUL17COLVAC | ATP_MAIN | 2.833 | 1 | **OPEN** |
| ATPMATCH-26JUL17VALTRA | ATP_MAIN | 0.8 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17GALCOP | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17NIJDEN | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPMATCH-26JUL17BORDAR | ATP_MAIN | 0.433 | 1 | **WAKING** |
| ITFMATCH-26JUL17KOIFIT | ITF_M | 0.167 | 2 | **WAKING** |
| ITFWMATCH-26JUL17KARRIC | ITF_W | 0.233 | 4 | **WAKING** |
| ITFWMATCH-26JUL17SCHDAD | ITF_W | 0.1 | 4 | **WAKING** |
| WTACHALLENGERMATCH-26JUL17BASCAR | WTA_CHALL | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL17PUTSHE | WTA_MAIN | 0.167 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
