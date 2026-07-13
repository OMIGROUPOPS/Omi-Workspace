# LIVE VALIDATION — rolling status

- cycle 119 @ **2026-07-13 05:29:20 PM ET** | build `a8b19264` | session boot 07-13 15:32 ET | log `live_v3_20260713.jsonl` | 5923 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 13 violation(s)
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
| 17:01:27 | **taker_capped** | KXITFMATCH-26JUL13STEKOT-KOT | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |
| 17:11:32 | **taker_capped** | KXITFMATCH-26JUL13STEKOT-KOT | taker verdict DEFERRED at daily cap 3 (3 today; sunset n>=30 graded) |

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:11 | ITFMATCH-26JUL13STEKOT-KOT | ITF_M | underdog | 20 | 20 | +0 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 17 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 10, 'NO_FLOW': 7} | repriceable now: true 8 / false 9 | **cumulative bid_grade lines: 9506 (repriceable true 1401 / false 8105)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13WOLFEN-F | 21 | 88m | 12/22-23/183 | 22-23 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→22 |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 116m | 2/59-60/19 | 59-60 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFMATCH-26JUL13DEMTRI-TRI | 12 | 28m | 0 | 12-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13IBRCAM-IBR | 40 | 76m | 9/45-45/167 | 41-45 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SCH | 25 | 24m | 0 | 25-48 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SIK | 51 | 35m | 0 | 51-74 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GILNAY-GIL | 63 | 14m | 0 | 63-67 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GILNAY-NAY | 32 | 29m | 4/36-40/54 | 32-36 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→36 |
| ITFWMATCH-26JUL13OHADOD-DOD | 25 | 45m | 3/29-29/65 | 25-29 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→29 |
| ITFWMATCH-26JUL13OHADOD-OHA | 70 | 61m | 1/76-76/1 | 70-75 | 6 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL13SATSCH-SCH | 9 | 7m | 0 | 9-49 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 116m | 13/51-54/2418 | 53-54 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 116m | 2/60-60/32 | 59-60 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→60 |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 116m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BLISAS-SAS | 55 | 116m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 116m | 8/89-90/236 | 89-90 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→89 |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 116m | 1/20-20/1 | 19-20 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→20 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 14 tracked game(s) ({'WAKING': 13, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL13DEMTRI | ITF_M | 0.0 | 36 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL13WOLFEN | ATP_CHALL | 0.167 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13IBRCAM | ITF_M | 0.1 | 4 | **WAKING** |
| ITFMATCH-26JUL13SIKSCH | ITF_M | 0.033 | 23 | **WAKING** |
| ITFMATCH-26JUL13STEKOT | ITF_M | 0.167 | 6 | **WAKING** |
| ITFWMATCH-26JUL13GILNAY | ITF_W | 0.167 | 4 | **WAKING** |
| ITFWMATCH-26JUL13OHADOD | ITF_W | 0.1 | 4 | **WAKING** |
| ITFWMATCH-26JUL13SATSCH | ITF_W | 0.067 | 40 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.033 | 1 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.033 | 1 | **WAKING** |

## PATTERNS (sub-B) — 1
- half_arm_aging: KXITFMATCH-26JUL13STEKOT-KOT {"fill": 20, "age_min": 78, "mode": "NO_BID(sib rested earlier, none now)"}

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
