# Window-1 local data integrity and provenance report

Research checkout: `C:\Users\omigr\OMI-Workspace-codex-window1`

Authoritative base: `193e90da406214d2e5d9b2c7b5f752ddda046895`, fetched from `origin/blend/kalshi-occ-fallback` before the isolated branch was created.

Inspection date: 2026-07-21 America/New_York. The original `C:\Users\omigr\OMI-Workspace` was used only as read-only evidence. No raw data was copied into Git.

## Local evidence coverage

- Tracked shape samples: 16 files, 17,548,295 bytes, named 2026-07-06 through 2026-07-21. This is not the requested January-present precursor corpus.
- Tracked `live_validation.jsonl`: 30,937 parseable rows and 2 malformed rows. It contains summary types such as bid grade, fill, fill regrade, flow state, pattern, and violation, but its top-level schema lacks exact order id, client-order id, ordered quantity, and exchange fill timestamp. It cannot reproduce live order outcomes.
- Tracked prior substrate: 414 rows dated 2026-05-14 through 2026-07-18. The July-12-forward seed has 187 rows: 19 on Jul 12, 34 on Jul 13, 38 on Jul 14, 24 on Jul 15, 34 on Jul 16, 37 on Jul 17, and 1 on Jul 18. Category counts are ATP_CHALL 74, ATP_MAIN 69, WTA_CHALL 7, and WTA_MAIN 37. None of those 187 rows carries a right-edge field. This is neither an exhaustive operational universe nor an untouched holdout.
- Tracked backwalk bank: 3,042 graded pairs. It is a prior frame-search corpus, not official July-12-forward order/fill truth.
- Tracked milestone shadow: 746 parseable rows, 1 malformed row, 497 events. It is schedule metadata, not a complete exchange event catalog or book/receipt ledger.
- Original read-only `premarket_ticks`: 7 files totaling 4,665 bytes, all with the same 2026-07-15 write time. The isolated worktree has no tracked files in that directory. This cannot represent the claimed 5,190-ticker July book series and is top-five even when present.
- Original read-only `subsecond_store.db`: absent.
- Original read-only `depth_recorder`: absent.
- Original read-only `ws_depth_recorder`: absent.
- Original read-only July-12-forward `live_v3` logs: zero files.
- Original read-only `tennis.db`: zero bytes.
- The original tree contains older raw forensic/session material, including a large untracked session log, but it does not supply the complete July-12–20 exact receipt and full-book bundle. Raw forensic logs may contain account/order detail and must not be committed.

The complete official event universe, official tradebook, order and fill receipts, January-present subsecond corpus, public tape identities, full `premarket_ticks`, `depth_recorder`, and full `ws_depth_recorder` sequence epochs are therefore not local.

## Nine required defect checks

| Defect | Local finding | Guard in the new harness |
|---|---|---|
| Schedule-only truncation | Earlier corpus builders explicitly set schedule-only right edge equal to scheduled time. The later book-frame file added a 30-minute fallback, but the local substrate has no right-edge fields and cannot verify it event by event. | A schedule-only edge requires a named positive corridor. Zero corridor is rejected. Verified actual start may end W1 even when earlier than schedule. |
| `float(size or 1)` | Confirmed in `capture_bookframe.py`: missing or zero size is promoted to one. | Missing and zero size normalize to zero; negative, non-finite, and invalid sizes are rejected. |
| Synthetic source admission | Confirmed: the predecessor SQL query reads all `prints` rows without a source allowlist. | Only allowlisted rows with `true_print=true` enter replay. |
| Duplicate receipts | Confirmed: predecessor rows merge by minute and price, which both collapses independent trades and can double overlapping feeds. | Deduplicate only by exchange receipt or trade identity; conflicting duplicates fail. |
| Local timestamp causality | Confirmed: predecessor order placement time is the engine-local `ts_epoch`, and exact exchange placement/fill clocks are absent. | Exchange timestamps are mandatory for schedule, order, print, book, and fill ordering. Local time is metadata. |
| `premarket_ticks` scope | Confirmed by prior builder comments and local schema: five-level snapshots at sparse cadence. | Labeled top-five and barred from queue proof. |
| `depth_recorder` scope | Archive is absent locally; operator description says snapshot, top-20, and change-deduplicated. | Labeled top-20 and barred from queue proof. |
| `ws_depth` gaps/corruption | Archive is absent, so July-20 sequence corruption cannot be measured locally. | Only full, uncorrupted, no-gap, no-reconnect sequence epochs are eligible. |
| Own-order ownership | Confirmed predecessor keys placement by ticker and price, not exact order identity. Aggregate book cannot identify own volume. | Exact order id plus client-order fingerprint is mandatory. |

The predecessor validation gate also tests realized duals only, ignores official non-fills, silently skips uncovered orders/events, accepts 90 percent, and uses tape volume reachability instead of exact queue reproduction. It is invalid for this mission and remains historical only.

## Control-document reconciliation against current operator direction

The documents agree on several durable points: Window-1 entry must be measured separately from exits, combined entry cost is judged against 100, schedule truth matters, causal data quality must be named, and the prior print-median/book-frame outputs require a validation gate.

They do not agree with the current direction on the active objective or live state:

- `OPEN_LEDGER.md` still describes a 70-percent whole-market bar, Loop-9 exit alternatives, and a book-frame run as running in tmux. Current direction is 75-percent dual W1 completion, Window 1 only, with exits parked. A read-only process check found no Python `capture_bookframe` or `bookframe_20260720` process.
- `OPEN_LEDGER.md` simultaneously preserves the frame-defective Loop-9 exit verdict and says it is void pending the book frame. That material is not authoritative for this lane.
- The prior book-frame description treats five-level REST ticks as the book/mid law. Current direction requires full macrostructure and microstructure and explicitly says top-five is not a full chain.
- Historical records alternate among combined-at-97 pass/fail, dual-negative mastery, and per-leg W1-close delta. Current direction requires strict under-100 combined cost and individual-leg negative delta reported independently. The new specification labels all yardsticks separately.
- The historical queue contains exit work and live policy work. Current queue for this branch is only validation, empirical W1 definition, entry-policy fit, ablation, and one untouched holdout. DCA does not enter the menu.

No control document was rewritten in this branch. These are discrepancy findings only.

## Provenance verdict

The local data can support source-contract tests, chronology audit, metric reconciliation, and a fail-closed harness. It cannot support an immutable full event denominator, event-by-event live validation, boundary sensitivity, policy tuning, feature ablation, or a holdout verdict.

The validation gate is therefore **FAIL — missing evidence before event comparison**. No strategy result, target result, target distance, or empirical ceiling is lawful from this disk.
