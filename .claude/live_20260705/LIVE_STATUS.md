# LIVE VALIDATION — rolling status

- cycle 220 @ **2026-07-17 03:39:58 PM ET** | build `07b05306` | session boot 07-17 15:16 ET | log `live_v3_20260717.jsonl` | 1614 session events | monitor READ-ONLY

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL17THOYOS-THO aim=12 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17SAIBRA-BRA aim=47 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17SAIBRA-SAI aim=28 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17OCODEL-OCO aim=10 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:18:52 | **self_fill_bell** | KXITFMATCH-26JUL17OCODEL-OCO | own buys rose 6c (10->16) in 1800s -> match-live presumption, entry buys FROZEN |
| 15:25:55 | **self_fill_bell** | KXATPCHALLENGERMATCH-26JUL17LAJNOG-NOG | own buys rose 4c (24->28) in 1800s -> match-live presumption, entry buys FROZEN |
| 15:31:17 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU | flatten DEFERRED: ev -1.29 above margin floor -3.0 |

## FILLS — 2 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:16 | ITFMATCH-26JUL17NEFGAI-GAI | ITF_M | ? | 46 | 39 | +7 (window_cell) | — | pre | single |  | MIXED |
| 15:31 | ATPCHALLENGERMATCH-26JUL17HOLBOU-B | ATP_CHALL | ? | 33 | 31 | +2 (window_cell) | — | pre | single |  | MIXED |

## RESTING BIDS — 11 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 4, 'NO_FLOW': 7} | repriceable now: true 3 / false 8 | **cumulative bid_grade lines: 12573 (repriceable true 1654 / false 10919)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17FORTOM-T | 64 | 23m | 0 | 64-66 | — | **NO_FLOW** | 63 |  |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-L | 71 | 21m | 0 | 71-72 | — | **NO_FLOW** | 69 |  |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-N | 28 | 14m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-S | 37 | 21m | 0 | 37-38 | — | **NO_FLOW** | 35 |  |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-Y | 62 | 12m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-G | 51 | 23m | 3/52-52/43 | 51-52 | 1 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-V | 45 | 23m | 3/48-49/175 | 48-49 | 3 | **FLOW_ABOVE** | 46 | REPRICEABLE→46 |
| ATPCHALLENGERMATCH-26JUL17WONJOH-J | 36 | 21m | 0 | 36-37 | — | **NO_FLOW** | 34 |  |
| ATPCHALLENGERMATCH-26JUL17WONJOH-W | 64 | 22m | 0 | 64-65 | — | **NO_FLOW** | 61 |  |
| ITFMATCH-26JUL17OCODEL-DEL | 82 | 23m | 1/84-84/70 | 82-83 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→84 |
| ITFMATCH-26JUL17OCODEL-OCO | 16 | 21m | 2/17-18/54 | 16-17 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→17 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL17NEFGAI | 46 | 58 | **104** | 97 | +7 |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | 33 | 86 | **119** | 97 | +22 |

## FLOW-STATE — 8 tracked game(s) ({'WAKING': 6, 'OPEN': 2}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL17NEFGAI | ITF_M | 0.333 | 3 | **OPEN** |
| ITFMATCH-26JUL17OCODEL | ITF_M | 0.4 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17FORTOM | ATP_CHALL | 0.033 | 2 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | ATP_CHALL | 2.167 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17LAJNOG | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17SMIYUN | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17VUKGAL | ATP_CHALL | 0.233 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17WONJOH | ATP_CHALL | 0.033 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17DELFUE-DEL {"kind": "position_basis", "ref": 86.0, "market_mid": 29.0, "divergence": 57.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
