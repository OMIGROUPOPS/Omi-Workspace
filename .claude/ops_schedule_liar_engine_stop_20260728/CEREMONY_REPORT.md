# Controlled Engine-Stop Ceremony

## Result

**PRE-FLIGHT FAIL - ENGINE NOT STOPPED.**

Phase 2 failed closed because no existing documented, reversible,
`live_v4`-only keepalive inhibitor exists. The active root cron checks every
two minutes and starts `live_v4.py` in tmux whenever the process is absent and
disk use is below 90%. Observed disk use was 65%, so a graceful stop without a
separate inhibitor would not leave the engine stopped.

Changing root cron, disabling all cron, inventing a sentinel or environment
variable, changing tmux controls, or patching the engine would all exceed this
authorization. None was attempted.

No signal was sent. The same PID remained running.

## Bound receipt

- Operational receipt:
  `1ae9a9ca6e9d45e0a7b179a7e98afa48ace761c0`
- Branch: `codex/ops-schedule-liar-containment-20260728`
- Running `live_v4.py` blob:
  `f1857199164664037fef41b024e60f27fa373548`
- Running source SHA-256:
  `834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54`
- Running source size: 997,352 bytes
- PID: `3504442`
- Process start: `Tue Jul 28 00:16:01 2026`

The source identity matched the required preimage throughout the ceremony.
The VPS Git HEAD advanced externally from
`5259223484fa3b7cc5626f8577a3c9f45527070d` to
`fd4abec0f3d464634ee1d61ac02f6c977c41fb3c` while the running source bytes
and PID remained unchanged.

## Stop-mechanics proof

The running configuration enables graceful shutdown. The running source
installs SIGINT/SIGTERM handlers whose first signal:

1. immediately marks shutdown requested;
2. arms a book-sized watchdog capped at 180 seconds;
3. writes the existing drain manifest;
4. cancels tracked V4 entry bids;
5. preserves resting exit sells; and
6. returns without settlement, DCA, or position mutation.

The existing deploy stop window is 200 seconds. A second signal would hard
exit and was not sent.

This behavior is individually understood, but it is not sufficient: a later
boot can replay drained entries, and the root cron would relaunch the process.
The missing keepalive inhibitor is therefore a terminal precondition failure.

## Cancellation-only mitigation while evaluating readiness

Only the already-committed, hash-verified containment tool was used. It
cancelled tennis entry buys and never targeted sells.

### First pass

- Pre-action: 55 entry buys / 273 contracts
- Cancelled: 59 entry buys / 293 contracts
- Reposts cancelled during the observation: 4 / 20
- Final: 0 entry buys
- Exit sells: 18 / 80 contracts before and after
- Held positions: 19 / 87.58 contracts before and after
- Observation: 324.588 seconds
- Entry fills reported by the bounded log slice: 0

### Inter-pass evidence

At `2026-07-28T10:11:44.489931Z`, one new entry buy for five contracts was
resting. Exit sells were 17 / 75 contracts and held positions were
18 / 82.58 contracts.

### Second pass

- Pre-action: 1 entry buy / 5 contracts
- Cancelled: 4 entry buys / 20 contracts
- Reposts cancelled during the observation: 3 / 15
- Final at `2026-07-28T10:18:01.001794Z`: 0 entry buys
- Exit sells: 17 / 75 contracts before and after
- Held positions: 18 before, 19 / 87.58 contracts at the final snapshot
- Observation: 337.340 seconds
- Service restarts: 0

Across both passes, 63 entry orders / 313 contracts were cancelled. All 63
were independently re-read as `canceled`. Eight entry orders / 40 contracts
were newly observed after the first pass's initial purge and were also
cancelled.

The position set changed while the still-running engine and exchange
continued operating. This tool performed no position mutation and created no
orders. The exact exchange rows are preserved in the receipts; the ceremony
does not misstate the changing live state as conservation.

## Final determination

The last frozen snapshot had zero resting tennis entry buys, but this is
temporary mitigation, not containment. The engine remained live, kept
conceiving/reposting during observation, and has no authorized durable
conception stop.

- Stop attempts: 0
- SIGINT/SIGTERM/SIGKILL: 0 / 0 / 0
- Restarts: 0
- Keepalive/cron/tmux changes: 0
- Source/configuration changes: 0
- Exit cancellations by the tool: 0
- Position mutations by the tool: 0
- Deployments: 0

The requested post-stop five-minute/two-trigger observation is inapplicable
because no stop occurred. The integrated PRE-RUN containment prerequisite
remains **BLOCKED**.

Operator authorization for a separately reviewed, existing-or-explicitly
created live_v4-only keepalive inhibition control is required before a
controlled engine stop can lawfully proceed.
