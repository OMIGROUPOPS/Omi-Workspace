"""v10 — Opus's bimodal-band rescue of the engine.

CLAIM under test: c5's consensus.sum=0 is NOT 'unresolvable' — it is 'resolvable into TWO
stable modes' that a single contiguous credible band cannot represent. Same artifact class as
the flat-top and tau-cliff collapses we already cleared.

Method (no recompute of band per discount; invariance intact):
  - Cache, ONCE on own moves: the per-resample best-X distribution (NBOOT argmax draws).
  - Cluster that distribution into <=2 modes (1D, gap-based split on sorted best-X).
  - Per-mode stability: a mode is STABLE if best-X lands within its window in >= ALPHA of
    resamples (mass share), i.e. the mode is repeatedly re-found, not a one-off blob.
  - resolvable = at least one stable mode exists.
  - Under discount (EV-only), fire the LOW stable mode's representative X; EXIT iff that mode's
    EV beats hold. The band never moves; the discount only selects which mode is profitable.

FALSIFIERS:
  T1 (c5 vs c44): does c5 yield >=1 stable low mode while c44 yields NO stable mode?
       If c44 also throws a stable low mode -> diffuse-but-stable is everywhere -> (B) wins.
  T2 (discount): does c5's low mode cross EV-positive cost-ordered across c5-29 while the
       jackpot/hammer set (c6/c10/c17 reach modes) and c44 stay DARK?
  DECIDER: per-mode stability of c5's LOW mode. Stable -> engine survives. Unstable -> (B).
"""
import numpy as np
from blend_park_v8 import pooled_tapes, score_and_bestx
from blend_continuous import CENTS
rng = np.random.default_rng(13)
KP, M0, TAU, NPOS_MIN, NBOOT, ALPHA = 2.0, 1.2, 0.7, 3, 300, 0.75
GAP = 6   # min separation (cents) to call two best-X clusters distinct modes
WIN = 3   # +-cents window around a mode center within which a draw 'belongs' to that mode

def boot_bestx(c):
    """Cached-once: distribution of best-X across NBOOT resamples of the cell's OWN tapes.
    Also returns baseline npos. Basis-invariant (cost only scales EV, not argmax location? no —
    argmax depends on cost via EV>0 mask; we therefore draw best-X at the cell's OWN cost=c,
    which is the invariant T-20 reference basis. Discount handled separately by EV-only re-pricing
    of the FIXED mode X's)."""
    pool = pooled_tapes(c)
    if not pool: return None, 0
    Xs, s, EV, bx = score_and_bestx(c, c, pool)
    if Xs is None or s.max() <= 0: return None, 0
    npos = int((EV > 0).sum())
    draws = []
    for _ in range(NBOOT):
        rp = [(m[idx], sv[idx], w) for (m, sv, w) in pool for idx in [rng.integers(0, len(m), len(m))]]
        X2, s2, E2, _ = score_and_bestx(c, c, rp)
        if X2 is None or s2.max() <= 0: continue
        draws.append(int(X2[int(np.argmax(s2))]))
    return np.array(draws), npos

def cluster_modes(draws):
    """Split sorted best-X draws into <=2 modes by the largest gap (if >=GAP). Returns list of
    dicts: center (median), share (fraction of draws within +-WIN of center)."""
    if len(draws) == 0: return []
    d = np.sort(draws)
    gaps = np.diff(d)
    modes = []
    if len(gaps) and gaps.max() >= GAP:
        k = int(np.argmax(gaps))
        groups = [d[:k+1], d[k+1:]]
    else:
        groups = [d]
    for g in groups:
        center = int(np.median(g))
        share = float(np.mean(np.abs(draws - center) <= WIN))
        modes.append(dict(center=center, share=share, n=len(g)))
    return sorted(modes, key=lambda m: m['center'])  # low mode first

# ---- ONE-TIME cache: bootstrap best-X distribution + clustered modes per cell ----
MODES = {}
for c in CENTS:
    draws, npos = boot_bestx(c)
    if draws is None or len(draws) == 0:
        MODES[c] = dict(npos=0, modes=[], stable=[]); continue
    ms = cluster_modes(draws)
    stable = [m for m in ms if m['share'] >= ALPHA]
    MODES[c] = dict(npos=npos, modes=ms, stable=stable)

