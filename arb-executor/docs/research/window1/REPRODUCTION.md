# Independent Window-1 correction reproduction

Branch: codex/window1-definition
Benchmark implementation commit: BENCHMARK_COMMIT_TO_BE_RECORDED
Production chronology inspected: 7def367c96d3a90f198c59c754109aa04b11e9f5
Corrected ledger SHA-256:
09671106b65b3f6ac6fc5f84fbae2248bca2c6466972f40076275b8991dbc5eb

Do not run this in the production checkout. Use a detached research worktree
and private evidence under /srv/omi-research. Never copy raw identities,
account payloads, logs, databases, or recorder archives into Git.

## Research worktree

    export RESEARCH_ROOT=/srv/omi-research/window1-independent-review
    export BENCHMARK_COMMIT=BENCHMARK_COMMIT_TO_BE_RECORDED
    git fetch origin codex/window1-definition
    git cat-file -e "$BENCHMARK_COMMIT^{commit}"
    git worktree add --detach "$RESEARCH_ROOT/worktree" "$BENCHMARK_COMMIT"
    cd "$RESEARCH_ROOT/worktree"
    python -B arb-executor/tests/test_window1_benchmark.py
    python -B arb-executor/tests/test_window1_policy_runner.py

Set private locations without printing them:

    export INPUT="$RESEARCH_ROOT/private/normalized"
    export OUTPUT="$RESEARCH_ROOT/private/validation"
    export LOG_DIR="<private production log directory, read-only>"
    export ACTIVE_PREFIX_BYTES=318840280
    mkdir -p "$INPUT" "$OUTPUT"

INPUT contains events.jsonl, decisions.jsonl, orders.jsonl, fills.jsonl,
prints.jsonl, and books.jsonl under DATA_CONTRACT.md. The supplied private
events/orders/fills hashes must match:

- events:
  1f150cf0e4e4a5809617c2b9303d5f1cf64b22d182d996ff893de255e6e48b46
- orders:
  655e20d9662819596c6e662f6014bfde9eafc0a57896436c13a693ac58915624
- fills:
  a5eedb4169b3dcc69bb2e0545f2770511de4a3fb5ed69bc9b938b82ac353a769
- corrected decisions:
  38cf05ee2649c628299577f5d793bf541b9813973f3094efc25d4f1b7ee6ac1f

## Reconcile causal decisions

The private normalized directory used as reconciliation input contains the
events, orders, and fills files. Run against immutable July 12-19 logs and
exactly the pinned prefix of the active July 20 log:

    python -B arb-executor/analysis/window1_evidence_reconcile.py +      --normalized-dir "$INPUT" +      --log-dir "$LOG_DIR" +      --active-log-prefix-bytes "$ACTIVE_PREFIX_BYTES" +      --output-dir "$RESEARCH_ROOT/private/reconcile"

Expected stop output:

- D 804;
- prior policy mismatches 351;
- classifications 132 causally proven refusal/no-placement, 47 mapping
  defects, 6 accepted-order/missing-receipt intersections, 4 genuinely
  unknown, and 162 logging gaps;
- 308 decision rows;
- 703 accepted orders missing terminal receipts;
- strategy_scoring_permitted false.

Use reconcile/decisions.jsonl as INPUT/decisions.jsonl. Keep the private
reconciliation directory outside Git.

## Manifest, ledger, and corrected validation

    python -B arb-executor/analysis/window1_benchmark.py manifest +      --input-dir "$INPUT" --output-dir "$OUTPUT"
    python -B arb-executor/analysis/window1_benchmark.py ledger +      --input-dir "$INPUT" --output-dir "$OUTPUT"
    python -B arb-executor/analysis/window1_benchmark.py validate +      --input-dir "$INPUT" --output-dir "$OUTPUT"

Validation must stop before scoring and report:

- floor_passing_events 804;
- entry_attempts_compared 3332;
- accepted orders compared 3318;
- failed attempts compared 14;
- matched fills 305;
- matched nonfills 2308;
- causal nonplacement legs 308;
- unobserved decision legs 335;
- mismatches 1054:
  accepted_order_missing_receipt 703, decision_unobserved 335, clock 14,
  fill_receipt 2;
- counterfactual unavailable orders 2613;
- strategy_scoring_permitted false.

The generated candidate_event_ledger.jsonl must have 804 rows and SHA-256:

    09671106b65b3f6ac6fc5f84fbae2248bca2c6466972f40076275b8991dbc5eb

## Public-safe aggregate

The private mismatch ledger contains exchange identities. Sanitize it before
anything enters Git:

    python -B arb-executor/analysis/window1_sanitize_validation.py +      --summary "$OUTPUT/validation_summary.json" +      --mismatches "$OUTPUT/validation_mismatch_ledger.jsonl" +      --output "$OUTPUT/CORRECTED_VALIDATION_SUMMARY.sanitized.json"

The sanitizer checks aggregate counts and emits no event, ticker, order,
client-order, attempt, fill, or account identities.

## Canonical source census

Run the count/schema-only census at idle I/O and low CPU priority:

    ionice -c3 nice -n 19 python -B +      arb-executor/analysis/window1_source_census.py +      --tennis-db "<private tennis.db path>" +      --fund-db "<private fund_equity.db path>" +      --corpus-events "<private corpus_events_v2.jsonl path>" +      --range-spectrum "<private range_spectrum_v1.jsonl path>" +      --output "$RESEARCH_ROOT/private/CANONICAL_SOURCE_CENSUS.sanitized.json"

It outputs schemas, counts, public category/date aggregates, and hashes only.
It never emits private database rows or identities.

## Stop law

Do not run boundary selection, candidate fit, ablations, a freeze, or holdout
on this snapshot. The actual validation gate failed and counterfactual book/
print evidence is unavailable. Repair the named sources and rerun only tests,
source census, reconciliation, manifest, ledger, validation, and sanitization.

If a future snapshot passes, July 12-20 is the complete development interval.
Only then may fit select and freeze a boundary/policy. The forward holdout is
the first three complete UTC dates strictly after the date of that committed
freeze, exactly once, with no date extension after viewing.

These commands do not deploy, access exchange trading endpoints, modify the
live bot, change production configuration, use Window 2, analyze exits or
settlement, or introduce DCA.
