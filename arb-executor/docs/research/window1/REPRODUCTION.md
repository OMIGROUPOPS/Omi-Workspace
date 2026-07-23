# Independent Window-1 correction reproduction

Branch: codex/window1-definition
Benchmark implementation commit: 7cc92744733f680adfddcfde3d9f6744e1d8a0bd
Production chronology inspected: 7def367c96d3a90f198c59c754109aa04b11e9f5
Corrected ledger SHA-256:
09671106b65b3f6ac6fc5f84fbae2248bca2c6466972f40076275b8991dbc5eb

Do not run this in the production checkout. Use a detached research worktree
and private evidence under /srv/omi-research. Never copy raw identities,
account payloads, logs, databases, or recorder archives into Git.

## July 23 supersession

The commands and stop law below reproduce the earlier lifecycle-grain
correction, but their assertion that counterfactual book/print evidence was
unavailable is superseded. Audit commit
`ff0f336f45fde9d54ca2948949689172e8203aff` located the Spaces sources; the
primary lane then completed the direct public-tape pagination and immutable
object manifest. The binding execution order is now:

1. verify the Spaces materialization against the committed object hashes;
2. build the per-game source-coverage ledger from the frozen databases and
   recovered recorders;
3. build the causal real-start ledger without treating first trade as start;
4. rerun actual lifecycle reproduction against those right edges;
5. only if all gates pass, run the event-streamed fit instrument.

`D=804` never changes. `PC`, `NC`, and `IC` overlap within `C`; `X` remains a
separate censored count inside `D`. The historical 4.9%-17.0% reproduction
bound must not be used as policy performance or a ceiling.

## Repaired-source fit and freeze

The development fit executed with runner commit
`bf7898102c006ffee2dc68435c019a9d207cdc6b` and fit-runner SHA-256
`ef5539cd615bdcc05f5bbd2969bcbfd421658abd2dc95fd7178e3c2443af302d`.
The complete frozen sanitized artifact set is commit
`58eef38d811e0228ae4b99bed5f81fcef33fd263`.
Audit source commit `ff0f336f45fde9d54ca2948949689172e8203aff`
is absorbed on this branch. Use owner-only evidence paths outside Git:

    export FIT_ROOT="<owner-only Window-1 fit root>"
    export EVENTS="$FIT_ROOT/joined/events.jsonl"
    export PRINTS="$FIT_ROOT/public/prints.jsonl"
    export TAPE_MANIFEST="$FIT_ROOT/public/PUBLIC_TAPE_MANIFEST.sanitized.json"
    export TICKS="$FIT_ROOT/public/ticks"
    export TOP20="$FIT_ROOT/public/depth_recorder"
    export EMPTY="$FIT_ROOT/empty"
    export MACRO_DB="$FIT_ROOT/private/macro_projection.db"
    export MACRO_RECEIPT="$FIT_ROOT/public/MACRO_PROJECTION_RECEIPT.json"
    export FIT_OUTPUT="$FIT_ROOT/output"
    export CACHE="$FIT_ROOT/cache"
    mkdir -p "$FIT_OUTPUT" "$CACHE" "$EMPTY"

The owner must verify these immutable source identities before executing:

- events:
  `1f150cf0e4e4a5809617c2b9303d5f1cf64b22d182d996ff893de255e6e48b46`;
- public prints:
  `e9b5a765b51ddbf0d65364c4f38744ad949ca3c675e5b3a0e472392fbcfabb55`;
- macro projection:
  `7244e7f9f773cf4c2ba69209d8e979de2f126937ba9b9d0c26440c2ebaf04a74`;
- shape prior:
  `6183ddec56eaab2ad48432aa7c802ea6265e608fa26cdd960aa1dde866824356`;
- real-start ledger:
  `90a943b598baa8debe1acd08fa4b664d3661cd3762c2e5ab54e54d781819b947`.

Run the cache-free tests, then the fit:

    python -m pytest -q \
      arb-executor/tests/test_window1_fit_benchmark.py \
      arb-executor/tests/test_window1_freeze_fit.py
    python -B arb-executor/analysis/window1_fit_benchmark.py \
      --events "$EVENTS" \
      --validation-summary .claude/window1_20260721/LIFECYCLE_VALIDATION_SUMMARY.json \
      --tape-manifest "$TAPE_MANIFEST" \
      --prints "$PRINTS" \
      --event-cache-dir "$CACHE" \
      --cache-workers 8 \
      --start-ledger .claude/window1_20260721/REAL_START_LEDGER.jsonl \
      --source-coverage-summary .claude/window1_20260721/SOURCE_COVERAGE_SUMMARY.json \
      --spaces-materialization-summary .claude/window1_20260721/SPACES_MATERIALIZATION_SUMMARY.json \
      --candidate-spec arb-executor/docs/research/window1/WINDOW1_CANDIDATES.json \
      --shape-prior arb-executor/data/shape_corpus/aim_v2_operational_LATCHCAL.json \
      --premarket-dir "$TICKS" \
      --recovered-premarket-dir "$EMPTY" \
      --depth-recorder-dir "$TOP20" \
      --ws-depth-dir "$EMPTY" \
      --database "$MACRO_DB" \
      --database-projection-receipt "$MACRO_RECEIPT" \
      --feature-output "$FIT_OUTPUT/WINDOW1_FEATURE_MATRIX.jsonl" \
      --detail-output "$FIT_OUTPUT/WINDOW1_CANDIDATE_DETAIL.jsonl" \
      --summary-output "$FIT_OUTPUT/WINDOW1_FIT_SUMMARY.json" \
      --ablation-output "$FIT_OUTPUT/WINDOW1_ABLATION_SUMMARY.json" \
      --coverage-output "$FIT_OUTPUT/WINDOW1_FEATURE_COVERAGE.json"

