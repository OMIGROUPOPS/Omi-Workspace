# LIVE VALIDATION — rolling status

- cycle 112 @ **2026-07-13 04:16:40 PM ET** | build `c0629420` | session boot 07-13 15:32 ET | log `live_v3_20260713.jsonl` | 2844 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 8 violation(s)
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

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_taker_capped.md**

## FILLS — 1 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:11 | ITFMATCH-26JUL13STEKOT-KOT | ITF_M | underdog | 20 | 20 | +0 (place_cell) | — | pre | single |  | PENDING |

## RESTING BIDS — 16 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 4, 'NO_FLOW': 12} | repriceable now: true 4 / false 12 | **cumulative bid_grade lines: 9488 (repriceable true 1400 / false 8088)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13WOLFEN-F | 21 | 16m | 2/23-23/24 | 22-23 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→23 |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 44m | 1/59-59/16 | 58-59 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→59 |
| ITFMATCH-26JUL13IBRCAM-IBR | 40 | 3m | 0 | 40-45 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13SIKSCH-SCH | 18 | 15m | 0 | 18-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL13STEKOT-STE | 77 | 5m | 0 | 78-83 | — | **NO_FLOW** | 77 |  |
| ITFWMATCH-26JUL13GILNAY-GIL | 60 | 15m | 0 | 60-69 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13GILNAY-NAY | 31 | 9m | 0 | 31-40 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13OHADOD-DOD | 22 | 1m | 0 | 23-29 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13OHADOD-OHA | 65 | 1m | 0 | 66-76 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SATSCH-SCH | 8 | 13m | 0 | 8-50 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13ARAZID-ARA | 48 | 44m | 9/51-51/2071 | 52-51 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| WTAMATCH-26JUL13BADKAL-BAD | 59 | 44m | 0 | 59-60 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BADKAL-KAL | 40 | 44m | 0 | 40-41 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13BLISAS-SAS | 55 | 44m | 0 | 55-56 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KRETOM-KRE | 87 | 44m | 2/90-90/13 | 89-90 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→90 |
| WTAMATCH-26JUL13VALCOS-COS | 16 | 44m | 0 | 19-20 | — | **NO_FLOW** | 99 |  |

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
| ATPCHALLENGERMATCH-26JUL13WOLFEN | ATP_CHALL | 0.1 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL13IBRCAM | ITF_M | 0.0 | 5 | **WAKING** |
| ITFMATCH-26JUL13STEKOT | ITF_M | 0.167 | 1 | **WAKING** |
| ITFWMATCH-26JUL13OHADOD | ITF_W | 0.033 | 6 | **WAKING** |
| WTAMATCH-26JUL13ARAZID | WTA_MAIN | 0.267 | — | **WAKING** |
| WTAMATCH-26JUL13BADKAL | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13BLISAS | WTA_MAIN | 0.0 | 1 | **WAKING** |
| WTAMATCH-26JUL13KRETOM | WTA_MAIN | 0.067 | 1 | **WAKING** |
| WTAMATCH-26JUL13VALCOS | WTA_MAIN | 0.0 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
