# Window-1 normalized evidence contract

The benchmark consumes UTF-8 JSON Lines under one input directory. Every file is hashed before use. Malformed rows are mismatches. Raw credentials, environment files, account payloads, private keys, runtime databases, full raw logs, and bulk recorder archives must remain outside Git.

## Required files

### `events.jsonl`

One row per exchange-catalog candidate event, not one row per observed tape file.

Required fields are `event_id`, `category`, `event_date`, `scheduled_start_exchange_ts`, `schedule_source`, `schedule_observed_exchange_ts`, and `legs`. Each leg has a public ticker and stable leg label. When known, actual-start fields are `actual_start_exchange_ts`, `actual_start_source`, and `actual_start_verified`.

An exclusion requires `floor_exclusion=verified_pre_window_cancel_or_void` and `floor_evidence_receipt_id`. Every other big-4 row passes the floor even when data is missing.

### `orders.jsonl`

One row per official engine order receipt. Required entry fields are `event_id`, `ticker`, `leg`, `order_id`, `client_order_id`, `purpose=entry`, `action=buy`, `price_cents`, `quantity`, `exchange_created_ts`, and an exchange-timestamped lifetime end in `exchange_cancelled_ts`, `exchange_expired_ts`, or `evaluation_end_exchange_ts`.

Local timestamps are retained only as metadata. The order id and client-order id are the ownership fingerprint. Aggregate book volume alone cannot identify our order.

### `fills.jsonl`

One row per official exchange fill receipt. Required fields are `fill_id` or exchange trade id, `order_id`, `ticker`, `price_cents`, `quantity`, and `exchange_ts`. Partial fills remain separate receipts and are accumulated to the exact ordered quantity.

### `prints.jsonl`

This file contains true prints only. Required fields are `receipt_id` or `trade_id`, `ticker`, `exchange_ts`, `price_cents`, `size`, `source`, and `true_print=true`.

Allowlisted sources are `public_tape`, `kalshi_public_trade`, and `exchange_trade`. Overlapping feeds must preserve the same exchange receipt identity. The benchmark deduplicates by that identity, not by minute, timestamp bucket, or price. Missing or zero size is zero.

Synthetic transitions, quote changes, and inferred last-price changes belong in a separate diagnostic file and are never admitted to `prints.jsonl`.

### `books.jsonl`

One row per book receipt. Fields are `receipt_id`, `ticker`, `exchange_ts`, `local_received_ts`, `source`, `capture_depth`, `bids`, and `asks`. Ladder entries are price and quantity pairs.

Full WebSocket rows also require `epoch_id`, `sequence`, `sequence_valid`, `gap_before`, `reconnect`, and `corrupt`. Only `source=ws_depth`, `capture_depth=full`, valid sequence rows inside an unbroken epoch can support queue replay.

`premarket_ticks` rows must be labeled `top5`. `depth_recorder` rows must be labeled `top20` and snapshot or change-deduplicated as applicable. They may provide limited features but cannot prove queue position.

### Fit and holdout outcome files

`analysis/window1_policy_runner.py` emits physically separate fit, ablation, and holdout JSONL files. Each row contains `event_id`, `candidate_id`, `period`, `status`, the boundary and policy parameters, causal feature receipts, and exactly two leg objects. It refuses to run until validation passes. Holdout accepts only the fit-frozen definition and refuses an existing output.

Each leg object carries `leg`, `ticker`, `required_quantity`, `filled_quantity`, `fill_vwap_cents`, first-fill and completion exchange timestamps, and the W1-close reference computed at the frozen right edge. Missing, error, unknown, thin, and corrupt states are explicit.

The benchmark ignores and should reject any exit, settlement, Window-2, or realized-P-and-L field as a decision input.

## Validation mismatch classes

- `clock`: exchange time missing, invalid, or not exactly reproduced;
- `price`: posted or fill price mismatch;
- `quantity`: required lot or cumulative fill mismatch;
- `queue`: cancellation ownership or queue interval prevents an exact answer;
- `source`: non-true print, missing receipt identity, duplicate conflict, or unsupported source;
- `book`: no valid full-ladder epoch, reconnect, gap, corruption, or truncated ladder;
- `policy`: a floor-passing event lacks both live entry attempts or the live policy receipt set disagrees;
- `fill`: official fill not reproduced;
- `nonfill`: replay fills an order the official machine did not;
- `schedule`: missing or unsupported schedule/start authority;
- `floor_law`: post-hoc or unsupported denominator exclusion;
- `missing_file`, `malformed_jsonl`, and `ledger`: bundle or immutability failures.

The gate passes only with zero mismatch rows.

## Named defect checks

1. Schedule-only rows use a declared positive corridor.
2. Missing and zero sizes remain zero.
3. Only allowlisted true prints are eligible.
4. Cross-feed duplicates use exchange receipt identity.
5. Exchange timestamps order causal events; local timestamps never substitute.
6. `premarket_ticks` is top-five only.
7. `depth_recorder` is snapshot/top-20 and change-deduplicated.
8. `ws_depth` gaps, reconnects, and corrupt epochs are rejected, including the known July-20 risk.
9. Own orders require exact engine fingerprints.

The unit suite exercises every guard plus exact fill and exact non-fill reproduction.
