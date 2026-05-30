"""Diagnose why v15 peak-readout fires X7 for c11/c12/c13 instead of true modes.
Dump, for each cell: the smoothed-histogram peaks, each peak's (center, occ, localcond,
hit, be, EVf, hold, mse) and WHICH gate each peak passes/fails. This tells us whether the
X7 fire is a spurious cheap crumb passing the joint gate, or a real segmentation error."""
import numpy as np
from blend_park_v8 import pooled_tapes, score_and_bestx
from park_v14_locked import fired_breakeven, FLOOR, WIN, M_CUSHION, NPOS_MIN
from _v15_peak_readout import get_draws, peaks_lowtohigh

CELLS=[11,12,13,5,6,91]
for c in CELLS:
    d,npos=get_draws(c,300)
    if d is None:
        print(f"\n=== c{c}: no draws ==="); continue
    print(f"\n=== c{c}  npos={npos}  Ndraws={len(d)}  draw-range[{d.min()},{d.max()}] ===")
    # raw histogram of where draws land (top cents by mass)
    vals,cnts=np.unique(d,return_counts=True)
    order=np.argsort(-cnts)[:8]
    print("  top draw cents (X:count):", ", ".join(f"{int(vals[i])}:{int(cnts[i])}" for i in order))
    peaks=peaks_lowtohigh(d,2)
    print(f"  peaks found (low->high): {[p[0] for p in peaks]}")
    for ctr,mask in peaks:
        occ=mask.mean(); localcond=(np.abs(d[mask]-ctr)<=WIN).mean()
        hit,be,EVf,hold=fired_breakeven(c,ctr,0)
        n=max(1.0,occ*npos); se=(hit*(1-hit)/n)**0.5 if 0<hit<1 else 1e-9; mse=(hit-be)/se
        clmass=int(mask.sum())
        # gate trace
        g_cond = localcond>=FLOOR
        g_ev   = EVf>0
        g_hold = EVf>hold
        cush   = be+M_CUSHION*(1-occ*localcond)
        g_cush = hit >= cush
        fires  = g_cond and g_ev and g_hold and g_cush
        print(f"   peak X={ctr:>3} clmass={clmass:>3} occ={occ:.2f} lcond={localcond:.2f} "
              f"hit={hit:.2f} be={be:.2f} EVf={EVf:+.3f} hold={hold:+.3f} mse={mse:+.2f} "
              f"cush_thr={cush:.2f} | cond:{int(g_cond)} ev:{int(g_ev)} hold:{int(g_hold)} cush:{int(g_cush)} "
              f"{'<== FIRES' if fires else ''}")
