"""Regime-aware stability: a cell is RESOLVABLE if EITHER its fire-point is stable
(narrow/favorite cells) OR its band is stable (wide/cheap cells). This matches the
regime structure: you don't need to pin xlo on a wide flat band if the band itself
is reproducible. npos>=3 stays as an orthogonal support guard."""
import numpy as np
from blend_park_v8 import pooled_tapes, score_and_bestx
from blend_continuous import CENTS
rng=np.random.default_rng(13)
KP,M0,TAU,WA,NPOS_MIN,NBOOT=2.0,1.2,0.7,3,3,200

def cred_band(c,cost,pool):
    Xs,s,EV,bx=score_and_bestx(c,cost,pool)
    if Xs is None or s.max()<=0: return None
    cred=s>=TAU*s.max(); Xc=Xs[cred]
    return int(Xc.min()),int(Xc.max()),int((EV>0).sum())

def metrics(c,cost=None):
    if cost is None: cost=c
    pool=pooled_tapes(c)
    if not pool: return None
    base=cred_band(c,cost,pool)
    if base is None: return dict(resolv=0.0,xlo=None,xhi=None,npos=0,w=None)
    xlo0,xhi0,npos=base; w0=xhi0-xlo0
    hx=0; hb=0; ok=0
    for _ in range(NBOOT):
        rp=[(m[idx],sv[idx],w) for (m,sv,w) in pool for idx in [rng.integers(0,len(m),len(m))]]
        b=cred_band(c,cost,rp)
        if b is None: continue
        xlo,xhi,_=b
        fp = abs(xlo-xlo0)<=3
        inter=max(0,min(xhi,xhi0)-max(xlo,xlo0)); uni=max(xhi,xhi0)-min(xlo,xlo0)
        bd = (uni==0) or (inter/uni>=0.5)
        if fp: hx+=1
        if bd: hb+=1
        if fp or bd: ok+=1
    return dict(resolv=ok/NBOOT,stab_xlo=hx/NBOOT,stab_band=hb/NBOOT,
                xlo=xlo0,xhi=xhi0,w=w0,npos=npos)

R={}
for c in CENTS:
    m=metrics(c)
    if m: R[c]=m

print("regime-aware RESOLVABILITY (fire-point OR band stable):")
print(" alpha nEXIT nPARK  within-jumps  c92 c91 c85 c9 c20 c49")
def fx(c):
    m=R[c]; return m['xlo'] if (m['w'] or 0)>WA else m['xlo']
for a in (0.60,0.70,0.75,0.80,0.85,0.90):
    E=[c for c in R if R[c]['resolv']>=a and R[c]['npos']>=NPOS_MIN and R[c]['xlo'] is not None]
    es=sorted(E); nj=0
    for i in range(1,len(es)):
        if es[i]-es[i-1]==1 and abs(fx(es[i])-fx(es[i-1]))>8: nj+=1
    def st(c): return 'E' if c in E else 'P'
    print(f" {a:.2f}  {len(E):>3}  {len(R)-len(E):>3}     {nj:>2}        {st(92)}  {st(91)} {st(85)} {st(9)} {st(20)} {st(49)}")

print("\nkey cells (resolv = max coverage of fire-point/band):")
print(" c   resolv  s_xlo  s_band  npos  band   w")
for c in [5,7,9,12,20,30,49,61,85,88,89,90,91,92]:
    if c in R:
        m=R[c]
        print(f" {c:>2}   {m['resolv']:.2f}   {m['stab_xlo']:.2f}   {m['stab_band']:.2f}   {m['npos']:>2}  [{m['xlo']},{m['xhi']}] {m['w']:>2}")
