# Schedule-Liar Tennis Operational Mitigation

## Status

**BLOCKED — HALT CONTROL UNAVAILABLE.**

The running engine has no documented persistent tennis-scoped or global
operator conception pause that both preserves exits and cannot self-clear.
The only in-memory `_conception_halt` is audit-derived and is cleared by an
unrelated passing `halted_reaudit`. It was not activated or misrepresented as
containment.

## Frozen lineage

- Receipt branch: `codex/ops-schedule-liar-containment-20260728`
- Receipt parent: `030e5d534a6b6bced9b6d360eb9b36ef18defa55`
- Pre-action VPS HEAD: `030e5d534a6b6bced9b6d360eb9b36ef18defa55`
- Final observed VPS HEAD: `e8a14aedab6d2d0d6538771654cfafe3054d8f5f` (advanced by an external,
  unattributed actor; running source was unchanged)
- Live PID: `3504442` before and `3504442` after
- `live_v4.py` blob: `f1857199164664037fef41b024e60f27fa373548`
- SHA-256: `834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54`
- Size: 997,352 bytes

## Authorized cancellation

- Initial resting tennis entries: 73 orders /
  365 contracts
- Replacement/reposted entries found after the initial census:
  16 orders /
  80 contracts
- Total entry buys cancelled: 89 orders /
  445 contracts
- Independently verified final status: 89 `canceled`,
  zero still resting
- Final resting tennis entries at 2026-07-28T05:35:21.947988Z: **0**

No sell order was cancelled. No replacement entry was posted by this tool.

## Exits and holdings

- Resting exits before: 23 orders /
  105 contracts
- Resting exits after: 15 orders /
  65 contracts
- Exit orders that left the book: 8; all independently
  verified `executed`
- Holdings before: 22 markets /
  105.58 contracts
- Holdings immediately after the cancellation pass: byte-equivalent ticker /
  quantity map
- Holdings after observation: 14 markets /
  65.58 contracts

The holding reductions correspond to the executed exits. This tool did not
mutate positions or cancel sells.

## Observation

- Active observation: 1147.711
  seconds total
- Longest continuous segment:
  425.078 seconds
- Complete reconcile receipts: 3
- New entry fills observed: 0
- New/replacement entry orders cancelled after initial census:
  16
- Final resting entry buys: 0

The same live PID and source bytes remained active. The heartbeat file was
stale/internally inconsistent even though process and reconcile activity
continued, so heartbeat freshness is not claimed.

## Decision

Cancellation reduced immediate exposure, but it cannot guarantee suppression:
the engine reposted entries because no durable halt exists. Status is
**BLOCKED**, and integrated PRE-RUN construction remains blocked on lawful
operational containment. Operator direction on a controlled engine stop or
another existing proven control is required.

No deployment, restart, configuration change, halt mutation, position
mutation, sell cancellation, settlement/DCA action, integrated-package
construction, or T2 work occurred.
