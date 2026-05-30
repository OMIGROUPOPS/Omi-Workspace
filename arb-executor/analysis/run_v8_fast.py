"""Fast driver: compute within-cell stability ONCE per cent (alpha-independent),
cache it, then run all of Opus's falsifiers off the cache."""
import numpy as np, json
from blend_park_v8 import stability, pooled_tapes, score_and_bestx, NPOS_MIN, TAU, WA
from blend_continuous import CENTS, SE

# 1) compute stability, bestx, npos ONCE per cent at T-20 floor (cost=c)
CACHE={}
for c in CENTS:
    stab,bx,npos=stability(c)            # 300 boots, once
    pool=pooled_tapes(c)
    Xs,s,EV,_=score_and_bestx(c,c,pool)
    if Xs is None or s.max()<=0:
        CACHE[c]=dict(stab=stab,bx=bx,npos=npos,exitable=False); continue
    allsv=np.concatenate([sv for _,sv,_ in pool])
    holdEV=float(np.mean(np.where(allsv==1,100-c,-c)))
    bestEV=float(EV[np.argmax(s)])
    cred=s>=TAU*s.max(); Xc=Xs[cred]; xlo,xhi=int(Xc.min()),int(Xc.max()); w=xhi-xlo
    fx=xlo if w>WA else bx
    CACHE[c]=dict(stab=stab,bx=bx,npos=npos,exitable=True,holdEV=holdEV,bestEV=bestEV,
                  xlo=xlo,xhi=xhi,width=w,fire_x=int(fx),regime='A' if w<=WA else 'B')
json.dump({str(k):{kk:(vv if not isinstance(vv,np.integer) else int(vv)) for kk,vv in v.items()} for k,v in CACHE.items()},
          open('/tmp/v8_cache.json','w'))

def classify(c,alpha):
    d=CACHE[c]
    if not d['exitable'] or d['stab']<alpha or d['npos']<NPOS_MIN:
        # HOLD if resolvable+supported but hold wins; else PARK
        if d['exitable'] and d['stab']>=alpha and d['npos']>=NPOS_MIN and d['holdEV']>=d['bestEV']:
            return 'HOLD',d
        if d['exitable'] and d['stab']>=alpha and d['npos']>=NPOS_MIN:
            return 'EXIT',d
        return 'PARK',d
    if d['holdEV']>=d['bestEV']: return 'HOLD',d
    return 'EXIT',d

print("="*70); print("v8 FAST — stability cached once, alpha applied after"); print("="*70)
for a in [0.75]:
    states={c:classify(c,a)[0] for c in CENTS}
    e=[c for c in CENTS if states[c]=='EXIT']
    print(f"alpha={a}: EXIT={len(e)} HOLD={sum(v=='HOLD' for v in states.values())} PARK={sum(v=='PARK' for v in states.values())}")
    print(f"  EXIT cents: {e}")

print("\n--- F1: c88-93 stability + within-EXIT jumps (alpha=0.75) ---")
for c in [88,89,90,91,92,93]:
    d=CACHE[c]; st,_=classify(c,0.75); print(f"  c{c}: {st} stab={d['stab']:.2f} npos={d['npos']}")

print("\n--- F2 (HAMMER): alpha sweep — continuity must NOT climb monotonically ---")
print("  alpha  nEXIT nHOLD nPARK within-jumps c92")
for a in (0.50,0.60,0.70,0.75,0.80,0.85,0.90,0.95):
    states={c:classify(c,a)[0] for c in CENTS}
    e=sorted([c for c in CENTS if states[c]=='EXIT'])
    nj=0
    for i in range(1,len(e)):
        if e[i]-e[i-1]==1:
            a1,a2=CACHE[e[i-1]],CACHE[e[i]]
            if a1['regime']==a2['regime'] and abs(a2['fire_x']-a1['fire_x'])>8: nj+=1
    print(f"  {a:.2f}   {len(e):>3}  {sum(v=='HOLD' for v in states.values()):>3}  "
          f"{sum(v=='PARK' for v in states.values()):>3}    {nj:>2}        {states[92]}")

print("\n--- SEAM: stability(>=0.75) vs npos(>=3) disagreement ---")
dis=[(c,CACHE[c]['stab'],CACHE[c]['npos']) for c in CENTS
     if (CACHE[c]['stab']>=0.75) != (CACHE[c]['npos']>=NPOS_MIN)]
print(f"  disagreements: {len(dis)}")
for c,s,n in dis[:25]:
    print(f"    c{c}: {'stable' if s>=0.75 else 'unstable'} stab={s:.2f} npos={n}")
