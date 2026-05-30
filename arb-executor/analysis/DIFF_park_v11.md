# DIFF — park_v11 (firewall wired): two of Opus's three forms HOLD; the reach-region veto is NOT derivable and collides with legitimate cheap-cell behavior

Branch: blend/agent-derivation. File: `park_v11_firewall.py`.

## Wired (Opus's corrected forms)
- **#2 resolvability = occ·cond ≥ FLOOR** (product, single global floor, epistemic gate). occ·cond = P(a resample both visits this mode AND pins its center).
- **#3 firewall** = lowest RESOLVED mode is the only fire candidate; must still clear EV/paid/supp (necessary-not-sufficient); reach-region veto on top.
- **#1 c5** → boundary (engine starts c6), single global α, no per-arm lowering.

## CONFIRMED (two of three forms hold cleanly)
**DIFF(b) — reach modes pre-screened out, as Opus predicted.** Every reach tail in the cheap zone is UNRESOLVED at occ·cond≥0.45: c5 +40 → 0.28, c6 +37 → 0.34, c17 +53 → 0.33, c7–c16 reaches all 0.02–0.22. The occ·cond floor demotes the lottery tails out of candidacy before the lowest-mode rule even runs. ✅

**NEW HAMMER passes.** Deliberately lifting c5/c6/c17 reach-mode EV above hold at disc=30 (ev 7.69/7.44/15.64 > hold) still gives `is_fire_candidate=False`. The reach can pencil positive and cannot fire — firewall is structural, not EV-dependent. ✅

## TWO FAILURES — the reach-region veto is mis-specified AND not derivable

### Failure A — `REACH_FRAC` (fraction of 94−c) is the wrong scale; it vetoes the FAVORITE BALLAST
A reach test of "center > REACH_FRAC·(94−c)" flagged c84–c92 (lowX 2–9, occ·cond 0.88–1.00) as reach, because their range Xmax=94−c is tiny (c90 → Xmax=4, so +4 reads as "reach"). These are the **highest-conviction cells in the book** — the favorite ballast — and the veto would kill them. Reach as a fraction of a truncated range is incoherent.

### Failure B (the real fork) — reach territory is NOT derivable from mode geometry; occ·cond already does the firewall's job
Classifying every resolved cell by within-cell mode structure yields three classes:

1. **UNIMODAL-resolved low** (c72,75,78,79,81–92): single tight bank, occ·cond 0.55–1.00 = favorite ballast. MUST fire. The +8 is the cell's whole identity, not a reach.
2. **low-resolved + reach-demoted** (c11–16,25,29–33,36,41,53,80): fire low, reach unresolved. Firewall perfect. ✅
3. **HIGH-resolved-only, low UNresolved** (~20 cells: c18,19,21,27,31,32,34,35,50,55,56,59–62,64,66,69–71,74): resolved mode ONLY at high X.

Class 3 is **exactly Opus's "reach-only-but-resolved" danger case** — and it's ~20 cells, not an edge case. The crux: **is c18's resolved +53 mode (occ·cond 0.56) a lottery reach to veto, or c18's genuine repeatable settlement behavior to fire?**

The marginal X-distribution of resolved-mode centers is a **continuous ramp from +2 (c92) to +53 (c18)** — there is NO gap separating "bank" from "reach." A cheap 18¢ contract reaching +53 is its *normal* behavior (it's cheap because the market expects high-end resolution), not a jackpot. c18's +53 is reliably visited and pinned (occ·cond 0.56); c5's +40 is not (0.28). **occ·cond ALREADY separates the legitimate cheap-cell reach (resolved) from the lottery tail (demoted).**

So the reach-region veto is either:
- **redundant** — occ·cond already demotes the lottery reaches (c5/c6/c7–17 all <0.45), so the veto changes nothing for them; OR
- **harmful** — any non-trivial absolute/fractional cutoff would veto the Class-3 cells (c18/19/21, occ·cond>0.5), which are legitimate cheap-cell reach behavior, not lotteries.

### Side effect of the bad veto (current baseline, with veto ON)
EXIT collapsed to 8 cells, PARK-engine=[], because the veto killed favorites (Class 1) and Class 3 both. This is the veto mis-firing, not the kernel.

## MY RECOMMENDATION TO OPUS (not co-signed — his call)
**Drop the reach-region veto. Let occ·cond≥FLOOR be the SOLE firewall, and fire the lowest RESOLVED mode unconditionally (still gated by EV/paid/supp).** Rationale: occ·cond demotes lottery reaches (c5 +40 = 0.28) while preserving legitimate cheap-cell reaches (c18 +53 = 0.56) and favorite banks (c84 +8 = 0.93). The reach-region boundary is not derivable (continuous ramp, no gap) and any setting either does nothing or amputates real cells. The NEW HAMMER still holds WITHOUT the veto, because c5/c6/c17 reaches are unresolved — occ·cond, not the veto, is what keeps them dark.

**The one thing to verify if Opus agrees:** with the veto dropped, re-confirm c5/c6 reaches stay PARK (they're unresolved, so yes) AND that no Class-3 cell's resolved high mode is actually a lottery we WANT parked. The candidate worry: does any Class-3 cell fire a high mode whose EV is a thin-kiss jackpot? That's now governed purely by EV/paid/supp — which is the gate built to kill exactly that. Diff to run on agreement: EV/paid/supp of every Class-3 fired mode at baseline.

## Status
#2 and the NEW HAMMER hold. The reach-region veto (part of #3) is mis-specified and not derivable — surfaced to Opus with the recommendation to drop it in favor of occ·cond as sole firewall. c6 engine-start also at risk (occ·cond 0.37 < 0.45 floor — occupancy 0.48 sinks it); FLOOR calibration is the remaining open knob. NOT locked. Awaiting Opus on: (1) drop reach-veto? (2) FLOOR value given it gates c6.
