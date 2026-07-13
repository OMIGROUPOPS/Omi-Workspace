# LIVE VALIDATION — rolling status

- cycle 19 @ **2026-07-13 12:02:22 AM ET** | build `92fcf15e` | session boot 07-12 20:59 ET | log `live_v3_20260712.jsonl` | 17571 session events | monitor READ-ONLY

## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET) — 0 item(s)
clean overnight — no watch fires
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 5 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 21:03:06 | **chase_cap** | KXITFWMATCH-26JUL12SUNYUN-SUN | chase ladder refused: pursuit_buys 3 >= cap 2 (proposed 53) |
| 21:03:06 | **chase_cap** | KXITFWMATCH-26JUL12SUNYUN-YUN | chase ladder refused: pursuit_buys 3 >= cap 2 (proposed 8) |
| 21:06:16 | **bell_missing** | KXATPMATCH-26JUL12ALTGAS | min_past_start 846.3 |
| 00:02:08 | **chase_cap** | KXITFWMATCH-26JUL13WONBOW-WON | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 25) |
| 00:02:08 | **chase_cap** | KXITFWMATCH-26JUL13WONBOW-WON | chase ladder refused: pursuit_buys 2 >= cap 2 (proposed 25) |

**LIVE DEFECT(S) — forensic blocks written: FORENSIC_chase_cap.md**

## FILLS — 0 graded (session)
none yet this session

## RESTING BIDS — 13 tape-graded (starvation = NO_FLOW only)
- classes now: {'NO_FLOW': 12, 'FLOW_ABOVE': 1} | repriceable now: true 1 / false 12 | **cumulative bid_grade lines: 8736 (repriceable true 1278 / false 7458)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13PRICRI-C | 8 | 2m | 0 | 8-9 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13VILGAN-G | 6 | 2m | 0 | 6-7 | — | **NO_FLOW** | 99 |  |
| ATPCHALLENGERMATCH-26JUL13VILGAN-V | 92 | 2m | 0 | 92-93 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12ALTGAS-ALT | 55 | 181m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| ATPMATCH-26JUL12SONSCH-SON | 65 | 181m | 328/67-70/44920 | 68-68 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→67 |
| ITFMATCH-26JUL13DUHGAT-GAT | 22 | 2m | 0 | 22-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13ARUMCK-ARU | 29 | 1m | 0 | 29-64 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SLASED-SED | 73 | 2m | 0 | 73-84 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SLASED-SLA | 16 | 2m | 0 | 16-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13SVIART-SVI | 16 | 1m | 0 | 16-51 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL13WONBOW-WON | 6 | 2m | 0 | 25-59 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13KAWWAL-WAL | 67 | 29m | 0 | 67-69 | — | **NO_FLOW** | 99 |  |
| WTAMATCH-26JUL13QUERUS-QUE | 28 | 8m | 0 | 28-29 | — | **NO_FLOW** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 11 tracked game(s) ({'WAKING': 6, 'OPEN': 1, 'QUIET': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL13VILGAN | ATP_CHALL | 0.367 | 1 | **OPEN** |
| ITFMATCH-26JUL13DUHGAT | ITF_M | 0.0 | 42 | **QUIET** |
| ITFWMATCH-26JUL13ARUMCK | ITF_W | 0.0 | 35 | **QUIET** |
| ITFWMATCH-26JUL13SVIART | ITF_W | 0.0 | 35 | **QUIET** |
| ITFWMATCH-26JUL13WONBOW | ITF_W | 0.0 | 34 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL13PRICRI | ATP_CHALL | 0.233 | 1 | **WAKING** |
| ATPMATCH-26JUL12ALTGAS | ATP_MAIN | 0.0 | 1 | **WAKING** |
| ATPMATCH-26JUL12SONSCH | ATP_MAIN | 2.7 | — | **WAKING** |
| ITFWMATCH-26JUL13SLASED | ITF_W | 0.133 | 11 | **WAKING** |
| WTAMATCH-26JUL13KAWWAL | WTA_MAIN | 0.033 | 2 | **WAKING** |
| WTAMATCH-26JUL13QUERUS | WTA_MAIN | 0.033 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## DRAIN-REPLAY (zero-tolerance) — 0 violations
every drained entry bid accounted for (replayed / refused-named / none drained)

## ERRORS — 0 handler errors this session (ZERO — clean loop)
