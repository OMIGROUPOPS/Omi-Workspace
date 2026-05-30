"""v9 — Opus's locked structure + the F3 discount seam (the test that locks or breaks it).

Corrections adopted from Opus:
  #1a regime-SWITCH not OR: favorite(narrow)->fire-point test; cheap(wide)->band test. one arm each.
  #1b CONSENSUS band: stable band = X's credible in >=alpha of resamples; FIRE its low edge.
      test-quantity == fired-quantity (re-unified).
  #2  alpha FIXED & epistemic (resolvable y/n). Profitability is a PARAMETER-FREE comparison
      (EV>holdEV) that CARRIES the basis dependence. Decomposition:
        EXIT       = resolvable & supported & profitable@basis
        PARK-engine= resolvable & supported & ~profitable@basis  (reactivates via discount, cost order)
        PARK-thin  = resolvable & ~supported                     (c92; reactivates only w/ more tapes)
        PARK-noise = ~resolvable                                  (permanent at ANY basis)
        HOLD       = resolvable & supported & profitable & hold beats every exit

F3 falsifiers (Opus):
  (a) PARK-engine -> EXIT in cost-basis order as discount deepens (cheap first)
  (b) NO EXIT -> PARK under discount (resolvable/supported/profitable all monotone-safe)
  (c) THE HAMMER: PARK-noise stays PARK even when a discount makes it nominally EV>0.
      (discount must NOT let profitability override resolvability = re-admit the lottery)
"""
import numpy as np
from blend_park_v8 import pooled_tapes, score_and_bestx
from blend_continuous import CENTS, SE
rng=np.random.default_rng(13)
KP,M0,TAU,WA,NPOS_MIN,NBOOT,ALPHA=2.0,1.2,0.7,3,3,200,0.75

def consensus_band(c,cost,pool,alpha=ALPHA):
    """Per-X credible-inclusion frequency over resamples; stable band = X's included >=alpha.
    Returns (xlo_consensus, xhi_consensus, regime, npos, base_width, resolvable, fire_x, EV_at_fire, holdEV)."""
    Xs,s,EV,bx=score_and_bestx(c,cost,pool)
    if Xs is None or s.max()<=0: return None
    npos=int((EV>0).sum())
    base_cred=s>=TAU*s.max(); bw=int(Xs[base_cred].max()-Xs[base_cred].min())
    regime='A' if bw<=WA else 'B'
    incl=np.zeros(len(Xs))
    fp_hits=0; xlo0=int(Xs[base_cred].min())
    for _ in range(NBOOT):
        rp=[(m[idx],sv[idx],w) for (m,sv,w) in pool for idx in [rng.integers(0,len(m),len(m))]]
        Xs2,s2,EV2,bx2=score_and_bestx(c,cost,rp)
        if Xs2 is None or s2.max()<=0: continue
        cr=s2>=TAU*s2.max()
        # map inclusion onto base Xs index (same Xs range since same c,cost)
        incl[:len(cr)]+=cr[:len(incl)] if len(cr)>=len(incl) else np.pad(cr,(0,len(incl)-len(cr)))
        xlo2=int(Xs2[cr].min())
        if abs(xlo2-xlo0)<=3: fp_hits+=1
    incl/=NBOOT
    consensus = incl>=alpha
    if regime=='A':
        resolvable = (fp_hits/NBOOT)>=alpha
    else:
        resolvable = consensus.any() and (consensus.sum()>=2)  # a real consensus band exists
    if consensus.any():
        cb_lo=int(Xs[consensus].min()); cb_hi=int(Xs[consensus].max())
    else:
        cb_lo=cb_hi=xlo0
    fire_x = cb_lo if regime=='B' else int(Xs[int(np.argmax(s))])
    i=int(np.where(Xs==fire_x)[0][0]) if fire_x in Xs else int(np.argmax(s))
    allsv=np.concatenate([sv for _,sv,_ in pool]); holdEV=float(np.mean(np.where(allsv==1,100-cost,-cost)))
    return dict(regime=regime,npos=npos,resolvable=bool(resolvable),fire_x=int(fire_x),
                EVfire=float(EV[i]),bestEV=float(EV[np.argmax(s)]),holdEV=holdEV,
                cb_lo=cb_lo,cb_hi=cb_hi)

def state(c,discount=0):
    cost=max(1,c-discount)
    pool=pooled_tapes(c)
    if not pool: return 'PARK-noise',None
    r=consensus_band(c,cost,pool)
    if r is None: return 'PARK-noise',None
    resolvable=r['resolvable']; supported=r['npos']>=NPOS_MIN; profitable=r['bestEV']>r['holdEV']
    if not resolvable: return 'PARK-noise',r
    if not supported: return 'PARK-thin',r
    if not profitable: return 'PARK-engine',r
    if r['holdEV']>=r['bestEV']: return 'HOLD',r
    return 'EXIT',r

# baseline (no discount)
print("="*70); print("v9 baseline (T-20 floor, discount=0)"); print("="*70)
BASE={c:state(c,0) for c in CENTS}
from collections import Counter
print(Counter(s for s,_ in BASE.values()))
noise=[c for c in CENTS if BASE[c][0]=='PARK-noise']
engine=[c for c in CENTS if BASE[c][0]=='PARK-engine']
exitc=[c for c in CENTS if BASE[c][0]=='EXIT']
print(f"EXIT: {exitc}")
print(f"PARK-engine (resolvable, unprofitable@floor): {engine}")
print(f"PARK-noise (unresolvable, permanent): {noise[:30]}")

# F3 discount sweep
print("\n"+"="*70); print("F3: discount sweep — does engine light up, does noise STAY DARK?"); print("="*70)
print(" discount  nEXIT  engine->EXIT(cost order?)  noise->EXIT(MUST be 0)  EXIT->PARK(MUST be 0)")
prev_states=BASE
for disc in (0,3,6,10,15,20):
    S={c:state(c,disc)[0] for c in CENTS}
    nE=sum(v=='EXIT' for v in S.values())
    # engine cells (baseline) that became EXIT
    eng2exit=[c for c in engine if S[c]=='EXIT']
    # noise cells (baseline) that became EXIT  -- THE HAMMER
    noise2exit=[c for c in noise if S[c]=='EXIT']
    # any baseline EXIT that fell to PARK
    e2p=[c for c in exitc if S[c].startswith('PARK')]
    order_ok = eng2exit==sorted(eng2exit)  # cheap-first since cents ascending
    print(f"  {disc:>3}      {nE:>3}    {str(eng2exit)[:34]:<34} {str(noise2exit):<22} {e2p}")

# THE explicit hammer: pick a known PARK-noise cheap cell, crank discount until nominally EV>0, check state
print("\n"+"="*70); print("HAMMER: force a PARK-noise cheap cell EV>0 via discount — must STAY PARK"); print("="*70)
for c in noise:
    if c<=30:  # cheap noise cell
        for disc in (0,5,10,15,20,25):
            st,r=state(c,disc)
            if r and r['bestEV']>r['holdEV']:
                print(f"  c{c} disc={disc}: nominal bestEV={r['bestEV']:.2f}>holdEV={r['holdEV']:.2f}  resolvable={r['resolvable']}  STATE={st}")
                break
        else:
            print(f"  c{c}: never crosses profitability in tested range (stays PARK-engine/noise)")
        if c>=12: break
