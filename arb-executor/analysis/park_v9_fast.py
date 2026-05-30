"""v9 FAST — resolvability/consensus-band computed ONCE (basis-invariant), profitability
recomputed per-discount (cheap). This architecture IS Opus's invariance claim made literal:
stability is on moves (cache once); only EV moves with basis."""
import numpy as np
from blend_park_v8 import pooled_tapes, score_and_bestx
from blend_continuous import CENTS
rng=np.random.default_rng(13)
KP,M0,TAU,WA,NPOS_MIN,NBOOT,ALPHA=2.0,1.2,0.7,3,3,200,0.75

# ---- ONE-TIME: resolvability + consensus band at the cell's OWN moves (basis-invariant) ----
RES={}
for c in CENTS:
    pool=pooled_tapes(c)
    if not pool: RES[c]=dict(resolvable=False,npos=0,regime='-',cb_lo=None,cb_hi=None); continue
    Xs,s,EV,bx=score_and_bestx(c,c,pool)   # cost=c only sets EV; resolvability uses band SHAPE
    if Xs is None or s.max()<=0: RES[c]=dict(resolvable=False,npos=0,regime='-',cb_lo=None,cb_hi=None); continue
    base=s>=TAU*s.max(); bw=int(Xs[base].max()-Xs[base].min()); regime='A' if bw<=WA else 'B'
    xlo0=int(Xs[base].min())
    incl=np.zeros(len(Xs)); fp=0
    for _ in range(NBOOT):
        rp=[(m[idx],sv[idx],w) for (m,sv,w) in pool for idx in [rng.integers(0,len(m),len(m))]]
        X2,s2,E2,_=score_and_bestx(c,c,rp)
        if X2 is None or s2.max()<=0: continue
        cr=s2>=TAU*s2.max()
        L=min(len(cr),len(incl)); incl[:L]+=cr[:L]
        if abs(int(X2[cr].min())-xlo0)<=3: fp+=1
    incl/=NBOOT; consensus=incl>=ALPHA
    resolvable = (fp/NBOOT>=ALPHA) if regime=='A' else (consensus.sum()>=2)
    cb_lo=int(Xs[consensus].min()) if consensus.any() else xlo0
    cb_hi=int(Xs[consensus].max()) if consensus.any() else xlo0
    RES[c]=dict(resolvable=bool(resolvable),npos=int((EV>0).sum()),regime=regime,
                cb_lo=cb_lo,cb_hi=cb_hi,argmax=int(Xs[int(np.argmax(s))]))

# ---- per-basis profitability (cheap; no bootstrap) ----
def profit_at(c,discount):
    cost=max(1,c-discount); pool=pooled_tapes(c)
    Xs,s,EV,_=score_and_bestx(c,cost,pool)
    if Xs is None or s.max()<=0: return None
    allsv=np.concatenate([sv for _,sv,_ in pool]); holdEV=float(np.mean(np.where(allsv==1,100-cost,-cost)))
    return float(EV[np.argmax(s)]),holdEV

def state(c,discount=0):
    r=RES[c]
    # SUPPORT precedes RESOLVABILITY: with npos<3 there aren't enough positive
    # observations to even pose the resolvability question -> structurally THIN.
    if r['npos']<NPOS_MIN: return 'PARK-thin'
    if not r['resolvable']: return 'PARK-noise'
    p=profit_at(c,discount)
    if p is None: return 'PARK-noise'
    bestEV,holdEV=p
    # supported+resolvable but exit does not beat hold NOW:
    #   bestEV<=0  -> dead at this basis, dormant ENGINE (reactivates as discount lifts cost)
    #   0<bestEV<=holdEV -> live positive edge, prefer to HOLD the position
    if bestEV<=holdEV: return 'PARK-engine' if bestEV<=0 else 'HOLD'
    return 'EXIT'

from collections import Counter
print("="*70); print("v9 baseline (discount=0)"); print("="*70)
B={c:state(c,0) for c in CENTS}; print(Counter(B.values()))
noise=[c for c in CENTS if B[c]=='PARK-noise']; engine=[c for c in CENTS if B[c]=='PARK-engine']
exitc=[c for c in CENTS if B[c]=='EXIT']; thin=[c for c in CENTS if B[c]=='PARK-thin']
hold=[c for c in CENTS if B[c]=='HOLD']
print(f"EXIT: {exitc}")
print(f"HOLD: {hold}")
print(f"PARK-engine: {engine}")
print(f"PARK-thin: {thin}")
print(f"PARK-noise (permanent): {noise}")

print("\n"+"="*70); print("F3 discount sweep — engine lights cost-ordered, noise stays DARK"); print("="*70)
print(" disc nEXIT  engine->EXIT          noise->EXIT(MUST=[])  EXIT->PARK(MUST=[])")
for disc in (0,3,6,10,15,20):
    S={c:state(c,disc) for c in CENTS}
    e2=[c for c in engine if S[c]=='EXIT']; n2=[c for c in noise if S[c]=='EXIT']; e2p=[c for c in exitc if S[c].startswith('PARK')]
    print(f"  {disc:>2}  {sum(v=='EXIT' for v in S.values()):>3}   {str(e2)[:20]:<20}  {str(n2):<20} {e2p}  order_ok={e2==sorted(e2)}")

print("\n"+"="*70); print("HAMMER: cheap PARK-noise cells forced EV>0 by discount — MUST stay PARK"); print("="*70)
for c in [x for x in noise if x<=25][:6]:
    for disc in (0,5,10,15,20,25,30):
        cost=max(1,c-disc); p=profit_at(c,disc)
        if p and p[0]>p[1]:
            print(f"  c{c} disc={disc} (cost={cost}): bestEV={p[0]:.2f}>holdEV={p[1]:.2f} nominally PROFITABLE | resolvable={RES[c]['resolvable']} -> STATE={state(c,disc)}")
            break
    else:
        print(f"  c{c}: stays unprofitable through disc=30")
