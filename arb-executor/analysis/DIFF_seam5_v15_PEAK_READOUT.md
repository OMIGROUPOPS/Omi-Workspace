# Seam 5 — v15 peak-readout: BUILT + VALIDATED, with one genuine fork remaining

Branch `blend/agent-derivation`. Supersedes the `08b61f7` "seam-5 OPEN" handoff.
Method = Opus's mode-count-free readout: scan bootstrap best-X density peaks low→high, fire the
LOWEST peak that jointly clears (per-mode cond ≥ FLOOR) AND (EV>0, EV>hold, hit ≥ breakeven+cushion).
No GAP, no dip percentile, no fixed mode count.

## 1. c13 is a REAL defect — Opus's density read was wrong, his method is right

Full bootstrap (B=300, then confirmed B=1000/2000), c13 best-X plurality = **X=24 (the MID mode), NOT
reach.** Tri-modal: low[6–18] / mid[20–27] / reach[≥32]. The low region has a genuine sharp bankable
mode: **center X=11, local cond 0.90, occ 0.43, +2.44 SE, EV +2.70.** GAP=6 destroys it by merging low
into mid (GAP makes ONE cut; cannot isolate a low mode from a tri-modal cell). So the readout METHOD is
vindicated; the OUTCOME bet ("c13 parks honestly, v14 locks") is refuted — c13 FIRES X11 and v14 was wrong.

## 2. The first peak-readout build mis-fired — and the fix is NOT a significance floor

First build collapsed many cells to a cheap X7 (c11→X7, c12→X7, c13→X7). Diagnosis (`_v15_diag.py`):
the smoothed peak-finder manufactures phantom peaks on the RISING SHOULDER of a real mode (e.g. c11
X7 clmass=13 sitting at the foot of the X18 mode, clmass=176). A tight 13-draw bump has local cond=1.00
(perfectly pinned to itself) and, being cheap, a high raw hit — so it clears `hit ≥ be+cushion` and, being
lowest, fires before the scan reaches the true mode.

**Falsified fix — mse/significance floor.** Adding `mse=(hit−be)/se ≥ FLOOR` kills the X7 crumbs BUT
also kills ballast (`_v15_msefix.py`): c91 hit=0.995/be=0.994→mse=+0.05; c86→+0.30; c87→+0.57; and the
seam-3 recovery c36→+0.93 all die. This is the SAME wall seam 3 hit: a margin-in-SE gate systematically
favors the cheap engine (huge margin) and executes the high-hit ballast (tiny margin over a high
breakeven). **Margin-on-the-cluster is doctrine-incompatible.**

**Adopted fix — occupancy-prominence on the PEAK (`_v15_promfix.py`).** A peak must own ≥ MIN_OCC of
total draws to count as a fireable mode. A 13-draw shoulder-bump (occ=0.04) is not a mode; the X18 mode
(occ=0.59) and ballast clusters (c91 occ=1.0, c36 X29 occ=0.50) all survive trivially. This is
occupancy-on-the-peak, never margin-on-the-cluster, so ballast is untouched. **Flat plateau:
MIN_OCC ∈ [0.08, 0.20] gives identical results** (knob-independent). Set MIN_OCC=0.10.

## 3. Gauntlet (MIN_OCC=0.10, smooth=2, corrected low→high scan)

| cell | v15 | note |
|---|---|---|
| c13 | EXIT X11 +2.44 | DEFECT FIXED (was parked by GAP) |
| c10 | EXIT X8 +2.24 | NEW real low mode GAP hid |
| c5 | EXIT X7 | engine mode, real |
| c6 | EXIT X7 | engine mode, real |
| c11 | EXIT X18 | true dominant mode (X7 phantom rejected) |
| c12 | EXIT X18 (B≥1000) | X13 at B=300 → under-resolved |
| c44 | PARK (all smooth, all B) | NOISE CONTROL SAFE |
| c91/c86/c87 | EXIT X3/X8/X7 | BALLAST PRESERVED |
| c36 | EXIT X29 | seam-3 recovery preserved |

## 4. Census v15 vs v14 (corrected scan, B=300)

v15: EXIT 29 / HOLD 9 / PARK-engine 42 / PARK-thin 10 / PARK-noise 0.
v14: EXIT 26 / HOLD 14 / PARK-engine 24 / PARK-thin 10 / PARK-noise 16.
EXIT diff: **shared 23, added 6 {10,13,37,38,61,74}, dropped 3 {41,75,88}.**
PARK-noise→0 is a LABEL migration (every occ≥0.10 cond-passing peak with EV≤0 now lands PARK-engine),
NOT a firing change — c44 etc. still never EXIT.

## 5. Stability

- **Bootstrap-B {300,1000,2000}:** robust core stable at every B (c13→X11, c10→X8, c5/c6→X7, c11→X18,
  c61→X32, c91→X3, **c44→PARK**). Directly answers the "small B → spurious peaks" worry: the MIN_OCC
  guard holds at every B; no phantom returns. c12 needs B≥1000 to resolve (X13→X18). **Recommend B=1000
  default** (your B≥2000 is safe but 1000 suffices; 2000 changes nothing on the core).
- **Smooth-window {1,2,3}:** EXIT-set wobbles ±1–2 cells (c31/c42/c62/c79 flip) — NOT perfectly stable.

## 6. THE FORK (genuine, method-level — needs your call)

v15 cleanly resolves modes that GAP merged. That exposes a cohort GAP accidentally hid: **high-occupancy,
near-breakeven cells sitting on the cushion knife-edge.** Examples (B=300):
- c61 X32: hit 0.709 vs cush 0.70 → passes by **+0.009**, FIRES (mse +0.27)
- c41 X29: hit 0.606 vs cush 0.61 → fails by **−0.004**, PARKS (mse +0.56)
- c38 X4: hit 0.912 vs cush 0.89 → passes +0.02 (mse +0.75); center drifts X4→X5→X6 with B
- c74 X18 mse +0.33; c75 X18 fails cushion, parks.

EXIT-vs-PARK for this cohort is being decided at the **third decimal of a bootstrap estimate** — same
fragility as the smooth-window wobble. The cushion `M_CUSHION·(1−occ·cond)` shrinks to ~0 for high-occ
cells, so it gives almost no margin EXACTLY where these cells live. The robust core (c13/c10/c5/c6/
ballast/c44) is rock-solid; the fight is entirely over this knife-edge cohort.

**Open question for you:** do these high-occ near-breakeven cells belong in EXIT or PARK, and what
gates them WITHOUT a margin-in-SE floor (which kills ballast)? Candidates I can test:
(a) an EV-magnitude floor scaled to occupancy (engine-like), (b) requiring the cohort's hit to clear
breakeven by a fixed absolute pad that does NOT divide by se (so ballast's tiny-but-certain margin still
passes via its high absolute hit), (c) leave the cushion as-is and accept ±1-cell smooth wobble as the
labeled risk dial. I lean (b) — an absolute pad is ballast-safe where an SE-relative one is not — but it
needs the same gauntlet+ballast+stability proof before any lock. I have NOT locked v15.
