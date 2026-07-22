# Window-1 local evidence-recovery report

Audit date: 2026-07-22 UTC
Starting commit: b703916951f00aab94cab0bc960c32d39c0c48e4
Development denominator: D = 804, unchanged
Execution scope: committed local artifacts only; no VPS or live-account query

## Stop result

The validation gate still fails. This lane produced a row-complete, sanitized
recovery census; it did not score a policy, tune a boundary, run an ablation,
select a fit, or open a holdout. C, S, all strategy percentages, and every
performance verdict remain unadjudicated.

The machine ledger is
.claude/window1_20260721/MISMATCH_RECOVERY_LEDGER.sanitized.jsonl. It has
exactly 1,054 unique rows. Every row records the event, market/ticker and leg,
order/attempt identity, causal timestamp, mismatch class, expected evidence,
evidence present, required source and identifiers, and recovery status. Where
the corrective branch intentionally omitted a private row identity, the field
is explicitly null and carries a local recovery slot; no event or order was
fabricated.

## Exact mismatch census and overlap

| Strict-gate mismatch class | Rows |
|---|---:|
| Accepted order missing terminal receipt | 703 |
| Required-leg decision unobserved | 335 |
| Failed attempt missing exchange rejection clock | 14 |
| Fill/terminal inconsistency | 2 |
| Total | 1,054 |

These are mismatch rows, not 1,054 distinct games. The 703, 14 and 2 rows
were sanitized to aggregate counts before the starting commit, so their event,
ticker and private identity are unavailable on this branch. The 335 decision
rows retain public event/ticker/leg identity because they are rebuilt from the
804-row event ledger and the sanitized causal-decision ledger.

The older 351 count is a separate event-level policy census and must not be
added to 1,054. Its 643 absent required legs divide into 308 legs with causal
decision receipts and 335 unobserved legs. The exact reclassification is:

| Policy classification | Events | Absent legs | Causal decision legs | Unobserved legs |
|---|---:|---:|---:|---:|
| Causally proven refusal/no-placement | 132 | 253 | 253 | 0 |
| Mapping defect | 47 | 52 | 50 | 2 |
| Accepted order intersects missing-receipt evidence | 6 | 6 | 1 | 5 |
| Genuinely unknown | 4 | 8 | 4 | 4 |
| Logging gap | 162 | 324 | 0 | 324 |
| Total | 351 | 643 | 308 | 335 |

Thus the 335 strict-gate rows are exactly the unobserved legs nested in the
351-event census. The six accepted-order events are an event-level overlap
with the missing-terminal-receipt problem; the sanitized branch does not
retain enough private keys to identify which of the 703 rows they intersect.
The 132 fully causal refusal/no-placement events are valid noncompletions and
are no longer strict validation mismatches.

## Recovery status

| Status | Rows | Meaning |
|---|---:|---|
| Possible | 3 | The decisive source class or a surviving exact mapping is already identified. |
| Uncertain | 1,051 | Candidate sources exist, but the needed identity, timestamp or surviving receipt has not been proven locally. |
| Impossible | 0 | No row is called irrecoverable without a source-exhaustion receipt. |

The three possible rows are the surviving TOK leg order-placement mapping for
KXATPCHALLENGERMATCH-26JUL12TOKROZ-TOK and the two fill/terminal conflicts,
which can be adjudicated against one immutable official export. All 703
terminal-receipt rows are uncertain, not impossible.

## Terminal-receipt recovery manifest

.claude/window1_20260721/TERMINAL_RECEIPT_RECOVERY_MANIFEST.sanitized.jsonl
contains 703 slots, one for every accepted order lacking terminal truth. The
current exact allocation is:

| Recovery source assigned on local evidence | Rows |
|---|---:|
| Private Kalshi order history | 0 |
| Private Kalshi fills | 0 |
| Frozen live_v4 logs | 0 |
| Persisted order ledger | 0 |
| Confirmed no surviving source | 0 |
| Pending private identity join | 703 |

This does not say the four source systems are empty. It says the public branch
does not contain the per-row order_id/client_order_id join needed to allocate
the 703 slots honestly. For each slot, recovery must proceed in this order:

1. Join the private normalized slot to order_id and, where present,
   client_order_id, plus event and ticker.
2. Query an immutable private order-history export for creation, terminal
   state, fill count, cancellation or expiry.
3. Join private fills by order_id to prove partial/full fill quantity and
   exchange fill time; fills alone cannot prove a terminal nonfill.
4. Use frozen engine logs for local placement/cancel intent and fingerprinting,
   never as a substitute for an exchange terminal timestamp.
5. Use the persisted order ledger only to prove that an order was observed
   resting; it is not a complete terminal history.
6. Mark no-surviving-source only after every named source is exhausted with a
   recorded query receipt.

No account endpoint was queried in this lane. No raw order ID, account payload,
private path, log record, database row, or credential is committed.

## Mapping defects

