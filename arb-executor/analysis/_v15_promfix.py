"""v15 fix v2 — the RIGHT fix: do not let the readout treat a cheap shoulder-bump as a peak.
Two complementary guards, both occupancy-on-the-PEAK (never margin-on-the-cluster, which kills ballast):

  (A) MIN_OCC: a peak's cluster must hold >= MIN_OCC of total draws to qualify as a fireable mode.
  (B) PROMINENCE: a peak must be a real local max with prominence over the adjacent valley
      (height >= PROM_FRAC * higher-neighbor-peak) — rejects rising-shoulder phantoms.

We test (A) alone first (simplest, doctrine-safe). Scan lowest->fire keeps Opus's readout intact.
Ballast check: c91 fires from clmass=299 (occ=1.0), c36 from clmass=149 (occ=0.50) -> both survive any
sane MIN_OCC. c11 X7 crumb clmass=13 (occ=0.04) -> dies. Sweep MIN_OCC."""
import numpy as np
from blend_park_v8 import pooled_tapes, score_and_bestx
from park_v14_locked import fired_breakeven, FLOOR, WIN, M_CUSHION, NPOS_MIN
from _v15_peak_readout import get_draws, peaks_lowtohigh

def v15_state_occfix(c, draws, npos, MIN_OCC, smooth=2):
    if npos<NPOS_MIN: return ('PARK-thin',None,None)
    for ctr,mask in peaks_lowtohigh(draws,smooth):
        occ=mask.mean()
        if occ<MIN_OCC: continue                          # NEW: peak must own real mass
        localcond=(np.abs(draws[mask]-ctr)<=WIN).mean()
        if localcond<FLOOR: continue
        hit,be,EVf,hold=fired_breakeven(c,ctr,0)
        n=max(1.0,occ*npos); se=(hit*(1-hit)/n)**0.5 if 0<hit<1 else 1e-9; mse=(hit-be)/se
        if EVf<=0: continue
        if EVf<=hold: continue
        if hit < be+M_CUSHION*(1-occ*localcond): continue # v14 cushion (ballast-safe, unchanged)
        return ('EXIT',ctr,round(mse,2))
    return ('PARK',None,None)

CACHE={}
gauntlet=[5,6,11,12,13,14,15,16,29,33,36,44,84,86,87,88,91]
for c in gauntlet: CACHE[c]=get_draws(c,300)

for MO in [0.08,0.10,0.12,0.15,0.20]:
    print(f"\n--- MIN_OCC={MO} ---")
    for c in gauntlet:
        d,npos=CACHE[c]
        if d is None: print(f"  c{c}: no draws"); continue
        st=v15_state_occfix(c,d,npos,MO,2)
        print(f"  c{c}: {st[0]}/X{st[1]}/{st[2]}SE")
