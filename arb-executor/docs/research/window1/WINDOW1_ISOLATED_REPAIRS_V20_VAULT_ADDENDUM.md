# Window-1 isolated repairs V20 vault addendum

Date: 2026-08-04. Development population only, D=804. Fix A and Fix C were replayed and scored separately over frozen V19; they were never stacked.

- V19 floor and consolidated result: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/isolated_repairs_v20_20260804/CONTROL_SUMMARY.json
- Fix A exact partitioned result: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/isolated_fix_a_anchor_freshness_v20_20260804/V19_NON_REGRESSION_COMPARISON.json
- Fix A FRONTIER/JOINT: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/isolated_fix_a_anchor_freshness_v20_20260804/FRONTIER.json
- Fix A REGRET: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/isolated_fix_a_anchor_freshness_v20_20260804/REGRET_GAUGE.json
- Sibling-source ruling: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/sibling_source_read_20260804/SIBLING_SOURCE_RECEIPT.json
- Fix C exact partitioned result: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/isolated_fix_c_shape_settlement_v20_20260804/V19_NON_REGRESSION_COMPARISON.json
- Fix C FRONTIER/JOINT: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/isolated_fix_c_shape_settlement_v20_20260804/FRONTIER.json
- Fix C REGRET: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/isolated_fix_c_shape_settlement_v20_20260804/REGRET_GAUGE.json
- WTA_MAIN V19 death census: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/wta_main_v19_death_trace_20260804/WTA_MAIN_DEATH_CENSUS.json

Rulings:

1. Fix A is live-ask anchoring on a fresh own-book receipt. The one-cent starting tolerance is operator-authorized from the frozen 2026-08-03 holdout diagnostic, not fitted here.
2. The mirror-sibling claim is false. The predicate reads the sibling ticker's own formed-book ask path. Fix B was not constructed.
3. Fix C re-asks unanimous LOWER only after a strictly later qualified own-ask receipt at or above the refused floor; it retains the inherited ten-second dwell and exact-five displayed-capacity laws.
4. V19 remains the mandatory non-regression floor for every isolated replay. Development evidence is not holdout validation and is not a market ceiling.
