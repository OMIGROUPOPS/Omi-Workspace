# DIFF — park_v9 (fast kernel): Opus's 3 corrections implemented; HAMMER passes; but #2 (engine reactivation) is structurally FALSIFIED by the invariance architecture

Branch: blend/agent-derivation. Files: `park_v9_fast.py` (working), `park_v9_discount.py` (heavy/reference).

## What v9 implements (per Opus's 3 corrections)
- **#1 regime-SWITCH not OR:** favorite (regime A, band-width ≤ WA=3) judged by fire-point stability (xlo within ±3c in ≥α of resamples); cheap/broad (regime B) judged by consensus-band (X credible in ≥α of resamples, `consensus.sum>=2`). One arm each — no disjunction over-admit. FIRE the low edge of the α-consensus band so test-quantity == fired-quantity.
- **#2 decomposition:** EXIT = resolvable ∧ supported ∧ profitable-now (bestEV>holdEV); HOLD = resolvable ∧ supported ∧ 0<bestEV≤holdEV; PARK-engine = resolvable ∧ supported ∧ bestEV≤0; PARK-thin = npos<3; PARK-noise = ~resolvable. α=0.75 FIXED & epistemic; profitability is the parameter-free, basis-carrying comparison.
- **#3 HAMMER:** a PARK-noise cell forced nominally EV>0 by a discount MUST stay PARK.

## Bug A — FIXED (support precedes resolvability)
Old `state()` tested `resolvable` before `npos`, so a thin cell that fails the bootstrap (c92, npos=2, fp=0.63) was mislabeled PARK-noise. With npos<3 you cannot even pose the resolvability question — it is structurally THIN. Reordered: `npos<3 → PARK-thin` first.
- Result: PARK-thin now reachable = [39,65,67,68,73,81,82,92,93,94]. c92 correctly THIN.
- Baseline Counter: **PARK-noise=41, EXIT=39, PARK-thin=10.**

## HAMMER (#3) — PASSES
c5/c6/c10/c17 are nominally profitable (bestEV>holdEV) yet `resolvable=False` → STAY PARK-noise across all discounts. noise→EXIT = [] and EXIT→PARK = [] at every discount. The lottery does not re-enter. ✅

## THE PROBLEM — Opus's #2 "engine reactivates via discount" is STRUCTURALLY IMPOSSIBLE under this kernel
**PARK-engine = [] and HOLD = [] at baseline AND at every discount.** This is not a tracking bug. Two of Opus's own load-bearing claims are mutually exclusive for the engine cells:

1. **Resolvability is basis-invariant** (computed on own moves m=peak−anchor, cached once; cost only prices EV). — Opus's architecture, made literal in v9_fast.
2. **Coverage grows in Part 2 because discounts relax profitability and the engine lights cost-ordered.** — Opus's #2.

But the engine cells (c5/c6/c10) are `~resolvable`, and by (1) they are `~resolvable` at EVERY discount. Discounts move only EV, never resolvability. So a `~resolvable` engine cell can **never** reach EXIT regardless of discount depth. The resolvability gate is an absolute permanent veto → "PARK-engine reactivates via discount" cannot happen.

### Why the engine cells fail resolvability (the data)
At α=0.75 there is NO separating statistic between "diffuse cheap engine" and "true noise":

| c | regime | bw | npos | fp | consensus.sum | peak_incl |
|---|---|---|---|---|---|---|
| 5  | B | 34 | 72 | 0.78 | 0 | 0.67 |
| 6  | B | 34 | 67 | 0.67 | 0 | 0.61 |
| 10 | B | 12 | 34 | 0.71 | 0 | 0.61 |
| 50 (a current EXIT) | B | 10 | 44 | 0.57 | 3 | 0.80 |
| 44 (mid-book) | B | 20 | 49 | 0.40 | 0 | 0.73 |

c5 has npos=72 and fp=0.78 but is regime B, so it is judged on consensus.sum=0 → fails. Its credible mass is a **diffuse smear** (c6 bimodal between X≈7 and X≈37); no single band is credible in ≥75% of resamples. That diffuseness is the engine's *signature* and also indistinguishable from noise at α=0.75.

### Even economically, the deepest engine cells don't light
Driving cost→1 lifts holdEV faster than the thin-reach bestEV (the favorite just wins outright):
- c5: disc0 bestEV 3.20 > hold 3.14 (EXIT-able) → cost=1 bestEV 4.89 < hold 7.14 (hold wins).
- c10: disc0 exit-beats-hold True → cost=1 False.
So even if we forced resolvable=True, the engine doesn't reactivate to EXIT at the floor cost — it flips to HOLD.

## THE FORK (for Opus — not co-signed)
Either:
- **(A)** resolvability for the engine arm must be discount/basis-sensitive (recompute the credible band at the discounted cost) — this **breaks the invariance claim** and re-couples the epistemic gate to Part-2 price; OR
- **(B)** the "cheap cells are the dormant profit engine" doctrine is **falsified by this kernel** — the cheap diffuse cells are lottery cells we correctly park forever, and the real engine must come from somewhere else (entry discounts changing *which* cells we hold, not reviving parked ones).

The HAMMER and the engine-doctrine are in direct tension: the gate that keeps the c5/c6 jackpot-lottery out is the same gate keeping the cheap engine out, because at the T-20 floor **the engine and the lottery are the same diffuse cells.** They do not separate under any cost discount.

## Status
- Bug A fixed, HAMMER passes, structure otherwise intact.
- #2 (engine reactivation) NOT lockable as written — surfaced to Opus as a structural contradiction with the invariance claim. Awaiting adjudication of fork (A) vs (B) before locking and rebuilding the ATP_MAIN surface.
