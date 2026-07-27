# Window-1 T1 Scoring-Package PRE-RUN

Status: **FROZEN, SCORE-FREE, NOT EXECUTED**

- Exact parent: `88b0eae8620172f41e2f5d45320408357de24c6f`
- Controlling independent T1 PASS: `de2f627e53885bd1a44a42b92f23b5b93a391a47`
- Audited metric/reference implementation: `e7e7b9071b9238868d0599a2e5f24bb92dcc9bdd`
- Candidates: 8, in the frozen T1 order
- D: 804 per candidate
- Target: PC >= 603; official rate PC/D
- Unique guarded fill rows: 3840
- Input-bundle SHA-256: `67a9166a229eca4e048c57bb2316a3298de679ea2b6dad215203e31206743cd0`
- Execution ID: `w1-t1-dev-20260712-20260720-grid1-scorepkg-v1`
- Frozen command template: `python -B arb-executor/analysis/window1_t1_scoring_runner_v1.py --repo . --package .claude/window1_t1_scoring_package_prerun_20260727/SCORING_INPUT_MANIFEST.json --mode execute --authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> --authorization-report <AUDIT_REPORT_PATH>`

The builder did not import or invoke the scorer. C, PC, IC, S, and all
performance fields remain null. The two parent Range-Attack candidates are
bound only as separately reportable audited references and are not rerun.
