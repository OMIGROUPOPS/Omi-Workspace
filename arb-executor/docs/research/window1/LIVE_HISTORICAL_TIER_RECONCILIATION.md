# Window-1 live/historical order-tier reconciliation

Date: 2026-07-23 UTC

Scope: read-only lifecycle evidence only

Denominator: unchanged at `D=804`

## Decision

The sampled historical tier did **not** recover any target order. The
predeclared expansion condition therefore did not fire: no complete 703-order
export was run, validation was not rerun, and the 703 slots were not
reclassified.

The result preserves a narrower but material contradiction:

- all 23 stratified target IDs returned HTTP 404 from exact live lookup;
- no target ID or client ID appeared in the fully paginated live collections;
- no target order or fill appeared in the fully paginated historical
  collections;
- all six same-period sibling controls were found by exact ID in the live
  order tier, and their seven exact fills were also found;
- the authoritative cutoff was 2026-05-24T00:00:00Z for both
  `orders_updated_ts` and `trades_created_ts`, before every sampled July order.

Under the published partition law, a July order cannot be explained as
historical merely because it later canceled or executed: its update followed
the May 24 cutoff. The target IDs are absent from the tier in which the cutoff
places them, while the controls prove that the credentials, account surface,
current endpoint and same-period tickers return real records.

This does **not** establish that the 703 were never exchange-created. It also
does not establish that every create returned HTTP 201 specifically. The
producer and its surviving logs do not preserve the raw response bodies or the
exact success HTTP status.

## Frozen sample

The selector reconstructed the same 703 target slots from the corrected
mismatch ledger, then scanned 3,371,070 byte-pinned engine-log rows. The target
population stratifies as follows:

| Evidence class | Target orders |
|---|---:|
| Normalized create receipt | 703 |
| At least one successful cancellation | 671 |
| At least one failed cancellation attempt | 24 |
| Failed cancellation with no later successful cancellation | 4 |
| No cancellation record | 28 |
| Orphan/re-adopted fingerprint | 198 |
| Immediate-filled normalized create state | 1 |

The cancellation classes are nonexclusive. Twenty of the 24 failed attempts
were followed by a successful cancellation. Thus `671 + 4 + 28 = 703` is the
exclusive lifecycle partition; “24 failed attempts” must not be mistaken for
24 terminal cancellation failures.

The frozen sample contains 23 targets and six controls:

- the one immediate-fill case;
- all four terminal cancellation failures;
- two retry-recovered cancellation failures;
- normal successful cancellations;
- orphan/re-adopted successful cancellations;
- never-cancelled cases;
- six exchange-confirmed sibling controls on sampled events.

Selection hashes and the complete public event/ticker-level result rows are in
the committed sanitized artifacts. Private order and client IDs remain only in
the owner-only evidence area.

## Query performed

The one authenticated run used GET only:

1. `GET /trade-api/v2/historical/cutoff`;
2. exact `GET /trade-api/v2/portfolio/orders/{order_id}` for each sample row;
3. live orders by ticker with:
   - all status and all subaccounts by omission;
   - a bounded UTC creation-time query;
   - separate `resting`, `canceled` and `executed` status queries;
   - an explicit primary-subaccount control;
4. historical orders by ticker;
5. live fills by exact order ID;
6. historical fills by ticker.

The historical endpoints do not expose the same exact-ID filters as the live
endpoints, so their ticker collections were completely paginated before exact
identity attribution.

| Completeness receipt | Count |
|---|---:|
| HTTP GET requests | 275 |
| HTTP 200 | 252 |
| HTTP 404 | 23 |
| Paginated logical queries | 245 |
| Completed pagination chains | 245 |
| Cursor cycles | 0 |
| Retries | 0 |
| Rate limits | 0 |
| Request errors | 0 |

All 23 HTTP 404 responses were the target exact-ID lookups. The six control
exact-ID lookups returned HTTP 200.

## A-E sample classification

| Classification | Targets | Controls |
|---|---:|---:|
| A — exchange-created, found live | 0 | 6 |
| B — exchange-created, found historical | 0 | 0 |
| C — preserved raw HTTP-201 create body, subsequently unretrievable | 0 | 0 |
| D — normalized/log-only acknowledgment, raw body absent | 23 | 0 |
| E — contradictory/unknown outside the D preservation rule | 0 | 0 |

The D label is deliberately limited to these 23 sampled rows. It is not a new
classification of the full 703.

The immediate-fill target also had zero exact fill receipts in either tier.
That is the strongest sampled conflict, but it remains D because the surviving
producer evidence is normalized rather than a preserved raw create response.

## Raw create and cancellation response audit

The raw bodies requested by the operator do not survive in the inspected
sources:

- `live_v4.py` accepts HTTP 200 or 201, parses the JSON in memory, then logs
  selected `order_id`, `client_order_id`, order-state, price, count, side and
  action fields. It does not log the raw response body or the exact HTTP
  success status.
- cancellation accepts HTTP 200 or 204 and immediately reduces the response to
  Boolean `True`; the later log contains `order_id`, label and Boolean success.
  HTTP status, raw body, `reduced_by`, count and exchange timestamp are not
  persisted.

The pinned-log census found zero raw create bodies and zero raw cancellation
bodies. No independent raw-response archive was present in the existing
private evidence inventory. Consequently:

- the 703 normalized create rows are consistent with the HTTP-200/201 success
  code path, but cannot prove 201 rather than 200;
- the 671 successful cancellation rows are consistent with the HTTP-200/204
  path, but cannot distinguish 200 from 204 or recover the response payload.

## Support-ready contradiction

The owner can supply the private IDs and immutable raw-query hashes out of band.
The sanitized support packet asks Kalshi to determine:

1. whether these IDs belong to a legacy or alternate order namespace;
2. why current live lookup retrieves same-period controls but not target IDs;
3. whether the then-operative `portfolio/events/orders` create route requires a
   different archival/account namespace for later retrieval;
4. whether Kalshi can retrieve the lifecycle directly from the private IDs.

Private evidence hashes are committed, but credentials, order IDs, client
order IDs, account payloads and raw response pages are not.

## Gate state

- `D=804` is unchanged.
- The 703 target slots are unchanged.
- Historical recovery trigger: `0`, so no full 703 query.
- Validation rerun: not performed.
- Strategy scoring, tuning, ablation and holdout: not performed.
- Window 2, exits, settlement, Mayo and DCA: untouched.

The next lawful step is external exchange-side adjudication of the sampled
private IDs or discovery of an independently preserved raw create-response
archive. It is not performance analysis.
