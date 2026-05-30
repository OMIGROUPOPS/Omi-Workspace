"""Confirm the mse-floor kills ballast (c91/c86/c87) via the flat-SE-margin mechanism, and inspect
c88's X2 fire. Dump the firing-peak details under v14-style logic vs the mse gate."""
import numpy as np
from blend_park_v8 import pooled_tapes, score_and_bestx
from park_v14_locked import fired_breakeven, FLOOR, WIN, M_CUSHION, NPOS_MIN
from _v15_peak_readout import get_draws, peaks_lowtohigh

for c in [91,86,87,88,36,84]:
    d,npos=get_draws(c,300)
    if d is None: print(f"c{c}: no draws"); continue
    print(f"\n=== c{c} npos={npos} range[{d.min()},{d.max()}] ===")
    for ctr,mask in peaks_lowtohigh(d,2):
        occ=mask.mean(); lc=(np.abs(d[mask]-ctr)<=WIN).mean()
        hit,be,EVf,hold=fired_breakeven(c,ctr,0)
        n=max(1.0,occ*npos); se=(hit*(1-hit)/n)**0.5 if 0<hit<1 else 1e-9; mse=(hit-be)/se
        cush=be+M_CUSHION*(1-occ*lc)
        v14pass = (lc>=FLOOR) and (EVf>0) and (EVf>hold) and (hit>=cush)
        print(f"  X={ctr:>3} clmass={int(mask.sum()):>3} occ={occ:.2f} lc={lc:.2f} hit={hit:.3f} "
              f"be={be:.3f} se={se:.4f} mse={mse:+.2f} EVf={EVf:+.2f} hold={hold:+.2f} "
              f"v14fire={int(v14pass)}")
