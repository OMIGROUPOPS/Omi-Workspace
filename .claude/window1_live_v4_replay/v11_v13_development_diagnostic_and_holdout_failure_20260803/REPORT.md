# V11/V13 development diagnostic and consumed holdout failure

## Development

The exact acted-set crosswalk is 482 V11-only, 230 shared, and 214 V13-only. The reported 268-leg headline decline is the net, not the V11-only set. Source: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/v11_v13_development_diagnostic_and_holdout_failure_20260803/V11_ACTED_V13_DID_NOT_SUMMARY.json

Every V11-only leg, its V13 blocking level, action support, floor gaps, and shape receipts: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/v11_v13_development_diagnostic_and_holdout_failure_20260803/V11_ACTED_V13_DID_NOT_CROSSWALK.jsonl.gz

Every V13 acted leg and its two floor gaps: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/v11_v13_development_diagnostic_and_holdout_failure_20260803/V13_ACTED_LEG_FLOOR_GAPS.jsonl.gz

Execution-floor collapse diagnostic by category and price region: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/v11_v13_development_diagnostic_and_holdout_failure_20260803/V13_EXECUTION_FLOOR_COLLAPSE_DIAGNOSTIC.json

## Holdout

The one authorized process was invoked once and exited 1 before policy evaluation because eight of 456 public-tape captures ended in HTTP 429. It produced zero V11/V12/V13 event rows and no performance result. The authorization is consumed and the process must not be retried. Source: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/v11_v13_development_diagnostic_and_holdout_failure_20260803/HOLDOUT_EXECUTION_FAILURE.json

Tests: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/v11_v13_development_diagnostic_and_holdout_failure_20260803/TEST_RESULTS.json

Forbidden-access receipt: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/v11_v13_development_diagnostic_and_holdout_failure_20260803/FORBIDDEN_ACCESS_RECEIPT.json

All inferential summaries are partitioned by category and leg price region. Overall values are conservation identities only; thin cells are marked and never pooled.