The expected fit summary SHA-256 is
`ccd12d7a034644549aba3da3991ac3a72beaec62aca6e36417d9dcc2677b0331`.
It selects
`tminus_8h__corridor_15m__walk_law_simultaneous_hold` with raw
`D=804, C=4, PC=0, NC=3, IC=0, X=734`.

The freeze is a one-way write and must use a new output path:

    python -B arb-executor/analysis/window1_freeze_fit.py \
      --fit-summary "$FIT_OUTPUT/WINDOW1_FIT_SUMMARY.json" \
      --event-ledger .claude/window1_20260721/corrected_event_ledger.jsonl \
      --freeze-timestamp 2026-07-23T21:08:05.408699Z \
      --output "$FIT_OUTPUT/WINDOW1_FIT_FREEZE.json"

The expected freeze SHA-256 is
`0a854b95896b52db5f053fa80778895d0bd2e20c9e3cdd73ea3e2b9dda93a0d1`.
It registers 2026-07-24, 2026-07-25, and 2026-07-26 as the only holdout.
Do not build or inspect that ledger before 2026-07-27T00:00:00Z.

## Research worktree

    export RESEARCH_ROOT=/srv/omi-research/window1-independent-review
    export BENCHMARK_COMMIT=7cc92744733f680adfddcfde3d9f6744e1d8a0bd
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

## Local-only mismatch recovery from b7039169

The 1,054-row sanitized recovery ledger can be rebuilt without a VPS, account
API, raw logs, databases, or private identities. Start from commit
b703916951f00aab94cab0bc960c32d39c0c48e4 and run:

    python -B arb-executor/analysis/window1_recovery_manifest.py \
      --events .claude/window1_20260721/corrected_event_ledger.jsonl \
      --policy-reclassification .claude/window1_20260721/POLICY_MISMATCH_RECLASSIFICATION.sanitized.jsonl \
      --decisions .claude/window1_20260721/CAUSAL_DECISIONS.sanitized.jsonl \
      --validation-summary .claude/window1_20260721/CORRECTED_VALIDATION_SUMMARY.sanitized.json \
      --output-dir .claude/window1_20260721

Expected result: mismatch_rows 1054, terminal_receipts 703,
mapping_defects 47, and recovery_status_counts possible 3, uncertain 1051,
impossible 0.

Generate the structural normalizer example and run cache-free tests:

    python -B arb-executor/analysis/window1_normalizer_repair.py \
      --sample-output .claude/window1_20260721/NORMALIZER_REPAIR_SAMPLES.sanitized.json
    python -B arb-executor/tests/test_window1_recovery_manifest.py
    python -B arb-executor/tests/test_window1_normalizer_repair.py

The sample file explicitly declares that its records are synthetic field-shape
examples and not market observations. These commands must not be followed by
candidate scoring while validation remains false.

## Read-only private lifecycle exhaustion

Run this stage only after independently verifying the storage prerequisite.
`PRIVATE_EVIDENCE` must resolve to an owner-only directory outside every Git
worktree. `PRIOR_PRIVATE` is the frozen private normalized bundle that supplied
the 703 target receipt slots. Neither location may be copied into Git.

    export PRIVATE_EVIDENCE="<owner-only private evidence directory>"
    export PRIOR_PRIVATE="<frozen private normalized evidence directory>"
    python -B arb-executor/analysis/window1_private_lifecycle.py preflight \
      --source-orders "$PRIOR_PRIVATE/orders.jsonl" \
      --source-mismatches "$PRIOR_PRIVATE/validation_mismatch_ledger.jsonl" \
      --source-events "$PRIOR_PRIVATE/events.jsonl" \
      --event-ledger "$PRIOR_PRIVATE/candidate_event_ledger.jsonl"
    python -B arb-executor/analysis/window1_private_lifecycle.py export \
      --source-orders "$PRIOR_PRIVATE/orders.jsonl" \
      --source-mismatches "$PRIOR_PRIVATE/validation_mismatch_ledger.jsonl" \
      --source-events "$PRIOR_PRIVATE/events.jsonl" \
      --event-ledger "$PRIOR_PRIVATE/candidate_event_ledger.jsonl" \
      --auth-module-dir "<production auth module directory>" \
      --output-dir "$PRIVATE_EVIDENCE/export"
    python -B arb-executor/analysis/window1_private_lifecycle.py join \
      --source-normalized-dir "$PRIOR_PRIVATE" \
      --source-mismatches "$PRIOR_PRIVATE/validation_mismatch_ledger.jsonl" \
      --decisions "$PRIOR_PRIVATE/decisions.jsonl" \
      --api-orders "$PRIVATE_EVIDENCE/export/api_orders.jsonl" \
      --api-fills "$PRIVATE_EVIDENCE/export/api_fills.jsonl" \
      --output-dir "$PRIVATE_EVIDENCE/joined"

