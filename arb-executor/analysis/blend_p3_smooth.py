"""
P3 ROOT-CAUSE FIX — continuous mode-selection.
Branch blend/agent-derivation.

Established (DIFF v4): the discontinuity is upstream of readout shape. It's the HARD
tau=0.7 credible cliff on a near-flat noisy score: a ~1% wobble flips which mode
(low-bank vs high-reach) clears tau, yanking xlo/argmax cent-to-cent.

Two fixes, both prototyped here, diffed against the within-regime flips
(c65/66/67=+1/+28/+2, c49/50=+11/+34, c39/40=+7/+29):

  (A) SMOOTH-ACROSS-CENTS: build the full score surface S[c, X], smooth along the
      c-axis (rolling median window=ws) so a single cell's mode can't flip on its own
      noise — it must agree with its neighbors. Then read xlo off the smoothed score.

  (B) SOFT-TAU: replace hard (s >= tau*max) membership with a sigmoid credible weight
      cw(X) = sigmoid((s - tau*max)/(beta*max)). xlo = lowest X with cw >= 0.5.
      As the low mode's relative weight rises/falls, xlo drifts continuously.

Doctrine call (agent, not capping): c20's genuine reach (+37) is REAL signal in a sea
of bank cents; we do NOT hard-cap the cheap zone. Continuous selection decides.

Target: within-regime jumps -> <4, all at true A<->B boundaries; cheap-zone xlo monotone.
"""
import numpy as np
from blend_continuous import CENTS, curve, effN, SE

K, H = 0.215, 2.006
WA, WB = 3, 12
KP, M0, FLOOR, TAU = 2.0, 1.2, 1, 0.7

# ---- build the raw score curve s_c(X) for every cent (the object both fixes operate on) ----
def score_curve(c):
    Xs = np.arange(FLOOR, 95 - c)
    if len(Xs) == 0:
        return Xs, np.array([])
    EV, HIT, ROI = curve(c, K, H, Xs)
    se = SE(c, K, H)
    paid = 1 - (HIT / 100) ** KP
    supp = np.minimum(1.0, (HIT / 100) / (M0 * se))
    s = np.where(EV > 0, EV * paid * supp, 0.0)
    return Xs, s, EV, HIT, ROI

RAW = {}
for c in CENTS:
    out = score_curve(c)
    if len(out[0]) > 0:
        Xs, s, EV, HIT, ROI = out
        RAW[c] = dict(Xs=Xs, s=s, EV=EV, HIT=HIT, ROI=ROI)

# ---------- FIX A: smooth the score surface ALONG the c-axis ----------
def smooth_across_cents(ws=3):
    """For each X offset, take rolling-median of score across neighboring cents.
    A cell's mode must agree with neighbors to survive -> kills 1-cell noise flips."""
    cs = sorted(RAW.keys())
    smoothed = {c: RAW[c]['s'].copy() for c in cs}
    half = ws // 2
    for ci, c in enumerate(cs):
        Xs = RAW[c]['Xs']
        for j, X in enumerate(Xs):
            vals = []
            for dc in range(-half, half + 1):
                cc = c + dc
                if cc in RAW:
                    Xs2 = RAW[cc]['Xs']
                    idx = np.where(Xs2 == X)[0]
                    if len(idx):
                        vals.append(RAW[cc]['s'][idx[0]])
            if vals:
                smoothed[c][j] = np.median(vals)
    return smoothed

def readout_smoothA(ws=3, tau=TAU):
    sm = smooth_across_cents(ws)
    R = {}
    for c in sorted(RAW.keys()):
        Xs = RAW[c]['Xs']; s = sm[c]
        if s.max() <= 0:
            R[c] = dict(regime="C", xlo=None, fire_x=None, width=None); continue
        cred = s >= tau * s.max()
        Xc = Xs[cred]; xlo, xhi = int(Xc.min()), int(Xc.max()); w = xhi - xlo
        argmax_x = int(Xs[int(np.argmax(s))])
        regime = "A" if w <= WA else "B"
        fire_x = argmax_x if regime == "A" else xlo
        R[c] = dict(regime=regime, xlo=xlo, xhi=xhi, width=w, fire_x=int(fire_x), argmax_x=argmax_x)
    return R

