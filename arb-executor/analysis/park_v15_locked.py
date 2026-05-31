"""v15 — seam-5 LOCKED. GAP-based <=2-mode clustering REPLACED by a mode-count-free peak readout.

WHY (seam 5): GAP=6 sat in a populated region and made exactly ONE cut, so it could not isolate a
sharp bankable LOW mode from a tri-modal cell (c13: real low mode X=11, cond 0.90, +2.7c, was merged
into the X=24 mid mode and wrongly parked). The fix is to drop the fixed mode count entirely and read
the bootstrap best-X density directly: scan its peaks low->high and fire the LOWEST peak that is a real
mode AND clears the (unchanged) tradeability gate.

GATE STACK (each on its own CAUSE; none is an SE-relative margin -> no third-decimal wobble):
  cond >= FLOOR        resolvability   ("when I look, is the center the same?") -- per-mode, v14.
  occ  >= MIN_OCC      prominence      ("is this a mode or a shoulder-bump?") -- the seam-5 fix.
  EV_fire > holdEV     beat-settling.
  hit >= be + M_CUSHION*(1-occ*cond)   rate-sanity + SAFETY (this is what parks the c44 noise smear;
                                       it is LOAD-BEARING and stays BINDING -- demoting it fires c44).
  EV_fire >= EV_VETO   magnitude       ("is it worth trading?") -- LOW secondary veto, drops the one
                                       bank-nothing exit (c38 @ +0.08c). Plateau-flat over [0.25,0.75]c.

FALSIFIED en route (kept as scar tissue): (a) mse / margin-in-SE floor -> kills ballast (thin margin
over a high breakeven; the seam-3 wall). (b) absolute-EV as the PRIMARY gate (E_min~1c) -> breaks c44
AND parks legitimate cheap-certain exits (c72 0.88c); EV is a continuum with no high gap, so a high
E_min just relocates the wobble. The cheap-end disqualification (c38) and the high-hit-crumb
disqualification are BOTH "doesn't pay", caught here by EV_VETO (cents) and cushion (rate) respectively.

Lock params: B(NBOOT)=1000, smooth=2, MIN_OCC=0.10, EV_VETO=0.50, FLOOR=0.50, M_CUSHION=0.15, WIN=3.
Stability: c44 PARK at every B and smooth; c13->X11 at every B/smooth; EXIT-set smooth{1,2}-stable to
within 1 immaterial cell (c29, banks ~4c at a coin-flip hit margin = the labeled risk dial).
"""
import numpy as np
from blend_park_v8 import pooled_tapes, score_and_bestx
from blend_continuous import CENTS
rng = np.random.default_rng(13)
KP, M0, TAU, NPOS_MIN = 2.0, 1.2, 0.7, 3
NBOOT = 1000                 # v15: B>=1000 (B=300 under-resolved c12; sharpens the density)
WIN = 3
FLOOR = 0.50                 # per-mode cond floor (resolvability firewall; the CAUSE). v14, unchanged.
M_CUSHION = 0.15             # LABELED risk dial; rate-sanity + safety (parks c44). BINDING. v14, unchanged.
MIN_OCC = 0.10               # SEAM-5 FIX: peak prominence floor. Flat plateau [0.08,0.20].
EV_VETO = 0.50               # secondary magnitude veto (cents). Flat plateau [0.25,0.75]. Drops null exits.
SMOOTH = 2                   # histogram smoothing half-window. Cap at 2 (smooth=3 over-merges modes).

def boot_draws(c):
    """Bootstrap best-X draws on OWN moves. Returns (draws array, npos)."""
    pool = pooled_tapes(c)
    if not pool: return None, 0
    Xs, s, EV, bx = score_and_bestx(c, c, pool)
    if Xs is None or s.max() <= 0: return None, 0
    npos = int((EV > 0).sum()); d = []
    for _ in range(NBOOT):
        rp = [(m[idx], sv[idx], w) for (m, sv, w) in pool for idx in [rng.integers(0, len(m), len(m))]]
        X2, s2, E2, _ = score_and_bestx(c, c, rp)
        if X2 is None or s2.max() <= 0: continue
        d.append(int(X2[int(np.argmax(s2))]))
    return (np.array(d), npos) if d else (None, npos)

def peaks_lowtohigh(draws, smooth=SMOOTH):
    """Valley-segmented local-maxima of the smoothed integer-cent histogram, ascending by center.
    Each peak -> (center=cluster median, cluster boolean mask)."""
    lo, hi = int(draws.min()), int(draws.max())
    grid = np.arange(lo, hi + 1)
    hist = np.array([(draws == x).sum() for x in grid], float)
    if smooth > 0:
        k = np.ones(2 * smooth + 1) / (2 * smooth + 1)
        hist = np.convolve(hist, k, mode='same')
    peakidx = [i for i in range(len(grid)) if hist[i] > 0 and
               (i == 0 or hist[i] >= hist[i - 1]) and (i == len(grid) - 1 or hist[i] >= hist[i + 1])]
    centers = [int(grid[i]) for i in peakidx]
    bounds = [lo]
    for a, b in zip(centers, centers[1:]):
        seg = (grid >= a) & (grid <= b); idxs = np.where(seg)[0]
        bounds.append(int(grid[idxs[np.argmin(hist[idxs])]]))
    bounds.append(hi + 1)
    clusters = []
    for j, ctr in enumerate(centers):
        a, b = bounds[j], bounds[j + 1]
        mask = (draws >= a) & (draws < b) if j < len(centers) - 1 else (draws >= a) & (draws <= hi)
        if mask.sum() == 0: continue
        clusters.append((int(np.median(draws[mask])), mask))
    seen = set(); out = []
    for ctr, mask in sorted(clusters, key=lambda z: z[0]):
        if ctr in seen: continue
        seen.add(ctr); out.append((ctr, mask))
    return out

