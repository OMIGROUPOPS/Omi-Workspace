"""
v7 — HOLD/PARK split (Opus structural fix), with his 3 falsification diffs + the npos seam.
Branch blend/agent-derivation.

Classification per cell (deterministic, no continuity objective):
  EXIT : peak score DISTINGUISHABLE from cell's own noise floor (bootstrap)  AND  enough tapes
         AND best exit beats hold-to-settle    -> A point / B band, fire xlo
  HOLD : resolvable, but holdEV >= max exit EV  -> economic, permanent at this basis (no free param)
  PARK : peak score NOT distinguishable from own noise -> epistemic abstention, price-parametric

The ONLY parameter is the PARK confidence (risk appetite, an operator dial — Druid sets it).
npos_min is a SEPARATE sample-support precondition on EXIT (Opus's flagged seam — test if they disagree).

Falsification diffs (break the split if they fail):
  D1: does the split reproduce the 4-survivor basin with PARK-confidence as the only param,
      and does tightening that confidence STOP moving continuity monotonically?
      Critically: is any c66-type (peak >> noise) cell EVER parked? If yes, test mis-specified.
  D2: does the bootstrap PARK boundary land the SAME cells as floor in [0.05,0.10]?
  D3: price-invariance on PARK: under a uniform entry discount, (a) HOLD stays put,
      (b) PARK flips to EXIT in cost-basis order (cheap first), (c) NO cell flips EXIT->PARK.
  SEAM: do npos_min and noise-distinguishability ever disagree on the real corpus?
"""
import numpy as np
from blend_continuous import curve, effN, SE, CENTS, rel
rng = np.random.default_rng(11)

K, H = 0.215, 2.006
KP, M0, TAU, WA = 2.0, 1.2, 0.7, 3
NPOS_MIN = 3

def cell_curve(c, cost=None):
    """Score curve at cent c. cost overrides the pricing basis (for price-invariance test);
    default cost=c is the T-20 floor."""
    if cost is None: cost = c
    Xs = np.arange(1, 95 - c)
    if len(Xs) == 0: return None
    EV, HIT, ROI = curve(c, K, H, Xs)  # pool/move-shape unchanged; cost only re-prices PnL
    # re-price at `cost` instead of c: kiss->+X unchanged; settle win->+(100-cost), loss->-cost
    # curve() priced at c; adjust the non-kiss leg. Recompute cleanly:
    return _repriced(c, cost, Xs)

def _repriced(c, cost, Xs):
    from blend_continuous import weights
    W = weights(c, K, H)
    EV = np.zeros(len(Xs)); HIT = np.zeros(len(Xs)); WT = 0.0
    for n, w in W.items():
        m, sv = rel[n]
        if len(m) == 0: continue
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
    holdEV = float(np.mean(np.where(np.array([sv for n in W for sv in rel[n][1]]) == 1, 100 - cost, -cost)))
    return dict(Xs=Xs, EV=EV, HIT=HIT, s=s, npos=int((EV > 0).sum()),
                holdEV=holdEV, se=se)

def noise_floor(c, nboot=200):
    """Bootstrap the cell's own peak-score noise floor: resample the cell's OWN tapes,
    recompute peak score, take the high quantile of the resampled peaks under the null
    that there's no real edge (shuffle settlement to kill structure)."""
    m, sv = rel[c]
    n = len(m)
    if n < 2: return np.inf
    peaks = []
    Xs = np.arange(1, 95 - c)
    if len(Xs) == 0: return np.inf
    se = SE(c, K, H)
    for _ in range(nboot):
        idx = rng.integers(0, n, n)
        mb = m[idx]
        svb = rng.permutation(sv)  # null: settlement detached from move -> no real edge
        EV = np.zeros(len(Xs)); HIT = np.zeros(len(Xs))
        for j, X in enumerate(Xs):
            kiss = mb >= X
            pnl = np.where(kiss, X, np.where(svb == 1, 100 - c, -c)).astype(float)
            EV[j] = pnl.mean(); HIT[j] = kiss.mean() * 100
        paid = 1 - (HIT / 100) ** KP
        supp = np.minimum(1.0, (HIT / 100) / (M0 * se))
        s = np.where(EV > 0, EV * paid * supp, 0.0)
        peaks.append(s.max())
    return np.quantile(peaks, 0.95)  # null 95th pct = the noise floor at conf=0.05

