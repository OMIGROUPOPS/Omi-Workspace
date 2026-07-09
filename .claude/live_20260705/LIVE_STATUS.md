# LIVE VALIDATION — rolling status

- cycle 62 @ **2026-07-09 12:50:53 AM ET** | build `45c0d73` | session boot 07-09 00:36 ET | log `live_v3_20260709.jsonl` | 2759 session events | monitor READ-ONLY
- tripwire artifact: absent (quiet)

## ZERO-TOLERANCE — 1 violation(s)
| ET | class | who | detail |
|---|---|---|---|
| 00:40:05 | **combined_over_goal** | KXITFWMATCH-26JUL09SEDKRO | pair combined 98c > goal 97c [organic: DEFECT-CLASS] |

## FILLS — 6 graded (session)
| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00:36 | ITFWMATCH-26JUL09SEDKRO-SED | ITF_W | ? | 8 | 4 | +4 (adopted_est) | — | pre | pair | 98 | PENDING |
| 00:36 | ITFMATCH-26JUL08MUJBEL-MUJ | ITF_M | ? | 39 | 35 | +4 (adopted_est) | — | pre | single |  | PENDING |
| 00:40 | ITFWMATCH-26JUL09SEDKRO-KRO | ITF_W | ? | 90 | 88 | +2 (fill_est) | — | pre | pair | 98 | PENDING |
| 00:41 | ITFWMATCH-26JUL08NAKMAL-MAL | ITF_W | ? | 23 | 19 | +4 (fill_est) | — | pre | single |  | PENDING |
| 00:48 | ITFWMATCH-26JUL09AHLMAK-AHL | ITF_W | ? | 31 | 27 | +4 (fill_est) | — | pre | single |  | PENDING |
| 00:50 | ITFWMATCH-26JUL08LUENAT-LUE | ITF_W | ? | 78 | 76 | +2 (fill_est) | — | pre | single |  | PENDING |

## RESTING BIDS — 25 tape-graded (starvation = NO_FLOW only)
- classes now: {'FLOW_ABOVE': 10, 'NO_FLOW': 15} | repriceable now: true 8 / false 17 | **cumulative bid_grade lines: 6116 (repriceable true 683 / false 5433)** -- the liquid_repost re-arm evidence accumulates here
| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |
|---|---|---|---|---|---|---|---|---|
| ITFMATCH-26JUL08DERMIL-DER | 71 | 14m | 1/75-75/1 | 73-75 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→75 |
| ITFMATCH-26JUL08MUJBEL-MUJ | 42 | 15m | 16/43-51/188 | 50-52 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→43 |
| ITFMATCH-26JUL09ARCALU-ALU | 49 | 14m | 0 | 49-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09ARCALU-ARC | 48 | 14m | 0 | 48-50 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BEAVAN-VAN | 46 | 9m | 0 | 46-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09BLATAL-BLA | 45 | 12m | 0 | 45-49 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAKROB-MAK | 38 | 8m | 0 | 38-42 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MAKROB-ROB | 58 | 14m | 0 | 58-62 | — | **NO_FLOW** | 99 |  |
| ITFMATCH-26JUL09MONBAD-MON | 58 | 8m | 0 | 58-59 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL08CHOYAM-YAM | 67 | 15m | 127/79-89/11275 | 86-80 | 12 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL09AHLMAK-MAK | 66 | 2m | 0 | 68-71 | — | **NO_FLOW** | 66 |  |
| ITFWMATCH-26JUL09BOSGOL-GOL | 49 | 12m | 3/51-51/141 | 49-51 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→51 |
| ITFWMATCH-26JUL09BURERC-ERC | 26 | 12m | 0 | 26-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09CEUBER-BER | 73 | 12m | 0 | 73-75 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DENKAZ-DEN | 66 | 12m | 0 | 66-73 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09DENKAZ-KAZ | 26 | 14m | 1/33-33/2 | 26-33 | 7 | **FLOW_ABOVE** | 99 |  |
| ITFWMATCH-26JUL09KOMPER-KOM | 28 | 12m | 0 | 28-30 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAIALL-MAI | 23 | 9m | 0 | 23-27 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09MAMJAN-MAM | 54 | 11m | 12/56-61/764 | 56-58 | 2 | **FLOW_ABOVE** | 99 | REPRICEABLE→56 |
| ITFWMATCH-26JUL09MATDYU-MAT | 86 | 13m | 1/87-87/1 | 86-87 | 1 | **FLOW_ABOVE** | 99 | REPRICEABLE→87 |
| ITFWMATCH-26JUL09PAWTEI-PAW | 79 | 10m | 0 | 79-80 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09SHONIS-NIS | 13 | 4m | 4/17-18/20 | 14-14 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→17 |
| ITFWMATCH-26JUL09SHONIS-SHO | 80 | 1m | 0 | 81-85 | — | **NO_FLOW** | 99 |  |
| ITFWMATCH-26JUL09TUPNUP-NUP | 9 | 6m | 26/12-14/593 | 9-10 | 3 | **FLOW_ABOVE** | 99 | REPRICEABLE→12 |
| ITFWMATCH-26JUL09TUPNUP-TUP | 88 | 10m | 3/92-92/15 | 88-92 | 4 | **FLOW_ABOVE** | 99 | REPRICEABLE→92 |

## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW
| event | basis | sib ask | achievable | goal | vs goal |
|---|---|---|---|---|---|
| ITFWMATCH-26JUL09AHLMAK | 31 | 71 | **102** | 97 | +5 |

## FLOW-STATE — 23 tracked game(s) ({'WAKING': 18, 'OPEN': 5}; thresholds PROVISIONAL, refit by the early-canvas study; window 30m)
| game | cat | prints/min | spread | state |
|---|---|---|---|---|
| ITFMATCH-26JUL08MUJBEL | ITF_M | 0.833 | 2 | **OPEN** |
| ITFWMATCH-26JUL09AHLMAK | ITF_W | 0.867 | 3 | **OPEN** |
| ITFWMATCH-26JUL09MAMJAN | ITF_W | 1.233 | 2 | **OPEN** |
| ITFWMATCH-26JUL09SEDKRO | ITF_W | 2.333 | 1 | **OPEN** |
| ITFWMATCH-26JUL09TUPNUP | ITF_W | 5.1 | 1 | **OPEN** |
| ITFMATCH-26JUL08DERMIL | ITF_M | 0.033 | 2 | **WAKING** |
| ITFMATCH-26JUL09ARCALU | ITF_M | 0.0 | 1 | **WAKING** |
| ITFMATCH-26JUL09BEAVAN | ITF_M | 0.0 | 3 | **WAKING** |
| ITFMATCH-26JUL09BLATAL | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09MAKROB | ITF_M | 0.0 | 4 | **WAKING** |
| ITFMATCH-26JUL09MONBAD | ITF_M | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL08CHOYAM | ITF_W | 12.067 | — | **WAKING** |
| ITFWMATCH-26JUL08LUENAT | ITF_W | 0.167 | 4 | **WAKING** |
| ITFWMATCH-26JUL08NAKMAL | ITF_W | 24.667 | — | **WAKING** |
| ITFWMATCH-26JUL09BOSGOL | ITF_W | 0.1 | 2 | **WAKING** |
| ITFWMATCH-26JUL09BURERC | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL09CEUBER | ITF_W | 0.0 | 2 | **WAKING** |
| ITFWMATCH-26JUL09DENKAZ | ITF_W | 0.033 | 7 | **WAKING** |
| ITFWMATCH-26JUL09KOMPER | ITF_W | 0.033 | 2 | **WAKING** |
| ITFWMATCH-26JUL09MAIALL | ITF_W | 0.0 | 4 | **WAKING** |
| ITFWMATCH-26JUL09MATDYU | ITF_W | 0.067 | 1 | **WAKING** |
| ITFWMATCH-26JUL09PAWTEI | ITF_W | 0.033 | 1 | **WAKING** |
| ITFWMATCH-26JUL09SHONIS | ITF_W | 1.2 | 4 | **WAKING** |

## PATTERNS (sub-B) — 0

## ERRORS — 0 handler errors this session (ZERO — clean loop)
