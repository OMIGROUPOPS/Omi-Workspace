# Window-1 second-leg X pricer V17 - 804 development diagnostic

All event and leg rows: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/second_leg_x_pricer_v17_20260803/EVENT_LEDGER.jsonl.gz

All category / price-region partitions and every reported number: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/second_leg_x_pricer_v17_20260803/POPULATION_SUMMARY.json

Conservation: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/second_leg_x_pricer_v17_20260803/CONSERVATION_RECEIPT.json

The only policy change from frozen V11 is distributional sibling-shape elimination after a strictly earlier first-leg action/fill X. Every fit is leave-one-event-out; cells below 20 examples abstain. No point target, timing feature, or realized-fall inversion enters behavior. Constants remain frozen at 10 seconds dwell and exact displayed capacity 5.
