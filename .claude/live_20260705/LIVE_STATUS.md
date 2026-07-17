# LIVE VALIDATION — rolling status

- cycle 222 @ **2026-07-17 04:00:55 PM ET** | build `6a326ecb` | session boot 07-17 15:16 ET | log `live_v3_20260717.jsonl` | 2631 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 48 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL17SAIBRA-SAI aim=28 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17OCODEL-OCO aim=10 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17AIAYAN-YAN aim=18 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17FORTOM-FOR aim=31 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co

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

## RESTING BIDS — 12 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 6} | repriceable now: true 3 / false 9 | **cumulative bid_grade lines: 12578 (repriceable true 1654 / false 10924)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17FORTOM-F | 31 | 1m | 0 | 34-35 | — | **NO_FLOW** | 32 |  |
| ATPCHALLENGERMATCH-26JUL17FORTOM-T | 65 | 0m | 0 | 65-66 | — | **NO_FLOW** | 63 |  |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-L | 71 | 42m | 3/72-72/158 | 71-72 | 1 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-N | 28 | 35m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-S | 37 | 42m | 0 | 37-38 | — | **NO_FLOW** | 35 |  |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-Y | 63 | 21m | 0 | 63-64 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-G | 51 | 44m | 5/52-52/47 | 51-52 | 1 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-V | 45 | 44m | 5/48-49/176 | 48-49 | 3 | **FLOW_ABOVE** | 46 | REPRICEABLE→46 |
| ATPCHALLENGERMATCH-26JUL17WONJOH-J | 36 | 42m | 0 | 36-37 | — | **NO_FLOW** | 34 |  |
| ATPCHALLENGERMATCH-26JUL17WONJOH-W | 64 | 43m | 1/65-65/150 | 64-65 | 1 | **FLOW_ABOVE** | 61 | flow above but bound 61c < flow -- chasing breaks goal |
| ITFMATCH-26JUL17OCODEL-DEL | 82 | 44m | 1/84-84/70 | 82-83 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→84 |
| ITFMATCH-26JUL17OCODEL-OCO | 16 | 42m | 2/17-18/54 | 16-17 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→17 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL17NEFGAI | 46 | 62 | **108** | 97 | +11 |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | 33 | 93 | **126** | 97 | +29 |

## FLOW-STATE — 8 tracked game(s) ({'WAKING': 7, 'OPEN': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL17NEFGAI | ITF_M | 5.433 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17FORTOM | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | ATP_CHALL | 4.867 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17LAJNOG | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17SMIYUN | ATP_CHALL | 0.0 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17VUKGAL | ATP_CHALL | 0.233 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17WONJOH | ATP_CHALL | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL17OCODEL | ITF_M | 0.067 | 1 | **WAKING** |

## PATTERNS (sub-B) — 4
- half_arm_aging: KXITFMATCH-26JUL17NEFGAI-GAI {"fill": 46, "age_min": 44, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17DELFUE-DEL {"kind": "position_basis", "ref": 86.0, "market_mid": 29.0, "divergence": 57.0}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD {"kind": "position_basis", "ref": 71.0, "market_mid": 26.5, "divergence": 44.5, "emitted_et": "2026-07-17 04:00:55 PM ET"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17SANALM-ALM {"kind": "position_basis", "ref": 68.0, "market_mid": 34.5, "divergence": 33.5, "emitted_et": "2026-07-17 04:00:55 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
