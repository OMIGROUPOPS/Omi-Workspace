# Corrected Window-1 validation report

Audit date: 2026-07-22 UTC
Development denominator: D = 804
Corrected ledger SHA-256:
09671106b65b3f6ac6fc5f84fbae2248bca2c6466972f40076275b8991dbc5eb

## Stop verdict

**The validation gate failed. No Window-1 candidate, boundary sensitivity,
ablation, fit freeze, or holdout was run.**

The corrected gate compares actual causal decisions and official accepted-order
outcomes. It no longer declares an actual fill/nonfill invalid merely because
a full ladder is absent. Full ladders and verified prints govern
counterfactual replay and queue bounds, not the truth of an official actual
receipt.

The corrected gate produced 1,054 mismatches:

| Class | Count | Meaning |
|---|---:|---|
| accepted_order_missing_receipt | 703 | Accepted entry order has no retrievable official terminal receipt |
| decision_unobserved | 335 | Required leg has neither a normalized attempt nor a causal refusal/no-placement receipt |
| clock | 14 | Failed HTTP attempt lacks an exchange rejection timestamp |
| fill_receipt | 1 | Official fills disagree with terminal fill count |
| fill_receipt | 1 | Executed status does not reach the ordered quantity |

Exact matches were 305 filled orders and 2,308 official nonfilled/cancelled
orders, or 2,613 accepted orders under the strict gate. Another terminal row
has internally consistent fill-count receipts but fails the stricter executed
quantity law. All 14 locally failed submissions retain their 400/409 outcome
but fail exact exchange-clock validation.

The raw private mismatch ledger remains outside Git. The public aggregate is
.claude/window1_20260721/CORRECTED_VALIDATION_SUMMARY.sanitized.json.

## Reclassification of the prior 351 policy mismatches

A refusal or no-placement is a real noncompletion when its causal engine
receipt survives. It is not automatically a validation mismatch. The frozen
log-prefix scan reclassified all 351 prior event-level policy mismatches:

| Classification | Events |
|---|---:|
| causally proven refusal/no-placement on every absent leg | 132 |
| normalized order mapping defect | 47 |
| accepted order intersects missing-terminal-receipt evidence | 6 |
| genuinely unknown despite some event visibility | 4 |
| logging gap | 162 |
| **Total** | **351** |

There are 308 sanitized causal decision receipts covering 183 events and 308
absent legs. Across the 351 events, the original missing-leg inventory is 643
legs: 308 now have decision receipts and 335 remain unobserved. A mapping
defect is not silently converted to a fill, nonfill, or refusal.

The active July 20 log was read only through byte 318,840,280. Immutable
July 12-19 gzip logs were scanned, including the recovered overlapping July 18
file with receipt deduplication. The scan read 3,371,071 physical rows.

## Nine banked completed pairs

The prior 80-row banked cohort contains nine pair-complete records. All nine
reproduce both legs' exact official fill receipts, price, banked quantity, and
last-fill exchange time. **Only eight of the nine meet the present five
contracts per leg law.** The ninth remains an exact actual pair but is not a
dual-five completion.

The all-event receipt inventory finds 31 events with at least five official
filled contracts on both legs before the validation inventory edge. That is
not a Window-1 C result: the validation edge is verified actual start where
available, otherwise scheduled start plus 60 minutes, and no candidate
Window-1 boundary has been frozen.

## Exact, bounded, and unavailable actual inventory

For receipt inventory only, never strategy scoring:

- exact actual dual-five lower bound: 31 events;
- optimistic dual-five upper bound if every missing-terminal order supplied
  its full stated capacity: 217 events;
- exact actual under-par dual-five lower bound: 27 events;
- optimistic under-par upper bound: 217 events.

The upper bounds are permissive capacity ceilings, not inferred fills. Missing
receipts never become fills. The 31/27 lower-bound rows are official actual
receipts under the validation inventory edge, not C/S under a selected
Window 1.

Counterfactual replay has zero exact orders and zero bounded orders in the
normalized bundle; 2,613 otherwise exact actual orders lack admissible
full-ladder/print replay evidence. This does not undo their official actual
outcomes. It blocks counterfactual policy simulation.

## Operator metrics

The denominator is known: **D = 804**.

Strategy quantities are intentionally null:

- C: not adjudicated;
- S: not adjudicated;
- C/D, S/C, S/D: not adjudicated;
- combined-vs-par distribution: not adjudicated;
- individual-leg delta against a frozen Window-1-close reference: not
  adjudicated;
- negative-leg rate: not adjudicated;
- distance from the 75-percent target: unknown.

No empirical Window-1 boundary or close reference exists while validation
fails. Reporting the 31 receipt-inventory events as C, or the 27 receipt-
inventory under-par events as S, would join different yardsticks.

## Per-source repair map

1. Recover exact official creation/terminal/cancellation/expiry receipts for
   the 703 accepted orders missing terminal truth.
2. Recover exchange-timestamped rejection receipts for the 14 failed attempts,
   or retain their clock mismatches.
3. Repair the 47 event/order leg mappings, then rerun decision reconciliation.
4. Recover logs/receipts for the remaining 166 logging-gap or genuinely
   unknown events; unknown stays in D.
5. Resolve both fill-receipt inconsistencies against an official immutable
   export.
6. Normalize existing top-five/top-20 evidence as limited-depth sources and
   recover retained ws_depth epochs plus receipt-identifiable prints before
   counterfactual tuning.

Until those repairs make the gate pass, the only permitted commands are tests,
source census, manifest, ledger, decision reconciliation, validation, and
sanitization.

Window 2, exits, settlement, DCA, live activation, and production changes
remain untouched.
