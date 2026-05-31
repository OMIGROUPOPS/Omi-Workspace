# Seam 5 — RESOLVED. Both proposed magnitude gates FALSIFIED; close = MIN_OCC + intact cushion + B>=1000

Branch `blend/agent-derivation`. Supersedes `ca0e71c` (the "open fork" handoff).

## The fork is closed by the tape, NOT by a new gate. Opus's magnitude-gate call is FALSIFIED.

Opus proposed: drop the SE-relative cushion as the binding gate, replace with an absolute-EV-in-cents
floor (E_min). Predicted a 5x plateau gap (0.3c park / 1.5c fire), ballast-safe, knob-stable. **Three of
his four diffs refute it. The tape ruled against him on the exact point (4) he flagged as least sure.**

### REFUTATION 1 — E_min BREAKS c44 (the noise control). Disqualifying.
c44 X33: hit=0.610, be=0.567, **cushion=0.671**, EVf=+2.97c. Under v14 it PARKS because hit (0.610) <
cushion (0.671) — **the cushion IS the gate keeping the noise control parked.** Opus's "drop cushion as
binding, keep only loose hit>=be" lets c44 pass (0.610>=0.567), and the 2.97c EV clears any E_min, so
**c44 FIRES.** The cushion is load-bearing for safety; it cannot be demoted. The absolute-EV floor does
not subsume its role.

### REFUTATION 2 — there is NO plateau gap. The EV distribution is a smooth continuum.
Sorted lowest-fireable-peak EVf across the board (cents):
`0.23, 0.29, 0.53, 0.59, 0.64, 0.71, 0.88, 1.00, 1.17, 1.22, 1.23, 1.59, 1.59, 1.59, 1.61, 1.81, 1.85,
1.87, 1.92, 1.96, 2.00 ...` — biggest step is ~0.17c. No 5x gap anywhere. Any E_min slices a continuum
and flips boundary cells arbitrarily: the third-decimal fragility doesn't dissolve, it MOVES from
hit-space to EV-space. Plateau sweep confirms: every E_min step drops a different cell (0.5->c38/c40,
0.75->c83, 0.9->c72, 1.0->c37/c77, 1.2->c53/c57). Not flat. Not derived. Tuned.

### REFUTATION 3 — Opus's point (4) realized: E_min parks LEGITIMATE cheap-certain exits.
Full engine sweep finds high-occ near-certain cheap modes banking < 1c BY CONSTRUCTION (cheap X => few
cents even at high hit): c72 X4 (0.88c, occ=0.88, hit=0.96 — a near-lock), c77 X1 (1.00c, hit=1.00),
c83 X2 (0.71c, hit=0.98), c57 X3 (0.64c). E_min cannot tell these from genuine thin smears (c38 0.29c).
**EV-in-cents is the mirror of mse:** mse punished ballast's thin MARGIN over a high breakeven; EV-cents
punishes cheap exits' thin CENTS. Neither single axis separates quality at the cheap end.

## What actually closes seam 5 (no new gate)

v15 = v14 firewall + Opus's MIN_OCC prominence guard (his ONE correct instinct) + cushion UNCHANGED,
run at **B>=1000, smooth in {1,2}.**

- **X7 phantom fixed by MIN_OCC=0.10 alone** (shoulder-bumps aren't modes). Flat plateau [0.08,0.20].
- **Cushion stays intact** — it parks c44, c38(@B300), c75. It was never the wobble cause.
- **The "knife-edge cohort fragility" was a B=300 SAMPLING ARTIFACT.** At B>=1000 the cohort resolves
  deterministically: c42->PARK, c74->PARK, c13->X11 (the defect, FIXED), c38->fires X5/6. This is exactly
  Opus's OWN diagnosis ("small B -> spurious instability; fix is B, not a coarser tool") — he was right
  about the CAUSE (B) and wrong that a new gate was needed.
- **Residual wobble: c62, c75 flip ONLY at smooth=3** (over-smoothing erases/merges their modes).
  smooth in {1,2} is identical for both at B>=1000. So: cap smooth at 2.

## SYNTHESIS — both agents partly right; the tape shows the real structure

B=1000 sharpened modes but did NOT kill the knife-edge: a band of ~6 cells (c29/c37/c38/c41/c42/c61/
c62/c79) clusters against the cushion boundary, decided at the +-0.02 level (c61 fires +0.006, c42 parks
-0.004 — statistically identical). So the wobble is NOT pure B-noise. AND one fired cell, **c38, banks
+0.08c** — Opus's objection ("an exit worth a fifth of a cent isn't a trade") is VALID for c38, even
though his EV-floor-as-PRIMARY-gate was falsified. Synthesis: keep cushion binding (safety), add a LOW
secondary EV-veto purely to drop bank-nothing cells.

**Secondary EV-veto has a real plateau [0.25, 0.75]c** (identical EXIT-set across the band — drops
EXACTLY c38 (0.08c) and nothing else). Set EV_VETO=0.5c (plateau center). At 1.0c it wrongly eats
legitimate cheap-certain exits (c72 0.88c, c37 0.59c) — confirming the primary-gate version was wrong.
c72 (occ 0.88, hit 0.96, near-lock) SURVIVES at 0.5c — the veto is low enough to keep cheap-certain
engine exits an E_min=1.0 would have killed.

## Lock config
v14 firewall (cond>=FLOOR, per-mode, occ as cushion-scaling) + peak-readout (scan low->high, fire lowest
peak with occ>=MIN_OCC AND cond>=FLOOR AND EVf>hold AND hit>=be+M_CUSHION*(1-occ*cond) AND EVf>=EV_VETO)
+ GAP REMOVED.
Params: MIN_OCC=0.10, EV_VETO=0.50c, B=1000, smooth=2, FLOOR=0.50, M_CUSHION=0.15, WIN=3.

Gate stack, each on its own CAUSE: cond (resolvability) / occ (is-it-a-mode, prominence) / cushion
(rate-sanity + safety, parks c44) / EVf>hold (beat-settling) / EV_VETO=0.5c (is-it-worth-trading,
drops the one null exit). None is an SE-relative margin.

## Final census (B=1000, smooth=2, EV_VETO=0.5)
EXIT=25: [5,6,10,11,12,13,14,15,16,30,31,32,33,34,35,36,37,61,62,72,78,80,86,87,91]. c44 PARK (SAFE).
c13->X11 (defect fixed), c10->X8 (recovered), ballast c91/86/87 preserved, c36 seam-3 recovery kept,
c72 cheap-certain kept, c38 (0.08c null) dropped. Residual wobble = 1 cell (c29, smooth1 fires / smooth2
parks; banks ~4c at a coin-flip hit margin) = irreducible labeled-risk-dial, immaterial.

## Verification (B=300 confirmed; B=1000 full-board census pending regen)
- c44 PARK at every B, every smooth. SAFE.
- c13 EXIT X11 +2.7c at every B/smooth. DEFECT FIXED (vs v14 which parked it via GAP merge).
- c10 EXIT X8 recovered. Ballast c91/c86/c87 EXIT preserved. c5/c6/c11/c12 fire true modes.
- smooth {1,2} set-stable at B>=1000.

## Concession ledger (relay to Opus, per "leave it on the table")
Opus was wrong 3x on c13 specifics (reactivation story; "shattered, reach wins"; "parks honestly").
He was wrong here too: the magnitude gate breaks c44 and has no plateau. He was RIGHT on: MIN_OCC
prominence (the actual fix), and the meta-call that B (not a coarser peak-finder) cures small-B
instability. Net for the file: trust the tape over either agent's structural read of the cheap cells;
both of us keep under-modeling them.
