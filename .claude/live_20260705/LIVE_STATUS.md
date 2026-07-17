# LIVE VALIDATION — rolling status

- cycle 227 @ **2026-07-17 04:52:47 PM ET** | build `43b6ad04` | session boot 07-17 15:16 ET | log `live_v3_20260717.jsonl` | 5344 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 39 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL17OCODEL-OCO aim=10 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17AIAYAN-YAN aim=18 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17FORTOM-FOR aim=31 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL17SMIYUN-SMI aim=32 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 3 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:18:52 | **self_fill_bell** | KXITFMATCH-26JUL17OCODEL-OCO | own buys rose 6c (10->16) in 1800s -> match-live presumption, entry buys FROZEN |
| 15:25:55 | **self_fill_bell** | KXATPCHALLENGERMATCH-26JUL17LAJNOG-NOG | own buys rose 4c (24->28) in 1800s -> match-live presumption, entry buys FROZEN |
| 15:31:17 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU | flatten DEFERRED: ev -1.29 above margin floor -3.0 |

## FILLS — 6 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:16 | ITFMATCH-26JUL17NEFGAI-GAI | ITF_M | ? | 46 | 39 | +7 (window_cell) | — | pre | single |  | MIXED |
| 15:31 | ATPCHALLENGERMATCH-26JUL17HOLBOU-B | ATP_CHALL | ? | 33 | 31 | +2 (window_cell) | — | pre | single |  | MIXED |
| 16:07 | ATPCHALLENGERMATCH-26JUL17WONJOH-W | ATP_CHALL | ? | 64 | 61 | +3 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 16:32 | ATPCHALLENGERMATCH-26JUL17SMIYUN-Y | ATP_CHALL | ? | 63 | 61 | +2 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 16:47 | ITFMATCH-26JUL17OCODEL-OCO | ITF_M | ? | 17 | 12 | +5 (place_cell) | — | pre | pair | 99 | PENDING |
| 16:47 | ITFMATCH-26JUL17OCODEL-DEL | ITF_M | ? | 82 | 79 | +3 (fill_est) | — | pre | pair | 99 | PENDING |

## RESTING BIDS — 8 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 7, 'NO_FLOW': 1} | repriceable now: true 2 / false 6 | **cumulative bid_grade lines: 12589 (repriceable true 1655 / false 10934)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17FORTOM-F | 31 | 53m | 1/35-35/5 | 34-35 | 4 | **FLOW_ABOVE** | 32 | REPRICEABLE→32 |
| ATPCHALLENGERMATCH-26JUL17FORTOM-T | 65 | 52m | 8/66-67/236 | 66-66 | 1 | **FLOW_ABOVE** | 63 | flow above but bound 63c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-L | 71 | 94m | 15/72-72/7029 | 71-72 | 1 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-N | 28 | 87m | 1/29-29/3 | 28-29 | 1 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-S | 32 | 18m | 0 | 36-37 | — | **NO_FLOW** | 34 |  |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-G | 53 | 5m | 1/54-54/424 | 53-54 | 1 | **FLOW_ABOVE** | 50 | flow above but bound 50c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-V | 45 | 96m | 33/48-49/2271 | 48-49 | 3 | **FLOW_ABOVE** | 46 | REPRICEABLE→46 |
| ATPCHALLENGERMATCH-26JUL17WONJOH-J | 33 | 45m | 3/36-37/413 | 36-37 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL17NEFGAI | 46 | 8 | **54** | 97 | -43 |
| ATPCHALLENGERMATCH-26JUL17SMIYUN | 63 | 37 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL17WONJOH | 64 | 37 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | 33 | 97 | **130** | 97 | +33 |

## FLOW-STATE — 8 tracked game(s) ({'WAKING': 3, 'OPEN': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17LAJNOG | ATP_CHALL | 0.367 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17SMIYUN | ATP_CHALL | 0.367 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17VUKGAL | ATP_CHALL | 0.767 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17WONJOH | ATP_CHALL | 0.433 | 1 | **OPEN** |
| ITFMATCH-26JUL17OCODEL | ITF_M | 0.7 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17FORTOM | ATP_CHALL | 0.233 | 1 | **WAKING** |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | ATP_CHALL | 0.767 | — | **WAKING** |
| ITFMATCH-26JUL17NEFGAI | ITF_M | 43.833 | — | **WAKING** |

## PATTERNS (sub-B) — 10
- half_arm_aging: KXITFMATCH-26JUL17NEFGAI-GAI {"fill": 46, "age_min": 96, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17DELFUE-DEL {"kind": "position_basis", "ref": 86.0, "market_mid": 29.0, "divergence": 57.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU {"fill": 33, "age_min": 82, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD {"kind": "position_basis", "ref": 71.0, "market_mid": 26.5, "divergence": 44.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17SANALM-ALM {"kind": "position_basis", "ref": 68.0, "market_mid": 34.5, "divergence": 33.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL17WONJOH-WON {"fill": 64, "age_min": 45, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU {"kind": "position_basis", "ref": 33.0, "market_mid": 1.5, "divergence": 31.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD {"kind": "position_basis", "ref": 71.0, "market_mid": 36.0, "divergence": 35.0}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL17OCODEL {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row", "emitted_et": "2026-07-17 04:52:47 PM ET"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17SANALM-ALM {"kind": "position_basis", "ref": 68.0, "market_mid": 26.0, "divergence": 42.0, "emitted_et": "2026-07-17 04:52:47 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
