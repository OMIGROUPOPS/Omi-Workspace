"""
Continuous always-on per-cent blend kernel (Opus 4.8 method) + numeric diff.
Branch blend/agent-derivation. ATP_MAIN, own tape only (anchor cent, peak cent, settle).

Kernel (no gate, no CV, no sigma-grid):
  geometry:   w_c(c+-d) = exp(-d^2 / (2 b(c)^2))
  bandwidth:  b(c) = k * shat(c) * Ntarget^(-1/5),  shat = 1.4826*MAD_rel(c)
  similarity: sim(c,n) = exp(-KS(c,n)^2 / (2 h^2))
  weight:     W_c(n) = w_c(n) * sim(c,n)
  effN(c)   = (sum W*ownN)^2 / sum (W*ownN)^2          (Kish)

apples->oranges: pool relative moves m=peak-anchor with weights W_c(n);
  price each candidate X at c's OWN cost:
    kiss (m>=X) -> +X ; else settle -> +(100-c) if win else -c
  EV_c(X), hit_c(X), ROI_c(X) are weighted aggregates.

best-X (conviction-weighted, no jackpot):
  X*(c) = argmax_X EV_c(X) * paid(X) * supp(X)
    paid(X) = 1 - hit_c(X)^kp
    supp(X) = min(1, effN(c)*hit_c(X) / m0)
"""
import pandas as pd, numpy as np
from scipy import stats
rng = np.random.default_rng(7)

df = pd.read_parquet("/tmp/atp_tape.parquet")  # anchor_cent, peak_cent, settlement_value
CENTS = list(range(5,95))

def tapes(c):
    d = df[df.anchor_cent==c]
    return d.peak_cent.to_numpy(), d.settlement_value.to_numpy()

# ---- per-cell move-shape stats ----
# Spread measure must NOT collapse to 0 at favorites (where >half tapes share a move).
# Use a robust spread that stays finite: average of MAD and IQR/1.349, floored.
rel = {}; ownN = {}; SPREAD = {}
for c in CENTS:
    peak,sv = tapes(c)
    m = peak - c
    rel[c]=(m,sv); ownN[c]=len(m)
    if len(m)==0:
        SPREAD[c]=1.0; continue
    mad = np.median(np.abs(m-np.median(m)))
    iqr = np.subtract(*np.percentile(m,[75,25]))/1.349
    SPREAD[c] = max(0.5*(mad+iqr), 0.75)   # robust, never 0; favorites -> ~0.75 floor

# KS distance cache
def ksd(a,b):
    ma,_=rel[a]; mb,_=rel[b]
    if len(ma)==0 or len(mb)==0: return 1.0
    return stats.ks_2samp(ma,mb).statistic

# ---- kernel ----
NTARGET=50
def bandwidth(c,k):
    # width proportional to local move-spread; favorites (small spread) -> sharp,
    # cheap heavy-tailed (large spread) -> wider. Bounded so never a +-15c smear.
    b = k*SPREAD[c]*NTARGET**(-0.2)
    return float(np.clip(b, 0.55, 2.2))   # +-1..+-2c meaningful, never wider

def weights(c,k,h,reach=6):
    b=bandwidth(c,k); out={}
    for d in range(-reach,reach+1):
        n=c+d
        if n<5 or n>94: continue
        g=np.exp(-d*d/(2*b*b))
        s=np.exp(-ksd(c,n)**2/(2*h*h)) if d!=0 else 1.0
        out[n]=g*s
    return out

def effN(c,k,h):
    W=weights(c,k,h)
    num=sum(W[n]*ownN[n] for n in W); den=sum((W[n]*ownN[n])**2 for n in W)
    return num*num/den if den>0 else 0.0

# ---- apples->oranges pooled curve ----
def curve(c,k,h,Xs):
    W=weights(c,k,h)
    EV=np.zeros(len(Xs)); HIT=np.zeros(len(Xs)); WT=0.0
    for n,w in W.items():
        m,sv=rel[n]
        if len(m)==0: continue
        for j,X in enumerate(Xs):
            kiss=m>=X
            pnl=np.where(kiss, X, np.where(sv==1,100-c,-c)).astype(float)
            EV[j]+=w*pnl.sum(); HIT[j]+=w*kiss.sum()
        WT+=w*len(m)
    EV/=WT; HIT=HIT/WT*100
    ROI=EV/c*100
    return EV,HIT,ROI

