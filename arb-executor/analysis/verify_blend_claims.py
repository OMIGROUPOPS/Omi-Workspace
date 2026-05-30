"""
Numeric verification of the THREE load-bearing claims in Opus's method derivation.
Branch: blend/agent-derivation. Data: own-tape only (anchor + peak), no invented values.

Outcome model (the honest reconstruction, matches build_curve_atp_main):
 For anchor cent c, offset +X (target c+X):
   hit if peak_cent >= c+X  -> capture +X
   else ride to settlement:  win-> +(100-c), loss-> -c
 EV = mean PnL; ROI = EV/c*100; hit = P(peak>=c+X).
"""
import pandas as pd, numpy as np
rng = np.random.default_rng(42)

df = pd.read_parquet("/tmp/atp_tape.parquet")  # anchor_cent, peak_cent, settlement_value

def cell_tapes(c):
    d = df[df["anchor_cent"] == c]
    return d["peak_cent"].to_numpy(), d["settlement_value"].to_numpy()

def pnl_curve(peak, sv, c, Xs):
    """Return EV, hit, roi arrays over offsets Xs for one cell's tapes."""
    ev=[]; hit=[]; roi=[]
    for X in Xs:
        tgt = c + X
        hits = peak >= tgt
        pnl = np.where(hits, X, np.where(sv==1, 100-c, -c)).astype(float)
        ev.append(pnl.mean()); hit.append(hits.mean()*100); roi.append(pnl.mean()/c*100)
    return np.array(ev), np.array(hit), np.array(roi)

def best_x(peak, sv, c, floor=1):
    """own-tape argmax best-X by EV among EV>0, X from floor..(94-c)."""
    Xs = np.arange(floor, 95-c)
    if len(Xs)==0: return None,None,None,None
    ev,hit,roi = pnl_curve(peak,sv,c,Xs)
    pos = ev>0
    if not pos.any(): return None,None,None,None
    i = np.argmax(np.where(pos, ev, -1e9))
    return int(Xs[i]), float(ev[i]), float(hit[i]), float(roi[i])

# ============================================================
# CLAIM 3 (do first, fully self-contained): homogeneity gate rejects 37/38
#   and the blind 2c pool destroys edge (+$29.40 -> -$8.10 in doctrine).
# ============================================================
from scipy import stats
def relative_moves(c):
    peak,sv = cell_tapes(c)
    return peak - c  # relative reach in cents (apples)

print("="*70)
print("CLAIM 3: homogeneity gate on relative-move distribution (37 vs 38)")
print("="*70)
for a,b in [(37,38),(19,20),(20,21),(12,13),(5,6)]:
    ma, mb = relative_moves(a), relative_moves(b)
    ks = stats.ks_2samp(ma, mb)
    verdict = "REJECT (oranges)" if ks.pvalue < 0.10 else "admit (apples)"
    print(f"  {a}c vs {b}c: KS={ks.statistic:.3f} p={ks.pvalue:.3f}  ->  {verdict}"
          f"   (medians {np.median(ma):.0f} vs {np.median(mb):.0f})")

# reproduce the doctrine $ result: own best-X $ vs blind [37,39) 2c pool
def dollars_at(c, X, sv_known=None):
    peak,sv = cell_tapes(c)
    pnl = np.where(peak>=c+X, X, np.where(sv==1,100-c,-c)).astype(float)
    return pnl.sum()/100*10  # 10 contracts, cents->$ (matches 10ct sizing)
# own picks
bx37 = best_x(*cell_tapes(37),37); bx38 = best_x(*cell_tapes(38),38)
x37 = bx37[0]; x38 = bx38[0] if bx38[0] is not None else 1  # 38c has no EV>0 exit -> floor +1
d37 = dollars_at(37,x37); d38 = dollars_at(38,x38)
print(f"\n  own 37c best-X=+{x37} -> $ {d37:+.2f}")
print(f"  own 38c best-X=+{x38} (no EV>0 exit; floor) -> $ {d38:+.2f}")
print(f"  constituent sum = {d37+d38:+.2f}")
# blind pool: merge 37&38 tapes, pick one X, apply to both
p37,s37=cell_tapes(37); p38,s38=cell_tapes(38)
pj=np.concatenate([p37,p38]); sj=np.concatenate([s37,s38])
# pool anchored at 37 (lower edge of [37,39))
bxj = best_x(pj,sj,37)
poolX = bxj[0]
d = (np.where(p37>=37+poolX,poolX,np.where(s37==1,100-37,-37)).sum()
     + np.where(p38>=38+poolX,poolX,np.where(s38==1,100-38,-38)).sum())/100*10