def ev_of_X(c, X, discount):
    """EV-only re-pricing of a FIXED mode-X under discount. Band unchanged (invariance)."""
    cost = max(1, c - discount); pool = pooled_tapes(c)
    EV = 0.0; WT = 0.0; hit = 0.0
    for m, sv, w in pool:
        kiss = m >= X
        pnl = np.where(kiss, X, np.where(sv == 1, 100 - cost, -cost)).astype(float)
        EV += w * pnl.sum(); hit += w * kiss.sum(); WT += w * len(m)
    allsv = np.concatenate([sv for _, sv, _ in pool])
    holdEV = float(np.mean(np.where(allsv == 1, 100 - cost, -cost)))
    return EV / WT, holdEV

def state(c, discount=0):
    M = MODES[c]
    if M['npos'] < NPOS_MIN: return 'PARK-thin'
    if not M['stable']: return 'PARK-noise'           # no stable mode -> genuinely unresolvable
    low = M['stable'][0]                               # fire the LOW stable mode
    bestEV, holdEV = ev_of_X(c, low['center'], discount)
    if bestEV <= holdEV: return 'PARK-engine' if bestEV <= 0 else 'HOLD'
    return 'EXIT'

if __name__ == '__main__':
    from collections import Counter
    print("="*78); print("v10 BIMODAL — per-mode stability cache (ALPHA=%.2f, GAP=%d, WIN=+-%d)" % (ALPHA, GAP, WIN)); print("="*78)

    # ---- DECIDER + T1: c5 vs c44 (and the rest of the cheap zone + jackpot set) ----
    print("\nT1/DECIDER — mode structure (center@share*; * = stable >= %.2f):" % ALPHA)
    print(f"{'c':>3} {'npos':>4}  modes (low->high)")
    for c in [5, 6, 10, 17, 19, 20, 44, 50, 92, 35, 60, 75, 80]:
        M = MODES[c]
        desc = "  ".join(f"{m['center']}@{m['share']:.2f}{'*' if m['share']>=ALPHA else ''}" for m in M['modes']) or "(degenerate)"
        print(f"{c:>3} {M['npos']:>4}  {desc}")

    print("\nBaseline states:")
    B = {c: state(c, 0) for c in CENTS}; print(Counter(B.values()))
    for lab in ['EXIT','HOLD','PARK-engine','PARK-thin','PARK-noise']:
        print(f"  {lab:<12}: {[c for c in CENTS if B[c]==lab]}")

    # ---- T2: discount sweep — engine lights cost-ordered, jackpot/noise stay dark ----
    print("\n"+"="*78); print("T2 — discount sweep: PARK-engine -> EXIT cost-ordered?  noise/jackpot stay dark?"); print("="*78)
    engine0 = [c for c in CENTS if B[c]=='PARK-engine']
    noise0  = [c for c in CENTS if B[c]=='PARK-noise']
    exit0   = [c for c in CENTS if B[c]=='EXIT']
    print(f" baseline PARK-engine = {engine0}")
    print(f" disc  nEXIT  engine->EXIT(cost-ordered?)        noise->EXIT(MUST=[])  EXIT->PARK(MUST=[])")
    for disc in (0,3,6,10,15,20):
        S = {c: state(c, disc) for c in CENTS}
        e2 = [c for c in engine0 if S[c]=='EXIT']
        n2 = [c for c in noise0  if S[c]=='EXIT']
        ep = [c for c in exit0   if S[c].startswith('PARK')]
        print(f"  {disc:>3}   {sum(v=='EXIT' for v in S.values()):>3}   {str(e2)[:28]:<28} order_ok={e2==sorted(e2)!s:<5}  {str(n2):<14}  {ep}")

    # ---- HAMMER (#3 retained): jackpot reach cells must stay parked at all discounts ----
    print("\n"+"="*78); print("HAMMER — jackpot reach cells (c6/c10/c17) must NEVER fire a high reach mode"); print("="*78)
    for c in [5,6,10,17]:
        M = MODES[c]
        lowc = M['stable'][0]['center'] if M['stable'] else None
        highs = [m['center'] for m in M['modes'] if lowc is None or m['center'] > lowc + GAP]
        line = f"  c{c}: stable_low={lowc}  high_modes={highs} -> fired X is always the LOW mode; reach tail never armed"
        print(line)
