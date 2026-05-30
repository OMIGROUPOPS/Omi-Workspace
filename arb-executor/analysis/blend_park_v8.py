"""
v8 — PARK = within-cell bootstrap-argmax STABILITY (Opus's corrected candidate 3).
Branch blend/agent-derivation.

Null criterion (Opus): destroy the exact statistic the readout fires on (which-X-is-best,
i.e. the SPECIFICITY of the kiss-rate edge) while preserving base rate, spread, N, cost basis.
=> resample the cell's OWN tapes; recompute best-X; PARK if best-X is NOT reproduced within
   +-2c in >= alpha of resamples. No foreign structure imported. No absolute EV floor.

Classification:
  resolvable = bootstrap-stable (best-X within +-2c in >= alpha of resamples)
  supported  = npos >= NPOS_MIN            (orthogonal: enough tapes)
  EXIT iff resolvable AND supported AND best-exit beats hold
  HOLD iff resolvable AND supported AND hold beats best-exit       (economic, permanent)
  PARK otherwise                                                    (epistemic, price-parametric)

Three falsifiers (break it if they fail):
  F1: does stability reproduce the 4-survivor EXIT basin WITHOUT an absolute floor, and is c92
      EXIT at EVERY alpha in 0.70-0.85? (if c92 ever parks, null still wrong)
  F2 (the one to hammer): sweep alpha; continuity must NOT improve monotonically with alpha.
      If it still climbs toward park-everything, stability sneaks in live signal -> split fails.
  F3: price-invariance — stability computed on MOVES (invariant to entry discount); under a
      uniform discount, PARK->EXIT in cost-basis order, NO stable cell flips EXIT->PARK.
  SEAM: do stability and npos disagree on a handful (favorites-thin / cheap-deep)? -> signal.
"""
import numpy as np
from blend_continuous import curve, effN, SE, CENTS, rel, weights
rng = np.random.default_rng(13)

K, H = 0.215, 2.006
KP, M0, TAU, WA = 2.0, 1.2, 0.7, 3
NPOS_MIN = 3
NBOOT = 300

def pooled_tapes(c):
    """The cell's full conviction-weighted pool: list of (m_array, sv_array, weight)."""
    W = weights(c, K, H)
    out = []
    for n, w in W.items():
        m, sv = rel[n]
        if len(m): out.append((m, sv, w))
    return out

def score_and_bestx(c, cost, pool):
    Xs = np.arange(1, 95 - c)
    if len(Xs) == 0: return None, None, None, None
    EV = np.zeros(len(Xs)); HIT = np.zeros(len(Xs)); WT = 0.0
    for m, sv, w in pool:
        for j, X in enumerate(Xs):
            kiss = m >= X
            pnl = np.where(kiss, X, np.where(sv == 1, 100 - cost, -cost)).astype(float)
            EV[j] += w * pnl.sum(); HIT[j] += w * kiss.sum()
        WT += w * len(m)
    EV /= WT; HIT = HIT / WT * 100
    se = SE(c, K, H)
    paid = 1 - (HIT / 100) ** KP
    supp = np.minimum(1.0, (HIT / 100) / (M0 * se))
    s = np.where(EV > 0, EV * paid * supp, 0.0)
    bx = int(Xs[int(np.argmax(s))]) if s.max() > 0 else None
    return Xs, s, EV, bx

def stability(c, cost=None):
    """Fraction of within-cell resamples whose best-X lands within +-2c of the full-pool best-X."""
    if cost is None: cost = c
    pool = pooled_tapes(c)
    if not pool: return 0.0, None, 0
    Xs, s, EV, bx = score_and_bestx(c, cost, pool)
    if bx is None: return 0.0, None, int((EV > 0).sum()) if EV is not None else 0
    npos = int((EV > 0).sum())
    hits = 0
    for _ in range(NBOOT):
        rpool = []
        for m, sv, w in pool:
            n = len(m); idx = rng.integers(0, n, n)
            rpool.append((m[idx], sv[idx], w))
        _, _, _, bxb = score_and_bestx(c, cost, rpool)
        if bxb is not None and abs(bxb - bx) <= 2: hits += 1
    return hits / NBOOT, bx, npos