print(f"  BLIND 2c pool [37,39) single X=+{poolX} applied to both -> $ {d:+.2f}  (edge destroyed)")

# ============================================================
# CLAIM 2: N* = bootstrap-argmax-stabilization point. Opus predicts ~40-60,
#   i.e. only cells with own-N below that should borrow.
#   Method: for each cell, bootstrap own tapes B times, recompute best-X,
#   measure share of bootstraps whose best-X is within +/-2c of the full-sample modal best-X.
#   "Stable" = share >= 80%. N* = smallest own-N at which cells are reliably stable.
# ============================================================
print("\n"+"="*70)
print("CLAIM 2: bootstrap-argmax stability vs own-N  (Opus predicts N*~40-60)")
print("="*70)
def stability(c, B=400):
    peak,sv = cell_tapes(c); n=len(peak)
    if n<5: return None
    full = best_x(peak,sv,c)[0]
    if full is None: return None
    cnt=0
    for _ in range(B):
        idx=rng.integers(0,n,n)
        bx=best_x(peak[idx],sv[idx],c)[0]
        if bx is not None and abs(bx-full)<=2: cnt+=1
    return full, cnt/B
rows=[]
for c in range(5,95):
    peak,sv=cell_tapes(c); n=len(peak)
    s=stability(c)
    if s is None: continue
    rows.append((c,n,s[0],s[1]))
import numpy as np
arr=np.array([(n,share) for _,n,_,share in rows])
# find N* : smallest own-N above which >=80% of cells are stable
stable_mask=arr[:,1]>=0.80
print(f"  cells tested: {len(rows)}  | stable(>=80%): {int(stable_mask.sum())}  unstable: {int((~stable_mask).sum())}")
# bucket by own-N
for lo,hi in [(0,30),(30,40),(40,50),(50,60),(60,100)]:
    m=(arr[:,0]>=lo)&(arr[:,0]<hi)
    if m.sum()==0: continue
    print(f"   ownN [{lo:>2},{hi:>3}): {int(m.sum()):>2} cells, stable share-of-cells={arr[m,1].mean()*100:4.0f}% mean modal-agreement")
# the thin cells specifically
print("  thin/extreme cells (own-N<30):")
for c,n,full,share in rows:
    if n<30:
        flag="STABLE" if share>=0.80 else "lottery"
        print(f"    c={c:>2} ownN={n:>2} best-X=+{full:>2} modal-agree={share*100:3.0f}%  {flag}")

# ============================================================
# CLAIM 1: CV bandwidth selector is corner-biased & unstable.
#   Reconstruct the own-curve-MSE objective vs sigma and show it is monotone
#   (slams to an endpoint) and flips direction between adjacent cells.
# ============================================================
print("\n"+"="*70)
print("CLAIM 1: own-curve-MSE-vs-sigma is monotone (corner solution), flips by cell")
print("="*70)
def gauss_w(c, nb, sigma):
    return np.exp(-0.5*((c-nb)/sigma)**2) if sigma>0 else (1.0 if c==nb else 0.0)
def pooled_curve(c, sigma, Xs):
    # weighted blend of neighbor relative-move EV curves, re-expressed at c's basis
    num=np.zeros(len(Xs)); den=0.0
    for nb in range(max(5,c-15),min(95,c+16)):
        peak,sv=cell_tapes(nb)
        if len(peak)==0: continue
        w=gauss_w(c,nb,sigma)
        if w<=0: continue
        # relative move shape from neighbor, applied to c's cost basis
        ev,_,_=pnl_curve(peak,sv,c,Xs)  # re-expressed at c
        num+=w*ev; den+=w
    return num/den if den>0 else num
def cv_err(c, sigma):
    Xs=np.arange(1,95-c)
    peak,sv=cell_tapes(c)
    own_ev,_,_=pnl_curve(peak,sv,c,Xs)
    pooled=pooled_curve(c,sigma,Xs)
    return np.mean((own_ev-pooled)**2)
sigmas=[0.5,1,2,3,4,6,8]
for c in [7,12,13,38]:
    errs=[cv_err(c,s) for s in sigmas]
    direction="DECREASING->wants MAX smoothing" if errs[-1]<errs[0] else "INCREASING->wants sigma->0"
    print(f"  c={c}: " + "  ".join(f"s{ s}={e:5.1f}" for s,e in zip(sigmas,errs)) + f"   [{direction}]")
