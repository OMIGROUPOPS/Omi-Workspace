# Canonical corpus and tradebook map

Audit date: 2026-07-22 UTC
Evidence chronology: production commit 7def367c96d3a90f198c59c754109aa04b11e9f5
Path policy: public logical aliases only; raw/private absolute paths are omitted

## Superseding July 23 source-recovery receipt

The empty normalized `books.jsonl` and `prints.jsonl` package is not evidence
that July market data was absent. Independent audit commit
`ff0f336f45fde9d54ca2948949689172e8203aff` proved that the normalizer had read
rotated local storage and had imposed a private-receipt requirement on public
prints. The primary lane then independently enumerated and hash-pinned the
recovered objects:

- `ticks/`: 1,608/1,608 required leg-tickers, giving both BBO and sized
  top-five depth for 804/804 games;
- `trades/`: 1,569/1,608 required leg-tickers;
- `ws_depth/`: 215 July 12-20 hourly objects, classified as
  `RAW_WS_DELTA` unless a ladder-bearing snapshot and gap-free sequence epoch
  prove more;
- direct public exchange tape: 4,836,462 positive-size true-print rows across
  1,606/1,608 tickers, 5,678 completely paginated pages, SHA-256
  `e9b5a765b51ddbf0d65364c4f38744ad949ca3c675e5b3a0e472392fbcfabb55`.

The audit's statement that all 39 missing Spaces trade files were zero-trade
markets was too broad. Complete public-tape pagination proves that 37 were
Spaces archive gaps recovered by the public endpoint. Exactly two tickers had
zero returned trades. Public prints are normalized by public exchange
`trade_id`, ticker, exchange `created_time`, price, positive size, and taker
side. A private order or fill receipt is neither present nor required.

The direct tape supplies causal execution evidence, not match-start truth.
First trade and first `last_trade` appearance remain corroborating regime
observations only because premarket trading is lawful. The real-start ledger
uses live-score, first-in-play, official milestone, lifecycle, and bounded
schedule evidence under the precedence in `WINDOW1_SPEC.md`.

The old 4.9%-17.0% range came from the empty-source/schedule-bound package. It
is retracted as candidate performance, an empirical ceiling, and evidence of
distance from the 75% target.

## Authority finding

There is no single January-present subsecond database on the VPS. The
operator's fixed context library is a tiered composite:

1. tennis.db historical match aggregates for the January-April era;
2. corpus_events_v2.jsonl for January-July event and clock provenance;
3. range_spectrum_v1.jsonl for April-July paired path/shape context;
4. subsecond_store.db and its raw parents for the short July subsecond era.

These sources are non-empty, useful, and not interchangeable. Calling their
union a January-present subsecond tradebook would overstate the evidence.
The January material remains fixed context only and was not mined to define a
new strategy.

The ratified actual exchange ledger is state/fund_equity.db, produced by
tools/fund_tracker.py. docs/THE_DAILY_STANDARD.md calls it the single source
of record and declares parallel figures a defect. There is no separately
ratified current graded-results database. DAYSHEET and game reports are
derived views. tennis.db.matches is an older February-April table, not the
current actual-trade authority.

## Fixed historical/context library

### tennis.db

- Logical path: $PROD_REPO/arb-executor/tennis.db
- Bytes in the later schema census: 17,145,282,560
- Read-only observed-stream SHA-256:
  ac72c037c340f9705314c1eab5e06ca44bf1d55cba337a3608797269bca4649b
  (the database is mutable; this is not a transactionally frozen snapshot)
- historical_events: 5,889 event-grain match summaries, January 2-April 10.
  Its 14 fields are event_ticker, category, winner, loser, first/min/max/last
  price by winner/loser side, total_trades, first_ts, and last_ts.
  first_ts/last_ts are UTC. Prices summarize the whole match and cannot
  decompose Window 1.
- matches: 3,627 old graded rows, February 5-April 17. This table is a fossil
  for current actual-outcome authority.
- kalshi_price_snapshots: 3,467,939 polling rows, April 21-July 22 at audit.
  They carry ticker/event/series, bid, ask, last, volume, occurrence time, and
  polling time. They are snapshots, not exchange receipt chains.

The repository taxonomy explicitly says there is no local tick-level
January-March record; historical_events is the available aggregate tier.

### corpus_events_v2.jsonl

- Logical path: $PROD_REPO/arb-executor/state/corpus_events_v2.jsonl
- Producer: analysis/corpus_restamp.py and corpus_restamp2.py
- Rows: 12,509 event registry rows
- Bytes: 4,221,024
- SHA-256: 839f0552fd4edf8e0116d4ba8e8f2bf7808db82396bfd7a0a2b1eadd860a3ebf
- Coverage: January 2-July 18
- Categories: ATP challenger 6,131; ATP main 2,441; WTA challenger
  1,243; WTA main 2,380; ITF men 170; ITF women 144.
- Clock lineage: 12,028 schedule-grade milestone rows. Current right-edge
  classes are 205 official/status observations, 104 promoted milestone
  observations, 4,411 onset estimates, and 7,789 schedule-only rows.

The corpus is an event/clock registry, not a print database. Schedule-only
rows require a named positive corridor. Onset estimates are never promoted to
observed starts.

### range_spectrum_v1.jsonl

- Logical path: $PROD_REPO/arb-executor/state/range_spectrum_v1.jsonl
- Producers: range_spectrum_build.py, range_spectrum_itf.py, and
  promote_and_recut.sh
- Current rows: 6,252 pair objects
- Current leg objects: 12,361; shaped leg objects: 12,170
- Pair rows by category: ATP challenger 3,038; ATP main 1,097; WTA
  challenger 721; WTA main 1,104; ITF men 154; ITF women 138.
