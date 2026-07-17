# LIVE VALIDATION — rolling status

- cycle 228 @ **2026-07-17 05:03:06 PM ET** | build `a8b08f1e` | session boot 07-17 15:16 ET | log `live_v3_20260717.jsonl` | 5698 session events | monitor READ-ONLY

## ⚠ GUN FEED: last new in-play sighting 49 min ago (>30 tripwire; source observed_starts.db)

## ENTRY DOSSIERS (vault-wired: every surface consulted or named — last 4)
- placed:path_aim UL18TIKSAT-TIK aim=47 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL18TUPSHO-SHO aim=38 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL18JANYOD-JAN aim=45 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co
- placed:path_aim UL18JANYOD-YOD aim=30 | atlas_page:CONS,contention_s:CONS,pair_state:CONS,reach_law:CONS,range_cell_m:GAP,dip_timing:CONS,flow_state:CONS,orientation_:CONS,fv_gap:NO-R,refuse_margi:CONS,operator_adj:CONS,fill_regime:CONS,honest_clock:CONS,w1_co

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: **PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**

## ZERO-TOLERANCE — 4 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:18:52 | **self_fill_bell** | KXITFMATCH-26JUL17OCODEL-OCO | own buys rose 6c (10->16) in 1800s -> match-live presumption, entry buys FROZEN |
| 15:25:55 | **self_fill_bell** | KXATPCHALLENGERMATCH-26JUL17LAJNOG-NOG | own buys rose 4c (24->28) in 1800s -> match-live presumption, entry buys FROZEN |
| 15:31:17 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU | flatten DEFERRED: ev -1.29 above margin floor -3.0 |
| 16:54:35 | **flatten_leash** | KXATPCHALLENGERMATCH-26JUL17VUKGAL-GAL | flatten DEFERRED: ev -0.77 above margin floor -3.0 |

## FILLS — 7 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 15:16 | ITFMATCH-26JUL17NEFGAI-GAI | ITF_M | ? | 46 | 39 | +7 (window_cell) | — | pre | single |  | MIXED |
| 15:31 | ATPCHALLENGERMATCH-26JUL17HOLBOU-B | ATP_CHALL | ? | 33 | 31 | +2 (window_cell) | — | pre | single |  | MIXED |
| 16:07 | ATPCHALLENGERMATCH-26JUL17WONJOH-W | ATP_CHALL | ? | 64 | 61 | +3 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 16:32 | ATPCHALLENGERMATCH-26JUL17SMIYUN-Y | ATP_CHALL | ? | 63 | 61 | +2 (window_cell) | — | pre | single |  | GIFT_CLASS |
| 16:47 | ITFMATCH-26JUL17OCODEL-OCO | ITF_M | ? | 17 | 12 | +5 (place_cell) | — | pre | pair | 99 | PENDING |
| 16:47 | ITFMATCH-26JUL17OCODEL-DEL | ITF_M | ? | 82 | 79 | +3 (fill_est) | — | pre | pair | 99 | PENDING |
| 16:54 | ATPCHALLENGERMATCH-26JUL17VUKGAL-G | ATP_CHALL | ? | 53 | 50 | +3 (window_cell) | — | pre | single |  | GIFT_CLASS |

