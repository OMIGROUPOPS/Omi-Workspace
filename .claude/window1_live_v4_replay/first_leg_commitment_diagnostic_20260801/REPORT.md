# Window 1 first-leg commitment diagnostic

Score-free July 12-20 development measurement. No scorer, policy replay, holdout, or live access.

Raw gap census: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/COMMITMENT_GAP_CENSUS.json
Raw conditional census: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/SIBLING_FLOOR_CONDITIONAL_CENSUS.json
Raw event ledger: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/FIRST_LEG_COMMITMENT_EVENT_LEDGER.jsonl.gz
Raw naked receipt: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/NAKED_NONCOMPLETION_RECEIPT.json
Raw rule spec: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/CAUSAL_COMMITMENT_RULE_SPEC.json

## Conservation

- D: 804.
- Both capacity-proven floor timestamps: 786.
- Strict first-leg commitments observable: 762.
- Strictly later sibling capacity floors: 762.
- Pair entry cost below 100: 443.
- Naked/noncompleted under the entry-cost diagnostic: 319.

Every distribution remains partitioned by tournament category and observable starting BBO price region. Thin cells are labeled rather than pooled. Exact-bell clocks are NOT_BOUND where the inherited exact-bell ledger has no event row.

## Interpretation fence

The conditional sibling-floor cells are descriptive development-tape observations, not a validated forecast. No naked-commitment probability or hold-duration threshold is bound. The smallest honest causal rule therefore returns INSUFFICIENT_COMMITMENT_EVIDENCE whenever the sibling is not currently coverable inside an independently bound value-and-fee budget.

