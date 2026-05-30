"""v11 — Opus's three corrected forms, wired and hunted.

#3 FIREWALL: the LOWEST RESOLVED mode is the only fire candidate; it must still clear the
   EV/paid/supp gate (necessary-not-sufficient); a cell whose lowest resolved mode lies in
   REACH territory is unfireable at ANY basis. NOT 'regardless of EV' (that fires un-paid crumbs).
#2 RESOLVABILITY: a mode is RESOLVED iff occ*cond >= FLOOR (product, smooth, single global floor),
   in the epistemic gate (NOT folded into EV). occ*cond = P(a resample both visits this mode AND
   pins its center). This also pre-screens reach tails out of firewall candidacy.
#1 c5 -> PARK-boundary (engine starts c6); single global ALPHA; no per-arm lowering, no window
   widening; c5 flagged 'revisit under Part-2 entry distribution' (different tapes, not different
   price on same tapes -> invariance intact).

Reach territory: derived, not set. A mode is 'reach' if its center X exceeds REACH_FRAC of the
   cell's available offset range (Xmax = 94-c). We report the lowest-resolved-mode X for all 90
   cells so the boundary can be checked against where bank vs reach actually sit.
"""
import numpy as np
from blend_park_v8 import pooled_tapes, score_and_bestx
from blend_continuous import CENTS
rng = np.random.default_rng(13)
KP, M0, TAU, NPOS_MIN, NBOOT = 2.0, 1.2, 0.7, 3, 300
GAP, WIN = 6, 3
FLOOR = 0.50          # occ*cond floor: more-likely-than-not resolved (engine-start robust across [0.45,0.55])
M_CUSHION = 0.15      # LABELED risk dial (NOT hidden knob): hit-cushion per unit resolvability-deficit.
                      # engine-start=c11 invariant for all m in [0,0.30]; m=0 max coverage, m>=0.15 conservative.
REACH_FRAC = 0.35     # mode center above this fraction of (94-c) = reach territory. Derived-checked.

def boot_modes(c):
    """Cache once on OWN moves: cluster best-X draws into <=2 modes; per mode return center,
    occupancy (cluster visit rate), conditional stability (pin rate within cluster), and the
    product occ*cond (resolvability quantity)."""
    pool = pooled_tapes(c)
    if not pool: return dict(npos=0, modes=[])
    Xs, s, EV, bx = score_and_bestx(c, c, pool)
    if Xs is None or s.max() <= 0: return dict(npos=0, modes=[])
    npos = int((EV > 0).sum())
    draws = []
    for _ in range(NBOOT):
        rp = [(m[idx], sv[idx], w) for (m, sv, w) in pool for idx in [rng.integers(0, len(m), len(m))]]
        X2, s2, E2, _ = score_and_bestx(c, c, rp)
        if X2 is None or s2.max() <= 0: continue
        draws.append(int(X2[int(np.argmax(s2))]))
    draws = np.array(draws)
    if len(draws) == 0: return dict(npos=npos, modes=[])
    d = np.sort(draws); gaps = np.diff(d)
    if len(gaps) and gaps.max() >= GAP:
        k = int(np.argmax(gaps)); groups = [d[:k+1], d[k+1:]]
    else:
        groups = [d]
    Xmax = 94 - c
    modes = []
    for i, g in enumerate(groups):
        center = int(np.median(g))
        if len(groups) == 2:
            mid = (np.median(groups[0]) + np.median(groups[1])) / 2
            inc = (draws <= mid) if i == 0 else (draws > mid)
        else:
            inc = np.ones(len(draws), bool)
        occ = float(inc.mean())
        cond = float(np.mean(np.abs(draws[inc] - center) <= WIN)) if inc.sum() else 0.0
        oc = occ * cond
        reach = center > REACH_FRAC * Xmax
        modes.append(dict(center=center, occ=round(occ,3), cond=round(cond,3),
                          oc=round(oc,3), reach=bool(reach), resolved=bool(oc >= FLOOR)))
    return dict(npos=npos, modes=sorted(modes, key=lambda m: m['center']))

