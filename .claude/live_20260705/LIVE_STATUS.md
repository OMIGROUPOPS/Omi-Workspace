# LIVE VALIDATION — rolling status

- cycle 213 @ **2026-07-17 02:26:59 PM ET** | build `f80a3506` | session boot 07-17 13:26 ET | log `live_v3_20260717.jsonl` | 4372 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL17SAIBRA-SAI aim=28 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- placed:path_aim UL17VUKGAL-GAL aim=48 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- placed:path_aim UL17VUKGAL-VUK aim=43 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca
- placed:path_aim UL17NEFGAI-NEF aim=36 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_cohort:SHAD,window_phase:CONS,ca

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 9 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 13:27:57 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17DELFUE-DEL | flatten DEFERRED: ev -1.07 above margin floor -3.0 |
| 13:30:50 | **self_fill_bell** | KXATPCHALLENGERMATCH-26JUL17DRAGEA-DRA | own buys rose 4c (31->35) in 1800s -> match-live presumption, entry buys FROZEN |
| 13:37:57 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17ADDIVA-ADD | flatten DEFERRED: ev -0.48 above margin floor -3.0 |
| 14:01:47 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD | flatten DEFERRED: ev -0.84 above margin floor -3.0 |
| 14:01:47 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17SANALM-ALM | flatten DEFERRED: ev -2.37 above margin floor -3.0 |
| 14:12:14 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD | flatten DEFERRED: ev -0.84 above margin floor -3.0 |
| 14:12:14 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17SANALM-ALM | flatten DEFERRED: ev -2.37 above margin floor -3.0 |
| 14:22:48 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD | flatten DEFERRED: ev -0.84 above margin floor -3.0 |
| 14:22:48 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17SANALM-ALM | flatten DEFERRED: ev -2.37 above margin floor -3.0 |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_flatten_leash.md**

## FILLS — 4 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 13:59 | ATPCHALLENGERMATCH-26JUL17SANALM-A | ATP_CHALL | ? | 48 | 46 | +2 (window_cell) | — | pre | single |  | MIXED |
| 14:00 | ATPCHALLENGERMATCH-26JUL17DRAGEA-G | ATP_CHALL | ? | 65 | 62 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:01 | ATPCHALLENGERMATCH-26JUL17RODCRA-R | ATP_CHALL | ? | 71 | 69 | +2 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 14:24 | ATPMATCH-26JUL17DZUMOL-MOL | ATP_MAIN | ? | 68 | 68 | +0 (window_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 8 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 2} | repriceable now: true 2 / false 6 | **cumulative bid_grade lines: 12544 (repriceable true 1651 / false 10893)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17HOLBOU-B | 33 | 59m | 0 | 33-34 | — | **NO_FLOW** | 31 |  |
| ATPCHALLENGERMATCH-26JUL17HOLBOU-H | 66 | 27m | 4/67-67/304 | 66-67 | 1 | **FLOW_ABOVE** | 64 | flow above but bound 64c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17RODCRA-C | 26 | 25m | 10/30-30/3190 | 29-30 | 4 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17SANALM-S | 49 | 28m | 7/52-53/141 | 52-53 | 3 | **FLOW_ABOVE** | 49 | flow above but bound 49c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-G | 48 | 25m | 2/52-53/109 | 51-52 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→52 |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-V | 43 | 25m | 0 | 48-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL17FRULEG-FRU | 16 | 59m | 6/17-19/529 | 16-20 | 1 | **FLOW_ABOVE** | 15 | flow above but bound 15c < flow -- chasing breaks goal |
| ITFMATCH-26JUL17FRULEG-LEG | 80 | 59m | 2/84-84/58 | 80-84 | 4 | **FLOW_ABOVE** | 81 | REPRICEABLE→81 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17SANALM | 48 | 53 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL17RODCRA | 71 | 30 | **101** | 97 | +4 |
| ATPMATCH-26JUL17DZUMOL | 68 | 33 | **101** | 97 | +4 |

## FLOW-STATE — 7 tracked game(s) ({'OPEN': 4, 'WAKING': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17DRAGEA | ATP_CHALL | 8.9 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17RODCRA | ATP_CHALL | 0.7 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17SANALM | ATP_CHALL | 0.367 | 1 | **OPEN** |
| ATPMATCH-26JUL17DZUMOL | ATP_MAIN | 1.533 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17VUKGAL | ATP_CHALL | 0.067 | 1 | **WAKING** |
| ITFMATCH-26JUL17FRULEG | ITF_M | 0.133 | 4 | **WAKING** |

## PATTERNS (sub-B) — 2
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17SEKCAS-SEK {"kind": "position_basis", "ref": 38.0, "market_mid": 2.5, "divergence": 35.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17PERSAN-SAN {"kind": "position_basis", "ref": 54.0, "market_mid": 10.0, "divergence": 44.0, "emitted_et": "2026-07-17 02:26:58 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
