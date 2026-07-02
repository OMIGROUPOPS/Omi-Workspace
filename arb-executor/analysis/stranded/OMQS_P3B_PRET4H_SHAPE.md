# OMQS — P3b: PRE-T-4H SHAPE STUDY, tier-partitioned (2026-07-01)

**Task (operator's early-hours thesis, Plex-activated by the 19% ceiling):** on the L1 tape, per tier, per pre-schedule bucket: (1) where does combined-≤97 become ACHIEVABLE and at what rate; (2) postability (real two-sided book, or paper); (4) joint throughput (achievable-≤97 × postable). Coverage check FIRST.

## (0) Coverage — L1 recorder DOES reach pre-T-4h
| tier | n | median reach before sched | max | reach ≥4h (pre-T-4h) |
|---|--:|--:|--:|--:|
| main (ATP/WTA) | 120 | **20.5 h** | 37.6 h | **93%** |
| thin (ITF) | 80 | **11.8 h** | 13.3 h | **100%** |
The L1 recorder covers the pre-T-4h region for effectively the whole corpus — the shape study runs on L1; the per-minute foundation is not needed.

## (1)(2)(4) Combined-≤97 achievability × postability × throughput, by tier × bucket
Achievable combined = best-**bid** sum (where a maker rests). Postable = both legs two-sided + combined spread ≤12¢.

**main (ATP/WTA) — NO early-hours opportunity:**
| bucket | n | bidsum med | ≤97% | postable% | JOINT% |
|---|--:|--:|--:|--:|--:|
| T-8h | 112 | 99 | 5 | 100 | 5 |
| T-4h | 112 | 99 | 5 | 100 | 5 |
| T-2h | 113 | 99 | 6 | 100 | 6 |
| T-0 | 120 | 99 | 5 | 100 | 5 |

Main is **postable everywhere but par-bound everywhere** — bid-sum sits at 99, ≤97 is 5-8% at *every* bucket and **does not improve earlier**. There is no pre-T-4h ≤97 window on main. (Per §0A invariant: a par-bound ceiling under perfect timing is a **doctrine signal** — main pairs structurally cannot be discounted, regardless of when you post.)

**thin (ITF) — a REAL early window:**
| bucket | n | bidsum med | ≤97% | postable% | **JOINT%** |
|---|--:|--:|--:|--:|--:|
| T-8h | 80 | 93 | **96** | 64 | 60 |
| T-6h | 80 | 94 | 92 | 76 | 69 |
| **T-4h** | 80 | 95 | **90** | **90** | **80** |
| **T-2h** | 80 | 96 | 90 | 91 | **81** |
| T-1h | 80 | 96 | 84 | 91 | 75 |
| T-30m | 80 | 96 | 85 | 91 | 76 |
| T-0 | 80 | 96 | 80 | 81 | 61 |

**ITF ≤97 is highly achievable early (96% at T-8h) and DEGRADES toward the gun (80% at T-0).** The combined gets more expensive as the match approaches (bid-sum 93→96). Postability is low very-early (64% at T-8h — book too thin) and peaks 90-91% at T-4h/T-2h. **Joint throughput (achievable AND postable) PEAKS at T-4h→T-2h = 80-81%** — that is the ITF sweet spot, and it is *outside* the old inside-T-4h window, which is why the contaminated dry-run ceiling read only 19%.

## Verdict (tier-partitioned)
- **ITF: the early-hours thesis is CONFIRMED.** A cheap, postable ≤97 combined exists in the **T-4h→T-2h** window (JOINT ~80%). This is the build target for the ITF shadow — and it requires the re-anchored/extended W1 from P3a (the old window excluded it).
- **main: the early-hours thesis is FALSIFIED.** Main is par-bound at every bucket (≤97 ≈ 5-8%); no timing recovers it. No pre-T-4h build for main.
- **(3) drift-shapes-per-side pre-T-4h: DEFERRED** — requires a settlement join (winner/loser labels) to re-measure winner-up/loser-down and the heavy-fav crater on the early tape. Queued as the settlement-joined pass.

Method: `p3b.py`. Sample ≤40/cat paired + scheduled + tape-covered.