- Bytes: 130,935,927
- SHA-256: 1e9891acaaea23a73160aaa26b10b17c87270c1209d9a2a0a23a6a6c56434884
- Coverage: April 20-July 18

The current file has 201 more pair rows than the Vault's stated 6,051 while
retaining the Vault's 12,170 shaped-leg count. The extra leg objects are not
silently treated as shaped observations. This artifact/document drift is a
named discrepancy and must be reconciled before any prior is refit.

### subsecond_store.db

- Logical path: $PROD_REPO/arb-executor/state/subsecond_store.db
- Producer: analysis/subsecond_consolidate.py
- Bytes at audit: 6,023,913,472
- Declared ingest rows: 23,715,462 from 19,148 ingest files
- Declared sources: backfill 21,061,384; synthetic book_transition 1,770,521;
  public_tape 883,557; ws_log zero
- Physical schema: event, ticker, ts, price, size, src

The store lacks exchange trade identity and taker direction. Synthetic
book-transition rows remain a distinct movement source and contribute zero
traded size. A full physical row/group scan was not forced against the live
17 GB/6 GB database stack after SQLite exhausted scratch; this protects the
production machine and does not imply the store is empty.

## Canonical actual exchange ledger

### fund_equity.db

- Logical path: $PROD_REPO/arb-executor/state/fund_equity.db
- Producer: tools/fund_tracker.py, direct exchange polling every 60 seconds
- Bytes at audit: 6,008,832
- Latest census SHA-256:
  1f9c827c4ef932d49ea66c890b105f422d917e2d460ad2bbadbfd9ffc8b17a73
- fills: 1,773 current official fill rows across 917 tickers at audit,
  spanning July 13-22. Relevant fields are
  fill_id, epoch, day, ticker, action, side, exact count_fp, yes price,
  taker flag, order_id, and retained raw receipt.
- orders_ledger: only orders observed resting by the tracker; fields are
  order identity, ticker, action, price, and creation time. It is not a
  complete accepted/rejected/terminal order history.
- equity, snap_positions, snap_orders, flags, and settlements are monitoring
  and derived-account tables, not counterfactual fill evidence.

This database is live/mutable; its point-in-time hash names the audited bytes,
not a permanent content address. Raw rows, identities, account payloads, and
database copies remain outside Git.

The private normalization also used read-only official API histories:
13,056 fill receipts and 14,928 order-history rows across all returned pages;
the July development timestamp slices were 1,937 fills and 4,391 orders.
Current history returned no record for 6,032 accepted engine identities
overall, including 703 accepted entry orders inside D. Ten sampled point
queries returned not-found. Local logs cannot manufacture those terminal
exchange receipts.

## July 12-20 causal evidence

| Source | Current evidence | Correct label | Causal limit |
|---|---:|---|---|
| Catalog | 804 events / 1,608 markets | exchange listing/schedule | occurrence time is not schedule-change history or actual start |
| Engine logs, frozen prefix | 3,371,071 physical rows scanned | local decision/order metadata | local time is not exchange time; one invalid JSON row; July 18 overlap deduplicated |
| premarket_ticks | 1,494 files / 1,589,606,993 bytes | top-five | not a full chain; no below-level-five proof |
| depth_recorder | 189 files / 435,950,289 bytes / 3,079,608 rows | change-deduplicated snapshot/top-20 | no prints; not a sequence-complete queue history |
| daysheet_tape | 476 files / 48,019,556 bytes / 883,557 rows | cached public tape | cache fields omit upstream trade identity/direction |
| book transitions | 1,770,521 declared rows | synthetic movement | traded size is always zero |
| ws_depth | no retained July 12-19 archive; July 20 rotated/corrupt risk | full ladder only inside valid epochs | no usable development-wide sequence census |

The active July 20 log was frozen by byte prefix 318,840,280. Later growth was
not read. Production processes, tmux sessions, recorders, bot code, orders,
positions, and configuration were untouched.

## Why normalized prints and books were zero

Zero normalized rows was a contract result, not proof that raw sources were
empty.

For public tape, the upstream exchange response exposed a stable trade_id,
taker fields, count_fp, and created_time. The daysheet cache producer retained
only ct, price_c, and ts, discarding identity and direction. The consolidation
code then looked for count or size rather than ct, converting all 883,557
cached sizes to zero. The validation contract correctly rejected the rows
because stable identity and verified positive size were absent at that stage.
This is: upstream field existed, producer discarded some fields, consolidator
discarded size, contract rejected the result.

The separately generated public backfill retained count_fp but also discarded
upstream trade identity/taker fields. It cannot restore receipt
deduplication. Synthetic transitions may describe movement but never restore
volume.

For books, top-five and top-20 raw rows exist. The private bundle's zero book
rows reflect an unimplemented/over-restrictive normalization path, not source
absence. Those rows can lawfully support limited contemporaneous features
after normalization, but they cannot prove exact queue state. Development-wide
full-ladder replay remains unavailable because valid ws_depth epochs do not
cover the period.

## Join to the corrected July ledger

Public event ticker is the event-grain key. Market ticker is the leg-grain key.
The exchange catalog supplies the complete July ledger; engine decisions and
orders join by event/market ticker; official fills join by exact private order
identity outside Git. Context sources join only where their own provenance and
clock tier permit.

Missing joins never remove a ledger row. They become missing, corrupt,
bounded, mapping_defect, logging_gap, or genuinely_unknown outcomes.

## Credential hygiene

A production helper contains a hardcoded exchange credential. No value was
copied to the worktree or reports. Rotation/removal belongs to the separate
live-safety lane. Nothing in this branch changes production credential state.
