# The 603 map — pre-match basis (canonical)  ·  `MODEL_FREE_CEILING`

Analysis seat only. Read-only. Print source = sealed re-pull (938dca47) via
`prints.jsonl`. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/THE_603_MAP_PREMATCH.json`.
Canonical stamp: `PRE_MATCH_CLOSE_BASIS`.

## Window law (ruled)

Span = **full pre-match life** = first print/book → **the bell (match start)**. **Close =
the last print before the bell** (the pre-match closing line). Everything (traded-below,
rest levels, seller flow) is clipped to the pre-match phase. The in-match trading-phase
map is stamped **`WRONG_PHASE_FOR_OBJECTIVE`** — the Window-1 arbitrage objective is the
pre-match line, not in-match trading.

**Validation:** ARNROM's pre-match close is **(ARN 62, ROM 39)** — exactly the original
audited closes. The audited closes *were* the pre-match closing lines; this basis is the
correct phase, and it confirms the entire prior audited-close body.

## The bell — honest clock (source `REAL_START_LEDGER_V3`, sha `84b455c5…`)

| precision_class (confidence) | games | bell used |
|---|--:|---|
| **exact** | **234** | `exact_start_utc` (official provider match-start) |
| live_by_only | 450 | `known_live_by_utc` (public-tape 5-prints-in-15m onset / live-v3/v4 log / tennis-db) |
| clean_interval | 31 | interval-resolved onset |
| schedule_only | 63 | `schedule_bound_utc` (last resort) |
| contradictory | 26 | best-available, flagged |

Estimation method, per precedence: exact official start → tape/live onset → schedule
bound. 234 exact, 792 with a usable bell; 12 games have **no pre-match prints**
(`NO_PREMATCH_PRINTS`).

## Tier census — pre-match life (conservation 804)

| tier | games |
|---|--:|
| **T1** both traded below own pre-match close | **492** |
| **T2** one did, other did not (blocker named) | **287** |
| **T3** neither | **13** |
| NO_PREMATCH_PRINTS | 12 |
| **total** | **804** |

**T1-joint** (both below close AND sum < 100): **464** — ATP_CHALL 198 · ATP_MAIN 107 ·
WTA_MAIN 107 · WTA_CHALL 52. Top cat×region: ATP_CHALL 51_75/26_50 **70**, 26_50/51_75
**61**; ATP_MAIN 26_50/51_75 41, 51_75/26_50 34; WTA_MAIN 26_50/51_75 29.

**By confidence** (tier split): exact-234 → T1 **167** / T2 63 / T3 2; live_by → T1 273 /
T2 160 / T3 10; schedule_only → T1 15 / T2 45 / T3 1. The high-confidence core (exact
234) is T1-joint **164 / 232**.

## Presence-convertible mass

For the 300 non-T1 games (287 T2 + 13 T3), lawful rest levels come from decision-time
pre-match evidence (running traded-low band / qualifying-floor path, close-free). A
blocker converts if seller-aggressed flow lands 1c/2c/3c above a below-close rest.

**Convertible 1c / 2c / 3c = 17 / 25 / 25.** Examples span both tours and confidences
(HOHSUR, TROGEO, CAMBOO exact; DONWES, SANLOP, TIMSAS live_by). Real mass — unlike the
in-match bases, the pre-match blocker often sits mid-range with genuine seller flow just
above a below-close rest.

## The verdict — achievable joint (against 603)

| conversion of T2/T3 | 1c | 2c / 3c |
|---|--:|--:|
| 0 % | 464 | 464 |
| 25 % | 468 | 470 |
| 50 % | 472 | 476 |
| 75 % | 477 | 483 |
| 100 % | 481 | **489** |

**Reachable-on-tape = 517** (T1 492 + 25 convertible). **UNREACHABLE_ON_THIS_TAPE = 275**
(ATP_CHALL 135 · WTA_CHALL 71 · WTA_MAIN 36 · ATP_MAIN 33; by confidence: live_by 156 ·
exact 56 · schedule 46).

**Against the named 603:** the pre-match map delivers **464 firm joint** (both legs below
their pre-match closing line, sum < 100), rising to **489** at full 3c presence
conversion, over a **reachable universe of 517**. The 603 denominator sits *above* the
517 the tape actually reaches on the pre-match phase — so on this basis 464–489 achievable
joint is measured against 517 reachable, not 603; reported here transparently rather than
forced to the label.

## Named rows

| game | pre-match close | tier | joint? | confidence |
|---|---|---|---|---|
| **ARNROM** | ARN 62 · ROM 39 | T1 | yes | exact — matches the audited closes exactly |
| **LAJVAN** | LAJ 45 · VAN 58 | T1 | yes | exact |

## Conservation

804 = 492 T1 + 287 T2 + 13 T3 + 12 NO_PREMATCH_PRINTS. Reachable 517 + unreachable 275 =
792 scored (+12 no-prematch = 804). T1-joint 464; achievable joint 464 → 489 at full
conversion. Bell: 234 exact + 558 estimated (live_by/interval/schedule) + 12 no-prematch.
In-match trading-phase map (`THE_603_MAP.json`, T1-joint 750) stamped
`WRONG_PHASE_FOR_OBJECTIVE`; settlement-basis control stamped `DEGENERATE_SETTLEMENT_BASIS`.

*All figures `MODEL_FREE_CEILING`.*