def classify(c, alpha=0.75, cost=None):
    if cost is None: cost = c
    stab, bx, npos = stability(c, cost)
    pool = pooled_tapes(c)
    Xs, s, EV, _ = score_and_bestx(c, cost, pool)
    resolvable = stab >= alpha
    supported = npos >= NPOS_MIN
    if not (resolvable and supported):
        return dict(state='PARK', stab=round(stab,3), npos=npos, resolvable=resolvable, supported=supported)
    # hold vs exit (economic, no param)
    allsv = np.concatenate([sv for _,sv,_ in pool])
    holdEV = float(np.mean(np.where(allsv == 1, 100 - cost, -cost)))
    bestEV = float(EV[np.argmax(s)])
    if holdEV >= bestEV:
        return dict(state='HOLD', stab=round(stab,3), npos=npos, holdEV=round(holdEV,2), bestEV=round(bestEV,2))
    cred = s >= TAU * s.max(); Xc = Xs[cred]; xlo, xhi = int(Xc.min()), int(Xc.max()); w = xhi - xlo
    fx = xlo if w > WA else bx
    return dict(state='EXIT', regime='A' if w <= WA else 'B', fire_x=int(fx),
                xlo=xlo, xhi=xhi, width=w, stab=round(stab,3), npos=npos)

if __name__ == "__main__":
    print("="*72); print("v8 PARK = within-cell bootstrap stability — classify at T-20 floor (alpha=0.75)"); print("="*72)
    C = {c: classify(c, 0.75) for c in CENTS}
    cE=[c for c in CENTS if C[c]['state']=='EXIT']; cH=[c for c in CENTS if C[c]['state']=='HOLD']; cP=[c for c in CENTS if C[c]['state']=='PARK']
    print(f"EXIT={len(cE)}  HOLD={len(cH)}  PARK={len(cP)}")
    print(f"  EXIT: {cE}")
    print(f"  HOLD: {cH}")

    # F1: c92 must be EXIT at every alpha 0.70-0.85; within-EXIT continuity basin
    print("\n--- F1: c92 stable at every alpha? + within-EXIT jumps ---")
    for c in [88,89,90,91,92,93]:
        r=classify(c,0.75); print(f"  c{c}: {r['state']} stab={r.get('stab')} npos={r.get('npos')}")
    ec=sorted(cE); wr=0
    for i in range(1,len(ec)):
        a,b=C[ec[i-1]],C[ec[i]]
        if ec[i]-ec[i-1]==1 and a['regime']==b['regime'] and abs(b['fire_x']-a['fire_x'])>8: wr+=1
    print(f"  within-regime adjacent jumps>8c among EXIT: {wr}")

    # F2 (HAMMER): sweep alpha; continuity must NOT climb monotonically toward park-all
    print("\n--- F2 (HAMMER): alpha sweep — does continuity climb monotonically? ---")
    print("  alpha  nEXIT  nHOLD  nPARK  within-jumps  c92-state")
    for a in (0.60,0.70,0.75,0.80,0.85,0.90,0.95):
        Ca={c:classify(c,a) for c in CENTS}
        e=[c for c in CENTS if Ca[c]['state']=='EXIT']
        nj=0; es=sorted(e)
        for i in range(1,len(es)):
            x,y=Ca[es[i-1]],Ca[es[i]]
            if es[i]-es[i-1]==1 and x['regime']==y['regime'] and abs(y['fire_x']-x['fire_x'])>8: nj+=1
        print(f"  {a:.2f}    {len(e):>2}    {sum(Ca[c]['state']=='HOLD' for c in CENTS):>2}    "
              f"{sum(Ca[c]['state']=='PARK' for c in CENTS):>2}     {nj:>2}          {Ca[92]['state']}")

    # SEAM: stability vs npos disagreement
    print("\n--- SEAM: stability(>=0.75) vs npos(>=3) disagreement ---")
    dis=[]
    for c in CENTS:
        stab,bx,npos=stability(c)
        rok=stab>=0.75; nok=npos>=NPOS_MIN
        if rok!=nok: dis.append((c,'stable' if rok else 'unstable',f'npos={npos}',f'stab={stab:.2f}'))
    print(f"  disagreements: {len(dis)}")
    for d in dis[:25]: print(f"    c{d[0]}: {d[1]}  {d[2]}  {d[3]}")
