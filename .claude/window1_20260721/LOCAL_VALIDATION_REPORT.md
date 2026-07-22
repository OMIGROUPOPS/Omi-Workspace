# Window-1 VPS validation report

## Plain result

- Window-1 definition: **not empirically selected**. The candidate grid and selection law remain frozen, but the evidence gate failed before scoring.
- Development period: **July 12–20 inclusive**. July 18–20 is inspected development/backwalk history, not untouched.
- Forward holdout: **not registered and not viewed**. After a lawful fit freeze, it will be the first three complete UTC dates after the freeze's UTC date.
- Development denominator: **`D = 804`**, all floor-passing big-4 exchange-catalog games. The immutable public ledger hash is `28348235eef26c10475e016614e999d83304ce01a587f890cd9f739c41269999`.
- Validation gate: **failed**, with 3,683 mismatch rows across all 804 events.
- Strategy `C` and `S`: **not computed**. `C/D`, `S/C`, combined entry delta, individual-leg deltas, failure funnel, distance from 75 percent, and an empirical ceiling are not reported because scoring is forbidden.
- Candidate tuning, boundary sensitivity, feature ablations, and forward holdout: **not run**.
- Window 2, exits, settlement, DCA, live activation, and production: **untouched**.

## Exact validation census

The normalized private bundle contains 9,447 engine entry attempts: 9,393 accepted orders and 54 failed attempts. Of those, 3,332 attempts belong to the immutable 804-event denominator: 3,318 accepted orders and 14 failed attempts.

The corrected gate result is:

- 2,615 `book` mismatches: 305 officially filled outcomes and 2,310 officially non-filled outcomes have no admissible causal full ladder at placement;
- 703 `order_identity` mismatches: accepted orders lack a retrievable exchange creation receipt;
- 14 `clock` mismatches: failed attempts have a local stable attempt record but no exchange rejection timestamp;
- 351 `policy` mismatches: 292 floor events have no exact entry-attempt receipt and 59 more do not cover both legs.

No replay fill or non-fill can be called exact while those book and receipt gaps remain. A replay that fills a real non-fill would be wrong, so the 2,310 known non-filled outcomes are blocking evidence, not ignorable rows.

## Historical nine completed duals

The authoritative historical source is the banked 80-row closed slate whose pair-law census reports 9 pair-complete events. Each of those nine was compared privately, event by event and leg by leg, with exact exchange fill receipts.

- 9/9 have both-leg exact order identities and fill receipts.
- 9/9 match the banked fill prices, quantities, and last-fill exchange times.
- 8/9 reach the benchmark's required five-contract lot on both legs.
- The remaining event is a real two-sided fill, but one leg is below the required lot.

This validates the historical receipt record, not the replay. The banked rows' inherited W1 labels are not adopted as the new empirical boundary.

## Source map and coverage

The full count-only inventory is `VPS_SOURCE_INVENTORY.sanitized.json`. Material facts:

- the exchange catalog supplies 1,608 markets and exactly 804 two-leg events for July 12–20;
- the point-in-time live-log census is 9 files, 318,840,280 bytes, 3,264,123 physical rows, and one malformed row;
- development `premarket_ticks` has 1,494 top-five files and 1,589,606,993 bytes; exact decompressed row count is unavailable because active files changed before the scan completed;
- development `depth_recorder` has 189 snapshot/top-20 files, 435,950,289 bytes, and 3,079,608 valid rows; all 3,079,608 lack a usable positive last-trade size;
- the initial `ws_depth` snapshot had 42 files and 1,010,387,170 bytes, but no July 12–19 data; all 19 July-20 files rotated away before a complete row/epoch/corruption census;
- the subsecond store is 6,023,913,472 bytes with 23,715,462 ingest-declared rows, including 883,557 public-tape rows and 1,770,521 synthetic transition rows; its prints table lacks receipt identity;
- the current schedule snapshot has no July 12–17 rows; only 40 of 804 events joined a verified exchange-status actual start;
- current private exchange history returned 1,937 fills and 4,391 orders in the timestamp slice, but the current order endpoint cannot retrieve 6,032 accepted historical engine IDs overall.

Raw order/fill payloads, runtime databases, logs, recorders, and the unsanitized mismatch ledger remain external to Git.

## Defect verification

All nine named defects are active checks:

1. Schedule-only replay requires a positive named corridor; historical schedule snapshots and most actual starts are still missing.
2. Missing or zero size stays zero. The killed `float(size or 1)` simulator is invalid and is neither running nor authoritative.
3. Synthetic transition rows are not true prints. The normalized admissible print file is empty until receipt-identifiable public trades exist.
4. The overlapping live logs produced 554 deduplicated order rows. Public-tape/WebSocket/transition deduplication cannot pass without shared receipt identity.
5. Local receipt time is metadata. It was not substituted for missing exchange creation or rejection timestamps.
6. `premarket_ticks` is labeled top-five only.
7. `depth_recorder` is labeled change-deduplicated snapshot/top-20.
8. `ws_depth` has no retained complete development chain; July-20 sequence and corruption status is unreconstructable locally.
9. Own volume is attributed only by exact engine fingerprints; aggregate book volume is never called ours.

## Stop rule and repair map

`SOURCE_REPAIR_MAP.json` names the exact per-source repair. The next permitted action is to recover missing read-only evidence and rerun tests, manifest, ledger, and validation. The gate must reach zero mismatches before any boundary candidate, policy, ablation, or holdout result is emitted.

One production helper source file contains a hardcoded exchange credential. Its value was not copied or committed. It must not be pushed and should be rotated/removed by the separate live-safety lane.
