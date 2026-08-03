# Window-1 holdout null-action correction

The 268 V11 UNPROVEN rows are not failed orders. All 268 have a raw null proposed price and no placement receipt. The prior adapter converted null to zero; therefore its -16 median, -53 p25, and -99 minimum were fabricated arithmetic, not policy prices. Exact correction: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/holdout_null_action_correction_20260803/MEASUREMENT_DEFECT_RECEIPT.json

Every V11 UNPROVEN leg, its qualifying ask floor, null placed price, null gap, and terminal predicate: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/holdout_null_action_correction_20260803/V11_UNPROVEN_LEG_LEDGER.jsonl

Grouped by category and price region, with no-action predicate conservation: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/holdout_null_action_correction_20260803/V11_UNPROVEN_GROUPED_CENSUS.json

The 188 actual V11 placements all used the contemporaneous ask and all were PROVEN_TAKER. Their true ask-floor gap has minimum 0, median 1, maximum 36, 93 exact-floor rows, and zero negative gaps: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/holdout_null_action_correction_20260803/V11_ACTUAL_PLACEMENT_GAP_CENSUS.json

The complete strict-null reaggregation for V11, V13, and V14: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/holdout_null_action_correction_20260803/V11_V13_V14_STRICT_NULL_REAGGREGATION.json

The price and no-call code paths: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/holdout_null_action_correction_20260803/V11_UNPROVEN_CODE_PATH_RECEIPT.json

This correction performs zero policy replays and makes no strategy change. It does not move the 18 V11 under-par completed pairs; the proposed 18-to-205 inference depended on nonexistent orders.
