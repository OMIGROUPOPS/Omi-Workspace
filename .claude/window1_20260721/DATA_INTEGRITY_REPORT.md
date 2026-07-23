# Window-1 data integrity and provenance

> **July 23 binding correction:** all 1,608 top-five objects are now
> size/hash verified against Spaces. Complete public-tape pagination recovered
> 4,836,462 positive-size true prints for 1,606 tickers. Of the 39 absent
> Spaces trade files, 37 were archive gaps recovered through the public tape
> and two were genuine zero-trade tickers. The zero-row bundle below is
> retained only as pipeline-failure history and cannot support a performance,
> ceiling, or distance-from-target claim.
>
> Superseded on 2026-07-22 by
> arb-executor/docs/research/window1/CANONICAL_CORPUS_TRADEBOOK_MAP.md and
> .claude/window1_20260721/RAW_TO_NORMALIZED_SOURCE_LEDGER.json. The prior
> zero-row normalized result did not mean the raw databases were empty.

## Authority and roles

The complete development universe comes from the historical exchange catalog for the four designated big-4 series. It contains 804 events and exactly two markets per event. Every event passes the pre-simulation floor. Missing schedules, bands, books, prints, receipts, or reconstruction state remain named outcomes in `D`.

July 12–20 is development/backwalk history. It may eventually support boundary selection, policy tuning, and ablations after validation passes. It is not untouched.

The first three complete UTC dates following the eventual fit freeze are reserved for the one forward holdout. Those dates do not exist yet, and no holdout data has been viewed.

The January-present corpus is context-only: established shapes, priors, and causal feature candidates. The locally visible shape sample begins July 6, so it cannot satisfy the January-present role and was not mined or refit.

## Normalized bundle receipt

The private external normalized bundle has:

- 804 event rows;
- 9,447 entry-attempt rows, including 54 failed attempts;
- 903 exact fill rows joined to engine entry order identities;
- zero admissible true-print rows;
- zero admissible full-ladder rows.

The public immutable event ledger has 804 rows and SHA-256 `28348235eef26c10475e016614e999d83304ce01a587f890cd9f739c41269999`. Raw orders, fills, account payloads, logs, archives, recorder data, and private mismatch identities remain in external research storage.

## Provenance limits

`premarket_ticks` is a top-five CSV view. `depth_recorder` is a change-deduplicated top-20 snapshot series. Neither proves full queue position. The latter has 3,079,608 development rows, all without independently verified positive last-trade size, so none is promoted to a true print.

The full-ladder recorder existed only for July 20–21 at inventory time. No July 12–19 full-ladder files existed, and July-20 files rotated away before the complete sequence scan finished. No book row is admitted without a readable, unbroken epoch, valid sequence, exact exchange timestamp, and corruption/gap/reconnect flags.

The subsecond prints table lacks trade receipt identity. Its synthetic transition source is categorically inadmissible, and overlapping public tape cannot be deduplicated causally without a stable receipt ID. Therefore `prints.jsonl` remains empty rather than manufacturing volume.

The live engine logs preserve placement fingerprints and local timestamps, but historical `entry_filled` rows lack exact exchange fill clocks and order IDs. Private exchange fill receipts repair the nine historical pair-complete rows, but the current order endpoint still lacks 703 accepted receipts relevant to `D` and 6,032 accepted log IDs overall.

## Gate consequence

The exact mismatch census is:

- book: 2,615;
- order identity: 703;
- failed-attempt clock: 14;
- policy coverage: 351;
- total: 3,683 across all 804 events.

Missing data never reduces `D`. Because the gate fails, candidate results, ablations, and delta metrics remain null. No survivor slice, reachability-only check, or 9/9 aggregate can substitute for exact fill and non-fill replay.

## Security boundary

Git may contain code, contracts, public catalog ledger rows, content hashes, and sanitized aggregate reports only. It must not contain credentials, environment files, keys, raw order or fill IDs, account payloads, private absolute paths, runtime databases, production logs, caches, recorder archives, corrupt bulk data, or unsanitized mismatch rows.

The production checkout contains a hardcoded exchange credential in a helper source file. The value is excluded from this branch. Rotation/removal belongs to the concurrent live-safety lane.
