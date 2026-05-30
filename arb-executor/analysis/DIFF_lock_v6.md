# DIFF v6 — LOCK. Gate-only. Soft-τ tested in Opus's exact sequence and REJECTED.

Branch: blend/agent-derivation. Constants k=0.215, h=2.006. Gate: max(EV·paid·supp)≤0.05 OR npos<3.

## Convergence with Opus (independent)
Opus, reasoning from the (stale) v4 prompt, arrived at the SAME fix I committed in v5:
a **peak-conviction gate** routing noise-floor cells (c65 peak 0.0001, c67 peak 0.0002) to HOLD
instead of dignifying their argmax. We agree:
- Gate is the real fix (11→4 within-regime jumps). LOCKED.
- Do NOT smooth score across cents (bleeds live c66 signal into dead neighbors = tape-override). CONFIRMED
  by my own probe: cross-cent smoothing ADDED flips (c80→81, c57→58).

## Where Opus's 2-stage proposal was tested and REJECTED
Opus proposed: gate FIRST, then within-cell soft-τ sigmoid to stabilize genuinely-flat-but-real cells
(c49). Tested his exact sequence:
- **GATE only (v5):** within-regime jumps>8c = **4**, cheap-zone jumps>5c = 5.
- **GATE + within-cell soft-τ:** within-regime = **5** (WORSE), cheap-zone = 2.
Soft-τ traded cheap-zone wobble (5→2, cosmetic) for NEW mid-zone flips (c54→55, c56→57, c61→62), net 4→5.
The score-weighted low-quantile xlo wanders on long-tailed soft membership where hard-cred was stable.
→ My earlier "soft-τ no-op" wasn't just wrong-order; soft-τ does not dominate the hard cliff here.

## Why gate-only is the lock
1. **Cheap ladder is already smooth.** Deltas c5-20: +0,+7,-1,-5,-1,+6,-2,-3,+0,+2,+0,+0,+3,+4 — small
   wobble around a rising +6→+12 bank floor. The two flagged ">5c" cells (c7,c11) are wide-band cells
   picking a slightly higher floor, NOT mode flips. Monotone-in-spirit.
2. **The 4 survivors are ALL real — both sides high-conviction EV>0:**
   - c19:+16(hit64,EV3.55) → c20:+37(hit42,EV4.10) → c21:+22(hit57,EV3.56)  [the c20 reach, preserved]
   - c45:+33(hit62,EV3.69) → c46:+16(hit79,EV2.83)
   - c49:+11(hit89,EV4.22) → c50:+34(hit65,EV4.47)
   These are two LIVE cells with genuinely different optimal exits — NOT Opus's dead-next-to-live case
   (those are now correctly HOLD). Forcing them continuous = tape-override. They are texture, not pathology.

## FINAL LOCKED STACK
1. bandwidth from move-spread
2. similarity from distance-tapered KS
3. support from SE
4. **HOLD = conviction gate (max score ≤ 0.05 OR npos < 3)**  ← the P3 fix
5. config: A=argmax point / B=band fire-xlo / C=hold
6. soft-τ: TESTED, REJECTED (net negative post-gate). Hard τ=0.7 cred region stays.

Doctrine: c20 reach preserved (real signal, not capped). The tape wins.
