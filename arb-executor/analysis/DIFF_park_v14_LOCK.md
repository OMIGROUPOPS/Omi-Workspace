# DIFF — park_v14 (LOCK): Opus's occ·cond seam confirmed → firewall split to cond (cause); occ → cushion-scaling + hit-rate only. v14 strictly dominates v13.

## The seam Opus pried (and it was real)
`occ·cond ≥ FLOOR` is a **product**, so the level set `occ·cond = 0.50` is not a point — it conflates economically opposite cells:
- **occ 0.55 · cond 0.91 = 0.50**: visits a bit less than half the time, but pins the center hard. A high-conviction reach.
- **occ 0.91 · cond 0.55 = 0.50**: almost always lands, but the center is smeary (cond 0.55, barely above the c44 noise floor 0.33). A frequent smear.

The product floor treats these identically and can be **gamed by occupancy in exactly the wrong direction**: high occ drags a weak cond over the line (admits smears), low occ drops a razor cond under it (rejects sharp-but-infrequent reaches). And occupancy was **double-charged** — it gated resolvability (FLOOR) *and* was already inside the hit-rate driving EV>breakeven. A mode reached 45% of the time has its kiss-rate (hence EV and breakeven margin) computed on that 45%; charging it again under the firewall punishes infrequency twice.

## The diff Opus demanded (cond≥0.85 ∧ occ·cond<0.50, clears breakeven on its OWN low hit?)
Corner is **non-empty** (15 sharp-but-infrequent modes). On Opus's literal test (EV>hold ∧ hit≥be): **10 clear**. But:
- 2 (c40, c41) clear only because EV>hold while **both are negative** ("loses less than holding" — not money). Real engine (EV>0) cuts to **8**.
- All 8 sit **<1 SE** of their own breakeven (largest c17 at 0.88 SE). On Opus's *stated* criterion the seam is open; on the *engine* criterion (EV>0 + tradeable margin) these are the same within-noise class the v13 cushion already prunes — **low-occ modes get the LARGEST cushion** since `1−occ·cond → 1`.

→ The seam is real in its **mechanism** (product double-charges occ) but the corner's payload is marginal. The genuine damage is elsewhere: the product floor **pre-screens the cheap engine-start** (c5/c6) out before the cushion can judge them.

## Why the literal split (cond-firewall + raw breakeven, occ fully removed) OVER-corrects — REJECTED
Simulated Opus's exact prescription (gate cond≥0.50; occ→breakeven only, raw `hit≥be`): EXIT jumps 22→**40**. Of 19 new EXITs, only **3** are SOLID (≥1 SE); 16 are sub-1-SE noise-band admits + a negative-EV cell (c40). Removing occ entirely leaves the **raw breakeven gate as the only thing between you and a low-occ lottery tail** — and at these N it can't tell a +0.4 SE blip from an edge. Worse, a flat ≥1 SE *requirement* **kills the favorite ballast** (c86/87/88/91): at hit≈0.97 the binomial SE→0 and `(hit−be)/se` goes unstable/negative. No scalar margin works across both the high-hit ballast (SE→0) and the low-occ reaches (SE wide).

## The lock: occ belongs in TWO places, never as a hard product-floor firewall
- **Firewall = cond ≥ FLOOR** (the CAUSE: "when I look, is the answer the same?"). This is what kills the c44 smear (cond 0.33). Occupancy is a frequency, not an epistemic fact.
- **occ → (a) the cushion SCALING `m·(1−occ·cond)`** (already in v13: → 0 for resolved ballast, widens for unresolved reaches — the margin shape no scalar SE rule can match) **and (b) the hit-rate inside EV/breakeven**. Same role Opus named ("economic input"), but kept as a *scaling*, not deleted.

This is the X-veto / Sharpe-conjunct pattern a **third** time: a firewall built on a correlate (occ) of the cause (cond). Lotteries were already dead on cond (unrepeatable tail center → low cond) and on breakeven (20% hit). occ in the firewall caught nothing live and falsely parked the one thing cond+breakeven would pass.

## v14 = v13 with ONE surgical change
`fireable_mode` selects the lowest mode with `cond ≥ FLOOR` (was `occ·cond ≥ FLOOR`). Cushion `M_CUSHION·(1−occ·cond)`, breakeven gate, EV>0/hold, all params — **IDENTICAL** to v13.

## Authoritative delta (each kernel built clean in its own process, rng(13))
| | v13 | v14 |
|---|---|---|
| EXIT | 22 | **26** |
| census | E22 H7 PE14 PT10 PN37 | E26 H14 PE24 PT10 PN16 |

**RECOVERED by v14 (4), LOST (0):**
| cell | X | occ | cond | EV>hold | breakeven margin |
|---|---|---|---|---|---|
| c5 | 8 | 0.61 | 0.72 | 2.94 > −1.77 | **+4.93 SE** |
| c6 | 7 | 0.48 | 0.78 | 2.00 > −3.44 | **+4.89 SE** |
| c12 | 20 | 0.94 | 0.50 | 3.70 > −3.83 | **+3.59 SE** |
| c36 | 29 | 0.98 | 0.51 | 1.93 > −4.64 | **+1.31 SE** |

**v14 strictly dominates v13's fire set**: every v13 EXIT retained, plus 4 recoveries — none below +1.31 SE. c5/c6 are the cheap engine-start (clear by ~5 SE) the product floor was wrongly parking. c12/c36 are frequently-visited borderline-cond cells freed once occ stops double-charging.

## Lock tests (all PASS on v14)
- **c44 stays PARK-noise** at every discount (smear dies on cond 0.33 — the cause, not the correlate).
- **c50 → HOLD** (cond-passing mode exists but EV ≤ hold; economically parked, not a resolvability failure).
- **Zero FATAL flips** (no EXIT → PARK-noise/thin) at any discount 0–30 → resolvability basis-invariant under cond firewall too.
- **NEW HAMMER**: deep reach modes (c5 X40, c6 X37, c17 X53) never the lowest cond-passing mode → never fire even when discount lifts their EV.
- **Discount monotone**: nEXIT 26→3 as holding gets cheaper.

## Params (unchanged from v13 except firewall variable)
FLOOR=0.50 **on cond** (was occ·cond), M_CUSHION=0.15 (labeled dial), GAP=6, WIN=3, KP=2.0, M0=1.2, TAU=0.7, NPOS_MIN=3, NBOOT=300. Kernel k=0.215, h=2.006 unchanged. **No new knob** — cond_floor inherits FLOOR's exact more-likely-than-not justification ("majority of visits agree on the center"); occ moving to cushion+hit-rate *removes* a gate rather than adding one.

## Verdict
Opus's cause-diagnosis was correct; his literal fix over-corrected. v14 takes the diagnosis (cond=firewall) and keeps v13's already-correct margin shape (cushion scaling) instead of a raw breakeven gate. Result: 4 solid recoveries, zero losses, ballast and smear-firewall intact. **ATP_MAIN exit LOCKS at v14.**
