"""v15 + absolute-EV floor (Opus's fork call). The magnitude gate replaces the SE-relative cushion
as the binding gate: a peak fires iff
  cond >= FLOOR (resolvability) AND occ >= MIN_OCC (prominence) AND EV_fire >= E_min cents (magnitude)
  AND EV_fire > hold (beat settling).
Cushion kept ONLY as a loose rate-sanity floor (un-paid high-hit crumb guard), dominated by E_min.

Four diffs Opus demanded:
 (1) E_min plateau sweep -> EXIT-set identity across band [0.5..1.5]c; find the flat plateau.
 (2) smooth-window {1,2,3} stability WITH E_min in place -> does the c31/42/62/79 wobble collapse?
 (3) ballast confirm: every v14 ballast cell clears E_min; c44 stays PARK.
 (4) ENGINE sweep (point 4, the one Opus is least sure of): over the FULL set of resolved cheap cells,
     does any genuine low engine mode bank < E_min? If yes, E_min must drop below it.
Uses cached B=300 draws (/tmp/v15_draws_b300.pkl).
"""
import numpy as np, pickle, collections
from blend_continuous import CENTS
from _v15_validate import peaks_lowtohigh, MIN_OCC
from park_v14_locked import fired_breakeven, FLOOR, WIN, M_CUSHION, NPOS_MIN

DRr=pickle.load(open('/tmp/v15_draws_b300.pkl','rb'))
DR={c:(None if d is None else np.array(d), n) for c,(d,n) in DRr.items()}
ALL=list(CENTS)

def state_emin(c, draws, npos, E_min, smooth=2, use_cushion_floor=True):
    """Returns (verdict, center, EVfire). E_min binding; cushion only a loose floor."""
    if draws is None or npos<NPOS_MIN: return ('PARK-thin',None,None)
    saw=False
    for ctr,mask in peaks_lowtohigh(draws,smooth):
        occ=mask.mean()
        if occ<MIN_OCC: continue
        lc=(np.abs(draws[mask]-ctr)<=WIN).mean()
        if lc<FLOOR: continue
        saw=True
        hit,be,EVf,hold=fired_breakeven(c,ctr,0)
        if EVf<=hold: continue                 # must beat settling
        if EVf<E_min: continue                 # MAGNITUDE gate (the new binding gate)
        # loose rate-sanity floor only (dominated by E_min); prevents un-paid high-hit crumb
        if use_cushion_floor and hit < be:     # bare breakeven sanity, NO SE cushion term
            continue
        return ('EXIT',ctr,EVf)
    return ('PARK' if saw else 'PARK-noise', None, None)

# baseline v15 EXIT set (no E_min, cushion as before) for reference
from _v15_validate import v15_state
v15_base={c:v15_state(c,*DR[c],2) for c in ALL}
base_exit={c:st[1] for c,st in v15_base.items() if st[0]=='EXIT'}

print("=== (1) E_min PLATEAU sweep (EXIT-set identity in cents) ===")
prev=None
for E in [0.25,0.5,0.6,0.75,0.9,1.0,1.1,1.2,1.35,1.5]:
    ex={}
    for c in ALL:
        d,npos=DR[c]; st,ctr,evf=state_emin(c,d,npos,E,2)
        if st=='EXIT': ex[c]=ctr
    s=set(ex)
    delta="" if prev is None else f"  +{sorted(s-prev)} -{sorted(prev-s)}"
    print(f"  E_min={E:>4}: |EXIT|={len(s)}{delta}")
    prev=s

# Fix E_min=1.0 for the rest
E0=1.0
exit10={}
for c in ALL:
    d,npos=DR[c]; st,ctr,evf=state_emin(c,d,npos,E0,2)
    if st=='EXIT': exit10[c]=(ctr,round(evf,2))

print(f"\n=== (2) smooth-window {{1,2,3}} stability WITH E_min={E0} ===")
sets={}
for sm in [1,2,3]:
    ex=set()
    for c in ALL:
        d,npos=DR[c]; st,ctr,evf=state_emin(c,d,npos,E0,sm)
        if st=='EXIT': ex.add(c)
    sets[sm]=ex; print(f"  smooth={sm}: |EXIT|={len(ex)}")
b=sets[2]
for sm in [1,3]:
    print(f"  smooth={sm} vs 2: added={sorted(sets[sm]-b)} dropped={sorted(b-sets[sm])}")
print(f"  prior wobblers {{31,42,62,79}} now: " +
      ", ".join(f"c{c}:{'EXIT' if c in b else 'park'}" for c in [31,42,62,79]))

print(f"\n=== (3) ballast + c44 confirm (E_min={E0}) ===")
for c in [91,86,87,84,88,44,36]:
    d,npos=DR[c]; st,ctr,evf=state_emin(c,d,npos,E0,2)
    print(f"  c{c}: {st}/X{ctr}/{'%.2f'%evf if evf is not None else '-'}c")

print(f"\n=== (4) FULL ENGINE sweep — any real cheap mode banking < E_min? ===")
# engine = cells whose LOWEST occ-qualifying cond-passing peak center is cheap (<=15c above) and EV>hold
risky=[]
for c in ALL:
    d,npos=DR[c]
    if d is None or npos<NPOS_MIN: continue
    for ctr,mask in peaks_lowtohigh(d,2):
        occ=mask.mean()
        if occ<MIN_OCC: continue
        lc=(np.abs(d[mask]-ctr)<=WIN).mean()
        if lc<FLOOR: continue
        hit,be,EVf,hold=fired_breakeven(c,ctr,0)
        if EVf<=hold: continue
        # a resolved, occ-real, beats-hold peak. Is it cheap-engine and banking little?
        if ctr<=15 and hit>=be:
            tag=" <== REAL CHEAP MODE BANKS < 1c" if EVf<E0 else ""
            if EVf<1.5:
                print(f"  c{c} X{ctr}: occ={occ:.2f} hit={hit:.2f} be={be:.2f} EVf={EVf:+.2f}c hold={hold:+.2f}{tag}")
            if EVf<E0: risky.append((c,ctr,round(EVf,2)))
        break  # only the lowest qualifying peak (what would actually fire)
print(f"  -> cheap modes that would PARK under E_min={E0} (their lowest-fireable peak banks <{E0}c): {risky}")

print(f"\n=== FINAL v15+E_min={E0} EXIT set ({len(exit10)}): ===")
print("  "+", ".join(f"c{c}:X{v[0]}({v[1]}c)" for c,v in sorted(exit10.items())))
