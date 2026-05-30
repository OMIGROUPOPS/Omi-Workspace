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

R0=3.0   # distance-taper scale for similarity (Opus: 1+|d|/r0)
def weights(c,k,h,reach=6,symmetrize=True):
    b=bandwidth(c,k); raw={}
    for d in range(-reach,reach+1):
        n=c+d
        if n<5 or n>94: continue
        g=np.exp(-d*d/(2*b*b))
        # distance-tapered KS so a single noisy far/adjacent KS can't skew one side
        s=np.exp(-(ksd(c,n)*(1+abs(d)/R0))**2/(2*h*h)) if d!=0 else 1.0
        raw[n]=g*s
    if not symmetrize: return raw
    # symmetrize magnitude across +-d (keep each neighbor's own tapes via its key)
    out={}
    for d in range(-reach,reach+1):
        n=c+d
        if n not in raw: continue
        m=c-d
        if m in raw and d!=0:
            out[n]=0.5*(raw[n]+raw[m])
        else:
            out[n]=raw[n]
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

def SE(c,k,h):
    eff=effN(c,k,h)
    return SPREAD[c]/np.sqrt(max(eff,1e-9))   # standard-error of the move (Opus)

def best_x(c,k,h,kp=2.0,m0=1.2,floor=1,tau=0.7):
    """Conviction-weighted CENTROID over credible region (>=tau*peak), not argmax.
    supp keys off SE(c) so favorites (tight spread) clear support on own tape and
    cheap cells must earn it via effN depth."""
    Xs=np.arange(floor,95-c)
    if len(Xs)==0: return None
    EV,HIT,ROI=curve(c,k,h,Xs)
    eff=effN(c,k,h); se=SE(c,k,h)
    paid=1-(HIT/100)**kp
    supp=np.minimum(1.0, (HIT/100)/(m0*se))      # SE-based support
    s=np.where(EV>0, EV*paid*supp, 0.0)
    if s.max()<=0: return None
    cred = s >= tau*s.max()                       # credible region
    Xc = Xs[cred]; sc = s[cred]
    xstar = float(np.sum(Xc*sc)/np.sum(sc))       # centroid readout
    xlo,xhi = int(Xc.min()), int(Xc.max())        # conviction width
    # report EV/hit/roi at the centroid X (nearest integer offset)
    i = int(np.argmin(np.abs(Xs-xstar)))
    return dict(X=round(xstar,1),Xint=int(Xs[i]),xlo=xlo,xhi=xhi,width=xhi-xlo,
                ev=float(EV[i]),hit=float(HIT[i]),roi=float(ROI[i]),
                eff=float(eff),se=float(se),b=float(bandwidth(c,k)))

if __name__=="__main__":
    from scipy.optimize import minimize
    import numpy as np
    # ---- JOINT (k,h) fit to median realized W(+-1)/W(0)=0.60, W(+-2)/W(0)=0.15 ----
    def realized_ratios(k,h):
        r1=[]; r2=[]
        for c in CENTS:
            W=weights(c,k,h); w0=W.get(c,0)
            if w0<=0: continue
            a1=[W[c+d]/w0 for d in (-1,1) if c+d in W]
            a2=[W[c+d]/w0 for d in (-2,2) if c+d in W]
            if a1: r1.append(np.mean(a1))
            if a2: r2.append(np.mean(a2))
        return np.median(r1), np.median(r2)
    def obj(p):
        k,h=p
        if k<=0 or h<=0: return 1e9
        m1,m2=realized_ratios(k,h)
        return (m1-0.60)**2 + (m2-0.15)**2
    res=minimize(obj,[0.3,0.4],method="Nelder-Mead",
                 options=dict(xatol=1e-3,fatol=1e-6,maxiter=400))
    k,h=res.x
    m1,m2=realized_ratios(k,h)
    print(f"JOINT FIT  k={k:.3f} h={h:.3f}  -> realized median +-1={m1:.3f} (t0.60)  +-2={m2:.3f} (t0.15)")
    # symmetry check on median cell
    W=weights(49,k,h); w0=W[49]
    asym=abs(W.get(48,0)-W.get(50,0))/w0*100
    print(f"  c=49 kernel norm: " + " ".join(f"{d:+d}:{W.get(49+d,0)/w0:.3f}" for d in [-2,-1,0,1,2]) + f"   asym={asym:.1f}%")

    # ===== DIFF A: continuity — centroid readout, count >8c jumps =====
    print("\n"+"="*64); print("DIFF A: centroid X*(c) continuity (target: jumps>8c -> single digits)"); print("="*64)
    res_x={}
    for c in CENTS:
        r=best_x(c,k,h)
        if r: res_x[c]=r
    cs=[c for c in CENTS if c in res_x]; xs=[res_x[c]["X"] for c in cs]
    jumps=sum(1 for i in range(1,len(xs)) if abs(xs[i]-xs[i-1])>8)
    print(f"  adjacent-cent X* jumps >8c: {jumps} of {len(xs)-1}   (was 27)")
    for c in [5,6,7,8,9,10,11,12,13,14,15,20,38,67,88,89,90,91,92,93]:
        if c in res_x:
            r=res_x[c]; print(f"  c={c:>2}: X*=+{r['X']:>4}  [{r['xlo']:>2},{r['xhi']:>2}] w={r['width']:>2} hit={r['hit']:>3.0f}% roi={r['roi']:>4.0f}% effN={r['eff']:>4.1f} SE={r['se']:>4.1f}")

    # ===== DIFF B: SE-supp leaves favorites convicted, kills 5->65 =====
    print("\n"+"="*64); print("DIFF B: favorites convicted (supp~1 own tape) AND 5c jackpot killed"); print("="*64)
    for c in [5,9,89,90,92]:
        r=best_x(c,k,h)
        Xs=np.arange(1,95-c); EV,HIT,ROI=curve(c,k,h,Xs); se=SE(c,k,h)
        supp=np.minimum(1.0,(HIT/100)/(1.2*se))
        print(f"  c={c:>2}: X*=+{r['X']}  SE={se:.2f}  max-supp={supp.max():.2f}  (5/9 should NOT reach +65/+90)")

    # ===== DIFF C: joint kernel symmetric at median, favorites sharper =====
    print("\n"+"="*64); print("DIFF C: median symmetric 0.6/0.15; favorites sharper by design"); print("="*64)
    for c in [9,49,90]:
        W=weights(c,k,h); w0=W[c]
        r1=np.mean([W.get(c+d,0)/w0 for d in(-1,1)])
        print(f"  c={c:>2} spread={SPREAD[c]:>4.1f} b={bandwidth(c,k):.2f}  +-1 weight={r1:.3f}")