## RESTING BIDS — 7 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 6, 'NO_FLOW': 1} | repriceable now: true 1 / false 6 | **cumulative bid_grade lines: 12592 (repriceable true 1655 / false 10937)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17FORTOM-F | 31 | 63m | 1/35-35/5 | 34-35 | 4 | **FLOW_ABOVE** | 32 | REPRICEABLE→32 |
| ATPCHALLENGERMATCH-26JUL17FORTOM-T | 66 | 1m | 0 | 66-67 | — | **NO_FLOW** | 63 |  |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-L | 71 | 104m | 18/72-72/7069 | 71-72 | 1 | **FLOW_ABOVE** | 69 | flow above but bound 69c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17LAJNOG-N | 28 | 97m | 4/29-29/8 | 28-29 | 1 | **FLOW_ABOVE** | 26 | flow above but bound 26c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17SMIYUN-S | 32 | 29m | 2/37-37/5 | 36-37 | 5 | **FLOW_ABOVE** | 34 | flow above but bound 34c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17VUKGAL-V | 44 | 9m | 10/48-49/602 | 48-49 | 4 | **FLOW_ABOVE** | 44 | flow above but bound 44c < flow -- chasing breaks goal |
| ATPCHALLENGERMATCH-26JUL17WONJOH-J | 33 | 55m | 8/36-37/476 | 36-37 | 3 | **FLOW_ABOVE** | 33 | flow above but bound 33c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL17NEFGAI | 46 | 2 | **48** | 97 | -49 |
| ATPCHALLENGERMATCH-26JUL17SMIYUN | 63 | 37 | **100** | 97 | +3 |
| ATPCHALLENGERMATCH-26JUL17WONJOH | 64 | 37 | **101** | 97 | +4 |
| ATPCHALLENGERMATCH-26JUL17VUKGAL | 53 | 49 | **102** | 97 | +5 |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | 33 | 97 | **130** | 97 | +33 |

## FLOW-STATE — 8 tracked game(s) ({'WAKING': 2, 'QUIET': 1, 'OPEN': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL17LAJNOG | ATP_CHALL | 0.433 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17SMIYUN | ATP_CHALL | 0.3 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17VUKGAL | ATP_CHALL | 1.067 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17WONJOH | ATP_CHALL | 0.6 | 1 | **OPEN** |
| ITFMATCH-26JUL17OCODEL | ITF_M | 0.5 | 1 | **OPEN** |
| ATPCHALLENGERMATCH-26JUL17HOLBOU | ATP_CHALL | 0.0 | — | **QUIET** |
| ATPCHALLENGERMATCH-26JUL17FORTOM | ATP_CHALL | 0.2 | 1 | **WAKING** |
| ITFMATCH-26JUL17NEFGAI | ITF_M | 53.967 | — | **WAKING** |

## PATTERNS (sub-B) — 11
- half_arm_aging: KXITFMATCH-26JUL17NEFGAI-GAI {"fill": 46, "age_min": 106, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17DELFUE-DEL {"kind": "position_basis", "ref": 86.0, "market_mid": 29.0, "divergence": 57.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU {"fill": 33, "age_min": 92, "mode": "NO_BID(sib rested earlier, none now)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD {"kind": "position_basis", "ref": 71.0, "market_mid": 26.5, "divergence": 44.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17SANALM-ALM {"kind": "position_basis", "ref": 68.0, "market_mid": 34.5, "divergence": 33.5}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL17WONJOH-WON {"fill": 64, "age_min": 56, "mode": "SET_BELOW_FLOW(prints 3c above)"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17HOLBOU-BOU {"kind": "position_basis", "ref": 33.0, "market_mid": 1.5, "divergence": 31.5}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17RODCRA-ROD {"kind": "position_basis", "ref": 71.0, "market_mid": 36.0, "divergence": 35.0}
- half_arm_aging: KXATPCHALLENGERMATCH-26JUL17SMIYUN-YUN {"fill": 63, "age_min": 30, "mode": "SET_BELOW_FLOW(prints 5c above)", "emitted_et": "2026-07-17 05:03:06 PM ET"}
- combined_over_goal_UNVERIFIED_BASIS: KXITFMATCH-26JUL17OCODEL {"combined": 99, "detail": "pair combined 99c > 97c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) \u2014 exchange-truth check required, NOT a ZT row"}
- reality_divergence: KXATPCHALLENGERMATCH-26JUL17SANALM-ALM {"kind": "position_basis", "ref": 68.0, "market_mid": 26.0, "divergence": 42.0}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
