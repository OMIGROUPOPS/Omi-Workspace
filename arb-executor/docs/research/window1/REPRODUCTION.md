# Independent Window-1 reproduction

## Git identity

Authoritative branch base:

`193e90da406214d2e5d9b2c7b5f752ddda046895`

Benchmark implementation commit:

`881c290df360cf534cb0e504ef1b0bd2676051e3`

Branch:

`codex/window1-definition`

Do not run these commands in the production checkout. Use a detached research worktree and external private evidence storage.

## Research-only setup

The operator chooses an external path and keeps it outside Git:

```bash
export RESEARCH_ROOT=/srv/omi-research/window1-forward-review
export BENCHMARK_COMMIT=881c290df360cf534cb0e504ef1b0bd2676051e3
git fetch origin codex/window1-definition
git cat-file -e "$BENCHMARK_COMMIT^{commit}"
git worktree add --detach "$RESEARCH_ROOT/worktree" "$BENCHMARK_COMMIT"
cd "$RESEARCH_ROOT/worktree"
python -B arb-executor/tests/test_window1_benchmark.py
python -B arb-executor/tests/test_window1_policy_runner.py
```

Set the normalized input and fresh output paths:

```bash
export INPUT="$RESEARCH_ROOT/private/normalized"
export OUTPUT="$RESEARCH_ROOT/private/validation-output"
export SPEC=arb-executor/docs/research/window1/WINDOW1_CANDIDATES.json
mkdir -p "$OUTPUT"
```

The private `INPUT` directory contains the five files defined in `DATA_CONTRACT.md`. Do not place raw order/fill payloads, account data, credentials, databases, logs, or recorder archives in the worktree.

## Current failed-gate reproduction

Run only tests, manifest, ledger, and validation:

```bash
python -B arb-executor/analysis/window1_benchmark.py manifest \
  --input-dir "$INPUT" --output-dir "$OUTPUT"
python -B arb-executor/analysis/window1_benchmark.py ledger \
  --input-dir "$INPUT" --output-dir "$OUTPUT"
python -B arb-executor/analysis/window1_benchmark.py validate \
  --input-dir "$INPUT" --output-dir "$OUTPUT"
```

For the 2026-07-22 evidence snapshot, validation must exit 3 and report:

- `floor_passing_events: 804`;
- `entry_attempts_compared: 3332`;
- `orders_compared: 3318`;
- `failed_attempts_compared: 14`;
- `mismatch_count: 3683`;
- mismatch types `book=2615`, `clock=14`, `order_identity=703`, `policy=351`;
- `strategy_scoring_permitted: false`.

The public candidate ledger must have 804 rows and SHA-256:

`28348235eef26c10475e016614e999d83304ce01a587f890cd9f739c41269999`

Do not run the remaining commands on this failed evidence snapshot.

## Development fit after a future passing gate

Only when `validation_summary.json` says `gate_pass: true` may the full July 12–20 development period be scored:

```bash
export FIT="$RESEARCH_ROOT/private/window1-development-outcomes.jsonl"
export ABLATE="$RESEARCH_ROOT/private/window1-development-ablations.jsonl"
python -B arb-executor/analysis/window1_policy_runner.py \
  --period fit --mode candidates \
  --input-dir "$INPUT" \
  --event-ledger "$OUTPUT/candidate_event_ledger.jsonl" \
  --validation-summary "$OUTPUT/validation_summary.json" \
  --candidate-spec "$SPEC" --output "$FIT"
python -B arb-executor/analysis/window1_benchmark.py fit \
  --fit-outcomes "$FIT" --output-dir "$OUTPUT"
python -B arb-executor/analysis/window1_policy_runner.py \
  --period fit --mode ablations \
  --input-dir "$INPUT" \
  --event-ledger "$OUTPUT/candidate_event_ledger.jsonl" \
  --validation-summary "$OUTPUT/validation_summary.json" \
  --candidate-spec "$SPEC" \
  --freeze "$OUTPUT/window1_freeze.json" --output "$ABLATE"
python -B arb-executor/analysis/window1_benchmark.py ablate \
  --fit-outcomes "$ABLATE" --output-dir "$OUTPUT"
```

The fit command freezes the boundary, policy, development-ledger subset hash, metrics, input hash, freeze timestamp, and the first three complete UTC dates strictly after the UTC freeze date.

## Required commit ceremony before holdout

Copy only the sanitized freeze receipt into the research branch, commit it and its three dates, then create a declaration bound to that commit and the freeze hash. The declaration schema is:

```json
{
  "holdout_dates": ["YYYY-MM-DD", "YYYY-MM-DD", "YYYY-MM-DD"],
  "source_freeze_sha256": "<sha256 of window1_freeze.json>",
  "git_commit_sha": "<full SHA of the commit containing the freeze and dates>",
  "freeze_receipt_repo_path": ".claude/window1_20260721/window1_freeze.json",
  "freeze_and_dates_committed_before_holdout": true
}
```

Commit the declaration before opening holdout evidence. The gate reads `freeze_receipt_repo_path` directly from `git_commit_sha` and requires its blob hash to match the external freeze. Different dates, a different freeze hash, an absent committed blob, an unsafe path, or a non-full Git SHA is rejected.

## Exactly one forward holdout

After all three registered UTC dates are complete, append their public event rows to `events.jsonl`, rebuild the ledger with the committed declaration, and verify that the development subset hash is unchanged:

```bash
export HOLDOUT_DECL="$RESEARCH_ROOT/worktree/.claude/window1_20260721/FORWARD_HOLDOUT_DECLARATION.json"
export HOLDOUT="$RESEARCH_ROOT/private/window1-forward-holdout-outcomes.jsonl"
python -B arb-executor/analysis/window1_benchmark.py ledger \
  --input-dir "$INPUT" --output-dir "$OUTPUT" \
  --holdout-declaration "$HOLDOUT_DECL"
python -B arb-executor/analysis/window1_policy_runner.py \
  --period holdout --mode candidates \
  --input-dir "$INPUT" \
  --event-ledger "$OUTPUT/candidate_event_ledger.jsonl" \
  --validation-summary "$OUTPUT/validation_summary.json" \
  --candidate-spec "$SPEC" \
  --freeze "$OUTPUT/window1_freeze.json" \
  --holdout-declaration "$HOLDOUT_DECL" \
  --output "$HOLDOUT"
python -B arb-executor/analysis/window1_benchmark.py holdout \
  --holdout-outcomes "$HOLDOUT" --output-dir "$OUTPUT" \
  --holdout-declaration "$HOLDOUT_DECL"
```

The holdout is exactly those three dates and exactly one evaluation. If `D` is too small for stability, report that fact; do not extend or shop dates.

## Exit codes and scope

- `0`: command passed its contract;
- `2`: manifest or ledger incomplete;
- `3`: validation gate failed;
- `4`: scoring blocked by a contract or freeze violation.

These commands do not deploy, reach the exchange, touch orders or positions, modify production configuration, use DCA, consume Window 2, or analyze exits.