# ---------- FIX B: soft-tau sigmoid credible weight ----------
def readout_softB(beta=0.12, thresh=0.5):
    R = {}
    for c in sorted(RAW.keys()):
        Xs = RAW[c]['Xs']; s = RAW[c]['s']
        if s.max() <= 0:
            R[c] = dict(regime="C", xlo=None, fire_x=None, width=None); continue
        mx = s.max()
        cw = 1.0 / (1.0 + np.exp(-(s - TAU * mx) / (beta * mx)))  # soft membership
        inb = cw >= thresh
        if not inb.any():
            R[c] = dict(regime="C", xlo=None, fire_x=None, width=None); continue
        Xc = Xs[inb]; xlo, xhi = int(Xc.min()), int(Xc.max()); w = xhi - xlo
        argmax_x = int(Xs[int(np.argmax(s))])
        regime = "A" if w <= WA else "B"
        fire_x = argmax_x if regime == "A" else xlo
        R[c] = dict(regime=regime, xlo=xlo, xhi=xhi, width=w, fire_x=int(fire_x), argmax_x=argmax_x)
    return R

# ---------- scoring helpers ----------
WATCH = [(65,66),(66,67),(49,50),(45,46),(39,40),(19,20),(20,21)]  # the v4 within-regime flips
def metrics(R, label):
    cs = sorted(R.keys())
    # same-regime, C-excluded adjacency jumps>8c
    wr = []
    for i in range(1, len(cs)):
        a, b = R[cs[i-1]], R[cs[i]]
        if a['regime']=='C' or b['regime']=='C': continue
        if a['regime']==b['regime'] and abs(b['fire_x']-a['fire_x'])>8:
            wr.append((cs[i-1],cs[i],a['fire_x'],b['fire_x'],a['regime']))
    # cheap-zone xlo monotone-ish (jumps>5c c5-30)
    cheap=[c for c in range(5,31) if c in R and R[c]['regime']!='C']
    cj=sum(1 for i in range(1,len(cheap)) if abs(R[cheap[i]]['fire_x']-R[cheap[i-1]]['fire_x'])>5)
    print(f"\n--- {label} ---")
    print(f"  within-regime jumps>8c (C-excl): {len(wr)}")
    for j in wr: print(f"     c{j[0]}->c{j[1]}: +{j[2]}->+{j[3]} (regime {j[4]})")
    print(f"  cheap-zone c5-30 fire_x jumps>5c: {cj}")
    print(f"  watched v4 flips now: " + " ".join(
        f"c{a}->{b}:{R[a]['fire_x'] if R[a]['regime']!='C' else 'H'}->{R[b]['fire_x'] if R[b]['regime']!='C' else 'H'}"
        for a,b in WATCH if a in R and b in R))
    return len(wr), cj

if __name__=="__main__":
    print("="*70); print("P3 ROOT-CAUSE FIX: continuous mode-selection — A vs B"); print("="*70)
    print("baseline (v4 hard-tau, fire-xlo): within-regime=11, cheap>5c=5")

    best=None
    for ws in (3,5):
        Ra=readout_smoothA(ws=ws)
        wr,cj=metrics(Ra, f"FIX A smooth-across-cents ws={ws}")
        if best is None or (wr,cj)<best[0]: best=((wr,cj),f"A ws={ws}",Ra)
    for beta in (0.08,0.12,0.20):
        Rb=readout_softB(beta=beta)
        wr,cj=metrics(Rb, f"FIX B soft-tau beta={beta}")
        if (wr,cj)<best[0]: best=((wr,cj),f"B beta={beta}",Rb)

    print("\n"+"="*70)
    print(f"WINNER: {best[1]}  -> within-regime jumps>8c={best[0][0]}, cheap>5c={best[0][1]}")
    print("="*70)
    R=best[2]
    print("\ncheap-zone fire ladder (winner):")
    for c in range(5,31):
        if c in R:
            r=R[c]
            print(f"  c{c:>2}: "+("HOLD" if r['regime']=='C' else f"+{r['fire_x']:>2} ({r['regime']}, w={r['width']})"))
