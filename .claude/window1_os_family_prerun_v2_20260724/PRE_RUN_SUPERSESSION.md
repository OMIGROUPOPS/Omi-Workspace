# Window-1 PRE-RUN supersession

This PRE-RUN supersedes commit
`a673ac2d813e32b6b328e2d86bbb9506dbadb852` before any candidate event was
scored. The first frozen invocation spent its ten-minute command window
building a Python byte-range index over the 1.77 GB normalized true-print
archive and emitted no event-progress line or result artifact. Its orphaned
process was identified by exact command line and stopped.

The scoring, feature, start-boundary, metric, candidate, ablation, and data
laws are unchanged. The superseding executor consumes the already-validated
804-event market-data cache created by the frozen fit runner from that same
hash-pinned complete true-print archive and top-five materialization. The new
PRE-RUN binds all 804 compressed cache objects as a hash set and freezes the
original cache key. At event read time it rechecks event and ticker identity,
time coverage of the guarded window, snapshot ordering, unique trade
identity, positive print size, and the frozen cache key.

No result directory, candidate metric, or holdout evidence existed when the
first invocation was stopped.
