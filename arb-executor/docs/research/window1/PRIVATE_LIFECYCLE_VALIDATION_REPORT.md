# Window-1 private lifecycle export and validation

Audit date: 2026-07-23 UTC

## Stop result

The read-only private lifecycle export completed, but it recovered no terminal
or fill receipt for any of the 703 unresolved accepted orders. The validation
gate therefore remains failed with the exact same 1,054 mismatches as before.

D remains 804. No candidate scoring, boundary selection, tuning, ablation,
holdout, Window 2, exit, settlement, DCA, Mayo join, order placement,
cancellation, replacement, or production mutation occurred.

## Storage prerequisite

Before the export, the corrected storage receipt was verified read-only:

- the mounted volume UUID and mount source matched;
- the volume had approximately 65.4 GB free and root approximately 16.6 GB;
- the root database path resolved to the volume and no root WAL/SHM existed;
- the rollback database was owned by root, mode 0444;
- the full rollback SHA-256 was
  f4385843ea8312175897edd874a34c70b99a74b30417fdd9ec6a878db9875815;
- five genuine Python children were present for te_live, tennis_odds,
  kalshi_price_scraper, betexplorer and fv_monitor_v3;
- their expected tmux sessions and fresh heartbeat evidence were present;
- the active database advanced during verification; and
- live_v4 PID 452320 remained untouched.

The private evidence directory was created on the verified volume with owner
root and mode 0700. Raw API pages and identity-bearing normalized files remain
there. Completed raw files are mode 0400. No raw path, credential, order ID,
client order ID, fill ID, trade ID or account payload is committed.

## Export contract

The instrument used only authenticated GET requests through the established
Kalshi signing mechanism. It never defines or calls POST, PUT, PATCH or DELETE.

The causal capture range was 2026-07-12T19:21:08Z through
2026-07-21T14:31:06Z. The lower edge is a declared one-hour buffer before the
earliest retained D entry clock. Local clocks select the export range only;
they never establish causal order. The upper edge is one second after the
latest frozen validation inventory edge.

For the 703 targets, the old normalized rows retained exact order ID, client
order ID, event, ticker, action, price, quantity and local attempt clock, but
not exchange creation time, side or terminal receipt. The strict join required
an exact order/client/ticker/action/price/quantity match and obtained exchange
time and side only from an official API order receipt. No fuzzy ticker-only
attribution was allowed.

The validation edge used the already-established actual-outcome inventory law:
verified actual start when present, otherwise scheduled start plus the declared
60-minute corridor. This is not an empirical Window-1 definition and was not
tuned.

## Pagination and immutable evidence

| Item | Result |
|---|---:|
| Authenticated GET attempts, including retries | 1,516 |
| Pagination queries | 785 |
| Queries ending with empty cursor | 785 |
| Cursor cycles | 0 |
| Request errors | 0 |
| Rate-limit responses | 26 |
| Successful rate-limit retries | 26 |
| Deduplicated orders | 2,366 |
| Deduplicated fills | 1,796 |
| Duplicate order identities | 0 |
| Duplicate fill identities | 0 |

The API historical cutoff was 2026-05-23T00:00:00Z for both orders and fills.
The July evidence is newer than that cutoff, so the current portfolio
endpoints—not historical endpoints—are authoritative for this range.

Every target received:

- an exact GET by order ID;
- a cursor-complete fills query by that same order ID; and
- coverage from the event-batched order history and causal-range fill export.

All 703 direct order lookups returned 404. No target identity occurred in the
complete bulk order pages, and no exact target fill was returned.

Private evidence hashes are recorded in the sanitized export and artifact
manifests. Hashes establish immutable byte identity but reveal no raw record.

## Strict 703-slot classification

| Classification | Count |
|---|---:|
| Exact terminal receipt recovered | 0 |
| Exact fill receipt recovered | 0 |
| Valid nonfill/cancellation/rejection recovered | 0 |
| Ambiguous | 0 |
| Still absent after complete source exhaustion | 703 |

A 404 was not converted to a cancellation, rejection or nonfill. Existing
engine logs and the persisted order ledger can prove placement intent or that
an order was once observed resting; neither can manufacture an official
terminal exchange receipt. These 703 rows are now source-exhausted against the
current/historical partition law, complete current order history, exact order
lookups, complete fills, frozen logs and the persisted ledger.

## Validation before and after

| Mismatch class | Before | After |
|---|---:|---:|
| Accepted order missing terminal receipt | 703 | 703 |
| Required-leg decision unobserved | 335 | 335 |
| Failed attempt missing exchange rejection clock | 14 | 14 |
| Fill/terminal inconsistency | 2 | 2 |
| Total | 1,054 | 1,054 |

The rerun preserved:

- 3,332 entry attempts;
- 3,318 accepted orders;
- 14 failed attempts;
- 305 matched filled orders;
- 2,308 matched nonfilled/canceled orders;
- 308 causal nonplacement legs; and
- 335 unobserved decision legs.

An initial join-instrument run incorrectly collapsed the 14 identity-free
failed attempts under an empty dictionary key. That run was rejected before
reporting. The code now replaces only exact nonempty target order IDs, has a
regression test for distinct identity-free attempts, and reproduces every
baseline count exactly.

The gate remains false. Strategy scoring is forbidden.

## Sanitized outputs

The committed machine outputs contain:

- one sanitized export manifest with pagination and raw-byte hashes;
- one sanitized 703-row slot classification;
- one sanitized join summary;
- one sanitized before/after validation summary; and
- one sanitized 1,054-row unresolved mismatch ledger.

Public event and market tickers are retained where useful. Private order,
client-order, fill, trade, attempt and account identities are absent.
KXATPCHALLENGERMATCH-26JUL21MICMAY is outside D and absent from every row.

## External-review boundary

No further benchmark work is lawful on this evidence snapshot. Resolving the
703 requires an exchange-side archival source or support response that can
return the missing official lifecycle receipts by exact order identity.
Neither a 404 nor absence from complete fills proves a nonfill.

Window-1 performance remains unadjudicated.
