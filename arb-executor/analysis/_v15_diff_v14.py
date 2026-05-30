"""Diff v15 EXIT set vs v14 EXIT set, and report SE/center of every cell that differs OR wobbles
under the smooth knob. Material = |mse|>=1.0-ish and EV clearly positive. Trivial = sub-1-SE boundary.
Also re-run v14 state() to get its authoritative EXIT set in THIS process."""
import numpy as np, collections
from blend_park_v8 import pooled_tapes, score_and_bestx
from blend_continuous import CENTS
import park_v14_locked as V14
from _v15_validate import get_draws, v15_state, peaks_lowtohigh
from park_v14_locked import fired_breakeven, FLOOR, WIN, M_CUSHION, NPOS_MIN

ALL=list(CENTS)
DR={c:get_draws(c,300) for c in ALL}

# v14 EXIT set via its own state()
v14_exit=set()
for c in ALL:
    try:
        stv=V14.state(c,0)
        s=stv[0] if isinstance(stv,(tuple,list)) else stv
        if str(s)=='EXIT': v14_exit.add(c)
    except Exception as e:
        print(f"v14 state c{c} err {e}")

v15_exit={}
for c in ALL:
    d,npos=DR[c]; st,ctr=v15_state(c,d,npos,2)
    if st=='EXIT': v15_exit[c]=ctr

ve=set(v15_exit)
print(f"v14 |EXIT|={len(v14_exit)}  v15 |EXIT|={len(ve)}")
print(f"v15 added (not in v14): {sorted(ve-v14_exit)}")
print(f"v15 dropped (in v14 not v15): {sorted(v14_exit-ve)}")
print(f"shared: {len(ve & v14_exit)}")

def mse_of(c,ctr):
    d,npos=DR[c]
    # find the cluster mask for ctr
    for cc,mask in peaks_lowtohigh(d,2):
        if cc==ctr:
            occ=mask.mean(); hit,be,EVf,hold=fired_breakeven(c,ctr,0)
            n=max(1.0,occ*npos); se=(hit*(1-hit)/n)**0.5 if 0<hit<1 else 1e-9
            return (hit-be)/se, EVf, occ
    return None,None,None

wobble=sorted(set([31,42,62,79]) | (ve-v14_exit) | (v14_exit-ve))
print("\nMateriality of differing/wobbling cells (v15 fired center if any):")
for c in wobble:
    ctr=v15_exit.get(c)
    if ctr is None:
        # show what v15 calls it
        d,npos=DR[c]; st,_=v15_state(c,d,npos,2)
        print(f"  c{c}: v15={st} (no EXIT)  inV14={c in v14_exit}")
    else:
        mse,EVf,occ=mse_of(c,ctr)
        print(f"  c{c}: v15 EXIT X{ctr} mse={mse:+.2f} EVf={EVf:+.2f} occ={occ:.2f}  inV14={c in v14_exit}")
