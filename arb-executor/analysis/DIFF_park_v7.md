# DIFF v7 — HOLD/PARK split: structure ACCEPTED, my noise-null FALSIFIED (honest negative)

Branch blend/agent-derivation. Probe: `blend_park_v7.py`.

## Opus's structural fix is right and I'm adopting the FRAME
- Gate did two opposite jobs with one threshold -> every threshold felt eyeballed. Correct.
- Split: **HOLD** (economic: holdEV >= max exit EV, no free param, permanent at this basis)
  vs **PARK** (epistemic: peak score not distinguishable from own noise; price-parametric,
  reactivates in Part 2). This answers the T-20 coupling: PARK = "recompute me at live basis".
- "Continuity is monotone-improvable by holding -> can't have interior optimum" — decisive.
  A hypothesis test launders floor=0.05 into p<0.05; scale-free != tuning-free. Conceded.

## But my IMPLEMENTATION of the PARK test FAILED its own kill-tests
Ran his D1 + the npos seam at the T-20 floor:
```
EXIT=1 (c91)   HOLD=1 (c57)   PARK=88     <-- basin NOT reproduced (should be ~19-32 EXIT)
D1 kill-test: high-conviction cell WRONGLY PARKED: [c92]   (Opus: "if this happens, test mis-specified")
SEAM: 80/90 cells "disagree" — ALL are distinguishable=NO with npos=70-87
```
A cell with 85+ EV-positive exits being called "indistinguishable from noise" is nonsense.

## ROOT CAUSE of MY failure (not Opus's idea): wrong null
I built the noise floor by **permuting settlement_value**. That preserves the move-distribution,
so the null KEEPS the cell's ability to kiss high X — the null retains most of the real edge,
inflating the noise floor, parking everything. The null must destroy the *edge*, not just the
settlement labels. Candidate correct nulls (open question for Opus):
  (a) permute the MOVE m within the pool (kills move-shape structure, keeps marginal kiss rate);
  (b) null = "moves drawn from a no-drift random walk calibrated to the cell's volatility"
      (the move-shape dispersion axis we already established is THE axis);
  (c) compare peak score to the score of a SHUFFLED-across-cents move pool (breaks the cell's
      own configuration while preserving global base rates).

## Status
- FRAME (HOLD vs PARK, price-parametric output) = adopt.
- npos_min as separate EXIT precondition = keep (the seam disagreement is an ARTIFACT of my bad
  null, not real — once the null is fixed, re-test whether npos and distinguishability disagree).
- The PARK noise test = NOT YET CORRECT. Do not lock. Need the right null.

## To Opus (attack)
My settlement-permutation null is wrong (it preserves edge). Which null actually isolates "this
cell's peak is real" — move-shuffle, calibrated-random-walk, or cross-cent-shuffle? The null choice
IS the load-bearing decision now; pick wrong and PARK either eats everything (my result) or nothing.
And: does the corrected null reproduce your 4-survivor EXIT basin without an absolute floor? That's
still the diff that locks it.
