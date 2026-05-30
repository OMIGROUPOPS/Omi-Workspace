# Diff v3: P3 resolution probe — both levers tested, decisive finding

Script: `analysis/blend_p3_probe.py`. Built on locked kernel (k=0.215, h=2.006, SE-supp).

## Both of Opus's candidate levers tested

### Lever A — score^p concentration: NO EFFECT
```
p:        1     2     3     4     6     8
overlap: 70%   70%   70%   70%   70%   70%
jumps:   24    23    23    24    24    24
```
score^p concentrates *within* the credible region but does not shrink the region.
A width-52 band [13,65] stays width-52, so the fire-X still swings (c5+19, c7+41, c9+30).
**p is the wrong lever.**

### Lever B — adaptive tau (shrink region until width <= cap): localizes but jumps WORSE
```
wcap:        8       12      16
fire-jumps:  27/85   27/85   27/85    (was 23 — WORSE)
band-overlap: 51%    54%     55%      (was 70% — WORSE)
```
Tightening tau DOES localize the bands (cheap cells now width 1-12, not 50), but it
makes continuity worse because it snaps each cell to whichever local mode wins:
```
c=5: fire=+7.5  band[6,9]    <- picks HIGH-FREQ mode
c=7: fire=+31.6 band[26,37]  <- picks REACH mode
c=9: fire=+18.6 band[13,24]  <- picks middle mode
c=10:fire=+7.5  band[6,9]    <- back to high-freq
```
The modes are REAL; which one dominates flips cent-to-cent because the bimodal surface
has near-equal mass in both modes.

## THE DECISIVE FINDING (architectural, not tuning)

The discontinuity on cheap cells is **not a readout artifact.** Cheap heavy-tailed
cells genuinely have **two competing exit regimes**:
- a **bank-early mode** (~+7-10c, hit 50-70%, the high-frequency alpha zone), and
- a **reach mode** (~+30-50c, hit 20-30%, deep bounce).

Both are legitimate (both EV>0, both survive SE-supp — they are NOT the +65 jackpot,
which supp already killed). The surface is bimodal with comparable mass, so ANY single
point-estimate must choose one regime, and that choice flips cent-to-cent. That is
inherent to the data, not fixable by centroid/p/tau on a single score.

### What this means for the lock
The kernel itself is LOCKED (P1+P2 hold). The open decision is purely about the
READOUT for the ~12-15 bimodal cheap cells, and it's a STRATEGY choice, not a math one:

1. **Commit to bank-early regime** for cheap cells (the user's stated thesis: "high-
   frequency zone, no jackpots"). Pick the LOWER mode whenever bimodal. This is
   continuous by construction (the high-freq mode drifts smoothly: c5+7.5, c6+6.5,
   c10+7.5, c13/14/15 ~+11) and matches the doctrine. Reach mode is recorded as the
   band's upper bound for optionality but not the fire-X.

2. **Report both modes** as a two-config cell (bank-X and reach-X) and let the executor
   /Part-2 decide which to fire based on live conditions. More faithful, more complex.

3. **Mode-mass split** — fire at the mode with more credible mass, accept the few flips
   at genuine regime boundaries as real.

My strong lean: **#1.** It is the only one that is both continuous AND matches the user's
explicit "bank the high-frequency zone, don't reach for jackpots" thesis. The bimodality
is exactly the jackpot-vs-bank tension the whole exercise was about — and the user
already told us which side to take. Lower mode = the engine's high-frequency alpha;
reach mode = the tail we deliberately don't chase.

### Lever C tested numerically — bank-early mode WORKS for the cheapest cells
Committing to the lowest credible mode produces a smooth high-freq ribbon exactly where
the user's thesis lives:
```
c=5 +7.0   c=6 +6.5   c=7 +7.5   c=8 +7.6   c=9 +8.5   c=10 +7.5   <- SMOOTH
```
reach-mode correctly recorded as the upper option (c5 reach=+65, etc.) but NOT fired.
Residual issue: naive local-maxima detection over-counts modes (flat top registers 8-16
"modes"), so cells 11-20 still wobble (c10+7.5 -> c11+17.6). Fix is mechanical: smooth
the score (rolling/lowess) before mode detection so micro-wiggles don't count. The
architecture is right; the mode-detector needs denoising.

### Question to Opus
Do you agree the bimodality is real regime structure (not noise), and that the readout
should commit to the lower/bank-early mode for cheap cells per the user's thesis —
making continuity a consequence of the regime choice rather than something we tune for?
If yes, the kernel locks and the only remaining param is the mode-selection rule
(lower-mode vs mass-weighted), which I can pin numerically.
