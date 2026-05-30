"""Full v15 validation before lock:
 (1) FULL CENSUS over all cents (compare to v14: EXIT26/HOLD14/PARKeng24/PARKthin10/PARKnoise16).
 (2) STABILITY — smooth-window sweep {1,2,3}: fired-mode SET-IDENTITY must be stable.
 (3) STABILITY — bootstrap-B sweep {300,1000,2000}: Opus's demand. Real modes must persist; if X7-type
     phantoms only appear at small B and vanish at B>=2000, that's the noise-spike warning. With the
     MIN_OCC prominence guard they should already be gone at B=300 AND stay gone at B=2000.
MIN_OCC=0.10 (center of the flat plateau [0.08,0.20]). v14 cushion retained (ballast-safe).
"""
import numpy as np, json, collections
from blend_park_v8 import pooled_tapes, score_and_bestx
from blend_continuous import CENTS
from park_v14_locked import fired_breakeven, FLOOR, WIN, M_CUSHION, NPOS_MIN

MIN_OCC=0.10

def get_draws(c, NBOOT, seed=13):
    rng=np.random.default_rng(seed)
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
    lo,hi=draws.min(),draws.max(); grid=np.arange(lo,hi+1)
    hist=np.array([(draws==x).sum() for x in grid], float)
    if smooth>0:
        k=np.ones(2*smooth+1)/(2*smooth+1); hist=np.convolve(hist,k,mode='same')
    peakidx=[i for i in range(len(grid)) if hist[i]>0 and
             (i==0 or hist[i]>=hist[i-1]) and (i==len(grid)-1 or hist[i]>=hist[i+1])]
    centers=[int(grid[i]) for i in peakidx]; bounds=[lo]
    for a,b in zip(centers,centers[1:]):
        seg=(grid>=a)&(grid<=b); idxs=np.where(seg)[0]
        bounds.append(int(grid[idxs[np.argmin(hist[idxs])]]))
    bounds.append(hi+1); clusters=[]
    for j,ctr in enumerate(centers):
        a,b=bounds[j],bounds[j+1]
        mask=(draws>=a)&(draws<b) if j<len(centers)-1 else (draws>=a)&(draws<=hi)
        if mask.sum()==0: continue
        clusters.append((int(np.median(draws[mask])), mask))
    seen=set(); out=[]
    for ctr,mask in sorted(clusters,key=lambda z:z[0]):
        if ctr in seen: continue
        seen.add(ctr); out.append((ctr,mask))
    return out

def v15_state(c, draws, npos, smooth=2):
    """Scan peaks low->high. A peak that fails any gate is SKIPPED (continue), never an early park
    (matches the validated gauntlet helper). The lowest FULLY-qualifying peak fires EXIT. If none fire,
    assign a terminal verdict from the strongest reason observed among occ-qualifying peaks, in v14
    priority: any peak reached cushion/hold stage -> HOLD/PARK-engine; only EV<=0 seen -> PARK-engine;
    no occ-qualifying cond-passing peak at all -> PARK-noise; npos thin -> PARK-thin."""
    if draws is None or npos<NPOS_MIN: return ('PARK-thin',None)
    saw_cond_peak=False; saw_hold=False; saw_cushfail=False; saw_pos_ev=False
    for ctr,mask in peaks_lowtohigh(draws,smooth):
        occ=mask.mean()
        if occ<MIN_OCC: continue
        localcond=(np.abs(draws[mask]-ctr)<=WIN).mean()
        if localcond<FLOOR: continue
        saw_cond_peak=True
        hit,be,EVf,hold=fired_breakeven(c,ctr,0)
        if EVf<=0: continue
        saw_pos_ev=True
        if EVf<=hold: saw_hold=True; continue
        if hit < be+M_CUSHION*(1-occ*localcond): saw_cushfail=True; continue
        return ('EXIT',ctr)                       # lowest fully-qualifying peak fires
    if not saw_cond_peak: return ('PARK-noise',None)
    if saw_hold:          return ('HOLD',None)
    if saw_cushfail:      return ('PARK-engine',None)
    return ('PARK-engine',None)                   # cond-passing peaks but all EV<=0 -> engine/dormant

if __name__=="__main__":
    ALL=list(CENTS)
    # precompute draws at B=300 once
    DR={}
    for c in ALL: DR[c]=get_draws(c,300)

    # (1) CENSUS
    cen=collections.Counter()
    exits={}
    for c in ALL:
        d,npos=DR[c]; st,ctr=v15_state(c,d,npos,2)
        cen[st]+=1
        if st=='EXIT': exits[c]=ctr
    print("=== v15 CENSUS (smooth=2, MIN_OCC=0.10, B=300) ===")
    for k in ['EXIT','HOLD','PARK-engine','PARK-thin','PARK-noise']:
        print(f"  {k}: {cen[k]}")
    print(f"  EXIT cells: {sorted(exits)}")

    # (2) smooth-window set-identity
    print("\n=== STABILITY: smooth-window {1,2,3} EXIT-set identity ===")
    sets={}
    for sm in [1,2,3]:
        ex=set()
        for c in ALL:
            d,npos=DR[c]; st,ctr=v15_state(c,d,npos,sm)
            if st=='EXIT': ex.add(c)
        sets[sm]=ex; print(f"  smooth={sm}: |EXIT|={len(ex)}")
    base=sets[2]
    for sm in [1,3]:
        print(f"  smooth={sm} vs 2: added={sorted(sets[sm]-base)} dropped={sorted(base-sets[sm])}")

    import json as _j
    _j.dump({str(c):exits.get(c) for c in exits}, open('/tmp/v15_exits_b300.json','w'))
    print('CENSUS+SMOOTH DONE')
