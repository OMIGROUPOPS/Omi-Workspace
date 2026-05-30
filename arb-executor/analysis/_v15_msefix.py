"""v15 fix test: add an mse (margin-in-SE significance) floor to the joint gate, replacing the
occupancy-blind point-estimate cushion check. A peak fires only if its breakeven margin is
statistically real at its OWN cluster mass: mse = (hit-be)/se >= MSE_FLOOR, where se uses n=occ*npos.
This rejects tight cheap crumbs (few draws -> wide se -> small mse) and selects the lowest peak whose
margin is significant. Sweep MSE_FLOOR to find the value that: kills X7 crumbs, keeps c13->X11,
keeps c5/c6 lowest-real-mode, parks c44, preserves ballast."""
import numpy as np
from blend_park_v8 import pooled_tapes, score_and_bestx
from park_v14_locked import fired_breakeven, FLOOR, WIN, M_CUSHION, NPOS_MIN
from _v15_peak_readout import get_draws, peaks_lowtohigh

def v15_state_msefix(c, draws, npos, MSE_FLOOR, smooth=2):
    if npos<NPOS_MIN: return ('PARK-thin',None,None)
    for ctr,mask in peaks_lowtohigh(draws,smooth):
        occ=mask.mean(); localcond=(np.abs(draws[mask]-ctr)<=WIN).mean()
        if localcond<FLOOR: continue
        hit,be,EVf,hold=fired_breakeven(c,ctr,0)
        n=max(1.0,occ*npos); se=(hit*(1-hit)/n)**0.5 if 0<hit<1 else 1e-9; mse=(hit-be)/se
        if EVf<=0: continue
        if EVf<=hold: continue
        if mse < MSE_FLOOR: continue          # NEW: significance floor replaces point cushion
        return ('EXIT',ctr,round(mse,2))
    return ('PARK',None,None)

CACHE={}
gauntlet=[5,6,11,12,13,14,15,16,29,33,36,44,84,86,87,88,91]
for c in gauntlet:
    CACHE[c]=get_draws(c,300)

for MF in [1.0,1.3,1.5,2.0]:
    print(f"\n--- MSE_FLOOR={MF} ---")
    for c in gauntlet:
        d,npos=CACHE[c]
        if d is None: print(f"  c{c}: no draws"); continue
        st=v15_state_msefix(c,d,npos,MF,2)
        print(f"  c{c}: {st[0]}/X{st[1]}/{st[2]}SE")
