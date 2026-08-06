# Boot Gate Stage B — recorder reconciliation and sealed stream

Status: **STAGE_B_PASS**. The authoritative WS recorder was alive but degraded by repeated reconnect gaps, so it received one documented recorder-only restart and was adopted under the corrected existing guard. The trading engine remains stopped and the containment cron marker remains installed.

## Recorder and coverage

- Pre-action recorder PID 325602 had run since 2026-07-30 08:49:47 ET. Its log contained 2,861 WS errors and 2,718 ping timeouts, so it was classified degraded rather than silently called healthy.
- One clean recorder-only restart produced PID 3459414 and a new immutable stream. SIGINT did not exit within 20 seconds; one SIGTERM exited in one second. No engine process was launched.
- Output: `/root/Omi-Workspace/arb-executor/data/durable/ws_depth_recorder/ws_*.jsonl.gz`.
- Archive plus live spool: zero hourly filename gaps from 2026-07-28 through the construction census. This is filename continuity, not a claim of frame continuity across the observed short reconnect/resubscribe intervals.
- Secondary legacy REST recorder remains running but is not the authoritative sealed stream.
- Recorder restarts performed by Stage B: one.

## Corrected touch law and seal

TOUCHED means consumed by evaluation, replay, diagnostic, or fix-motivating citation. Raw capture, storage commits, mechanical accumulator output, capture-integrity reconciliation, and seal metadata are not touch.

The 172-event re-audit finds one genuine touch (`KXATPCHALLENGERMATCH-26JUL27SAHTUR`) and seals 171 untouched, floor-passing events. The event-list SHA-256 is `06ede0264a196bbebc005785c3ffdee5a840afe1a617f86f0354eedf65ac4313`. The N>=60 condition is satisfied; no exam ran because Stage B does not invent the missing corrected-population boundary package or executable replay ceremony.

## Forward stream and nightly reconciliation

- 60 newly discovered events were tagged capture-only at activation; no decision-relevant consumer ran.
- Registry writes are append-only and protected by a non-blocking single-writer lock.
- The nightly 02:00 ET N=20 job implements `938dca474e8bc4d96b17095e2aaa7cbb2fe97a87`.
- First pass: 20/20 PRINTS_FAITHFUL; 4,127 exchange trades and 4,127 stored prints; every mismatch count zero.
- Shape-accumulator output is capture-class until a later decision-relevant artifact consumes an event.

## Containment and drift

- `live_v4.py` process count: zero.
- Active `live_v4.py` cron launch lines: zero; the schedule-liar containment marker is unchanged.
- `live_v4.py` was not edited. Its pre-existing working-tree drift remains +692/-39, working blob `c25cd3129248710a665d77eb815a9df6a93c9009`, SHA-256 `25698d80642524c70f39d850ef0a7041edda6df9c4d2dbac0c666d58aab56a63`.
- The drift mixes capture, replay, observe-only, and decision-affecting changes. It is not adopted and is not Stage-C ready.
