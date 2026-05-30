# Diff v2: centroid + SE-supp + joint (k,h) — two locked, one still open

Script: `analysis/blend_continuous.py` (updated). Joint fit: k=0.215, h=2.006.

## LOCKED

**P1 — joint (k,h) calibration + asymmetry fix. DONE.**
```
realized median  +-1=0.600 (target 0.60)   +-2=0.150 (target 0.15)
c=49 kernel: -2:0.175  -1:0.625  0:1.0  +1:0.625  +2:0.175   asym=0.0%
```
Distance-tapered KS `exp(-(KS*(1+|d|/r0))^2/2h^2)` + magnitude symmetrization killed
the lopsidedness. DIFF C confirms width tracks spread by design:
```
c=9  spread43.0 b2.20  +-1=0.874 (wide, cheap)
c=49 spread11.1 b1.10  +-1=0.625 (median)
c=90 spread 0.8 b0.55  +-1=0.158 (sharp, favorite)
```

**P2 — SE-based supp. DONE, behaves exactly as predicted.**
```
favorites c=89/90/92: SE~0.5  max-supp=1.00  -> convicted on own tape
cheap     c=5:  SE=6.2  max-supp=0.13   c=9: SE=16.1 max-supp=0.05
```
Jackpots structurally killed: 5c cannot reach +65, 9c cannot reach +90 (supp starves
the tail). Favorites clear support on their own tight tape. effN is the cheap-cell
axis, spread the favorite axis, SE=spread/sqrt(effN) unifies them. Confirmed.

## STILL OPEN

**P3 — centroid did NOT fix continuity. 23 of 85 jumps >8c (was 27).**
Root cause found: on flat bimodal cheap-cell surfaces the tau=0.7 credible region spans
almost the ENTIRE offset range, so the centroid just tracks the region's geometric
middle, which swings as the far (tail) mode drifts:
```
c=5: X*=+22.5 region[6,40] width34
c=6: X*=+29.5 region[6,40] width34
c=7: X*=+42.2 region[13,65] width52   <- centroid of a width-52 band is not a pick
c=9: X*=+30.4 region[7,60] width53
```
Favorites and real-edge mids are fine (width 0-14, smooth). The problem is isolated to
the cheap heavy-tailed cells where the score surface is genuinely flat-topped across a
huge X range. A width-52 credible region is the method telling us the cell does not have
a localized best-X at all under the current score.

### The question this raises for Opus
The centroid assumed bimodal-but-localized (two peaks, centroid between them moves
smoothly). Reality on cheap cells is flat-topped-across-50c, not two clean peaks. Two
candidate fixes — which is correct?

1. **Tighten the credible region adaptively** so it can't exceed a sane width: e.g.
   tau scales up until region width <= w_max (say 12c), OR use tau on a *concave-
   transformed* score so the flat top sharpens. This forces a localized centroid.

2. **The flat top is real signal — cheap cells SHOULD report a band, not a point.**
   Then continuity should be measured on the band CENTER OF MASS weighted by score^p
   (p>1) to concentrate, and we accept that cheap cells carry a wide conviction
   interval [xlo,xhi] as the honest config (you exit anywhere in the band). The >8c
   "jumps" may then be an artifact of collapsing a band to a single number for the
   jump metric — measure overlap of consecutive bands instead.

My lean: (2) is more honest to the data (the surface really is flat there), but (1) is
what the executor needs (it wants one X to fire on). Possibly both: report the band as
the config, fire at the score^p-concentrated center. Need your call on p and whether
the jump metric should be band-overlap, not center-delta.

## Diff results summary vs Opus's three predictions
- centroid cuts jumps 30->single digits: **FAILED (27->23)** — flat-top, not bimodal-localized.
- SE-supp leaves favorites convicted + kills 5->65: **CONFIRMED.**
- joint (k,h) median symmetric 0.6/0.15, favorites sharper: **CONFIRMED.**
