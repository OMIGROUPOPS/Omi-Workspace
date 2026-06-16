# C-STAIRCASE-REVALIDATE — gated re-validation (commit-for-review, NOT sealed)

Predecessor: `range_final` @ **3c2161c**. Pre-committed schedule: `range_final_walk_schedule.json` @ **3a701ba** (the hypothesis, registered before the walk, NOT tuned). Latch cancel: `live_v4` match_live_cancel @ **0499570**.

## Two corrections tested
1. **Walking staircase** (not the static deep bid that produced the −28pp fill artifact) — depth steps deep_target→anchor-1 over the pre-committed knots, most aggressive final 10 min.
2. **WTA_CHALL n re-booked** via the walk leg-population + **class-A pipeline trace** (not a re-book comparison alone).

## (β) Tail cancel keys on _is_match_live (volume-burst latch), NOT wall-clock — CONFIRMED
`live_v4.py` match_live_cancel fires on `_is_match_live` alone (commit 0499570, delay-proof). Sim cutoff = `onset` (the burst-latch minute); no wall-clock 2-min floor.

## (γ) Per-cat bars  [ROC: win ≥ +0.30, no cat loses > −0.20 (±0.10 noise); FILL: within ±5pp]
| cat | CUR real | STAIR real | ΔROC | ROC bar | CUR fill% | STAIR fill% | ΔFILL | FILL bar |
|---|---|---|---|---|---|---|---|---|
| **ATP_MAIN** | 9.86 | 10.38 | **+0.52** | **WIN/PASS** | 76.2 | 72.3 | −4.0 | **PASS** |
| WTA_MAIN | 11.42 | 11.04 | −0.37 | **FAIL** | 66.2 | 70.2 | +4.0 | PASS |
| ATP_CHALL | 11.24 | 11.06 | −0.18 | neutral | 58.0 | 72.1 | +14.1 | **FAIL** |
| WTA_CHALL | 10.34 | 9.03 | −1.31 | **FAIL** | 60.5 | 78.5 | +18.0 | **FAIL** |

**Only ATP_MAIN clears BOTH binding bars.** WTA_MAIN fails ROC (−0.37 loss > −0.20); ATP_CHALL fails FILL (+14.1pp — more near-market fills, no ROC gain, the 06-02 "more fills ≠ better" pattern); WTA_CHALL fails both.

## WTA_CHALL — class A (evidence), pipeline bug found? **NO**
- `categorize()` (`data/scripts/cell_key_helpers.py:42`) is a pure ticker-prefix matcher — **no category-specific drop / tournament-filter / date-gap**.
- PMF WTA_CHALL = 649 events ≈ 1,298 legs, **faithfully matches the g9_metadata source (1,318 WTA_CHALL legs)** → the build drops nothing.
- g9 source coverage: WTA_CHALL **1,318** vs ATP_CHALL 7,782 / ATP_MAIN 5,646 / WTA_MAIN 5,364 → WTA_CHALL is genuinely small **in the historical g9 window**. (Recent `kalshi_price_snapshots` shows WTA_CHALL has grown forward — 539 ≈ WTA_MAIN 711 — but that growth is not in the g9 tape the surface is built from.)
- **VERDICT: no pipeline bug; thinness genuine; WTA_CHALL stays HELD-CURRENT (do not deepen).**

## Sibling byte-stability
Class A found no bug → no re-book → **no booking count changed**; the other 3 cats' counts are unchanged by construction. Engine sanity holds: ATP_CHALL CUR real_roc **11.24** (== committed `entry_lift_permatch`); ATP_MAIN **18.48** under the old probe exit / **9.86** under the deployed `_full` exit (reseal-superseded baseline; walk sound).

## Verdict — commit-for-review, NO seal / NO deploy / NO LOCKED_DOWN
- **ATP_MAIN staircase passes both binding bars** (ΔROC +0.52, ΔFILL −4.0) → ratifiable deploy candidate, **ATP_MAIN only**.
- WTA_MAIN, ATP_CHALL → stay current (each fails a bar).
- WTA_CHALL → held-current (genuine thinness, class-A confirmed).