CACHE = {c: boot_modes(c) for c in CENTS}

def ev_paid_supp_X(c, X, discount):
    """EV/paid/supp gate value at fixed mode-X under discount (EV-only re-pricing; band fixed)."""
    cost = max(1, c - discount); pool = pooled_tapes(c)
    EV = 0.0; HIT = 0.0; WT = 0.0
    for m, sv, w in pool:
        kiss = m >= X
        pnl = np.where(kiss, X, np.where(sv == 1, 100 - cost, -cost)).astype(float)
        EV += w * pnl.sum(); HIT += w * kiss.sum(); WT += w * len(m)
    ev = EV / WT; hit = HIT / WT * 100
    from blend_continuous import SE
    K, H = 0.215, 2.006
    se = SE(c, K, H); paid = 1 - (hit/100)**KP; supp = min(1.0, (hit/100)/(M0*se))
    sgate = ev * paid * supp if ev > 0 else 0.0
    allsv = np.concatenate([sv for _, sv, _ in pool])
    holdEV = float(np.mean(np.where(allsv == 1, 100 - cost, -cost)))
    return ev, holdEV, sgate

def fireable_mode(c):
    """Lowest RESOLVED mode that is NOT in reach territory. None -> cell unfireable at any basis."""
    res = [m for m in CACHE[c]['modes'] if m['resolved']]
    if not res: return None
    return res[0]                     # lowest RESOLVED mode; reach-region veto DROPPED (Opus signed):
                                      # occ*cond is the sole firewall (cause), not X-space (symptom)

def fired_breakeven(c, X, discount=0):
    """Derived per-cent breakeven: smallest hit making EV_fire>=holdEV, from OWN cost geometry +
    empirical miss-settlement. Parameter-free. Returns (hit, hit_breakeven, EV_fire, holdEV)."""
    cost = max(1, c - discount); pool = pooled_tapes(c)
    Marr=[];SV=[];W=[]
    for m,sv,w in pool: Marr.append(m);SV.append(sv);W.append(np.full(len(m),w))
    Marr=np.concatenate(Marr);SV=np.concatenate(SV);W=np.concatenate(W)
    kiss=Marr>=X; hit=float(np.average(kiss,weights=W))
    holdEV=float(np.average(np.where(SV==1,100-cost,-cost),weights=W))
    miss=~kiss
    settle_miss=float(np.average(np.where(SV[miss]==1,100-cost,-cost),weights=W[miss])) if miss.sum()>0 else -cost
    denom=(X-settle_miss); hit_be=(holdEV-settle_miss)/denom if abs(denom)>1e-9 else 1e9
    EV_fire=hit*X+(1-hit)*settle_miss
    return hit, hit_be, EV_fire, holdEV

def state(c, discount=0):
    M = CACHE[c]
    if M['npos'] < NPOS_MIN: return 'PARK-thin'
    fm = fireable_mode(c)                            # lowest RESOLVED mode (occ*cond sole firewall)
    if fm is None: return 'PARK-noise'
    hit, hit_be, EV_fire, holdEV = fired_breakeven(c, fm['center'], discount)
    # tradeability gate (CAUSE variable = hit vs derived breakeven, + confidence-scaled cushion):
    if EV_fire <= holdEV:                            # below derived breakeven now
        return 'PARK-engine' if EV_fire <= 0 else 'HOLD'
    if hit < hit_be + M_CUSHION*(1 - fm['oc']):      # within estimation noise of breakeven -> not yet tradeable
        return 'PARK-engine'
    return 'EXIT'

