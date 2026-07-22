# Corrected Window-1 denominator audit

Audit date: 2026-07-22 UTC
Development interval: 2026-07-12 through 2026-07-20 inclusive
Production chronology inspected at: 7def367c96d3a90f198c59c754109aa04b11e9f5
Research branch parent before this correction: 5cfc81bfe40a2eb33f35236b5ad708269c7c53ae

## Verdict

The lawful development denominator is **D = 804**. This is no longer the
assumption that every catalog event passes. It is the result of applying the
ratified pre-simulation law to all 804 unique big-4 match events and finding
zero supported exclusions.

| Waterfall step | Removed | Remainder |
|---|---:|---:|
| Raw unique big-4 catalog events, U | - | 804 |
| Duplicate market/event rows | 0 | 804 |
| Proven reschedule aliases | 0 | 804 |
| Non-match rows | 0 | 804 |
| Verified pre-window cancellation/void receipts | 0 | 804 |
| Causally known pre-simulation violent-faller refusals | 0 | **804** |

Category counts are ATP challenger 369, ATP main 147, WTA challenger 136,
and WTA main 152. The catalog has 1,608 markets, exactly two per event, with
no duplicate market ticker, duplicate event ticker, duplicate title pair,
missing event ticker, or missing occurrence timestamp.

The corrected immutable ledger is
.claude/window1_20260721/corrected_event_ledger.jsonl: 804 rows, SHA-256
09671106b65b3f6ac6fc5f84fbae2248bca2c6466972f40076275b8991dbc5eb.

## Governing law and chronology

The authority order used here is:

1. superseding operator direction for this benchmark;
2. current docs/LIVING_VAULT.md, docs/THE_DAILY_STANDARD.md, BOARD and
   HANDOFF chronology;
3. sealed entry-table/band/pair-policy receipts;
4. current production code/config only to identify then-operative decisions;
5. older filenames and analyses as non-authoritative fossils.

The operative market scope is all floor-passing big-4 games. The sealed solve
contains REFUSE cells, including the violent-faller class, but its band label
is computed from whole-path anchor, net move, and dip. Recognition tables only
begin classifying partial journeys after the simulated left edge. Applying the
eventual band to exclude a game before replay would leak future path
information.

Therefore a violent-faller exclusion is lawful only when a contemporaneous
engine/operator receipt proves that the class was known before simulation.
No such receipt was found for any of the 804 rows. Candidate-policy refusal,
missing band, thin tape, unknown state, missing data, corrupt data, and
simulator error remain outcomes inside D.

The current production discovery-volume floor is ITF-specific. It supplies no
big-4 exclusion. The solve's support threshold (MIN_TOUCH/MIN_CATCH = 8)
is a cell-estimation floor, not a rule that removes a listed game from the
benchmark denominator.

## Cancellation, void, and alias review

The catalog has 782 binary-finalized events and 22 scalar/early-close events.
The latter label is a post-listing market outcome, not proof that a match was
cancelled before its candidate Window-1 left edge. All 804 events have
non-zero exchange volume and the normal early-close market rule. Three scalar
rows have settlement timestamps more than eight hours before the catalog's
final occurrence timestamp, but the final occurrence field is not a
chronological schedule snapshot and cannot establish a pre-window void.
Those rows remain in D.

No duplicate or reschedule alias was proven. Similar player/title strings are
not sufficient to collapse exchange event identities without a source receipt.

## Per-row law

Every ledger row records date, category, public event identity, both public
leg tickers and labels, required lot five, floor decision, exact rule,
available evidence fields, and causal data state. The default reason is
no_lawful_pre_simulation_exclusion_receipt; it is not
all_games_assumed_to_pass.

Allowed exclusions in the instrument are:

- verified_pre_window_cancel_or_void, with a receipt; or
- causal_pre_window_violent_faller_refuse, with a receipt, an approved
  source, and proof the decision preceded simulation.

Any unsupported or post-hoc exclusion is a floor_law mismatch.

## Split and scope

July 12-20 is inspected development/backwalk history. It may be used only
after the validation gate passes. The forward holdout remains the first three
complete UTC dates strictly after the date of a future committed fit freeze.
No dates have been selected and no holdout evidence has been viewed.

This audit establishes D only. It does not establish C, S, a Window-1
boundary, a candidate policy, individual-leg close-reference deltas, or a
75-percent verdict.
