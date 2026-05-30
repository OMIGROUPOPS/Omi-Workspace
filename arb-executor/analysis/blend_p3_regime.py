"""
P3 RESOLUTION PROBE — regime-aware readout (Opus call).
Branch blend/agent-derivation.

Opus's call: the 90 cells are THREE populations, not one. One readout shape
cannot serve all three; forcing it manufactures the discontinuity.

  Regime A  (point-convicted):  width <= wA  -> config = argmax (the point)
  Regime B  (band-convicted):   width >= wB  -> config = [xlo,xhi], FIRE xlo
  (interpolate wA<width<wB        -> treat as B: fire xlo, report band)
  Regime C  (hold):             max score<=0 -> config = HOLD, no exit, EXCLUDED from continuity

Key override of agent's lean: for Regime B fire at the LOW edge xlo (high-frequency
edge), NOT a concentrated center. Doctrine: don't reach when reaching buys no score.

Three falsifiable diffs (lock if all pass):
  1. xlo(c) near-monotone across cheap zone (Regime B continuity)
  2. excluding Regime-C + per-regime metric -> real discontinuities drop to a handful
     at TRUE regime boundaries only
  3. firing xlo keeps cheap-cell EV positive while staying off the jackpot
"""
import numpy as np
from blend_continuous import (CENTS, curve, effN, SE, bandwidth, SPREAD, ownN, rel)

# joint-fitted constants (locked)
K, H = 0.215, 2.006
WA, WB = 3, 12   # regime width thresholds (Opus suggested wA~3, wB~12)

# v5 ROOT-CAUSE FIX: HOLD is not "max score<=0"; it's "too little EV-positive
# conviction to be a real exit". Expensive favorites are EV-negative almost everywhere
# and only a razor-thin single X squeaks positive -> that needle flips on sub-penny noise.
SCORE_FLOOR = 0.05   # absolute conviction floor on max(EV*paid*supp)
NPOS_MIN = 3         # need >=3 EV-positive candidates to constitute a real exit band

def readout(c, kp=2.0, m0=1.2, floor=1, tau=0.7):
    """Regime-aware. Returns dict with regime, fire_x (executor X), band, diagnostics."""
    Xs = np.arange(floor, 95 - c)
    if len(Xs) == 0:
        return None
    EV, HIT, ROI = curve(c, K, H, Xs)
    eff = effN(c, K, H); se = SE(c, K, H)
    paid = 1 - (HIT / 100) ** kp
    supp = np.minimum(1.0, (HIT / 100) / (m0 * se))
    s = np.where(EV > 0, EV * paid * supp, 0.0)
    npos = int((EV > 0).sum())

    # Regime C: marginal/needle cell -> HOLD (economic fact, not a knob)
    if s.max() <= SCORE_FLOOR or npos < NPOS_MIN:
        return dict(c=c, regime="C", fire_x=None, xlo=None, xhi=None, width=None,
                    ev=None, hit=None, roi=None, eff=float(eff), se=float(se))

    cred = s >= tau * s.max()
    Xc = Xs[cred]
    xlo, xhi = int(Xc.min()), int(Xc.max())
    width = xhi - xlo
    argmax_x = int(Xs[int(np.argmax(s))])

    if width <= WA:
        regime = "A"; fire_x = argmax_x          # point: fire the argmax
    else:
        regime = "B"; fire_x = xlo               # band: fire the high-frequency low edge

    i = int(np.where(Xs == fire_x)[0][0])
    return dict(c=c, regime=regime, fire_x=int(fire_x), xlo=xlo, xhi=xhi, width=int(width),
                argmax_x=argmax_x,
                ev=float(EV[i]), hit=float(HIT[i]), roi=float(ROI[i]),
                eff=float(eff), se=float(se), b=float(bandwidth(c, K)))


