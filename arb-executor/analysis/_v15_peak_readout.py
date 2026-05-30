"""v15 candidate — Opus's mode-count-free readout:
fire the LOWEST local density peak of the bootstrap best-X distribution that JOINTLY clears
  (1) local cond >= FLOOR  (trustworthy center), AND
  (2) EV>0, EV>hold, hit >= breakeven + cushion  (economically real at its own occupancy).
No GAP. No dip percentile. No fixed mode count. Scan peaks low->high.

Peak-finding: smooth the integer-cent histogram with a small window, find local maxima; for each
peak define its cluster as the contiguous valley-to-valley region; compute occ (cluster mass),
center (cluster median), local cond (pin-rate to center within +-WIN among cluster draws).
"""
import numpy as np, collections
from blend_park_v8 import pooled_tapes, score_and_bestx
from blend_continuous import CENTS
from park_v14_locked import fired_breakeven, FLOOR, WIN, M_CUSHION, NPOS_MIN
rng=np.random.default_rng(13)

def get_draws(c, NBOOT):
    pool=pooled_tapes(c)
    if not pool: return None,0
    Xs,s,EV,bx=score_and_bestx(c,c,pool)
    if Xs is None or s.max()<=0: return None,0
    npos=int((EV>0).sum()); d=[]
    for _ in range(NBOOT):
        rp=[(m[idx],sv[idx],w) for (m,sv,w) in pool for idx in [rng.integers(0,len(m),len(m))]]
        X2,s2,E2,_=score_and_bestx(c,c,rp)
        if X2 is None or s2.max()<=0: continue
        d.append(int(X2[int(np.argmax(s2))]))
    return (np.array(d),npos) if d else (None,npos)

def peaks_lowtohigh(draws, smooth=2):
    """Find local-maxima peaks of the cent histogram (smoothed), return list of (center, cluster_mask_fn)
    valley-segmented, ordered by center ascending."""
    lo,hi=draws.min(),draws.max()
    grid=np.arange(lo,hi+1)
    hist=np.array([(draws==x).sum() for x in grid], float)
    if smooth>0:
        k=np.ones(2*smooth+1)/(2*smooth+1)
        hist=np.convolve(hist,k,mode='same')
    # local maxima
    peakidx=[i for i in range(len(grid)) if hist[i]>0 and
             (i==0 or hist[i]>=hist[i-1]) and (i==len(grid)-1 or hist[i]>=hist[i+1])]
    # merge adjacent plateau peaks
    centers=[int(grid[i]) for i in peakidx]
    # valleys: split at the local minima between consecutive peaks
    bounds=[lo]
    for a,b in zip(centers,centers[1:]):
        seg=grid>=a; seg&=grid<=b
        idxs=np.where(seg)[0]
        vmin=idxs[np.argmin(hist[idxs])]
        bounds.append(int(grid[vmin]))
    bounds.append(hi+1)
    clusters=[]
    for j,ctr in enumerate(centers):
        a,b=bounds[j],bounds[j+1]
        mask=(draws>=a)&(draws<b) if j<len(centers)-1 else (draws>=a)&(draws<=hi)
        if mask.sum()==0: continue
        clusters.append((int(np.median(draws[mask])), mask))
    # dedupe by center
    seen=set(); out=[]
    for ctr,mask in sorted(clusters,key=lambda z:z[0]):
        if ctr in seen: continue
        seen.add(ctr); out.append((ctr,mask))
    return out

def v15_state(c, draws, npos, smooth=2):
    if npos<NPOS_MIN: return ('PARK-thin',None,None)
    for ctr,mask in peaks_lowtohigh(draws,smooth):
        occ=mask.mean(); localcond=(np.abs(draws[mask]-ctr)<=WIN).mean()
        if localcond<FLOOR: continue                      # not trustworthy; try next peak up
        hit,be,EVf,hold=fired_breakeven(c,ctr,0)
        n=max(1.0,occ*npos); se=(hit*(1-hit)/n)**0.5 if 0<hit<1 else 1e-9; mse=(hit-be)/se
        if EVf<=0: continue                               # negative-EV peak, keep scanning
        if EVf<=hold: continue                            # doesn't beat hold; keep scanning (HOLD-ish)
        if hit < be+M_CUSHION*(1-occ*localcond): continue # within-noise of breakeven; keep scanning
        return ('EXIT',ctr,round(mse,2))                  # lowest qualifying peak FIRES
    return ('PARK',None,None)  # no qualifying peak (could be HOLD/PARK-engine/noise; lumped here)

# GAUNTLET + c13
CACHE={}
gauntlet=[5,6,11,12,13,14,15,16,29,33,36,44,84,86,87,88,91]
print("v15 PEAK readout (smooth=2) on the gauntlet:")
for c in gauntlet:
    d,npos=get_draws(c,300); CACHE[c]=(d,npos)
    if d is None: print(f"  c{c}: no draws"); continue
    st=v15_state(c,d,npos,2)
    print(f"  c{c}: {st[0]}/X{st[1]}/{st[2]}SE")
