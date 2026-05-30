"""Authoritative v15 (corrected scan) vs v14 EXIT diff, using cached draws. Reports materiality."""
import numpy as np, pickle, collections
from blend_continuous import CENTS
import park_v14_locked as V14
from _v15_validate import v15_state, peaks_lowtohigh, MIN_OCC
from park_v14_locked import fired_breakeven, FLOOR, WIN, M_CUSHION

DRr=pickle.load(open('/tmp/v15_draws_b300.pkl','rb'))
DR={c:(None if d is None else np.array(d), n) for c,(d,n) in DRr.items()}
ALL=list(CENTS)

v14_exit=set()
for c in ALL:
    try:
        stv=V14.state(c,0); s=stv[0] if isinstance(stv,(tuple,list)) else stv
        if str(s)=='EXIT': v14_exit.add(c)
    except Exception as e: print(f"v14 c{c} err {e}")

cen=collections.Counter(); v15_exit={}
for c in ALL:
    d,npos=DR[c]; st,ctr=v15_state(c,d,npos,2); cen[st]+=1
    if st=='EXIT': v15_exit[c]=ctr
ve=set(v15_exit)
print("=== v15 CENSUS (corrected scan) ===")
for k in ['EXIT','HOLD','PARK-engine','PARK-thin','PARK-noise']: print(f"  {k}: {cen[k]}")
print(f"\nv14 |EXIT|={len(v14_exit)}  v15 |EXIT|={len(ve)}  shared={len(ve&v14_exit)}")
print(f"v15 added : {sorted(ve-v14_exit)}")
print(f"v15 dropped: {sorted(v14_exit-ve)}")

def mse_of(c,ctr):
    d,npos=DR[c]
    for cc,mask in peaks_lowtohigh(d,2):
        if cc==ctr:
            occ=mask.mean(); hit,be,EVf,hold=fired_breakeven(c,ctr,0)
            n=max(1.0,occ*npos); se=(hit*(1-hit)/n)**0.5 if 0<hit<1 else 1e-9
            return (hit-be)/se,EVf,occ
    return None,None,None

print("\nMateriality of differing cells:")
for c in sorted((ve-v14_exit)|(v14_exit-ve)):
    if c in v15_exit:
        m,e,o=mse_of(c,v15_exit[c]); print(f"  c{c}: v15 EXIT X{v15_exit[c]} mse={m:+.2f} EVf={e:+.2f} occ={o:.2f} (NEW)")
    else:
        d,npos=DR[c]; st,_=v15_state(c,d,npos,2); print(f"  c{c}: v15 {st} (was v14 EXIT)")
