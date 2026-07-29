# Window-1 T2 scoring-package V5 PRE-RUN

Status: **SCORE-FREE / NOT AUTHORIZED / NOT EXECUTED**

V5 corrects construction-test honesty only. The frozen V4 runtime semantics
and every V4 package artifact remain unchanged. The sole inherited-file edit
is `arb-executor/tests/test_window1_t2_scoring_package_v4.py`.

The V4 construction tests made three real-development scorer-call attempts,
completed one in-memory event row, completed zero candidates, and persisted
zero result rows. V5 records that truth additively; V4 is not amended.

The corrected tests use three synthetic scorer calls and reject all 804 frozen
development event IDs before importing the scorer. The real population is
limited to 6432 prepared-call inspections through
the shared V4 no-score seam, with zero scorer calls.

Input-bundle SHA-256: `649a63f79a1b5ffb4fb50199df9029a2e78b1df3af6678e611bd011e4fd056dd`.

No V5 authorization or results directory exists. C/PC/IC/S, frontier, regret,
attribution, ranking, selection, and performance remain null. No holdout,
live, network-runtime, Kalshi, or trading surface was accessed.
