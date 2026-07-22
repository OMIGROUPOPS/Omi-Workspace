# Window-1 normalized evidence contract v2

The benchmark consumes UTF-8 JSON Lines under one private input directory.
Every file is hashed before use. Malformed rows are mismatches. Credentials,
environment files, account payloads, keys, runtime databases, logs, and bulk
recorder archives remain outside Git.

## events.jsonl

One row per exchange-catalog candidate event, not one row per observed tape
file. Required fields are event_id, category, event_date,
scheduled_start_exchange_ts, schedule_source, schedule_observed_exchange_ts,
and two public legs. Known actual starts carry timestamp, source, and a
verified flag.

An exclusion requires either:

- verified_pre_window_cancel_or_void plus a receipt; or
- causal_pre_window_violent_faller_refuse plus a receipt,
  floor_decision_before_simulation=true, and an approved engine/operator
  decision source.

An eventual whole-path band label is not causal floor evidence. Every other
big-4 row remains in D even when data is missing.

## decisions.jsonl

One row per causally logged refusal/no-placement on a required leg that has no
normalized entry attempt. Required fields are decision_id, event_id, ticker,
leg, decision_type, reason, receipt event type, source, and the surviving
source clock. Decision type is causal_refusal or causal_no_placement.

A local engine timestamp can prove that the local policy made a non-placement
decision inside the frozen validation corridor. It never becomes an exchange
order/fill clock. A leg with neither an attempt nor such a receipt is
decision_unobserved and remains a noncompletion inside D.

## orders.jsonl

One row per engine entry attempt, including rejected or failed submissions.

An accepted order requires exact event, ticker, leg, order and client-order
identity, purpose=entry, action=buy, price, quantity, exchange creation and
evaluation-end timestamps, official exchange_status, and official
exchange_fill_count. Exact fill receipts must agree with the terminal count
and status.

A rejected attempt requires a stable attempt identity, event/ticker/leg,
price, quantity, exchange rejection timestamp, and rejection code. A local
HTTP error with no exchange timestamp remains a clock mismatch. Local logs
cannot manufacture an exchange rejection receipt.

Local timestamps are metadata. Accepted-order ownership comes from exact order
and client-order fingerprints, never aggregate book volume.

## fills.jsonl

One row per official exchange fill receipt. Required fields are stable fill or
trade identity, order identity, ticker, action, price, quantity, and exchange
timestamp. Partial fills remain separate and accumulate to the exact quantity.
Duplicate or missing fill identity is an error.

## prints.jsonl

True prints only. Required fields are stable receipt/trade identity, ticker,
exchange timestamp, price, independently verified size, source, and
true_print=true.

Allowlisted sources are public_tape, kalshi_public_trade, and exchange_trade.
Overlapping feeds deduplicate by exchange identity, not timestamp/price
buckets. Missing or zero size contributes zero. Synthetic transitions,
quote changes, and inferred last-price changes are diagnostic movement only.

## books.jsonl

Each row carries receipt identity, ticker, exchange and local receive clocks,
source, capture depth, bids, and asks.

Full WebSocket rows also require epoch, sequence, validity, gap, reconnect, and
corruption state. Only full, valid rows inside an unbroken ws_depth epoch can
support exact queue replay.

premarket_ticks is labeled top5. depth_recorder is labeled top20 and snapshot
or change-deduplicated as applicable. They can support limited causal features
but cannot prove full queue position.

## Validation laws

The actual-outcome gate compares decisions and official exchange truth:

1. every required leg has either an entry attempt or causal refusal/no-
   placement receipt;
2. every accepted order has official creation, terminal status, fill count,
   and exact fills where applicable;
3. every failed attempt has the required exchange clock and code;
4. event, ticker, leg, price, quantity, status, first fill, completion, and
   nonfill agree exactly;
5. there are zero mismatch rows.

Full-ladder replay is separately labeled exact, bounded, or unavailable. Its
absence does not erase an official actual fill or cancellation. Strategy
scoring additionally requires the admissible causal book/print evidence needed
by the hypothetical policy.

Mismatch classes include clock, price, quantity, source, schedule, floor_law,
decision_receipt, decision_unobserved, accepted_order_missing_receipt,
fill_receipt, queue, book, fill, nonfill, missing_file, malformed_jsonl, and
ledger.

## Counterfactual fill law

For a hypothetical resting bid, exact fill requires completion under the
pessimistic queue bound. Exact nonfill requires failure even under the
optimistic bound. The interval is queue_unknown, never a fill.

Zero/missing size contributes zero. Synthetic transitions contribute zero.
Receipt identity deduplicates overlapping tape/WebSocket sources. Local receipt
time does not order exchange events. Own volume is attributable only from
exact private engine fingerprints.

## Named defect checks

1. Schedule-only rows use a declared positive corridor.
2. Missing and zero sizes remain zero.
3. Only allowlisted true prints are eligible.
4. Cross-feed duplicates use exchange receipt identity.
5. Exchange timestamps order causal exchange events.
6. premarket_ticks is top-five only.
7. depth_recorder is snapshot/top-20 and change-deduplicated.
8. ws_depth gaps, reconnects, corruption, and July-20 archive risk are named.
9. Own orders require exact engine fingerprints.
10. The cached public-tape size key is ct. A consolidator must not silently
    convert it to zero, and stable upstream trade identity is still required.

## Fit and holdout outputs

Policy outputs are physically separated into fit, ablation, and holdout files.
Every event remains explicit as filled, not_filled, missing, unknown, thin,
corrupt, or error. Each candidate uses the same D, required five-contract lot,
clock, source law, and causal features.

No exit, settlement, Window-2, or realized-P-and-L field is accepted as an
entry input. Holdout accepts only the committed fit freeze and its three
pre-registered dates, and refuses a second evaluation.
