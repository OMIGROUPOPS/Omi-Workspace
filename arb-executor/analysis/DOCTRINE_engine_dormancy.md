# DOCTRINE NOTE — "Dormant" means re-bucketing, NEVER reactivation

**Written into the doctrine at Opus's explicit instruction, in his exact terms, because the loose
version will mislead any reader into expecting discount-reactivation, which the kernel structurally
cannot do.**

## The claim, stated precisely
The cheap "engine" (c5–c10, and the within-noise reaches c18/19/21 pruned at m=0.15) is **dormant at
the T-20 worst-case floor**. It is dormant in exactly ONE sense and explicitly NOT the other:

- **Re-bucketing (the TRUE sense):** In Part 2, an entry discount changes *which historical tapes
  anchor at a given cent*. A cell that anchors at, say, c6 after a discount is a **different tape**
  than the one that anchored at c6 at the T-20 floor — premarket drift re-buckets the population.
  That different tape is **legitimately re-resolved from scratch** (new moves, new occ·cond, new
  breakeven). The engine can light in Part 2 because we are looking at a different set of observations.

- **Reactivation (the BANNED sense):** A discount does NOT revive a cell that parked at the floor.
  Resolvability is computed on **moves** (m = peak − anchor); a discount only lowers cost, which
  prices EV — it never moves the credible band. So a cell that is PARK-noise (unresolved) or
  PARK-engine (resolved but sub-breakeven) at the floor will be **exactly as unresolved / sub-breakeven
  at every discount**, because the moves are identical. There is no resolved-but-dormant set that a
  discount can "light up." Recomputing the band at a discounted cost on the SAME tape is the banned
  recompute (it re-couples the epistemic gate to price — the exact coupling the HOLD/PARK split exists
  to kill).

## Why this is load-bearing
Earlier in the derivation we expected PARK-engine to be non-empty at the floor and to "light
cost-ordered under discount." That reactivation story was **wrong and is forbidden by invariance.**
The empty-then-populated PARK-engine at the floor (14 cells at m=0.15) is the **accepted conclusion**,
not an unmet falsifier (F3a). Those PARK-engine cells are resolved but sub-breakeven NOW; they do not
become tradeable by discounting THIS tape — they become tradeable only if Part-2 re-bucketing puts a
DIFFERENT, more-favorable tape population at their cent.

## The observable signature (so no one mistakes it for a bug)
- `nEXIT` SHRINKS as a uniform discount deepens (43 → 0 by disc≈20). This is **correct**: lowering
  cost lifts holdEV faster than the fixed-X reach EV (the favorite just wins outright), so EXIT cells
  transition ECONOMICALLY to HOLD/PARK-engine. **No cell ever flips EXIT → PARK-noise/PARK-thin**
  (resolvability is invariant). The economic boundary moves; the epistemic one does not.
- A uniform discount is NOT the Part-2 mechanism. Part 2 is a *re-bucketing of tapes per cent*, not a
  *uniform price cut on the existing tapes*. The uniform-discount sweep is only an invariance probe.

## One-line version for the blueprint
> The cheap engine is dormant at the T-20 floor in the **re-bucketing** sense only (Part-2 discounts
> change which tapes anchor at each cent → a different population, legitimately re-resolved), and
> **never** in the **reactivation** sense (a discount cannot revive a parked cell, because
> resolvability is on moves and a discount does not move the band). Expecting parked cheap cells to
> "light up" under a uniform discount is a category error the kernel structurally forbids.

---

# DOCTRINE NOTE (v14) — The firewall gates the CAUSE (cond), never a correlate (occ·cond)

**The third instance of the same failure mode. Recorded so it is never reintroduced.**

## The principle
Resolvability has exactly one epistemic question: **"when I look, is the answer the same?"** That is
`cond` — the conditional stability of the mode center (majority of bootstrap visits agree on it within
±WIN). `cond` is the CAUSE of the c44 noise failure (c44 cond 0.33 = the center is unrepeatable).

`occ` (occupancy = how often a resample visits the cluster at all) is a **FREQUENCY, not an epistemic
fact**. Frequency is an economic input — it is already priced as the hit-rate inside EV/breakeven, and
it already scales the confidence cushion `m·(1−occ·cond)`. Putting `occ` into the firewall as the
product `occ·cond ≥ FLOOR` **double-charges occupancy** and lets a high-occ smear sneak a weak cond
over the line while dropping a sharp-but-infrequent reach (and the cheap engine-start c5/c6) under it.

