"""P3 probe: score^p concentration (fire-X) + band-overlap continuity metric.
Builds on blend_continuous funcs. Sweeps p to find where cheap-cell bands localize
and the band-overlap continuity holds, without an external smoothness prior."""
import numpy as np
src=open("analysis/blend_continuous.py").read().split('if __name__')[0]
ns={}; exec(src,ns)
weights=ns['weights']; curve=ns['curve']; effN=ns['effN']; SE=ns['SE']; SPREAD=ns['SPREAD']; bandwidth=ns['bandwidth']
CENTS=ns['CENTS']
k,h=0.215,2.006

def config(c,p,kp=2.0,m0=1.2,tau=0.7):
    Xs=np.arange(1,95-c)
    if len(Xs)==0: return None
    EV,HIT,ROI=curve(c,k,h,Xs); se=SE(c,k,h)
    paid=1-(HIT/100)**kp
    supp=np.minimum(1.0,(HIT/100)/(m0*se))
    s=np.where(EV>0,EV*paid*supp,0.0)
    if s.max()<=0: return None
    # score^p concentration for the FIRE-X (centroid of s^p over credible region)
    sp=s**p
    cred=s>=tau*s.max()
    Xc=Xs[cred]; spc=sp[cred]
    firex=float(np.sum(Xc*spc)/np.sum(spc))
    # band = credible region on the RAW score (honest conviction interval)
    return dict(fire=firex, xlo=int(Xc.min()), xhi=int(Xc.max()), width=int(Xc.max()-Xc.min()))

def band_overlap_metric(p):
    cfg={c:config(c,p) for c in CENTS}; cfg={c:v for c,v in cfg.items() if v}
    cs=sorted(cfg)
    # fraction of adjacent cents whose credible bands OVERLAP
    ov=0; tot=0
    for a,b in zip(cs,cs[1:]):
        if b-a!=1: continue
        tot+=1
        A=cfg[a]; B=cfg[b]
        if min(A['xhi'],B['xhi'])>=max(A['xlo'],B['xlo']): ov+=1
    # fire-X continuity (center-delta) for comparison
    fires=[cfg[c]['fire'] for c in cs]
    jumps=sum(1 for i in range(1,len(fires)) if abs(fires[i]-fires[i-1])>8)
    medw=np.median([cfg[c]['width'] for c in cs])
    return ov,tot,jumps,len(fires)-1,medw

print("p   band-overlap   fireX-jumps>8c   med-bandwidth")
for p in [1,2,3,4,6,8]:
    ov,tot,jumps,nj,medw=band_overlap_metric(p)
    print(f"{p:<3} {ov}/{tot} ({ov/tot*100:.0f}%)      {jumps}/{nj}            {medw:.0f}c")

print("\nDetail at p=4 (cheap cells):")
for c in [5,6,7,8,9,10,11,12,13,14,15,20,89,90,92]:
    r=config(c,4)
    if r: print(f"  c={c:>2}: fire=+{r['fire']:>4.1f}  band[{r['xlo']:>2},{r['xhi']:>2}] w={r['width']:>2}")

print("\n"+"="*64)
print("LEVER 1: adaptive tau -> shrink credible region until width <= cap")
print("="*64)
def config_adaptive(c,wcap=12,kp=2.0,m0=1.2):
    Xs=np.arange(1,95-c)
    if len(Xs)==0: return None
    EV,HIT,ROI=curve(c,k,h,Xs); se=SE(c,k,h)
    paid=1-(HIT/100)**kp; supp=np.minimum(1.0,(HIT/100)/(m0*se))
    s=np.where(EV>0,EV*paid*supp,0.0)
    if s.max()<=0: return None
    # raise tau from 0.7 upward until contiguous region around peak <= wcap
    peak=np.argmax(s)
    for tau in np.arange(0.70,0.999,0.02):
        cred=s>=tau*s.max()
        # contiguous run containing the peak
        lo=peak
        while lo>0 and cred[lo-1]: lo-=1
        hi=peak
        while hi<len(s)-1 and cred[hi+1]: hi+=1
        if Xs[hi]-Xs[lo]<=wcap:
            Xc=Xs[lo:hi+1]; sc=s[lo:hi+1]
            return dict(fire=float(np.sum(Xc*sc)/np.sum(sc)),xlo=int(Xs[lo]),xhi=int(Xs[hi]),width=int(Xs[hi]-Xs[lo]),tau=round(tau,2))
    # fallback: just the peak
    return dict(fire=float(Xs[peak]),xlo=int(Xs[peak]),xhi=int(Xs[peak]),width=0,tau=0.99)

