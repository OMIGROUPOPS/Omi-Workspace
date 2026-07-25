# Round-2 stdout-safe deterministic execution-package PRE-RUN

Status: **FROZEN, VALIDATED, NOT SCORED.**

- Parent: `4b243babee97fe251bde21fa6a1197dfbba5387d`
- Controlling forensic: `2ac4a2f49b55a5284cc1a9146047c3f42ea7561e`
- Forensic report blob: `b587b24173eb7e3605fa00b0fd06666b88b14442`
- Execution ID: `w1r2-dev-20260712-20260720-0a7fd1c6-grid2-stdoutsafe`
- Input-bundle SHA-256: `e0e088e355589f77e3b3a9cf1a9da51b3045f70c551721fe41e3da5df4ffee2b`
- Exact command: `python -B arb-executor/analysis/window1_round2_grid_runner.py --repo . --package .claude/window1_round2_stdout_safe_execution_package_20260725/SCORING_INPUT_BUNDLE.json --mode execute`
- Eight candidates dispatch in the existing frozen order.
- All 6,432 frozen candidate-event streams are materialized and hash-bound as scorer inputs.
- The frozen scorer is invoked exactly once per candidate.
- `PROGRESS.log` is authoritative; stdout/stderr echo is nonfatal.
- Seven synthetic output-handle fixture cases are bound in tests.
- Retired grid1 evidence is excluded and never consumed.
- Validation-only loaded all receipts with zero scorer calls.
- No benchmark, ranking, tuning, ablation, or holdout ran.
