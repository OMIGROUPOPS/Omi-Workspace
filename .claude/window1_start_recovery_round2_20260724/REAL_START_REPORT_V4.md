# Window-1 Start-Truth Recovery Round 2

Extraction remained blind to policy decisions, placements, fills, prices,
deltas, candidate results, and success labels.  The frozen 234 exact starts
and 31 clean intervals were preserved.  Only the 539 previously blocked
events were eligible for a new ruling.

## Start gate — PASS

- D = 804
- exact starts = 687
- clean causal intervals = 31
- live-by-only = 52
- contradictory = 14
- schedule-only = 20
- unresolved = 0
- positive-capable population = 718
- gate required = 603
- gate margin = 115
- newly recovered exact starts = 453
- residual timing-blocked population = 86

The new exact source is the retained TennisExplorer finished-result start
clock, the historical provider surface used by `te_live.py` and named
`te_honest` in the chronological Vault.  Promotion required the exact same
two structured-target players (surname plus first initial), tournament,
date corridor used only for identity alignment, provider match ID, a
completed result, and a minute start clock.  The displayed
Berlin/Prague/Vienna timezone was converted with `Europe/Berlin`; schedule
was never used as an interval endpoint.

11 otherwise crosswalked events
remain contradictory because a higher-precedence raw milestone receipt
still said `not_started` at or after the result clock.  Lower-precedence
tape/live-by disagreements are retained in the conflict ledger; the exact
result clock controls by the frozen source precedence rather than by which
value would improve policy performance.

The six-family/24-policy development preflight remains frozen and unscored.
No candidate runner, tuning, ablation, or holdout evaluation was executed.