for wcap in [8,12,16]:
    cfg={c:config_adaptive(c,wcap) for c in CENTS}; cfg={c:v for c,v in cfg.items() if v}
    cs=sorted(cfg); fires=[cfg[c]['fire'] for c in cs]
    jumps=sum(1 for i in range(1,len(fires)) if abs(fires[i]-fires[i-1])>8)
    ov=tot=0
    for a,b in zip(cs,cs[1:]):
        if b-a!=1: continue
        tot+=1
        if min(cfg[a]['xhi'],cfg[b]['xhi'])>=max(cfg[a]['xlo'],cfg[b]['xlo']): ov+=1
    print(f"  wcap={wcap}: fire-jumps>8c={jumps}/{len(fires)-1}  band-overlap={ov}/{tot} ({ov/tot*100:.0f}%)")

print("\n  Detail wcap=12 (cheap cells localize?):")
for c in [5,6,7,8,9,10,11,12,13,14,15,20]:
    r=config_adaptive(c,12)
    if r: print(f"  c={c:>2}: fire=+{r['fire']:>4.1f} band[{r['xlo']:>2},{r['xhi']:>2}] w={r['width']:>2} tau={r['tau']}")

print("\n"+"="*64)
print("LEVER C: commit to LOWER (bank-early) mode for bimodal cells")
print("="*64)
from scipy.signal import argrelextrema
def config_bankmode(c,kp=2.0,m0=1.2,tau=0.5):
    Xs=np.arange(1,95-c)
    if len(Xs)<3: return None
    EV,HIT,ROI=curve(c,k,h,Xs); se=SE(c,k,h)
    paid=1-(HIT/100)**kp; supp=np.minimum(1.0,(HIT/100)/(m0*se))
    s=np.where(EV>0,EV*paid*supp,0.0)
    if s.max()<=0: return None
    # find local maxima of s above tau*peak; pick the LOWEST-X one (bank-early)
    thr=tau*s.max()
    maxima=[i for i in range(1,len(s)-1) if s[i]>=s[i-1] and s[i]>=s[i+1] and s[i]>=thr]
    if not maxima: maxima=[int(np.argmax(s))]
    pick=maxima[0]  # lowest-X credible mode
    # localized centroid around that mode (contiguous >=0.85*local)
    lo=pick
    while lo>0 and s[lo-1]>=0.85*s[pick]: lo-=1
    hi=pick
    while hi<len(s)-1 and s[hi+1]>=0.85*s[pick]: hi+=1
    Xc=Xs[lo:hi+1]; sc=s[lo:hi+1]
    fire=float(np.sum(Xc*sc)/np.sum(sc))
    return dict(fire=fire, xlo=int(Xs[lo]),xhi=int(Xs[hi]),
                reach=int(Xs[maxima[-1]]), nmodes=len(maxima))
cfg={c:config_bankmode(c) for c in CENTS}; cfg={c:v for c,v in cfg.items() if v}
cs=sorted(cfg); fires=[cfg[c]['fire'] for c in cs]
jumps=sum(1 for i in range(1,len(fires)) if abs(fires[i]-fires[i-1])>8)
big=sum(1 for i in range(1,len(fires)) if abs(fires[i]-fires[i-1])>5)
print(f"  fire-jumps >8c: {jumps}/{len(fires)-1}   >5c: {big}/{len(fires)-1}")
for c in [5,6,7,8,9,10,11,12,13,14,15,20,38,67,89,90,92]:
    r=cfg.get(c)
    if r: print(f"  c={c:>2}: fire=+{r['fire']:>4.1f}  bank-band[{r['xlo']:>2},{r['xhi']:>2}]  reach-mode=+{r['reach']:>2}  modes={r['nmodes']}")
