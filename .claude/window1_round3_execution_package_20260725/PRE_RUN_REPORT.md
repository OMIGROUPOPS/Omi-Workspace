# Round-3 deterministic execution-package PRE-RUN

Status: **FROZEN, VALIDATED, NOT SCORED.**

- Parent: `14e0e846e8922da98f656aef1f43d2c48da96ee7`
- Round-2 results audit: `807e2c865c3cf7384757c54a3b879518568dec4f`
- Round-3 PRE-RUN audit: `b415a98e2430642242f8e0205fb9b5edfee841b5`
- Execution ID: `w1r3-dev-20260712-20260720-14e0e846-grid1-stdoutsafe`
- Input-bundle SHA-256: `7dec1673c79dd548899f2e003ce753d90af01b182c929aa04be5f20714b24cb5`
- Runner SHA-256: `f9dfab1e73574b25640a55205e3d00e5a28056f55f38fb3419adb728795ce5b4`
- Scorer SHA-256: `b41e6915882fd5b81b583d4c03317d21f1d708fd7710ea4b26a4a6da428fe997`
- Scorer contract SHA-256: `c0918343eb53bd0cdaebc7efe585ed4d4ee6af9e64ef2a651aae3243a3840c27`
- Exact unexecuted command: `python -B arb-executor/analysis/window1_round3_grid_runner.py --repo . --package .claude/window1_round3_execution_package_20260725/SCORING_INPUT_BUNDLE.json --mode execute`
- Eight candidates and 6,432 committed streams are inputs in their frozen order; no stream was regenerated.
- `PROGRESS.log` is authoritative and file-first; cosmetic stdout/stderr loss is nonfatal.
- Validation-only loaded the package with zero scorer calls.
- No benchmark, score, tuning, ranking, ablation, or holdout access occurred.
