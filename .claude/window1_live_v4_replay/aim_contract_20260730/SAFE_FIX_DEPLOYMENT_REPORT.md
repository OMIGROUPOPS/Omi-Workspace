# Part 7 — safe-fix and retention deployment

Deployed 2026-07-30.  The trading engine remained off throughout.

## What changed

- Fill-receipt polling is enabled.
- The old atlas onset-relative timing field is refused wherever the live
  consumer expects scheduled-start-relative time.  No substitute timing
  trigger is invented.
- Schedule revisions, full-event observed starts, decision-time anchor
  lineage, and per-tick BBO/trade retention are enabled.
- The WebSocket recorder writes a unique gzip stream per process so a restart
  cannot append new ticks behind an incomplete prior gzip member.

The following remain deliberately disabled:

- sealed one-authority action;
- contention `DROP` enforcement;
- entry-table prior action;
- pair-class steering.

## Replay against the exact deployed source

Five fixed games were replayed twice from the same tape: the unchanged
four-defect control and the safe-fill-plus-clock profile.

| Measure | Control | Safe profile | Change |
|---|---:|---:|---:|
| pair completions | 0/5 | 0/5 | 0 |
| legs filled | 4/10 | 4/10 | 0 |
| silent defect signals | 8 | 0 | -8 |
| worst fill-to-engine-booking delay | 22 s | 5 s | -17 s |
| prompt bulk receipt actions | 0 | 4 | +4 |

The fixes removed the simulated unbooked-fill/naked-leg signals and shortened
booking delay.  They did not improve or damage completions in this sample.
The four additional actions are prompt receipt bookings, not new market
orders.

Replay artifact:
`safe_fix_replay_deployed/SAFE_FIX_REPLAY.json`.

## VPS state

Free space was 24 GB before and 24 GB after (50% used).  The collector
processes after restart were:

- `te_live.py`: PID 212573;
- `kalshi_price_scraper.py`: PID 212610;
- `ws_depth_recorder.py`: PID 214143.

`live_v4.py` was absent before and after.  It was not started.

The schedule revision table existed and had 538 rows on its first verification.
The full-event observed-start table existed and had zero rows, as no match had
gone in-play after restart.  The first new session-safe WebSocket stream
retained 522 subscribed markets and emitted the required receive timestamp,
staleness status, raw-frame hash, parsed frame, and BBO field.

## Installed SHA-256

| VPS file | SHA-256 |
|---|---|
| `live_v4.py` | `539a832e52470b43be0f5dc1aecebfbdfa6b0433a3d66d1ef2e47288da917685` |
| `config/deploy_v5_live.json` | `87940c06a7a51048068f60d946910ef854510e15cca7e59b2079db9c1a8270b6` |
| `kalshi_price_scraper.py` | `e1e119f56d8453bbd417ef61a167b875c9212c142a71da325217be897b9ff01e` |
| `te_live.py` | `3e51797bb2de514e5628278c22eb04c2da506591b93dd8cf1157d7c39e930654` |
| `ws_depth_recorder.py` | `c9a5970c5a8a5106ae2d5ed348bf8cc202cbcc883a61720ca56853370e0a8cae` |

The pre-deployment bytes are preserved under
`/tmp/window1_20260730_pre` on the VPS.

## Verification

- two existing live safety suites: PASS;
- 25 focused contract/retention/wrongness tests: PASS;
- restart-safe recorder test subset: 3/3 PASS;
- all deployed Python files: AST/compile PASS;
- deployed JSON: parse PASS;
- local, staging, and installed hashes: exact.