def best_x(c,k,h,kp=2.0,m0=9.0,floor=1):
    Xs=np.arange(floor,95-c)
    if len(Xs)==0: return None
    EV,HIT,ROI=curve(c,k,h,Xs)
    eff=effN(c,k,h)
    paid=1-(HIT/100)**kp
    supp=np.minimum(1.0, eff*(HIT/100)/m0)
    score=np.where(EV>0, EV*paid*supp, -1e9)
    if not (score>-1e8).any(): return None
    i=int(np.argmax(score))
    return dict(X=int(Xs[i]),ev=float(EV[i]),hit=float(HIT[i]),roi=float(ROI[i]),
                eff=float(eff),b=float(bandwidth(c,k)))

if __name__=="__main__":
    # -------- CALIBRATE k: median cell -> +-1 weight ~0.6, +-2 ~0.15 --------
    # geometry only (sim=1 at d for the calibration of pure shape on median cell)
    import math
    # k so the MEDIAN-spread cell yields +-1 weight ~0.6  (exp(-1/(2b^2))=0.6 => b~0.99)
    b_target = math.sqrt(-1/(2*math.log(0.6)))
    spread_med = np.median([SPREAD[c] for c in CENTS])
    k = b_target/(spread_med*NTARGET**(-0.2))
    # -------- CALIBRATE h: p~0.16 neighbor (KS~0.26) keeps ~0.7; 37/38 (KS~0.36)->~0.4 --
    import math
    h = math.sqrt(-0.26**2/(2*math.log(0.7)))
    print(f"Calibrated  k={k:.3f}  h={h:.3f}  (b_target={b_target:.3f})")
    # show resulting median-cell kernel shape
    med_c=49
    W=weights(med_c,k,h); w0=W[med_c]
    print(f"median cell c={med_c} kernel (norm to own):",
          {d:round(W.get(med_c+d,0)/w0,3) for d in [-2,-1,0,1,2,3]})

    # ===== DIFF 1: does bandwidth track stability? =====
    print("\n"+"="*64)
    print("DIFF 1: bandwidth b(c) vs known stability (favorites tight, cheap wide)")
    print("="*64)
    for c in [5,7,9,12,13,38,67,89,90,91,92,93]:
        print(f"  c={c:>2} ownN={ownN[c]:>2} spread={SPREAD[c]:>4.1f} b(c)={bandwidth(c,k):>4.2f} effN={effN(c,k,h):>5.1f}")

    # ===== DIFF 2: is X*(c) smooth across cents + kills jackpots? =====
    print("\n"+"="*64)
    print("DIFF 2: X*(c) continuity + jackpot kill (5->65? 9->90? keep 12->20?)")
    print("="*64)
    res={}
    for c in CENTS:
        r=best_x(c,k,h)
        if r: res[c]=r
    for c in [5,6,7,8,9,10,11,12,13,14,15,20,38,67,88,89,90,91,92,93]:
        if c in res:
            r=res[c]; print(f"  c={c:>2}: X*=+{r['X']:>2}  ev={r['ev']:>5.2f} hit={r['hit']:>4.0f}% roi={r['roi']:>5.0f}% effN={r['eff']:>4.1f}")
    # smoothness: how many adjacent X* jumps > 8c
    xs=[res[c]['X'] for c in CENTS if c in res]
    cs=[c for c in CENTS if c in res]
    jumps=sum(1 for i in range(1,len(xs)) if abs(xs[i]-xs[i-1])>8)
    print(f"  adjacent-cent X* jumps >8c: {jumps} of {len(xs)-1}")

    # ===== DIFF 3: 37/38 continuous down-weight recovers $ vs blind pool? =====
    print("\n"+"="*64)
    print("DIFF 3: 37/38 soft down-weight vs blind pool (constituent +$39.90 truth)")
    print("="*64)
    print(f"  sim(37,38)={np.exp(-ksd(37,38)**2/(2*h*h)):.2f}  (Opus target ~0.4)")
    def dollars(c,X):
        m,sv=rel[c]
        return np.where(m>=X,X,np.where(sv==1,100-c,-c)).sum()/100*10
    r37=res.get(37); r38=res.get(38)
    if r37 and r38:
        print(f"  blended X*: 37->+{r37['X']} (${dollars(37,r37['X']):+.2f}), 38->+{r38['X']} (${dollars(38,r38['X']):+.2f})  sum=${dollars(37,r37['X'])+dollars(38,r38['X']):+.2f}")