if __name__ == "__main__":
    R = {c: readout(c) for c in CENTS}
    R = {c: r for c, r in R.items() if r is not None}

    # regime census
    nA = sum(1 for r in R.values() if r["regime"] == "A")
    nB = sum(1 for r in R.values() if r["regime"] == "B")
    nC = sum(1 for r in R.values() if r["regime"] == "C")
    print("=" * 70)
    print(f"REGIME CENSUS (90 cents):  A(point)={nA}  B(band,fire-xlo)={nB}  C(hold)={nC}")
    print("=" * 70)

    # ============ DIFF 1: xlo(c) near-monotone across cheap zone ============
    print("\n" + "=" * 70)
    print("DIFF 1: Regime-B fire_x (xlo) continuity across cheap zone c=5..30")
    print("=" * 70)
    cheap = [c for c in range(5, 31) if c in R]
    print("   c  regime  fire_x  band[xlo,xhi]  w   hit%  roi%   EV")
    prev = None; jumps_cheap = 0
    for c in cheap:
        r = R[c]
        fx = r["fire_x"]
        flag = ""
        if prev is not None and fx is not None and r["regime"] != "C":
            if abs(fx - prev) > 5:
                flag = "  <-- JUMP>5c"; jumps_cheap += 1
        if fx is not None:
            prev = fx
        if r["regime"] == "C":
            print(f"  {c:>2}    C     HOLD     --            --   --     --     --{flag}")
        else:
            print(f"  {c:>2}    {r['regime']}     +{fx:<5} [{r['xlo']:>2},{r['xhi']:>2}]      {r['width']:>2}  {r['hit']:>4.0f}  {r['roi']:>4.0f}  {r['ev']:>5.2f}{flag}")
    print(f"\n  cheap-zone fire_x jumps >5c: {jumps_cheap}")

    # ============ DIFF 2: per-regime continuity vs naive ============
    print("\n" + "=" * 70)
    print("DIFF 2: per-regime, C-excluded continuity vs naive single-readout")
    print("=" * 70)
    cs = sorted(R.keys())
    # naive: treat every cell's fire_x (or argmax for C-as-number) as one series, count >8c
    naive_series = []
    for c in cs:
        r = R[c]
        naive_series.append(r["fire_x"] if r["fire_x"] is not None else 0)  # C forced to 0 (the artifact)
    naive_jumps = sum(1 for i in range(1, len(naive_series)) if abs(naive_series[i] - naive_series[i-1]) > 8)

    # regime-aware: continuity only WITHIN non-C cells, and flag a jump only if BOTH
    # neighbors are same-or-adjacent regime (true boundary changes are allowed/expected)
    real_jumps = []
    for i in range(1, len(cs)):
        a, b = R[cs[i-1]], R[cs[i]]
        if a["regime"] == "C" or b["regime"] == "C":
            continue  # hold is a valid config, not a discontinuity
        fa, fb = a["fire_x"], b["fire_x"]
        # both fire xlo (B) or both point (A): expect smooth. A<->B transition: allow.
        if a["regime"] == b["regime"] and abs(fb - fa) > 8:
            real_jumps.append((cs[i-1], cs[i], fa, fb, a["regime"]))
    print(f"  NAIVE (one readout, C->0):           jumps>8c = {naive_jumps}")
    print(f"  REGIME-AWARE (C excluded, same-regime only): jumps>8c = {len(real_jumps)}")
    if real_jumps:
        print("  remaining same-regime jumps (true pathology if any):")
        for (ca, cb, fa, fb, rg) in real_jumps:
            print(f"    c{ca}->c{cb}: +{fa}->+{fb}  (both regime {rg})")
    else:
        print("  -> NO same-regime jumps>8c. All transitions are regime boundaries or hold.")

    # ============ DIFF 3: cheap fire-xlo EV positive AND off-jackpot ============
    print("\n" + "=" * 70)
    print("DIFF 3: cheap fire_x EV>0 AND off-jackpot (fire_x << argmax_reach)")
    print("=" * 70)
    print("   c  fire_x  EV(fire)  hit%   |  argmax_x  band_top  (jackpot we're NOT taking)")
    for c in [5, 6, 7, 8, 9, 10, 12, 15, 20]:
        if c not in R: continue
        r = R[c]
        if r["regime"] == "C":
            print(f"  {c:>2}   HOLD"); continue
        print(f"  {c:>2}   +{r['fire_x']:<5} {r['ev']:>6.2f}   {r['hit']:>4.0f}   |   +{r['argmax_x']:<6}  +{r['xhi']}")

    # full surface dump for the record
    print("\n" + "=" * 70)
    print("FULL READOUT (all 90 cents)")
    print("=" * 70)
    print("   c  reg  fire_x  band      w   hit%  roi%    EV    effN   SE")
    for c in cs:
        r = R[c]
        if r["regime"] == "C":
            print(f"  {c:>2}   C   HOLD     --        --   --    --     --    {r['eff']:>4.1f} {r['se']:>5.1f}")
        else:
            print(f"  {c:>2}   {r['regime']}   +{r['fire_x']:<5} [{r['xlo']:>2},{r['xhi']:>2}]   {r['width']:>2}  {r['hit']:>4.0f}  {r['roi']:>4.0f}  {r['ev']:>5.2f}  {r['eff']:>4.1f} {r['se']:>5.1f}")
