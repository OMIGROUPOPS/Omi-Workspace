"""Re-test stability on the FIRED quantity (xlo of the credible band) and on a
band-overlap criterion, not argmax. argmax is the known-noisy lottery; the readout
fires xlo. A cell is 'resolvable' if its fire point / band is reproducible under resample."""
import numpy as np, json
from blend_park_v8 import pooled_tapes, score_and_bestx
from blend_continuous import CENTS, SE
rng=np.random.default_rng(13)
KP,M0,TAU,WA,NPOS_MIN,NBOOT=2.0,1.2,0.7,3,3,200

def curve_xlo(c,cost,pool):
    Xs,s,EV,bx=score_and_bestx(c,cost,pool)
    if Xs is None or s.max()<=0: return None,None,None
    cred=s>=TAU*s.max(); Xc=Xs[cred]
    xlo,xhi=int(Xc.min()),int(Xc.max())
    return xlo,xhi,int((EV>0).sum())

def stab_metrics(c,cost=None):
    if cost is None: cost=c
    pool=pooled_tapes(c)
    if not pool: return None
    base=curve_xlo(c,cost,pool)
    if base[0] is None: return dict(stab_xlo=0,stab_band=0,xlo=None,npos=0)
    xlo0,xhi0,npos=base
    hx=0; hb=0
    for _ in range(NBOOT):
        rp=[(m[idx],sv[idx],w) for (m,sv,w) in pool for idx in [rng.integers(0,len(m),len(m))]]
        b=curve_xlo(c,cost,rp)
        if b[0] is None: continue
        xlo,xhi,_=b
        if abs(xlo-xlo0)<=3: hx+=1                       # fire point reproducible within 3c
        # band overlap (Jaccard) >=0.5
        inter=max(0,min(xhi,xhi0)-max(xlo,xlo0)); uni=max(xhi,xhi0)-min(xlo,xlo0)
        if uni>0 and inter/uni>=0.5: hb+=1
        elif uni==0: hb+=1
    return dict(stab_xlo=hx/NBOOT,stab_band=hb/NBOOT,xlo=xlo0,xhi=xhi0,npos=npos)

print("stability of FIRE-POINT (xlo +-3c) and BAND-overlap vs old argmax:")
print(" c   stab_xlo  stab_band  npos  band")
rows={}
for c in CENTS:
    m=stab_metrics(c)
    if m is None: continue
    rows[c]=m
for c in [5,7,9,12,20,30,49,61,85,88,89,90,91,92,93]:
    if c in rows:
        m=rows[c]
        print(f" {c:>2}   {m['stab_xlo']:.2f}      {m['stab_band']:.2f}      {m['npos']:>2}   [{m['xlo']},{m['xhi']}]")

# does fire-point stability keep c92 EXIT and reproduce a cheap basin?
print("\nclassification by stab_xlo (alpha sweep), npos>=3 required:")
print(" alpha nEXIT nPARK c92 c91 c9 c20")
for a in (0.50,0.60,0.70,0.75,0.85):
    e=[c for c in rows if rows[c]['stab_xlo']>=a and rows[c]['npos']>=NPOS_MIN]
    def st(c): return 'E' if (c in rows and rows[c]['stab_xlo']>=a and rows[c]['npos']>=NPOS_MIN) else 'P'
    print(f" {a:.2f}  {len(e):>3}   {90-len(e):>3}   {st(92)}   {st(91)}  {st(9)}  {st(20)}")