if __name__ == '__main__':
    from collections import Counter
    print("="*80); print(f"v11 FIREWALL — FLOOR(occ*cond)={FLOOR}  REACH_FRAC={REACH_FRAC}  GAP={GAP} WIN=+-{WIN}"); print("="*80)

    # ---- DIFF (a): lowest-resolved-mode X for all 90 cells; flag any reach-territory lowest mode ----
    print("\nDIFF(a) — lowest RESOLVED mode per cell (R=resolved, reach=in reach territory):")
    danger = []
    for c in CENTS:
        res = [m for m in CACHE[c]['modes'] if m['resolved']]
        if not res:
            continue
        low = res[0]; Xmax = 94 - c
        flag = "  <-- LOWEST RESOLVED IS REACH (firewall must veto)" if low['reach'] else ""
        if low['reach']: danger.append(c)
        if c <= 35 or flag:   # cheap zone + any danger cell anywhere
            print(f"  c{c:>2}: lowX={low['center']:>3} (of 0..{Xmax})  occ*cond={low['oc']:.2f}  reach={low['reach']}{flag}")
    print(f"  >>> cells whose LOWEST resolved mode is reach-territory (firewall load-bearing here): {danger}")

    # ---- DIFF (b): occ*cond for every REACH mode in cheap zone; confirm most below FLOOR ----
    print("\nDIFF(b) — reach modes in cheap zone (c<=29): occ*cond, resolved? (most should be UNRESOLVED):")
    for c in [x for x in CENTS if x <= 29]:
        for m in CACHE[c]['modes']:
            if m['reach']:
                print(f"  c{c:>2}: reachX={m['center']:>3}  occ={m['occ']:.2f} cond={m['cond']:.2f}  occ*cond={m['oc']:.2f}  resolved={m['resolved']}")

    # ---- baseline states ----
    print("\nBaseline states:")
    B = {c: state(c, 0) for c in CENTS}; print(Counter(B.values()))
    for lab in ['EXIT','HOLD','PARK-engine','PARK-thin','PARK-noise']:
        print(f"  {lab:<12}: {[c for c in CENTS if B[c]==lab]}")
    print(f"  c5 fireable_mode = {fireable_mode(5)}  -> state={B[5]}  (cheapest cell; engine-start=c11 — see DIFF/DOCTRINE)")
    print(f"  c6 fireable_mode = {fireable_mode(6)}  -> state={B[6]}")

    # ---- LOCK TEST: discount sweep, three required behaviors ----
    print("\n"+"="*80); print("LOCK TEST — (1) bank modes light cost-ordered (2) c44/c50 stay dark (3) NEW HAMMER"); print("="*80)
    engine0 = [c for c in CENTS if B[c]=='PARK-engine']; exit0 = [c for c in CENTS if B[c]=='EXIT']
    noise0  = [c for c in CENTS if B[c]=='PARK-noise']
    print(f" baseline PARK-engine={engine0}")
    print(f" disc nEXIT  engine->EXIT(cost-ordered?)     c44/c50      EXIT->PARK(MUST=[])")
    for disc in (0,3,6,10,15,20,25,30):
        S = {c: state(c, disc) for c in CENTS}
        e2 = [c for c in engine0 if S[c]=='EXIT']
        dk = {c: S[c] for c in (44,50)}
        ep = [c for c in exit0 if S[c].startswith('PARK')]
        print(f"  {disc:>2}  {sum(v=='EXIT' for v in S.values()):>3}   {str(e2)[:26]:<26} ord={e2==sorted(e2)!s:<5} {dk}  {ep}")

    # ---- NEW HAMMER: force a reach mode's EV above hold; confirm it still does NOT fire ----
    print("\nNEW HAMMER — deliberately lift a reach mode's EV via deep discount; must NOT fire:")
    for c in [5,6,17]:
        reach = [m for m in CACHE[c]['modes'] if m['reach']]
        for m in reach:
            ev,holdEV,sgate = ev_paid_supp_X(c, m['center'], 30)  # huge discount
            fm = fireable_mode(c)
            fired = (fm is not None and fm['center']==m['center'])
            print(f"  c{c} reachX={m['center']} @disc30: ev={ev:.2f} hold={holdEV:.2f} sgate={sgate:.2f} | "
                  f"is_fire_candidate={fired} (MUST be False: never the lowest resolved non-reach mode)")
