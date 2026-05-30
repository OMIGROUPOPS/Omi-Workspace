# DIFF v4 — Regime-aware readout (Opus call) tested against his own 3 falsifiers

Branch: blend/agent-derivation. Probe: `blend_p3_regime.py`. Constants k=0.215, h=2.006 (locked).
Regime thresholds wA=3, wB=12. Census over 90 cents: **A(point)=32, B(band,fire-xlo)=54, C(hold)=3.**

## What CONVERGED (lock these)
1. **Band-overlap metric is broken for narrow bands** — confirmed; flagged the smoothest (favorite) zone as 100% disjoint. Dropped.
2. **score^p does nothing** (jumps 25→23). Dropped. No `p` knob.
3. **Fire xlo, not center, for band cells** — DIFF 3 CLEAN PASS. Every cheap cell fires xlo with EV>0
   (c5:+6 EV2.98 hit73%, c9:+7 EV2.23 hit70%, c20:+37 EV4.10) while declining the band-top jackpot
   (c9 leaves +24/+60 on the table). Doctrinally correct: don't reach when reaching buys no score.
4. **Regime C = hold is a valid config, not a discontinuity** — excluding the 3 [0,0] cells (c68,82,93)
   from the continuity metric is correct.

## What did NOT pass (Opus's prediction partially REFUTED by his own test)
- **DIFF 1 (xlo near-monotone cheap zone): PARTIAL.** Much smoother than centroid (was 23 jumps) but
  NOT monotone — 5 jumps>5c remain in c5-30 (c7:+13, c11:+12 noise wobble; c19→20→21 +16→+37→+22 genuine).
- **DIFF 2 (real jumps drop to a handful at TRUE boundaries): FAIL on magnitude.** Naive 19 → regime-aware 11,
  BUT the 11 are NOT at regime boundaries — they are **within-regime flips**:
  - c65→66→67: +1→+28→+2 (all Regime A)
  - c49→50: +11→+34 (both B); c45→46: +33→+16 (both B)
  - c39→40: +7→+29 (both A)
- **Firing xlo for ALL cells (A included) made it WORSE: 11→17.** For narrow A-cells xlo≡argmax, so it can't help.

## ROOT CAUSE (the real "one bug")
The bimodality is **NOT confined to cheap cells** — c65/66/67 flip exactly as hard as c7/8.
The three-regime split relabeled the pathology, it did not remove it. The discontinuity is **upstream of the
readout shape**: it lives in the **hard τ=0.7 credible-region cliff applied to a near-flat, noisy score**.
On a flat top, a ~1% score wobble flips which mode (low bank vs high reach) clears τ, which yanks BOTH xlo
and argmax cent-to-cent. Point/band/hold is the right *taxonomy* but it is not the *fix*.

## PROPOSED RESOLUTION (for Opus to weigh)
Keep the regime taxonomy (it's honest) AND keep fire-xlo for B (it's correct). Add the missing piece:
**make mode-selection continuous instead of a hard τ-cliff.** Two candidates:
  (a) Smooth the score across cents BEFORE thresholding (rolling/lowess over c on the score surface,
      not the within-cell curve) so the τ-membership of a mode can't flip on 1% noise.
  (b) Replace hard τ with a soft credible weight (sigmoid around τ) so xlo = lowest X whose smoothed
      score weight ≥ 0.5 — drifts continuously as the low mode's relative weight rises/falls.
Prediction to test: (a) or (b) collapses the within-regime jumps (c65/66/67, c49/50) to <4 total,
all at true A↔B boundaries, with cheap-zone xlo monotone. THAT locks the readout.
