# LIVE VALIDATION — rolling status

- cycle 61 @ **2026-07-09 12:40:41 AM ET** | build `09fa303` | session boot 07-09 00:36 ET | log `live_v3_20260709.jsonl` | 1524 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 00:40:05 | **combined_over_goal** | KXITFWMATCH-26JUL09SEDKRO | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 3 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:36 | ITFWMATCH-26JUL09SEDKRO-SED | ITF_W | ? | 8 | 4 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
| 00:36 | ITFMATCH-26JUL08MUJBEL-MUJ | ITF_M | ? | 39 | 35 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 00:40 | ITFWMATCH-26JUL09SEDKRO-KRO | ITF_W | ? | 90 | 88 | +2 (fill_est) | — | pre | pair | 98 | PENDING |

## RESTING BIDS — 25 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 8, 'NO_FLOW': 16, 'FLOW_AT_LEVEL': 1} | repriceable now: true 5 / false 20 | **cumulative bid_grade lines: 6104 (repriceable true 679 / false 5425)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL08DERMIL-DER | 71 | 4m | 1/75-75/1 | 73-75 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| ITFMATCH-26JUL08MUJBEL-MUJ | 42 | 4m | 1/43-43/4 | 43-48 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFMATCH-26JUL09ARCALU-ALU | 49 | 4m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ARCALU-ARC | 48 | 4m | 0 | 48-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BEAVAN-VAN | 45 | 2m | 0 | 45-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BLATAL-BLA | 45 | 2m | 0 | 45-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAKROB-MAK | 37 | 4m | 0 | 37-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAKROB-ROB | 58 | 4m | 0 | 58-62 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 4m | 34/85-89/3231 | 86-87 | 18 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL08NAKMAL-MAL | 23 | 4m | 253/27-38/19854 | 33-27 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→27 |
| ITFWMATCH-26JUL09AHLMAK-AHL | 30 | 4m | 0 | 30-34 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09AHLMAK-MAK | 66 | 3m | 0 | 66-71 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09BOSGOL-GOL | 49 | 2m | 0 | 49-51 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09BURERC-ERC | 26 | 2m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-BER | 73 | 2m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DENKAZ-DEN | 66 | 2m | 0 | 66-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DENKAZ-KAZ | 26 | 4m | 0 | 26-33 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09KOMPER-KOM | 28 | 2m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-MAI | 22 | 2m | 0 | 22-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAMJAN-MAM | 54 | 1m | 2/56-57/24 | 56-58 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ITFWMATCH-26JUL09MATDYU-MAT | 86 | 3m | 1/87-87/1 | 86-87 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→87 |
| ITFWMATCH-26JUL09PAWTEI-PAW | 78 | 2m | 0 | 79-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-NIS | 9 | 4m | 2/14-14/13 | 9-14 | 5 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL09TUPNUP-NUP | 8 | 4m | 28/8-10/601 | 8-10 | 0 | **FLOW_AT_LEVEL** | 99 |  |
| ITFWMATCH-26JUL09TUPNUP-TUP | 87 | 3m | 1/92-92/2 | 88-92 | 5 | **FLOW_ABOVE** | 99 |  |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
no open half-pairs

## FLOW-STATE — 21 tracked game(s) ({'WAKING': 17, 'OPEN': 4}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 9.6 | 1 | **OPEN** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 1.0 | 2 | **OPEN** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 2.533 | 2 | **OPEN** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 4.767 | 2 | **OPEN** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.067 | 2 | **WAKING** |
| ITFMATCH-26JUL08MUJBEL | ITF_M | 0.333 | 5 | **WAKING** |
| ITFMATCH-26JUL09ARCALU | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09BEAVAN | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09BLATAL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09MAKROB | ITF_M | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 15.9 | — | **WAKING** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.867 | 4 | **WAKING** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09BURERC | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL09CEUBER | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL09DENKAZ | ITF_W | 0.033 | 7 | **WAKING** |
| ITFWMATCH-26JUL09KOMPER | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL09MAIALL | ITF_W | 0.033 | 5 | **WAKING** |
| ITFWMATCH-26JUL09MATDYU | ITF_W | 0.1 | 1 | **WAKING** |
| ITFWMATCH-26JUL09PAWTEI | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 1.2 | 5 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
