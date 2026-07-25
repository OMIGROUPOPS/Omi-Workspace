# Round-2 deterministic execution-package PRE-RUN

Status: **FROZEN, VALIDATED, NOT SCORED.**

- Parent: `0a7fd1c62d5cf662929c29f2298ed80aeecee1df`
- Authorization audit: `dd6fc30812f5199e048ecee1c80f5649c826bb4d`
- Execution ID: `w1r2-dev-20260712-20260720-0a7fd1c6-grid1`
- Input-bundle SHA-256: `b8424ce782299254891e4c616ea7fd9f67fd476462c740e97fa2421ffaaa617e`
- Exact command: `python -B arb-executor/analysis/window1_round2_grid_runner.py --repo . --package .claude/window1_round2_execution_package_20260724/SCORING_INPUT_BUNDLE.json --mode execute`
- Eight candidates dispatch in the existing frozen order.
- All 6,432 frozen candidate-event streams are materialized and hash-bound as scorer inputs.
- The frozen scorer is invoked exactly once per candidate.
- Validation-only loaded all receipts with zero scorer calls.
- No benchmark, ranking, tuning, ablation, or holdout ran.
