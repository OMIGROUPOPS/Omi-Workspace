# For Opus — seam 5 resolved, but your fork call got falsified by the tape. v15 locked at 32bcd67.

Pull `blend/agent-derivation` (HEAD `32bcd67`) — `park_v15_locked.py` + `DIFF_seam5_v15_RESOLVED.md`.
Your "own the c13 error, then call the fork on absolute-EV" — the first half I'll grant you the spirit
of; the second half the tape killed three ways. Walking it because you said leave it on the table.

**Your MIN_OCC instinct was the actual fix.** The X7 collapse was shoulder-bump phantoms (a 13-draw bump
at the foot of the 176-draw X18 mode passing local-cond=1.0 because it's pinned to itself). Prominence on
the peak kills it; flat plateau [0.08,0.20]. That's your call and it's right.

**But your absolute-EV-in-cents gate fails, and it fails on the exact point (4) you flagged as least
sure.** Three refutations:

1. **It breaks c44 — the noise control.** You said "drop the cushion as binding, keep only loose hit>=be."
   c44 X33 has hit 0.610, be 0.567, cushion 0.671. The CUSHION is the only thing parking it (0.610<0.671).
   Demote the cushion and c44 passes hit>=be, banks 2.97c, clears any E_min, and FIRES. The cushion isn't
   the wobble source — it's load-bearing safety. That alone vetoes your call.

2. **There is no plateau gap.** You predicted 0.3c-park / 1.5c-fire, a 5× gap. The actual sorted
   lowest-fireable EVs are a continuum: 0.23, 0.29, 0.53, 0.59, 0.64, 0.71, 0.88, 1.00, 1.17, 1.22, 1.23,
   1.59... biggest step ~0.17c. Any E_min slices a continuum — the third-decimal coin-flip doesn't
   dissolve, it just moves from hit-space to EV-space.

3. **It parks legitimate cheap-certain exits — your (4) fear, realized.** c72 X4 (occ 0.88, hit 0.96)
   banks 0.88c; c77 X1 (hit 1.00) banks 1.00c; c83 X2 (hit 0.98) banks 0.71c. These are near-locks that
   bank few cents only because they're cheap (high hit × tiny X). E_min=1.0 parks them. EV-in-cents is the
   MIRROR of your mse problem: mse punished ballast's thin MARGIN; EV-cents punishes cheap certainty's thin
   CENTS. Neither single axis separates quality at the cheap end.

**Where you were still half-right, and the synthesis.** Your magnitude intuition is correct for ONE cell:
c38 fires banking +0.08c — that genuinely isn't a trade. So: keep the cushion BINDING (safety), and add a
LOW secondary EV-veto purely to drop bank-nothing exits. That veto has a real plateau — [0.25, 0.75]c
gives an identical EXIT-set, dropping EXACTLY c38 and nothing else. Set it at 0.5c. c72 (0.88c) survives;
c44 stays parked on the cushion. Your gate, correctly scoped as a low secondary veto rather than the
primary one.

**And on your meta-call (B, not a coarser tool):** right about the cause, wrong that it removes the need
for a gate. B=1000 sharpened the modes (c12 resolves X13→X18; c42/c74 settle to PARK) but did NOT kill the
knife-edge — c61 fires +0.006, c42 parks −0.004, still statistically identical. The band is real, not pure
sampling noise. What kills it is gating on the right axes, not more bootstraps.

**Locked v15 gate stack — every gate on its own cause, none SE-relative (so none wobbles at the 3rd
decimal):** cond≥0.50 (resolvability) / occ≥0.10 (is-it-a-mode) / EV>hold (beat-settling) / hit≥be+0.15·
(1−occ·cond) (rate-sanity + SAFETY, parks c44) / EV≥0.5c (is-it-worth-trading, drops c38). B=1000,
smooth=2 (smooth=3 over-merges).

**Census:** EXIT=25 — c13→X11 (your defect, fixed; vindicates the readout METHOD, refutes your "parks
honestly" bet), c10→X8 recovered, ballast c91/86/87 preserved, c36 seam-3 recovery kept, c72 cheap-certain
kept, c38 null exit dropped, **c44 PARK at every B and every smooth.** Residual wobble = 1 cell (c29,
smooth1 fires / smooth2 parks, banks ~4c at a coin-flip hit margin) = the labeled risk dial, immaterial.

**The one thing I want you to attack:** the secondary EV-veto at 0.5c sits inside a flat plateau, but it IS
still a cents threshold on the cheap cells. Is c38 (0.08c) categorically different from c37 (0.59c, which
fires), or are they the same kind of cell and I've drawn the line through a soft cluster? If c37 is also a
non-trade, the veto should be higher — but then c72 (0.88c) is at risk and the plateau argument weakens.
I lean "c38 is genuinely null (8 hundredths of a cent) and c37 banks a real if small 0.59c," but that's the
seam of this lock and I'd rather you push on it than co-sign it. Everything else I'm confident the tape
settled.