## The rule
- **Firewall:** `cond ≥ FLOOR` (FLOOR=0.50: "the majority of visits agree on the center"). Cause only.
- **occ:** flows through (a) the hit-rate in EV/breakeven and (b) the cushion scaling `(1−occ·cond)`.
  Never as a hard pre-screen.

## Why not the literal split (cond-firewall + raw breakeven, occ deleted)
Deleting occ entirely leaves the raw breakeven gate as the sole defense against low-occ lottery tails;
at realized N it admits a band of sub-1-SE noise cells. And a flat SE-margin *requirement* kills the
favorite ballast (hit≈0.97 → SE→0 → ratio explodes). The cushion `m·(1−occ·cond)` is the correct
margin shape: → 0 for resolved ballast (no cushion needed), widens for unresolved reaches. Keep it.

## The pattern (now three times — STOP building firewalls on correlates)
1. **X-veto** (reach-region in X-space): X correlates with un-paid crumbs but isn't the cause; vetoed favorite ballast. DROPPED.
2. **Sharpe conjunct**: rewarded concentrated tails; the lotteries were already dead on occ·cond. REJECTED.
3. **occ·cond product floor**: occ correlates with lotteries (they're low-occ) but the cause is cond; the product double-charged occ and parked the cheap engine. SPLIT to cond-only firewall (v14).

Each time the extra/wrong conjunct **caught nothing live** (the bad thing was already dead on the true
cause + breakeven) and **rejected something real**. The firewall gates the cause. Full stop.

## Observable signature (v14)
Moving the firewall from occ·cond to cond recovered exactly 4 cells, lost 0: c5/c6 (cheap engine-start,
+4.9 SE), c12/c36 (frequently-visited borderline-cond, +3.6/+1.3 SE). c44 still PARK-noise (cond 0.33
kills it). Ballast intact. v14 strictly dominates v13's fire set.

---

# DOCTRINE NOTE (v14 LOCK) — `cond` is per-mode, not diluted-global. Test-quantity == fired-quantity.

**Opus's seam 4 (bimodal cells parked by a unimodal cond statistic) was REAL but already pre-solved.**
The danger: if `cond` were measured against a single global consensus center over ALL bootstrap draws,
a bimodal-but-sharp cell would score low cond purely because its mass splits across two tight modes
straddling the blend point — the exact artifact that once called c5 "noise." The fear was that this
artifact had reincarnated inside the firewall statistic.

**It hasn't.** `boot_modes` splits the draws into ≤2 modes FIRST (line 47–48), then measures `cond` on
`draws[inc]` — *this mode's own cluster* — against *this mode's own center* (line 61). `cond` is the
within-mode conditional stability of the fired (lowest) mode. `occ` carries the between-mode split.
They are already decomposed exactly as the c5-vs-c44 falsifier did it.

**The airtight proof (exact global-cond recomputed from re-drawn bootstrap):**
| cell | per-mode cond | global (unimodal) cond | fires? |
|---|---|---|---|
| c5 | 0.72 | **0.21** | EXIT (+4.93 SE) |
| c6 | 0.78 | **0.04** | EXIT (+4.89 SE) |
| c36 | 0.51 | 0.49 | EXIT (+1.31 SE) |

c5/c6 — the cheap bimodal engine-start — fire ONLY because the firewall uses per-mode cond. A global
statistic reads them at 0.21 / 0.04 (noise) and parks ~$10 of edge. The per-mode statistic is
load-bearing, not incidental.

**Over-recovery check:** c17/18/21 pass the cond firewall (per-mode 0.54–0.77, trustworthy centers) but
are still parked PARK-engine by the breakeven gate, because their low occ makes them sub-1-SE on
breakeven. Firewall lets the trustworthy-but-infrequent center through; the economics catch the
infrequency. End-to-end architecture confirmed.

**The unifying principle (what closed the null, the band, the centroid, and now the firewall):** the
statistic that gates a decision must be computed on the SAME object the readout acts on. The readout
fires the lowest mode; the firewall judges that lowest mode's own within-mode cond. Test-quantity and
fired-quantity are unified — no structural gap remains for a special-cell to hide in. Every gate is now
(a) on the cause and (b) computed on the fired object. **ATP_MAIN exit LOCKS at v14.**
