# Diff: continuous always-on kernel (Opus 4.8 method) — first numeric run

Script: `analysis/blend_continuous.py`. ATP_MAIN, own tape only.
Constants: k=0.203 (geometry), h=0.308 (similarity), NTARGET=50, m0=9, kp=2.
Spread = robust 0.5*(MAD+IQR/1.349), floored 0.75 (MAD alone collapses to 0 at favorites).
Bandwidth b(c)=clip(k*spread*N^-0.2, 0.55, 2.2).

## CONVERGES with Opus (3 of the method's pillars hold)

**DIFF 1 — bandwidth tracks move-shape dispersion, NOT count. CONFIRMED.**
```
favorites 89-93c: spread 0.8  -> b=0.55 (sharp, self-convicted)
cheap 7/9/13c:    spread 21-43 -> b~2.0 (wider pool)
c=5:              spread 8.9  -> b=0.83
```
Width is set by dispersion. No CV, no grid. The N* axis is dead; spread is the axis.

**Jackpots killed / real edges kept. CONFIRMED.**
```
5c -> +8  (was +65 lottery)      9c -> +36 region (was +90)
12c-> +20 hit54%  (REAL edge kept)
favorites bank small: 89c->+5 hit96%, 90c->+2 hit100%
```

**DIFF 3 — 37/38 soft down-weight beats blind pool. CONFIRMED.**
```
sim(37,38)=0.50 ; blended sum +$19.50  vs  blind-pool +$9.80  (truth +$39.90)
```
Continuous down-weighting recovers edge toward truth without a hard gate.

## DIVERGES — three problems to resolve before locking

**P1 — median-cell kernel is asymmetric and too tight.**
```
c=49 kernel (norm to own): -2:0.074  -1:0.256  0:1.0  +1:0.119  +2:0.029
```
The KS-similarity factor makes it lopsided (-1=0.256 vs +1=0.119), and +-1 is far
below Opus's 0.6 target. Geometry was calibrated alone; the sim factor then crushed
and skewed it. => k and h must be calibrated JOINTLY on the realized weight surface,
not independently.

**P2 — effN collapsed to ~1-7 (favorites effN=1.0).**
Sharp bandwidth x sim multiplier starves the pool. effN=1 at a favorite means the
config stands on essentially its own tape — defeats the "conviction from weighted
depth" purpose. The bandwidth floor (0.55) is too tight, or NTARGET^-0.2 over-damps.
=> effN target needs an explicit floor (e.g. favorites should still pool +-1 enough
to reach effN ~ own-N-ish), OR the sim sharpness h is too aggressive.

**P3 — CONTINUITY FAILS: 27 of 83 adjacent X* jumps > 8c.**
e.g. 14c->+10 then 20c->+50. Opus's continuity/conviction test does NOT pass yet.
The conviction-weighted score EV*paid*supp still flips between local optima cent-to-
cent. Either the score has multiple comparable peaks (needs a smoothness prior across
cents) or supp/paid exponents (m0, kp) are mis-set so the argmax is knife-edge.

## Questions back to Opus
1. Joint calibration of (k,h): calibrate so the REALIZED W-surface (geometry x sim)
   gives median +-1 ~0.6 / +-2 ~0.15 and stays symmetric. How to keep sim from
   skewing the geometry?
2. effN floor: should favorites pool enough +-1 mass to lift effN off 1.0, or is low
   effN at favorites actually correct (they ARE self-convicted)? If correct, effN is
   not the universal conviction axis — spread is.
3. Continuity: do we need an explicit cross-cent smoothness prior on X*(c), or should
   the score itself be smooth enough that argmax is stable? The 27 jumps say it isn't.
