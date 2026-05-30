# DIFF — park_v13 (LOCK): breakeven-hit diff settles c18/19/21; cushion engine-start is m-invariant → m is a labeled risk dial, kernel LOCKS

Branch: blend/agent-derivation. Final kernel.

## What Opus conceded (recorded)
- **Sharpe conjunct: DEAD.** It rewards the concentrated tail (forced c5 lottery Sharpe 0.247 > c18 engine 0.166). Wrong variable, conceded without reservation.
- **Empty PARK-engine-at-floor: ACCEPTED conclusion, not unmet F3(a).** His reactivation story was forbidden by invariance (resolvability is on moves; a discount doesn't move the band; no resolved-but-dormant set exists for a discount to light). Doctrine must say **"dormant = re-bucketing (Part-2 changes which tapes anchor at a cent = a different tape, legitimately re-resolved), NEVER reactivation (same tape, banned recompute)."**

## The lock-blocker: paid is asleep at low hit, so c18/19/21 were gated only by EV>hold
Opus's catch (correct): `paid(X)=1−hit^KP` was built to kill the un-paid certainty crumb (hit→1 ⟹ paid→0). At hit=0.33, paid ≈ 1 — it contributes ~zero penalty. So "paid already damps the low-hit reach" was circular/false-in-force. c18/19/21 were gated only by EV>hold + supp. Needed the non-circular test: the **derived breakeven hit rate**.

## BREAKEVEN-HIT DIFF (the decider) — c18/19/21 are MARGINAL (within estimation noise)
breakeven hit* solves EV_fire(hit) = holdEV using the cell's OWN cost geometry + empirical miss-settlement (parameter-free, different per cent):

| cell | firedX | hit | breakeven | margin | **margin/SE** | verdict |
|---|---|---|---|---|---|---|
| **c18** | +53 | 0.332 | 0.282 | +0.049 | **1.68 SE** | within noise |
| **c19** | +52 | 0.354 | 0.305 | +0.048 | **1.66 SE** | within noise |
| **c21** | +47 | 0.394 | 0.339 | +0.055 | **1.89 SE** | within noise |
| c11 | +18 | 0.498 | 0.293 | +0.205 | **5.24 SE** | clears (chasm) |
| c14 | +11 | 0.675 | 0.470 | +0.205 | **6.42 SE** | clears (chasm) |
| c16 | +11 | 0.698 | 0.471 | +0.227 | **5.47 SE** | clears (chasm) |
| c33 | +29 | 0.585 | 0.473 | +0.112 | **4.65 SE** | clears |
| c29 | +30 | 0.558 | 0.504 | +0.054 | 2.11 SE | clears (just) |
| **c56** | +36 | 0.635 | 0.640 | **−0.005** | **−0.15 SE** | BELOW breakeven (was a v12 mis-fire) |

The bank-mode engine (c11/14/16/33) clears breakeven by **4.6–6.4 SE** — a chasm. The high-reach-only cells (c18/19/21) clear by only **~1.7 SE** — real point-estimate margin, but within estimation noise at occ·cond 0.56. Opus's branch-B is the truth. EV>hold alone is NOT sufficient: it admitted c56 (below breakeven) and the within-noise cluster.

## THE GATE (Opus's confidence-scaled cushion — right variable, derived margin)
```
fire iff:  EV_fire > holdEV                       (breakeven, derived per cent — necessary)
      AND  hit(fired_X) >= hit_breakeven(c) + m·(1 − occ·cond)
```
Logic: a highly-resolved reach (high occ·cond) fires near breakeven (we trust the hit estimate); a barely-resolved reach (occ·cond near FLOOR) needs a hit cushion because the estimate is shaky and a thin EV>hold could be noise. Ties the economic gate to epistemic confidence. m = cushion in hit-points demanded per unit resolvability-deficit.

## CUSHION STABILITY (Opus's required check) — engine-start is m-INVARIANT → m is a labeled dial, not a hidden knob

| m | nfire | cheapest | c18/19/21 | c56 |
|---|---|---|---|---|
| 0.00 | 36 | **c11** | fire | dead (below breakeven) |
| 0.10 | 29 | **c11** | fire | dead |
| **0.15** | 22 | **c11** | **pruned** | dead |
| 0.20 | 19 | **c11** | pruned | dead |
| 0.30 | 16 | **c11** | pruned | dead |

**Engine-start = c11 for EVERY m in [0, 0.30].** It never moves — c11/14/15/16 (clearing breakeven by 5+ SE) anchor the spine regardless. The cushion does NOT walk engine-start up (Opus's feared failure mode does not occur). It only prunes the marginal high-reach cells from the middle. Clean break at **m=0.15** where c18/19/21 drop together.

→ Therefore **m is exactly the acceptable case Opus named: a labeled coverage/risk-appetite dial the operator sets, not a hidden floor.** m=0 = max coverage (fire the marginal reaches); m≥0.15 = conservative (prune to the high-confidence engine). The spine (c11–16, c29–35, favorites c84–91) is present at every setting. c56 is correctly evicted at all m (below breakeven).

## LOCK DECISION
- **Default m = 0.15** (prunes the within-noise reaches; defensible conservative T-20 floor — matches the worst-case doctrine). Operator may set m=0 for max coverage. LABELED dial, documented.
- Every gate is now on a CAUSE, not a symptom: resolvability=occ·cond (epistemic), tradeability=EV>derived-breakeven + confidence-scaled hit cushion (economic, hit-rate is the cause-variable). No X-space veto, no Sharpe, no hand-set P(loss) line.
- Final params: FLOOR(occ·cond)=0.50 (more-likely-than-not, engine-start robust), m=0.15 (labeled dial), GAP=6, WIN=3, KP/M0/TAU/WA/NPOS_MIN unchanged. k=0.215,h=2.006 kernel unchanged.

## Invariance (F3) — HOLDS in its true form
Full baseline now populates ALL five states: EXIT=22, HOLD=7, PARK-engine=14, PARK-thin=10, PARK-noise=37. Engine-start=c11. c18/19/21 correctly PARK-engine (within-noise reaches pruned at m=0.15); c56 → HOLD; favorites split EXIT/HOLD; c44/c50 PARK-noise.

Under discount, EXIT cells DO transition — but checking WHICH state they go to: **FATAL resolvability flips (EXIT→PARK-noise/PARK-thin) = {} at EVERY discount.** Every flip is ECONOMIC (EXIT→HOLD or EXIT→PARK-engine): as cost drops, holding a cheaply-acquired position beats exiting it (holdEV rises faster than the fixed-X reach EV). This is the already-accepted "nEXIT shrinking = favorite-wins-outright" behavior, NOT the lottery re-entering. Resolvability is perfectly invariant (it's on moves; discount never touches it). The F3 firewall protects resolvability flips, not the economic EXIT/HOLD boundary, which MUST move with basis. F3 holds.

## Status: KERNEL LOCKED (pending Opus's final ack on default m=0.15). Next: rebuild ATP_MAIN surface on v13, re-render pyramid, user sign-off, then replicate ATP_CHALL/WTA_MAIN/WTA_CHALL + rewire blueprint/executor.
