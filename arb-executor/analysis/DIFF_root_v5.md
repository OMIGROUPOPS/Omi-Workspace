# DIFF v5 — ROOT CAUSE FOUND. Continuity locked (11 → 4 within-regime jumps).

Branch: blend/agent-derivation. Probes: `blend_p3_smooth.py` (the two fixes that FAILED, kept as evidence)
and the v5 reclassification (inline). Constants k=0.215, h=2.006.

## The two "obvious" fixes both FAILED — and that was the tell
- **Soft-τ sigmoid: perfect no-op (11→11, every β).** A soft credible weight does nothing when the
  credible region is already a single point.
- **Smooth-across-cents: barely moved it (11→9 at ws=5) AND introduced new flips.** Smoothing a readout
  can't fix a curve that has only one candidate to read.

## Why: the score curve is a NEEDLE, not a flat top
Inspecting the watched flip cells directly:
- c65: **exactly 1 X with EV>0** out of 29 (needle at +1, everything else 0.00).
- c67: **exactly 1 X with EV>0** (needle at +2).
- c40: needle at +29. c39: 2 positive X near 0.
- (c49/c50 ARE genuinely bimodal with a real valley 0.78–0.85 — those are the real ones.)

The expensive favorites (cost 64–67¢, 71–73, 77, 80–82, 90–93) are so heavily priced that **almost every
exit is EV-NEGATIVE**; only a razor-thin single X squeaks positive, and *which* one flips cent-to-cent on
sub-penny EV noise. `EV·paid·supp ≈ 0.00` across the whole curve — the "modes" were floating-point
tie-breaking on a flat-ZERO surface. Both Opus's centroid and my xlo were reading noise.

## THE FIX — one layer deeper than the readout
Redefine the HOLD regime. It is NOT `max score ≤ 0`. It is **"too little EV-positive conviction to
constitute a real exit"**:
```
HOLD if  max(EV·paid·supp) ≤ SCORE_FLOOR (0.05)   OR   #{X: EV>0} < NPOS_MIN (3)
```
This is an **economic fact**, not a tuning knob: an expensive favorite where ~every exit loses money
should hold to settlement, not emit a noisy +X.

## RESULT (the lock)
- Census: **A=18, B=53, C(hold/marginal)=18.**
- **within-regime jumps>8c: 11 → 4.** All 4 survivors are real cheap/mid texture:
  c19→20→21 (+16→+37→+22, the genuine c20 reach), c45→46 (+33→+16), c49→50 (+11→+34, true bimodal).
- Every expensive-zone noise-flip (c65/67/72/77/80-82/90-93) correctly → HOLD. ZERO expensive-zone jumps.
- Cheap-zone fire-xlo unchanged (5 jumps>5c) — still smooth bank-mode ladder, c20 reach preserved.

## DOCTRINE CALL (agent, standing)
c20's +37 reach is REAL signal in a sea of bank cents — NOT hard-capped. The 4 remaining jumps are
true regime texture; forcing them flat would be approximation overriding the tape. Continuous
mode-selection is unnecessary; the needle cells were never bimodal, just marginal.

## Final readout stack (proposed LOCK)
1. width from move-spread (bandwidth) — LOCKED
2. similarity from distance-tapered KS — LOCKED
3. support from SE — LOCKED
4. **HOLD = score-floor OR npos floor** (NEW — this is the P3 fix) 
5. config: A=argmax point / B=band fire-xlo / C=hold