# cache draws once per cell
CACHE = {}
for c in CENTS:
    CACHE[c] = boot_draws(c)

def fired_breakeven(c, X, discount=0):
    """Derived per-cent breakeven: smallest hit making EV_fire>=holdEV, from OWN cost geometry +
    empirical miss-settlement. Parameter-free. Returns (hit, hit_breakeven, EV_fire, holdEV).
    EV_fire is in CENTS. (Unchanged from v14.)"""
    cost = max(1, c - discount); pool = pooled_tapes(c)
    Marr = []; SV = []; W = []
    for m, sv, w in pool: Marr.append(m); SV.append(sv); W.append(np.full(len(m), w))
    Marr = np.concatenate(Marr); SV = np.concatenate(SV); W = np.concatenate(W)
    kiss = Marr >= X; hit = float(np.average(kiss, weights=W))
    holdEV = float(np.average(np.where(SV == 1, 100 - cost, -cost), weights=W))
    miss = ~kiss
    settle_miss = float(np.average(np.where(SV[miss] == 1, 100 - cost, -cost), weights=W[miss])) if miss.sum() > 0 else -cost
    denom = (X - settle_miss); hit_be = (holdEV - settle_miss) / denom if abs(denom) > 1e-9 else 1e9
    EV_fire = hit * X + (1 - hit) * settle_miss
    return hit, hit_be, EV_fire, holdEV

def state(c, discount=0, smooth=SMOOTH):
    """v15 readout. Scan density peaks low->high; the LOWEST peak passing every gate FIRES EXIT.
    A peak failing a gate is SKIPPED (never an early park). Terminal verdict from the strongest reason
    among occ-qualifying cond-passing peaks, mirroring v14's HOLD/PARK-engine/PARK-noise distinction."""
    draws, npos = CACHE[c]
    if draws is None or npos < NPOS_MIN: return 'PARK-thin'
    saw_cond = False; saw_hold = False; saw_neg = False
    for ctr, mask in peaks_lowtohigh(draws, smooth):
        occ = float(mask.mean())
        if occ < MIN_OCC: continue                                  # not a mode (prominence)
        cond = float(np.mean(np.abs(draws[mask] - ctr) <= WIN))
        if cond < FLOOR: continue                                   # center not trustworthy
        saw_cond = True
        hit, hit_be, EV_fire, holdEV = fired_breakeven(c, ctr, discount)
        if EV_fire <= holdEV:                                       # below derived breakeven now
            if EV_fire <= 0: saw_neg = True
            else: saw_hold = True
            continue
        if hit < hit_be + M_CUSHION * (1 - occ * cond): continue    # rate-sanity + SAFETY (parks c44)
        if EV_fire < EV_VETO: continue                              # magnitude: drops bank-nothing exits
        return 'EXIT'                                               # lowest fully-qualifying peak fires
    if not saw_cond: return 'PARK-noise'
    if saw_hold: return 'HOLD'
    return 'PARK-engine'

def fired_center(c, discount=0, smooth=SMOOTH):
    """The X that state() would fire (or None). For surface rebuild / executor wiring."""
    draws, npos = CACHE[c]
    if draws is None or npos < NPOS_MIN: return None
    for ctr, mask in peaks_lowtohigh(draws, smooth):
        occ = float(mask.mean())
        if occ < MIN_OCC: continue
        cond = float(np.mean(np.abs(draws[mask] - ctr) <= WIN))
        if cond < FLOOR: continue
        hit, hit_be, EV_fire, holdEV = fired_breakeven(c, ctr, discount)
        if EV_fire <= holdEV: continue
        if hit < hit_be + M_CUSHION * (1 - occ * cond): continue
        if EV_fire < EV_VETO: continue
        return ctr
    return None

if __name__ == '__main__':
    from collections import Counter
    print("=" * 78)
    print(f"v15 PEAK-READOUT LOCKED  B={NBOOT} smooth={SMOOTH} MIN_OCC={MIN_OCC} EV_VETO={EV_VETO} "
          f"FLOOR={FLOOR} M_CUSHION={M_CUSHION} WIN=+-{WIN}  [GAP REMOVED]")
    print("=" * 78)
    cen = Counter(); exits = {}
    for c in CENTS:
        st = state(c, 0); cen[st] += 1
        if st == 'EXIT': exits[c] = fired_center(c, 0)
    for k in ['EXIT', 'HOLD', 'PARK-engine', 'PARK-thin', 'PARK-noise']:
        print(f"  {k}: {cen[k]}")
    print(f"  EXIT cells: " + ", ".join(f"c{c}:X{x}" for c, x in sorted(exits.items())))
    print(f"  c44 (noise control) -> {state(44,0)}   [MUST be a PARK]")
