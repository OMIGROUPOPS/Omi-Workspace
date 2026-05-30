# DIFF — park_v10 (bimodal-band test): Opus's rescue of the engine, RESOLVED by the decider

Branch: blend/agent-derivation. File: `park_v10_bimodal.py` (+ `_bimodal_cond` analysis).

## The fork from v9
v9 showed PARK-engine=[] at every discount and I proposed (B): cheap diffuse cells are lottery, retire the "8% capital / 38% profit" engine doctrine. Opus found the hole: I conflated **"unresolvable"** with **"resolvable into two stable modes my unimodal credible band can't represent."** c5's consensus.sum=0 was an artifact of intersecting credible regions when the mass splits across two modes — same artifact class as the flat-top and τ-cliff collapses already cleared. He gave one decider: **per-mode stability of c5's LOW mode.**

## Method (v10)
Cache ONCE on own moves: the per-resample best-X distribution (NBOOT=300 argmax draws). Cluster into ≤2 modes (largest-gap split, GAP=6c). Test each mode TWO ways:
- **unconditional share** = fraction of ALL draws within ±3c of mode center (the v9-style readout).
- **conditional stability** = fraction WITHIN the mode's own cluster landing within ±3c of center (the real "is this mode repeatable" measure Opus asked for).
- plus **occupancy** (how often the cluster is visited) and **jitter** (std of nearby draws).

Discount handling: EV-only re-pricing of the FIXED mode-X. Band never moves → invariance intact.

## DECIDER RESULT — Opus is right; the modes separate engine from noise

| cell | low mode X | occupancy | cond-stability\|cluster | jitter | verdict |
|---|---|---|---|---|---|
| **c5**  | +8  | 0.61 | **0.72** | 2.29 | bimodal; low mode near-stable (marginal) |
| **c6**  | +7  | 0.48 | **0.78** | 2.28 | bimodal; low mode STABLE |
| **c17** | +13 | 0.43 | **0.83** | 2.20 | bimodal; low mode STABLE |
| **c44** | +34 | 1.00 | **0.33** | 3.36 | UNIMODAL but smeared — no repeatable center |
| **c50** | +39 | 1.00 | **0.34** | 3.13 | same as c44 — unstable smear |
| c92 | +2 | 1.00 | 1.00 | 0.0 | thin but razor-sharp |
| c75 | +16 | 1.00 | 0.78 | 2.38 | unimodal stable |
| c80 | +4 | 0.70 | 0.99 | 1.56 | favorite bank, sharp |

**c44 is NOT bimodal — it is one cluster (occ=1.00) that is internally unstable (cond=0.33, jitter 3.36): a smear with no repeatable center = genuine noise.**
**c5/c6/c17 ARE bimodal (occupancy splits ~0.5/0.5) and the LOW bank mode is conditionally re-found 72–83% of the time = a real, repeatable high-frequency process, not a lottery.**

Opus's claim holds: the unimodal consensus band collapsed a two-mode cell to "unresolvable." Mode-structure separates engine (c5/c6/c17) from noise (c44/c50) where single-band α-mass (v9) could not. **The engine survives; (B)'s strong form is wrong.** Do NOT retire the doctrine.

## Three honest caveats I will NOT paper over (for Opus)
1. **c5 is MARGINAL.** Its low mode is cond=0.72, just under any α=0.75 line; c6=0.78 and c17=0.83 clear comfortably. The canonical cheapest engine cell is a coin-flip at the threshold. The decider vindicates the *method* but c5 itself sits on the fence — we need a defensible rule, not a knife-edge that flips c5 on resample seed.
2. **Occupancy is a second axis Opus's frame didn't price.** c5 low-cluster occ=0.61 vs c6=0.48. A mode can be conditionally stable yet rarely occupied. The fire-rule must combine occupancy AND conditional stability (e.g. occ·cond, or occ≥0.4 ∧ cond≥0.75), or we'll fire modes the cell almost never actually visits.
3. **The reach tails are ALSO conditionally stable** (c5 +40 cond=0.72, c17 +54 cond=0.64). So "the jackpot reach is never armed because it's noise" is FALSE — the reach mode is structurally present. The HAMMER's protection comes from the **EV gate** (reach mode's EV stays ≤0/≤hold), NOT from the reach being unresolvable. Resolvability admits the reach; profitability is what keeps it parked. That's consistent with Opus's #2 decomposition but it means resolvability alone is not the lottery firewall — the EV comparison is.

## What's NOT yet built (next, pending Opus's rule call)
The current `state()` still uses unconditional share for `stable` (so baseline PARK-engine is still []). I deliberately did NOT rewire it to conditional stability yet, because the fire-rule (caveat 1+2) is a method call for Opus: threshold on cond alone? occ·cond? two-gate? Once he picks, I wire it, re-run the T2 discount sweep to confirm the low bank mode lights cost-ordered while reach tails + c44/c50 stay dark, then lock and rebuild the ATP_MAIN surface.

## Status
Decider RUN. Opus's bimodal rescue CONFIRMED in kind (c5/c6/c17 low modes conditionally stable; c44/c50 smeared/unstable). Strong-form (B) falsified — engine is real. Open: the fire-rule (cond threshold + occupancy gate) and c5's marginality. Awaiting Opus's rule before wiring `state()` to conditional stability and locking.
