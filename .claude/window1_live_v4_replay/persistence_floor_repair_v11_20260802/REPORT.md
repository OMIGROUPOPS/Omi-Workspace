# Window-1 V11 fitted persistence-floor repair

V10 71-leg gap diagnosis: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802/V10_NEW_ACTION_GAP_SUMMARY.json

V10 287/190 residual diagnosis and ordinal coverage: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802/V10_RESIDUAL_DIAGNOSIS.json

V11 full D=804 and strict-late D=305 funnels against all five ceilings, partitioned by category and starting-price region: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802/FUNNEL_AND_FIVE_CEILINGS.json

Exact V11 leg ledger with qualifying-ask and traded-low gaps: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802/POPULATION_LEG_LEDGER.jsonl.gz

The accepted correction is narrow: it acts only in a no-ordinal shape state with zero leave-one-leg-out evidence of a later capacity-qualified lower ask. The broad persistence variants were rejected because they reduced execution-floor precision. Development replay only; no holdout or ceiling claim.
