# Window-1 sealed-171 exam: consumed serialization failure

The exam input gate passed. The canonical public print pull contains 1,062,870
positive-size trades for 342 legs; all 1,231 pages terminated normally. The
independent nightly-method sample reconciled 155,463 exchange trades to
155,463 captured prints across 20 events with zero identity, price, size, or
taker-side mismatch.

The adapter passed decision-inertness before authorization consumption. V36
replayed all 804 development events and inspected 3,631,920 decisions; V35
replayed all 804 and inspected 3,610,317. For both brains the strict trace,
census trace, full scorecard, strict frontier, and census frontier were
byte-identical to the frozen packages. Policy mutations and sealed invocations
at this gate were zero.

The one authorized sealed process then started. It evaluated all 171 V36
events and failed before V35 began and before any score artifact was emitted.
The exact error was `RangeError: Invalid string length` at the full decision
trace `Array.join` inside `gzipRows`. The authorization is consumed: one
invocation, zero retries, V36=171, V35=0, R3=0, and zero completed scorecards,
frontiers, regret outputs, or performance conclusions. The partial results
directory is preserved with its generated start receipt unchanged.

R3 remained excluded under blocker
`4f4d546421043f187bc73e2d9ad1eca0b9cf7f36`. No live engine, account, order,
position, or trading surface was accessed. No policy was edited. Any future
exam requires a new authorization after independent audit of a bounded,
streaming decision-trace serializer; this package cannot authorize a retry.

Canonical report:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a746d17582284736f9b3a9e6c8db2bf61e9204e1/.claude/window1_fresh_holdout_exam_unblock_20260807/REPORT.md

Consumed failure receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a746d17582284736f9b3a9e6c8db2bf61e9204e1/.claude/window1_fresh_holdout_exam_unblock_20260807/EXECUTION_FAILURE.json

DEV inertness receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a746d17582284736f9b3a9e6c8db2bf61e9204e1/.claude/window1_fresh_holdout_exam_unblock_20260807/DEV_INERTNESS/DEV_INERTNESS_RECEIPT.json

Print re-pull and N=20 reconciliation:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a746d17582284736f9b3a9e6c8db2bf61e9204e1/.claude/window1_fresh_holdout_exam_unblock_20260807/PRINT_REPULL_RECEIPT.json

Exact process transcript:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a746d17582284736f9b3a9e6c8db2bf61e9204e1/.claude/window1_fresh_holdout_exam_unblock_20260807/AUTHORIZED_PROCESS_TRANSCRIPT.txt

Preserved generated start receipt:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a746d17582284736f9b3a9e6c8db2bf61e9204e1/.claude/window1_fresh_holdout_exam_results_20260807/EXECUTION_START_RECEIPT.json

VAULTED: sealed-exam authorization consumed once; no retry; no performance
result; streaming-serializer repair and fresh independent authority required.