The named event-level report is MAPPING_DEFECT_REPORT.md and the machine rows
are .claude/window1_20260721/MAPPING_DEFECTS.sanitized.jsonl. There are 47
events, 52 absent legs, 50 causal decision legs and 51 mapped order-placement
legs. Only two absent legs remain unobserved, both on the July 12 TOKROZ event:
the TOK leg has surviving order-placement evidence; the ROZ leg has neither a
mapped placement nor a causal decision.

KXATPCHALLENGERMATCH-26JUL21MICMAY is absent from both the July 12-20 corrected
ledger and the 351-event policy census. Its ticker date is July 21, so the
Michelsen/Mayo incident is a separate post-sample forensic, not one of the 47
mapping defects and not part of D. The local artifacts do not establish its
participant mapping. Its sanitized scope receipt is
.claude/window1_20260721/POST_SAMPLE_MICMAY_FORENSIC.json.

## Why prints and books normalized to zero

Raw evidence was nonempty. Zero normalized rows reflected producer loss and
contract rejection, not source absence.

The public-trade response supplied trade_id, created_time,
yes_price_dollars, count_fp and taker fields. The daysheet cache producer kept
only ts, price_c and ct, discarding stable receipt identity and direction.
subsecond_consolidate.py then searched count or size rather than ct, so the
cached size became zero. The strict contract rejected those rows because a
deduplicable identity and verified positive size no longer coexisted.

The exact repair is to retain trade_id before cache serialization, retain
created_time as the exchange clock, retain count_fp or map ct to size, retain
taker_side, and deduplicate overlapping feeds by trade_id. Missing or zero
size remains zero. A book_transition is always size zero and never a print.

The 1,494 premarket files are top-five snapshots and the 3,079,608 depth rows
are change-deduplicated top-20 snapshots. Their zero normalized book count was
an omitted/over-restrictive adapter, not raw absence. They may support named
limited-depth causal features after normalization, but neither is an exact
queue chain. Exact queue replay requires a readable ws_depth epoch with full
ladders, exchange sequence continuity, gaps, reconnects and corruption
marked. No such development-wide chain is established locally.

The pure repair contract is analysis/window1_normalizer_repair.py. Its
sanitized structural examples are
.claude/window1_20260721/NORMALIZER_REPAIR_SAMPLES.sanitized.json. The samples
are synthetic field-shape demonstrations, not market observations.

## Chronological coverage proof

| Claimed tier | Proven coverage | Proven contents | Causal limitation |
|---|---|---|---|
| Historical macro/context | January 2-April 10; 5,889 historical_events | Whole-match price extrema, totals and first/last clocks | Aggregate summaries; cannot decompose Window 1 |
| January-present aggregate context | corpus registry January 2-July 18; range spectrum April 20-July 18; polling snapshots April 21-July 22 | Event clocks, shapes/cells and bid/ask snapshots | Not a continuous receipt or sequence chain |
| True subsecond causal evidence | 883,557 raw cached public-tape rows in the development inventory; the sanitized census does not retain a per-file minimum/maximum date receipt | Subsecond exchange time/price/count existed upstream | Cache lost trade identity/direction and consolidator lost ct; zero admissible receipt-deduplicable prints, so chronological causal coverage is not proven |
| July 12-20 operational evidence | D=804 catalog; frozen engine log census; 1,494 top-five files; 3,079,608 top-20 rows | Actual decisions/attempts plus limited books | Private terminal gaps, no retained July 12-19 ws_depth chain, July 20 unsafe |

The declared 23,715,462-row subsecond store is not a January-present causal
chain. It combines July backfill, 1,770,521 synthetic transitions and 883,557
cached tape rows in a schema lacking receipt identity and direction. January
material is fixed context only. No source is promoted beyond its timestamp,
depth, identity or sequence guarantees.

## The 9, 8, 31 and 27 populations

- Nine is the pair-complete subset of an 80-row historical banked cohort; all
  nine reproduce their banked fill receipts.
- Eight is the subset of those nine with at least five contracts on each leg.
- Thirty-one is the lower-bound count across the entire D inventory with at
  least five official fills per leg before the validation inventory edge.
- Twenty-seven is the under-par subset of those 31 under that same inventory
  edge.

The banked artifact deliberately exposes ordinal slots rather than event IDs,
so its exact overlap with the 31 cannot be proven from the sanitized branch.
The set relation that is proven is 27 inside 31. None of 9, 8, 31 or 27 is a
Window-1 strategy C or S because no Window-1 boundary/close reference has
passed validation and frozen.

## Next smallest validation step

After storage migration, make one read-only immutable private export containing
only the identifiers and official lifecycle fields needed for the 703 slot
join. Join it outside Git, emit a sanitized source-allocation receipt and rerun
validation. Do not scan books, replay candidates, or open the holdout first.

D remains exactly 804. Missing, unknown and corrupt rows remain in D. Window 2,
exits, settlement, DCA, live activation and production changes remain outside
scope.