Copy the already-frozen immutable event ledger into a separate validation
input directory, add the joined private order and fill files there, and run
validation only:

    python -B arb-executor/analysis/window1_benchmark.py validate \
      --input-dir "<private joined validation input>" \
      --output-dir "<private validation output>"
    python -B arb-executor/analysis/window1_private_lifecycle.py sanitize-validation \
      --before-summary "$PRIOR_PRIVATE/validation_summary.json" \
      --after-summary "<private validation output>/validation_summary.json" \
      --after-mismatches "<private validation output>/validation_mismatch_ledger.jsonl" \
      --output-dir "<sanitized staging directory>"

The committed receipt for the completed run reports 785 cursor-complete
queries, zero cursor cycles, zero request errors, 703 exact target lookups and
703 targets still absent after complete source exhaustion. Validation remains
false with 1,054 mismatches, so no scoring command is authorized.

## Offline strict identity bridge

Do not call Kalshi during this stage. Use only the immutable private lifecycle
files, the frozen normalized orders/mismatch ledger, immutable gzip logs, and
exactly the byte-pinned active-log prefix:

    python -B arb-executor/analysis/window1_identity_bridge.py \
      --slot-join "$PRIVATE_EVIDENCE/joined/slot_join.private.jsonl" \
      --source-orders "$PRIVATE_EVIDENCE/joined/orders.jsonl" \
      --source-mismatches "$PRIOR_PRIVATE/validation_mismatch_ledger.jsonl" \
      --api-orders "$PRIVATE_EVIDENCE/api_orders.private.jsonl" \
      --api-fills "$PRIVATE_EVIDENCE/api_fills.private.jsonl" \
      --raw-pages "$PRIVATE_EVIDENCE/raw_api_pages.private.jsonl" \
      --export-receipt "$PRIVATE_EVIDENCE/EXPORT_RECEIPT.private.json" \
      --log-dir "$LOG_DIR" \
      --active-log-prefix-bytes 318840280 \
      --output-dir "$PRIVATE_EVIDENCE/identity-bridge"

Expected result at commit time: D 804, target slots 703, exact-order matches 0,
exact-client matches 0, admissible unique composite matches 0, unresolved 703,
and `validation_rerun_required` false. The tool has no network client or HTTP
request operation. Its private identity ledger must remain outside Git.

## Read-only live/historical tier reconciliation

The 2026-07-23 decisive sample uses
`arb-executor/analysis/window1_tier_reconcile.py`. Set
`PRIVATE_EVIDENCE_ROOT` to the owner-only external evidence directory; never
place it or its contents in Git.

Offline selection:

```bash
python3 -B arb-executor/analysis/window1_tier_reconcile.py select \
  --source-orders "$PRIVATE_EVIDENCE_ROOT/joined/orders.jsonl" \
  --source-mismatches \
    "$RESEARCH_ROOT/corrected-run/validation/validation_mismatch_ledger.jsonl" \
  --existing-api-orders "$PRIVATE_EVIDENCE_ROOT/api_orders.private.jsonl" \
  --log-dir "$PRODUCTION_READONLY/arb-executor/logs" \
  --active-log-prefix-bytes 318840280 \
  --output-dir "$PRIVATE_EVIDENCE_ROOT/tier-reconciliation"
```

Expected offline receipt: target population 703; successful cancellations
671; cancellation failure attempts 24; cancellation failures without later
success 4; never-cancelled 28; one immediate-fill state; sample 23 targets plus
six exchange-confirmed sibling controls. The selector must report zero
preserved raw create response bodies and zero preserved raw cancellation
response bodies.

The authenticated query command is GET-only:

```bash
python3 -B arb-executor/analysis/window1_tier_reconcile.py query-sample \
  --sample \
    "$PRIVATE_EVIDENCE_ROOT/tier-reconciliation/TIER_SAMPLE.private.jsonl" \
  --auth-module-dir "$PRODUCTION_READONLY/arb-executor" \
  --output-dir "$PRIVATE_EVIDENCE_ROOT/tier-reconciliation/query"
```

The frozen run receipt is 275 GETs, 245/245 completed pagination chains, no
cursor cycle, retry, rate limit or request error, 23 target exact-ID HTTP 404s,
and six control exact-ID HTTP 200s. Historical target recovery is zero.
Therefore the predeclared full-703 expansion condition is false and validation
must not be rerun.
