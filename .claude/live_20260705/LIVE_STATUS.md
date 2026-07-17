# LIVE VALIDATION — rolling status

- cycle 152 @ **2026-07-17 03:54:40 AM ET** | build `d4c17c4f` | session boot 07-17 02:56 ET | log `live_v3_20260717.jsonl` | 8132 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 161 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- refused:below_leg_floor UL17WAGWIS-WAG aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16SHESTR-STR aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:w1_preference UL16SHESTR-SHE aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:NOT-,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- refused:below_leg_floor UL17WAGWIS-WAG aim=None | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:NOT-,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 6 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 02:57:54 | **self_fill_bell** | KXATPCHALLENGERMATCH-26JUL17NIJDEN-DEN | own buys rose 5c (74->79) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:00:46 | **self_fill_bell** | KXWTACHALLENGERMATCH-26JUL17BASCAR-BAS | own buys rose 4c (60->64) in 1800s -> match-live presumption, entry buys FROZEN |
| 03:28:54 | **w2_fill** | KXATPCHALLENGERMATCH-26JUL17GALCOP-COP | W2 FILL (buy after start): 56c x1 booking=reconcile_adoption gun=percat_fitted |
| 03:28:57 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17GALCOP-COP | flatten DEFERRED: ev -0.65 above margin floor -3.0 |
| 03:40:09 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17GALCOP-COP | flatten DEFERRED: ev -0.65 above margin floor -3.0 |
| 03:52:15 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17GALCOP-COP | flatten DEFERRED: ev -0.65 above margin floor -3.0 |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_flatten_leash.md**

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 03:28 | ATPCHALLENGERMATCH-26JUL17GALCOP-C | ATP_CHALL | ? | 56 | 53 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 03:38 | ATPMATCH-26JUL17VALTRA-TRA | ATP_MAIN | ? | 29 | 27 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 16 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 12, 'FLOW_AT_LEVEL': 2, 'NO_FLOW': 2} | repriceable now: true 5 / false 11 | **cumulative bid_grade lines: 12121 (repriceable true 1596 / false 10525)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17NIJDEN-D | 79 | 57m | 13/79-80/61 | 79-80 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ATPCHALLENGERMATCH-26JUL17NIJDEN-N | 18 | 57m | 2/20-21/26 | 20-21 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |
| ATPMATCH-26JUL17BORDAR-DAR | 54 | 22m | 10/59-59/1803 | 58-59 | 5 | **FLOW_ABOVE** | 99 |  |
| ATPMATCH-26JUL17CERRUU-CER | 23 | 22m | 8/27-27/624 | 26-27 | 4 | **FLOW_ABOVE** | 25 | REPRICEABLE→25 |
| ATPMATCH-26JUL17CERRUU-RUU | 69 | 22m | 6/74-74/274 | 73-74 | 5 | **FLOW_ABOVE** | 74 |  |
| ATPMATCH-26JUL17COLVAC-COL | 56 | 57m | 90/56-58/14000 | 56-57 | 0 | **FLOW_AT_LEVEL** | 58 |  |
| ATPMATCH-26JUL17COLVAC-VAC | 43 | 56m | 57/44-44/7493 | 43-44 | 1 | **FLOW_ABOVE** | 42 | flow above but bound 42c < flow -- chasing breaks goal |
| ATPMATCH-26JUL17VALTRA-VAL | 68 | 16m | 5/72-72/24 | 71-72 | 4 | **FLOW_ABOVE** | 68 | flow above but bound 68c < flow -- chasing breaks goal |
| ITFMATCH-26JUL17KOIFIT-FIT | 50 | 57m | 7/62-64/251 | 61-62 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL17KOIFIT-KOI | 23 | 57m | 1/37-37/87 | 35-39 | 14 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17KARRIC-RIC | 25 | 57m | 13/32-34/692 | 31-34 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL17SCHDAD-DAD | 32 | 2m | 0 | 33-35 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL17SCHDAD-SCH | 65 | 56m | 2/69-69/61 | 65-67 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→69 |
| WTACHALLENGERMATCH-26JUL17BASCAR-B | 64 | 54m | 1/65-65/25 | 64-65 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→65 |
| WTACHALLENGERMATCH-26JUL17BASCAR-C | 35 | 56m | 0 | 35-37 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL17PUTSHE-SHE | 37 | 53m | 9/40-41/229 | 40-41 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→40 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPMATCH-26JUL17VALTRA | 29 | 72 | **101** | 97 | +4 |

## FLOW-STATE — 11 tracked game(s) ({'WAKING': 7, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPMATCH-26JUL17CERRUU | ATP_MAIN | 0.6 | 1 | **OPEN** |
| ATPMATCH-26JUL17COLVAC | ATP_MAIN | 3.0 | 1 | **OPEN** |
| ITFMATCH-26JUL17KOIFIT | ITF_M | 0.267 | 1 | **OPEN** |
| ITFWMATCH-26JUL17KARRIC | ITF_W | 0.267 | 3 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17GALCOP | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17NIJDEN | ATP_CHALL | 0.267 | 1 | **WAKING** |
| ATPMATCH-26JUL17BORDAR | ATP_MAIN | 0.4 | 1 | **WAKING** |
| ATPMATCH-26JUL17VALTRA | ATP_MAIN | 0.467 | 1 | **WAKING** |
| ITFWMATCH-26JUL17SCHDAD | ITF_W | 0.067 | 2 | **WAKING** |
| WTACHALLENGERMATCH-26JUL17BASCAR | WTA_CHALL | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL17PUTSHE | WTA_MAIN | 0.233 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
