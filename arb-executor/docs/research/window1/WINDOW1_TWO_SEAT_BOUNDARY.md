# Window-1 two-seat ownership boundary

Effective after the 2026-07-31 worktree consolidation.

## Shared objective

The next Window-1 problem is **23 of 598**: the committed quote-touch replay
found 598 negative-combined-delta maker opportunities under the 10-second
print-or-quote law, while the best unchanged OS path captured 23.  The working
hypothesis is positioning: orders rest below touch without a causal mechanism
that recognizes a pulsing leg will return to a previously observed price.

This statement is a problem definition, not an authorization to score, tune,
deploy, or mutate live state.

## Codex live seat

- Branch: `codex/window1-live-consolidated`
- Worktree: `C:\Users\omigr\OMI-Workspace-codex-window1`
- Owns `arb-executor/live_v4.py`.
- Owns the replay shell `arb-executor/analysis/window1_live_v4_replay.py`.
- Owns live/replay fixes, deployment and runtime configuration, reconciliation,
  order-safety code, and tests that exercise those surfaces.
- Integrates analysis only after an explicit handoff and review.

## Claude Code analysis seat

- Branch: `codex/window1-analysis-seat`
- Worktree: `C:\Users\omigr\OMI-Workspace-claude-analysis`
- Analysis only. New work is confined to:
  - `arb-executor/analysis/second_seat/`
  - `arb-executor/tests/analysis_second_seat/`
  - `arb-executor/docs/research/window1/second_seat/`
  - `.claude/window1_second_seat/`
- May read all committed inputs and live/replay code.
- Must never modify, copy over, regenerate, stage, or commit:
  - `arb-executor/live_v4.py`
  - `arb-executor/analysis/window1_live_v4_replay.py`
  - `arb-executor/config/`
  - `arb-executor/deploy/`
  - live, order, position, reconciliation, or settlement code/tests
  - another worktree or branch
- Must not access live/production systems, orders, positions, credentials, or
  deployment controls.

## Collision rule

Each seat commits and pushes only its own branch.  Cross-seat changes move by
an explicit commit SHA and review; neither seat edits the other worktree.
Analysis findings arrive as receipts, fixtures, and proposed behavior.  Codex
alone decides whether and how they enter the replay shell or live code.

Run the boundary checker before every analysis-seat commit:

```text
python -B arb-executor/analysis/window1_seat_boundary.py --repo . --seat analysis --base origin/codex/window1-live-consolidated
```

