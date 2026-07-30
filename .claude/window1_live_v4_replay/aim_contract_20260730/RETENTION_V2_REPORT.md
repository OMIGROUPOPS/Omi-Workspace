# Window-1 retention V2

## What is added

### Schedule revisions

`kalshi_price_scraper.py` now polls all six tennis series and creates
`kalshi_schedule_revisions`. A row is retained whenever a market's
schedule-bearing fields change:

- open time;
- close time;
- expected expiration;
- expiration;
- latest expiration;
- occurrence datetime;
- status.

Each revision carries first/last observation time in UTC, the canonical
schedule-field payload and hash, the exact HTTP response SHA-256, ticker,
event, series, and request path. Repeated unchanged observations update only
`last_observed_at_utc`; they do not fabricate revisions.

### Per-tick BBO and trades

The always-on, read-only `ws_depth_recorder.py` now covers all six tennis
series and reconstructs the BBO on every order-book snapshot/delta while
retaining the original parsed frame. Each record adds exact receive time,
provider source time when supplied, measured staleness or the explicit
`NO_SOURCE_TIMESTAMP` state, an SHA-256 of the exact WebSocket payload, and
the reconstructed two-sided BBO or `NO_DENOMINATOR`. This collector runs
while the trading engine is off.

`live_v4` also writes daily `bbo_YYYYMMDD.jsonl` and
`trade_YYYYMMDD.jsonl` streams under `state/window1_decision_inputs_v2` when
the OS itself is running.

BBO-change rows retain full event/market IDs, source and receive timestamps,
staleness, raw WebSocket frame hash, best bid/ask, and the latest trade
identity/lineage. Trade rows retain exchange trade ID when supplied, source
and receive timestamps, staleness, raw-frame hash, price, size, and side.
Missing source timestamps remain null; receive time is never relabeled as
exchange source time.

### Observed starts

`te_live.py` retains the legacy `observed_starts` table for compatibility and
adds `observed_start_events`, keyed by full Kalshi event ticker. A full ID is
written only when both matched player codes resolve to exactly one recent
Kalshi event. One-code and ambiguous matches remain absent instead of storing
a three-letter surrogate. The `/live/` page SHA-256 is retained.

### Decision-time anchors

Every entry consultation now retains the exact consultation timestamp,
category, full IDs, anchor source and price, trade source/receive timestamps,
staleness, trade ID and raw hash, and the same fields for its bid/ask
denominator. The entry dossier embeds this immutable consultation lineage.

## Population time

There are zero historical rows satisfying the strict contract, so there is no
honest empirical strict-branch collection forecast yet. Two weeks of the new
collector is the minimum calibration period before replacing this statement
with measured fresh-anchor and fallback-branch arrival rates.

Historical range-spectrum arrival rates give only optimistic lower bounds:

| Category | relaxed primary cells with zero observations | median days to n=20 | p90 days | warning |
|---|---:|---:|---:|---|
| ATP Challenger | 0 | 99 | 178 | slowest observed cell 593 days |
| ATP Main | 42 | 1,780 | 1,780 | most cells have no usable relaxed history |
| WTA Challenger | 4 | 455 | 910 | slowest observed cell 1,820 days |
| WTA Main | 33 | 1,780 | 1,780 | most cells have no usable relaxed history |
| ITF Men | 32 | 60 | 120 | based on only six observed days |
| ITF Women | 40 | 40 | 80 | based on only four observed days |

These are not production ETAs. They prove that all 90 one-cent cells will not
clear `n=20` quickly, and some may never clear without years of tape. The
lawful response is `THIN`, not pooling. The four ratified depth regimes share
the same anchor observation, so they do not multiply anchor collection time;
fallback source branches do.

## Verification

- retention AST/syntax census: PASS;
- retention contract tests: 4/4 PASS;
- full-event observed-start tests: 2/2 PASS;
- read-only WebSocket retention tests: 3/3 PASS;
- range-spectrum source copy local/VPS SHA-256:
  `1e9891acaaea23a73160aaa26b10b17c87270c1209d9a2a0a23a6a6c56434884`.

Deployment is recorded in the Part 7 report with before/after hashes, free
space, process identities, and evidence that the trading engine remained off.

### Restart-safe WebSocket files

Deployment verification exposed a retention failure in the old hourly naming
scheme: terminating the recorder could leave the active gzip member without a
footer, and a same-hour restart would append new records behind that damaged
member.  The pre-change file
`ws_20260730_06.jsonl.gz` is preserved unchanged.  Recorder sessions now write
unique immutable streams named
`ws_<UTC-hour>_<UTC-session>_<pid>.jsonl.gz`; existing `ws_*.jsonl.gz`
consumers continue to match them.

The first repaired stream was
`ws_20260730_06_20260730T063112Z_214143.jsonl.gz`.  Its first retained frame
contains the exact receive timestamp, explicit
`NO_SOURCE_TIMESTAMP`, raw-frame SHA-256, parsed frame, and BBO field.  New
ticks are therefore not hidden behind the damaged old member.
