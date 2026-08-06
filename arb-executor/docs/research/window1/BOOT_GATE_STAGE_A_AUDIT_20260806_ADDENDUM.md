# Boot gate Stage A — read-only inheritance audit

Stage A is complete. Stage B and Stage C were not authorized and were not
started. Restart readiness is **NOT_READY**.

The fresh VPS audit found no `live_v4.py` process, no resting exchange order,
and no unsettled exchange position. The controlling July 28 stop receipt held
12 exits / 50 contracts, not 17. Five of those order IDs now report executed;
seven are not returned by the historical order lookup. Kalshi reports a
$398.2753 balance and zero portfolio value.

The VPS checkout is not a clean cutover base: HEAD is
`7036ace045c6ee0e45b9c4bdc956c54906d21afa`, with 13 modified and 12,418
untracked paths. HEAD `live_v4.py` remains blob `f1857199`, while the working
file is uncommitted blob `c25cd312` (SHA-256 `25698d80`, 1,025,887 bytes), a
692-addition/39-deletion working diff. Root cron still has zero active
`live_v4.py` launch lines and the containment marker, but its full hash has
drifted from the controlled-stop hash. A standalone `depth_recorder.py`
process is already running; that fact must be reconciled before Stage B.

Canonical report:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/322a170ea7ad1e9431a26e375540eb75277ae29b/.claude/boot_gate_stage_a_audit_20260806/STAGE_A_REPORT.md

Complete read-only snapshot:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/322a170ea7ad1e9431a26e375540eb75277ae29b/.claude/boot_gate_stage_a_audit_20260806/VPS_AND_EXCHANGE_READONLY_SNAPSHOT.json

Readiness receipt:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/322a170ea7ad1e9431a26e375540eb75277ae29b/.claude/boot_gate_stage_a_audit_20260806/STAGE_A_READINESS_RECEIPT.json
