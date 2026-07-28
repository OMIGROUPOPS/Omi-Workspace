# Schedule-Liar Controlled Engine Stop

## Status

**STOPPED_AND_CONTAINED.**

The only root-cron line capable of launching `live_v4.py` was disabled with
the named temporary maintenance marker. The exact pre-edit crontab was backed
up first. Twelve tennis entry buys / 60 contracts were cancelled, every
whole-contract holding was covered by a resting exit, and PID `3504442`
received one SIGINT.

The main loop did not reach `shutdown_drain_begin`. Its existing internal
17-second shutdown watchdog fired and terminated the process. No second
signal and no SIGKILL were sent.

## Frozen engine identity

- VPS HEAD during the ceremony:
  `fd4abec0f3d464634ee1d61ac02f6c977c41fb3c`
- Pre-stop PID: `3504442`
- Post-stop process count: `0`
- `live_v4.py` blob:
  `f1857199164664037fef41b024e60f27fa373548`
- Source SHA-256:
  `834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54`
- Source size: 997,352 bytes
- Configuration SHA-256:
  `3d5b07af10523e9b724f019dc367e4cf74b93f4dd66c0ff7bed0d347c72722a1`

Source and configuration bytes were unchanged.

## Keepalive inhibition

The raw pre-edit root crontab was absent at the backup path before creation
and is frozen at:

`/root/root.crontab.pre_schedule_liar_stop_20260728_e7004235.raw`

- Backup SHA-256:
  `4c38967f85112908020b7207f491a8486cbfc9c70a8b9d6c8cc5d0a2500c98f4`
- Backup size: 6,081 bytes
- Backup mode/owner: `0400 root:root`

Exactly line 17 changed. The replacement is:

```text
# TEMP_MAINTENANCE_SCHEDULE_LIAR_CONTAINMENT_20260728 */2 * * * * U=$(df --output=pcent / | tail -1 | tr -dc 0-9); [ "${U:-100}" -lt 90 ] && ! ps -C python3 -o args= | grep -q "live_v4.py" && tmux new-session -d -s live_v4 "cd /root/Omi-Workspace/arb-executor && ulimit -n 262144 && python3 -u live_v4.py >> /tmp/live_v4.log 2>&1"
```

Installed crontab SHA-256:
`0e2af22e4ab536b4273e61d9251359eda71e369fb8591f22443c66aa88709926`.
All other lines remained byte-identical and in order. The installed file has
zero active `live_v4.py` launch lines. Cron restoration is prohibited until a
future independently audited and separately authorized integrated deployment
ceremony.

## Five-contract holding reconciliation

The newly observed holding was
`KXITFMATCH-26JUL28LAZGHE-LAZ`.

- Entry order: `70cba478-f1ec-4f53-b947-cce2522597f6`
- Entry: 5 at 26 cents
- Entry fill: `2026-07-28T10:15:32.167242Z`
- Protective exit:
  `6ca81fa8-62f7-4a5a-891d-a9db0637cabf`
- Exit: 5 at 33 cents
- Exit fill: `2026-07-28T11:01:56.800031Z`

The exchange showed no current unsettled LAZGHE position. It was fully exited
before this ceremony, so no protective heal was placed.

## Entry purge and pre-stop invariant

The committed cancellation-only sweeper cancelled the 12 entries / 60
contracts in the fresh census. All twelve were independently re-read as
`canceled`, with zero fills. No entry was resting immediately before SIGINT.

Pre-stop:

- Exit orders: 12 / 50 contracts
- Held markets: 11 / 50.58 contracts
- Whole-contract holdings: exactly covered
- Named residue: 0.58 contract in
  `KXWTACHALLENGERMATCH-26JUL26ARSANN-ANN`

The running C47 law explicitly names sub-share residues as bot-invisible with
integer required exit quantity zero.

## Signal and shutdown

- SIGINT timestamp: `2026-07-28T12:40:23.774914916Z`
- Signals sent: one SIGINT
- Second signal: not sent
- SIGKILL: not sent
- Internal `entry_resting` states: 49
- Raw budget: `5 + 0.25 * 49 = 17.25` seconds
- Source integer budget: 17 seconds
- Authorized second-signal deadline: 27 seconds

The process was still present at 21.141 seconds. The source then logged:

```text
[STOP] shutdown budget (17s) exceeded -> hard exit
```

It was absent by the 44.503-second observation. Exact subsecond process-exit
time is unavailable; the report preserves the observed bounds instead of
inventing precision. The exit path was the running source's existing
watchdog, not a second operator signal.

## Post-stop proof

Twenty-three samples from `2026-07-28T12:42:36.789611958Z` through
`2026-07-28T12:48:12.226781360Z` showed:

- process count zero;
- no `live_v4` tmux session;
- zero active keepalive lines; and
- the same inhibited crontab hash.

Four keepalive opportunities at 12:42, 12:44, 12:46, and 12:48 UTC passed
without a replacement process.

Final fully paginated exchange state:

- Tennis entry buys: 0
- Exit orders: 12 / 50 contracts
- Held markets: 11 / 50.58 contracts
- Natural post-stop exit fills: 0
- Drain-replay adoption rows: 0

Every pre-stop exit order ID, ticker, price, remaining quantity, and status
was unchanged. Every holding ticker and quantity was unchanged. No conception
or entry-order receipt appeared after SIGINT. All unrelated tmux sessions and
key safety/data services remained active.

## Ruling

Operational containment now passes for **read-only integrated PRE-RUN
construction**. This receipt does not authorize deployment, audit approval,
restart, or cron restoration.

The engine must remain stopped and the temporary cron marker must remain in
place until the integrated P0 REAL-START plus CASUKA candidate receives a
fresh independent PASS and a separate operator deployment/restart
authorization.
