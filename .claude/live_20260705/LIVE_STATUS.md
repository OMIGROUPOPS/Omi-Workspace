# LIVE VALIDATION — rolling status

- cycle 115 @ **2026-07-13 04:47:35 PM ET** | build `066d0c26` | session boot 07-13 15:32 ET | log `live_v3_20260713.jsonl` | 4130 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 11 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 15:38:15 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 1958.3 |
| 15:43:02 | **taker_capped** | KXITFWMATCH-26JUL13OLIKAI-KAI | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 15:43:03 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 15:53:02 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:03:03 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:11:18 | **taker_capped** | KXITFMATCH-26JUL13STEKOT-KOT | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:13:06 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:13:11 | **self_fill_bell** | KXITFMATCH-26JUL13IBRCAM-IBR | own buys rose 5c (35->40) in 1800s -> match-live presumption, entry buys FROZEN |
| 16:21:19 | **taker_capped** | KXITFMATCH-26JUL13STEKOT-KOT | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:23:11 | **taker_capped** | KXATPCHALLENGERMATCH-26JUL13RODALK-ALK | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 16:31:22 | **taker_capped** | KXITFMATCH-26JUL13STEKOT-KOT | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:11 | ITFMATCH-26JUL13STEKOT-KOT | ITF_M | underdog | 20 | 20 | +0 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 16 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 8} | repriceable now: true 5 / false 11 | **cumulative bid_grade lines: 9496 (repriceable true 1400 / false 8096)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13WOLFEN-F | 21 | 47m | 6/23-23/89 | 22-23 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 75m | 2/59-60/19 | 59-60 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFMATCH-26JUL13IBRCAM-IBR | 40 | 34m | 4/45-45/61 | 40-45 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SCH | 18 | 46m | 0 | 18-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13STEKOT-STE | 77 | 36m | 1/85-85/25 | 79-83 | 8 | **FLOW_ABOVE** | 77 | flow above but bound 77c < flow -- chasing breaks goal |
| ITFWMATCH-26JUL13GILNAY-GIL | 60 | 46m | 0 | 60-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GILNAY-NAY | 31 | 40m | 0 | 31-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13OHADOD-DOD | 25 | 3m | 0 | 25-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13OHADOD-OHA | 70 | 19m | 1/76-76/1 | 70-75 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13SATSCH-SCH | 8 | 44m | 0 | 8-50 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 75m | 11/51-53/2081 | 53-54 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 75m | 1/60-60/29 | 59-60 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 75m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BLISAS-SAS | 55 | 75m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 75m | 7/89-90/235 | 89-90 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 75m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFMATCH-26JUL13STEKOT | 20 | 83 | **103** | 97 | +6 |

## FLOW-STATE — 13 tracked game(s) ({'WAKING': 10, 'QUIET': 3}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL13SIKSCH | ITF_M | 0.0 | 32 | **QUIET** |
| ITFWMATCH-26JUL13GILNAY | ITF_W | 0.0 | 9 | **QUIET** |
| ITFWMATCH-26JUL13SATSCH | ITF_W | 0.0 | 42 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL13WOLFEN | ATP_CHALL | 0.133 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.033 | 1 | **WAKING** |
| ITFMATCH-26JUL13IBRCAM | ITF_M | 0.133 | 5 | **WAKING** |
| ITFMATCH-26JUL13STEKOT | ITF_M | 0.067 | 4 | **WAKING** |
| ITFWMATCH-26JUL13OHADOD | ITF_W | 0.1 | 4 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.167 | 1 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXITFMATCH-26JUL13STEKOT-KOT {"fill": 20, "age_min": 36, "mode": "SET_BELOW_FLOW(prints 8c above)", "emitted_et": "2026-07-13 04:47:35 PM ET"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