def classify(c, conf_q=0.95, cost=None):
    cc = cell_curve(c, cost)
    if cc is None: return dict(state='PARK', reason='no-Xs')
    s = cc['s']; nf = noise_floor(c)
    peak = s.max()
    distinguishable = peak > nf
    enough = cc['npos'] >= NPOS_MIN
    # economic: best exit EV vs hold
    bestexitEV = cc['EV'][np.argmax(s)] if peak > 0 else -np.inf
    if not distinguishable or not enough:
        # PARK if unresolved; but if it's unresolved AND hold clearly best, still HOLD (c91 favorites)
        if cc['holdEV'] >= bestexitEV and enough:
            return dict(state='HOLD', peak=peak, nf=nf, npos=cc['npos'], holdEV=cc['holdEV'], bestEV=float(bestexitEV))
        return dict(state='PARK', peak=peak, nf=nf, npos=cc['npos'], distinguishable=distinguishable, enough=enough)
    if cc['holdEV'] >= bestexitEV:
        return dict(state='HOLD', peak=peak, nf=nf, npos=cc['npos'], holdEV=cc['holdEV'], bestEV=float(bestexitEV))
    # EXIT: regime + fire xlo
    Xs = cc['Xs']; cred = s >= TAU * peak; Xc = Xs[cred]
    xlo, xhi = int(Xc.min()), int(Xc.max()); w = xhi - xlo
    fx = xlo if w > WA else int(Xs[int(np.argmax(s))])
    return dict(state='EXIT', regime='A' if w <= WA else 'B', fire_x=int(fx),
                xlo=xlo, xhi=xhi, width=w, peak=float(peak), nf=float(nf), npos=cc['npos'])

if __name__ == "__main__":
    print("="*72); print("v7 HOLD/PARK split — classify all 90 cents at T-20 floor"); print("="*72)
    C = {c: classify(c) for c in CENTS}
    cE=[c for c in CENTS if C[c]['state']=='EXIT']; cH=[c for c in CENTS if C[c]['state']=='HOLD']; cP=[c for c in CENTS if C[c]['state']=='PARK']
    print(f"EXIT={len(cE)}  HOLD={len(cH)}  PARK={len(cP)}")
    print(f"  EXIT cents: {cE}")
    print(f"  HOLD cents: {cH}")
    print(f"  PARK cents: {cP}")

    # D1: continuity among EXIT only; is c66-type (peak>>nf) ever parked?
    print("\n--- D1: within-EXIT continuity + 'is a high-conviction cell ever parked?' ---")
    exitcells=sorted(cE); wr=0
    for i in range(1,len(exitcells)):
        a,b=C[exitcells[i-1]],C[exitcells[i]]
        if exitcells[i]-exitcells[i-1]==1 and a['regime']==b['regime'] and abs(b['fire_x']-a['fire_x'])>8: wr+=1
    print(f"  within-regime adjacent jumps>8c among EXIT cells: {wr}")
    mis=[c for c in cP if C[c].get('peak',0) > 3*C[c].get('nf',1e9)]
    print(f"  high-conviction cells wrongly PARKED (peak>3x noise): {mis}  (should be EMPTY)")

    # SEAM: do npos_min and distinguishability ever disagree?
    print("\n--- SEAM: npos_min vs noise-distinguishability disagreement ---")
    dis=[]
    for c in CENTS:
        cc=cell_curve(c)
        if cc is None: continue
        nf=noise_floor(c); peak=cc['s'].max()
        d_ok = peak>nf; n_ok = cc['npos']>=NPOS_MIN
        if d_ok != n_ok: dis.append((c, 'dist' if d_ok else 'nodist', f"npos={cc['npos']}"))
    print(f"  cells where the two conditions DISAGREE: {len(dis)}")
    for d in dis[:20]: print(f"    c{d[0]}: distinguishable={d[1]}  {d[2]}")
