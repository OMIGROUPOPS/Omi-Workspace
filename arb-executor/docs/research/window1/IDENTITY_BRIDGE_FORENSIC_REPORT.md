# Window-1 strict identity-bridge forensic

Audit date: 2026-07-23 UTC

## Stop result

The offline identity bridge recovered no lifecycle receipt from the immutable
private API export. All 703 slots remain unresolved:

| Join tier | Matched slots | Collisions |
|---|---:|---:|
| Exact exchange `order_id` | 0 | 0 |
| Exact `client_order_id` | 0 | 0 |
| Unique corroborated composite | 0 | 0 |
| Unresolved | 703 | — |

No Kalshi request was made. Because no proven identity repair changed the
join, validation was not rerun. D remains 804 and the prior 1,054 validation
mismatches remain authoritative. No scoring, tuning, ablation, holdout,
Window 2, exit, settlement, DCA, production change, order, cancellation or
Mayo join occurred.

## What every slot actually contains

The prior `slot_join.private.jsonl` unexpectedly contained no source
identifiers. The forensic therefore rebuilt the same 703-slot event/ticker/leg
multiset from the frozen private orders and unsanitized mismatch ledger, then
required exact agreement with that prior multiset before analysis.

The rebuilt private ledger records the actual value for every field below.
Only field presence and format are public:

| Field | Present | Absent | Meaning |
|---|---:|---:|---|
| Internal `attempt_id` | 0 | 703 | No such producer field survived |
| Internal `trade_id` | 703 | 0 | Engine correlation ID, not exchange identity |
| Exchange `order_id` | 703 | 0 | Hyphenated UUID string |
| `client_order_id` | 703 | 0 | Hyphenated UUID string |
| Event | 703 | 0 | Public event ticker |
| Market/ticker | 703 | 0 | Public market ticker |
| Side | 0 | 703 | Recovered only from the independent log receipt |
| Action | 703 | 0 | All normalized entry actions are present |
| Price cents | 703 | 0 | Exact integer cents |
| Quantity | 703 | 0 | Exact normalized count |
| Local logged timestamp | 703 | 0 | Local receipt metadata |
| Exchange creation timestamp | 0 | 703 | Missing from the slot |
| Validation evaluation edge | 703 | 0 | Exchange-clock inventory edge |

The private 703-row identity ledger remains owner-only outside Git. Its
SHA-256 is
`58fec1f1897c2f77619500a6e1722bc712d101f67dca50db086b580f92e044e4`.

## Are these real accepted exchange orders?

Yes. All 703 are corroborated by a persisted `order_placed` receipt with the
same exchange order ID, client order ID, ticker, side/action, exact price,
exact quantity and local receipt clock:

- 702 receipts report exchange state `resting`;
- 1 reports exchange state `filled`;
- 0 are supported only by an internal attempt record; and
- 0 were promoted to accepted without a successful placement receipt.

The placement chokepoint was inspected read-only. It emits `order_placed` only
after `api_post` returns a non-error response and emits `order_error`
otherwise. The `response_status` value is an exchange order state, not an HTTP
success code. The inspected production source had SHA-256
`834b9e04e2cd1781b7f55fdcf80ed90555bd12341b6e98ec75ad4b06d77f1d54`;
the running bot was not signaled, restarted or changed.

This proves original acceptance, not terminal lifecycle outcome. A persisted
successful placement receipt cannot manufacture a later terminal receipt.

## Exact failure census

Failure classes are nonexclusive because a slot can fail exact identity and
also have an inadmissible composite candidate.

| Failure class | Slots |
|---|---:|
| Exchange ID absent from slot | 0 |
| Exchange ID present but absent from API export | 703 |
| Identifier format/type mismatch | 0 |
| Ticker or participant mapping mismatch | 0 |
| Timestamp/timezone mismatch | 46 |
| Side/action canonicalization mismatch | 0 |
| Cents/dollars or count/count_fp mismatch | 0 |
| Query-window exclusion | 0 |
| Genuinely no corresponding exchange record | 0 |

For all 703, both exact exchange ID and exact client ID are absent from the
API export. UUID case, hyphenation and type normalization find zero additional
candidates.

For 657 slots, no API row has even the same full ticker + side + action +
price + quantity composite. For the other 46, one API row shares that full
composite but its exchange creation time is outside the declared causal
receipt interval:

`0 <= local order_placed receipt time - exchange creation time <= 60 seconds`.

Those 46 are other orders, not admissible nearest-time matches. None was
converted into a fill, nonfill or terminal receipt. There are no collisions at
any join tier.

## Immutable export audit

The byte hashes of all immutable private inputs were rechecked before the
bridge. The export range is UTC:

- lower bound: `2026-07-12T19:21:08Z`;
- upper validation/fill bound: `2026-07-21T14:31:06Z`;
- order collection upper bound: export start;
- exact order-ID lookups: no time filter; and
- order-scoped fill lookups: no time filter.

The existing raw pages prove:

| Export property | Result |
|---|---:|
| HTTP method | GET only |
| Total HTTP attempts | 1,516 |
| Retry attempts | 26 |
| Logical exact-order queries | 703 |
| Logical order-scoped fill queries | 703 |
| Event-batched order collection queries | 81 |
| Causal-range fill collection queries | 1 |
| Historical cutoff queries | 1 |
| Cursor groups | 785 |
| Cursor groups ending empty | 785 |
| Cursor-chain errors | 0 |
| Cursor cycles | 0 |
| Request errors after retry | 0 |

All 703 exact-order queries ended in 404 after retry. The collection calls
specified no status filter. Returned order status coverage is 1,736 canceled
and 630 executed records. The export contains 2,366 exact-ID-deduplicated
orders and 1,796 exact fill/trade-ID-deduplicated fills, with zero duplicate
occurrences or conflicting duplicate payloads.

The historical cutoff was 2026-05-23 UTC, earlier than the July lower bound,
so the current portfolio partition was the declared source. No missing page,
filter omission, cursor break, status restriction, timezone conversion,
identifier coercion or bulk-window edge explains the 703 exact-ID misses.
Direct ID and order-scoped fill queries independently rule out bulk query
window exclusion.

## Deterministic join law

The bridge applies one-to-one identity tiers in this order:

1. exact exchange order ID;
2. exact client order ID, unique on both sides;
3. exact ticker + side + action + price cents + quantity plus a causally
   compatible exchange creation timestamp, unique on both sides and
   independently corroborated by the persisted successful placement receipt.

UUID canonicalization is diagnostic only. It cannot create a match. Ticker-
only, participant-only and nearest-time matching are forbidden.

## External-review boundary

The forensic changes the interpretation of the 703 rows: they are proven real
accepted placements whose terminal lifecycle records are absent from the
frozen API export, not synthetic accepted attempts. It does not repair any
terminal receipt.

The validation gate remains failed. Further progress requires an
exchange-side archival/account-partition source that returns these exact
order identities. The current immutable export is exhausted.
