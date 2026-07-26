# EXECUTION AUTHORIZATION — Window-1 Range-Attack Scoring Package V2

This document is an authorization-binding addendum to the independently reproduced PASS audit at
fa9bab4752041f045d7e7962168b483235a9db8b on audit/window1-independent. It changes no audit finding;
it exists solely to carry the exact literal bindings that verify_authorization_report_text requires.

RULING: PASS

Package commit:
e7e7b9071b9238868d0599a2e5f24bb92dcc9bdd

Execution ID:
w1-range-attack-v2-dev-20260712-20260720-grid2-scorepkg-v2

Input-bundle SHA-256:
21b4db24ac041d4fcea27f99367881571a16c74b4fbf7b3b2e80ccddabd8c732

Frozen command template (one exact literal line):
python -B arb-executor/analysis/window1_range_attack_scoring_runner_v2.py --repo . --package .claude/window1_range_attack_scoring_package_v2_prerun_20260726/SCORING_INPUT_MANIFEST.json --mode execute --authorization-commit <AUDIT_COMMIT_SUPPLIED_SEPARATELY> --authorization-report <AUDIT_REPORT_PATH>

Scope: this authorization binds exactly one deterministic execution of the package above under the
frozen command template, with the authorization commit SHA supplied separately at run time. It does
not itself execute the benchmark. Results must return for independent audit before any further use.
