# V52i Iteration 8 - depth-informed level selection

Date: 2026-08-13

V52i changes exactly clause 3/N4 level selection over frozen V52h. The
incumbent live read must first earn authority. Only then may two recorded
depth priors refine the target downward inside the live post-onset observation
bounds. The priors never create authority, withdraw authority, block a post,
or raise a target. Clauses 1, 2, 4, 5, and 6, the disagreement referee,
trades-as-truth crediting, scavenger OFF, and `REFLEX_POST=0` are frozen.

The two operator-bound roles are `G_GRID_LEVEL_DISCOUNT` and
`G3_DIP_RECOVERY_GRADIENT`. G3 is the explicit `G3` candidate in the Greek
instrument registry at `2d48e4ee65e2d4b320accafcd4ac39669591d64b` and moves
from `UNVALIDATED-CANDIDATE` to `UNDER-VALIDATION_V52I` only for this run.
There is no separately named G-grid asset in that registry. The G-grid role is
therefore bound honestly as the under-validation behavioral weighting use of
the already validated P1 THE GRID cell-conditional discount; P1's bytes and
canonical CLEAN status are unchanged. No parallel surface is invented.

The fixed observation population is five pins plus 25 fresh events. The seed
is derived from source implementation commit
`17623dce8efe139f0825226a5bf07aba7a9a2a7a`; seed SHA-256 is
`279f91bad0c55415c352197e5549cd6948dda6299a4de0c5473cfdcf0e34f5c0`.
The fresh 25 has zero overlap with every V52b through V52h fresh cohort.

V52h and V52i each observe 18 complete-at-delta, 10 partial, and two neither;
both conserve to 30 and observe zero complete-at-loss. V52i records 24,597
receipt-level depth target refinements across 57 affected action streams, but
the credited entries and outcomes do not change. Completes are not reduced
and all pins are unharmed.

The bought-above-later-floor claim does not validate. Across 46 credited legs,
the signed entry-minus-post-onset-floor distribution is identical before and
after: median 1 cent, p75 2, p90 16, total 202. Restricting to the 30 positive
gaps gives median 2, p75 6, p90 16, total 202. Thus the distribution does not
shift toward zero. V52i creates zero new one-sided exposures; the frozen V52h
comparison remains six, with its already receipted durations.

Every one of 395,073 decision receipts continuously records N2/N4/N5. Exactly
two under-validation candidate identities appear, every use carries source
SHA/status provenance, canonical CLEAN remains unchanged, and no unvalidated,
quarantined, superseded, or fallback asset loads. The pair-budget records
conserve with zero joint-target sum above 99, and `REFLEX_POST=0`.

Two clean builds are byte-identical. Nineteen focused and inherited suites
pass 790,744 assertions with zero failures, omissions, or deselections. This
is a 30-game observation, not a disposition-804 run or an operative ruling.
No sealed population, deployment, authorization, live, network-runtime,
order, position, exit, settlement, or DCA action occurred.

Canonical package:

- `.claude/window1_live_v4_replay/v52i_depth_informed_level_selection_20260813/`
