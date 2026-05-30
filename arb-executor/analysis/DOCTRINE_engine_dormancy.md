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
