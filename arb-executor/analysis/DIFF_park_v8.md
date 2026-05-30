# DIFF v8 — PARK via bootstrap stability: argmax FALSIFIED, regime-aware fire/band WORKS

Branch blend/agent-derivation. Probes: `blend_park_v8.py`, `run_v8_fast.py`, `stab_xlo.py`, `stab_combined.py`.

## Opus's null CRITERION accepted; his proposed TARGET (argmax stability) FALSIFIED
Criterion (correct, adopted): null must destroy the fired statistic's SPECIFICITY while
preserving base rate/spread/N/cost. Within-cell bootstrap does that. Candidates 1 (move-shuffle)
and settlement-perm rejected — both preserve P(m>=X). Agreed.

BUT his proposed stability target = **best-X (argmax) within +-2c** FAILS his own kill-test:
```
alpha=0.75 argmax-stability:  EXIT=13  PARK=77
  c92 PARKS at EVERY alpha (stab 0.63)   <-- Opus: "if c92 parks, null still wrong"
  entire cheap engine c5-29 'unstable' (stab 0.16-0.55) despite npos 60-87
```
ROOT CAUSE: argmax of a near-flat (cheap) or needle (favorite) curve is intrinsically unstable
even when the cell has real resolvable edge. **argmax is the noisy lottery we've been fighting all
session** — Opus reintroduced it as the discriminator. Also his "favorites stable by construction"
assumption is wrong: expensive favorites are stable in FIRE-POINT but have almost no positive
tapes (c92 npos=2, c93 npos=1) — they're THIN, not high-conviction-broad.

## THE FIX: stability of the FIRED quantity, regime-aware
The readout fires xlo, not argmax. Test stability of what we fire:
- narrow/favorite cells -> fire-point (xlo +-3c) stable
- wide/cheap cells -> BAND-overlap (Jaccard>=0.5) stable  (fire-point wobbles, band doesn't)
RESOLVABLE = fire-point OR band stable. Results (alpha=0.75):
```
 c    resolv  s_xlo  s_band  npos   verdict
 c5   0.81    0.78   0.40    72     EXIT (engine, band-stable)
 c7   0.81    0.17   0.79    87     EXIT (band-stable though xlo wobbles)
 c9   0.81    0.38   0.67    85     EXIT
 c85  1.00    1.00   0.74     9     EXIT (favorite, fire-point rock-solid)
 c91  0.99    0.99   0.99     3     EXIT
 c92  0.59    0.59   0.59     2     PARK  <- correct: THIN (npos=2), not wrongly-parked
```
- F1: favorites c85-91 now correctly EXIT (argmax parked them). c92 parks on npos AND low resolv
  — the honest answer to the kill-test: c92 is thin, not high-conviction. Null is NOT wrong here.
- F2 (the hammer): **continuity FLAT at 0 jumps for all alpha>=0.70** — non-gameable CONFIRMED.

## The honest status of the parameter (this is the real finding)
alpha-sweep nEXIT: 0.60->59, 0.70->42, 0.75->34, 0.80->24, 0.85->18, 0.90->11.
alpha does NOT move continuity (flat 0) but DOES smoothly move COVERAGE. So Opus was right that
alpha isn't a continuity knob, but it IS a coverage/risk-appetite dial — exactly the labeled
operator parameter he argued for. The parameter didn't vanish; it got correctly RELABELED as risk
appetite. That's the lockable outcome: no hidden floor, one honest dial (Druid sets alpha).

## Open for Opus (attack)
1. Is "fire-point OR band stable" the right resolvability union, or does the OR over-admit (a cell
   resolvable on band but firing a wobbly xlo still fires a noisy number)? Maybe: band-stable cells
   must fire band-LOW-EDGE-of-the-STABLE-band, not the per-resample xlo.
2. alpha as coverage dial: at the T-20 floor, what coverage is doctrinally right? If the engine is
   off until Part 2, low coverage (high alpha, ~11-18 cells) may be correct NOW and expand as
   discounts land. Does alpha then become a FUNCTION of entry basis, not a constant?
3. F3 price-invariance still unrun (stability on moves is basis-invariant by construction; needs
   the discount-simulation to confirm PARK->EXIT in cost order, no EXIT->PARK).
