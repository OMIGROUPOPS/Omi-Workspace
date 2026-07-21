# Independent Window-1 reproduction

## Git identity

The research branch was cut from the fetched authoritative base:

`193e90da406214d2e5d9b2c7b5f752ddda046895`

The byte-exact benchmark implementation and all blocked-state reports are in:

`e0bb8650049763929e7c882ccc51940ddee2b07a`

Do not run these commands in the production checkout.

## Required VPS staging

Create a research-only normalized directory outside Git, for example:

`/srv/omi-research/window1-normalized-v1`

Populate the five files defined in `DATA_CONTRACT.md` from read-only copies or read-only queries of:

- the exchange event catalog and chronological schedule/start receipts for every big-4 game from July 12 through July 20;
- complete engine order and fill receipts, including non-filled entry orders and exchange timestamps;
- the January-present subsecond print/shape corpus;
- public tape and trade archives with receipt identities and verified sizes;
- `premarket_ticks`, labeled top-five;
- `depth_recorder`, labeled snapshot/top-20/change-deduplicated;
- `ws_depth_recorder`, retaining full ladders, sequence number, epoch, reconnect, gap, and corruption flags;
- exact engine fingerprints needed to attribute own resting volume.

Do not copy credentials, environment files, account snapshots, private keys, runtime databases, raw logs, or bulk archives into the Git worktree. The normalized bundle is an external benchmark input.

The local checkout does not contain a reliable raw-schema adapter for the unseen VPS `ws_depth_recorder` archive. CC must normalize that archive without changing these semantics; if a field cannot be produced, leave it missing and let the gate fail rather than infer it.

## Exact benchmark commands

Use a separate VPS worktree:

```bash
git fetch origin codex/window1-definition
git cat-file -e e0bb8650049763929e7c882ccc51940ddee2b07a^{commit}
git worktree add --detach /srv/omi-research/OMI-Workspace-codex-window1 e0bb8650049763929e7c882ccc51940ddee2b07a
cd /srv/omi-research/OMI-Workspace-codex-window1
python -B arb-executor/tests/test_window1_benchmark.py
python -B arb-executor/tests/test_window1_policy_runner.py
```

Set paths for the external normalized bundle and a fresh research output directory:

```bash
INPUT=/srv/omi-research/window1-normalized-v1
OUTPUT=/srv/omi-research/window1-run-20260721
SPEC=arb-executor/docs/research/window1/WINDOW1_CANDIDATES.json
FIT=/srv/omi-research/window1-fit-outcomes.jsonl
ABLATE=/srv/omi-research/window1-fit-ablations.jsonl
HOLDOUT=/srv/omi-research/window1-holdout-outcomes.jsonl
python -B arb-executor/analysis/window1_benchmark.py manifest --input-dir $INPUT --output-dir $OUTPUT
python -B arb-executor/analysis/window1_benchmark.py ledger --input-dir $INPUT --output-dir $OUTPUT
python -B arb-executor/analysis/window1_benchmark.py validate --input-dir $INPUT --output-dir $OUTPUT
```

The next command is forbidden unless validation exits zero and `validation_summary.json` says `gate_pass: true`.

Produce fit-only outcomes for all 16 boundary baselines and every declared policy. The benchmark selects the boundary first, compares policies only inside that boundary, and freezes both:

```bash
python -B arb-executor/analysis/window1_policy_runner.py --period fit --mode candidates --input-dir $INPUT --event-ledger $OUTPUT/candidate_event_ledger.jsonl --validation-summary $OUTPUT/validation_summary.json --candidate-spec $SPEC --output $FIT
python -B arb-executor/analysis/window1_benchmark.py fit --fit-outcomes $FIT --output-dir $OUTPUT
```

Run the one-feature-family-at-a-time ablations on fit only, locked to the frozen boundary and selected policy:

```bash
python -B arb-executor/analysis/window1_policy_runner.py --period fit --mode ablations --input-dir $INPUT --event-ledger $OUTPUT/candidate_event_ledger.jsonl --validation-summary $OUTPUT/validation_summary.json --candidate-spec $SPEC --freeze $OUTPUT/window1_freeze.json --output $ABLATE
python -B arb-executor/analysis/window1_benchmark.py ablate --fit-outcomes $ABLATE --output-dir $OUTPUT
```

Only then may the runner evaluate the single frozen candidate on 2026-07-18 through 2026-07-20. Run the untouched holdout exactly once:

```bash
python -B arb-executor/analysis/window1_policy_runner.py --period holdout --mode candidates --input-dir $INPUT --event-ledger $OUTPUT/candidate_event_ledger.jsonl --validation-summary $OUTPUT/validation_summary.json --candidate-spec $SPEC --freeze $OUTPUT/window1_freeze.json --output $HOLDOUT
python -B arb-executor/analysis/window1_benchmark.py holdout --holdout-outcomes $HOLDOUT --output-dir $OUTPUT
```

The holdout command rejects a changed event-ledger hash, a candidate other than the fit selection, a non-holdout row, or an existing holdout result.

## Exit codes

- `0`: command passed its contract;
- `2`: manifest or ledger incomplete;
- `3`: validation gate failed;
- `4`: scoring blocked by a contract or freeze violation.

No command deploys, reaches the exchange, touches positions, modifies production configuration, or reads an exit result.
