# LIVE VALIDATION — rolling status

- cycle 211 @ **2026-07-17 02:06:18 PM ET** | build `302fa115` | session boot 07-17 13:26 ET | log `live_v3_20260717.jsonl` | 3150 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 47 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL17SAIBRA-BRA aim=47 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- placed:path_aim UL17SAIBRA-SAI aim=28 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- placed:path_aim UL17VUKGAL-GAL aim=48 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- placed:path_aim UL17VUKGAL-VUK aim=43 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 5 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 13:27:57 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17DELFUE-DEL | flatten DEFERRED: ev -1.07 above margin floor -3.0 |
| 13:30:50 | **self_fill_bell** | KXATPCHALLENGERMATCH-26JUL17DRAGEA-DRA | own buys rose 4c (31->35) in 1800s -> match-live presumption, entry buys FROZEN |
| 13:37:57 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17ADDIVA-ADD | flatten DEFERRED: ev -0.48 above margin floor -3.0 |
| 14:01:47 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD | flatten DEFERRED: ev -0.84 above margin floor -3.0 |
| 14:01:47 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17SANALM-ALM | flatten DEFERRED: ev -2.37 above margin floor -3.0 |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_flatten_leash.md**

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 13:59 | ATPCHALLENGERMATCH-26JUL17SANALM-A | ATP_CHALL | ? | 48 | 46 | +2 (window_cell) | — | pre | single |  | MIXED |
| 14:00 | ATPCHALLENGERMATCH-26JUL17DRAGEA-G | ATP_CHALL | ? | 65 | 62 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:01 | ATPCHALLENGERMATCH-26JUL17RODCRA-R | ATP_CHALL | ? | 71 | 69 | +2 (window_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 10 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_AT_LEVEL': 1, 'NO_FLOW': 4, 'FLOW_ABOVE': 5} | repriceable now: true 1 / false 9 | **cumulative bid_grade lines: 12542 (repriceable true 1650 / false 10892)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17HOLBOU-B | 33 | 38m | 0 | 33-34 | — | **NO_FLOW** | 31 |  |
| ATPCHALLENGERMATCH-26JUL17HOLBOU-H | 66 | 6m | 0 | 66-67 | — | **NO_FLOW** | 64 |  |
| ATPCHALLENGERMATCH-26JUL17RODCRA-C | 26 | 5m | 2/30-30/62 | 29-30 | 4 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17SANALM-S | 49 | 7m | 1/52-52/7 | 51-52 | 3 | **FLOW_ABOVE** | 49 | flow above but bound 49c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-G | 48 | 5m | 1/52-52/9 | 51-52 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-V | 43 | 5m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL17DZUMOL-DZU | 32 | 37m | 22/33-34/2858 | 32-33 | 1 | **FLOW_ABOVE** | 31 | flow above but bound 31c < flow -- chasing breaks goal |
| ATPMATCH-26JUL17DZUMOL-MOL | 67 | 39m | 37/67-68/5147 | 67-68 | 0 | **FLOW_AT_LEVEL** | 68 |  |
| ITFMATCH-26JUL17FRULEG-FRU | 16 | 38m | 5/17-19/528 | 16-17 | 1 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFMATCH-26JUL17FRULEG-LEG | 80 | 39m | 0 | 80-85 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17SANALM | 48 | 52 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL17RODCRA | 71 | 30 | **101** | 97 | +4 |

## FLOW-STATE — 7 tracked game(s) ({'OPEN': 3, 'WAKING': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17DRAGEA | ATP_CHALL | 0.567 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17SANALM | ATP_CHALL | 0.333 | 1 | **OPEN** |
| ATPMATCH-26JUL17DZUMOL | ATP_MAIN | 1.833 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17RODCRA | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17VUKGAL | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL17FRULEG | ITF_M | 0.167 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17SEKCAS-SEK {"kind": "position_basis", "ref": 38.0, "market_mid": 2.5, "divergence": 35.5}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
