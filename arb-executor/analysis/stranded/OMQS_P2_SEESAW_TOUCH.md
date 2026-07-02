# OMQS — P2: SEESAW AT THE TOUCH (2026-07-01, Plex precondition)

**Question:** the seesaw (paired mid-sum ≈ 0.998) is a MID fact. The sequential-divot doctrine acts at the TOUCH (best bid / best ask). Do bid-sum and ask-sum track mid-sum tightly enough (r>0.9, offset <±2¢) to license sequential per-leg divot entry — or does the touch diverge, requiring simultaneous resting posts on the illiquid tier?

## Method
100 paired events Jun 24-30 (≤20/cat), 30s grid T-4h→T-0 (scheduled-start anchored — the seesaw correlation is anchor-invariant, so robust to P1's clock finding). Per grid point: paired mid-sum, bid-sum, ask-sum, last-sum. Pearson r of bid-sum & ask-sum vs mid-sum; mean offsets; combined-spread tail; divot-timing check (at leg-1 mid local-minima, is leg-2's bid ≥ its running median?). Tiered main(ATP/WTA) vs thin(ITF).

## Result — CLEAN TIER SPLIT
| tier | events | r(bid,mid) | r(ask,mid) | offset bid/ask vs mid | spread>6¢ tail | verdict |
|---|--:|--:|--:|--:|--:|---|
| **main (ATP/WTA)** | 60 | **0.864** | **0.879** | **±1.12¢** ✅ | **1%** | near-tight — touch tracks mid |
| **thin (ITF)** | 40 | **0.469** | **0.535** | **±3.64¢** ❌ | **66%** | DIVERGENT — touch ≠ mid |

- **main:** r narrowly under the 0.9 gate but offset PASSES (±1.1¢) and the wide-spread tail is negligible (1%). Effectively **tight tracking.**
- **thin(ITF):** correlation collapses (0.47/0.54), offset fails (±3.6¢), and **two-thirds of the time the combined spread exceeds 6¢.** The touch is decoupled from the mid.

## Divot-timing check — and a tension
| tier | divots | leg-2 bid strong (≥ run-median) at leg-1 divot | lagging |
|---|--:|--:|--:|
| main | 3 | 100% (N=3, not meaningful — main drifts smoothly, few divots) | 0 |
| thin (ITF) | 41 | **83%** | 17% (median gap 1.5¢) |

**The tension Plex must weigh:** the divots (catchable sharp dips) are **almost entirely an ITF phenomenon** (41 vs 3) — main markets drift smoothly with little to catch. The inverse seesaw *does* hold at the divot (83% of ITF divots have leg-2's bid strong). **But ITF is exactly the tier where bid/ask sums diverge from the mid (r 0.47, 66% wide-spread).** So the markets with the most to catch are the least reliable at the touch; the tier that tracks tight (main) has few divots.

## Decision (per Plex's rule)
- **main / liquid tier → SEQUENTIAL DOCTRINE LICENSED** (tight tracking: offset ±1.1¢, spread tail 1%, r ≈ 0.87).
- **thin / ITF tier → SEQUENTIAL NOT LICENSED; requires SIMULTANEOUS RESTING POSTS** (divergence: r 0.47-0.54, offset ±3.6¢, 66% wide-spread).
- **Open caveat:** on main the sequential-divot premise is weakly exercised (few divots — smooth drift); on ITF the divots exist and the seesaw holds (83%) but the wide spread means you cannot cleanly capture the divot at the touch. Sequential-divot's real edge is therefore **narrow**: it needs a liquid market (tight touch) that also dips (rare on main). This is the open question the operator flagged — P2 sharpens it rather than fully closing it.

Method: `p2.py`.
