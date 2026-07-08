# LIVE VALIDATION — rolling status

- cycle 1 @ **2026-07-08 02:24:02 PM ET** | build `7c7b971` | session boot 07-08 14:22 ET | log `live_v3_20260708.jsonl` | 1015 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 0 violation(s)
**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 14:22 | ATPCHALLENGERMATCH-26JUL08GEAZIN-Z | ATP_CHALL | ? | 27 | 24 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:22 | WTACHALLENGERMATCH-26JUL07KOBMAN-K | WTA_CHALL | ? | 26 | 23 | +3 (adopted_est) | — | pre | single |  | PENDING |
| 14:23 | ITFMATCH-26JUL08DELRAP-RAP | ITF_M | ? | 65 | 62 | +3 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 6 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 5, 'NO_FLOW': 1} | repriceable now: true 1 / false 5 | **cumulative bid_grade lines: 5673 (repriceable true 557 / false 5116)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL06HOLSCH-S | 50 | 2m | 21/86-91/2468 | 90-89 | 36 | **FLOW_ABOVE** | 99 |  |
| ATPCHALLENGERMATCH-26JUL06VUKBRO-B | 49 | 2m | 39/90-93/9311 | 92-91 | 41 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08DRASLO-SLO | 6 | 2m | 0 | 7-16 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL08NAKDEA-DEA | 21 | 2m | 9/51-56/223 | 54-56 | 30 | **FLOW_ABOVE** | 99 |  |
| ITFMATCH-26JUL08POLROZ-POL | 48 | 2m | 4/49-51/343 | 48-50 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→49 |
| ITFWMATCH-26JUL08PARSLA-SLA | 16 | 2m | 11/17-20/954 | 16-17 | 1 | **FLOW_ABOVE** | 13 | flow above but bound 13c < flow -- chasing breaks goal |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 9 tracked game(s) ({'WAKING': 3, 'OPEN': 5, 'QUIET': 1}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ATPCHALLENGERMATCH-26JUL08GEAZIN | ATP_CHALL | 4.433 | 1 | **OPEN** |
| ITFMATCH-26JUL08DELRAP | ITF_M | 0.967 | 1 | **OPEN** |
| ITFMATCH-26JUL08NAKDEA | ITF_M | 4.833 | 2 | **OPEN** |
| ITFMATCH-26JUL08POLROZ | ITF_M | 0.6 | 2 | **OPEN** |
| ITFWMATCH-26JUL08PARSLA | ITF_W | 1.5 | 1 | **OPEN** |
| ITFMATCH-26JUL08DRASLO | ITF_M | 0.0 | 9 | **QUIET** |
| ATPCHALLENGERMATCH-26JUL06HOLSCH | ATP_CHALL | 4.733 | — | **WAKING** |
| ATPCHALLENGERMATCH-26JUL06VUKBRO | ATP_CHALL | 12.133 | — | **WAKING** |
| WTACHALLENGERMATCH-26JUL07KOBMAN | WTA_CHALL | 0.2 | 1 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
